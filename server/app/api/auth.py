"""Improved authentication API with dependency injection."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from app.schemas import (
    LoginSchema, RegisterSchema, TokenSchema, RefreshTokenSchema,
    ResetPasswordRequestSchema, ResetPasswordSchema, ChangePasswordSchema
)
from app.core.improved_container import get_auth_service
from app.services.interfaces.auth_service_interface import IAuthService


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate request data
        schema = LoginSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Validation failed',
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
                'message': 'Invalid email or password'
            }), 401
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Login error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate request data
        schema = RegisterSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Validation failed',
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
            role=data.get('role', 'student'),
            tenant_id=data.get('tenant_id')
        )
        
        if not user:
            return jsonify({
                'error': 'registration_failed',
                'message': 'User registration failed. Email may already exist.'
            }), 400
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
    
    except Exception as e:
        current_app.logger.exception(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
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
                'message': 'Failed to refresh token'
            }), 401
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.exception(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
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
                'message': 'Failed to logout'
            }), 500
        
        return jsonify({
            'message': 'Successfully logged out'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate request data
        schema = ChangePasswordSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Validation failed',
                'errors': e.messages
            }), 400
        
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
                'message': 'Failed to change password. Current password may be incorrect.'
            }), 400
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Change password error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint with improved architecture."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Validate request data
        schema = ResetPasswordSchema()
        try:
            data = schema.load(json_data)
        except ValidationError as e:
            return jsonify({
                'error': 'validation_error',
                'message': 'Validation failed',
                'errors': e.messages
            }), 400
        
        # Get auth service through dependency injection
        auth_service: IAuthService = get_auth_service()
        
        # Reset password
        success = auth_service.reset_password(
            email=data['email'],
            new_password=data['new_password']
        )
        
        if not success:
            return jsonify({
                'error': 'reset_password_failed',
                'message': 'Failed to reset password. User may not exist.'
            }), 400
        
        return jsonify({
            'message': 'Password reset successfully'
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Reset password error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500