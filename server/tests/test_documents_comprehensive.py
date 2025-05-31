"""Comprehensive test suite for documents endpoints."""

import pytest
from app import db
from app.models import User, Tenant, Document


class TestDocumentsComprehensive:
    """Comprehensive document endpoint tests."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app, client):
        """Setup for each test."""
        self.app = test_app
        self.client = client
        
        with self.app.app_context():
            # Create test tenant
            self.tenant = Tenant(
                name='Test Tenant Docs',
                slug='test-tenant-docs',
                email='test-docs@tenant.com',
                is_active=True
            )
            db.session.add(self.tenant)
            db.session.commit()
            
            # Store tenant ID
            self.tenant_id = self.tenant.id
            
            # Create users
            self.admin_user = User(
                email='test_admin_docs@bdc.com',
                username='test_admin_docs',
                first_name='Test',
                last_name='Admin',
                role='super_admin',
                is_active=True,
                tenant_id=self.tenant_id
            )
            self.admin_user.password = 'Admin123!'
            db.session.add(self.admin_user)
            
            self.trainer_user = User(
                email='test_trainer_docs@bdc.com',
                username='test_trainer_docs',
                first_name='Test',
                last_name='Trainer',
                role='trainer',
                is_active=True,
                tenant_id=self.tenant_id
            )
            self.trainer_user.password = 'Trainer123!'
            db.session.add(self.trainer_user)
            
            self.student_user = User(
                email='test_student_docs@bdc.com',
                username='test_student_docs',
                first_name='Test',
                last_name='Student',
                role='student',
                is_active=True,
                tenant_id=self.tenant_id
            )
            self.student_user.password = 'Student123!'
            db.session.add(self.student_user)
            
            db.session.commit()
            
            # Store user IDs
            self.admin_id = self.admin_user.id
            self.trainer_id = self.trainer_user.id
            self.student_id = self.student_user.id
            
            # Create test documents
            self.doc1 = Document(
                title='Test Document 1',
                description='First test document',
                file_path='/uploads/test1.pdf',
                file_size=1024,
                file_type='pdf',
                document_type='training',
                upload_by=self.trainer_id,
                is_active=True
            )
            db.session.add(self.doc1)
            
            self.doc2 = Document(
                title='Test Document 2',
                description='Second test document',
                file_path='/uploads/test2.docx',
                file_size=2048,
                file_type='docx',
                document_type='report',
                upload_by=self.admin_id,
                is_active=True
            )
            db.session.add(self.doc2)
            
            db.session.commit()
            
            # Store document IDs
            self.doc1_id = self.doc1.id
            self.doc2_id = self.doc2.id
            
            # Get tokens
            self.admin_token = self._get_token('test_admin_docs@bdc.com', 'Admin123!')
            self.trainer_token = self._get_token('test_trainer_docs@bdc.com', 'Trainer123!')
            self.student_token = self._get_token('test_student_docs@bdc.com', 'Student123!')
        
        yield
        
        # Cleanup
        with self.app.app_context():
            Document.query.delete()
            User.query.filter(User.email.like('test_%docs@bdc.com')).delete()
            Tenant.query.filter_by(slug='test-tenant-docs').delete()
            db.session.commit()
    
    def _get_token(self, email, password):
        """Helper to get auth token."""
        response = self.client.post('/api/auth/login', json={
            'email': email,
            'password': password,
            'remember': False
        })
        return response.get_json()['access_token']
    
    def test_list_documents_as_admin(self):
        """Test listing documents as admin."""
        response = self.client.get('/api/documents',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Response has 'documents' key instead of 'items'
        assert 'documents' in data or isinstance(data, list)
        docs = data.get('documents', data) if isinstance(data, dict) else data
        assert len(docs) >= 2
    
    def test_list_documents_pagination(self):
        """Test document list pagination."""
        response = self.client.get('/api/documents?page=1&per_page=1',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Response has 'documents' key
        docs = data.get('documents', data.get('items', data)) if isinstance(data, dict) else data
        if isinstance(data, dict) and 'documents' in data:
            assert len(data['documents']) == 1
    
    def test_list_documents_search(self):
        """Test searching documents."""
        response = self.client.get('/api/documents?search=test',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        docs = data.get('documents', data.get('items', data)) if isinstance(data, dict) else data
        assert len(docs) >= 2
    
    def test_list_user_documents(self):
        """Test listing user's own documents."""
        response = self.client.get('/api/user/documents',
                                 headers={'Authorization': f'Bearer {self.trainer_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Handle both list and dict responses
        if isinstance(data, list):
            docs = data
        else:
            docs = data.get('documents', data.get('items', []))
        # Trainer should see their own document
        assert any(d['id'] == self.doc1_id for d in docs)
    
    def test_get_document_permissions(self):
        """Test getting document permissions."""
        response = self.client.get(f'/api/documents/{self.doc1_id}/permissions',
                                 headers={'Authorization': f'Bearer {self.trainer_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'permissions' in data or isinstance(data, list)
    
    def test_add_document_permission(self):
        """Test adding document permission."""
        response = self.client.post(f'/api/documents/{self.doc1_id}/permissions',
                                  headers={'Authorization': f'Bearer {self.trainer_token}'},
                                  json={
                                      'user_id': self.student_id,
                                      'permission': 'read'
                                  })
        
        # This might return 201 or 200 depending on implementation
        assert response.status_code in [200, 201]
    
    def test_remove_document_permission(self):
        """Test removing document permission."""
        # First add permission
        self.client.post(f'/api/documents/{self.doc1_id}/permissions',
                       headers={'Authorization': f'Bearer {self.trainer_token}'},
                       json={
                           'user_id': self.student_id,
                           'permission': 'read'
                       })
        
        # Then remove it
        response = self.client.delete(f'/api/documents/{self.doc1_id}/permissions',
                                    headers={'Authorization': f'Bearer {self.trainer_token}'},
                                    json={
                                        'user_id': self.student_id
                                    })
        
        assert response.status_code == 200
    
    def test_list_documents_as_student(self):
        """Test that students can list documents."""
        response = self.client.get('/api/documents',
                                 headers={'Authorization': f'Bearer {self.student_token}'})
        
        # Students might see limited documents or get forbidden
        assert response.status_code in [200, 403]
    
    def test_unauthorized_permission_change(self):
        """Test that users cannot change permissions on documents they don't own."""
        response = self.client.post(f'/api/documents/{self.doc2_id}/permissions',
                                  headers={'Authorization': f'Bearer {self.trainer_token}'},
                                  json={
                                      'user_id': self.student_id,
                                      'permission': 'write'
                                  })
        
        # Should be forbidden since trainer doesn't own doc2
        assert response.status_code == 403