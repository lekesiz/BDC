"""
Production security configuration with comprehensive hardening.
"""

import os
import secrets
from datetime import timedelta
from typing import Dict, List, Any

class ProductionSecurityConfig:
    """Enhanced production configuration with security hardening."""
    
    # Flask Core Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False
    
    # Ensure required environment variables are set
    @classmethod
    def validate_required_env_vars(cls):
        """Validate all required environment variables are set."""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY', 
            'DATABASE_URL',
            'REDIS_URL',
            'DB_ENCRYPTION_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Database Security
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'max_overflow': 0,
        'pool_pre_ping': True,
        'connect_args': {
            'sslmode': 'require',  # Force SSL for database connections
            'connect_timeout': 10,
            'application_name': 'bdc-production'
        }
    }
    
    # Redis Security
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_SSL_CERT_REQS = 'required'
    
    # JWT Security (using RS256 for better security)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # For backward compatibility
    JWT_PRIVATE_KEY = os.getenv('JWT_PRIVATE_KEY')  # RSA private key
    JWT_PUBLIC_KEY = os.getenv('JWT_PUBLIC_KEY')   # RSA public key
    JWT_ALGORITHM = 'RS256' if os.getenv('JWT_PRIVATE_KEY') else 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ERROR_MESSAGE_KEY = 'message'
    JWT_DECODE_AUDIENCE = 'bdc-users'
    JWT_ENCODE_ISSUER = 'bdc-application'
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_NAME = '__BDC_Session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_REGENERATE_ON_LOGIN = True
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "60/minute"
    RATELIMIT_STRATEGY = "sliding-window-counter"
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_EXEMPT_WHEN = lambda: False  # No exemptions in production
    
    # CORS Security (must be explicitly configured)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    CORS_ALLOW_CREDENTIALS = True
    CORS_MAX_AGE = 86400
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Content Security Policy
    CSP_DEFAULT_SRC = "'self'"
    CSP_SCRIPT_SRC = "'self' 'unsafe-inline' https://cdn.jsdelivr.net"
    CSP_STYLE_SRC = "'self' 'unsafe-inline' https://fonts.googleapis.com"
    CSP_FONT_SRC = "'self' https://fonts.gstatic.com"
    CSP_IMG_SRC = "'self' data: https:"
    CSP_CONNECT_SRC = "'self' wss: https:"
    CSP_OBJECT_SRC = "'none'"
    CSP_BASE_URI = "'self'"
    CSP_FORM_ACTION = "'self'"
    CSP_FRAME_ANCESTORS = "'none'"
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': (
            'geolocation=(), microphone=(), camera=(), payment=(), '
            'usb=(), magnetometer=(), gyroscope=(), accelerometer=()'
        )
    }
    
    # Force HTTPS
    PREFERRED_URL_SCHEME = 'https'
    FORCE_HTTPS = True
    
    # File Upload Security
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'secure_uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'document': ['pdf', 'doc', 'docx', 'txt'],
        'spreadsheet': ['xls', 'xlsx', 'csv']
    }
    UPLOAD_VIRUS_SCAN = True
    UPLOAD_QUARANTINE_DIR = os.path.join(os.path.dirname(__file__), '..', 'quarantine')
    
    # Data Encryption
    ENCRYPTION_KEY = os.getenv('DB_ENCRYPTION_KEY')
    FIELD_ENCRYPTION_ENABLED = True
    
    # Password Policy
    PASSWORD_POLICY = {
        'min_length': 12,
        'max_length': 128,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_digits': True,
        'require_special': True,
        'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
        'max_consecutive_identical': 2,
        'history_count': 12,
        'max_age_days': 90,
        'lockout_attempts': 5,
        'lockout_duration_minutes': 30
    }
    
    # Audit and Logging
    AUDIT_ENABLED = True
    AUDIT_LOG_RETENTION_DAYS = 90
    SECURITY_LOG_LEVEL = 'INFO'
    LOG_FORMAT = 'json'
    LOG_LEVEL = 'INFO'
    
    # CSRF Protection
    CSRF_ENABLED = True
    CSRF_TOKEN_LIFETIME = 3600  # 1 hour
    CSRF_EXEMPT_ENDPOINTS = []  # No exemptions in production
    
    # Input Validation
    INPUT_VALIDATION_ENABLED = True
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_JSON_PAYLOAD_SIZE = 1024 * 1024  # 1MB
    MAX_FORM_FIELDS = 100
    
    # IP Whitelisting
    ADMIN_IP_WHITELIST = os.getenv('ADMIN_IP_WHITELIST', '').split(',') if os.getenv('ADMIN_IP_WHITELIST') else []
    API_IP_WHITELIST = os.getenv('API_IP_WHITELIST', '').split(',') if os.getenv('API_IP_WHITELIST') else []
    
    # Trusted Proxies (for proper IP detection)
    TRUSTED_PROXIES = os.getenv('TRUSTED_PROXIES', '').split(',') if os.getenv('TRUSTED_PROXIES') else []
    
    # Email Security
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    MAIL_SUPPRESS_SEND = False
    
    # API Security
    API_RATE_LIMIT = "1000/hour"
    API_KEY_REQUIRED = True
    API_VERSION_DEPRECATION_WARNINGS = True
    
    # Monitoring and Alerting
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    PROMETHEUS_METRICS_ENABLED = True
    HEALTH_CHECK_ENABLED = True
    
    # Cache Security
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = "bdc_prod:"
    
    # Compliance
    GDPR_COMPLIANCE_ENABLED = True
    DATA_RETENTION_DAYS = 2555  # 7 years
    AUDIT_TRAIL_REQUIRED = True
    
    # Feature Flags for Security
    SECURITY_FEATURES = {
        'rate_limiting': True,
        'csrf_protection': True,
        'input_validation': True,
        'audit_logging': True,
        'field_encryption': True,
        'password_policy': True,
        'security_headers': True,
        'ip_whitelisting': False,  # Enable if needed
        'mfa_required': True,
        'session_security': True
    }
    
    # Database Query Logging (for security monitoring)
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 30
    
    # WebSocket Security
    WEBSOCKET_ORIGINS = CORS_ORIGINS
    WEBSOCKET_RATE_LIMIT = "100/minute"
    
    # Backup and Recovery
    BACKUP_ENCRYPTION_ENABLED = True
    BACKUP_RETENTION_DAYS = 90
    
    @classmethod
    def init_app(cls, app):
        """Initialize production security configuration."""
        # Validate environment variables
        cls.validate_required_env_vars()
        
        # Setup logging
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            # Setup different log files for different purposes
            log_handlers = {
                'application': 'logs/bdc_application.log',
                'security': 'logs/bdc_security.log',
                'audit': 'logs/bdc_audit.log',
                'compliance': 'logs/bdc_compliance.log'
            }
            
            for log_type, log_file in log_handlers.items():
                handler = RotatingFileHandler(
                    log_file,
                    maxBytes=50*1024*1024,  # 50MB
                    backupCount=20
                )
                
                if log_type == 'security':
                    handler.setLevel(logging.WARNING)
                elif log_type == 'audit':
                    handler.setLevel(logging.INFO)
                else:
                    handler.setLevel(logging.INFO)
                
                formatter = logging.Formatter(
                    '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] %(message)s'
                )
                handler.setFormatter(formatter)
                
                logger = logging.getLogger(f'bdc.{log_type}')
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('BDC Production Security Configuration Loaded')
        
        # Initialize security middleware
        cls._init_security_middleware(app)
    
    @classmethod
    def _init_security_middleware(cls, app):
        """Initialize security middleware."""
        # Import and initialize security components
        from app.security import (
            SecurityHeaders, CSRFProtection, RateLimitingService,
            AuditLogger, InputValidator, EncryptionService
        )
        
        # Initialize security headers
        SecurityHeaders(app)
        
        # Initialize CSRF protection
        if cls.SECURITY_FEATURES['csrf_protection']:
            CSRFProtection(app)
        
        # Initialize rate limiting
        if cls.SECURITY_FEATURES['rate_limiting']:
            RateLimitingService(app)
        
        # Initialize audit logging
        if cls.SECURITY_FEATURES['audit_logging']:
            AuditLogger(app)
        
        # Add before request hooks
        @app.before_request
        def security_checks():
            from flask import request, abort, g
            
            # Check for required HTTPS
            if cls.FORCE_HTTPS and not request.is_secure:
                if not request.headers.get('X-Forwarded-Proto') == 'https':
                    abort(400, description="HTTPS required")
            
            # IP whitelist check for admin endpoints
            if request.endpoint and 'admin' in request.endpoint:
                if cls.ADMIN_IP_WHITELIST:
                    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                    if client_ip not in cls.ADMIN_IP_WHITELIST:
                        app.logger.warning(f"Unauthorized admin access attempt from {client_ip}")
                        abort(403, description="Access denied")
            
            # Set security context
            g.security_context = {
                'client_ip': request.headers.get('X-Forwarded-For', request.remote_addr),
                'user_agent': request.headers.get('User-Agent', ''),
                'request_id': secrets.token_hex(8)
            }
        
        app.logger.info("Security middleware initialized successfully")
    
    # Environment-specific overrides
    @classmethod
    def get_config_for_env(cls, env: str) -> Dict[str, Any]:
        """Get configuration overrides for specific environments."""
        configs = {
            'staging': {
                'DEBUG': False,
                'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),  # Longer for testing
                'RATELIMIT_DEFAULT': "200/minute",  # More lenient for testing
                'CORS_ORIGINS': ['https://staging.bdc.com'],
            },
            'production': {
                'DEBUG': False,
                'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),
                'RATELIMIT_DEFAULT': "60/minute",
                'CORS_ORIGINS': ['https://app.bdc.com'],
            }
        }
        
        return configs.get(env, {})