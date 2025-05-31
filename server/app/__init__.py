"""Main application module with clean initialization."""

from typing import Optional
from flask import Flask

# Import the new application factory
from app.core.app_factory import create_app as factory_create_app

# Import extensions for backward compatibility
from app.extensions import db


def create_app(config_object: Optional[object] = None) -> Flask:
    """Create Flask application using the new clean architecture.
    
    This is the main entry point for creating Flask applications.
    All initialization is handled by the ApplicationFactory with
    no import-time dependencies or side effects.
    
    Args:
        config_object: Optional configuration object to use
        
    Returns:
        Configured Flask application instance
    """
    return factory_create_app(config_object)

