"""Two-Factor Authentication API endpoints."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.two_factor_service import TwoFactorService
from app.extensions import limiter

from app.utils.logging import logger

two_fa_bp = Blueprint('two_factor_auth', __name__)


@two_fa_bp.route('/setup', methods=['POST'])
@jwt_required()
def setup_2fa():
    """Set up two-factor authentication for the current user."""
    try:
        user_id = get_jwt_identity()
        
        # Set up 2FA
        result, error = TwoFactorService.setup_2fa(user_id)
        
        if error:
            return jsonify({
                'error': 'setup_failed',
                'message': error
            }), 400
        
        return jsonify({
            'message': '2FA setup initiated',
            'qr_code': result['qr_code'],
            'secret': result['secret'],
            'backup_codes': result['backup_codes']
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"2FA setup error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to set up 2FA'
        }), 500


@two_fa_bp.route('/verify-setup', methods=['POST'])
@jwt_required()
def verify_2fa_setup():
    """Verify 2FA setup with initial token."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        token = data.get('token')
        if not token:
            return jsonify({
                'error': 'validation_error',
                'message': 'Token is required'
            }), 400
        
        # Verify setup
        success, message = TwoFactorService.verify_setup(user_id, token)
        
        if not success:
            return jsonify({
                'error': 'verification_failed',
                'message': message
            }), 400
        
        return jsonify({
            'message': message,
            'enabled': True
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"2FA verification error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to verify 2FA setup'
        }), 500


@two_fa_bp.route('/verify', methods=['POST'])
@limiter.limit("10 per minute")
def verify_2fa():
    """Verify 2FA token during login (after initial auth)."""
    try:
        data = request.get_json()
        
        session_token = data.get('session_token')
        verification_token = data.get('token')
        
        if not session_token or not verification_token:
            return jsonify({
                'error': 'validation_error',
                'message': 'Session token and verification token are required'
            }), 400
        
        # Verify the session and token
        user_id, error = TwoFactorService.verify_2fa_session(
            session_token, 
            verification_token
        )
        
        if error:
            return jsonify({
                'error': 'verification_failed',
                'message': error
            }), 401
        
        # Create full access token after successful 2FA
        from app.models import User
        user = User.query.get(user_id)
        
        access_token = create_access_token(
            identity=user_id,
            additional_claims={
                'role': user.role,
                'email': user.email,
                '2fa_verified': True
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'message': '2FA verification successful'
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"2FA verify error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to verify 2FA token'
        }), 500


@two_fa_bp.route('/disable', methods=['POST'])
@jwt_required()
def disable_2fa():
    """Disable two-factor authentication."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Require password confirmation
        password = data.get('password')
        if not password:
            return jsonify({
                'error': 'validation_error',
                'message': 'Password confirmation required'
            }), 400
        
        # Verify password
        from app.models import User
        user = User.query.get(user_id)
        if not user or not user.verify_password(password):
            return jsonify({
                'error': 'auth_failed',
                'message': 'Invalid password'
            }), 401
        
        # Disable 2FA
        success, message = TwoFactorService.disable_2fa(user_id)
        
        if not success:
            return jsonify({
                'error': 'disable_failed',
                'message': message
            }), 400
        
        return jsonify({
            'message': message,
            'enabled': False
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"2FA disable error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to disable 2FA'
        }), 500


@two_fa_bp.route('/backup-codes', methods=['POST'])
@jwt_required()
def regenerate_backup_codes():
    """Regenerate backup codes."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Require password confirmation
        password = data.get('password')
        if not password:
            return jsonify({
                'error': 'validation_error',
                'message': 'Password confirmation required'
            }), 400
        
        # Verify password
        from app.models import User
        user = User.query.get(user_id)
        if not user or not user.verify_password(password):
            return jsonify({
                'error': 'auth_failed',
                'message': 'Invalid password'
            }), 401
        
        # Regenerate codes
        codes, error = TwoFactorService.regenerate_backup_codes(user_id)
        
        if error:
            return jsonify({
                'error': 'regeneration_failed',
                'message': error
            }), 400
        
        return jsonify({
            'message': 'Backup codes regenerated successfully',
            'backup_codes': codes
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Backup code regeneration error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to regenerate backup codes'
        }), 500


@two_fa_bp.route('/status', methods=['GET'])
@jwt_required()
def get_2fa_status():
    """Get 2FA status for the current user."""
    try:
        user_id = get_jwt_identity()
        status = TwoFactorService.get_2fa_status(user_id)
        
        return jsonify(status), 200
        
    except Exception as e:
        current_app.logger.exception(f"2FA status error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to get 2FA status'
        }), 500


@two_fa_bp.route('/qr-code', methods=['GET'])
@jwt_required()
def get_qr_code():
    """Get QR code for existing 2FA setup."""
    try:
        user_id = get_jwt_identity()
        
        from app.models import TwoFactorAuth
        two_fa = TwoFactorAuth.query.filter_by(user_id=user_id).first()
        
        if not two_fa:
            return jsonify({
                'error': 'not_found',
                'message': '2FA not set up'
            }), 404
        
        if two_fa.is_enabled:
            return jsonify({
                'error': 'already_enabled',
                'message': '2FA is already enabled. Disable first to get new QR code.'
            }), 400
        
        qr_code = two_fa.generate_qr_code()
        
        return jsonify({
            'qr_code': qr_code,
            'message': 'QR code generated'
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"QR code generation error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'Failed to generate QR code'
        }), 500