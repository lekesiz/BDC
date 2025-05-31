"""Improved document service with dependency injection."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging
import os

from app.services.interfaces.document_service_interface import IDocumentService
from app.repositories.interfaces.document_repository_interface import IDocumentRepository
from app.extensions import db

logger = logging.getLogger(__name__)


class ImprovedDocumentService(IDocumentService):
    """Improved document service with dependency injection."""
    
    def __init__(self, document_repository: IDocumentRepository, db_session: Optional[Session] = None):
        """Initialize service with dependencies.
        
        Args:
            document_repository: Document repository implementation
            db_session: Database session (optional)
        """
        self.document_repository = document_repository
        self.db_session = db_session or db.session
    
    def create_document(self, title: str, file_path: str, file_type: str,
                       file_size: int, upload_by: int, document_type: str = 'general',
                       beneficiary_id: Optional[int] = None, 
                       evaluation_id: Optional[int] = None,
                       **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new document."""
        try:
            document_data = {
                'title': title,
                'file_path': file_path,
                'file_type': file_type,
                'file_size': file_size,
                'upload_by': upload_by,
                'document_type': document_type,
                'is_active': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            if beneficiary_id:
                document_data['beneficiary_id'] = beneficiary_id
            if evaluation_id:
                document_data['evaluation_id'] = evaluation_id
            
            # Add any additional kwargs
            document_data.update(kwargs)
            
            document = self.document_repository.create(**document_data)
            self.db_session.commit()
            
            logger.info(f"Created document {document.id}: {title}")
            return document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document)
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create document: {str(e)}")
            return None
    
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            document = self.document_repository.find_by_id(document_id)
            if document:
                return document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document)
            return None
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {str(e)}")
            return None
    
    def get_documents_by_uploader(self, uploader_id: int) -> List[Dict[str, Any]]:
        """Get documents by uploader."""
        try:
            documents = self.document_repository.find_by_uploader_id(uploader_id)
            return [document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document) 
                   for document in documents]
        except Exception as e:
            logger.error(f"Failed to get documents for uploader {uploader_id}: {str(e)}")
            return []
    
    def get_documents_by_beneficiary(self, beneficiary_id: int) -> List[Dict[str, Any]]:
        """Get documents for a beneficiary."""
        try:
            documents = self.document_repository.find_by_beneficiary_id(beneficiary_id)
            return [document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document) 
                   for document in documents]
        except Exception as e:
            logger.error(f"Failed to get documents for beneficiary {beneficiary_id}: {str(e)}")
            return []
    
    def get_documents_by_evaluation(self, evaluation_id: int) -> List[Dict[str, Any]]:
        """Get documents for an evaluation."""
        try:
            documents = self.document_repository.find_by_evaluation_id(evaluation_id)
            return [document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document) 
                   for document in documents]
        except Exception as e:
            logger.error(f"Failed to get documents for evaluation {evaluation_id}: {str(e)}")
            return []
    
    def get_documents_by_type(self, document_type: str) -> List[Dict[str, Any]]:
        """Get documents by type."""
        try:
            documents = self.document_repository.find_by_type(document_type)
            return [document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document) 
                   for document in documents]
        except Exception as e:
            logger.error(f"Failed to get documents by type {document_type}: {str(e)}")
            return []
    
    def get_all_documents(self, limit: Optional[int] = None, 
                         offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all documents."""
        try:
            documents = self.document_repository.find_all(limit=limit, offset=offset)
            return [document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document) 
                   for document in documents]
        except Exception as e:
            logger.error(f"Failed to get all documents: {str(e)}")
            return []
    
    def update_document(self, document_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update document."""
        try:
            document = self.document_repository.update(document_id, **kwargs)
            if document:
                self.db_session.commit()
                logger.info(f"Updated document {document_id}")
                return document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document)
            return None
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            return None
    
    def delete_document(self, document_id: int, remove_file: bool = True) -> bool:
        """Delete document."""
        try:
            document = self.document_repository.find_by_id(document_id)
            if not document:
                return False
            
            # Remove file from filesystem if requested
            if remove_file and hasattr(document, 'file_path'):
                try:
                    if os.path.exists(document.file_path):
                        os.remove(document.file_path)
                        logger.info(f"Removed file: {document.file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove file {document.file_path}: {str(e)}")
            
            success = self.document_repository.delete(document_id)
            if success:
                self.db_session.commit()
                logger.info(f"Deleted document {document_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return False
    
    def deactivate_document(self, document_id: int) -> bool:
        """Deactivate document (soft delete)."""
        try:
            document = self.document_repository.update(document_id, is_active=False)
            if document:
                self.db_session.commit()
                logger.info(f"Deactivated document {document_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to deactivate document {document_id}: {str(e)}")
            return False
    
    def reactivate_document(self, document_id: int) -> bool:
        """Reactivate document."""
        try:
            document = self.document_repository.update(document_id, is_active=True)
            if document:
                self.db_session.commit()
                logger.info(f"Reactivated document {document_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to reactivate document {document_id}: {str(e)}")
            return False
    
    def search_documents(self, query: str, document_type: Optional[str] = None,
                        uploader_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search documents by title and description."""
        try:
            documents = self.document_repository.search(query, document_type, uploader_id)
            return [document.to_dict() if hasattr(document, 'to_dict') else self._serialize_document(document) 
                   for document in documents]
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            return []
    
    def get_document_statistics(self, uploader_id: Optional[int] = None) -> Dict[str, Any]:
        """Get document statistics."""
        try:
            return self.document_repository.get_statistics(uploader_id)
        except Exception as e:
            logger.error(f"Failed to get document statistics: {str(e)}")
            return {}
    
    def check_permission(self, document_id: int, user_id: int, permission_type: str = 'read') -> bool:
        """Check if a user has permission to access a document."""
        try:
            document = self.document_repository.find_by_id(document_id)
            if not document:
                return False
            
            # Basic permission check: owner has all permissions
            if getattr(document, 'upload_by', None) == user_id:
                return True
            
            # TODO: Implement more sophisticated permission checking with DocumentPermission model
            # For now, allow read access to all active documents
            if permission_type == 'read' and getattr(document, 'is_active', True):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to check permission for document {document_id}: {str(e)}")
            return False
    
    def grant_permission(self, document_id: int, user_id: Optional[int] = None, 
                        role: Optional[str] = None, permissions: Optional[Dict[str, bool]] = None,
                        expires_in: Optional[int] = None) -> Optional[Any]:
        """Grant permissions to a user or role for a document."""
        try:
            # TODO: Implement DocumentPermission model integration
            # For now, just return a mock permission object
            logger.info(f"Would grant permissions to document {document_id} for user {user_id} or role {role}")
            return {
                'id': 1,
                'document_id': document_id,
                'user_id': user_id,
                'role': role,
                'permissions': permissions or {'read': True},
                'expires_in': expires_in
            }
        except Exception as e:
            logger.error(f"Failed to grant permission for document {document_id}: {str(e)}")
            return None
    
    def revoke_permission(self, document_id: int, user_id: Optional[int] = None, 
                         role: Optional[str] = None) -> bool:
        """Revoke permissions from a user or role for a document."""
        try:
            # TODO: Implement DocumentPermission model integration
            logger.info(f"Would revoke permissions from document {document_id} for user {user_id} or role {role}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke permission for document {document_id}: {str(e)}")
            return False
    
    def get_document_permissions(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all permissions for a document."""
        try:
            # TODO: Implement DocumentPermission model integration
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get permissions for document {document_id}: {str(e)}")
            return []
    
    def get_user_document_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all documents a user has access to."""
        try:
            # Get documents uploaded by the user
            user_documents = self.document_repository.find_by_uploader_id(user_id)
            
            # TODO: Also get documents with explicit permissions
            permissions = []
            for doc in user_documents:
                permissions.append({
                    'document_id': doc.id,
                    'document_title': getattr(doc, 'title', ''),
                    'permissions': {'read': True, 'update': True, 'delete': True, 'share': True},
                    'permission_type': 'owner'
                })
            
            return permissions
        except Exception as e:
            logger.error(f"Failed to get document permissions for user {user_id}: {str(e)}")
            return []
    
    def _serialize_document(self, document) -> Dict[str, Any]:
        """Serialize document for API response."""
        return {
            'id': document.id,
            'title': getattr(document, 'title', ''),
            'description': getattr(document, 'description', ''),
            'file_path': getattr(document, 'file_path', ''),
            'file_type': getattr(document, 'file_type', ''),
            'file_size': getattr(document, 'file_size', 0),
            'document_type': getattr(document, 'document_type', 'general'),
            'is_active': getattr(document, 'is_active', True),
            'upload_by': getattr(document, 'upload_by', None),
            'beneficiary_id': getattr(document, 'beneficiary_id', None),
            'evaluation_id': getattr(document, 'evaluation_id', None),
            'created_at': getattr(document, 'created_at', datetime.now()).isoformat(),
            'updated_at': getattr(document, 'updated_at', datetime.now()).isoformat()
        }