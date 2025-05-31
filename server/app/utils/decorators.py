"""Utility decorators for the application."""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from marshmallow import ValidationError


def validate_request(schema):
    """Decorator to validate request data using a Marshmallow schema."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            json_data = request.get_json()
            if not json_data:
                return jsonify({'error': 'No input data provided'}), 400
            
            try:
                # Validate and deserialize input
                schema.load(json_data)
            except ValidationError as err:
                return jsonify({'errors': err.messages}), 422
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requires_permission(permission):
    """Decorator to check if user has required permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # For now, just check if user is authenticated
            # In production, check actual permissions
            if not user_id:
                return jsonify({'error': 'Permission denied'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Get user from database and check role
        from app.models import User
        user = User.query.get(user_id)
        
        if not user or user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function