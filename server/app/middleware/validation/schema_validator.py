"""
Schema-based validation using Marshmallow.
"""

from typing import Dict, Any, Type, List, Optional
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE
from marshmallow.fields import Field
import re


class SchemaValidator:
    """
    Centralized schema validation with enhanced security features.
    """
    
    def __init__(self):
        """Initialize the schema validator."""
        self.custom_validators = {}
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register default custom validators."""
        self.register_validator('safe_string', self._validate_safe_string)
        self.register_validator('safe_html', self._validate_safe_html)
        self.register_validator('phone', self._validate_phone)
        self.register_validator('username', self._validate_username)
        self.register_validator('alphanumeric', self._validate_alphanumeric)
        self.register_validator('no_special_chars', self._validate_no_special_chars)
    
    def register_validator(self, name: str, validator_func):
        """Register a custom validator."""
        self.custom_validators[name] = validator_func
    
    def validate(self, schema_class: Type[Schema], data: Dict[str, Any], 
                 partial: bool = False, strict: bool = True) -> Dict[str, Any]:
        """
        Validate data against a schema.
        
        Args:
            schema_class: Marshmallow schema class
            data: Data to validate
            partial: Allow partial validation
            strict: Use strict mode (exclude unknown fields)
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Create schema instance with appropriate settings
        schema = schema_class(unknown=EXCLUDE if strict else None)
        
        # Load and validate data
        try:
            validated_data = schema.load(data, partial=partial)
            return validated_data
        except ValidationError as e:
            # Enhance error messages for better user feedback
            enhanced_errors = self._enhance_error_messages(e.messages)
            raise ValidationError(enhanced_errors)
    
    def _enhance_error_messages(self, errors: Dict) -> Dict:
        """Enhance validation error messages for better clarity."""
        enhanced = {}
        
        for field, messages in errors.items():
            if isinstance(messages, list):
                enhanced[field] = [self._enhance_single_message(msg) for msg in messages]
            elif isinstance(messages, dict):
                enhanced[field] = self._enhance_error_messages(messages)
            else:
                enhanced[field] = self._enhance_single_message(messages)
        
        return enhanced
    
    def _enhance_single_message(self, message: str) -> str:
        """Enhance a single error message."""
        # Map technical messages to user-friendly ones
        message_map = {
            'Missing data for required field.': 'This field is required.',
            'Not a valid email address.': 'Please enter a valid email address.',
            'Not a valid URL.': 'Please enter a valid URL.',
            'Not a valid number.': 'Please enter a valid number.',
            'Shorter than minimum length': 'This field is too short.',
            'Longer than maximum length': 'This field is too long.',
        }
        
        for pattern, replacement in message_map.items():
            if pattern in message:
                return message.replace(pattern, replacement)
        
        return message
    
    # Custom validators
    def _validate_safe_string(self, value: str) -> str:
        """Validate string is safe (no XSS attempts)."""
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'onerror\s*=',
            r'onclick\s*=',
            r'<iframe.*?>',
            r'<object.*?>',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError("Input contains potentially dangerous content")
        
        return value
    
    def _validate_safe_html(self, value: str) -> str:
        """Validate HTML content is safe."""
        # This is a basic check - use bleach for actual HTML sanitization
        if '<script' in value.lower() or 'javascript:' in value.lower():
            raise ValidationError("HTML contains potentially dangerous content")
        
        return value
    
    def _validate_phone(self, value: str) -> str:
        """Validate phone number format."""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
        
        # Check if it's a valid phone number (basic check)
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValidationError("Invalid phone number format")
        
        return cleaned
    
    def _validate_username(self, value: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_\-\.]{3,30}$', value):
            raise ValidationError(
                "Username must be 3-30 characters and contain only letters, numbers, underscore, hyphen, or dot"
            )
        
        return value
    
    def _validate_alphanumeric(self, value: str) -> str:
        """Validate string contains only alphanumeric characters."""
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise ValidationError("Only letters and numbers are allowed")
        
        return value
    
    def _validate_no_special_chars(self, value: str) -> str:
        """Validate string contains no special characters."""
        if re.search(r'[<>\"\'%;()&+\[\]{}\|\\^~`]', value):
            raise ValidationError("Special characters are not allowed")
        
        return value


# Common field definitions with enhanced validation
class SecureFields:
    """Common secure field definitions."""
    
    @staticmethod
    def email(required: bool = True, **kwargs) -> fields.Email:
        """Secure email field."""
        return fields.Email(
            required=required,
            validate=[
                validate.Length(max=254),
                validate.Email(error="Invalid email format")
            ],
            error_messages={
                'required': 'Email is required',
                'invalid': 'Invalid email format'
            },
            **kwargs
        )
    
    @staticmethod
    def password(required: bool = True, **kwargs) -> fields.String:
        """Secure password field with complexity requirements."""
        return fields.String(
            required=required,
            load_only=True,
            validate=[
                validate.Length(min=12, max=128),
                validate.Regexp(
                    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
                    error="Password must contain uppercase, lowercase, number, and special character"
                )
            ],
            error_messages={
                'required': 'Password is required'
            },
            **kwargs
        )
    
    @staticmethod
    def name(required: bool = True, max_length: int = 100, **kwargs) -> fields.String:
        """Secure name field."""
        return fields.String(
            required=required,
            validate=[
                validate.Length(min=1, max=max_length),
                validate.Regexp(
                    r'^[a-zA-Z\s\-\'\.]+$',
                    error="Name can only contain letters, spaces, hyphens, apostrophes, and dots"
                )
            ],
            **kwargs
        )
    
    @staticmethod
    def phone(required: bool = False, **kwargs) -> fields.String:
        """Secure phone field."""
        return fields.String(
            required=required,
            validate=[
                validate.Regexp(
                    r'^[\+\d\s\-\(\)\.]+$',
                    error="Invalid phone number format"
                ),
                validate.Length(min=10, max=20)
            ],
            **kwargs
        )
    
    @staticmethod
    def url(required: bool = False, schemes: List[str] = None, **kwargs) -> fields.URL:
        """Secure URL field."""
        if schemes is None:
            schemes = ['http', 'https']
        
        return fields.URL(
            required=required,
            schemes=schemes,
            validate=[
                validate.Length(max=2000)
            ],
            error_messages={
                'invalid': 'Invalid URL format'
            },
            **kwargs
        )
    
    @staticmethod
    def safe_string(required: bool = True, max_length: int = 255, 
                    allow_special: bool = False, **kwargs) -> fields.String:
        """Secure string field with XSS protection."""
        validators = [validate.Length(min=1, max=max_length)]
        
        if not allow_special:
            validators.append(
                validate.Regexp(
                    r'^[a-zA-Z0-9\s\-_\.,:;!?\'"]+$',
                    error="Special characters are not allowed"
                )
            )
        
        return fields.String(
            required=required,
            validate=validators,
            **kwargs
        )
    
    @staticmethod
    def positive_integer(required: bool = True, **kwargs) -> fields.Integer:
        """Positive integer field."""
        return fields.Integer(
            required=required,
            validate=[
                validate.Range(min=1, error="Value must be positive")
            ],
            **kwargs
        )
    
    @staticmethod
    def currency(required: bool = True, **kwargs) -> fields.Decimal:
        """Currency field with proper decimal places."""
        return fields.Decimal(
            required=required,
            places=2,
            validate=[
                validate.Range(min=0, error="Amount cannot be negative")
            ],
            **kwargs
        )