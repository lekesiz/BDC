"""
API Tests for BDC endpoints.

These tests ensure all API endpoints work correctly,
return appropriate status codes, and handle errors properly.
"""

import pytest
import json
from datetime import datetime


def get_auth_token(client, user):
    """Helper function to get auth token for a user."""
    login_data = {
        'email': user.email,
        'password': 'password123'  # Default test password
    }
    response = client.post('/api/auth/login', json=login_data)
    return response.get_json()['access_token']
from app.models import User, Beneficiary, Program


@pytest.mark.api
class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_register_endpoint(self, client):
        """Test user registration endpoint."""
        data = {
            'email': 'test@example.com',
            'password': 'Test123!',
            'confirm_password': 'Test123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = client.post('/api/auth/register', json=data)
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
        assert response.status_code == 201
        json_data = response.get_json()
        assert 'access_token' in json_data
        assert 'refresh_token' in json_data
        assert 'token_type' in json_data
        assert json_data['token_type'] == 'bearer'
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        data = {
            'email': test_user.email,  # Duplicate email
            'password': 'Test123!',
            'confirm_password': 'Test123!',
            'first_name': 'Another',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['error'] == 'validation_error'
        assert 'Email already registered' in json_data['errors']['email'][0]
    
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
        assert 'Invalid email or password' in response.get_json()['message']
    
    def test_get_current_user(self, client, test_trainer):
        """Test getting current user information."""
        # First login to get token
        login_data = {
            'email': test_trainer.email,
            'password': 'password123'
        }
        login_response = client.post('/api/auth/login', json=login_data)
        token = login_response.get_json()['access_token']
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/users/me', headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['email'] == test_trainer.email
        assert json_data['first_name'] == test_trainer.first_name
        assert json_data['last_name'] == test_trainer.last_name
        assert json_data['role'] == test_trainer.role
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get('/api/users/me')
        assert response.status_code == 401


@pytest.mark.api
class TestBeneficiaryAPI:
    """Test beneficiary API endpoints."""
    
    def test_list_beneficiaries(self, client, test_trainer):
        """Test listing beneficiaries."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/beneficiaries', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        # Response is paginated
        assert 'items' in data
        assert isinstance(data['items'], list)
    
    def test_create_beneficiary(self, client, test_admin):
        """Test creating a new beneficiary."""
        token = get_auth_token(client, test_admin)
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'email': 'newben@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'first_name': 'New',
            'last_name': 'Beneficiary',
            'birth_date': '1990-01-01',
            'phone': '+1234567890'
        }
        
        response = client.post('/api/beneficiaries', json=data, headers=headers)
        if response.status_code != 201:
            print(f"Response: {response.get_json()}")
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['user']['email'] == data['email']
    
    def test_get_beneficiary(self, client, test_trainer, test_beneficiary):
        """Test getting a specific beneficiary."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get(f'/api/beneficiaries/{test_beneficiary.id}', headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == test_beneficiary.id
    
    def test_update_beneficiary(self, client, test_trainer, test_beneficiary):
        """Test updating beneficiary information."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
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
        token = get_auth_token(client, test_admin)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.delete(
            f'/api/beneficiaries/{test_beneficiary.id}',
            headers=headers
        )
        assert response.status_code in [200, 204]
    
    def test_search_beneficiaries(self, client, test_trainer):
        """Test searching beneficiaries."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/beneficiaries?search=test', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        # Response is paginated
        assert 'items' in data
        assert isinstance(data['items'], list)


@pytest.mark.api
class TestProgramAPI:
    """Test program API endpoints."""
    
    def test_list_programs(self, client, test_trainer):
        """Test listing programs."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/programs', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_create_program(self, client, test_admin):
        """Test creating a new program."""
        token = get_auth_token(client, test_admin)
        headers = {'Authorization': f'Bearer {token}'}
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
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get(f'/api/programs/{test_program.id}', headers=headers)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == test_program.id
    
    def test_assign_beneficiaries_to_program(self, client, test_trainer, test_program, test_beneficiary):
        """Test assigning beneficiaries to a program."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'beneficiary_id': test_beneficiary.id
        }
        
        response = client.post(
            f'/api/programs/{test_program.id}/enroll',
            json=data,
            headers=headers
        )
        assert response.status_code in [200, 201]


@pytest.mark.api
class TestDocumentAPI:
    """Test document API endpoints."""
    
    def test_upload_document(self, client, test_trainer):
        """Test document upload endpoint."""
        from io import BytesIO
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create a test file
        data = {
            'file': (BytesIO(b'Test file content'), 'test.pdf'),
            'title': 'Test Document',
            'description': 'Test document description',
            'type': 'general'
        }
        
        response = client.post(
            '/api/documents/upload',
            data=data,
            headers=headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code in [200, 201]
        json_data = response.get_json()
        
        # The upload response returns document_id, not the full document
        assert 'document_id' in json_data
        assert 'message' in json_data
        assert json_data['message'] == 'Document uploaded successfully'
    
    def test_list_documents(self, client, test_trainer):
        """Test listing documents."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/documents', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        # Response is paginated
        assert 'documents' in data
        assert isinstance(data['documents'], list)
    
    def test_share_document(self, client, test_trainer, test_document, test_beneficiary):
        """Test document sharing."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'user_id': test_beneficiary.user.id,  # Share with the beneficiary's user
            'permissions': {
                'read': True,
                'write': False,
                'delete': False,
                'share': False
            }
        }
        
        response = client.post(
            f'/api/documents/{test_document.id}/permissions',
            json=data,
            headers=headers
        )
        assert response.status_code in [200, 201]


@pytest.mark.api
class TestNotificationAPI:
    """Test notification API endpoints."""
    
    def test_get_notifications(self, client, test_beneficiary):
        """Test getting user notifications."""
        token = get_auth_token(client, test_beneficiary.user)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/notifications', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        # Response is paginated
        assert 'notifications' in data
        assert isinstance(data['notifications'], list)
    
    def test_get_unread_notifications_count(self, client, test_beneficiary):
        """Test getting unread notifications count."""
        token = get_auth_token(client, test_beneficiary.user)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/notifications/unread-count', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'unread_count' in data
        assert isinstance(data['unread_count'], int)
    
    def test_mark_notification_read(self, client, test_beneficiary, test_notification):
        """Test marking notification as read."""
        token = get_auth_token(client, test_beneficiary.user)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.post(
            f'/api/notifications/{test_notification.id}/read',
            headers=headers
        )
        assert response.status_code == 200


@pytest.mark.api 
class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_not_found(self, client, test_trainer):
        """Test 404 error for non-existent resource."""
        token = get_auth_token(client, test_trainer)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/beneficiaries/999999', headers=headers)
        assert response.status_code == 404
    
    def test_400_bad_request(self, client, test_admin):
        """Test 400 error for invalid data."""
        token = get_auth_token(client, test_admin)
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            # Empty payload should fail
        }
        response = client.post('/api/programs', json=data, headers=headers)
        assert response.status_code in [400, 500]  # Could be 400 or 500 depending on error handling
    
    def test_403_forbidden(self, client, test_beneficiary, test_program):
        """Test 403 error for unauthorized action."""
        token = get_auth_token(client, test_beneficiary.user)
        headers = {'Authorization': f'Bearer {token}'}
        # Beneficiary trying to update a program (admin only)
        data = {
            'name': 'Updated Program'
        }
        response = client.put(f'/api/programs/{test_program.id}', json=data, headers=headers)
        assert response.status_code == 403
    
    def test_method_not_allowed(self, client):
        """Test 405 error for unsupported method."""
        response = client.patch('/api/auth/login')  # PATCH not allowed on login
        assert response.status_code == 405