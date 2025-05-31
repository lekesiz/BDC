"""Authentication API routes using dependency injection."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.core.container import get_auth_service
from app.schemas.user import UserSchema
from app.schemas.auth import LoginSchema
from app.utils.decorators import validate_request


auth_bp_v2 = Blueprint('auth_v2', __name__, url_prefix='/api/v2/auth')
user_schema = UserSchema()
login_schema = LoginSchema()


@auth_bp_v2.route('/login', methods=['POST'])
@validate_request(login_schema)
def login():
    """Login endpoint."""
    data = request.get_json()
    auth_service = get_auth_service()
    
    result = auth_service.authenticate(
        email=data['email'],
        password=data['password'],
        remember=data.get('remember', False)
    )
    
    if not result:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'user': user_schema.dump(result['user']),
        'access_token': result['access_token'],
        'refresh_token': result['refresh_token'],
        'expires_in': result['expires_in']
    }), 200


@auth_bp_v2.route('/register', methods=['POST'])
@validate_request(user_schema)
def register():
    """Register endpoint."""
    data = request.get_json()
    auth_service = get_auth_service()
    
    try:
        user = auth_service.register(data)
        if not user:
            return jsonify({'error': 'User already exists'}), 400
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth_bp_v2.route('/refresh', methods=['POST'])
def refresh():
    """Refresh token endpoint."""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'Refresh token required'}), 400
    
    auth_service = get_auth_service()
    result = auth_service.refresh_token(refresh_token)
    
    if not result:
        return jsonify({'error': 'Invalid refresh token'}), 401
    
    return jsonify({
        'access_token': result['access_token'],
        'expires_in': result['expires_in']
    }), 200


@auth_bp_v2.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint."""
    user_id = get_jwt_identity()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    auth_service = get_auth_service()
    auth_service.logout(user_id, token)
    
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp_v2.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password endpoint."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    auth_service = get_auth_service()
    reset_token = auth_service.reset_password(email)
    
    if not reset_token:
        # Don't reveal if email exists
        return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
    
    # In real app, send email with reset token
    # For now, return token (only for development)
    return jsonify({
        'message': 'Password reset token generated',
        'reset_token': reset_token  # Remove in production
    }), 200


@auth_bp_v2.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    
    auth_service = get_auth_service()
    user = auth_service.confirm_reset_password(token, new_password)
    
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    return jsonify({'message': 'Password reset successfully'}), 200


@auth_bp_v2.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password endpoint."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    auth_service = get_auth_service()
    success = auth_service.change_password(user_id, current_password, new_password)
    
    if not success:
        return jsonify({'error': 'Invalid current password'}), 400
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp_v2.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    """Verify token endpoint."""
    user_id = get_jwt_identity()
    auth_service = get_auth_service()
    
    # Get token from header
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = auth_service.verify_token(token)
    
    if not user or user.id != user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify({
        'valid': True,
        'user': user_schema.dump(user)
    }), 200