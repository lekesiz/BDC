"""SMS message model for tracking SMS history and delivery status."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Index
from sqlalchemy.orm import relationship

from app.extensions import db


class SMSStatus(Enum):
    """SMS delivery status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"
    CANCELLED = "cancelled"


class SMSType(Enum):
    """SMS message type enumeration."""
    APPOINTMENT_REMINDER = "appointment_reminder"
    ASSESSMENT_NOTIFICATION = "assessment_notification"
    PASSWORD_RESET = "password_reset"
    TWO_FACTOR_AUTH = "two_factor_auth"
    GENERAL_NOTIFICATION = "general_notification"
    WELCOME_MESSAGE = "welcome_message"
    PROGRAM_UPDATE = "program_update"
    EMERGENCY_ALERT = "emergency_alert"


class SMSProvider(Enum):
    """SMS provider enumeration."""
    TWILIO = "twilio"
    AWS_SNS = "aws_sns"
    NEXMO = "nexmo"
    MESSAGEBIRD = "messagebird"
    SINCH = "sinch"


class SMSMessage(db.Model):
    """SMS message model for tracking SMS history."""
    __tablename__ = 'sms_messages'
    
    id = Column(Integer, primary_key=True)
    
    # Recipient information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    recipient_phone = Column(String(20), nullable=False)
    recipient_name = Column(String(100), nullable=True)
    
    # Message details
    message_type = Column(String(50), nullable=False, default=SMSType.GENERAL_NOTIFICATION.value)
    template_id = Column(String(100), nullable=True)
    message_content = Column(Text, nullable=False)
    language = Column(String(5), nullable=False, default='en')
    
    # Provider information
    provider = Column(String(50), nullable=False, default=SMSProvider.TWILIO.value)
    provider_message_id = Column(String(100), nullable=True)
    provider_response = Column(JSON, nullable=True)
    
    # Delivery status
    status = Column(String(20), nullable=False, default=SMSStatus.PENDING.value)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Cost tracking
    cost_amount = Column(Float, nullable=True)
    cost_currency = Column(String(3), nullable=True, default='USD')
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    
    # Related entities
    related_id = Column(Integer, nullable=True)
    related_type = Column(String(50), nullable=True)
    
    # Tenant information
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Metadata
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='sms_messages')
    tenant = relationship('Tenant', backref='sms_messages')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_sms_user_status', 'user_id', 'status'),
        Index('idx_sms_phone_status', 'recipient_phone', 'status'),
        Index('idx_sms_scheduled', 'scheduled_for', 'status'),
        Index('idx_sms_created_at', 'created_at'),
        Index('idx_sms_provider_id', 'provider_message_id'),
    )
    
    def __init__(self, **kwargs):
        """Initialize SMS message with defaults."""
        super(SMSMessage, self).__init__(**kwargs)
        if self.status is None:
            self.status = SMSStatus.PENDING.value
    
    def to_dict(self):
        """Return a dict representation of the SMS message."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recipient_phone': self.recipient_phone,
            'recipient_name': self.recipient_name,
            'message_type': self.message_type,
            'template_id': self.template_id,
            'message_content': self.message_content,
            'language': self.language,
            'provider': self.provider,
            'provider_message_id': self.provider_message_id,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'cost_amount': self.cost_amount,
            'cost_currency': self.cost_currency,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'related_id': self.related_id,
            'related_type': self.related_type,
            'tenant_id': self.tenant_id,
            'metadata': self.extra_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def mark_as_sent(self, provider_message_id=None, provider_response=None):
        """Mark the SMS as sent."""
        self.status = SMSStatus.SENT.value
        self.sent_at = datetime.utcnow()
        if provider_message_id:
            self.provider_message_id = provider_message_id
        if provider_response:
            self.provider_response = provider_response
    
    def mark_as_delivered(self):
        """Mark the SMS as delivered."""
        self.status = SMSStatus.DELIVERED.value
        self.delivered_at = datetime.utcnow()
    
    def mark_as_failed(self, error_message=None):
        """Mark the SMS as failed."""
        self.status = SMSStatus.FAILED.value
        self.failed_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message
    
    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
    
    def __repr__(self):
        """String representation of the SMS message."""
        return f'<SMSMessage {self.id}: {self.recipient_phone} - {self.status}>'


class SMSTemplate(db.Model):
    """SMS template model for managing message templates."""
    __tablename__ = 'sms_templates'
    
    id = Column(Integer, primary_key=True)
    
    # Template identification
    template_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content
    content_en = Column(Text, nullable=False)  # English content
    content_tr = Column(Text, nullable=True)   # Turkish content
    
    # Template type
    message_type = Column(String(50), nullable=False)
    
    # Variables
    variables = Column(JSON, nullable=True)  # List of variable names
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Tenant
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='sms_templates')
    
    def get_content(self, language='en'):
        """Get template content in specified language."""
        if language == 'tr' and self.content_tr:
            return self.content_tr
        return self.content_en
    
    def render(self, variables=None, language='en'):
        """Render template with variables."""
        content = self.get_content(language)
        if variables:
            for key, value in variables.items():
                placeholder = f'{{{{{key}}}}}'
                content = content.replace(placeholder, str(value))
        return content
    
    def to_dict(self):
        """Return a dict representation of the SMS template."""
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'content_en': self.content_en,
            'content_tr': self.content_tr,
            'message_type': self.message_type,
            'variables': self.variables,
            'is_active': self.is_active,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the SMS template."""
        return f'<SMSTemplate {self.template_id}: {self.name}>'


class SMSCampaign(db.Model):
    """SMS campaign model for bulk SMS operations."""
    __tablename__ = 'sms_campaigns'
    
    id = Column(Integer, primary_key=True)
    
    # Campaign details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template
    template_id = Column(String(100), nullable=True)
    message_content = Column(Text, nullable=True)
    
    # Recipients
    recipient_count = Column(Integer, default=0)
    recipient_filters = Column(JSON, nullable=True)  # Filters for selecting recipients
    
    # Status
    status = Column(String(20), nullable=False, default='draft')  # draft, scheduled, running, completed, cancelled
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Statistics
    messages_sent = Column(Integer, default=0)
    messages_delivered = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Tenant
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='sms_campaigns')
    creator = relationship('User', backref='created_sms_campaigns')
    
    def to_dict(self):
        """Return a dict representation of the SMS campaign."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_id': self.template_id,
            'message_content': self.message_content,
            'recipient_count': self.recipient_count,
            'recipient_filters': self.recipient_filters,
            'status': self.status,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'messages_sent': self.messages_sent,
            'messages_delivered': self.messages_delivered,
            'messages_failed': self.messages_failed,
            'total_cost': self.total_cost,
            'tenant_id': self.tenant_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the SMS campaign."""
        return f'<SMSCampaign {self.id}: {self.name}>'