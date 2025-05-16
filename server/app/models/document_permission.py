"""Document permission model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.extensions import db

class DocumentPermission(db.Model):
    """Document permission model for access control."""
    __tablename__ = 'document_permissions'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    role = Column(String(50), nullable=True)  # If not user-specific, but role-based
    
    # Permissions (CRUD operations)
    can_read = Column(Boolean, default=True)
    can_update = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    
    # Expiry and status
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship('Document', backref='permissions')
    user = relationship('User', backref='document_permissions')
    
    def to_dict(self):
        """Return a dict representation of the document permission."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'role': self.role,
            'can_read': self.can_read,
            'can_update': self.can_update,
            'can_delete': self.can_delete,
            'can_share': self.can_share,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def has_expired(self):
        """Check if the permission has expired."""
        if not self.expires_at:
            return False
        
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        """String representation of the document permission."""
        if self.user_id:
            return f'<DocumentPermission document={self.document_id} user={self.user_id}>'
        return f'<DocumentPermission document={self.document_id} role={self.role}>'