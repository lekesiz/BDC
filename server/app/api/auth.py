"""Authentication API."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt, create_access_token, 
    create_refresh_token
)
from marshmallow import ValidationError

from app.extensions import db, logger
from app.schemas import (
    LoginSchema, RegisterSchema, TokenSchema, RefreshTokenSchema,
    ResetPasswordRequestSchema, ResetPasswordSchema, ChangePasswordSchema
)
from app.services import AuthService
from app.models import User


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/debug', methods=['GET'])
def debug_auth():
    """Debug endpoint to check auth."""
    from app.models import User
    admin = User.query.filter_by(email='admin@bdc.com').first()
    
    return jsonify({
        'admin_exists': admin is not None,
        'admin_active': admin.is_active if admin else None,
        'admin_role': admin.role if admin else None,
        'password_test': admin.verify_password('Admin123!') if admin else None,
        'total_users': User.query.count()
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
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
        
        # Authenticate user
        tokens = AuthService.login(
            email=data['email'],
            password=data['password'],
            remember=data.get('remember', False)
        )
        
        if not tokens:
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Get user data to include in response
        from app.models import User
        user = User.query.filter_by(email=data['email']).first()
        
        # Return tokens with user data
        response_data = {
            **tokens,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.exception(f"Login error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Register user
        user = AuthService.register(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'student')
        )
        
        if not user:
            return jsonify({
                'error': 'registration_failed',
                'message': 'Registration failed'
            }), 400
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Return tokens
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': 3600  # 1 hour in seconds
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        logger.exception(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Token refresh endpoint."""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        
        # Create new access token
        access_token = create_access_token(identity=user_id)
        
        # Return new access token
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': 3600  # 1 hour in seconds
        }), 200
    
    except Exception as e:
        logger.exception(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint."""
    try:
        # Get JWT token
        token = get_jwt()
        
        # Revoke token
        success = AuthService.logout(token)
        
        if not success:
            return jsonify({
                'error': 'logout_failed',
                'message': 'Logout failed'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Successfully logged out'
        }), 200
    
    except Exception as e:
        logger.exception(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/reset-password/request', methods=['POST'])
def request_password_reset():
    """Password reset request endpoint."""
    try:
        # Validate request data
        schema = ResetPasswordRequestSchema()
        data = schema.load(request.json)
        
        # Request password reset
        success = AuthService.request_password_reset(data['email'])
        
        # Always return success to prevent email enumeration
        return jsonify({
            'message': 'If your email is registered, you will receive a password reset link'
        }), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        logger.exception(f"Password reset request error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Password reset endpoint."""
    try:
        # Validate request data
        schema = ResetPasswordSchema()
        data = schema.load(request.json)
        
        # Reset password
        success = AuthService.reset_password(
            token=data['token'],
            password=data['password']
        )
        
        if not success:
            return jsonify({
                'error': 'reset_failed',
                'message': 'Password reset failed'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Password reset successful'
        }), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        logger.exception(f"Password reset error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Password change endpoint."""
    try:
        # Get user identity
        user_id = get_jwt_identity()
        
        # Validate request data
        schema = ChangePasswordSchema()
        data = schema.load(request.json)
        
        # Change password
        success = AuthService.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        if not success:
            return jsonify({
                'error': 'change_failed',
                'message': 'Password change failed'
            }), 400
        
        # Return success response
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': e.messages
        }), 400
    
    except Exception as e:
        logger.exception(f"Password change error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500