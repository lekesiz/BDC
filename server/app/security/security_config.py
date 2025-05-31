"""
Enhanced security configuration for production deployment.
"""

import os
import secrets
from datetime import timedelta
from typing import Dict, List, Any

class SecurityConfig:
    """Enhanced security configuration for production."""
    
    # Password Policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    PASSWORD_MAX_AGE_DAYS = 90
    PASSWORD_HISTORY_COUNT = 12
    PASSWORD_LOCKOUT_ATTEMPTS = 5
    PASSWORD_LOCKOUT_DURATION = timedelta(minutes=30)
    
    # Session Security
    SESSION_TIMEOUT = timedelta(hours=2)
    SESSION_REGENERATE_ON_LOGIN = True
    SESSION_INVALIDATE_ON_LOGOUT = True
    SESSION_SECURE_COOKIES = True
    SESSION_HTTPONLY_COOKIES = True
    SESSION_SAMESITE = 'Strict'
    
    # JWT Security
    JWT_ALGORITHM = 'RS256'  # Use RSA instead of HMAC for better security
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_ISSUER = 'bdc-application'
    JWT_AUDIENCE = 'bdc-users'
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = "100/hour"
    RATE_LIMIT_LOGIN = "5/minute"
    RATE_LIMIT_API = "1000/hour"
    RATE_LIMIT_UPLOAD = "10/minute"
    RATE_LIMIT_PASSWORD_RESET = "3/hour"
    
    # Input Validation
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_JSON_PAYLOAD_SIZE = 1024 * 1024  # 1MB
    MAX_FORM_FIELDS = 100
    MAX_STRING_LENGTH = 10000
    
    # File Upload Security
    ALLOWED_FILE_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
        'spreadsheet': ['xls', 'xlsx', 'csv'],
        'presentation': ['ppt', 'pptx']
    }
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    UPLOAD_SCAN_ENABLED = True
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'accelerometer=()'
        ),
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
    }
    
    # CORS Security
    CORS_ORIGINS = []  # Must be explicitly set in production
    CORS_ALLOW_CREDENTIALS = True
    CORS_MAX_AGE = 86400  # 24 hours
    
    # Database Security
    DB_ENCRYPTION_KEY = None  # Set from environment
    DB_CONNECTION_TIMEOUT = 30
    DB_QUERY_TIMEOUT = 60
    DB_MAX_CONNECTIONS = 20
    
    # Audit and Logging
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_RETENTION_DAYS = 90
    SECURITY_LOG_LEVEL = 'INFO'
    
    # IP Whitelisting
    ADMIN_IP_WHITELIST = []  # Must be set in production
    API_IP_WHITELIST = []    # Optional API IP restrictions
    
    # Environment-based configuration
    @classmethod
    def load_from_env(cls) -> Dict[str, Any]:
        """Load security configuration from environment variables."""
        return {
            'SECRET_KEY': os.getenv('SECRET_KEY') or secrets.token_urlsafe(32),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY') or secrets.token_urlsafe(32),
            'JWT_PRIVATE_KEY': os.getenv('JWT_PRIVATE_KEY'),
            'JWT_PUBLIC_KEY': os.getenv('JWT_PUBLIC_KEY'),
            'DB_ENCRYPTION_KEY': os.getenv('DB_ENCRYPTION_KEY'),
            'CORS_ORIGINS': os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else [],
            'ADMIN_IP_WHITELIST': os.getenv('ADMIN_IP_WHITELIST', '').split(',') if os.getenv('ADMIN_IP_WHITELIST') else [],
            'API_IP_WHITELIST': os.getenv('API_IP_WHITELIST', '').split(',') if os.getenv('API_IP_WHITELIST') else [],
            'TRUSTED_PROXIES': os.getenv('TRUSTED_PROXIES', '').split(',') if os.getenv('TRUSTED_PROXIES') else [],
        }
    
    @classmethod
    def validate_production_config(cls) -> List[str]:
        """Validate that all required security settings are configured for production."""
        errors = []
        
        required_env_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL',
            'REDIS_URL'
        ]
        
        for var in required_env_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
        
        # Check for default/weak values
        if os.getenv('SECRET_KEY') == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY is still set to default development value")
        
        if os.getenv('JWT_SECRET_KEY') == 'jwt-secret-key-change-in-production':
            errors.append("JWT_SECRET_KEY is still set to default development value")
        
        # Validate CORS origins
        cors_origins = cls.load_from_env().get('CORS_ORIGINS', [])
        if '*' in cors_origins:
            errors.append("CORS origins should not include '*' in production")
        
        return errors