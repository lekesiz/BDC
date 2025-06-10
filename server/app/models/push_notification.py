"""Push notification models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.extensions import db
import json


class PushNotificationDevice(db.Model):
    """User device tokens for push notifications."""
    __tablename__ = 'push_notification_devices'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Device information
    device_token = Column(String(255), nullable=False, unique=True)
    device_type = Column(String(20), nullable=False)  # ios, android, web
    device_name = Column(String(100), nullable=True)
    device_model = Column(String(100), nullable=True)
    device_os = Column(String(50), nullable=True)
    app_version = Column(String(20), nullable=True)
    
    # Push notification service info
    provider = Column(String(20), nullable=False)  # fcm, apns, webpush
    provider_data = Column(Text, nullable=True)  # JSON with provider-specific data
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='push_devices')
    
    # Indexes
    __table_args__ = (
        Index('idx_push_devices_user_active', 'user_id', 'is_active'),
        Index('idx_push_devices_token', 'device_token'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_token': self.device_token[:10] + '...' if len(self.device_token) > 10 else self.device_token,
            'device_type': self.device_type,
            'device_name': self.device_name,
            'device_model': self.device_model,
            'device_os': self.device_os,
            'app_version': self.app_version,
            'provider': self.provider,
            'is_active': self.is_active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def register_device(cls, user_id, device_token, device_type, provider, **kwargs):
        """Register or update a device token."""
        # Check if device already exists
        device = cls.query.filter_by(device_token=device_token).first()
        
        if device:
            # Update existing device
            device.user_id = user_id
            device.is_active = True
            device.failed_attempts = 0
            device.last_error = None
            
            # Update optional fields
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
        else:
            # Create new device
            device = cls(
                user_id=user_id,
                device_token=device_token,
                device_type=device_type,
                provider=provider,
                **kwargs
            )
            db.session.add(device)
        
        db.session.commit()
        return device
    
    @classmethod
    def get_active_devices(cls, user_id):
        """Get all active devices for a user."""
        return cls.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(cls.last_used_at.desc()).all()
    
    def mark_as_used(self):
        """Mark device as recently used."""
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_failed(self, error_message):
        """Mark a failed push attempt."""
        self.failed_attempts += 1
        self.last_error = error_message
        
        # Deactivate after 5 failed attempts
        if self.failed_attempts >= 5:
            self.is_active = False
        
        db.session.commit()
    
    def deactivate(self):
        """Deactivate this device."""
        self.is_active = False
        db.session.commit()


class PushNotificationLog(db.Model):
    """Log of sent push notifications."""
    __tablename__ = 'push_notification_logs'
    
    id = Column(Integer, primary_key=True)
    
    # Recipient information
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    device_id = Column(Integer, ForeignKey('push_notification_devices.id', ondelete='SET NULL'), nullable=True)
    
    # Notification content
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON payload
    
    # Notification type and priority
    notification_type = Column(String(50), nullable=True)  # message, alert, update, etc.
    priority = Column(String(20), default='normal')  # low, normal, high
    
    # Status
    status = Column(String(20), nullable=False)  # pending, sent, failed, delivered, read
    error_message = Column(Text, nullable=True)
    
    # Provider information
    provider = Column(String(20), nullable=True)
    provider_message_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', backref='push_notifications')
    device = relationship('PushNotificationDevice', backref='notifications')
    
    # Indexes
    __table_args__ = (
        Index('idx_push_logs_user_created', 'user_id', 'created_at'),
        Index('idx_push_logs_status', 'status'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'title': self.title,
            'body': self.body,
            'data': json.loads(self.data) if self.data else None,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    @classmethod
    def create_notification(cls, user_id, title, body, **kwargs):
        """Create a new notification log."""
        notification = cls(
            user_id=user_id,
            title=title,
            body=body,
            status='pending',
            **kwargs
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def mark_as_sent(self, provider_message_id=None):
        """Mark notification as sent."""
        self.status = 'sent'
        self.sent_at = datetime.utcnow()
        if provider_message_id:
            self.provider_message_id = provider_message_id
        db.session.commit()
    
    def mark_as_failed(self, error_message):
        """Mark notification as failed."""
        self.status = 'failed'
        self.error_message = error_message
        db.session.commit()
    
    def mark_as_delivered(self):
        """Mark notification as delivered."""
        self.status = 'delivered'
        self.delivered_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.status = 'read'
        self.read_at = datetime.utcnow()
        db.session.commit()