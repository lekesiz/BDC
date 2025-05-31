"""Endpoint mapping configuration for gradual migration to refactored services."""

from flask import Flask
from app.api.auth import auth_bp
from app.api.auth_refactored import auth_refactored_bp


def configure_auth_endpoints(app: Flask, use_refactored: bool = False):
    """
    Configure authentication endpoints based on refactoring stage.
    
    Args:
        app: Flask application instance
        use_refactored: Whether to use refactored endpoints
    """
    if use_refactored:
        # Use refactored endpoints
        app.register_blueprint(auth_refactored_bp, url_prefix='/api/v2/auth')
        print("Using refactored authentication endpoints at /api/v2/auth")
    else:
        # Use original endpoints
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("Using original authentication endpoints at /api/auth")
    
    # During migration, both can be active
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(auth_refactored_bp, url_prefix='/api/v2/auth')


# Feature flags for gradual migration
FEATURE_FLAGS = {
    'use_refactored_auth': False,
    'use_refactored_user': False,
    'use_refactored_notifications': False,
}


def get_feature_flag(flag_name: str) -> bool:
    """Get feature flag value."""
    return FEATURE_FLAGS.get(flag_name, False)


def set_feature_flag(flag_name: str, value: bool):
    """Set feature flag value."""
    FEATURE_FLAGS[flag_name] = value