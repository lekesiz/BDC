"""Document repository interface."""
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models import Document, DocumentShare, Folder
from app.repositories.v2.interfaces.base_repository_interface import IBaseRepository


class IDocumentRepository(IBaseRepository[Document]):
    """Document repository interface with document-specific operations."""
    
    @abstractmethod
    def find_by_beneficiary(self, beneficiary_id: int) -> List[Document]:
        """Find all documents for a beneficiary."""
        pass
    
    @abstractmethod
    def find_by_folder(self, folder_id: int) -> List[Document]:
        """Find all documents in a folder."""
        pass
    
    @abstractmethod
    def find_by_uploaded_by(self, user_id: int) -> List[Document]:
        """Find all documents uploaded by a user."""
        pass
    
    @abstractmethod
    def find_by_type(self, document_type: str) -> List[Document]:
        """Find all documents of a specific type."""
        pass
    
    @abstractmethod
    def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Search documents with filters."""
        pass
    
    @abstractmethod
    def create_folder(self, folder_data: Dict[str, Any]) -> Folder:
        """Create a new folder."""
        pass
    
    @abstractmethod
    def get_folders(self, parent_id: Optional[int] = None) -> List[Folder]:
        """Get folders, optionally filtered by parent."""
        pass
    
    @abstractmethod
    def move_document(self, document_id: int, folder_id: Optional[int]) -> bool:
        """Move document to a folder."""
        pass
    
    @abstractmethod
    def share_document(self, document_id: int, shared_with_id: int, 
                      permissions: str = 'view') -> DocumentShare:
        """Share document with a user."""
        pass
    
    @abstractmethod
    def get_shared_documents(self, user_id: int) -> List[Document]:
        """Get documents shared with a user."""
        pass
    
    @abstractmethod
    def revoke_share(self, document_id: int, user_id: int) -> bool:
        """Revoke document share."""
        pass
    
    @abstractmethod
    def get_document_shares(self, document_id: int) -> List[DocumentShare]:
        """Get all shares for a document."""
        pass
    
    @abstractmethod
    def update_document_metadata(self, document_id: int, metadata: Dict[str, Any]) -> Optional[Document]:
        """Update document metadata."""
        pass
    
    @abstractmethod
    def get_document_statistics(self) -> Dict[str, Any]:
        """Get document statistics."""
        pass
    
    @abstractmethod
    def get_expiring_documents(self, days: int = 30) -> List[Document]:
        """Get documents expiring in the next N days."""
        pass
    
    @abstractmethod
    def archive_document(self, document_id: int) -> bool:
        """Archive a document."""
        pass