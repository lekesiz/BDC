// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Frontend Security Module
 * Comprehensive client-side security utilities and protections
 */
export { default as SecurityProvider } from './SecurityProvider';
export { default as InputSanitizer } from './InputSanitizer';
export { default as CSPHelper } from './CSPHelper';
export { default as SecureStorage } from './SecureStorage';
export { default as XSSProtection } from './XSSProtection';
export { default as AuthSecurity } from './AuthSecurity';
export { default as PrivacyManager } from './PrivacyManager';
export { default as SecurityMonitor } from './SecurityMonitor';
// Security hooks
export { useSecureAPI } from './hooks/useSecureAPI';
export { useInputValidation } from './hooks/useInputValidation';
export { useCSRFToken } from './hooks/useCSRFToken';
export { useSecurityContext } from './hooks/useSecurityContext';
// Security utilities
export * from './utils/validation';
export * from './utils/encryption';
export * from './utils/sanitization';
export * from './utils/security-headers';