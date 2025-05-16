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
