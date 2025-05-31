"""Document repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.repositories.interfaces.base_repository_interface import IBaseRepository


class IDocumentRepository(IBaseRepository, ABC):
    """Interface for document repository operations."""
    
    @abstractmethod
    def find_by_uploader_id(self, uploader_id: int) -> List[Any]:
        """Find documents by uploader ID.
        
        Args:
            uploader_id: Uploader ID
            
        Returns:
            List of document instances
        """
        pass
    
    @abstractmethod
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Any]:
        """Find documents by beneficiary ID.
        
        Args:
            beneficiary_id: Beneficiary ID
            
        Returns:
            List of document instances
        """
        pass
    
    @abstractmethod
    def find_by_evaluation_id(self, evaluation_id: int) -> List[Any]:
        """Find documents by evaluation ID.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            List of document instances
        """
        pass
    
    @abstractmethod
    def find_by_type(self, document_type: str) -> List[Any]:
        """Find documents by type.
        
        Args:
            document_type: Document type
            
        Returns:
            List of document instances
        """
        pass
    
    @abstractmethod
    def find_active_documents(self) -> List[Any]:
        """Find all active documents.
        
        Returns:
            List of active document instances
        """
        pass
    
    @abstractmethod
    def search(self, query: str, document_type: Optional[str] = None,
              uploader_id: Optional[int] = None) -> List[Any]:
        """Search documents by title and description.
        
        Args:
            query: Search query
            document_type: Optional document type filter
            uploader_id: Optional uploader ID filter
            
        Returns:
            List of matching document instances
        """
        pass
    
    @abstractmethod
    def get_statistics(self, uploader_id: Optional[int] = None) -> Dict[str, Any]:
        """Get document statistics.
        
        Args:
            uploader_id: Optional uploader ID filter
            
        Returns:
            Dictionary with document statistics
        """
        pass