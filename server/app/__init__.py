"""Main application module."""

import os
import logging
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager

from app.extensions import (
    db, migrate, jwt, ma, cors, cache, mail, limiter, logger, socketio
)
from app.utils import configure_logger
from app.realtime import configure_socketio


def create_app(config_object=None):
    """Application factory pattern."""
    app = Flask(__name__)

    # Load configuration
    if config_object is None:
        config_name = os.getenv('FLASK_ENV', 'default')
        from config import config
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app, 
                  resources={
                      r"/*": {
                          "origins": app.config['CORS_ORIGINS'],
                          "methods": ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
                          "allow_headers": ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
                          "supports_credentials": True,
                          "expose_headers": ['Content-Type', 'Authorization'],
                          "send_wildcard": False,
                          "allow_credentials": True,
                          "max_age": 3600
                      }
                  },
                  supports_credentials=True,
                  intercept_exceptions=False)
    cache.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    # Initialize Socket.IO with proper CORS settings
    socketio.init_app(app, 
                     cors_allowed_origins='*',
                     cors_credentials=True,
                     async_mode='eventlet',
                     allow_upgrades=True,
                     ping_timeout=60,
                     ping_interval=25,
                     logger=True,
                     engineio_logger=True)

    # Set up logging
    configure_logger(app)

    # Register blueprints
    register_blueprints(app)

    # Import WebSocket handlers
    from app import socketio_basic
    
    # Register error handlers
    register_error_handlers(app)

    # Register middleware
    register_middleware(app)

    # Register JWT callbacks
    register_jwt_callbacks(app)
    
    # Import socketio events
    from app import socketio_events

    # Configure SocketIO
    configure_socketio(app)

    # Prometheus metrics
    if os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true':
        try:
            from prometheus_flask_exporter import PrometheusMetrics
            PrometheusMetrics(app, path='/metrics')
            app.logger.info('Prometheus metrics enabled at /metrics')
        except ImportError:
            app.logger.warning('prometheus_flask_exporter not installed; metrics disabled')

    # Create uploads directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Initialize database and create all test users if needed
    with app.app_context():
        db.create_all()
        
        # Ensure admin user exists
        from app.models.user import User
        from app.models.tenant import Tenant
        
        # Create default tenant if needed
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(
                name='Default',
                slug='default', 
                email='admin@default.com',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            app.logger.info("Created default tenant")
        
        # Define all test users
        test_users = [
            {
                'email': 'admin@bdc.com',
                'username': 'admin',
                'password': 'Admin123!',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'super_admin'
            },
            {
                'email': 'tenant@bdc.com',
                'username': 'tenant',
                'password': 'Tenant123!',
                'first_name': 'Tenant',
                'last_name': 'Admin',
                'role': 'tenant_admin'
            },
            {
                'email': 'trainer@bdc.com',
                'username': 'trainer',
                'password': 'Trainer123!',
                'first_name': 'Trainer',
                'last_name': 'User',
                'role': 'trainer'
            },
            {
                'email': 'student@bdc.com',
                'username': 'student',
                'password': 'Student123!',
                'first_name': 'Student',
                'last_name': 'User',
                'role': 'student'
            }
        ]
        
        # Create or update all test users
        for user_data in test_users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=True
                )
                db.session.add(user)
                app.logger.info(f"Created user: {user_data['email']}")
            
            # Always reset password for testing
            user.password = user_data['password']
            
            # Add tenant relationship if it exists
            if hasattr(user, 'tenants') and tenant not in user.tenants:
                user.tenants.append(tenant)
            
            db.session.commit()
        
        app.logger.info(f"Total users in database: {User.query.count()}")

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
    def test_cors():
        """Test CORS endpoint."""
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        return jsonify({'message': 'CORS test successful'}), 200

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.beneficiaries_v2 import beneficiaries_bp as beneficiaries_v2_bp
    from app.api.evaluations import evaluations_bp
    from app.api.profile import profile_bp
    from app.api.documents import documents_bp
    from app.api.appointments import appointments_bp
    from app.api.notifications import notifications_bp
    from app.api.availability import availability_bp
    from app.api.reports import reports_bp
    from app.api.notifications_unread import notifications_unread_bp
    from app.api.tenants import tenants_bp
    from app.api.folders import folders_bp
    from app.api.calendar import calendar_bp
    from app.api.messages import messages_bp
    from app.api.analytics import analytics_bp
    from app.api.user_settings import user_settings_bp
    from app.api.user_activities import user_activities_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # User profile blueprint
    from app.api.users_profile import users_profile_bp
    app.register_blueprint(users_profile_bp, url_prefix='/api')
    app.register_blueprint(beneficiaries_v2_bp, url_prefix='/api/beneficiaries')
    app.register_blueprint(evaluations_bp, url_prefix='/api/evaluations')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(documents_bp, url_prefix='/api')
    app.register_blueprint(appointments_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp, url_prefix='/api')
    app.register_blueprint(availability_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    app.register_blueprint(notifications_unread_bp, url_prefix='/api/notifications')
    app.register_blueprint(tenants_bp, url_prefix='/api')
    app.register_blueprint(folders_bp, url_prefix='/api')
    app.register_blueprint(calendar_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(user_settings_bp)  # Routes already have /api prefix
    app.register_blueprint(user_activities_bp)  # Routes already have /api prefix

    # Test blueprints
    from app.api.tests import tests_bp
    app.register_blueprint(tests_bp, url_prefix='/api')
    
    # Programs blueprint
    from app.api.programs import programs_bp
    from app.api.programs_v2 import programs_bp as programs_v2_bp
    app.register_blueprint(programs_v2_bp, url_prefix='/api')
    
    # Portal blueprint
    from app.api.portal import portal_bp
    app.register_blueprint(portal_bp, url_prefix='/api/portal')
    
    # Settings blueprints
    from app.api.settings import settings_bp
    from app.api.settings_general import settings_general_bp
    from app.api.settings_appearance import settings_appearance_bp
    from app.api.calendars_availability import calendar_availability_bp
    
    app.register_blueprint(settings_bp, url_prefix='/api')
    app.register_blueprint(settings_general_bp, url_prefix='/api')
    app.register_blueprint(settings_appearance_bp, url_prefix='/api')
    app.register_blueprint(calendar_availability_bp, url_prefix='/api')
    
    # Assessment blueprints
    from app.api.assessment import assessment_bp
    from app.api.assessment_templates import assessment_templates_bp
    
    app.register_blueprint(assessment_bp, url_prefix='/api')
    app.register_blueprint(assessment_templates_bp, url_prefix='/api')
    
    # Add a simple test route
    @app.route('/api/test', methods=['GET', 'OPTIONS'])
    def test_endpoint():
        return jsonify({"message": "Test endpoint working", "cors": "enabled"})


def register_error_handlers(app):
    """Register error handlers."""
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


def register_middleware(app):
    """Register middleware."""
    from app.middleware.request_context import request_context_middleware
    from app.middleware.cors_middleware import init_cors_middleware
    from flask import request, make_response

    # Apply CORS middleware
    init_cors_middleware(app)
    
    # Apply middleware
    app.before_request(request_context_middleware)
    
    # Handle OPTIONS requests for CORS preflight
    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            response = make_response()
            origin = request.headers.get('Origin')
            if origin in app.config['CORS_ORIGINS']:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '3600'
            return response
    
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin and origin in app.config['CORS_ORIGINS']:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
            response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
        return response

    # Future middleware will be added here
    # app.before_request(auth_middleware)
    # ...


def register_jwt_callbacks(app):
    """Register JWT callbacks."""
    from app.models.user import TokenBlocklist, User
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT token."""
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token is revoked."""
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token."""
        return jsonify({
            'error': 'token_expired',
            'message': 'The token has expired',
            'status_code': 401
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token."""
        return jsonify({
            'error': 'invalid_token',
            'message': 'Signature verification failed',
            'status_code': 401
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token."""
        return jsonify({
            'error': 'authorization_required',
            'message': 'Authorization is required',
            'status_code': 401
        }), 401