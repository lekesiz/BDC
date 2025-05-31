"""Settings models."""

from app.extensions import db
from datetime import datetime


class GeneralSettings(db.Model):
    """General settings model for tenant configuration."""
    __tablename__ = 'general_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, unique=True)
    
    # Site Information
    site_name = db.Column(db.String(100), nullable=False, default='Beneficiary Development Center')
    site_logo = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#3B82F6')  # Hex color
    secondary_color = db.Column(db.String(7), default='#1E40AF')  # Hex color
    
    # Notification Settings
    enable_notifications = db.Column(db.Boolean, default=True)
    enable_email_notifications = db.Column(db.Boolean, default=True)
    enable_sms_notifications = db.Column(db.Boolean, default=False)
    
    # Localization
    default_language = db.Column(db.String(5), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    date_format = db.Column(db.String(20), default='MM/DD/YYYY')
    time_format = db.Column(db.String(10), default='12h')  # 12h or 24h
    week_starts_on = db.Column(db.String(10), default='sunday')  # sunday or monday
    
    # Business Hours
    working_hours_start = db.Column(db.String(5), default='09:00')
    working_hours_end = db.Column(db.String(5), default='17:00')
    
    # File Upload Settings
    max_file_upload_size = db.Column(db.Integer, default=10485760)  # 10MB in bytes
    allowed_file_types = db.Column(db.JSON, default=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'])
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='general_settings')
    
    def __repr__(self):
        return f'<GeneralSettings {self.tenant_id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'site_name': self.site_name,
            'site_logo': self.site_logo,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'enable_notifications': self.enable_notifications,
            'enable_email_notifications': self.enable_email_notifications,
            'enable_sms_notifications': self.enable_sms_notifications,
            'default_language': self.default_language,
            'timezone': self.timezone,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'week_starts_on': self.week_starts_on,
            'working_hours_start': self.working_hours_start,
            'working_hours_end': self.working_hours_end,
            'max_file_upload_size': self.max_file_upload_size,
            'allowed_file_types': self.allowed_file_types,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AppearanceSettings(db.Model):
    """Appearance settings for UI customization."""
    __tablename__ = 'appearance_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For user-specific settings
    
    # Theme Settings
    theme = db.Column(db.String(20), default='light')  # light, dark, or auto
    font_family = db.Column(db.String(50), default='Inter')
    font_size = db.Column(db.String(10), default='medium')  # small, medium, large
    
    # Layout Settings
    sidebar_position = db.Column(db.String(10), default='left')  # left or right
    sidebar_collapsed = db.Column(db.Boolean, default=False)
    compact_mode = db.Column(db.Boolean, default=False)
    
    # Color Scheme
    accent_color = db.Column(db.String(7))  # Hex color
    background_color = db.Column(db.String(7))  # Hex color
    text_color = db.Column(db.String(7))  # Hex color
    
    # Component Settings
    rounded_corners = db.Column(db.Boolean, default=True)
    show_animations = db.Column(db.Boolean, default=True)
    animation_speed = db.Column(db.String(10), default='normal')  # slow, normal, fast
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='appearance_settings')
    user = db.relationship('User', backref='appearance_settings')
    
    def __repr__(self):
        return f'<AppearanceSettings {self.tenant_id}:{self.user_id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'theme': self.theme,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'sidebar_position': self.sidebar_position,
            'sidebar_collapsed': self.sidebar_collapsed,
            'compact_mode': self.compact_mode,
            'accent_color': self.accent_color,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'rounded_corners': self.rounded_corners,
            'show_animations': self.show_animations,
            'animation_speed': self.animation_speed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class NotificationSettings(db.Model):
    """Notification settings for user preferences."""
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Email Notifications
    email_new_message = db.Column(db.Boolean, default=True)
    email_appointment_reminder = db.Column(db.Boolean, default=True)
    email_assessment_assigned = db.Column(db.Boolean, default=True)
    email_assessment_completed = db.Column(db.Boolean, default=True)
    email_document_shared = db.Column(db.Boolean, default=True)
    email_program_update = db.Column(db.Boolean, default=True)
    email_weekly_summary = db.Column(db.Boolean, default=False)
    
    # In-App Notifications
    app_new_message = db.Column(db.Boolean, default=True)
    app_appointment_reminder = db.Column(db.Boolean, default=True)
    app_assessment_assigned = db.Column(db.Boolean, default=True)
    app_assessment_completed = db.Column(db.Boolean, default=True)
    app_document_shared = db.Column(db.Boolean, default=True)
    app_program_update = db.Column(db.Boolean, default=True)
    
    # SMS Notifications
    sms_appointment_reminder = db.Column(db.Boolean, default=False)
    sms_assessment_deadline = db.Column(db.Boolean, default=False)
    
    # Quiet Hours
    quiet_hours_enabled = db.Column(db.Boolean, default=False)
    quiet_hours_start = db.Column(db.String(5), default='22:00')
    quiet_hours_end = db.Column(db.String(5), default='08:00')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notification_settings')
    
    def __repr__(self):
        return f'<NotificationSettings {self.user_id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_new_message': self.email_new_message,
            'email_appointment_reminder': self.email_appointment_reminder,
            'email_assessment_assigned': self.email_assessment_assigned,
            'email_assessment_completed': self.email_assessment_completed,
            'email_document_shared': self.email_document_shared,
            'email_program_update': self.email_program_update,
            'email_weekly_summary': self.email_weekly_summary,
            'app_new_message': self.app_new_message,
            'app_appointment_reminder': self.app_appointment_reminder,
            'app_assessment_assigned': self.app_assessment_assigned,
            'app_assessment_completed': self.app_assessment_completed,
            'app_document_shared': self.app_document_shared,
            'app_program_update': self.app_program_update,
            'sms_appointment_reminder': self.sms_appointment_reminder,
            'sms_assessment_deadline': self.sms_assessment_deadline,
            'quiet_hours_enabled': self.quiet_hours_enabled,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Create an alias for backward compatibility
Settings = GeneralSettings