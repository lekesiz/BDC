"""Folder model for organizing documents."""

from datetime import datetime
from app.extensions import db


class Folder(db.Model):
    """Model for organizing documents in folders."""
    __tablename__ = 'folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'))
    path = db.Column(db.String(1000))  # Full path for easy querying
    
    # Ownership
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Permissions
    is_public = db.Column(db.Boolean, default=False)
    is_shared = db.Column(db.Boolean, default=False)
    
    # Metadata
    color = db.Column(db.String(7))  # Hex color code
    icon = db.Column(db.String(50))  # Icon name
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('Folder', remote_side=[id], backref='subfolders')
    owner = db.relationship('User', back_populates='folders')
    tenant = db.relationship('Tenant', back_populates='folders')
    # documents = db.relationship('Document', backref='folder', lazy='dynamic')  # Document model doesn't have folder_id
    
    def to_dict(self):
        """Convert folder to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'path': self.path,
            'owner_id': self.owner_id,
            'is_public': self.is_public,
            'is_shared': self.is_shared,
            'color': self.color,
            'icon': self.icon,
            'subfolder_count': len(self.subfolders) if hasattr(self, 'subfolders') else 0,
            'document_count': 0,  # self.documents.count() if hasattr(self.documents, 'count') else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }