"""Email verification middleware."""

from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.email_verification_service import EmailVerificationService
import logging

logger = logging.getLogger(__name__)


def email_verification_required(f):
    """Decorator to require email verification for accessing certain endpoints."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            # Get current user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'error': 'user_not_found',
                    'message': 'User not found'
                }), 404
            
            # Check if verification is required
            if EmailVerificationService.check_verification_required(user):
                return jsonify({
                    'error': 'email_not_verified',
                    'message': 'Please verify your email address to access this feature',
                    'email_verified': False,
                    'email': user.email
                }), 403
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Email verification check error: {str(e)}")
            return jsonify({
                'error': 'server_error',
                'message': 'An error occurred during verification check'
            }), 500
    
    return decorated_function


def soft_email_verification_check(f):
    """Decorator that adds email verification status to response but doesn't block access."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            # Get current user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            # Execute the original function
            response = f(*args, **kwargs)
            
            # If user exists and response is JSON, add verification status
            if user and isinstance(response, tuple) and len(response) >= 1:
                data, status_code = response[0], response[1] if len(response) > 1 else 200
                
                if isinstance(data, dict):
                    data['email_verification_status'] = {
                        'verified': user.email_verified,
                        'email': user.email,
                        'required': EmailVerificationService.check_verification_required(user)
                    }
                    return data, status_code
            
            return response
            
        except Exception as e:
            logger.error(f"Soft email verification check error: {str(e)}")
            # Don't break the original functionality
            return f(*args, **kwargs)
    
    return decorated_function


class EmailVerificationMiddleware:
    """Middleware for email verification checks."""
    
    def __init__(self, app=None):
        self.app = app
        self.excluded_paths = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/auth/verify-email',
            '/api/auth/resend-verification',
            '/api/auth/verification-status',
            '/api/auth/logout',
            '/api/auth/reset-password-request',
            '/api/auth/reset-password',
            '/health'
        ]
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        self.app = app
        
        # Add configuration
        app.config.setdefault('REQUIRE_EMAIL_VERIFICATION', True)
        app.config.setdefault('EMAIL_VERIFICATION_EXEMPT_ROLES', ['super_admin'])
        
        logger.info("Email verification middleware initialized")
    
    def should_check_verification(self, request):
        """Check if the current request should be checked for email verification."""
        # Skip if verification is disabled
        if not current_app.config.get('REQUIRE_EMAIL_VERIFICATION', True):
            return False
        
        # Skip for excluded paths
        if request.path in self.excluded_paths:
            return False
        
        # Skip for static files and non-API routes
        if not request.path.startswith('/api/'):
            return False
        
        return True