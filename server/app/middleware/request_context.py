"""Request context middleware."""

import uuid
from functools import wraps
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, current_user

from app.extensions import logger


def request_context_middleware():
    """Initialize request context."""
    # Generate a unique ID for the request
    request_id = str(uuid.uuid4())
    g.request_id = request_id
    
    # Add request ID to log records
    logger.request_id = request_id
    
    # Try to get the current user for logging
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            g.user_id = user_id
            logger.user_id = user_id
    except:
        # If token is invalid, we just don't set user info
        pass


def auth_required(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        if current_user.role != 'admin':
            return {'error': 'admin_required', 'message': 'Admin role required'}, 403
        return f(*args, **kwargs)
    return decorated


def role_required(roles):
    """Decorator to require specific role(s)."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            if current_user.role not in roles:
                return {'error': 'unauthorized', 'message': 'Insufficient permissions'}, 403
            return f(*args, **kwargs)
        return decorated
    return decorator