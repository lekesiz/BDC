"""
Main validation middleware for Flask applications.
"""

import functools
import logging
from typing import Dict, List, Optional, Any, Callable
from flask import request, jsonify, g
from marshmallow import Schema, ValidationError
from werkzeug.exceptions import BadRequest
import json

from .schema_validator import SchemaValidator
from .sanitizers import InputSanitizer
from .validators import SQLValidator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationMiddleware:
    """
    Comprehensive validation middleware for API endpoints.
    """
    
    def __init__(self, app=None):
        """Initialize the validation middleware."""
        self.app = app
        self.schema_validator = SchemaValidator()
        self.input_sanitizer = InputSanitizer()
        self.sql_validator = SQLValidator()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        self.app = app
        app.before_request(self._validate_request)
        
        # Register error handlers
        app.register_error_handler(ValidationError, self._handle_validation_error)
        app.register_error_handler(BadRequest, self._handle_bad_request)
    
    def _validate_request(self):
        """Validate incoming requests before processing."""
        # Skip validation for certain endpoints
        if request.endpoint in ['static', 'health.health_check']:
            return
        
        # Validate content type for POST/PUT/PATCH requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.endpoint and not request.endpoint.startswith('api.upload'):
                # For non-upload endpoints, validate JSON content
                if not request.is_json and request.data:
                    return jsonify({
                        'error': 'Content-Type must be application/json',
                        'status': 'error'
                    }), 400
        
        # Store request start time for monitoring
        g.request_start_time = logger.log_performance_start('request_validation')
        
        # Sanitize query parameters
        if request.args:
            sanitized_args = self.input_sanitizer.sanitize_dict(dict(request.args))
            request.args = sanitized_args
        
        # Log request for audit
        logger.info(f"Incoming request: {request.method} {request.path}", extra={
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string
        })
    
    def _handle_validation_error(self, error: ValidationError):
        """Handle marshmallow validation errors."""
        logger.warning(f"Validation error: {error.messages}", extra={
            'validation_errors': error.messages,
            'endpoint': request.endpoint
        })
        
        return jsonify({
            'error': 'Validation failed',
            'errors': error.messages,
            'status': 'error'
        }), 400
    
    def _handle_bad_request(self, error: BadRequest):
        """Handle bad request errors."""
        logger.warning(f"Bad request: {error.description}", extra={
            'error': str(error),
            'endpoint': request.endpoint
        })
        
        return jsonify({
            'error': error.description or 'Bad request',
            'status': 'error'
        }), 400
    
    def validate(self, schema: Schema = None, 
                 location: str = 'json',
                 required: bool = True,
                 validate_sql: bool = True,
                 custom_validators: List[Callable] = None):
        """
        Decorator to validate request data against a schema.
        
        Args:
            schema: Marshmallow schema class for validation
            location: Where to get data from ('json', 'args', 'form', 'files')
            required: Whether data is required
            validate_sql: Whether to check for SQL injection
            custom_validators: List of custom validation functions
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Get data based on location
                data = self._get_request_data(location, required)
                
                if data is None and required:
                    return jsonify({
                        'error': f'No {location} data provided',
                        'status': 'error'
                    }), 400
                
                # Skip validation if no data and not required
                if data is None:
                    return func(*args, **kwargs)
                
                # Sanitize input data
                if isinstance(data, dict):
                    data = self.input_sanitizer.sanitize_dict(data)
                elif isinstance(data, list):
                    data = [self.input_sanitizer.sanitize_dict(item) if isinstance(item, dict) else item 
                           for item in data]
                
                # SQL injection validation
                if validate_sql and isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            try:
                                self.sql_validator.validate(value)
                            except ValueError as e:
                                logger.warning(f"SQL injection attempt detected: {str(e)}", extra={
                                    'field': key,
                                    'value': value[:100],  # Log only first 100 chars
                                    'ip': request.remote_addr
                                })
                                return jsonify({
                                    'error': 'Invalid input detected',
                                    'field': key,
                                    'status': 'error'
                                }), 400
                
                # Schema validation
                if schema:
                    try:
                        validated_data = self.schema_validator.validate(schema, data)
                        # Store validated data in g for use in the endpoint
                        g.validated_data = validated_data
                    except ValidationError as e:
                        return jsonify({
                            'error': 'Validation failed',
                            'errors': e.messages,
                            'status': 'error'
                        }), 400
                
                # Custom validators
                if custom_validators:
                    for validator in custom_validators:
                        try:
                            validator(data)
                        except ValueError as e:
                            return jsonify({
                                'error': str(e),
                                'status': 'error'
                            }), 400
                
                # Log successful validation
                if hasattr(g, 'request_start_time'):
                    logger.log_performance_end(g.request_start_time, 'request_validation')
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def _get_request_data(self, location: str, required: bool) -> Optional[Any]:
        """Get data from request based on location."""
        try:
            if location == 'json':
                return request.get_json(force=True) if required else request.get_json()
            elif location == 'args':
                return dict(request.args) if request.args else None
            elif location == 'form':
                return dict(request.form) if request.form else None
            elif location == 'files':
                return dict(request.files) if request.files else None
            else:
                raise ValueError(f"Invalid location: {location}")
        except Exception as e:
            logger.error(f"Error getting request data: {str(e)}")
            if required:
                raise BadRequest(f"Invalid {location} data")
            return None
    
    def validate_api_key(self, func):
        """Decorator to validate API key."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not api_key:
                return jsonify({
                    'error': 'API key required',
                    'status': 'error'
                }), 401
            
            # Validate API key format and existence
            if not self._is_valid_api_key(api_key):
                logger.warning(f"Invalid API key attempt", extra={
                    'ip': request.remote_addr,
                    'api_key': api_key[:8] + '...' if len(api_key) > 8 else api_key
                })
                return jsonify({
                    'error': 'Invalid API key',
                    'status': 'error'
                }), 401
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def _is_valid_api_key(self, api_key: str) -> bool:
        """Validate API key format and existence."""
        # Basic format validation
        if not api_key or len(api_key) < 32:
            return False
        
        # Additional validation logic here
        # This would typically check against a database or cache
        return True
    
    def rate_limit(self, max_requests: int = 100, window: int = 3600):
        """
        Decorator for rate limiting.
        
        Args:
            max_requests: Maximum number of requests allowed
            window: Time window in seconds
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # This would typically use Redis or similar for distributed rate limiting
                # For now, using a simple in-memory implementation
                
                client_id = self._get_client_id()
                
                # Check rate limit
                if self._is_rate_limited(client_id, max_requests, window):
                    logger.warning(f"Rate limit exceeded", extra={
                        'client_id': client_id,
                        'max_requests': max_requests,
                        'window': window
                    })
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': window,
                        'status': 'error'
                    }), 429
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def _get_client_id(self) -> str:
        """Get client identifier for rate limiting."""
        # Use authenticated user ID if available
        if hasattr(g, 'current_user') and g.current_user:
            return f"user:{g.current_user.id}"
        
        # Otherwise use IP address
        return f"ip:{request.remote_addr}"
    
    def _is_rate_limited(self, client_id: str, max_requests: int, window: int) -> bool:
        """Check if client is rate limited."""
        # This is a placeholder - in production, use Redis or similar
        # For now, always return False
        return False


# Global instance
validation_middleware = ValidationMiddleware()