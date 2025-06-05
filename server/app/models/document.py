"""Document model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.extensions import db

class Document(db.Model):
    """Document model."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    document_type = Column(String(50), nullable=False, default='general')
    is_active = Column(Boolean, default=True)
    upload_by = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id', ondelete='CASCADE'), nullable=True)
    evaluation_id = Column(Integer, ForeignKey('evaluations.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Versioning fields
    current_version = Column(Integer, default=1)
    version_control_enabled = Column(Boolean, default=False)
    max_versions = Column(Integer, default=10)  # Maximum versions to keep
    
    # Additional metadata
    tags = Column(JSON)
    category = Column(String(50))
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # File metadata
    filename = Column(String(255))
    mime_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 hash
    
    # Access tracking
    download_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    
    # Relationships
    uploader = relationship('User', backref='uploaded_documents', lazy='select')
    beneficiary = relationship('Beneficiary', back_populates='documents', lazy='select')
    evaluation = relationship('Evaluation', backref='documents', lazy='select')
    tenant = relationship('Tenant', backref='documents')
    
    def to_dict(self):
        """Return a dict representation of the document."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'document_type': self.document_type,
            'is_active': self.is_active,
            'upload_by': self.upload_by,
            'uploader_name': f"{self.uploader.first_name} {self.uploader.last_name}" if self.uploader else None,
            'beneficiary_id': self.beneficiary_id,
            'evaluation_id': self.evaluation_id,
            'current_version': self.current_version,
            'version_control_enabled': self.version_control_enabled,
            'tags': self.tags,
            'category': self.category,
            'filename': self.filename,
            'mime_type': self.mime_type,
            'download_count': self.download_count,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the document."""
        return f'<Document {self.title}>'