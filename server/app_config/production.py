"""Production-specific configuration with security hardening."""

import os
from datetime import timedelta
import sys
sys.path.append('..')
from config import Config

class ProductionConfig(Config):
    """Production configuration with enhanced security and performance."""
    
    # Environment
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Security - All keys must be set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    if not SECRET_KEY or not JWT_SECRET_KEY:
        raise ValueError("SECRET_KEY and JWT_SECRET_KEY must be set in production")
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DATABASE_POOL_SIZE', 20)),
        'pool_timeout': int(os.environ.get('DATABASE_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.environ.get('DATABASE_POOL_RECYCLE', 3600)),
        'max_overflow': int(os.environ.get('DATABASE_MAX_OVERFLOW', 0)),
        'pool_pre_ping': True,
        'echo': False
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # Cache Configuration
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = os.environ.get('CACHE_KEY_PREFIX', 'bdc_prod')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', REDIS_URL)
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '60 per minute')
    RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'sliding-window-counter')
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Shorter for production
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)     # Shorter for production
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ALGORITHM = 'HS256'
    JWT_ERROR_MESSAGE_KEY = 'message'
    
    # Security Headers and CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    TRUSTED_HOSTS = os.environ.get('TRUSTED_HOSTS', '').split(',')
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Security Headers
    CONTENT_SECURITY_POLICY = os.environ.get('CONTENT_SECURITY_POLICY')
    X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'DENY')
    X_CONTENT_TYPE_OPTIONS = os.environ.get('X_CONTENT_TYPE_OPTIONS', 'nosniff')
    REFERRER_POLICY = os.environ.get('REFERRER_POLICY', 'strict-origin-when-cross-origin')
    
    # SSL/HTTPS
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'true').lower() == 'true'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH')
    SSL_CA_BUNDLE_PATH = os.environ.get('SSL_CA_BUNDLE_PATH')
    
    # File Upload Security
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB in production
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    PROMETHEUS_ENABLED = os.environ.get('PROMETHEUS_ENABLED', 'true').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Feature Flags
    ENABLE_AI_FEATURES = os.environ.get('ENABLE_AI_FEATURES', 'true').lower() == 'true'
    ENABLE_GOOGLE_CALENDAR = os.environ.get('ENABLE_GOOGLE_CALENDAR', 'true').lower() == 'true'
    ENABLE_FILE_UPLOADS = os.environ.get('ENABLE_FILE_UPLOADS', 'true').lower() == 'true'
    ENABLE_REALTIME_NOTIFICATIONS = os.environ.get('ENABLE_REALTIME_NOTIFICATIONS', 'true').lower() == 'true'
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')
    
    # Backup Configuration
    BACKUP_S3_BUCKET = os.environ.get('BACKUP_S3_BUCKET')
    BACKUP_ENCRYPTION_KEY = os.environ.get('BACKUP_ENCRYPTION_KEY')
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', '0 2 * * *')
    
    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT = int(os.environ.get('HEALTH_CHECK_TIMEOUT', 30))
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 60))
    
    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=365)  # Static file caching
    
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific app configuration."""
        # Import here to avoid circular imports
        import logging
        from logging.handlers import RotatingFileHandler
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        # Sentry error tracking
        if cls.SENTRY_DSN:
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                integrations=[
                    FlaskIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,
                environment='production'
            )
        
        # Production logging
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
                
            file_handler = RotatingFileHandler(
                'logs/bdc_production.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('BDC Production Startup')