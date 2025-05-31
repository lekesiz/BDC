"""Document service interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class IDocumentService(ABC):
    """Interface for document service."""
    
    @abstractmethod
    def check_permission(self, document_id: int, user_id: int, permission_type: str = 'read') -> bool:
        """
        Check if a user has permission to access a document.
        
        Args:
            document_id (int): Document ID
            user_id (int): User ID
            permission_type (str): Permission type ('read', 'update', 'delete', 'share')
            
        Returns:
            bool: True if the user has permission, False otherwise
        """
        pass
    
    @abstractmethod
    def grant_permission(
        self, 
        document_id: int, 
        user_id: Optional[int] = None, 
        role: Optional[str] = None, 
        permissions: Optional[Dict[str, bool]] = None, 
        expires_in: Optional[int] = None
    ) -> Any:
        """
        Grant permissions to a user or role for a document.
        
        Args:
            document_id (int): Document ID
            user_id (int): User ID (optional if role is provided)
            role (str): User role (optional if user_id is provided)
            permissions (dict): Dictionary of permissions (e.g., {'read': True, 'update': True})
            expires_in (int): Number of days until the permission expires (optional)
            
        Returns:
            DocumentPermission: The created permission or None if creation fails
        """
        pass
    
    @abstractmethod
    def revoke_permission(self, document_id: int, user_id: Optional[int] = None, role: Optional[str] = None) -> bool:
        """
        Revoke permissions from a user or role for a document.
        
        Args:
            document_id (int): Document ID
            user_id (int): User ID (optional if role is provided)
            role (str): User role (optional if user_id is provided)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_document_permissions(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get all permissions for a document.
        
        Args:
            document_id (int): Document ID
            
        Returns:
            list: List of permissions
        """
        pass
    
    @abstractmethod
    def get_user_document_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all documents a user has access to.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of documents with permissions
        """
        pass