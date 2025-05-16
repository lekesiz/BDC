"""User profile model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db

class UserProfile(db.Model):
    """User profile model."""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    avatar_url = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    twitter_url = Column(String(255), nullable=True)
    website_url = Column(String(255), nullable=True)
    timezone = Column(String(50), nullable=True, default='UTC')
    language = Column(String(10), nullable=True, default='en')
    notification_preferences = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='profile', uselist=False)
    
    def to_dict(self):
        """Return a dict representation of the user profile."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'avatar_url': self.avatar_url,
            'phone_number': self.phone_number,
            'job_title': self.job_title,
            'department': self.department,
            'bio': self.bio,
            'location': self.location,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'website_url': self.website_url,
            'timezone': self.timezone,
            'language': self.language,
            'notification_preferences': self.notification_preferences,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the user profile."""
        return f'<UserProfile user_id={self.user_id}>'