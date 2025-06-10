import { Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { MFAService } from './mfa.service';
import { SSOService } from './sso.service';
import { BiometricService } from './biometric.service';
import { SessionService } from './session.service';
import { Request } from 'express';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { createHash, randomBytes } from 'crypto';

export interface AuthFlowState {
  flowId: string;
  userId?: string;
  step: AuthFlowStep;
  method: AuthMethod;
  attempts: number;
  maxAttempts: number;
  expiresAt: Date;
  metadata: Record<string, any>;
}

export enum AuthFlowStep {
  INITIAL = 'initial',
  CREDENTIALS = 'credentials',
  MFA_REQUIRED = 'mfa_required',
  MFA_CHOICE = 'mfa_choice',
  MFA_VERIFICATION = 'mfa_verification',
  BIOMETRIC = 'biometric',
  SSO_REDIRECT = 'sso_redirect',
  SSO_CALLBACK = 'sso_callback',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum AuthMethod {
  PASSWORD = 'password',
  SSO = 'sso',
  BIOMETRIC = 'biometric',
  MAGIC_LINK = 'magic_link',
  PASSKEY = 'passkey',
}

export interface AuthFlowResult {
  success: boolean;
  nextStep?: AuthFlowStep;
  flowId?: string;
  data?: any;
  error?: string;
}

export interface AuthOptions {
  rememberMe?: boolean;
  trustedDevice?: boolean;
  elevatedAuth?: boolean;
}

@Injectable()
export class AuthFlowService {
  private flows: Map<string, AuthFlowState> = new Map();

  constructor(
    private configService: ConfigService,
    private mfaService: MFAService,
    private ssoService: SSOService,
    private biometricService: BiometricService,
    private sessionService: SessionService,
    private eventEmitter: EventEmitter2
  ) {
    // Clean up expired flows periodically
    setInterval(() => this.cleanupExpiredFlows(), 60000); // Every minute
  }

  /**
   * Initialize authentication flow
   */
  async initializeFlow(
    method: AuthMethod,
    request: Request,
    options?: AuthOptions
  ): Promise<AuthFlowResult> {
    const flowId = this.generateFlowId();
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    const flowState: AuthFlowState = {
      flowId,
      step: AuthFlowStep.INITIAL,
      method,
      attempts: 0,
      maxAttempts: 5,
      expiresAt,
      metadata: {
        ipAddress: this.getClientIp(request),
        userAgent: request.headers['user-agent'],
        options,
      },
    };

    this.flows.set(flowId, flowState);

    // Emit flow started event
    this.eventEmitter.emit('auth.flow.started', {
      flowId,
      method,
      ipAddress: flowState.metadata.ipAddress,
    });

    // Determine next step based on method
    let nextStep: AuthFlowStep;
    let data: any = {};

    switch (method) {
      case AuthMethod.SSO:
        nextStep = AuthFlowStep.SSO_REDIRECT;
        const providers = this.ssoService.getAvailableProviders();
        data = { providers };
        break;
      
      case AuthMethod.BIOMETRIC:
        nextStep = AuthFlowStep.BIOMETRIC;
        const biometricOptions = await this.biometricService.checkBiometricAvailability();
        data = { biometricOptions };
        break;
      
      case AuthMethod.PASSWORD:
      default:
        nextStep = AuthFlowStep.CREDENTIALS;
        break;
    }

    flowState.step = nextStep;
    this.flows.set(flowId, flowState);

    return {
      success: true,
      flowId,
      nextStep,
      data,
    };
  }

  /**
   * Process credentials step
   */
  async processCredentials(
    flowId: string,
    credentials: { username: string; password: string },
    request: Request
  ): Promise<AuthFlowResult> {
    const flowState = this.getFlowState(flowId);
    
    if (!flowState || flowState.step !== AuthFlowStep.CREDENTIALS) {
      throw new UnauthorizedException('Invalid flow state');
    }

    // Increment attempts
    flowState.attempts++;
    
    if (flowState.attempts > flowState.maxAttempts) {
      return this.failFlow(flowId, 'Too many attempts');
    }

    try {
      // Validate credentials (this would be implemented by the user service)
      const user = await this.validateCredentials(credentials.username, credentials.password);
      
      if (!user) {
        this.flows.set(flowId, flowState);
        return {
          success: false,
          flowId,
          error: 'Invalid credentials',
        };
      }

      flowState.userId = user.id;
      
      // Check if MFA is required
      if (user.mfaEnabled) {
        flowState.step = AuthFlowStep.MFA_REQUIRED;
        this.flows.set(flowId, flowState);

        const mfaMethods = await this.getAvailableMFAMethods(user.id);
        
        return {
          success: true,
          flowId,
          nextStep: AuthFlowStep.MFA_CHOICE,
          data: { methods: mfaMethods },
        };
      }

      // No MFA required, complete authentication
      return this.completeAuthentication(flowId, user.id, request);
    } catch (error) {
      return this.failFlow(flowId, error.message);
    }
  }

  /**
   * Process MFA verification
   */
  async processMFAVerification(
    flowId: string,
    method: 'totp' | 'backup',
    code: string,
    request: Request
  ): Promise<AuthFlowResult> {
    const flowState = this.getFlowState(flowId);
    
    if (!flowState || flowState.step !== AuthFlowStep.MFA_VERIFICATION) {
      throw new UnauthorizedException('Invalid flow state');
    }

    if (!flowState.userId) {
      throw new UnauthorizedException('User not identified');
    }

    try {
      let verified = false;
      
      if (method === 'totp') {
        // Get user's MFA secret (would be fetched from database)
        const mfaSecret = await this.getUserMFASecret(flowState.userId);
        verified = this.mfaService.verifyToken(mfaSecret, code);
      } else if (method === 'backup') {
        // Verify backup code
        const backupCodes = await this.getUserBackupCodes(flowState.userId);
        const result = this.mfaService.verifyBackupCode(backupCodes, code);
        verified = result.valid;
        
        if (verified) {
          // Update user's backup codes
          await this.updateUserBackupCodes(flowState.userId, result.remainingCodes);
        }
      }

      if (!verified) {
        flowState.attempts++;
        this.flows.set(flowId, flowState);
        
        return {
          success: false,
          flowId,
          error: 'Invalid code',
        };
      }

      // MFA verified, complete authentication
      return this.completeAuthentication(flowState.flowId, flowState.userId, request, {
        mfaVerified: true,
      });
    } catch (error) {
      return this.failFlow(flowId, error.message);
    }
  }

  /**
   * Process SSO callback
   */
  async processSSOCallback(
    flowId: string,
    provider: string,
    code: string,
    state: string,
    request: Request
  ): Promise<AuthFlowResult> {
    const flowState = this.getFlowState(flowId);
    
    if (!flowState || flowState.step !== AuthFlowStep.SSO_CALLBACK) {
      throw new UnauthorizedException('Invalid flow state');
    }

    try {
      // Validate state parameter
      if (!this.ssoService.validateState(state, flowState.metadata.ssoState)) {
        throw new UnauthorizedException('Invalid state parameter');
      }

      let profile: any;
      
      // Handle provider-specific callback
      switch (provider) {
        case 'google':
          profile = await this.ssoService.handleGoogleCallback(code);
          break;
        case 'microsoft':
          profile = await this.ssoService.handleMicrosoftCallback(code);
          break;
        default:
          throw new UnauthorizedException('Unknown SSO provider');
      }

      // Find or create user based on SSO profile
      const user = await this.findOrCreateSSOUser(profile);
      
      // Link SSO account if user already exists
      if (user.existingUser) {
        await this.ssoService.linkSSOAccount(
          user.id,
          provider,
          profile.id,
          profile
        );
      }

      // Complete authentication
      return this.completeAuthentication(flowId, user.id, request, {
        ssoProvider: provider,
      });
    } catch (error) {
      return this.failFlow(flowId, error.message);
    }
  }

  /**
   * Process biometric authentication
   */
  async processBiometricAuth(
    flowId: string,
    response: any,
    request: Request
  ): Promise<AuthFlowResult> {
    const flowState = this.getFlowState(flowId);
    
    if (!flowState || flowState.step !== AuthFlowStep.BIOMETRIC) {
      throw new UnauthorizedException('Invalid flow state');
    }

    try {
      // Get user device based on credential ID
      const device = await this.getUserDeviceByCredentialId(response.id);
      
      if (!device) {
        throw new UnauthorizedException('Device not registered');
      }

      // Verify biometric response
      const result = await this.biometricService.verifyAuthenticationResponse(
        device.userId,
        response,
        device
      );

      if (!result.verified) {
        return {
          success: false,
          flowId,
          error: 'Biometric verification failed',
        };
      }

      // Update device counter
      if (result.newCounter) {
        await this.updateDeviceCounter(device.id, result.newCounter);
      }

      // Complete authentication
      return this.completeAuthentication(flowId, device.userId, request, {
        biometricAuth: true,
        deviceId: device.id,
      });
    } catch (error) {
      return this.failFlow(flowId, error.message);
    }
  }

  /**
   * Complete authentication flow
   */
  private async completeAuthentication(
    flowId: string,
    userId: string,
    request: Request,
    additionalData?: any
  ): Promise<AuthFlowResult> {
    const flowState = this.getFlowState(flowId);
    
    if (!flowState) {
      throw new UnauthorizedException('Invalid flow state');
    }

    try {
      // Create session
      const sessionResult = await this.sessionService.createSession(
        userId,
        request,
        {
          rememberMe: flowState.metadata.options?.rememberMe,
          mfaVerified: additionalData?.mfaVerified,
          metadata: {
            authMethod: flowState.method,
            ...additionalData,
          },
        }
      );

      // Mark flow as completed
      flowState.step = AuthFlowStep.COMPLETED;
      this.flows.set(flowId, flowState);

      // Emit authentication completed event
      this.eventEmitter.emit('auth.flow.completed', {
        flowId,
        userId,
        method: flowState.method,
        sessionId: sessionResult.session.id,
      });

      // Clean up flow after delay
      setTimeout(() => this.flows.delete(flowId), 5000);

      return {
        success: true,
        flowId,
        data: {
          accessToken: sessionResult.accessToken,
          refreshToken: sessionResult.refreshToken,
          session: sessionResult.session,
        },
      };
    } catch (error) {
      return this.failFlow(flowId, error.message);
    }
  }

  /**
   * Fail authentication flow
   */
  private failFlow(flowId: string, reason: string): AuthFlowResult {
    const flowState = this.flows.get(flowId);
    
    if (flowState) {
      flowState.step = AuthFlowStep.FAILED;
      this.flows.set(flowId, flowState);

      // Emit authentication failed event
      this.eventEmitter.emit('auth.flow.failed', {
        flowId,
        reason,
        method: flowState.method,
      });
    }

    // Clean up flow after delay
    setTimeout(() => this.flows.delete(flowId), 5000);

    return {
      success: false,
      error: reason,
    };
  }

  /**
   * Get flow state
   */
  private getFlowState(flowId: string): AuthFlowState | null {
    const flowState = this.flows.get(flowId);
    
    if (!flowState) {
      return null;
    }

    // Check if flow is expired
    if (new Date() > flowState.expiresAt) {
      this.flows.delete(flowId);
      return null;
    }

    return flowState;
  }

  /**
   * Generate flow ID
   */
  private generateFlowId(): string {
    return randomBytes(32).toString('hex');
  }

  /**
   * Clean up expired flows
   */
  private cleanupExpiredFlows(): void {
    const now = new Date();
    
    for (const [flowId, flowState] of this.flows.entries()) {
      if (now > flowState.expiresAt) {
        this.flows.delete(flowId);
      }
    }
  }

  /**
   * Get client IP address
   */
  private getClientIp(request: Request): string {
    const forwarded = request.headers['x-forwarded-for'];
    
    if (forwarded) {
      return (forwarded as string).split(',')[0].trim();
    }
    
    return request.ip || request.connection.remoteAddress || '';
  }

  // Placeholder methods that would be implemented by user service
  private async validateCredentials(username: string, password: string): Promise<any> {
    // Implementation would validate against user database
    return null;
  }

  private async getUserMFASecret(userId: string): Promise<string> {
    // Implementation would fetch from database
    return '';
  }

  private async getUserBackupCodes(userId: string): Promise<string[]> {
    // Implementation would fetch from database
    return [];
  }

  private async updateUserBackupCodes(userId: string, codes: string[]): Promise<void> {
    // Implementation would update database
  }

  private async getAvailableMFAMethods(userId: string): Promise<string[]> {
    // Implementation would check user's enabled MFA methods
    return ['totp', 'backup'];
  }

  private async findOrCreateSSOUser(profile: any): Promise<any> {
    // Implementation would find or create user based on SSO profile
    return null;
  }

  private async getUserDeviceByCredentialId(credentialId: string): Promise<any> {
    // Implementation would fetch device from database
    return null;
  }

  private async updateDeviceCounter(deviceId: string, counter: number): Promise<void> {
    // Implementation would update device counter in database
  }
}