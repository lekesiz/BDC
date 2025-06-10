# Advanced Authentication System

This comprehensive authentication system provides enterprise-grade security features including Multi-Factor Authentication (MFA), Single Sign-On (SSO), biometric authentication, and advanced session management.

## Features

### 1. Multi-Factor Authentication (MFA)
- **TOTP-based 2FA**: Time-based One-Time Password implementation using industry-standard algorithms
- **Backup codes**: Secure recovery codes for account access when primary MFA device is unavailable
- **Encrypted storage**: All MFA secrets are encrypted using AES-256-GCM
- **QR code generation**: Easy setup process for authenticator apps

### 2. Single Sign-On (SSO)
- **OAuth2 Providers**:
  - Google authentication
  - Microsoft/Azure AD authentication
- **SAML 2.0**: Enterprise SAML integration support
- **Account linking**: Link multiple SSO providers to a single user account
- **State validation**: CSRF protection for OAuth flows

### 3. Biometric Authentication
- **WebAuthn/FIDO2**: Platform authenticator support (Touch ID, Face ID, Windows Hello)
- **Device management**: Register and manage multiple biometric devices
- **Mobile support**: Native biometric authentication for iOS and Android
- **Attestation verification**: Cryptographic proof of authenticator legitimacy

### 4. Advanced Session Management
- **Redis-based sessions**: High-performance session storage
- **Device tracking**: Identify and manage devices across sessions
- **Location awareness**: GeoIP-based location tracking for security monitoring
- **Session elevation**: Temporary privilege elevation for sensitive operations
- **Activity logging**: Comprehensive session activity tracking
- **Suspicious activity detection**: Automatic detection of anomalous behavior

### 5. Unified Authentication Flow
- **Flexible authentication**: Support for multiple authentication methods
- **Step-based flow**: Guided authentication process with clear state management
- **Rate limiting**: Built-in protection against brute force attacks
- **Event-driven architecture**: Real-time authentication events for monitoring

## Installation

```bash
npm install speakeasy qrcode google-auth-library @microsoft/microsoft-graph-client @azure/msal-node saml2-js @simplewebauthn/server ioredis geoip-lite useragent
```

## Configuration

Add the following environment variables to your `.env` file:

```env
# MFA Configuration
MFA_ENCRYPTION_KEY=your-32-byte-hex-key # Generate with: openssl rand -hex 32

# SSO Configuration
SSO_GOOGLE_CLIENT_ID=your-google-client-id
SSO_GOOGLE_CLIENT_SECRET=your-google-client-secret
SSO_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

SSO_MICROSOFT_CLIENT_ID=your-microsoft-client-id
SSO_MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
SSO_MICROSOFT_TENANT_ID=your-tenant-id
SSO_MICROSOFT_REDIRECT_URI=http://localhost:3000/auth/microsoft/callback

SSO_SAML_ENTRY_POINT=https://your-idp.com/sso/saml
SSO_SAML_ISSUER=your-app-entity-id
SSO_SAML_CERT=your-saml-certificate
SSO_SAML_PRIVATE_KEY=your-saml-private-key

# WebAuthn Configuration
WEBAUTHN_RP_NAME=BDC Platform
WEBAUTHN_RP_ID=localhost
WEBAUTHN_ORIGIN=http://localhost:3000

# Session Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# JWT Configuration
JWT_ACCESS_SECRET=your-access-token-secret
JWT_REFRESH_SECRET=your-refresh-token-secret

# Application Configuration
APP_URL=http://localhost:3000
```

## Usage

### Import the Module

```typescript
import { AdvancedAuthModule } from './app/services/auth/advanced/auth.module';

@Module({
  imports: [AdvancedAuthModule],
})
export class AppModule {}
```

### Authentication Flow Example

```typescript
import { Controller, Post, Body, Req } from '@nestjs/common';
import { AuthFlowService, AuthMethod } from './auth-flow.service';

@Controller('auth')
export class AuthController {
  constructor(private authFlowService: AuthFlowService) {}

  @Post('login')
  async login(@Body() body: any, @Req() request: Request) {
    // Initialize authentication flow
    const flow = await this.authFlowService.initializeFlow(
      AuthMethod.PASSWORD,
      request,
      { rememberMe: body.rememberMe }
    );

    // Process credentials
    if (flow.nextStep === 'credentials') {
      return this.authFlowService.processCredentials(
        flow.flowId,
        { username: body.username, password: body.password },
        request
      );
    }

    return flow;
  }

  @Post('mfa/verify')
  async verifyMFA(@Body() body: any, @Req() request: Request) {
    return this.authFlowService.processMFAVerification(
      body.flowId,
      body.method,
      body.code,
      request
    );
  }
}
```

### MFA Setup Example

```typescript
import { MFAService } from './mfa.service';

// Generate MFA secret for user
const { secret, qrCode, backupCodes } = await mfaService.generateSecret(
  userId,
  userEmail
);

// Display QR code to user for scanning with authenticator app
// Store encrypted secret and backup codes in database

// Verify TOTP token
const isValid = mfaService.verifyToken(encryptedSecret, userToken);
```

### SSO Integration Example

```typescript
import { SSOService } from './sso.service';

// Generate Google OAuth URL
const state = ssoService.generateState();
const authUrl = ssoService.getGoogleAuthUrl(state);
// Redirect user to authUrl

// Handle OAuth callback
const profile = await ssoService.handleGoogleCallback(code);
// Create or update user based on profile
```

### Biometric Registration Example

```typescript
import { BiometricService } from './biometric.service';

// Generate registration options
const options = await biometricService.generateRegistrationOptions(
  userId,
  userName,
  userDisplayName
);

// Send options to client for WebAuthn registration
// Client performs registration and sends response

// Verify registration
const result = await biometricService.verifyRegistrationResponse(
  userId,
  registrationResponse
);

if (result.verified) {
  // Store device information in database
}
```

## Security Best Practices

1. **Environment Variables**: Never commit sensitive configuration to version control
2. **HTTPS Only**: Always use HTTPS in production for all authentication endpoints
3. **Rate Limiting**: Implement rate limiting on all authentication endpoints
4. **Audit Logging**: Log all authentication events for security monitoring
5. **Regular Updates**: Keep all dependencies updated for security patches
6. **Session Timeout**: Configure appropriate session timeouts based on security requirements
7. **CORS Configuration**: Properly configure CORS for your authentication endpoints

## Database Schema

You'll need to create the following tables to support the authentication system:

```sql
-- MFA Secrets
CREATE TABLE user_mfa_secrets (
  user_id UUID PRIMARY KEY,
  secret TEXT NOT NULL,
  backup_codes TEXT[],
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SSO Links
CREATE TABLE user_sso_links (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  provider VARCHAR(50) NOT NULL,
  provider_user_id VARCHAR(255) NOT NULL,
  profile_data JSONB,
  linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(provider, provider_user_id)
);

-- Biometric Devices
CREATE TABLE user_biometric_devices (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  credential_id TEXT NOT NULL,
  credential_public_key BYTEA NOT NULL,
  counter INTEGER NOT NULL,
  device_type VARCHAR(100),
  transports TEXT[],
  aaguid VARCHAR(100),
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_sso_links_user_id ON user_sso_links(user_id);
CREATE INDEX idx_biometric_devices_user_id ON user_biometric_devices(user_id);
CREATE INDEX idx_biometric_devices_credential_id ON user_biometric_devices(credential_id);
```

## Monitoring and Analytics

The authentication system emits the following events that can be used for monitoring:

- `auth.flow.started`: Authentication flow initiated
- `auth.flow.completed`: Successful authentication
- `auth.flow.failed`: Failed authentication attempt
- `auth.mfa.enabled`: MFA enabled for user
- `auth.sso.linked`: SSO account linked
- `auth.biometric.registered`: Biometric device registered
- `auth.session.created`: New session created
- `auth.session.terminated`: Session terminated
- `auth.suspicious.activity`: Suspicious activity detected

## Testing

The system includes comprehensive error handling and validation. When testing:

1. Test each authentication method independently
2. Verify MFA flows with correct and incorrect codes
3. Test SSO integration with provider sandboxes
4. Use WebAuthn testing tools for biometric flows
5. Monitor Redis for proper session management
6. Verify security events are properly emitted

## Support

For issues or questions:
1. Check environment variable configuration
2. Verify Redis connectivity
3. Ensure all npm dependencies are installed
4. Check application logs for detailed error messages
5. Verify database schema matches requirements