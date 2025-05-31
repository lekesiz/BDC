"""
Tests for the refactored DocumentService.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

from app.services.document_service_refactored import DocumentService
from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.models.user import User
from app.models.beneficiary import Beneficiary


@pytest.fixture
def mock_repositories():
    """Create mock repositories for testing."""
    return {
        'document_repository': Mock(),
        'user_repository': Mock(),
        'beneficiary_repository': Mock(),
        'notification_service': Mock()
    }


@pytest.fixture
def document_service(mock_repositories):
    """Create DocumentService instance with mocked dependencies."""
    return DocumentService(
        mock_repositories['document_repository'],
        mock_repositories['user_repository'],
        mock_repositories['beneficiary_repository'],
        mock_repositories['notification_service']
    )


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    doc = Document()
    doc.id = 1
    doc.title = "Test Document"
    doc.upload_by = 1
    doc.beneficiary_id = 1
    doc.is_active = True
    return doc


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User()
    user.id = 1
    user.role = 'trainer'
    return user


@pytest.fixture
def sample_beneficiary():
    """Create a sample beneficiary for testing."""
    beneficiary = Beneficiary()
    beneficiary.id = 1
    beneficiary.trainer_id = 1
    return beneficiary


class TestDocumentServiceChekPermission:
    """Test check_permission method."""
    
    def test_check_permission_document_not_found(self, document_service, mock_repositories):
        """Test permission check when document doesn't exist."""
        mock_repositories['document_repository'].find_by_id.return_value = None
        
        result = document_service.check_permission(1, 1, 'read')
        
        assert result is False
    
    def test_check_permission_user_not_found(self, document_service, mock_repositories, sample_document):
        """Test permission check when user doesn't exist."""
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = None
        
        result = document_service.check_permission(1, 1, 'read')
        
        assert result is False
    
    def test_check_permission_document_owner(self, document_service, mock_repositories, sample_document, sample_user):
        """Test permission check for document owner."""
        sample_document.upload_by = sample_user.id
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        
        result = document_service.check_permission(1, 1, 'delete')
        
        assert result is True
    
    def test_check_permission_super_admin(self, document_service, mock_repositories, sample_document, sample_user):
        """Test permission check for super admin."""
        sample_user.role = 'super_admin'
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        
        result = document_service.check_permission(1, 1, 'delete')
        
        assert result is True
    
    def test_check_permission_trainer_assigned_beneficiary(self, document_service, mock_repositories, 
                                                         sample_document, sample_user, sample_beneficiary):
        """Test permission check for trainer assigned to beneficiary."""
        sample_user.role = 'trainer'
        sample_document.beneficiary_id = sample_beneficiary.id
        sample_beneficiary.trainer_id = sample_user.id
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        mock_repositories['beneficiary_repository'].find_by_id.return_value = sample_beneficiary
        
        result = document_service.check_permission(1, 1, 'read')
        
        assert result is True
    
    def test_check_permission_user_specific_permission(self, document_service, mock_repositories,
                                                      sample_document, sample_user):
        """Test permission check with user-specific permission."""
        permission = DocumentPermission()
        permission.can_read = True
        permission.can_update = False
        permission.is_active = True
        permission.expires_at = None
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = permission
        
        assert document_service.check_permission(1, 1, 'read') is True
        assert document_service.check_permission(1, 1, 'update') is False
    
    def test_check_permission_expired_permission(self, document_service, mock_repositories,
                                               sample_document, sample_user):
        """Test permission check with expired permission."""
        permission = DocumentPermission()
        permission.can_read = True
        permission.is_active = True
        permission.expires_at = datetime.utcnow() - timedelta(days=1)
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = permission
        
        result = document_service.check_permission(1, 1, 'read')
        
        assert result is False
    
    def test_check_permission_role_based_permission(self, document_service, mock_repositories,
                                                  sample_document, sample_user):
        """Test permission check with role-based permission."""
        permission = DocumentPermission()
        permission.can_read = True
        permission.is_active = True
        permission.expires_at = None
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = None
        mock_repositories['document_repository'].find_permission_by_document_and_role.return_value = permission
        
        result = document_service.check_permission(1, 1, 'read')
        
        assert result is True


class TestDocumentServiceGrantPermission:
    """Test grant_permission method."""
    
    def test_grant_permission_invalid_params(self, document_service):
        """Test grant permission with invalid parameters."""
        result = document_service.grant_permission(1)
        
        assert result is None
    
    def test_grant_permission_document_not_found(self, document_service, mock_repositories):
        """Test grant permission when document doesn't exist."""
        mock_repositories['document_repository'].find_by_id.return_value = None
        
        result = document_service.grant_permission(1, user_id=1)
        
        assert result is None
    
    def test_grant_permission_create_new_user_permission(self, document_service, mock_repositories,
                                                       sample_document):
        """Test creating new user permission."""
        new_permission = DocumentPermission()
        new_permission.id = 1
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = None
        mock_repositories['document_repository'].create_permission.return_value = new_permission
        
        result = document_service.grant_permission(
            document_id=1,
            user_id=2,
            permissions={'read': True, 'update': True}
        )
        
        assert result is not None
        assert result.id == 1
        mock_repositories['notification_service'].create_notification.assert_called_once()
    
    def test_grant_permission_update_existing_permission(self, document_service, mock_repositories,
                                                      sample_document):
        """Test updating existing permission."""
        existing_permission = DocumentPermission()
        existing_permission.can_read = True
        existing_permission.can_update = False
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = existing_permission
        mock_repositories['document_repository'].update_permission.return_value = existing_permission
        
        result = document_service.grant_permission(
            document_id=1,
            user_id=2,
            permissions={'update': True}
        )
        
        assert result.can_update is True
        mock_repositories['notification_service'].create_notification.assert_not_called()
    
    def test_grant_permission_with_expiry(self, document_service, mock_repositories,
                                        sample_document):
        """Test granting permission with expiry date."""
        new_permission = DocumentPermission()
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = None
        mock_repositories['document_repository'].create_permission.return_value = new_permission
        
        result = document_service.grant_permission(
            document_id=1,
            user_id=2,
            expires_in=7
        )
        
        create_call_args = mock_repositories['document_repository'].create_permission.call_args[1]
        assert create_call_args['expires_at'] is not None
    
    def test_grant_permission_role_based(self, document_service, mock_repositories,
                                       sample_document):
        """Test granting role-based permission."""
        new_permission = DocumentPermission()
        
        mock_repositories['document_repository'].find_by_id.return_value = sample_document
        mock_repositories['document_repository'].find_permission_by_document_and_role.return_value = None
        mock_repositories['document_repository'].create_permission.return_value = new_permission
        
        result = document_service.grant_permission(
            document_id=1,
            role='trainer',
            permissions={'read': True}
        )
        
        assert result is not None
        create_call_args = mock_repositories['document_repository'].create_permission.call_args[1]
        assert create_call_args['role'] == 'trainer'
        assert create_call_args['user_id'] is None


class TestDocumentServiceRevokePermission:
    """Test revoke_permission method."""
    
    def test_revoke_permission_invalid_params(self, document_service):
        """Test revoke permission with invalid parameters."""
        result = document_service.revoke_permission(1)
        
        assert result is False
    
    def test_revoke_permission_not_found(self, document_service, mock_repositories):
        """Test revoke permission when permission doesn't exist."""
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = None
        
        result = document_service.revoke_permission(1, user_id=1)
        
        assert result is False
    
    def test_revoke_permission_success(self, document_service, mock_repositories):
        """Test successful permission revocation."""
        permission = DocumentPermission()
        permission.is_active = True
        
        mock_repositories['document_repository'].find_permission_by_document_and_user.return_value = permission
        mock_repositories['document_repository'].update_permission.return_value = permission
        
        result = document_service.revoke_permission(1, user_id=1)
        
        assert result is True
        assert permission.is_active is False
    
    def test_revoke_permission_role_based(self, document_service, mock_repositories):
        """Test revoking role-based permission."""
        permission = DocumentPermission()
        permission.is_active = True
        
        mock_repositories['document_repository'].find_permission_by_document_and_role.return_value = permission
        mock_repositories['document_repository'].update_permission.return_value = permission
        
        result = document_service.revoke_permission(1, role='trainer')
        
        assert result is True
        assert permission.is_active is False


class TestDocumentServiceGetPermissions:
    """Test get_document_permissions and get_user_document_permissions methods."""
    
    def test_get_document_permissions(self, document_service, mock_repositories):
        """Test getting all permissions for a document."""
        permission1 = Mock()
        permission1.to_dict.return_value = {'id': 1, 'can_read': True}
        permission2 = Mock()
        permission2.to_dict.return_value = {'id': 2, 'can_read': True}
        
        mock_repositories['document_repository'].find_permissions_by_document.return_value = [
            permission1, permission2
        ]
        
        result = document_service.get_document_permissions(1)
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
    
    def test_get_user_document_permissions_user_not_found(self, document_service, mock_repositories):
        """Test getting user documents when user doesn't exist."""
        mock_repositories['user_repository'].find_by_id.return_value = None
        
        result = document_service.get_user_document_permissions(1)
        
        assert result == []
    
    def test_get_user_document_permissions_owned_documents(self, document_service, mock_repositories,
                                                         sample_user):
        """Test getting user's owned documents."""
        document = Mock()
        document.id = 1
        document.to_dict.return_value = {'id': 1, 'title': 'My Document'}
        
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        mock_repositories['document_repository'].find_by_uploader_id.return_value = [document]
        mock_repositories['document_repository'].find_permissions_by_user.return_value = []
        mock_repositories['document_repository'].find_permissions_by_document.return_value = []
        
        result = document_service.get_user_document_permissions(1)
        
        assert len(result) == 1
        assert result[0]['document']['id'] == 1
        assert result[0]['owner'] is True
        assert result[0]['permissions']['read'] is True
        assert result[0]['permissions']['delete'] is True
    
    def test_get_user_document_permissions_with_explicit_permissions(self, document_service, mock_repositories,
                                                                   sample_user):
        """Test getting documents with explicit permissions."""
        document = Mock()
        document.id = 2
        document.to_dict.return_value = {'id': 2, 'title': 'Shared Document'}
        
        permission = Mock()
        permission.document_id = 2
        permission.can_read = True
        permission.can_update = False
        permission.can_delete = False
        permission.can_share = False
        permission.expires_at = None
        permission.has_expired.return_value = False
        
        mock_repositories['user_repository'].find_by_id.return_value = sample_user
        mock_repositories['document_repository'].find_by_uploader_id.return_value = []
        mock_repositories['document_repository'].find_permissions_by_user.return_value = [permission]
        mock_repositories['document_repository'].find_by_id.return_value = document
        mock_repositories['document_repository'].find_permissions_by_document.return_value = []
        
        result = document_service.get_user_document_permissions(1)
        
        assert len(result) == 1
        assert result[0]['document']['id'] == 2
        assert result[0]['owner'] is False
        assert result[0]['permissions']['read'] is True
        assert result[0]['permissions']['update'] is False