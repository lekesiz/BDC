"""Simple authentication API for testing."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

from app.extensions import db
from app.models import User
from app.schemas import LoginSchema

simple_auth_bp = Blueprint('simple_auth', __name__)

@simple_auth_bp.route('/test-login', methods=['POST'])
def test_login():
    """Simple test login endpoint."""
    try:
        # Get JSON data
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body is empty'
            }), 400
        
        # Simple validation
        email = json_data.get('email')
        password = json_data.get('password')
        
        if not email or not password:
            return jsonify({
                'error': 'validation_error',
                'message': 'Email and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Verify password
        if not user.verify_password(password):
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({
                'error': 'account_disabled',
                'message': 'Account is disabled'
            }), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'tenant_id': user.tenant_id,
                'is_active': user.is_active
            }
        }), 200
    
    except Exception as e:
        current_app.logger.exception(f"Login error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500


@simple_auth_bp.route('/debug', methods=['GET'])
def debug_auth():
    """Debug endpoint to check auth setup."""
    try:
        admin = User.query.filter_by(email='admin@bdc.com').first()
        
        return jsonify({
            'status': 'ok',
            'admin_exists': admin is not None,
            'admin_active': admin.is_active if admin else None,
            'admin_role': admin.role if admin else None,
            'password_test': admin.verify_password('Admin123!') if admin else None,
            'total_users': User.query.count()
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500