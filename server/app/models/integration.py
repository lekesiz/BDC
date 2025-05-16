"""Integration model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.extensions import db

class UserIntegration(db.Model):
    """User integration model for external services."""
    __tablename__ = 'user_integrations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    provider = Column(String(50), nullable=False)  # 'google_calendar', 'microsoft_calendar', etc.
    status = Column(String(20), nullable=False, default='pending')  # 'pending', 'active', 'error'
    data = Column(Text, nullable=True)  # JSON string with integration data (tokens, etc.)
    error_message = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='integrations')
    
    def to_dict(self):
        """Return a dict representation of the integration."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the integration."""
        return f'<UserIntegration user_id={self.user_id} provider={self.provider}>'