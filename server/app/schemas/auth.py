"""Authentication schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from app.models import User


class LoginSchema(Schema):
    """Schema for login requests."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    remember_me = fields.Boolean(load_default=False)


class RegisterSchema(Schema):
    """Schema for registration requests."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, 
                           validate=validate.Length(min=8, error="Password must be at least 8 characters long"))
    confirm_password = fields.String(required=True, load_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    role = fields.String(validate=validate.OneOf(['tenant_admin', 'trainer', 'student']), load_default='student')
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validate that passwords match."""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_password')
    
    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already in use."""
        user = User.query.filter_by(email=value).first()
        if user:
            raise ValidationError('Email already registered')


class TokenSchema(Schema):
    """Schema for authentication tokens."""
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(required=True)
    expires_in = fields.Integer(required=True)


class RefreshTokenSchema(Schema):
    """Schema for refresh token requests."""
    refresh_token = fields.String(required=True)


class ResetPasswordRequestSchema(Schema):
    """Schema for password reset requests."""
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    """Schema for password reset."""
    token = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    confirm_password = fields.String(required=True)
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validate that passwords match."""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_password')


class ChangePasswordSchema(Schema):
    """Schema for password change."""
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))
    confirm_password = fields.String(required=True)
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Validate that passwords match."""
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_name='confirm_password')