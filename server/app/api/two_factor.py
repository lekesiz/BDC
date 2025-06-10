"""Two-Factor Authentication API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.two_factor_service import TwoFactorService
from app.middleware.i18n_middleware import i18n_response
import logging

logger = logging.getLogger(__name__)

two_factor_bp = Blueprint('two_factor', __name__, url_prefix='/api/two-factor')


@two_factor_bp.route('/setup', methods=['POST'])
@jwt_required()
@i18n_response
def setup_2fa():
    """Initialize 2FA setup for current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        success, result = TwoFactorService.setup_2fa(user)
        
        if not success:
            return jsonify({
                'error': 'setup_failed',
                'message': result.get('error', 'Failed to setup 2FA')
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"2FA setup error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@two_factor_bp.route('/verify-setup', methods=['POST'])
@jwt_required()
@i18n_response
def verify_setup():
    """Verify 2FA setup with initial token."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Verification code is required'
            }), 400
        
        success, message = TwoFactorService.verify_2fa_setup(user, token)
        
        if not success:
            return jsonify({
                'error': 'verification_failed',
                'message': message
            }), 400
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"2FA verify setup error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@two_factor_bp.route('/verify-login', methods=['POST'])
@i18n_response
def verify_login():
    """Verify 2FA code during login process."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        token = data.get('token')
        session_token = data.get('session_token')
        
        if not token:
            return jsonify({
                'error': 'invalid_request',
                'message': '2FA code is required'
            }), 400
        
        # If session token provided, verify session
        if session_token:
            success, user = TwoFactorService.verify_2fa_session(session_token, token)
            if success and user:
                # Generate new JWT tokens
                from app.services.auth_service import AuthService
                auth_service = AuthService()
                tokens = auth_service._generate_tokens(user)
                
                return jsonify({
                    'success': True,
                    'access_token': tokens['access_token'],
                    'refresh_token': tokens['refresh_token'],
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role
                    }
                }), 200
        
        # Otherwise verify with user_id
        if not user_id:
            return jsonify({
                'error': 'invalid_request',
                'message': 'User ID or session token is required'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        success, error = TwoFactorService.verify_2fa_login(user, token)
        
        if not success:
            return jsonify({
                'error': 'verification_failed',
                'message': error or 'Invalid 2FA code'
            }), 400
        
        # Generate JWT tokens
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        tokens = auth_service._generate_tokens(user)
        
        return jsonify({
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        logger.error(f"2FA verify login error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@two_factor_bp.route('/disable', methods=['POST'])
@jwt_required()
@i18n_response
def disable_2fa():
    """Disable 2FA for current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Password is required to disable 2FA'
            }), 400
        
        success, message = TwoFactorService.disable_2fa(user, password)
        
        if not success:
            return jsonify({
                'error': 'disable_failed',
                'message': message
            }), 400
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"2FA disable error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@two_factor_bp.route('/regenerate-backup-codes', methods=['POST'])
@jwt_required()
@i18n_response
def regenerate_backup_codes():
    """Regenerate backup codes for current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        success, backup_codes = TwoFactorService.regenerate_backup_codes(user)
        
        if not success:
            return jsonify({
                'error': 'regenerate_failed',
                'message': '2FA is not enabled or failed to regenerate codes'
            }), 400
        
        return jsonify({
            'success': True,
            'backup_codes': backup_codes
        }), 200
        
    except Exception as e:
        logger.error(f"2FA regenerate backup codes error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@two_factor_bp.route('/status', methods=['GET'])
@jwt_required()
@i18n_response
def get_2fa_status():
    """Get 2FA status for current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': '$t:api.auth.user_not_found'
            }), 404
        
        status = TwoFactorService.get_2fa_status(user)
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        logger.error(f"2FA status error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500


@two_factor_bp.route('/create-session', methods=['POST'])
@i18n_response
def create_2fa_session():
    """Create a 2FA session for step-up authentication."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Email and password are required'
            }), 400
        
        # Verify credentials
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Check if 2FA is enabled
        status = TwoFactorService.get_2fa_status(user)
        if not status.get('enabled'):
            return jsonify({
                'error': '2fa_not_enabled',
                'message': '2FA is not enabled for this account'
            }), 400
        
        # Create 2FA session
        session_token = TwoFactorService.create_2fa_session(user)
        
        if not session_token:
            return jsonify({
                'error': 'session_failed',
                'message': 'Failed to create 2FA session'
            }), 500
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'requires_2fa': True
        }), 200
        
    except Exception as e:
        logger.error(f"2FA create session error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': '$t:api.error.server'
        }), 500