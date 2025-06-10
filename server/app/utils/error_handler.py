"""Standardized error handling utilities."""

from functools import wraps
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, current_app, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
import traceback
from app.middleware.i18n_middleware import i18n_response


class AppError(Exception):
    """Base application error class."""
    
    def __init__(self, message: str, code: str = None, status_code: int = 400, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.code = code or 'APP_ERROR'
        self.status_code = status_code
        self.details = details or {}


class ValidationError(AppError):
    """Validation error class."""
    
    def __init__(self, message: str, fields: Dict = None):
        super().__init__(
            message=message,
            code='VALIDATION_ERROR',
            status_code=422,
            details={'fields': fields} if fields else {}
        )


class AuthenticationError(AppError):
    """Authentication error class."""
    
    def __init__(self, message: str = '$t:api.error.unauthorized'):
        super().__init__(
            message=message,
            code='AUTHENTICATION_ERROR',
            status_code=401
        )


class AuthorizationError(AppError):
    """Authorization error class."""
    
    def __init__(self, message: str = '$t:api.error.forbidden'):
        super().__init__(
            message=message,
            code='AUTHORIZATION_ERROR',
            status_code=403
        )


class NotFoundError(AppError):
    """Not found error class."""
    
    def __init__(self, message: str = '$t:api.error.not_found', resource: str = None):
        super().__init__(
            message=message,
            code='NOT_FOUND',
            status_code=404,
            details={'resource': resource} if resource else {}
        )


class ConflictError(AppError):
    """Conflict error class."""
    
    def __init__(self, message: str = '$t:api.error.conflict', field: str = None):
        super().__init__(
            message=message,
            code='CONFLICT',
            status_code=409,
            details={'field': field} if field else {}
        )


class RateLimitError(AppError):
    """Rate limit error class."""
    
    def __init__(self, message: str = '$t:api.error.rate_limit', retry_after: int = None):
        super().__init__(
            message=message,
            code='RATE_LIMIT_EXCEEDED',
            status_code=429,
            details={'retry_after': retry_after} if retry_after else {}
        )


class ExternalServiceError(AppError):
    """External service error class."""
    
    def __init__(self, message: str, service: str = None):
        super().__init__(
            message=message,
            code='EXTERNAL_SERVICE_ERROR',
            status_code=503,
            details={'service': service} if service else {}
        )


def format_error_response(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Format error into standardized response."""
    # Handle our custom errors
    if isinstance(error, AppError):
        response = {
            'error': {
                'code': error.code,
                'message': error.message,
                'details': error.details
            }
        }
        return response, error.status_code
    
    # Handle Marshmallow validation errors
    if isinstance(error, ValidationError):
        response = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': '$t:api.error.validation',
                'details': {
                    'fields': error.messages if hasattr(error, 'messages') else str(error)
                }
            }
        }
        return response, 422
    
    # Handle SQLAlchemy errors
    if isinstance(error, IntegrityError):
        response = {
            'error': {
                'code': 'DATABASE_INTEGRITY_ERROR',
                'message': '$t:api.error.database_integrity',
                'details': {
                    'constraint': str(error.orig) if hasattr(error, 'orig') else str(error)
                }
            }
        }
        return response, 409
    
    if isinstance(error, SQLAlchemyError):
        response = {
            'error': {
                'code': 'DATABASE_ERROR',
                'message': '$t:api.error.database',
                'details': {}
            }
        }
        return response, 500
    
    # Handle Werkzeug HTTP exceptions
    if isinstance(error, HTTPException):
        response = {
            'error': {
                'code': error.name.upper().replace(' ', '_'),
                'message': error.description,
                'details': {}
            }
        }
        return response, error.code
    
    # Handle generic exceptions
    response = {
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': '$t:api.error.server',
            'details': {}
        }
    }
    
    # Include stack trace in development
    if current_app.debug:
        response['error']['details']['trace'] = traceback.format_exc()
    
    return response, 500


def handle_errors(f):
    """Decorator to handle errors in view functions."""
    @wraps(f)
    @i18n_response
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Log the error
            log_error(e)
            
            # Format and return error response
            response, status_code = format_error_response(e)
            return jsonify(response), status_code
    
    return decorated_function


def log_error(error: Exception):
    """Log error with context."""
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'request_method': request.method,
        'request_path': request.path,
        'request_args': dict(request.args),
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    }
    
    # Add user info if available
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        if user_id:
            error_info['user_id'] = user_id
    except:
        pass
    
    # Log based on error type
    if isinstance(error, AppError) and error.status_code < 500:
        current_app.logger.warning(f"Application error: {error_info}")
    else:
        current_app.logger.error(f"Server error: {error_info}", exc_info=True)


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(Exception)
    @i18n_response
    def handle_exception(e):
        """Handle all exceptions."""
        log_error(e)
        response, status_code = format_error_response(e)
        return jsonify(response), status_code
    
    @app.errorhandler(404)
    @i18n_response
    def handle_not_found(e):
        """Handle 404 errors."""
        error = NotFoundError('$t:api.error.not_found')
        response, status_code = format_error_response(error)
        return jsonify(response), status_code
    
    @app.errorhandler(500)
    @i18n_response
    def handle_internal_error(e):
        """Handle 500 errors."""
        log_error(e)
        response = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '$t:api.error.server',
                'details': {}
            }
        }
        return jsonify(response), 500


# Utility functions for common error scenarios
def validate_request_data(data: Dict, required_fields: list) -> Dict:
    """Validate request data has required fields."""
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValidationError(
            message='$t:api.validation.missing_fields',
            fields={field: '$t:api.validation.field_required' for field in missing}
        )
    return data


def validate_pagination_params(page: int = 1, per_page: int = 10) -> Tuple[int, int]:
    """Validate pagination parameters."""
    if page < 1:
        raise ValidationError('$t:api.validation.page_invalid')
    if per_page < 1 or per_page > 100:
        raise ValidationError('$t:api.validation.per_page_invalid')
    return page, per_page


def handle_database_error(error: SQLAlchemyError):
    """Handle database errors with appropriate responses."""
    if isinstance(error, IntegrityError):
        # Parse constraint name from error
        constraint = str(error.orig)
        if 'unique constraint' in constraint.lower():
            raise ConflictError('$t:api.error.resource_exists')
        elif 'foreign key constraint' in constraint.lower():
            raise ValidationError('$t:api.error.invalid_reference')
        else:
            raise ConflictError('$t:api.error.constraint_violation')
    else:
        raise AppError('$t:api.error.database', code='DATABASE_ERROR', status_code=500)