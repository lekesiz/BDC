import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as speakeasy from 'speakeasy';
import * as QRCode from 'qrcode';
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

export interface MFASecret {
  userId: string;
  secret: string;
  backupCodes: string[];
  createdAt: Date;
  verified: boolean;
}

export interface MFAVerificationResult {
  valid: boolean;
  remainingBackupCodes?: number;
}

@Injectable()
export class MFAService {
  private readonly encryptionKey: Buffer;
  private readonly algorithm = 'aes-256-gcm';

  constructor(private configService: ConfigService) {
    const key = this.configService.get<string>('MFA_ENCRYPTION_KEY');
    if (!key || key.length !== 64) {
      throw new Error('MFA_ENCRYPTION_KEY must be 32 bytes (64 hex characters)');
    }
    this.encryptionKey = Buffer.from(key, 'hex');
  }

  /**
   * Generate a new TOTP secret for a user
   */
  async generateSecret(userId: string, userEmail: string): Promise<{
    secret: string;
    qrCode: string;
    backupCodes: string[];
  }> {
    const secret = speakeasy.generateSecret({
      name: `BDC (${userEmail})`,
      issuer: 'BDC Platform',
      length: 32,
    });

    // Generate backup codes
    const backupCodes = this.generateBackupCodes(8);

    // Generate QR code
    const qrCode = await QRCode.toDataURL(secret.otpauth_url);

    return {
      secret: this.encryptSecret(secret.base32),
      qrCode,
      backupCodes: backupCodes.map(code => this.encryptSecret(code)),
    };
  }

  /**
   * Verify a TOTP token
   */
  verifyToken(encryptedSecret: string, token: string): boolean {
    const secret = this.decryptSecret(encryptedSecret);
    
    return speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window: 2, // Allow 2 time steps before/after for clock drift
    });
  }

  /**
   * Verify a backup code
   */
  verifyBackupCode(
    encryptedBackupCodes: string[],
    code: string
  ): { valid: boolean; remainingCodes: string[] } {
    const decryptedCodes = encryptedBackupCodes.map(c => this.decryptSecret(c));
    const codeIndex = decryptedCodes.indexOf(code);

    if (codeIndex === -1) {
      return { valid: false, remainingCodes: encryptedBackupCodes };
    }

    // Remove used backup code
    const remainingCodes = [...encryptedBackupCodes];
    remainingCodes.splice(codeIndex, 1);

    return { valid: true, remainingCodes };
  }

  /**
   * Generate new backup codes
   */
  generateBackupCodes(count: number = 8): string[] {
    const codes: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const code = this.generateSecureCode();
      codes.push(code);
    }

    return codes;
  }

  /**
   * Encrypt a secret using AES-256-GCM
   */
  private encryptSecret(secret: string): string {
    const iv = randomBytes(16);
    const cipher = createCipheriv(this.algorithm, this.encryptionKey, iv);
    
    const encrypted = Buffer.concat([
      cipher.update(secret, 'utf8'),
      cipher.final(),
    ]);
    
    const authTag = cipher.getAuthTag();
    
    // Combine iv, authTag, and encrypted data
    const combined = Buffer.concat([iv, authTag, encrypted]);
    
    return combined.toString('base64');
  }

  /**
   * Decrypt a secret using AES-256-GCM
   */
  private decryptSecret(encryptedSecret: string): string {
    const combined = Buffer.from(encryptedSecret, 'base64');
    
    // Extract components
    const iv = combined.slice(0, 16);
    const authTag = combined.slice(16, 32);
    const encrypted = combined.slice(32);
    
    const decipher = createDecipheriv(this.algorithm, this.encryptionKey, iv);
    decipher.setAuthTag(authTag);
    
    const decrypted = Buffer.concat([
      decipher.update(encrypted),
      decipher.final(),
    ]);
    
    return decrypted.toString('utf8');
  }

  /**
   * Generate a secure backup code
   */
  private generateSecureCode(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    const codeLength = 8;
    let code = '';
    
    const randomValues = randomBytes(codeLength);
    
    for (let i = 0; i < codeLength; i++) {
      code += chars[randomValues[i] % chars.length];
      if (i === 3) code += '-'; // Add hyphen for readability
    }
    
    return code;
  }

  /**
   * Validate MFA configuration
   */
  validateMFAConfig(mfaSecret: MFASecret): boolean {
    if (!mfaSecret.verified) {
      return false;
    }

    // Check if secret is not too old (optional security measure)
    const maxAge = 365 * 24 * 60 * 60 * 1000; // 1 year
    const age = Date.now() - mfaSecret.createdAt.getTime();
    
    if (age > maxAge) {
      return false;
    }

    return true;
  }

  /**
   * Generate recovery codes for account recovery
   */
  generateRecoveryCodes(count: number = 16): string[] {
    const codes: string[] = [];
    const usedCodes = new Set<string>();
    
    while (codes.length < count) {
      const code = this.generateSecureCode();
      
      // Ensure uniqueness
      if (!usedCodes.has(code)) {
        usedCodes.add(code);
        codes.push(code);
      }
    }
    
    return codes;
  }
}