"""User preference model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class UserPreference(db.Model):
    """User preference model."""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    # UI preferences
    theme = Column(String(20), default='light')
    language = Column(String(10), default='en')
    
    # Notification preferences
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # Privacy preferences
    profile_visibility = Column(String(20), default='all')  # 'all', 'users', 'none'
    show_online_status = Column(Boolean, default=True)
    share_activity = Column(Boolean, default=True)
    allow_data_collection = Column(Boolean, default=True)
    
    # Additional UI preferences
    sidebar_collapsed = Column(Boolean, default=False)
    density = Column(String(20), default='normal')  # 'compact', 'normal', 'comfortable'
    accent_color = Column(String(20), default='blue')
    font_size = Column(String(20), default='medium')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship('User', backref='preferences')
    
    def to_dict(self):
        """Return a dict representation of the user preference."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'notifications_enabled': self.notifications_enabled,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'push_notifications': self.push_notifications,
            'profile_visibility': self.profile_visibility,
            'show_online_status': self.show_online_status,
            'share_activity': self.share_activity,
            'allow_data_collection': self.allow_data_collection,
            'sidebar_collapsed': self.sidebar_collapsed,
            'density': self.density,
            'accent_color': self.accent_color,
            'font_size': self.font_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
