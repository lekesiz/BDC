"""User activity tracking model."""
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

from app.extensions import db


class UserActivity(db.Model):
    """Model for tracking user activities."""
    
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    details = db.Column(JSON, default={})
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_activities', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        """String representation."""
        return f'<UserActivity {self.activity_type} by user {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }