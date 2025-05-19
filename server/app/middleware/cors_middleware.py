"""CORS middleware for debugging and handling CORS issues."""

from flask import request
from app.extensions import logger


def init_cors_middleware(app):
    """Initialize CORS debugging middleware."""
    
    @app.before_request
    def handle_preflight():
        """Handle preflight CORS requests."""
        if request.method == 'OPTIONS':
            logger.info(f"Handling OPTIONS preflight request: {request.url}")
            logger.info(f"Origin: {request.headers.get('Origin')}")
            logger.info(f"Access-Control-Request-Method: {request.headers.get('Access-Control-Request-Method')}")
            logger.info(f"Access-Control-Request-Headers: {request.headers.get('Access-Control-Request-Headers')}")
            return '', 200
    
    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses."""
        origin = request.headers.get('Origin')
        
        # Log the response for debugging
        logger.info(f"Response status: {response.status_code} for {request.method} {request.url}")
        
        # Set CORS headers if origin is present
        if origin:
            if origin in app.config['CORS_ORIGINS']:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '3600'
            else:
                logger.warning(f"Origin {origin} not in allowed origins: {app.config['CORS_ORIGINS']}")
        
        return response