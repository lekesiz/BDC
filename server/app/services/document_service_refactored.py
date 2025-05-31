"""Refactored Document Service implementation with dependency injection."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from flask import current_app

from app.services.interfaces.document_service_interface import IDocumentService
from app.services.interfaces.document_repository_interface import IDocumentRepository
from app.services.interfaces.user_repository_interface import IUserRepository
from app.services.interfaces.beneficiary_repository_interface import IBeneficiaryRepository
from app.services.interfaces.notification_service_interface import INotificationService
from app.models.document_permission import DocumentPermission
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentService(IDocumentService):
    """Document service implementation with dependency injection."""
    
    def __init__(
        self,
        document_repository: IDocumentRepository,
        user_repository: IUserRepository,
        beneficiary_repository: IBeneficiaryRepository,
        notification_service: INotificationService
    ):
        """
        Initialize DocumentService with injected dependencies.
        
        Args:
            document_repository: The document repository interface
            user_repository: The user repository interface
            beneficiary_repository: The beneficiary repository interface
            notification_service: The notification service interface
        """
        self.document_repository = document_repository
        self.user_repository = user_repository
        self.beneficiary_repository = beneficiary_repository
        self.notification_service = notification_service
    
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
        try:
            # Get the document
            document = self.document_repository.find_by_id(document_id)
            if not document:
                return False
            
            # Get the user
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False
            
            # Document owner has all permissions
            if document.upload_by == user_id:
                return True
            
            # Super admin has all permissions
            if user.role == 'super_admin':
                return True
                
            # Check if document is related to the user's beneficiary (for trainers)
            if user.role == 'trainer' and document.beneficiary_id:
                # Check if the user is the trainer for this beneficiary
                beneficiary = self.beneficiary_repository.find_by_id(document.beneficiary_id)
                if beneficiary and beneficiary.trainer_id == user_id:
                    return True
            
            # Check specific permission
            permission_field = f'can_{permission_type}'
            
            # Check user-specific permission
            user_permission = self.document_repository.find_permission_by_document_and_user(
                document_id, user_id
            )
            
            if user_permission and user_permission.is_active:
                # Check if permission has expired
                if user_permission.expires_at and user_permission.expires_at < datetime.utcnow():
                    return False
                    
                return getattr(user_permission, permission_field, False)
            
            # Check role-based permission
            role_permission = self.document_repository.find_permission_by_document_and_role(
                document_id, user.role
            )
            
            if role_permission and role_permission.is_active:
                # Check if permission has expired
                if role_permission.expires_at and role_permission.expires_at < datetime.utcnow():
                    return False
                    
                return getattr(role_permission, permission_field, False)
            
            return False
            
        except Exception as e:
            logger.exception(f"Error checking permission: {str(e)}")
            return False
    
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
        try:
            # Validate parameters
            if not user_id and not role:
                logger.error("Either user_id or role must be provided")
                return None
                
            # Get the document
            document = self.document_repository.find_by_id(document_id)
            if not document:
                logger.error(f"Document {document_id} not found")
                return None
                
            # Set default permissions
            if not permissions:
                permissions = {
                    'read': True,
                    'update': False,
                    'delete': False,
                    'share': False
                }
                
            # Calculate expiry date
            expires_at = None
            if expires_in:
                expires_at = datetime.utcnow() + timedelta(days=expires_in)
                
            # Check if permission already exists
            existing_permission = None
            
            if user_id:
                existing_permission = self.document_repository.find_permission_by_document_and_user(
                    document_id, user_id
                )
            elif role:
                existing_permission = self.document_repository.find_permission_by_document_and_role(
                    document_id, role
                )
                
            # Update existing permission or create new one
            if existing_permission:
                # Update existing permission
                existing_permission.can_read = permissions.get('read', existing_permission.can_read)
                existing_permission.can_update = permissions.get('update', existing_permission.can_update)
                existing_permission.can_delete = permissions.get('delete', existing_permission.can_delete)
                existing_permission.can_share = permissions.get('share', existing_permission.can_share)
                existing_permission.expires_at = expires_at
                existing_permission.is_active = True
                existing_permission.updated_at = datetime.utcnow()
                
                permission = self.document_repository.update_permission(existing_permission)
            else:
                # Create new permission
                permission_data = {
                    'document_id': document_id,
                    'user_id': user_id,
                    'role': role,
                    'can_read': permissions.get('read', True),
                    'can_update': permissions.get('update', False),
                    'can_delete': permissions.get('delete', False),
                    'can_share': permissions.get('share', False),
                    'expires_at': expires_at,
                    'is_active': True
                }
                
                permission = self.document_repository.create_permission(**permission_data)
                
                # Send notification to user if user-specific permission
                if user_id:
                    self.notification_service.create_notification(
                        user_id=user_id,
                        type='document_shared',
                        title='Document Shared With You',
                        message=f'You have been granted access to "{document.title}"',
                        data={
                            'document_id': document_id,
                            'document_title': document.title,
                            'permissions': permissions
                        },
                        related_id=document_id,
                        related_type='document',
                        sender_id=document.upload_by,
                        priority='normal',
                        send_email=True
                    )
            
            return permission
            
        except Exception as e:
            logger.exception(f"Error granting permission: {str(e)}")
            return None
    
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
        try:
            # Validate parameters
            if not user_id and not role:
                logger.error("Either user_id or role must be provided")
                return False
                
            # Find permission
            permission = None
            if user_id:
                permission = self.document_repository.find_permission_by_document_and_user(
                    document_id, user_id
                )
            else:
                permission = self.document_repository.find_permission_by_document_and_role(
                    document_id, role
                )
                
            if not permission:
                return False
                
            # Revoke permission
            permission.is_active = False
            self.document_repository.update_permission(permission)
            
            return True
            
        except Exception as e:
            logger.exception(f"Error revoking permission: {str(e)}")
            return False
    
    def get_document_permissions(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get all permissions for a document.
        
        Args:
            document_id (int): Document ID
            
        Returns:
            list: List of permissions
        """
        try:
            permissions = self.document_repository.find_permissions_by_document(
                document_id, is_active=True
            )
            
            return [permission.to_dict() for permission in permissions]
            
        except Exception as e:
            logger.exception(f"Error getting document permissions: {str(e)}")
            return []
    
    def get_user_document_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all documents a user has access to.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of documents with permissions
        """
        try:
            # Get user's role
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return []
                
            # Get documents the user has uploaded
            own_documents = self.document_repository.find_by_uploader_id(user_id)
            
            # Get documents the user has explicit permissions for
            user_permissions = self.document_repository.find_permissions_by_user(
                user_id, is_active=True
            )
            
            # Get documents the user has role-based permissions for
            role_permissions = self.document_repository.find_permission_by_document_and_role(
                user.role
            )
            
            # Combine all documents
            documents = []
            
            # Add own documents
            for doc in own_documents:
                documents.append({
                    'document': doc.to_dict(),
                    'permissions': {
                        'read': True,
                        'update': True,
                        'delete': True,
                        'share': True
                    },
                    'owner': True
                })
                
            # Add documents with explicit permissions
            document_ids_added = {doc.id for doc in own_documents}
            
            for perm in user_permissions:
                if perm.has_expired():
                    continue
                    
                doc = self.document_repository.find_by_id(perm.document_id)
                if doc and doc.id not in document_ids_added:
                    documents.append({
                        'document': doc.to_dict(),
                        'permissions': {
                            'read': perm.can_read,
                            'update': perm.can_update,
                            'delete': perm.can_delete,
                            'share': perm.can_share
                        },
                        'owner': False,
                        'expires_at': perm.expires_at.isoformat() if perm.expires_at else None
                    })
                    document_ids_added.add(doc.id)
            
            # Handle role-based permissions 
            if user.role:
                # Get all permissions for this role
                role_permissions = self.document_repository.find_permissions_by_document(None, is_active=True)
                role_permissions = [p for p in role_permissions if p.role == user.role]
                
                for perm in role_permissions:
                    if perm.has_expired():
                        continue
                        
                    doc = self.document_repository.find_by_id(perm.document_id)
                    if doc and doc.id not in document_ids_added:
                        documents.append({
                            'document': doc.to_dict(),
                            'permissions': {
                                'read': perm.can_read,
                                'update': perm.can_update,
                                'delete': perm.can_delete,
                                'share': perm.can_share
                            },
                            'owner': False,
                            'role_based': True,
                            'expires_at': perm.expires_at.isoformat() if perm.expires_at else None
                        })
                        document_ids_added.add(doc.id)
                    
            return documents
            
        except Exception as e:
            logger.exception(f"Error getting user document permissions: {str(e)}")
            return []