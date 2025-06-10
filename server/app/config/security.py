"""Security configuration for BDC application."""

import os
from typing import List, Dict

class SecurityConfig:
    """Security configuration settings."""
    
    # IP Whitelisting
    ENABLE_IP_WHITELIST = os.environ.get('ENABLE_IP_WHITELIST', 'false').lower() == 'true'
    IP_WHITELIST = os.environ.get('IP_WHITELIST', '0.0.0.0/0').split(',')
    ADMIN_IP_WHITELIST = os.environ.get('ADMIN_IP_WHITELIST', '').split(',') if os.environ.get('ADMIN_IP_WHITELIST') else []
    
    # Threat Detection
    ENABLE_THREAT_DETECTION = os.environ.get('ENABLE_THREAT_DETECTION', 'true').lower() == 'true'
    THREAT_DETECTION_SENSITIVITY = os.environ.get('THREAT_DETECTION_SENSITIVITY', 'medium')  # low, medium, high
    
    # Rate Limiting (requests per minute)
    RATE_LIMITS = {
        'default': int(os.environ.get('RATE_LIMIT_DEFAULT', '100')),
        'login': int(os.environ.get('RATE_LIMIT_LOGIN', '5')),
        'register': int(os.environ.get('RATE_LIMIT_REGISTER', '3')),
        'api': int(os.environ.get('RATE_LIMIT_API', '60')),
        'strict': int(os.environ.get('RATE_LIMIT_STRICT', '10'))  # For suspicious IPs
    }
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
    }
    
    # Session Security
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME', '3600'))  # 1 hour
    
    # Password Policy
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '8'))
    PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true'
    PASSWORD_REQUIRE_DIGITS = os.environ.get('PASSWORD_REQUIRE_DIGITS', 'true').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'true').lower() == 'true'
    PASSWORD_HISTORY_COUNT = int(os.environ.get('PASSWORD_HISTORY_COUNT', '5'))
    
    # Account Security
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    ACCOUNT_LOCKOUT_DURATION = int(os.environ.get('ACCOUNT_LOCKOUT_DURATION', '900'))  # 15 minutes
    REQUIRE_EMAIL_VERIFICATION = os.environ.get('REQUIRE_EMAIL_VERIFICATION', 'true').lower() == 'true'
    
    # API Security
    API_KEY_HEADER = os.environ.get('API_KEY_HEADER', 'X-API-Key')
    REQUIRE_API_KEY = os.environ.get('REQUIRE_API_KEY', 'false').lower() == 'true'
    
    # File Upload Security
    ALLOWED_EXTENSIONS = {
        'document': ['pdf', 'doc', 'docx', 'txt', 'odt'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'spreadsheet': ['xls', 'xlsx', 'csv', 'ods'],
        'presentation': ['ppt', 'pptx', 'odp']
    }
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', str(10 * 1024 * 1024)))  # 10MB default
    SCAN_UPLOADS = os.environ.get('SCAN_UPLOADS', 'true').lower() == 'true'
    
    # Audit and Logging
    ENABLE_AUDIT_LOGGING = os.environ.get('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    LOG_SECURITY_EVENTS = os.environ.get('LOG_SECURITY_EVENTS', 'true').lower() == 'true'
    AUDIT_LOG_RETENTION_DAYS = int(os.environ.get('AUDIT_LOG_RETENTION_DAYS', '90'))
    
    # Multi-Factor Authentication
    ENABLE_MFA = os.environ.get('ENABLE_MFA', 'false').lower() == 'true'
    MFA_ISSUER_NAME = os.environ.get('MFA_ISSUER_NAME', 'BDC Platform')
    
    # CORS Settings (already in main config, but security-specific here)
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    CORS_ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOWED_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']
    
    @classmethod
    def get_security_config(cls) -> Dict:
        """Get all security configuration as dictionary."""
        return {
            'ip_whitelist': {
                'enabled': cls.ENABLE_IP_WHITELIST,
                'whitelist': cls.IP_WHITELIST,
                'admin_whitelist': cls.ADMIN_IP_WHITELIST
            },
            'threat_detection': {
                'enabled': cls.ENABLE_THREAT_DETECTION,
                'sensitivity': cls.THREAT_DETECTION_SENSITIVITY
            },
            'rate_limits': cls.RATE_LIMITS,
            'security_headers': cls.SECURITY_HEADERS,
            'session': {
                'secure': cls.SESSION_COOKIE_SECURE,
                'httponly': cls.SESSION_COOKIE_HTTPONLY,
                'samesite': cls.SESSION_COOKIE_SAMESITE,
                'lifetime': cls.PERMANENT_SESSION_LIFETIME
            },
            'password_policy': {
                'min_length': cls.PASSWORD_MIN_LENGTH,
                'require_uppercase': cls.PASSWORD_REQUIRE_UPPERCASE,
                'require_lowercase': cls.PASSWORD_REQUIRE_LOWERCASE,
                'require_digits': cls.PASSWORD_REQUIRE_DIGITS,
                'require_special': cls.PASSWORD_REQUIRE_SPECIAL,
                'history_count': cls.PASSWORD_HISTORY_COUNT
            },
            'account_security': {
                'max_login_attempts': cls.MAX_LOGIN_ATTEMPTS,
                'lockout_duration': cls.ACCOUNT_LOCKOUT_DURATION,
                'require_email_verification': cls.REQUIRE_EMAIL_VERIFICATION
            },
            'file_upload': {
                'allowed_extensions': cls.ALLOWED_EXTENSIONS,
                'max_size': cls.MAX_FILE_SIZE,
                'scan_enabled': cls.SCAN_UPLOADS
            },
            'audit': {
                'enabled': cls.ENABLE_AUDIT_LOGGING,
                'log_security_events': cls.LOG_SECURITY_EVENTS,
                'retention_days': cls.AUDIT_LOG_RETENTION_DAYS
            },
            'mfa': {
                'enabled': cls.ENABLE_MFA,
                'issuer': cls.MFA_ISSUER_NAME
            }
        }