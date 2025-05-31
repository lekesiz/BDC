"""Production configuration for BDC application."""

import os
from datetime import timedelta
from typing import Dict, Any


class ProductionConfig:
    """Production configuration class with optimized settings."""
    
    # Application Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required for production")
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '20')),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10,
        'echo': False
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', '2592000'))
    )
    JWT_ALGORITHM = 'HS256'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Security Configuration
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', SECRET_KEY)
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUPPRESS_SEND = False
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/uploads/bdc')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    ALLOWED_EXTENSIONS = set(
        os.environ.get('ALLOWED_EXTENSIONS', 'pdf,png,jpg,jpeg,gif,doc,docx,txt,csv,xlsx').split(',')
    )
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('API_RATE_LIMIT_STORAGE', REDIS_URL)
    RATELIMIT_DEFAULT = os.environ.get('API_RATE_LIMIT', '1000 per hour')
    RATELIMIT_HEADERS_ENABLED = True
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/bdc/app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    
    # Cache Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    CACHE_KEY_PREFIX = 'bdc:'
    
    # Celery Configuration
    CELERY = {
        'broker_url': os.environ.get('CELERY_BROKER_URL', REDIS_URL),
        'result_backend': os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL),
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'worker_concurrency': int(os.environ.get('CELERY_WORKER_CONCURRENCY', '4')),
        'task_routes': {
            'app.tasks.send_email': {'queue': 'emails'},
            'app.tasks.generate_report': {'queue': 'reports'},
            'app.tasks.backup_database': {'queue': 'maintenance'},
        },
        'beat_schedule': {
            'cleanup-expired-tokens': {
                'task': 'app.tasks.cleanup_expired_tokens',
                'schedule': timedelta(hours=1),
            },
            'database-backup': {
                'task': 'app.tasks.backup_database',
                'schedule': timedelta(hours=6),
            },
            'generate-analytics': {
                'task': 'app.tasks.generate_analytics',
                'schedule': timedelta(hours=24),
            },
        }
    }
    
    # Security Headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss:; "
            "frame-ancestors 'none'"
        )
    }
    
    # Monitoring & Analytics
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    PROMETHEUS_METRICS_ENABLED = os.environ.get('PROMETHEUS_METRICS_ENABLED', 'True').lower() == 'true'
    HEALTH_CHECK_ENABLED = os.environ.get('HEALTH_CHECK_ENABLED', 'True').lower() == 'true'
    
    # External Service Configuration
    GOOGLE_CALENDAR_CLIENT_ID = os.environ.get('GOOGLE_CALENDAR_CLIENT_ID')
    GOOGLE_CALENDAR_CLIENT_SECRET = os.environ.get('GOOGLE_CALENDAR_CLIENT_SECRET')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    
    # Backup Configuration
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_S3_BUCKET = os.environ.get('BACKUP_S3_BUCKET')
    BACKUP_S3_REGION = os.environ.get('BACKUP_S3_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # Feature Flags
    FEATURES = {
        'analytics': os.environ.get('ENABLE_ANALYTICS', 'True').lower() == 'true',
        'notifications': os.environ.get('ENABLE_NOTIFICATIONS', 'True').lower() == 'true',
        'email_verification': os.environ.get('ENABLE_EMAIL_VERIFICATION', 'True').lower() == 'true',
        'two_factor_auth': os.environ.get('ENABLE_TWO_FACTOR_AUTH', 'False').lower() == 'true',
        'api_docs': os.environ.get('ENABLE_API_DOCS', 'False').lower() == 'true',
    }
    
    # Performance Settings
    GUNICORN_CONFIG = {
        'workers': int(os.environ.get('GUNICORN_WORKERS', '4')),
        'threads': int(os.environ.get('GUNICORN_THREADS', '2')),
        'max_requests': int(os.environ.get('GUNICORN_MAX_REQUESTS', '1000')),
        'max_requests_jitter': int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', '100')),
        'timeout': 30,
        'keepalive': 2,
        'worker_class': 'eventlet',
        'worker_connections': 1000,
    }
    
    @staticmethod
    def init_app(app):
        """Initialize application with production-specific configurations."""
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        # Ensure log directory exists
        log_dir = os.path.dirname(ProductionConfig.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        file_handler = RotatingFileHandler(
            ProductionConfig.LOG_FILE,
            maxBytes=ProductionConfig.LOG_MAX_BYTES,
            backupCount=ProductionConfig.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(ProductionConfig.LOG_FORMAT))
        file_handler.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        # Configure Sentry if enabled
        if ProductionConfig.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=ProductionConfig.SENTRY_DSN,
                integrations=[
                    FlaskIntegration(transaction_style='endpoint'),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,
                release=os.environ.get('APP_VERSION', 'unknown'),
                environment='production'
            )
        
        # Ensure upload directory exists
        if not os.path.exists(ProductionConfig.UPLOAD_FOLDER):
            os.makedirs(ProductionConfig.UPLOAD_FOLDER, exist_ok=True)
        
        # Set proper permissions for upload directory
        os.chmod(ProductionConfig.UPLOAD_FOLDER, 0o755)


# Export the configuration
Config = ProductionConfig