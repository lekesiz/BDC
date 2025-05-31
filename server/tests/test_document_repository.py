"""
Tests for DocumentRepository implementation.
"""

import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock, MagicMock, patch

from app.repositories.document_repository import DocumentRepository
from app.models.document import Document
from app.models.document_permission import DocumentPermission


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock(spec=Session)
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.delete = Mock()
    return session


@pytest.fixture
def document_repository(mock_db_session):
    """Create DocumentRepository instance with mocked session."""
    return DocumentRepository(mock_db_session)


@pytest.fixture
def sample_document():
    """Create a sample document."""
    doc = Document()
    doc.id = 1
    doc.title = "Test Document"
    doc.upload_by = 1
    doc.beneficiary_id = 1
    return doc


@pytest.fixture
def sample_permission():
    """Create a sample document permission."""
    perm = DocumentPermission()
    perm.id = 1
    perm.document_id = 1
    perm.user_id = 1
    perm.is_active = True
    return perm


class TestDocumentRepository:
    """Test DocumentRepository methods."""
    
    def test_find_by_id(self, document_repository, mock_db_session, sample_document):
        """Test finding document by ID."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_document
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_by_id(1)
        
        assert result == sample_document
        mock_db_session.query.assert_called_with(Document)
        mock_query.filter.assert_called()
    
    def test_find_by_beneficiary_id(self, document_repository, mock_db_session, sample_document):
        """Test finding documents by beneficiary ID."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_document]
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_by_beneficiary_id(1)
        
        assert len(result) == 1
        assert result[0] == sample_document
    
    def test_find_by_uploader_id(self, document_repository, mock_db_session, sample_document):
        """Test finding documents by uploader ID."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_document]
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_by_uploader_id(1)
        
        assert len(result) == 1
        assert result[0] == sample_document
    
    def test_find_all_with_pagination(self, document_repository, mock_db_session, sample_document):
        """Test finding all documents with pagination."""
        mock_query = Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_document]
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_all(limit=10, offset=0)
        
        assert len(result) == 1
        assert result[0] == sample_document
        mock_query.limit.assert_called_with(10)
        mock_query.offset.assert_called_with(0)
    
    def test_create_document(self, document_repository, mock_db_session):
        """Test creating a new document."""
        document_data = {
            'title': 'New Document',
            'upload_by': 1,
            'file_path': '/path/to/file',
            'file_type': 'pdf',
            'file_size': 1024
        }
        
        result = document_repository.create(**document_data)
        
        assert isinstance(result, Document)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_update_document(self, document_repository, mock_db_session, sample_document):
        """Test updating a document."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_document
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.update(1, title='Updated Title')
        
        assert result == sample_document
        assert sample_document.title == 'Updated Title'
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_update_document_not_found(self, document_repository, mock_db_session):
        """Test updating non-existent document."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.update(999, title='Updated Title')
        
        assert result is None
        mock_db_session.commit.assert_not_called()
    
    def test_delete_document(self, document_repository, mock_db_session, sample_document):
        """Test deleting a document."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_document
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.delete(1)
        
        assert result is True
        mock_db_session.delete.assert_called_with(sample_document)
        mock_db_session.commit.assert_called_once()
    
    def test_delete_document_not_found(self, document_repository, mock_db_session):
        """Test deleting non-existent document."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.delete(999)
        
        assert result is False
        mock_db_session.delete.assert_not_called()
    
    def test_save_document(self, document_repository, mock_db_session, sample_document):
        """Test saving a document instance."""
        result = document_repository.save(sample_document)
        
        assert result == sample_document
        mock_db_session.add.assert_called_with(sample_document)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_with(sample_document)


class TestDocumentPermissionMethods:
    """Test document permission related methods."""
    
    def test_create_permission(self, document_repository, mock_db_session):
        """Test creating a new permission."""
        permission_data = {
            'document_id': 1,
            'user_id': 1,
            'can_read': True,
            'can_update': False
        }
        
        result = document_repository.create_permission(**permission_data)
        
        assert isinstance(result, DocumentPermission)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_find_permission_by_document_and_user(self, document_repository, mock_db_session, sample_permission):
        """Test finding permission by document and user."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_permission
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_permission_by_document_and_user(1, 1)
        
        assert result == sample_permission
        mock_db_session.query.assert_called_with(DocumentPermission)
    
    def test_find_permission_by_document_and_role(self, document_repository, mock_db_session, sample_permission):
        """Test finding permission by document and role."""
        sample_permission.role = 'trainer'
        sample_permission.user_id = None
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_permission
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_permission_by_document_and_role(1, 'trainer')
        
        assert result == sample_permission
    
    def test_find_permissions_by_document(self, document_repository, mock_db_session, sample_permission):
        """Test finding all permissions for a document."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_permission]
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_permissions_by_document(1, is_active=True)
        
        assert len(result) == 1
        assert result[0] == sample_permission
    
    def test_find_permissions_by_user(self, document_repository, mock_db_session, sample_permission):
        """Test finding all permissions for a user."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_permission]
        mock_db_session.query.return_value = mock_query
        
        result = document_repository.find_permissions_by_user(1, is_active=True)
        
        assert len(result) == 1
        assert result[0] == sample_permission
    
    def test_update_permission(self, document_repository, mock_db_session, sample_permission):
        """Test updating a permission."""
        result = document_repository.update_permission(sample_permission)
        
        assert result == sample_permission
        mock_db_session.add.assert_called_with(sample_permission)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_with(sample_permission)