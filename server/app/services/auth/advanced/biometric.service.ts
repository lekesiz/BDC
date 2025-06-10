import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
  VerifiedRegistrationResponse,
  VerifiedAuthenticationResponse,
} from '@simplewebauthn/server';
import {
  PublicKeyCredentialCreationOptionsJSON,
  PublicKeyCredentialRequestOptionsJSON,
  RegistrationResponseJSON,
  AuthenticationResponseJSON,
  AuthenticatorDevice,
} from '@simplewebauthn/typescript-types';
import { randomBytes } from 'crypto';

export interface BiometricDevice {
  id: string;
  userId: string;
  credentialId: string;
  credentialPublicKey: Buffer;
  counter: number;
  deviceType: string;
  transports?: AuthenticatorTransport[];
  aaguid?: string;
  createdAt: Date;
  lastUsedAt: Date;
  name?: string;
}

export interface BiometricChallenge {
  userId: string;
  challenge: string;
  type: 'registration' | 'authentication';
  expiresAt: Date;
}

@Injectable()
export class BiometricService {
  private readonly rpName: string;
  private readonly rpId: string;
  private readonly origin: string;
  private challenges: Map<string, BiometricChallenge> = new Map();

  constructor(private configService: ConfigService) {
    this.rpName = this.configService.get('WEBAUTHN_RP_NAME', 'BDC Platform');
    this.rpId = this.configService.get('WEBAUTHN_RP_ID', 'localhost');
    this.origin = this.configService.get('WEBAUTHN_ORIGIN', 'http://localhost:3000');
  }

  /**
   * Generate registration options for WebAuthn
   */
  async generateRegistrationOptions(
    userId: string,
    userName: string,
    userDisplayName: string,
    existingDevices: AuthenticatorDevice[] = []
  ): Promise<PublicKeyCredentialCreationOptionsJSON> {
    const options = await generateRegistrationOptions({
      rpName: this.rpName,
      rpID: this.rpId,
      userID: userId,
      userName,
      userDisplayName,
      attestationType: 'direct',
      excludeCredentials: existingDevices.map(device => ({
        id: device.credentialID,
        type: 'public-key',
        transports: device.transports,
      })),
      authenticatorSelection: {
        authenticatorAttachment: 'platform', // Prefer platform authenticators (biometric)
        requireResidentKey: false,
        userVerification: 'required',
      },
      supportedAlgorithmIDs: [-7, -257], // ES256, RS256
    });

    // Store challenge for verification
    this.storeChallenge(userId, options.challenge, 'registration');

    return options;
  }

  /**
   * Verify registration response
   */
  async verifyRegistrationResponse(
    userId: string,
    response: RegistrationResponseJSON
  ): Promise<{ verified: boolean; device?: AuthenticatorDevice }> {
    const challenge = this.getChallenge(userId, 'registration');
    if (!challenge) {
      throw new Error('No registration challenge found');
    }

    let verification: VerifiedRegistrationResponse;
    try {
      verification = await verifyRegistrationResponse({
        response,
        expectedChallenge: challenge,
        expectedOrigin: this.origin,
        expectedRPID: this.rpId,
        requireUserVerification: true,
      });
    } catch (error) {
      console.error('Registration verification failed:', error);
      return { verified: false };
    }

    if (!verification.verified || !verification.registrationInfo) {
      return { verified: false };
    }

    const { credentialPublicKey, credentialID, counter, aaguid } = verification.registrationInfo;

    const device: AuthenticatorDevice = {
      credentialID: Buffer.from(credentialID),
      credentialPublicKey,
      counter,
      transports: response.response.transports,
      aaguid,
    };

    // Clear used challenge
    this.clearChallenge(userId, 'registration');

    return { verified: true, device };
  }

  /**
   * Generate authentication options
   */
  async generateAuthenticationOptions(
    userId: string,
    userDevices: AuthenticatorDevice[]
  ): Promise<PublicKeyCredentialRequestOptionsJSON> {
    const options = await generateAuthenticationOptions({
      rpID: this.rpId,
      allowCredentials: userDevices.map(device => ({
        id: device.credentialID,
        type: 'public-key',
        transports: device.transports,
      })),
      userVerification: 'required',
    });

    // Store challenge for verification
    this.storeChallenge(userId, options.challenge, 'authentication');

    return options;
  }

  /**
   * Verify authentication response
   */
  async verifyAuthenticationResponse(
    userId: string,
    response: AuthenticationResponseJSON,
    device: AuthenticatorDevice
  ): Promise<{ verified: boolean; newCounter?: number }> {
    const challenge = this.getChallenge(userId, 'authentication');
    if (!challenge) {
      throw new Error('No authentication challenge found');
    }

    let verification: VerifiedAuthenticationResponse;
    try {
      verification = await verifyAuthenticationResponse({
        response,
        expectedChallenge: challenge,
        expectedOrigin: this.origin,
        expectedRPID: this.rpId,
        authenticator: {
          credentialID: device.credentialID,
          credentialPublicKey: device.credentialPublicKey,
          counter: device.counter,
          transports: device.transports,
        },
        requireUserVerification: true,
      });
    } catch (error) {
      console.error('Authentication verification failed:', error);
      return { verified: false };
    }

    if (!verification.verified) {
      return { verified: false };
    }

    // Clear used challenge
    this.clearChallenge(userId, 'authentication');

    return {
      verified: true,
      newCounter: verification.authenticationInfo.newCounter,
    };
  }

  /**
   * Store challenge for later verification
   */
  private storeChallenge(
    userId: string,
    challenge: string,
    type: 'registration' | 'authentication'
  ): void {
    const key = `${userId}-${type}`;
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000); // 5 minutes

    this.challenges.set(key, {
      userId,
      challenge,
      type,
      expiresAt,
    });

    // Clean up expired challenges
    this.cleanupExpiredChallenges();
  }

  /**
   * Retrieve stored challenge
   */
  private getChallenge(
    userId: string,
    type: 'registration' | 'authentication'
  ): string | null {
    const key = `${userId}-${type}`;
    const challenge = this.challenges.get(key);

    if (!challenge) {
      return null;
    }

    if (new Date() > challenge.expiresAt) {
      this.challenges.delete(key);
      return null;
    }

    return challenge.challenge;
  }

  /**
   * Clear stored challenge
   */
  private clearChallenge(
    userId: string,
    type: 'registration' | 'authentication'
  ): void {
    const key = `${userId}-${type}`;
    this.challenges.delete(key);
  }

  /**
   * Clean up expired challenges
   */
  private cleanupExpiredChallenges(): void {
    const now = new Date();
    
    for (const [key, challenge] of this.challenges.entries()) {
      if (now > challenge.expiresAt) {
        this.challenges.delete(key);
      }
    }
  }

  /**
   * Generate device-specific options for mobile biometric authentication
   */
  generateMobileBiometricOptions(userId: string, platform: 'ios' | 'android'): {
    challenge: string;
    timeout: number;
    userVerification: string;
    attestation: string;
  } {
    const challenge = randomBytes(32).toString('base64url');
    
    // Store challenge for mobile verification
    this.storeChallenge(userId, challenge, 'authentication');

    return {
      challenge,
      timeout: 300000, // 5 minutes
      userVerification: 'required',
      attestation: platform === 'ios' ? 'direct' : 'none',
    };
  }

  /**
   * Verify mobile biometric response
   */
  async verifyMobileBiometric(
    userId: string,
    signature: string,
    publicKey: string,
    challenge: string
  ): Promise<boolean> {
    const storedChallenge = this.getChallenge(userId, 'authentication');
    
    if (!storedChallenge || storedChallenge !== challenge) {
      return false;
    }

    // Verify signature using public key
    // This is a simplified example - actual implementation would use
    // platform-specific verification methods
    
    // Clear used challenge
    this.clearChallenge(userId, 'authentication');

    return true;
  }

  /**
   * Check if biometric authentication is available
   */
  async checkBiometricAvailability(): Promise<{
    available: boolean;
    platform?: string;
    authenticators?: string[];
  }> {
    // This would be implemented on the client side
    // Server returns configuration for client to check
    return {
      available: true,
      platform: 'webauthn',
      authenticators: ['platform', 'cross-platform'],
    };
  }

  /**
   * Get device type from AAGUID
   */
  getDeviceType(aaguid?: string): string {
    if (!aaguid) return 'Unknown';

    // Map of known AAGUIDs to device types
    const aaguidMap: Record<string, string> = {
      'd8522d9f-575b-4866-88a9-ba99fa02f35b': 'Touch ID',
      'fbfc3007-154e-4ecc-8c0b-6e020557d7bd': 'Face ID',
      '53414d53-554e-4700-0000-000000000000': 'Samsung Biometric',
      '39a5647e-1853-446c-a1f6-a79bae9f5bc7': 'Windows Hello',
    };

    return aaguidMap[aaguid] || 'Platform Authenticator';
  }
}