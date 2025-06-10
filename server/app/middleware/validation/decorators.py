"""
Validation decorators for easy integration with Flask routes.
"""

import functools
from typing import Dict, List, Optional, Callable, Type
from flask import request, jsonify, g
from marshmallow import Schema, ValidationError
from werkzeug.exceptions import BadRequest

from .validation_middleware import validation_middleware
from .validators import (
    EmailValidator, PasswordValidator, URLValidator,
    FileValidator, JSONValidator, SQLValidator
)
from .business_validators import (
    BeneficiaryValidator, AppointmentValidator,
    ProgramValidator, EvaluationValidator, UserValidator
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_request(schema: Type[Schema] = None,
                    location: str = 'json',
                    required: bool = True,
                    validate_sql: bool = True,
                    custom_validators: List[Callable] = None):
    """
    Decorator to validate request data.
    
    Args:
        schema: Marshmallow schema class
        location: Where to get data ('json', 'args', 'form', 'files')
        required: Whether data is required
        validate_sql: Whether to check for SQL injection
        custom_validators: List of custom validation functions
    
    Example:
        @app.route('/api/users', methods=['POST'])
        @validate_request(UserCreateSchema)
        def create_user():
            data = g.validated_data
            # Process validated data
    """
    return validation_middleware.validate(
        schema=schema,
        location=location,
        required=required,
        validate_sql=validate_sql,
        custom_validators=custom_validators
    )


def validate_json(schema: Type[Schema], validate_sql: bool = True):
    """
    Shorthand decorator for JSON validation.
    
    Example:
        @app.route('/api/login', methods=['POST'])
        @validate_json(LoginSchema)
        def login():
            data = g.validated_data
    """
    return validate_request(schema=schema, location='json', validate_sql=validate_sql)


def validate_query(schema: Type[Schema]):
    """
    Shorthand decorator for query parameter validation.
    
    Example:
        @app.route('/api/users')
        @validate_query(UserSearchSchema)
        def list_users():
            filters = g.validated_data
    """
    return validate_request(schema=schema, location='args', required=False)


def validate_form(schema: Type[Schema]):
    """
    Shorthand decorator for form data validation.
    
    Example:
        @app.route('/api/upload', methods=['POST'])
        @validate_form(FileUploadSchema)
        def upload_file():
            data = g.validated_data
    """
    return validate_request(schema=schema, location='form')


def validate_files(max_size: int = 10 * 1024 * 1024,
                  allowed_extensions: List[str] = None,
                  required: bool = True):
    """
    Decorator to validate file uploads.
    
    Args:
        max_size: Maximum file size in bytes
        allowed_extensions: List of allowed file extensions
        required: Whether file is required
    
    Example:
        @app.route('/api/documents', methods=['POST'])
        @validate_files(max_size=5*1024*1024, allowed_extensions=['pdf', 'doc'])
        def upload_document():
            file = request.files.get('file')
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'file' not in request.files and required:
                return jsonify({
                    'error': 'No file provided',
                    'status': 'error'
                }), 400
            
            if 'file' in request.files:
                file = request.files['file']
                validator = FileValidator(
                    allowed_extensions=allowed_extensions,
                    max_size=max_size
                )
                
                try:
                    file_info = validator.validate(file)
                    g.file_info = file_info
                except ValueError as e:
                    logger.warning(f"File validation failed: {str(e)}", extra={
                        'filename': file.filename,
                        'ip': request.remote_addr
                    })
                    return jsonify({
                        'error': str(e),
                        'status': 'error'
                    }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_email(field_name: str = 'email'):
    """
    Decorator to validate email fields.
    
    Example:
        @app.route('/api/check-email', methods=['POST'])
        @validate_email()
        def check_email():
            email = request.json.get('email')
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data or field_name not in data:
                return jsonify({
                    'error': f'{field_name} is required',
                    'status': 'error'
                }), 400
            
            validator = EmailValidator()
            try:
                validated_email = validator.validate(data[field_name])
                data[field_name] = validated_email
            except ValueError as e:
                return jsonify({
                    'error': str(e),
                    'field': field_name,
                    'status': 'error'
                }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_password(field_name: str = 'password',
                     min_length: int = 12,
                     require_special: bool = True):
    """
    Decorator to validate password fields.
    
    Example:
        @app.route('/api/change-password', methods=['POST'])
        @validate_password(field_name='new_password')
        def change_password():
            data = request.json
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data or field_name not in data:
                return jsonify({
                    'error': f'{field_name} is required',
                    'status': 'error'
                }), 400
            
            validator = PasswordValidator(
                min_length=min_length,
                require_special=require_special
            )
            
            try:
                validator.validate(data[field_name])
            except ValueError as e:
                return jsonify({
                    'error': str(e),
                    'field': field_name,
                    'status': 'error'
                }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_business_rule(rule_type: str, **rule_params):
    """
    Decorator to validate business rules.
    
    Args:
        rule_type: Type of business rule ('beneficiary', 'appointment', 'program', 'evaluation', 'user')
        **rule_params: Additional parameters for the validator
    
    Example:
        @app.route('/api/appointments', methods=['POST'])
        @validate_json(AppointmentCreateSchema)
        @validate_business_rule('appointment', action='booking')
        def create_appointment():
            data = g.validated_data
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            data = g.get('validated_data', request.get_json())
            
            try:
                if rule_type == 'beneficiary':
                    if rule_params.get('action') == 'registration':
                        BeneficiaryValidator.validate_registration(data)
                    elif rule_params.get('action') == 'enrollment':
                        BeneficiaryValidator.validate_program_enrollment(
                            data.get('beneficiary_id'),
                            data.get('program_id')
                        )
                
                elif rule_type == 'appointment':
                    if rule_params.get('action') == 'booking':
                        AppointmentValidator.validate_booking(data)
                    elif rule_params.get('action') == 'cancellation':
                        AppointmentValidator.validate_cancellation(
                            data.get('appointment_id'),
                            g.current_user.id
                        )
                
                elif rule_type == 'program':
                    if rule_params.get('action') == 'creation':
                        ProgramValidator.validate_program_creation(data)
                    elif rule_params.get('action') == 'attendance':
                        ProgramValidator.validate_session_attendance(
                            data.get('session_id'),
                            data.get('beneficiary_id')
                        )
                
                elif rule_type == 'evaluation':
                    if rule_params.get('action') == 'submission':
                        EvaluationValidator.validate_evaluation_submission(data)
                
                elif rule_type == 'user':
                    if rule_params.get('action') == 'role_change':
                        UserValidator.validate_role_change(
                            data.get('user_id'),
                            data.get('new_role'),
                            g.current_user.id
                        )
                    elif rule_params.get('action') == 'profile_update':
                        UserValidator.validate_profile_update(
                            g.current_user.id,
                            data
                        )
                
            except ValueError as e:
                logger.warning(f"Business rule validation failed: {str(e)}", extra={
                    'rule_type': rule_type,
                    'action': rule_params.get('action'),
                    'user_id': getattr(g, 'current_user', {}).get('id')
                })
                
                if isinstance(e.args[0], dict):
                    return jsonify({
                        'error': 'Validation failed',
                        'errors': e.args[0],
                        'status': 'error'
                    }), 400
                else:
                    return jsonify({
                        'error': str(e),
                        'status': 'error'
                    }), 400
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def sanitize_output(fields_to_sanitize: List[str] = None,
                   remove_fields: List[str] = None):
    """
    Decorator to sanitize response data.
    
    Args:
        fields_to_sanitize: List of fields to HTML escape
        remove_fields: List of fields to remove from response
    
    Example:
        @app.route('/api/users/<int:user_id>')
        @sanitize_output(remove_fields=['password_hash', 'reset_token'])
        def get_user(user_id):
            user = User.query.get(user_id)
            return jsonify(user.to_dict())
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            
            # Handle different response types
            if hasattr(response, 'json'):
                data = response.json
            elif isinstance(response, dict):
                data = response
            elif isinstance(response, tuple) and isinstance(response[0], dict):
                data = response[0]
            else:
                return response
            
            # Remove sensitive fields
            if remove_fields and isinstance(data, dict):
                for field in remove_fields:
                    data.pop(field, None)
                    
                    # Handle nested removal in lists
                    for key, value in data.items():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    item.pop(field, None)
            
            # Sanitize specified fields
            if fields_to_sanitize and isinstance(data, dict):
                from .sanitizers import InputSanitizer
                sanitizer = InputSanitizer()
                
                for field in fields_to_sanitize:
                    if field in data and isinstance(data[field], str):
                        data[field] = sanitizer.escape_html(data[field])
            
            # Return modified response
            if hasattr(response, 'json'):
                response.json = data
                return response
            elif isinstance(response, tuple):
                return (data, *response[1:])
            else:
                return data
        
        return wrapper
    return decorator


def rate_limit(max_requests: int = 100, window: int = 3600):
    """
    Shorthand for rate limiting decorator.
    
    Example:
        @app.route('/api/expensive-operation')
        @rate_limit(max_requests=10, window=3600)
        def expensive_operation():
            # Limited to 10 requests per hour
    """
    return validation_middleware.rate_limit(max_requests=max_requests, window=window)


def require_api_key():
    """
    Shorthand for API key validation.
    
    Example:
        @app.route('/api/external/webhook')
        @require_api_key()
        def webhook():
            # Requires valid API key
    """
    return validation_middleware.validate_api_key