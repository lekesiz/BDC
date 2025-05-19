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
