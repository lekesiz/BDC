"""Activity model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.extensions import db


class Activity(db.Model):
    """Activity model for tracking user actions."""
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Activity details
    type = Column(String(50), nullable=False)  # login, logout, test_completed, etc.
    description = Column(Text)
    activity_data = Column(JSON)  # Additional data about the activity
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship('User', backref='activities')
    
    def to_dict(self):
        """Return a dict representation of the activity."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'description': self.description,
            'activity_data': self.activity_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
