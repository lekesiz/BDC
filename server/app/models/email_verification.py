"""Email verification model."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import secrets
from app.extensions import db


class EmailVerificationToken(db.Model):
    """Email verification token model."""
    __tablename__ = 'email_verification_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    email = Column(String(120), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', backref='verification_tokens')
    
    def __init__(self, user_id, email, expires_in_hours=24):
        """Initialize verification token."""
        self.user_id = user_id
        self.email = email
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        self.used_at = datetime.utcnow()
    
    @classmethod
    def create_for_user(cls, user, expires_in_hours=24):
        """Create a verification token for a user."""
        token = cls(
            user_id=user.id,
            email=user.email,
            expires_in_hours=expires_in_hours
        )
        db.session.add(token)
        db.session.commit()
        return token
    
    @classmethod
    def verify_token(cls, token_string):
        """Verify a token and return the associated user."""
        token = cls.query.filter_by(
            token=token_string,
            is_used=False
        ).first()
        
        if not token:
            return None, "Invalid verification token"
        
        if token.is_expired():
            return None, "Verification token has expired"
        
        # Mark token as used
        token.mark_as_used()
        db.session.commit()
        
        return token.user, None
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'expires_at': self.expires_at.isoformat(),
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat()
        }