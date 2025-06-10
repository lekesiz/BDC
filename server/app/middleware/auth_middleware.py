"""Authentication and authorization middleware."""
from functools import wraps
from flask import g, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User
from app.extensions import db


def require_auth(f):
    """Require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            
            # Get user ID from JWT
            user_id = get_jwt_identity()
            
            # Load user from database
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({
                    'error': 'unauthorized',
                    'message': 'User not found or inactive'
                }), 401
            
            # Set user in request context
            g.current_user = user
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'unauthorized',
                'message': str(e)
            }), 401
    
    return decorated_function


def require_role(allowed_roles):
    """Require specific roles for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                
                # Get user ID from JWT
                user_id = get_jwt_identity()
                
                # Load user from database
                user = User.query.get(user_id)
                if not user or not user.is_active:
                    return jsonify({
                        'error': 'unauthorized',
                        'message': 'User not found or inactive'
                    }), 401
                
                # Check if user has required role
                if user.role not in allowed_roles:
                    return jsonify({
                        'error': 'forbidden',
                        'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                    }), 403
                
                # Set user in request context
                g.current_user = user
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'unauthorized',
                    'message': str(e)
                }), 401
        
        return decorated_function
    return decorator


def require_tenant(f):
    """Require user to belong to a tenant."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            
            # Get user ID from JWT
            user_id = get_jwt_identity()
            
            # Load user from database
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({
                    'error': 'unauthorized',
                    'message': 'User not found or inactive'
                }), 401
            
            # Check if user has tenant
            if not user.tenant_id and user.role != 'super_admin':
                return jsonify({
                    'error': 'forbidden',
                    'message': 'User must belong to a tenant'
                }), 403
            
            # Set user and tenant in request context
            g.current_user = user
            g.tenant_id = user.tenant_id
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'unauthorized',
                'message': str(e)
            }), 401
    
    return decorated_function


def optional_auth(f):
    """Optional authentication - sets user if authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            
            # Get user ID from JWT if present
            user_id = get_jwt_identity()
            
            if user_id:
                # Load user from database
                user = User.query.get(user_id)
                if user and user.is_active:
                    g.current_user = user
                else:
                    g.current_user = None
            else:
                g.current_user = None
            
        except:
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function


def check_permission(permission):
    """Check if user has specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                
                # Get user ID from JWT
                user_id = get_jwt_identity()
                
                # Load user from database
                user = User.query.get(user_id)
                if not user or not user.is_active:
                    return jsonify({
                        'error': 'unauthorized',
                        'message': 'User not found or inactive'
                    }), 401
                
                # Super admin has all permissions
                if user.role == 'super_admin':
                    g.current_user = user
                    return f(*args, **kwargs)
                
                # Check specific permission based on role
                role_permissions = {
                    'tenant_admin': [
                        'manage_users', 'manage_beneficiaries', 'manage_programs',
                        'view_reports', 'manage_evaluations', 'manage_documents'
                    ],
                    'trainer': [
                        'view_beneficiaries', 'manage_evaluations', 'view_programs',
                        'view_reports', 'manage_appointments', 'manage_documents'
                    ],
                    'trainee': [
                        'view_own_data', 'take_evaluations', 'view_own_reports',
                        'book_appointments', 'view_documents'
                    ]
                }
                
                user_permissions = role_permissions.get(user.role, [])
                
                if permission not in user_permissions:
                    return jsonify({
                        'error': 'forbidden',
                        'message': f'Permission denied. Required: {permission}'
                    }), 403
                
                # Set user in request context
                g.current_user = user
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'error': 'unauthorized',
                    'message': str(e)
                }), 401
        
        return decorated_function
    return decorator