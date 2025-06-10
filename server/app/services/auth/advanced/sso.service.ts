import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { OAuth2Client } from 'google-auth-library';
import { Client as MicrosoftClient } from '@microsoft/microsoft-graph-client';
import { ConfidentialClientApplication } from '@azure/msal-node';
import * as saml2 from 'saml2-js';
import { createHash } from 'crypto';

export interface SSOProvider {
  id: string;
  name: string;
  type: 'oauth2' | 'saml';
  enabled: boolean;
}

export interface SSOUserProfile {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  displayName?: string;
  avatar?: string;
  provider: string;
  rawProfile?: any;
}

export interface SSOConfig {
  google?: {
    clientId: string;
    clientSecret: string;
    redirectUri: string;
  };
  microsoft?: {
    clientId: string;
    clientSecret: string;
    tenantId: string;
    redirectUri: string;
  };
  saml?: {
    entryPoint: string;
    issuer: string;
    cert: string;
    privateKey: string;
  };
}

@Injectable()
export class SSOService {
  private googleClient: OAuth2Client;
  private microsoftClient: ConfidentialClientApplication;
  private samlServiceProvider: any;
  private ssoConfig: SSOConfig;

  constructor(private configService: ConfigService) {
    this.initializeProviders();
  }

  private initializeProviders() {
    this.ssoConfig = {
      google: {
        clientId: this.configService.get('SSO_GOOGLE_CLIENT_ID'),
        clientSecret: this.configService.get('SSO_GOOGLE_CLIENT_SECRET'),
        redirectUri: this.configService.get('SSO_GOOGLE_REDIRECT_URI'),
      },
      microsoft: {
        clientId: this.configService.get('SSO_MICROSOFT_CLIENT_ID'),
        clientSecret: this.configService.get('SSO_MICROSOFT_CLIENT_SECRET'),
        tenantId: this.configService.get('SSO_MICROSOFT_TENANT_ID'),
        redirectUri: this.configService.get('SSO_MICROSOFT_REDIRECT_URI'),
      },
      saml: {
        entryPoint: this.configService.get('SSO_SAML_ENTRY_POINT'),
        issuer: this.configService.get('SSO_SAML_ISSUER'),
        cert: this.configService.get('SSO_SAML_CERT'),
        privateKey: this.configService.get('SSO_SAML_PRIVATE_KEY'),
      },
    };

    // Initialize Google OAuth2 client
    if (this.ssoConfig.google?.clientId) {
      this.googleClient = new OAuth2Client(
        this.ssoConfig.google.clientId,
        this.ssoConfig.google.clientSecret,
        this.ssoConfig.google.redirectUri
      );
    }

    // Initialize Microsoft MSAL client
    if (this.ssoConfig.microsoft?.clientId) {
      this.microsoftClient = new ConfidentialClientApplication({
        auth: {
          clientId: this.ssoConfig.microsoft.clientId,
          clientSecret: this.ssoConfig.microsoft.clientSecret,
          authority: `https://login.microsoftonline.com/${this.ssoConfig.microsoft.tenantId}`,
        },
      });
    }

    // Initialize SAML service provider
    if (this.ssoConfig.saml?.issuer) {
      this.samlServiceProvider = new saml2.ServiceProvider({
        entity_id: this.ssoConfig.saml.issuer,
        private_key: this.ssoConfig.saml.privateKey,
        certificate: this.ssoConfig.saml.cert,
        assert_endpoint: `${this.configService.get('APP_URL')}/auth/saml/callback`,
      });
    }
  }

  /**
   * Get available SSO providers
   */
  getAvailableProviders(): SSOProvider[] {
    const providers: SSOProvider[] = [];

    if (this.ssoConfig.google?.clientId) {
      providers.push({
        id: 'google',
        name: 'Google',
        type: 'oauth2',
        enabled: true,
      });
    }

    if (this.ssoConfig.microsoft?.clientId) {
      providers.push({
        id: 'microsoft',
        name: 'Microsoft',
        type: 'oauth2',
        enabled: true,
      });
    }

    if (this.ssoConfig.saml?.issuer) {
      providers.push({
        id: 'saml',
        name: 'SAML',
        type: 'saml',
        enabled: true,
      });
    }

    return providers;
  }

  /**
   * Generate Google OAuth2 authorization URL
   */
  getGoogleAuthUrl(state: string): string {
    if (!this.googleClient) {
      throw new Error('Google SSO not configured');
    }

    return this.googleClient.generateAuthUrl({
      access_type: 'offline',
      scope: [
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
      ],
      state,
    });
  }

  /**
   * Handle Google OAuth2 callback
   */
  async handleGoogleCallback(code: string): Promise<SSOUserProfile> {
    if (!this.googleClient) {
      throw new Error('Google SSO not configured');
    }

    const { tokens } = await this.googleClient.getToken(code);
    this.googleClient.setCredentials(tokens);

    const ticket = await this.googleClient.verifyIdToken({
      idToken: tokens.id_token,
      audience: this.ssoConfig.google.clientId,
    });

    const payload = ticket.getPayload();

    return {
      id: payload.sub,
      email: payload.email,
      firstName: payload.given_name,
      lastName: payload.family_name,
      displayName: payload.name,
      avatar: payload.picture,
      provider: 'google',
      rawProfile: payload,
    };
  }

  /**
   * Generate Microsoft OAuth2 authorization URL
   */
  async getMicrosoftAuthUrl(state: string): Promise<string> {
    if (!this.microsoftClient) {
      throw new Error('Microsoft SSO not configured');
    }

    const authCodeUrlParameters = {
      scopes: ['user.read', 'openid', 'profile', 'email'],
      redirectUri: this.ssoConfig.microsoft.redirectUri,
      state,
    };

    const response = await this.microsoftClient.getAuthCodeUrl(authCodeUrlParameters);
    return response;
  }

  /**
   * Handle Microsoft OAuth2 callback
   */
  async handleMicrosoftCallback(code: string): Promise<SSOUserProfile> {
    if (!this.microsoftClient) {
      throw new Error('Microsoft SSO not configured');
    }

    const tokenRequest = {
      code,
      scopes: ['user.read', 'openid', 'profile', 'email'],
      redirectUri: this.ssoConfig.microsoft.redirectUri,
    };

    const response = await this.microsoftClient.acquireTokenByCode(tokenRequest);
    
    // Get user profile from Microsoft Graph
    const graphClient = MicrosoftClient.init({
      authProvider: (done) => {
        done(null, response.accessToken);
      },
    });

    const user = await graphClient.api('/me').get();

    return {
      id: user.id,
      email: user.mail || user.userPrincipalName,
      firstName: user.givenName,
      lastName: user.surname,
      displayName: user.displayName,
      avatar: null, // Microsoft Graph requires additional API call for photo
      provider: 'microsoft',
      rawProfile: user,
    };
  }

  /**
   * Generate SAML authentication request
   */
  getSAMLAuthUrl(relayState: string): string {
    if (!this.samlServiceProvider) {
      throw new Error('SAML SSO not configured');
    }

    const identityProvider = new saml2.IdentityProvider({
      sso_login_url: this.ssoConfig.saml.entryPoint,
      certificates: [this.ssoConfig.saml.cert],
    });

    const request = this.samlServiceProvider.create_login_request_url(
      identityProvider,
      {
        relay_state: relayState,
      }
    );

    return request;
  }

  /**
   * Handle SAML response
   */
  async handleSAMLResponse(samlResponse: string): Promise<SSOUserProfile> {
    if (!this.samlServiceProvider) {
      throw new Error('SAML SSO not configured');
    }

    const identityProvider = new saml2.IdentityProvider({
      sso_login_url: this.ssoConfig.saml.entryPoint,
      certificates: [this.ssoConfig.saml.cert],
    });

    return new Promise((resolve, reject) => {
      this.samlServiceProvider.post_assert(
        identityProvider,
        {
          request_body: {
            SAMLResponse: samlResponse,
          },
        },
        (err: any, samlAssertion: any) => {
          if (err) {
            reject(err);
            return;
          }

          const user = samlAssertion.user;
          
          resolve({
            id: user.name_id,
            email: user.attributes?.email || user.name_id,
            firstName: user.attributes?.firstName,
            lastName: user.attributes?.lastName,
            displayName: user.attributes?.displayName,
            provider: 'saml',
            rawProfile: user,
          });
        }
      );
    });
  }

  /**
   * Link SSO account to existing user
   */
  async linkSSOAccount(
    userId: string,
    provider: string,
    providerUserId: string,
    profile: SSOUserProfile
  ): Promise<void> {
    // Generate unique link ID
    const linkId = this.generateLinkId(provider, providerUserId);
    
    // Store the link in database
    // This would typically involve saving to a user_sso_links table
    // with columns: user_id, provider, provider_user_id, profile_data, linked_at
    
    // For now, we'll just log the action
    console.log(`Linking SSO account: User ${userId} -> ${provider}:${providerUserId}`);
  }

  /**
   * Unlink SSO account from user
   */
  async unlinkSSOAccount(userId: string, provider: string): Promise<void> {
    // Remove the link from database
    console.log(`Unlinking SSO account: User ${userId} from ${provider}`);
  }

  /**
   * Get linked SSO accounts for a user
   */
  async getLinkedAccounts(userId: string): Promise<SSOProvider[]> {
    // Query database for linked accounts
    // This is a placeholder implementation
    return [];
  }

  /**
   * Generate unique link ID for SSO accounts
   */
  private generateLinkId(provider: string, providerUserId: string): string {
    const data = `${provider}:${providerUserId}`;
    return createHash('sha256').update(data).digest('hex');
  }

  /**
   * Validate SSO state parameter
   */
  validateState(state: string, expectedState: string): boolean {
    return state === expectedState;
  }

  /**
   * Generate secure state parameter for OAuth flows
   */
  generateState(): string {
    return createHash('sha256')
      .update(`${Date.now()}-${Math.random()}`)
      .digest('hex');
  }
}