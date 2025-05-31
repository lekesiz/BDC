"""
Tests for the refactored Document API endpoints.
"""

import pytest
from unittest.mock import Mock, patch
import json
from io import BytesIO

from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.models.user import User


@pytest.fixture
def app(app):
    """Configure app for testing."""
    from app.api.documents_refactored import documents_refactored_bp
    app.register_blueprint(documents_refactored_bp, url_prefix='/api/v2')
    return app


@pytest.fixture
def auth_headers(app):
    """Create authentication headers for API requests."""
    with app.test_client() as client:
        response = client.post('/api/v2/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        token = json.loads(response.data)['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def mock_container():
    """Mock the DI container."""
    container = Mock()
    
    # Mock services
    container.resolve = Mock(side_effect=lambda service_name: {
        'document_service': Mock(),
        'user_repository': Mock(),
        'document_repository': Mock(),
        'beneficiary_repository': Mock()
    }.get(service_name))
    
    return container


class TestDocumentEndpoints:
    """Test document API endpoints."""
    
    @patch('app.api.documents_refactored.get_container')
    def test_get_documents_success(self, mock_get_container, client, auth_headers, mock_container):
        """Test getting documents successfully."""
        mock_get_container.return_value = mock_container
        
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'trainer'
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        # Mock documents
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.title = "Test Document"
        mock_doc.document_type = "general"
        mock_doc.is_active = True
        mock_doc.created_at = Mock()
        mock_doc.to_dict.return_value = {
            'id': 1,
            'title': 'Test Document',
            'document_type': 'general'
        }
        
        mock_container.resolve('beneficiary_repository').find_by_trainer_id.return_value = []
        mock_container.resolve('document_repository').find_by_beneficiary_id.return_value = []
        
        response = client.get('/api/v2/documents', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'documents' in data
        assert 'total' in data
        assert 'pages' in data
    
    @patch('app.api.documents_refactored.get_container')
    def test_get_documents_with_filters(self, mock_get_container, client, auth_headers, mock_container):
        """Test getting documents with filters."""
        mock_get_container.return_value = mock_container
        
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'admin'
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        mock_doc = Mock()
        mock_doc.document_type = "report"
        mock_doc.title = "Monthly Report"
        mock_doc.is_active = True
        mock_doc.created_at = Mock()
        mock_doc.to_dict.return_value = {
            'id': 1,
            'title': 'Monthly Report',
            'document_type': 'report'
        }
        
        mock_container.resolve('document_repository').find_all.return_value = [mock_doc]
        
        response = client.get('/api/v2/documents?type=report&search=monthly', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['documents']) == 1
    
    @patch('app.api.documents_refactored.get_container')
    def test_check_document_permission(self, mock_get_container, client, auth_headers, mock_container):
        """Test checking document permission."""
        mock_get_container.return_value = mock_container
        
        mock_container.resolve('document_service').check_permission.return_value = True
        
        response = client.get('/api/v2/documents/1/check-permission?type=read', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['has_permission'] is True
        assert data['permission_type'] == 'read'
    
    @patch('app.api.documents_refactored.get_container')
    def test_get_document_permissions(self, mock_get_container, client, auth_headers, mock_container):
        """Test getting document permissions."""
        mock_get_container.return_value = mock_container
        
        # Mock user and document
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'trainer'
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        mock_doc = Mock()
        mock_doc.upload_by = 1
        mock_container.resolve('document_repository').find_by_id.return_value = mock_doc
        
        # Mock permissions
        mock_permissions = [
            {'id': 1, 'user_id': 2, 'can_read': True},
            {'id': 2, 'role': 'trainer', 'can_read': True}
        ]
        mock_container.resolve('document_service').get_document_permissions.return_value = mock_permissions
        
        response = client.get('/api/v2/documents/1/permissions', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['document_id'] == 1
        assert len(data['permissions']) == 2
    
    @patch('app.api.documents_refactored.get_container')
    def test_grant_document_permission(self, mock_get_container, client, auth_headers, mock_container):
        """Test granting document permission."""
        mock_get_container.return_value = mock_container
        
        # Mock user and document
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'admin'
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        mock_doc = Mock()
        mock_doc.upload_by = 1
        mock_container.resolve('document_repository').find_by_id.return_value = mock_doc
        
        # Mock permission
        mock_permission = Mock()
        mock_permission.to_dict.return_value = {
            'id': 1,
            'user_id': 2,
            'can_read': True,
            'can_update': False
        }
        mock_container.resolve('document_service').grant_permission.return_value = mock_permission
        
        request_data = {
            'user_id': 2,
            'permissions': {'read': True, 'update': False}
        }
        
        response = client.post('/api/v2/documents/1/permissions', 
                             json=request_data,
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Permission granted successfully'
        assert 'permission' in data
    
    @patch('app.api.documents_refactored.get_container')
    def test_revoke_document_permission(self, mock_get_container, client, auth_headers, mock_container):
        """Test revoking document permission."""
        mock_get_container.return_value = mock_container
        
        # Mock user and document
        mock_user = Mock()
        mock_user.id = 1
        mock_user.role = 'admin'
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        mock_doc = Mock()
        mock_doc.upload_by = 1
        mock_container.resolve('document_repository').find_by_id.return_value = mock_doc
        
        mock_container.resolve('document_service').revoke_permission.return_value = True
        
        request_data = {'user_id': 2}
        
        response = client.delete('/api/v2/documents/1/permissions', 
                               json=request_data,
                               headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Permission revoked successfully'
    
    @patch('app.api.documents_refactored.get_container')
    def test_get_user_documents(self, mock_get_container, client, auth_headers, mock_container):
        """Test getting user documents."""
        mock_get_container.return_value = mock_container
        
        mock_documents = [
            {
                'document': {'id': 1, 'title': 'My Document'},
                'permissions': {'read': True, 'update': True},
                'owner': True
            },
            {
                'document': {'id': 2, 'title': 'Shared Document'},
                'permissions': {'read': True, 'update': False},
                'owner': False
            }
        ]
        mock_container.resolve('document_service').get_user_document_permissions.return_value = mock_documents
        
        response = client.get('/api/v2/user/documents', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 2
        assert len(data['documents']) == 2
    
    @patch('app.api.documents_refactored.get_container')
    def test_upload_document(self, mock_get_container, client, auth_headers, mock_container):
        """Test uploading a document."""
        mock_get_container.return_value = mock_container
        
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        # Mock created document
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.file_path = '/uploads/documents/general/test.pdf'
        mock_container.resolve('document_repository').create.return_value = mock_doc
        
        # Create test file
        data = {
            'file': (BytesIO(b'test content'), 'test.pdf'),
            'type': 'general',
            'title': 'Test Document',
            'description': 'Test description'
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'), \
             patch('werkzeug.datastructures.FileStorage.save'):
            
            response = client.post('/api/v2/documents/upload',
                                 data=data,
                                 headers=auth_headers,
                                 content_type='multipart/form-data')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Document uploaded successfully'
        assert data['document_id'] == 1


class TestErrorCases:
    """Test error cases for document endpoints."""
    
    @patch('app.api.documents_refactored.get_container')
    def test_get_documents_user_not_found(self, mock_get_container, client, auth_headers, mock_container):
        """Test getting documents when user not found."""
        mock_get_container.return_value = mock_container
        mock_container.resolve('user_repository').find_by_id.return_value = None
        
        response = client.get('/api/v2/documents', headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'User not found'
    
    @patch('app.api.documents_refactored.get_container')
    def test_grant_permission_no_user_or_role(self, mock_get_container, client, auth_headers, mock_container):
        """Test granting permission without user_id or role."""
        mock_get_container.return_value = mock_container
        
        # Mock user and document
        mock_user = Mock()
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        mock_doc = Mock()
        mock_container.resolve('document_repository').find_by_id.return_value = mock_doc
        
        request_data = {'permissions': {'read': True}}
        
        response = client.post('/api/v2/documents/1/permissions',
                             json=request_data,
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Either user_id or role must be provided'
    
    @patch('app.api.documents_refactored.get_container')
    def test_upload_document_no_file(self, mock_get_container, client, auth_headers, mock_container):
        """Test uploading document without file."""
        mock_get_container.return_value = mock_container
        
        mock_user = Mock()
        mock_container.resolve('user_repository').find_by_id.return_value = mock_user
        
        response = client.post('/api/v2/documents/upload',
                             data={},
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No file provided'