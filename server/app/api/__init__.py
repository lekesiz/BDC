"""API package."""

from app.api.auth import auth_bp
from app.api.users import users_bp
from app.api.portal import portal_bp

# Export all blueprints
__all__ = [
    'auth_bp',
    'users_bp',
    'portal_bp'
]