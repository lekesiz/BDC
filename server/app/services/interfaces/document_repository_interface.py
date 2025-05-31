"""Document repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.models.document import Document
from app.models.document_permission import DocumentPermission


class IDocumentRepository(ABC):
    """Interface for document repository."""
    
    @abstractmethod
    def find_by_id(self, document_id: int) -> Optional[Document]:
        """Find document by ID."""
        pass
    
    @abstractmethod
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Document]:
        """Find documents by beneficiary ID."""
        pass
    
    @abstractmethod
    def find_by_uploader_id(self, uploader_id: int) -> List[Document]:
        """Find documents by uploader ID."""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = None, offset: int = None) -> List[Document]:
        """Find all documents with optional pagination."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> Document:
        """Create a new document."""
        pass
    
    @abstractmethod
    def update(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document by ID."""
        pass
    
    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        pass
    
    @abstractmethod
    def save(self, document: Document) -> Document:
        """Save document instance."""
        pass
    
    # DocumentPermission related methods
    @abstractmethod
    def create_permission(self, **kwargs) -> DocumentPermission:
        """Create a new document permission."""
        pass
    
    @abstractmethod
    def find_permission_by_document_and_user(self, document_id: int, user_id: int) -> Optional[DocumentPermission]:
        """Find permission by document and user."""
        pass
    
    @abstractmethod
    def find_permission_by_document_and_role(self, document_id: int, role: str) -> Optional[DocumentPermission]:
        """Find permission by document and role."""
        pass
    
    @abstractmethod
    def find_permissions_by_document(self, document_id: int, is_active: bool = True) -> List[DocumentPermission]:
        """Find all permissions for a document."""
        pass
    
    @abstractmethod
    def find_permissions_by_user(self, user_id: int, is_active: bool = True) -> List[DocumentPermission]:
        """Find all permissions for a user."""
        pass
    
    @abstractmethod
    def update_permission(self, permission: DocumentPermission) -> DocumentPermission:
        """Update document permission."""
        pass