"""Sentry integration for error tracking and monitoring."""

import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from flask import request


def init_sentry(app):
    """Initialize Sentry for the Flask application."""
    dsn = os.getenv('SENTRY_DSN')
    
    if not dsn:
        app.logger.info('Sentry DSN not configured, skipping initialization')
        return
    
    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=None,  # Capture all levels
        event_level=None  # Don't create events from logs by default
    )
    
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FlaskIntegration(
                transaction_style='endpoint'
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            logging_integration,
        ],
        
        # Performance monitoring
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', 0.1)),
        
        # Environment
        environment=app.config.get('ENV', 'production'),
        
        # Release tracking
        release=os.getenv('APP_VERSION', '1.0.0'),
        
        # Configure error filtering
        before_send=before_send_filter,
        
        # Attach request data
        attach_stacktrace=True,
        send_default_pii=False,  # Don't send personally identifiable information
        
        # Performance
        profiles_sample_rate=float(os.getenv('SENTRY_PROFILES_SAMPLE_RATE', 0.1)),
    )
    
    app.logger.info('Sentry initialized successfully')


def before_send_filter(event, hint):
    """Filter events before sending to Sentry."""
    # Don't send events in development unless explicitly enabled
    if os.getenv('FLASK_ENV') == 'development' and not os.getenv('SENTRY_ENABLED'):
        return None
    
    # Filter out health check requests
    if 'request' in event and event['request'].get('url', '').endswith('/health'):
        return None
    
    # Filter out 404 errors for common bot paths
    if 'exception' in event:
        for value in event['exception']['values']:
            if value.get('type') == 'NotFound':
                url = event.get('request', {}).get('url', '')
                bot_paths = ['.php', '.asp', 'wp-admin', 'wp-login', '.env']
                if any(path in url for path in bot_paths):
                    return None
    
    # Add custom context
    if request:
        event['extra']['request_id'] = request.headers.get('X-Request-ID')
        event['extra']['user_agent'] = request.headers.get('User-Agent')
    
    return event


def set_user_context(user):
    """Set user context for Sentry."""
    if not user:
        sentry_sdk.set_user(None)
        return
    
    sentry_sdk.set_user({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'role': user.role,
    })
    
    # Add additional context
    sentry_sdk.set_context('user_details', {
        'tenant_id': user.tenant_id,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    })


def capture_message(message, level='info', **kwargs):
    """Capture a message in Sentry."""
    sentry_sdk.capture_message(message, level=level, **kwargs)


def capture_exception(error, **kwargs):
    """Capture an exception in Sentry."""
    sentry_sdk.capture_exception(error, **kwargs)


def add_breadcrumb(message, category='action', level='info', data=None):
    """Add a breadcrumb for better error context."""
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def start_transaction(name, op='http.server'):
    """Start a performance transaction."""
    return sentry_sdk.start_transaction(name=name, op=op)


def configure_scope_middleware(app):
    """Configure Sentry scope for each request."""
    @app.before_request
    def configure_sentry_scope():
        """Configure Sentry scope with request information."""
        with sentry_sdk.configure_scope() as scope:
            # Add request information
            scope.set_tag('endpoint', request.endpoint)
            scope.set_tag('method', request.method)
            
            # Add custom headers
            scope.set_extra('request_id', request.headers.get('X-Request-ID'))
            scope.set_extra('api_version', request.headers.get('X-API-Version', 'v1'))
            
            # Add user context if authenticated
            if hasattr(request, 'current_user') and request.current_user:
                set_user_context(request.current_user)