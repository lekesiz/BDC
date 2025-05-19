"""Settings schemas for validation."""

from marshmallow import Schema, fields, validate, ValidationError


class GeneralSettingsSchema(Schema):
    """Schema for general settings."""
    id = fields.Int(dump_only=True)
    tenant_id = fields.Int(dump_only=True)
    
    # Site Information
    site_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    site_logo = fields.Str(allow_none=True)
    primary_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'))
    secondary_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'))
    
    # Notification Settings
    enable_notifications = fields.Bool()
    enable_email_notifications = fields.Bool()
    enable_sms_notifications = fields.Bool()
    
    # Localization
    default_language = fields.Str(validate=validate.Length(min=2, max=5))
    timezone = fields.Str(validate=validate.Length(min=1, max=50))
    date_format = fields.Str(validate=validate.OneOf([
        'MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD', 
        'DD.MM.YYYY', 'MMM DD, YYYY', 'DD MMM YYYY'
    ]))
    time_format = fields.Str(validate=validate.OneOf(['12h', '24h']))
    week_starts_on = fields.Str(validate=validate.OneOf(['sunday', 'monday']))
    
    # Business Hours
    working_hours_start = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    working_hours_end = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    
    # File Upload Settings
    max_file_upload_size = fields.Int(validate=validate.Range(min=1024, max=104857600))  # 1KB to 100MB
    allowed_file_types = fields.List(fields.Str())
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class GeneralSettingsUpdateSchema(Schema):
    """Schema for updating general settings."""
    # Site Information
    site_name = fields.Str(validate=validate.Length(min=1, max=100))
    site_logo = fields.Str(allow_none=True)
    primary_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'))
    secondary_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'))
    
    # Notification Settings
    enable_notifications = fields.Bool()
    enable_email_notifications = fields.Bool()
    enable_sms_notifications = fields.Bool()
    
    # Localization
    default_language = fields.Str(validate=validate.Length(min=2, max=5))
    timezone = fields.Str(validate=validate.Length(min=1, max=50))
    date_format = fields.Str(validate=validate.OneOf([
        'MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD', 
        'DD.MM.YYYY', 'MMM DD, YYYY', 'DD MMM YYYY'
    ]))
    time_format = fields.Str(validate=validate.OneOf(['12h', '24h']))
    week_starts_on = fields.Str(validate=validate.OneOf(['sunday', 'monday']))
    
    # Business Hours
    working_hours_start = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    working_hours_end = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    
    # File Upload Settings
    max_file_upload_size = fields.Int(validate=validate.Range(min=1024, max=104857600))
    allowed_file_types = fields.List(fields.Str())


class AppearanceSettingsSchema(Schema):
    """Schema for appearance settings."""
    id = fields.Int(dump_only=True)
    tenant_id = fields.Int(dump_only=True)
    user_id = fields.Int(allow_none=True)
    
    # Theme Settings
    theme = fields.Str(validate=validate.OneOf(['light', 'dark', 'auto']))
    font_family = fields.Str(validate=validate.Length(max=50))
    font_size = fields.Str(validate=validate.OneOf(['small', 'medium', 'large']))
    
    # Layout Settings
    sidebar_position = fields.Str(validate=validate.OneOf(['left', 'right']))
    sidebar_collapsed = fields.Bool()
    compact_mode = fields.Bool()
    
    # Color Scheme
    accent_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'), allow_none=True)
    background_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'), allow_none=True)
    text_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'), allow_none=True)
    
    # Component Settings
    rounded_corners = fields.Bool()
    show_animations = fields.Bool()
    animation_speed = fields.Str(validate=validate.OneOf(['slow', 'normal', 'fast']))
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class AppearanceSettingsUpdateSchema(Schema):
    """Schema for updating appearance settings."""
    # Theme Settings
    theme = fields.Str(validate=validate.OneOf(['light', 'dark', 'auto']))
    font_family = fields.Str(validate=validate.Length(max=50))
    font_size = fields.Str(validate=validate.OneOf(['small', 'medium', 'large']))
    
    # Layout Settings
    sidebar_position = fields.Str(validate=validate.OneOf(['left', 'right']))
    sidebar_collapsed = fields.Bool()
    compact_mode = fields.Bool()
    
    # Color Scheme
    accent_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'), allow_none=True)
    background_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'), allow_none=True)
    text_color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'), allow_none=True)
    
    # Component Settings
    rounded_corners = fields.Bool()
    show_animations = fields.Bool()
    animation_speed = fields.Str(validate=validate.OneOf(['slow', 'normal', 'fast']))


class NotificationSettingsSchema(Schema):
    """Schema for notification settings."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    
    # Email Notifications
    email_new_message = fields.Bool()
    email_appointment_reminder = fields.Bool()
    email_assessment_assigned = fields.Bool()
    email_assessment_completed = fields.Bool()
    email_document_shared = fields.Bool()
    email_program_update = fields.Bool()
    email_weekly_summary = fields.Bool()
    
    # In-App Notifications
    app_new_message = fields.Bool()
    app_appointment_reminder = fields.Bool()
    app_assessment_assigned = fields.Bool()
    app_assessment_completed = fields.Bool()
    app_document_shared = fields.Bool()
    app_program_update = fields.Bool()
    
    # SMS Notifications
    sms_appointment_reminder = fields.Bool()
    sms_assessment_deadline = fields.Bool()
    
    # Quiet Hours
    quiet_hours_enabled = fields.Bool()
    quiet_hours_start = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    quiet_hours_end = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class NotificationSettingsUpdateSchema(Schema):
    """Schema for updating notification settings."""
    # Email Notifications
    email_new_message = fields.Bool()
    email_appointment_reminder = fields.Bool()
    email_assessment_assigned = fields.Bool()
    email_assessment_completed = fields.Bool()
    email_document_shared = fields.Bool()
    email_program_update = fields.Bool()
    email_weekly_summary = fields.Bool()
    
    # In-App Notifications
    app_new_message = fields.Bool()
    app_appointment_reminder = fields.Bool()
    app_assessment_assigned = fields.Bool()
    app_assessment_completed = fields.Bool()
    app_document_shared = fields.Bool()
    app_program_update = fields.Bool()
    
    # SMS Notifications
    sms_appointment_reminder = fields.Bool()
    sms_assessment_deadline = fields.Bool()
    
    # Quiet Hours
    quiet_hours_enabled = fields.Bool()
    quiet_hours_start = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))
    quiet_hours_end = fields.Str(validate=validate.Regexp(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'))