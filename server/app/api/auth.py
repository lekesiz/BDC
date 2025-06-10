"""Improved authentication API with dependency injection."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from app.schemas import (
    LoginSchema, RegisterSchema, TokenSchema, RefreshTokenSchema,
    ResetPasswordRequestSchema, ResetPasswordSchema, ChangePasswordSchema
)
from app.core.container import get_auth_service
from app.services.interfaces.auth_service_interface import IAuthService

from app.utils.logging import logger
from app.middleware.i18n_middleware import i18n_response


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@i18n_response
def login():
    """User login endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = LoginSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Authenticate user
        result = auth_service.login(
            email=data['email'],
            password=data['password'],
            remember=data.get('remember', False)
        )
        
        if not result:
            return jsonify({
                'error': 'invalid_credentials',
                'message': '$t:api.auth.login_failed'
            }), 401
        
        # Check if 2FA is required
        from app.services.two_factor_service import TwoFactorService
        from app.models.user import User
        
        user = User.query.filter_by(email=data['email']).first()
        if user:
            two_fa_status = TwoFactorService.get_2fa_status(user)
            if two_fa_status.get('enabled'):
                # Create 2FA session instead of returning tokens
                session_token = TwoFactorService.create_2fa_session(user)
                return jsonify({
                    'requires_2fa': True,
                    'session_token': session_token,
                    'user_id': user.id
                }), 200
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Login error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/register', methods=['POST'])
@i18n_response
def register():
    """User registration endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = RegisterSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Register user
        user = auth_service.register(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'trainee'),
            tenant_id=data.get('tenant_id')
        )
        
        if not user:
            return jsonify({
                'error': 'registration_failed',
                'message': '$t:api.auth.registration_failed'
            }), 400
        
        # Send verification email
        from app.services.email_verification_service import EmailVerificationService
        EmailVerificationService.send_verification_email(user)
        
        # Return user data with tokens for auto-login
        return jsonify({
            'message': '$t:api.auth.register_success',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'tenant_id': user.tenant_id,
                'email_verified': user.email_verified
            },
            'access_token': getattr(user, '_access_token', None),
            'refresh_token': getattr(user, '_refresh_token', None)
        }), 201
    
    except Exception as e:
        current_app.logger.exception(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@i18n_response
def refresh():
    """Token refresh endpoint with improved architecture."""
    try:
        user_id = get_jwt_identity()
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Refresh token
        result = auth_service.refresh_token(user_id)
        
        if not result:
            return jsonify({
                'error': 'refresh_failed',
                'message': '$t:api.auth.refresh_failed'
            }), 401
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@i18n_response
def logout():
    """User logout endpoint with improved architecture."""
    try:
        jti = get_jwt()['jti']
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Logout user
        success = auth_service.logout(jti)
        
        if not success:
            return jsonify({
                'error': 'logout_failed',
                'message': '$t:api.auth.logout_failed'
            }), 500
        
        return jsonify({
            'message': '$t:api.auth.logout_success'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/reset-password-request', methods=['POST'])
@i18n_response
def reset_password_request():
    """Request password reset endpoint."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = ResetPasswordRequestSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Request password reset
        success = auth_service.request_password_reset(data['email'])
        
        # Always return success for security reasons
        return jsonify({
            'message': '$t:api.auth.password_reset_requested'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Reset password request error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/reset-password', methods=['POST'])
@i18n_response
def reset_password():
    """Reset password with token endpoint."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = ResetPasswordSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Reset password
        success = auth_service.reset_password(
            token=data['token'],
            new_password=data['new_password']
        )
        
        if not success:
            return jsonify({
                'error': 'reset_password_failed',
                'message': '$t:api.auth.reset_password_failed'
            }), 400
        
        return jsonify({
            'message': '$t:api.auth.password_reset_success'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Reset password error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@i18n_response
def change_password():
    """Change password for authenticated user."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': '$t:api.validation.request_empty'
            }), 400
        
        # Validate request data
        schema = ChangePasswordSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': '$t:api.error.validation',
                'errors': e.messages
            }), 400
        
        # Get current user
        user_id = get_jwt_identity()
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Change password
        success = auth_service.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if not success:
            return jsonify({
                'error': 'change_password_failed',
                'message': '$t:api.auth.change_password_failed'
            }), 400
        
        return jsonify({
            'message': '$t:api.auth.password_changed'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Change password error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/verify-email/<token>', methods=['GET'])
@i18n_response
def verify_email(token):
    """Verify email address using token."""
    try:
        from app.services.email_verification_service import EmailVerificationService
        
        # Verify the email token
        success, message = EmailVerificationService.verify_email(token)
        
        if not success:
            return jsonify({
                'error': 'verification_failed',
                'message': message
            }), 400
        
        return jsonify({
            'message': '$t:api.auth.email_verified',
            'success': True
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Email verification error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/resend-verification', methods=['POST'])
@jwt_required()
@i18n_response
def resend_verification():
    """Resend email verification link."""
    try:
        from app.models.user import User
        from app.services.email_verification_service import EmailVerificationService
        
        # Get current user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        # Resend verification email
        success, message = EmailVerificationService.resend_verification_email(user)
        
        if not success:
            return jsonify({
                'error': 'resend_failed',
                'message': message
            }), 400
        
        return jsonify({
            'message': '$t:api.auth.verification_email_sent',
            'success': True
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Resend verification error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@auth_bp.route('/verification-status', methods=['GET'])
@jwt_required()
@i18n_response
def verification_status():
    """Check email verification status."""
    try:
        from app.models.user import User
        
        # Get current user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        return jsonify({
            'email_verified': user.email_verified,
            'email_verified_at': user.email_verified_at.isoformat() if user.email_verified_at else None,
            'email': user.email
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Verification status error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500