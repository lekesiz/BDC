"""
API Tests for BDC endpoints.

These tests ensure all API endpoints work correctly,
return appropriate status codes, and handle errors properly.
"""

import pytest
import json
from datetime import datetime
from app.models import User, Beneficiary, Program


@pytest.mark.api
class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_register_endpoint(self, client):
        """Test user registration endpoint."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert 'access_token' in json_data
        assert 'user' in json_data
        assert json_data['user']['email'] == data['email']
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        data = {
            'username': 'another_user',
            'email': test_user.email,  # Duplicate email
            'password': 'Test123!',
            'first_name': 'Another',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['message']
    
    def test_login_endpoint(self, client, test_user):
        """Test user login endpoint."""
        data = {
            'email': test_user.email,
            'password': 'password123'  # Assuming this is the test password
        }
        
        response = client.post('/api/auth/login', json=data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'access_token' in json_data
        assert 'user' in json_data
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        data = {
            'email': test_user.email,
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login', json=data)
        assert response.status_code == 401
        assert 'Invalid credentials' in response.get_json()['message']
    
    def test_get_current_user(self, client, test_trainer):
        """Test getting current user information."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get('/api/auth/me', headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == test_trainer['user'].id
        assert json_data['email'] == test_trainer['user'].email
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401


@pytest.mark.api
class TestBeneficiaryAPI:
    """Test beneficiary API endpoints."""
    
    def test_list_beneficiaries(self, client, test_trainer):
        """Test listing beneficiaries."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get('/api/beneficiaries', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_create_beneficiary(self, client, test_trainer):
        """Test creating a new beneficiary."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'username': 'newbeneficiary',
            'email': 'newben@example.com',
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'Beneficiary',
            'date_of_birth': '1990-01-01',
            'phone': '+1234567890'
        }
        
        response = client.post('/api/beneficiaries', json=data, headers=headers)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['email'] == data['email']
    
    def test_get_beneficiary(self, client, test_trainer, test_beneficiary):
        """Test getting a specific beneficiary."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}', headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == test_beneficiary.id
    
    def test_update_beneficiary(self, client, test_trainer, test_beneficiary):
        """Test updating beneficiary information."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'phone': '+9876543210',
            'notes': 'Updated phone number'
        }
        
        response = client.put(
            f'/api/beneficiaries/{test_beneficiary.id}',
            json=data,
            headers=headers
        )
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['phone'] == data['phone']
    
    def test_delete_beneficiary(self, client, test_admin, test_beneficiary):
        """Test deleting a beneficiary (admin only)."""
        headers = {'Authorization': f'Bearer {test_admin["token"]}'}
        response = client.delete(
            f'/api/beneficiaries/{test_beneficiary.id}',
            headers=headers
        )
        assert response.status_code in [200, 204]
    
    def test_search_beneficiaries(self, client, test_trainer):
        """Test searching beneficiaries."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get('/api/beneficiaries?search=test', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


@pytest.mark.api
class TestProgramAPI:
    """Test program API endpoints."""
    
    def test_list_programs(self, client, test_trainer):
        """Test listing programs."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get('/api/programs', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_create_program(self, client, test_trainer):
        """Test creating a new program."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'name': 'Test Program',
            'description': 'Test program description',
            'start_date': '2025-01-01',
            'end_date': '2025-03-31',
            'status': 'active'
        }
        
        response = client.post('/api/programs', json=data, headers=headers)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['name'] == data['name']
    
    def test_get_program_details(self, client, test_trainer, test_program):
        """Test getting program details."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get(f'/api/programs/{test_program.id}', headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == test_program.id
    
    def test_assign_beneficiaries_to_program(self, client, test_trainer, test_program, test_beneficiary):
        """Test assigning beneficiaries to a program."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'beneficiary_ids': [test_beneficiary.id]
        }
        
        response = client.post(
            f'/api/programs/{test_program.id}/beneficiaries',
            json=data,
            headers=headers
        )
        assert response.status_code in [200, 201]


@pytest.mark.api
class TestDocumentAPI:
    """Test document API endpoints."""
    
    def test_upload_document(self, client, test_trainer):
        """Test document upload endpoint."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'title': 'Test Document',
            'description': 'Test document description',
            'file_path': '/uploads/test.pdf',
            'file_size': 1024,
            'mime_type': 'application/pdf'
        }
        
        response = client.post('/api/documents', json=data, headers=headers)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['title'] == data['title']
    
    def test_list_documents(self, client, test_trainer):
        """Test listing documents."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get('/api/documents', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_share_document(self, client, test_trainer, test_document, test_beneficiary):
        """Test document sharing."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'document_id': test_document.id,
            'user_ids': [test_beneficiary.id],
            'permission': 'read'
        }
        
        response = client.post('/api/documents/share', json=data, headers=headers)
        assert response.status_code in [200, 201]


@pytest.mark.api
class TestNotificationAPI:
    """Test notification API endpoints."""
    
    def test_get_notifications(self, client, test_beneficiary):
        """Test getting user notifications."""
        token = test_beneficiary.generate_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/notifications', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_unread_notifications(self, client, test_beneficiary):
        """Test getting unread notifications."""
        token = test_beneficiary.generate_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/notifications/unread', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_mark_notification_read(self, client, test_beneficiary, test_notification):
        """Test marking notification as read."""
        token = test_beneficiary.generate_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = client.put(
            f'/api/notifications/{test_notification.id}/read',
            headers=headers
        )
        assert response.status_code == 200


@pytest.mark.api 
class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_not_found(self, client, test_trainer):
        """Test 404 error for non-existent resource."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        response = client.get('/api/beneficiaries/999999', headers=headers)
        assert response.status_code == 404
    
    def test_400_bad_request(self, client, test_trainer):
        """Test 400 error for invalid data."""
        headers = {'Authorization': f'Bearer {test_trainer["token"]}'}
        data = {
            'name': 'Test',
            # Missing required fields
        }
        response = client.post('/api/programs', json=data, headers=headers)
        assert response.status_code == 400
    
    def test_403_forbidden(self, client, test_beneficiary, test_program):
        """Test 403 error for unauthorized action."""
        token = test_beneficiary.generate_auth_token()
        headers = {'Authorization': f'Bearer {token}'}
        # Beneficiary trying to delete a program (admin only)
        response = client.delete(f'/api/programs/{test_program.id}', headers=headers)
        assert response.status_code == 403
    
    def test_method_not_allowed(self, client):
        """Test 405 error for unsupported method."""
        response = client.patch('/api/auth/login')  # PATCH not allowed on login
        assert response.status_code == 405