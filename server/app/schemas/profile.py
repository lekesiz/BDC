"""User profile schemas."""

from marshmallow import Schema, fields, validate, validates, ValidationError


class UserProfileSchema(Schema):
    """Schema for UserProfile model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    avatar_url = fields.String()
    phone_number = fields.String()
    job_title = fields.String()
    department = fields.String()
    bio = fields.String()
    location = fields.String()
    linkedin_url = fields.String()
    twitter_url = fields.String()
    website_url = fields.String()
    timezone = fields.String()
    language = fields.String(validate=validate.OneOf(['en', 'fr', 'tr', 'de', 'es']))
    notification_preferences = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserProfileUpdateSchema(Schema):
    """Schema for updating a user profile."""
    avatar_url = fields.String()
    phone_number = fields.String()
    job_title = fields.String()
    department = fields.String()
    bio = fields.String()
    location = fields.String()
    linkedin_url = fields.URL(allow_none=True)
    twitter_url = fields.URL(allow_none=True)
    website_url = fields.URL(allow_none=True)
    timezone = fields.String()
    language = fields.String(validate=validate.OneOf(['en', 'fr', 'tr', 'de', 'es']))
    notification_preferences = fields.String()
    
    @validates('linkedin_url')
    def validate_linkedin_url(self, value):
        """Validate LinkedIn URL format."""
        if value and 'linkedin.com' not in value:
            raise ValidationError('Must be a valid LinkedIn URL')
            
    @validates('twitter_url')
    def validate_twitter_url(self, value):
        """Validate Twitter URL format."""
        if value and 'twitter.com' not in value and 'x.com' not in value:
            raise ValidationError('Must be a valid Twitter/X URL')