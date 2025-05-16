"""User schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import User


class UserBaseSchema(Schema):
    """Base schema for User model."""
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    role = fields.String(validate=validate.OneOf(['super_admin', 'tenant_admin', 'trainer', 'student']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserSchema(UserBaseSchema):
    """Schema for User model."""
    is_active = fields.Boolean()
    last_login = fields.DateTime(dump_only=True)
    tenants = fields.List(fields.Nested('TenantSchema', only=('id', 'name')), dump_only=True)


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a user."""
    password = fields.String(required=True, load_only=True, 
                           validate=validate.Length(min=8, error="Password must be at least 8 characters long"))
    confirm_password = fields.String(required=True, load_only=True)
    tenant_id = fields.Integer(required=False)
    
    @validates('confirm_password')
    def validate_confirm_password(self, value):
        """Validate that passwords match."""
        if value != self.context.get('password'):
            raise ValidationError('Passwords do not match')
    
    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already in use."""
        user = User.query.filter_by(email=value).first()
        if user:
            raise ValidationError('Email already registered')


class UserUpdateSchema(Schema):
    """Schema for updating a user."""
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    role = fields.String(validate=validate.OneOf(['super_admin', 'tenant_admin', 'trainer', 'student']))
    is_active = fields.Boolean()
    
    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already in use by another user."""
        user_id = self.context.get('user_id')
        user = User.query.filter_by(email=value).first()
        if user and user.id != user_id:
            raise ValidationError('Email already registered')


class UserProfileSchema(Schema):
    """Schema for user profile."""
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email(dump_only=True)
    role = fields.String(dump_only=True)
    
    # Profile specific fields could be added here
    avatar = fields.String()
    phone = fields.String()
    language = fields.String()
    theme = fields.String()
    timezone = fields.String()
    notification_preferences = fields.Dict()


class TenantSchema(Schema):
    """Schema for Tenant model."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    subdomain = fields.String(required=True)
    logo_url = fields.String()
    primary_color = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TenantCreateSchema(Schema):
    """Schema for creating a tenant."""
    name = fields.String(required=True)
    subdomain = fields.String(required=True)
    logo_url = fields.String()
    primary_color = fields.String()
    admin_email = fields.Email(required=True)
    admin_password = fields.String(required=True, load_only=True)
    admin_first_name = fields.String(required=True)
    admin_last_name = fields.String(required=True)
    
    @validates('subdomain')
    def validate_subdomain(self, value):
        """Validate that subdomain is valid and not already in use."""
        from app.models import Tenant
        import re
        
        if not re.match(r'^[a-z0-9-]+$', value):
            raise ValidationError('Subdomain can only contain lowercase letters, numbers, and hyphens')
        
        tenant = Tenant.query.filter_by(subdomain=value).first()
        if tenant:
            raise ValidationError('Subdomain already in use')


class TenantUpdateSchema(Schema):
    """Schema for updating a tenant."""
    name = fields.String()
    logo_url = fields.String()
    primary_color = fields.String()
    is_active = fields.Boolean()