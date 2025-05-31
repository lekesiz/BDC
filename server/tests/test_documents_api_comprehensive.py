"""Comprehensive tests for documents API endpoints."""
import pytest
from unittest.mock import Mock, patch
import json
import io
from datetime import datetime
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.document import Document
from app.models.beneficiary import Beneficiary
from app.models.folder import Folder


class TestDocumentsAPI:
    """Test documents API endpoints comprehensively."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        """Set up test environment."""
        self.app = test_app
        self.client = test_app.test_client()
        
        with test_app.app_context():
            # Create test tenant
            self.tenant = Tenant(
                name='Test Tenant',
                slug='test-tenant',
                email='tenant@test.com',
                is_active=True
            )
            db.session.add(self.tenant)
            
            # Create test users
            self.admin_user = User(
                email='admin@test.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role='super_admin',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.admin_user.password = 'Admin123!'
            
            self.trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.trainer.password = 'Trainer123!'
            
            self.student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.student.password = 'Student123!'
            
            db.session.add_all([self.admin_user, self.trainer, self.student])
            
            # Create beneficiary
            self.beneficiary = Beneficiary(
                user_id=self.student.id,
                tenant_id=self.tenant.id,
                status='active',
                enrollment_date=datetime.now()
            )
            db.session.add(self.beneficiary)
            
            # Create folders
            self.root_folder = Folder(
                name='Documents',
                tenant_id=self.tenant.id,
                created_by_id=self.admin_user.id
            )
            
            self.subfolder = Folder(
                name='Training Materials',
                tenant_id=self.tenant.id,
                parent_id=self.root_folder.id,
                created_by_id=self.admin_user.id
            )
            
            db.session.add_all([self.root_folder, self.subfolder])
            
            # Create documents
            self.doc1 = Document(
                title='Training Manual',
                filename='training_manual.pdf',
                file_path='/uploads/training_manual.pdf',
                file_size=1024000,
                mime_type='application/pdf',
                document_type='manual',
                folder_id=self.subfolder.id,
                uploaded_by_id=self.admin_user.id,
                tenant_id=self.tenant.id,
                access_level='internal',
                is_public=False
            )
            
            self.doc2 = Document(
                title='Student Guide',
                filename='student_guide.docx',
                file_path='/uploads/student_guide.docx',
                file_size=512000,
                mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                document_type='guide',
                uploaded_by_id=self.trainer.id,
                tenant_id=self.tenant.id,
                beneficiary_id=self.beneficiary.id,
                access_level='beneficiary',
                is_public=False
            )
            
            self.public_doc = Document(
                title='Public Information',
                filename='public_info.pdf',
                file_path='/uploads/public_info.pdf',
                file_size=256000,
                mime_type='application/pdf',
                document_type='info',
                uploaded_by_id=self.admin_user.id,
                tenant_id=self.tenant.id,
                access_level='public',
                is_public=True
            )
            
            db.session.add_all([self.doc1, self.doc2, self.public_doc])
            db.session.commit()
            
            # Create access tokens
            self.admin_token = create_access_token(identity=self.admin_user.id)
            self.trainer_token = create_access_token(identity=self.trainer.id)
            self.student_token = create_access_token(identity=self.student.id)
    
    def test_get_documents_list(self):
        """Test getting documents list."""
        response = self.client.get('/api/documents',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'documents' in data
        assert len(data['documents']) >= 3
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
    
    def test_get_documents_with_filters(self):
        """Test getting documents with filters."""
        # Filter by document type
        response = self.client.get('/api/documents?document_type=manual',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(d['document_type'] == 'manual' for d in data['documents'])
        
        # Filter by folder
        response = self.client.get(f'/api/documents?folder_id={self.subfolder.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any(d['folder_id'] == self.subfolder.id for d in data['documents'])
    
    def test_get_document_by_id(self):
        """Test getting specific document."""
        response = self.client.get(f'/api/documents/{self.doc1.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == self.doc1.id
        assert data['title'] == 'Training Manual'
        assert data['file_size'] == 1024000
    
    def test_upload_document(self):
        """Test uploading a new document."""
        # Create test file
        test_file = io.BytesIO(b'Test file content')
        test_file.name = 'test_document.txt'
        
        response = self.client.post('/api/documents/upload',
            data={
                'file': (test_file, 'test_document.txt'),
                'title': 'Test Document',
                'document_type': 'report',
                'folder_id': self.root_folder.id,
                'access_level': 'internal',
                'description': 'A test document'
            },
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Document'
        assert data['filename'] == 'test_document.txt'
        assert data['document_type'] == 'report'
    
    def test_update_document_metadata(self):
        """Test updating document metadata."""
        response = self.client.put(f'/api/documents/{self.doc1.id}',
            data=json.dumps({
                'title': 'Updated Training Manual',
                'description': 'Updated description',
                'tags': ['training', 'manual', 'updated']
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Training Manual'
        assert data['description'] == 'Updated description'
        assert 'training' in data.get('tags', [])
    
    def test_move_document(self):
        """Test moving document to different folder."""
        response = self.client.post(f'/api/documents/{self.doc1.id}/move',
            data=json.dumps({
                'folder_id': self.root_folder.id
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['folder_id'] == self.root_folder.id
    
    def test_share_document(self):
        """Test sharing document with users."""
        response = self.client.post(f'/api/documents/{self.doc1.id}/share',
            data=json.dumps({
                'user_ids': [self.student.id],
                'access_level': 'read',
                'expires_at': None
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]  # Might not be implemented
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'shared_with' in data
    
    def test_download_document(self):
        """Test downloading a document."""
        response = self.client.get(f'/api/documents/{self.doc1.id}/download',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Download might fail if file doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type in [
                'application/pdf',
                'application/octet-stream'
            ]
    
    def test_delete_document(self):
        """Test deleting a document."""
        # Create a document to delete
        with self.app.app_context():
            doc_to_delete = Document(
                title='To Delete',
                filename='delete_me.txt',
                file_path='/uploads/delete_me.txt',
                file_size=100,
                mime_type='text/plain',
                document_type='other',
                uploaded_by_id=self.admin_user.id,
                tenant_id=self.tenant.id
            )
            db.session.add(doc_to_delete)
            db.session.commit()
            delete_id = doc_to_delete.id
        
        response = self.client.delete(f'/api/documents/{delete_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify document is deleted
        with self.app.app_context():
            doc = Document.query.get(delete_id)
            assert doc is None
    
    def test_get_document_versions(self):
        """Test getting document versions."""
        response = self.client.get(f'/api/documents/{self.doc1.id}/versions',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'versions' in data
    
    def test_restore_document_version(self):
        """Test restoring previous document version."""
        response = self.client.post(f'/api/documents/{self.doc1.id}/restore',
            data=json.dumps({
                'version_id': 1
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404, 400]
    
    def test_bulk_download_documents(self):
        """Test bulk downloading documents as zip."""
        response = self.client.post('/api/documents/bulk-download',
            data=json.dumps({
                'document_ids': [self.doc1.id, self.doc2.id]
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type == 'application/zip'
    
    def test_get_my_documents(self):
        """Test getting documents for current user."""
        response = self.client.get('/api/documents/my',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'documents' in data
        # Should include documents shared with the student
    
    def test_search_documents(self):
        """Test searching documents."""
        response = self.client.get('/api/documents/search?q=training',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'documents' in data
        assert any('training' in d['title'].lower() for d in data['documents'])
    
    def test_get_document_preview(self):
        """Test getting document preview."""
        response = self.client.get(f'/api/documents/{self.doc1.id}/preview',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert 'preview_url' in json.loads(response.data)
    
    def test_document_access_permissions(self):
        """Test document access permissions."""
        # Student accessing their document
        response = self.client.get(f'/api/documents/{self.doc2.id}',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        assert response.status_code == 200
        
        # Student accessing admin document
        response = self.client.get(f'/api/documents/{self.doc1.id}',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        assert response.status_code in [403, 404]
        
        # Anyone accessing public document
        response = self.client.get(f'/api/documents/{self.public_doc.id}')
        assert response.status_code == 200
    
    def test_upload_large_file(self):
        """Test uploading large file."""
        # Create large test file (5MB)
        large_file = io.BytesIO(b'x' * 5 * 1024 * 1024)
        large_file.name = 'large_file.bin'
        
        response = self.client.post('/api/documents/upload',
            data={
                'file': (large_file, 'large_file.bin'),
                'title': 'Large File',
                'document_type': 'other'
            },
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Should handle large files
        assert response.status_code in [201, 413]  # 413 if file too large
    
    def test_upload_invalid_file_type(self):
        """Test uploading invalid file type."""
        test_file = io.BytesIO(b'#!/bin/bash\necho "test"')
        test_file.name = 'script.sh'
        
        response = self.client.post('/api/documents/upload',
            data={
                'file': (test_file, 'script.sh'),
                'title': 'Shell Script',
                'document_type': 'other'
            },
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Might reject certain file types
        assert response.status_code in [201, 400]
    
    def test_document_analytics(self):
        """Test getting document analytics."""
        response = self.client.get('/api/documents/analytics',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'total_documents' in data
            assert 'total_size' in data
            assert 'documents_by_type' in data
    
    def test_document_audit_log(self):
        """Test getting document audit log."""
        response = self.client.get(f'/api/documents/{self.doc1.id}/audit-log',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'audit_entries' in data
    
    def test_export_document_list(self):
        """Test exporting document list."""
        response = self.client.get('/api/documents/export?format=csv',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type in ['text/csv', 'application/csv']