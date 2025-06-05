"""Clean application factory with no import-time dependencies."""

import os
import logging
from typing import Optional, Dict, Any
from flask import Flask, request

from app.core.config_manager import config_manager, ConfigValidationResult
from app.core.extension_manager import extension_manager
from app.core.lazy_container import lazy_container


class ApplicationFactory:
    """Factory for creating Flask applications with clean initialization."""
    
    def __init__(self):
        """Initialize application factory."""
        self._logger = logging.getLogger(__name__)
    
    def create_application(self, config_object: Optional[object] = None) -> Flask:
        """Create a Flask application with clean initialization.
        
        Args:
            config_object: Optional configuration object to use
            
        Returns:
            Configured Flask application instance
            
        Raises:
            RuntimeError: If configuration validation fails
        """
        app = Flask(__name__)
        
        try:
            # 1. Load and validate configuration
            config_result = self._configure_application(app, config_object)
            if not config_result.is_valid:
                raise RuntimeError(f"Configuration validation failed: {config_result.errors}")
            
            # 2. Set up logging first (critical for debugging)
            self._configure_logging(app)
            
            # 3. Initialize extensions in proper order
            if not extension_manager.initialize_extensions(app):
                raise RuntimeError("Extension initialization failed")
            
            # 4. Initialize dependency injection container
            lazy_container.initialize(app)
            
            # 5. Register blueprints (lazy loaded)
            self._register_blueprints(app)
            
            # 6. Register error handlers
            self._register_error_handlers(app)
            
            # 7. Register middleware
            self._register_middleware(app)
            
            # 8. Register CLI commands
            self._register_cli_commands(app)
            
            # 9. Set up environment-specific features
            self._setup_environment_features(app)
            
            # 10. Register health endpoints
            self._register_health_endpoints(app)
            
            # 11. Initialize database (tables only, no data)
            self._initialize_database(app)
            
            app.logger.info("Application created successfully")
            return app
            
        except Exception as e:
            logging.error(f"Failed to create application: {e}")
            raise
    
    def _configure_application(self, app: Flask, config_object: Optional[object]) -> ConfigValidationResult:
        """Configure the application."""
        return config_manager.load_configuration(app, config_object)
    
    def _configure_logging(self, app: Flask) -> None:
        """Configure application logging."""
        try:
            from app.utils.logger import configure_logger
            configure_logger(app)
            app.logger.info("Logging configured successfully")
        except Exception as e:
            # Fallback to basic logging if custom logger fails
            logging.basicConfig(level=logging.INFO)
            app.logger.warning(f"Failed to configure custom logging, using basic: {e}")
    
    def _register_blueprints(self, app: Flask) -> None:
        """Register application blueprints (lazy loaded)."""
        try:
            # Import and register blueprints only when needed
            self._register_auth_blueprints(app)
            self._register_api_blueprints(app)
            self._register_v2_blueprints(app)
            
            app.logger.info("Blueprints registered successfully")
            
        except Exception as e:
            app.logger.error(f"Failed to register blueprints: {e}")
            raise
    
    def _register_auth_blueprints(self, app: Flask) -> None:
        """Register authentication blueprints."""
        from app.api.auth import auth_bp
        from app.api.simple_auth import simple_auth_bp
        from app.api.two_factor_auth import two_fa_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(simple_auth_bp, url_prefix='/api/auth')
        app.register_blueprint(two_fa_bp, url_prefix='/api/auth/2fa')
    
    def _register_api_blueprints(self, app: Flask) -> None:
        """Register main API blueprints."""
        # Import blueprints lazily to avoid import-time dependencies
        blueprints_to_register = [
            ('app.api.users', 'users_bp', '/api/users'),
            ('app.api.beneficiaries_v2', 'beneficiaries_bp', '/api/beneficiaries'),
            ('app.api.profile', 'profile_bp', '/api/profile'),
            ('app.api.documents', 'documents_bp', '/api'),
            ('app.api.appointments', 'appointments_bp', '/api'),
            ('app.api.notifications', 'notifications_bp', '/api'),
            ('app.api.availability', 'availability_bp', '/api'),
            ('app.api.reports', 'reports_bp', '/api'),
            ('app.api.tenants', 'tenants_bp', '/api'),
            ('app.api.folders', 'folders_bp', '/api'),
            ('app.api.calendar', 'calendar_bp', '/api'),
            ('app.api.messages', 'messages_bp', '/api'),
            ('app.api.analytics', 'analytics_bp', '/api'),
            ('app.api.user_settings', 'user_settings_bp', None),  # Routes already have /api prefix
            ('app.api.user_activities', 'user_activities_bp', None),  # Routes already have /api prefix
            ('app.api.tests', 'tests_bp', '/api'),
            ('app.api.programs_v2', 'programs_bp', '/api'),
            ('app.api.portal', 'portal_bp', '/api/portal'),
            ('app.api.settings', 'settings_bp', '/api'),
            ('app.api.settings_general', 'settings_general_bp', '/api'),
            ('app.api.settings_appearance', 'settings_appearance_bp', '/api'),
            ('app.api.calendars_availability', 'calendar_availability_bp', '/api'),
            ('app.api.assessment', 'assessment_bp', '/api'),
            ('app.api.assessment_templates', 'assessment_templates_bp', '/api'),
            ('app.api.health', 'health_bp', '/api'),
            ('app.api.settings_routes', 'settings_bp', None),  # Routes already have /api prefix
            ('app.api.recurring_appointments', 'bp', '/api/recurring-appointments'),
            ('app.api.ai_reports', 'bp', None),
            ('app.api.sms', 'sms_bp', None),  # SMS API endpoints
            ('app.api.adaptive_tests', 'adaptive_test_bp', None),  # Adaptive test endpoints
            ('app.api.question_randomization', 'randomization_bp', '/api/randomization'),  # Question randomization endpoints
        ]
        
        # Additional blueprints that might cause import issues
        problematic_blueprints = [
            ('app.api.evaluations', 'evaluations_bp', '/api/evaluations'),
            ('app.api.tests_simple', 'tests_simple_bp', '/api/evaluations'),  # Map to same endpoint
        ]
        
        # Register safe blueprints first
        for module_path, blueprint_name, url_prefix in blueprints_to_register:
            try:
                module = __import__(module_path, fromlist=[blueprint_name])
                blueprint = getattr(module, blueprint_name)
                if url_prefix:
                    app.register_blueprint(blueprint, url_prefix=url_prefix)
                else:
                    app.register_blueprint(blueprint)
                app.logger.debug(f"Registered blueprint: {blueprint_name}")
            except Exception as e:
                app.logger.warning(f"Failed to register blueprint {blueprint_name}: {e}")
        
        # Try to register problematic blueprints with error handling
        for module_path, blueprint_name, url_prefix in problematic_blueprints:
            try:
                module = __import__(module_path, fromlist=[blueprint_name])
                blueprint = getattr(module, blueprint_name)
                if url_prefix:
                    app.register_blueprint(blueprint, url_prefix=url_prefix)
                else:
                    app.register_blueprint(blueprint)
                app.logger.debug(f"Registered blueprint: {blueprint_name}")
            except Exception as e:
                app.logger.warning(f"Failed to register blueprint {blueprint_name}: {e}")
                # Continue without this blueprint
    
    def _register_v2_blueprints(self, app: Flask) -> None:
        """Register v2 API blueprints."""
        try:
            from app.api.v2.auth import auth_bp_v2
            from app.api.v2.beneficiaries import beneficiaries_bp_v2
            from app.api.v2.cached_endpoints import cached_bp
            
            app.register_blueprint(auth_bp_v2)
            app.register_blueprint(beneficiaries_bp_v2)
            app.register_blueprint(cached_bp)
            
        except ImportError as e:
            app.logger.warning(f"Could not import v2 API blueprints: {e}")
    
    def _register_error_handlers(self, app: Flask) -> None:
        """Register error handlers."""
        from flask import jsonify
        from werkzeug.exceptions import HTTPException
        
        @app.errorhandler(HTTPException)
        def handle_http_exception(error):
            """Handle HTTP exceptions."""
            response = jsonify({
                'error': error.name,
                'message': error.description,
                'status_code': error.code
            })
            response.status_code = error.code
            return response

        @app.errorhandler(Exception)
        def handle_generic_exception(error):
            """Handle generic exceptions."""
            app.logger.exception(error)
            response = jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            })
            response.status_code = 500
            return response
        
        app.logger.info("Error handlers registered successfully")
    
    def _register_middleware(self, app: Flask) -> None:
        """Register application middleware."""
        try:
            from app.middleware.request_context import request_context_middleware
            from app.middleware.cors_middleware import init_cors_middleware
            
            # Apply CORS middleware
            init_cors_middleware(app)
            
            # Apply request context middleware
            app.before_request(request_context_middleware)
            
            # Register optional middleware
            self._register_optional_middleware(app)
            
            # Register response middleware
            self._register_response_middleware(app)
            
            app.logger.info("Middleware registered successfully")
            
        except Exception as e:
            app.logger.error(f"Failed to register middleware: {e}")
            raise
    
    def _register_optional_middleware(self, app: Flask) -> None:
        """Register optional middleware based on configuration."""
        # Cache middleware
        try:
            from app.middleware.cache_middleware import init_cache_middleware
            init_cache_middleware(app)
        except ImportError:
            app.logger.warning("Cache middleware not available")
        
        # IP whitelist middleware
        if os.getenv('IP_WHITELIST_ENABLED', 'false').lower() == 'true':
            try:
                from app.middleware.ip_whitelist import IPWhitelistMiddleware
                app.wsgi_app = IPWhitelistMiddleware(app.wsgi_app)
                app.logger.info("IP whitelist middleware enabled")
            except Exception as e:
                app.logger.error(f"Failed to initialize IP whitelist middleware: {e}")
    
    def _register_response_middleware(self, app: Flask) -> None:
        """Register response middleware."""
        from flask import request, make_response
        
        # CORS preflight handling
        @app.before_request
        def handle_preflight():
            if request.method == 'OPTIONS':
                response = make_response()
                origin = request.headers.get('Origin')
                allowed_origins = app.config.get('CORS_ORIGINS', ['*'])
                
                if origin in allowed_origins or '*' in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    response.headers['Access-Control-Max-Age'] = '3600'
                return response
        
        # Security headers
        @app.after_request
        def add_security_headers(response):
            if os.getenv('SECURE_HEADERS', 'false').lower() == 'true':
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-Frame-Options'] = 'SAMEORIGIN'
                response.headers['X-XSS-Protection'] = '1; mode=block'
                
                # HSTS (only in production)
                if app.config.get('ENV') == 'production':
                    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            return response
        
        # CORS headers
        @app.after_request
        def after_request(response):
            origin = request.headers.get('Origin')
            allowed_origins = app.config.get('CORS_ORIGINS', ['*'])
            
            if origin and (origin in allowed_origins or '*' in allowed_origins):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
                response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '3600'
            
            return response
    
    def _register_cli_commands(self, app: Flask) -> None:
        """Register CLI commands."""
        try:
            from app.cli import register_cli_commands
            register_cli_commands(app)
            app.logger.info("CLI commands registered successfully")
        except Exception as e:
            app.logger.warning(f"Failed to register CLI commands: {e}")
    
    def _setup_environment_features(self, app: Flask) -> None:
        """Set up environment-specific features."""
        env = app.config.get('ENV', 'development')
        
        if env == 'production':
            self._setup_production_features(app)
        elif env == 'development':
            self._setup_development_features(app)
    
    def _setup_production_features(self, app: Flask) -> None:
        """Set up production-specific features."""
        # Security middleware
        try:
            from app.middleware.security_middleware import SecurityMiddleware
            SecurityMiddleware(app)
            app.logger.info("Production security middleware enabled")
        except ImportError:
            app.logger.warning("Security middleware not available")
        
        # Backup manager
        try:
            from app.utils.backup_manager import BackupManager, setup_backup_scheduler
            backup_manager = BackupManager(app)
            setup_backup_scheduler(app, backup_manager)
            app.logger.info("Backup manager initialized")
        except ImportError:
            app.logger.warning("Backup manager not available")
        
        # Prometheus metrics
        if os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true':
            try:
                from prometheus_flask_exporter import PrometheusMetrics
                PrometheusMetrics(app, path='/metrics')
                app.logger.info("Prometheus metrics enabled at /metrics")
            except ImportError:
                app.logger.warning("prometheus_flask_exporter not installed; metrics disabled")
    
    def _setup_development_features(self, app: Flask) -> None:
        """Set up development-specific features."""
        # Request logging
        @app.before_request
        def log_request_info():
            app.logger.debug(f'Request: {request.method} {request.path} - {request.remote_addr}')
        
        @app.after_request
        def log_response_info(response):
            app.logger.debug(f'Response: {response.status} - {response.content_length} bytes')
            return response
    
    def _register_health_endpoints(self, app: Flask) -> None:
        """Register health check endpoints."""
        from flask import jsonify
        
        @app.route('/health')
        def health_check():
            """Basic health check endpoint."""
            return jsonify({'status': 'healthy'}), 200
        
        @app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
        def test_cors():
            """Test CORS endpoint."""
            return jsonify({'message': 'CORS test successful'}), 200
        
        # Advanced health checks
        try:
            from app.utils.health_checker import create_health_endpoints
            create_health_endpoints(app)
            app.logger.info("Advanced health check endpoints created")
        except ImportError:
            app.logger.warning("Advanced health checker not available")
    
    def _initialize_database(self, app: Flask) -> None:
        """Initialize database tables (no data)."""
        try:
            with app.app_context():
                from app.extensions import db
                db.create_all()
                app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize database: {e}")
            raise


# Global application factory instance
app_factory = ApplicationFactory()


def create_app(config_object: Optional[object] = None) -> Flask:
    """Create Flask application using the factory.
    
    Args:
        config_object: Optional configuration object to use
        
    Returns:
        Configured Flask application instance
    """
    return app_factory.create_application(config_object)