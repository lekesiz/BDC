"""Document service module."""

from datetime import datetime, timedelta
from flask import current_app

from app.extensions import db
from app.services.notification_service import NotificationService


class DocumentService:
    """Document service for document operations."""
    
    @staticmethod
    def check_permission(document_id, user_id, permission_type='read'):
        """
        Check if a user has permission to access a document.
        
        Args:
            document_id (int): Document ID
            user_id (int): User ID
            permission_type (str): Permission type ('read', 'update', 'delete', 'share')
            
        Returns:
            bool: True if the user has permission, False otherwise
        """
        from app.models.document import Document
        from app.models.document_permission import DocumentPermission
        from app.models.user import User
        
        # Get the document
        document = Document.query.get(document_id)
        if not document:
            return False
        
        # Get the user
        user = User.query.get(user_id)
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
            from app.models.beneficiary import Beneficiary
            beneficiary = Beneficiary.query.get(document.beneficiary_id)
            if beneficiary and beneficiary.trainer_id == user_id:
                return True
        
        # Check specific permission
        permission_field = f'can_{permission_type}'
        
        # Check user-specific permission
        user_permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if user_permission:
            # Check if permission has expired
            if user_permission.expires_at and user_permission.expires_at < datetime.utcnow():
                return False
                
            return getattr(user_permission, permission_field, False)
        
        # Check role-based permission
        role_permission = DocumentPermission.query.filter_by(
            document_id=document_id,
            role=user.role,
            is_active=True
        ).first()
        
        if role_permission:
            # Check if permission has expired
            if role_permission.expires_at and role_permission.expires_at < datetime.utcnow():
                return False
                
            return getattr(role_permission, permission_field, False)
        
        return False
    
    @staticmethod
    def can_access_document(user, document):
        """Check if a user can access (view) a document."""
        # Owner can always access
        if document.upload_by == user.id:
            return True
        
        # Super admin can access all
        if user.role == 'super_admin':
            return True
        
        # Tenant admin can access documents in their tenant
        if user.role == 'tenant_admin' and document.tenant_id:
            if user.tenants and document.tenant_id == user.tenants[0].id:
                return True
        
        # Check beneficiary access
        if document.beneficiary_id:
            from app.models.beneficiary import Beneficiary
            beneficiary = Beneficiary.query.get(document.beneficiary_id)
            if beneficiary:
                # Beneficiary can access their own documents
                if beneficiary.user_id == user.id:
                    return True
                # Trainer can access their beneficiary's documents
                if user.role == 'trainer' and beneficiary.trainer_id == user.id:
                    return True
        
        # Check document permissions
        return DocumentService.check_permission(document.id, user.id, 'read')
    
    @staticmethod
    def can_modify_document(user, document):
        """Check if a user can modify (update) a document."""
        # Owner can always modify
        if document.upload_by == user.id:
            return True
        
        # Super admin can modify all
        if user.role == 'super_admin':
            return True
        
        # Check document permissions
        return DocumentService.check_permission(document.id, user.id, 'update')
    
    @staticmethod
    def can_delete_document(user, document):
        """Check if a user can delete a document."""
        # Owner can always delete
        if document.upload_by == user.id:
            return True
        
        # Super admin can delete all
        if user.role == 'super_admin':
            return True
        
        # Tenant admin can delete documents in their tenant
        if user.role == 'tenant_admin' and document.tenant_id:
            if user.tenants and document.tenant_id == user.tenants[0].id:
                return True
        
        # Check document permissions
        return DocumentService.check_permission(document.id, user.id, 'delete')
    
    @staticmethod
    def can_share_document(user, document):
        """Check if a user can share a document."""
        # Owner can always share
        if document.upload_by == user.id:
            return True
        
        # Super admin can share all
        if user.role == 'super_admin':
            return True
        
        # Check document permissions
        return DocumentService.check_permission(document.id, user.id, 'share')
    
    @staticmethod
    def grant_permission(document_id, user_id=None, role=None, permissions=None, expires_in=None):
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
        from app.models.document import Document
        from app.models.document_permission import DocumentPermission
        
        # Validate parameters
        if not user_id and not role:
            current_app.logger.error("Either user_id or role must be provided")
            return None
            
        # Get the document
        document = Document.query.get(document_id)
        if not document:
            current_app.logger.error(f"Document {document_id} not found")
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
            existing_permission = DocumentPermission.query.filter_by(
                document_id=document_id,
                user_id=user_id
            ).first()
        elif role:
            existing_permission = DocumentPermission.query.filter_by(
                document_id=document_id,
                role=role
            ).first()
            
        # Update existing permission or create new one
        try:
            if existing_permission:
                # Update existing permission
                existing_permission.can_read = permissions.get('read', existing_permission.can_read)
                existing_permission.can_update = permissions.get('update', existing_permission.can_update)
                existing_permission.can_delete = permissions.get('delete', existing_permission.can_delete)
                existing_permission.can_share = permissions.get('share', existing_permission.can_share)
                existing_permission.expires_at = expires_at
                existing_permission.is_active = True
                existing_permission.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                return existing_permission
            else:
                # Create new permission
                permission = DocumentPermission(
                    document_id=document_id,
                    user_id=user_id,
                    role=role,
                    can_read=permissions.get('read', True),
                    can_update=permissions.get('update', False),
                    can_delete=permissions.get('delete', False),
                    can_share=permissions.get('share', False),
                    expires_at=expires_at,
                    is_active=True
                )
                
                db.session.add(permission)
                db.session.commit()
                
                # Send notification to user if user-specific permission
                if user_id:
                    NotificationService.create_notification(
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
            current_app.logger.error(f"Error granting permission: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def revoke_permission(document_id, user_id=None, role=None):
        """
        Revoke permissions from a user or role for a document.
        
        Args:
            document_id (int): Document ID
            user_id (int): User ID (optional if role is provided)
            role (str): User role (optional if user_id is provided)
            
        Returns:
            bool: True if successful, False otherwise
        """
        from app.models.document_permission import DocumentPermission
        
        # Validate parameters
        if not user_id and not role:
            current_app.logger.error("Either user_id or role must be provided")
            return False
            
        try:
            # Find permission
            if user_id:
                permission = DocumentPermission.query.filter_by(
                    document_id=document_id,
                    user_id=user_id
                ).first()
            else:
                permission = DocumentPermission.query.filter_by(
                    document_id=document_id,
                    role=role
                ).first()
                
            if not permission:
                return False
                
            # Revoke permission
            permission.is_active = False
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error revoking permission: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_document_permissions(document_id):
        """
        Get all permissions for a document.
        
        Args:
            document_id (int): Document ID
            
        Returns:
            list: List of permissions
        """
        from app.models.document_permission import DocumentPermission
        
        try:
            permissions = DocumentPermission.query.filter_by(
                document_id=document_id,
                is_active=True
            ).all()
            
            return [permission.to_dict() for permission in permissions]
            
        except Exception as e:
            current_app.logger.error(f"Error getting document permissions: {str(e)}")
            return []
    
    @staticmethod
    def get_user_document_permissions(user_id):
        """
        Get all documents a user has access to.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of documents with permissions
        """
        from app.models.document_permission import DocumentPermission
        from app.models.document import Document
        from app.models.user import User
        
        try:
            # Get user's role
            user = User.query.get(user_id)
            if not user:
                return []
                
            # Get documents the user has uploaded
            own_documents = Document.query.filter_by(
                upload_by=user_id
            ).all()
            
            # Get documents the user has explicit permissions for
            user_permissions = DocumentPermission.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            # Get documents the user has role-based permissions for
            role_permissions = DocumentPermission.query.filter_by(
                role=user.role,
                is_active=True
            ).all()
            
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
            for perm in user_permissions:
                if perm.has_expired():
                    continue
                    
                doc = Document.query.get(perm.document_id)
                if doc and doc.upload_by != user_id:  # Skip own documents
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
                    
            # Add documents with role-based permissions
            for perm in role_permissions:
                if perm.has_expired():
                    continue
                    
                doc = Document.query.get(perm.document_id)
                # Skip if document already added (own or explicit permission)
                if doc and doc.upload_by != user_id and not any(d['document']['id'] == doc.id for d in documents):
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
                    
            return documents
            
        except Exception as e:
            current_app.logger.error(f"Error getting user document permissions: {str(e)}")
            return []