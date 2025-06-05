"""Document version model for tracking document history."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from app.extensions import db


class DocumentVersion(db.Model):
    """Document version model for version control."""
    __tablename__ = 'document_versions'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # File information
    file_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 hash for integrity
    
    # Version metadata
    title = Column(String(255))
    description = Column(Text)
    change_notes = Column(Text)  # What changed in this version
    
    # User who created this version
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Status
    is_current = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship('Document', backref='versions')
    creator = relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        """Return a dict representation of the document version."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'version_number': self.version_number,
            'filename': self.filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_hash': self.file_hash,
            'title': self.title,
            'description': self.description,
            'change_notes': self.change_notes,
            'created_by': self.created_by,
            'creator': {
                'id': self.creator.id,
                'name': f"{self.creator.first_name} {self.creator.last_name}",
                'email': self.creator.email
            } if self.creator else None,
            'is_current': self.is_current,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the document version."""
        return f'<DocumentVersion {self.id}: Document {self.document_id} v{self.version_number}>'


class DocumentComparison(db.Model):
    """Model for storing document comparison results."""
    __tablename__ = 'document_comparisons'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    version1_id = Column(Integer, ForeignKey('document_versions.id'), nullable=False)
    version2_id = Column(Integer, ForeignKey('document_versions.id'), nullable=False)
    
    # Comparison results
    similarity_score = Column(Float)  # 0-100 similarity percentage
    differences = Column(JSON)  # Detailed differences
    comparison_type = Column(String(50))  # 'text', 'binary', 'structural'
    
    # User who requested comparison
    compared_by = Column(Integer, ForeignKey('users.id'))
    compared_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship('Document')
    version1 = relationship('DocumentVersion', foreign_keys=[version1_id])
    version2 = relationship('DocumentVersion', foreign_keys=[version2_id])
    user = relationship('User')
    
    def to_dict(self):
        """Return a dict representation of the comparison."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'version1': {
                'id': self.version1_id,
                'version_number': self.version1.version_number,
                'created_at': self.version1.created_at.isoformat()
            } if self.version1 else None,
            'version2': {
                'id': self.version2_id,
                'version_number': self.version2.version_number,
                'created_at': self.version2.created_at.isoformat()
            } if self.version2 else None,
            'similarity_score': self.similarity_score,
            'differences': self.differences,
            'comparison_type': self.comparison_type,
            'compared_by': self.compared_by,
            'compared_at': self.compared_at.isoformat() if self.compared_at else None
        }