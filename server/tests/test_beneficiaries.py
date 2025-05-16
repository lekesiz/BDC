import pytest
import json
from datetime import datetime
from models import Beneficiary

class TestBeneficiaries:
    """Test beneficiary endpoints."""
    
    def test_create_beneficiary(self, client, auth_headers, test_tenant, test_trainer):
        """Test creating a new beneficiary."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1987654321',
            'date_of_birth': '1995-05-15',
            'trainer_id': test_trainer.id,
            'status': 'active'
        }
        
        response = client.post('/api/beneficiaries',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['first_name'] == 'Jane'
        assert data['last_name'] == 'Smith'
        assert data['email'] == 'jane.smith@example.com'
    
    def test_create_beneficiary_duplicate_email(self, client, auth_headers, test_beneficiary):
        """Test creating a beneficiary with duplicate email."""
        data = {
            'first_name': 'Another',
            'last_name': 'Person',
            'email': test_beneficiary.email,
            'phone': '+1999999999',
            'date_of_birth': '1990-01-01',
            'status': 'active'
        }
        
        response = client.post('/api/beneficiaries',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']
    
    def test_get_beneficiaries(self, client, auth_headers, test_beneficiary):
        """Test getting list of beneficiaries."""
        response = client.get('/api/beneficiaries',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'beneficiaries' in data
        assert 'total' in data
        assert len(data['beneficiaries']) > 0
    
    def test_get_beneficiaries_with_search(self, client, auth_headers, test_beneficiary):
        """Test searching beneficiaries."""
        response = client.get(f'/api/beneficiaries?search={test_beneficiary.first_name}',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['beneficiaries']) > 0
        assert data['beneficiaries'][0]['first_name'] == test_beneficiary.first_name
    
    def test_get_beneficiaries_with_filter(self, client, auth_headers, test_beneficiary):
        """Test filtering beneficiaries by status."""
        response = client.get('/api/beneficiaries?status=active',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(b['status'] == 'active' for b in data['beneficiaries'])
    
    def test_get_beneficiary_by_id(self, client, auth_headers, test_beneficiary):
        """Test getting a specific beneficiary."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_beneficiary.id
        assert data['email'] == test_beneficiary.email
    
    def test_get_beneficiary_not_found(self, client, auth_headers):
        """Test getting a non-existent beneficiary."""
        response = client.get('/api/beneficiaries/99999',
                             headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_beneficiary(self, client, auth_headers, test_beneficiary):
        """Test updating a beneficiary."""
        data = {
            'phone': '+1555555555',
            'status': 'graduated'
        }
        
        response = client.put(f'/api/beneficiaries/{test_beneficiary.id}',
                             json=data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['phone'] == '+1555555555'
        assert data['status'] == 'graduated'
    
    def test_delete_beneficiary(self, client, auth_headers, test_beneficiary, db_session):
        """Test deleting a beneficiary."""
        response = client.delete(f'/api/beneficiaries/{test_beneficiary.id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        
        # Verify soft delete
        beneficiary = db_session.query(Beneficiary).filter_by(id=test_beneficiary.id).first()
        assert beneficiary.deleted_at is not None
    
    def test_assign_trainer(self, client, auth_headers, test_beneficiary, test_trainer):
        """Test assigning a trainer to a beneficiary."""
        data = {
            'trainer_id': test_trainer.id
        }
        
        response = client.post(f'/api/beneficiaries/{test_beneficiary.id}/assign-trainer',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['trainer_id'] == test_trainer.id
    
    def test_get_beneficiary_progress(self, client, auth_headers, test_beneficiary):
        """Test getting beneficiary progress."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}/progress',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'overall_progress' in data
        assert 'program_progress' in data
        assert 'test_scores' in data
    
    def test_get_beneficiary_tests(self, client, auth_headers, test_beneficiary):
        """Test getting beneficiary test history."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}/tests',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tests' in data
        assert isinstance(data['tests'], list)
    
    def test_get_beneficiary_appointments(self, client, auth_headers, test_beneficiary):
        """Test getting beneficiary appointments."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}/appointments',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'appointments' in data
        assert isinstance(data['appointments'], list)
    
    def test_export_beneficiaries(self, client, auth_headers):
        """Test exporting beneficiaries to CSV."""
        response = client.get('/api/beneficiaries/export?format=csv',
                             headers=auth_headers)
        
        assert response.status_code == 200
        assert response.content_type == 'text/csv'
    
    def test_import_beneficiaries(self, client, auth_headers):
        """Test importing beneficiaries from CSV."""
        csv_data = """first_name,last_name,email,phone,date_of_birth
Alice,Brown,alice.brown@example.com,+1234567890,1990-01-01
Bob,Wilson,bob.wilson@example.com,+0987654321,1992-05-15"""
        
        response = client.post('/api/beneficiaries/import',
                              data={'file': (csv_data, 'beneficiaries.csv')},
                              headers=auth_headers,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['imported'] == 2
    
    def test_get_beneficiary_documents(self, client, auth_headers, test_beneficiary):
        """Test getting beneficiary documents."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}/documents',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'documents' in data
        assert isinstance(data['documents'], list)
    
    def test_access_control(self, client, student_headers, test_beneficiary):
        """Test that students cannot access beneficiary data."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}',
                             headers=student_headers)
        
        assert response.status_code == 403
    
    def test_trainer_can_access_own_beneficiaries(self, client, trainer_headers, test_beneficiary):
        """Test that trainers can access their own beneficiaries."""
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}',
                             headers=trainer_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_beneficiary.id