"""Document repository implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.document_repository_interface import IDocumentRepository
from app.models import Document
from app.extensions import db


class DocumentRepository(BaseRepository[Document], IDocumentRepository):
    """Document repository implementation."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize document repository."""
        super().__init__(Document, db_session)
    
    def find_by_uploader_id(self, uploader_id: int) -> List[Document]:
        """Find documents by uploader ID."""
        return self.db_session.query(Document).filter_by(
            upload_by=uploader_id
        ).order_by(Document.created_at.desc()).all()
    
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Document]:
        """Find documents by beneficiary ID."""
        return self.db_session.query(Document).filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(Document.created_at.desc()).all()
    
    def find_by_evaluation_id(self, evaluation_id: int) -> List[Document]:
        """Find documents by evaluation ID."""
        return self.db_session.query(Document).filter_by(
            evaluation_id=evaluation_id
        ).order_by(Document.created_at.desc()).all()
    
    def find_by_type(self, document_type: str) -> List[Document]:
        """Find documents by type."""
        return self.db_session.query(Document).filter_by(
            document_type=document_type
        ).order_by(Document.created_at.desc()).all()
    
    def find_active_documents(self) -> List[Document]:
        """Find all active documents."""
        return self.db_session.query(Document).filter_by(
            is_active=True
        ).order_by(Document.created_at.desc()).all()
    
    def search(self, query: str, document_type: Optional[str] = None,
              uploader_id: Optional[int] = None) -> List[Document]:
        """Search documents by title and description."""
        search_filter = or_(
            Document.title.ilike(f'%{query}%'),
            Document.description.ilike(f'%{query}%')
        )
        
        filters = [search_filter]
        
        if document_type:
            filters.append(Document.document_type == document_type)
        if uploader_id:
            filters.append(Document.upload_by == uploader_id)
        
        return self.db_session.query(Document).filter(
            and_(*filters)
        ).order_by(Document.created_at.desc()).all()
    
    def get_statistics(self, uploader_id: Optional[int] = None) -> Dict[str, Any]:
        """Get document statistics."""
        query = self.db_session.query(Document)
        
        if uploader_id:
            query = query.filter_by(upload_by=uploader_id)
        
        total_count = query.count()
        active_count = query.filter_by(is_active=True).count()
        
        # Get type distribution
        type_stats = {}
        for doc_type, count in query.with_entities(
            Document.document_type, 
            db.func.count(Document.id)
        ).group_by(Document.document_type).all():
            type_stats[doc_type] = count
        
        # Calculate total file size
        total_size = query.with_entities(
            db.func.sum(Document.file_size)
        ).scalar() or 0
        
        return {
            'total_documents': total_count,
            'active_documents': active_count,
            'inactive_documents': total_count - active_count,
            'total_file_size': total_size,
            'documents_by_type': type_stats
        }
    
    def create(self, **kwargs) -> Document:
        """Create a new document."""
        document = Document(**kwargs)
        self.db_session.add(document)
        self.db_session.flush()
        return document
    
    def update(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document by ID."""
        document = self.find_by_id(document_id)
        if not document:
            return None
        
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)
        
        document.updated_at = datetime.utcnow()
        self.db_session.flush()
        return document
    
    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        document = self.find_by_id(document_id)
        if not document:
            return False
        
        self.db_session.delete(document)
        self.db_session.flush()
        return True
    
    def save(self, document: Document) -> Document:
        """Save document instance."""
        self.db_session.add(document)
        self.db_session.flush()
        return document
    
    def find_all(self, limit: int = None, offset: int = None) -> List[Document]:
        """Find all documents with optional pagination."""
        query = self.db_session.query(Document).order_by(Document.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count(self) -> int:
        """Count total documents."""
        return self.db_session.query(Document).count()