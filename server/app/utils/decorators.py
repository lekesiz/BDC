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
            
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get user from database
            from app.models import User
            from flask import g
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Set user in g for access in route
            g.current_user = user
            
            # Super admin has all permissions
            if user.role == 'super_admin':
                return f(*args, **kwargs)
            
            # Check permission based on role
            if not _has_permission(user.role, permission):
                return jsonify({
                    'error': 'Permission denied',
                    'message': f'Required permission: {permission}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def _has_permission(role, permission):
    """Check if role has permission."""
    # Define role permissions
    permissions = {
        'tenant_admin': [
            'users.view', 'users.create', 'users.edit', 'users.delete',
            'beneficiaries.view', 'beneficiaries.create', 'beneficiaries.edit', 
            'beneficiaries.delete', 'beneficiaries.export',
            'programs.view', 'programs.create', 'programs.edit', 'programs.delete',
            'evaluations.view', 'evaluations.create', 'evaluations.edit', 'evaluations.delete',
            'appointments.view', 'appointments.create', 'appointments.edit', 'appointments.delete',
            'documents.view', 'documents.upload', 'documents.delete',
            'reports.view', 'reports.generate', 'reports.export',
            'settings.view', 'settings.edit'
        ],
        'trainer': [
            'beneficiaries.view', 'beneficiaries.create', 'beneficiaries.edit',
            'programs.view', 'programs.enroll',
            'evaluations.view', 'evaluations.create', 'evaluations.edit',
            'appointments.view', 'appointments.create', 'appointments.edit',
            'documents.view', 'documents.upload',
            'reports.view', 'reports.generate'
        ],
        'trainee': [
            'profile.view', 'profile.edit',
            'programs.view', 'programs.enroll',
            'evaluations.view', 'evaluations.take',
            'appointments.view', 'appointments.book',
            'documents.view',
            'reports.view_own'
        ]
    }
    
    role_permissions = permissions.get(role, [])
    return permission in role_permissions


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