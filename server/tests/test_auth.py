import pytest
import json
from flask_jwt_extended import decode_token
from models import User

class TestAuth:
    """Test authentication endpoints."""
    
    def test_register_success(self, client, test_tenant):
        """Test successful user registration."""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Password123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student',
            'tenant_id': test_tenant.id
        }
        
        response = client.post('/api/auth/register', 
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert 'user' in data
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        data = {
            'email': test_user.email,
            'username': 'anotheruser',
            'password': 'Password123!',
            'first_name': 'Another',
            'last_name': 'User',
            'role': 'student',
            'tenant_id': test_user.tenant_id
        }
        
        response = client.post('/api/auth/register',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        data = {
            'email': test_user.email,
            'password': 'password123'
        }
        
        response = client.post('/api/auth/login',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == test_user.email
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        data = {
            'email': test_user.email,
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data['error']
    
    def test_login_inactive_user(self, client, test_user, db_session):
        """Test login with inactive user."""
        test_user.is_active = False
        db_session.commit()
        
        data = {
            'email': test_user.email,
            'password': 'password123'
        }
        
        response = client.post('/api/auth/login',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Account is disabled' in data['error']
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post('/api/auth/logout',
                              headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Successfully logged out'
    
    def test_logout_without_auth(self, client):
        """Test logout without authentication."""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self, client, test_user):
        """Test token refresh."""
        # First login to get tokens
        login_data = {
            'email': test_user.email,
            'password': 'password123'
        }
        
        login_response = client.post('/api/auth/login',
                                    json=login_data,
                                    content_type='application/json')
        
        tokens = json.loads(login_response.data)
        refresh_token = tokens['refresh_token']
        
        # Use refresh token to get new access token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/api/auth/refresh',
                              headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user info."""
        response = client.get('/api/auth/me',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == test_user.email
        assert data['role'] == test_user.role
    
    def test_update_password(self, client, auth_headers, test_user, db_session):
        """Test password update."""
        data = {
            'current_password': 'password123',
            'new_password': 'NewPassword123!'
        }
        
        response = client.put('/api/auth/password',
                             json=data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password updated successfully'
        
        # Verify new password works
        login_data = {
            'email': test_user.email,
            'password': 'NewPassword123!'
        }
        
        login_response = client.post('/api/auth/login',
                                    json=login_data,
                                    content_type='application/json')
        
        assert login_response.status_code == 200
    
    def test_update_password_wrong_current(self, client, auth_headers):
        """Test password update with wrong current password."""
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'NewPassword123!'
        }
        
        response = client.put('/api/auth/password',
                             json=data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Current password is incorrect' in data['error']
    
    def test_forgot_password(self, client, test_user):
        """Test forgot password request."""
        data = {
            'email': test_user.email
        }
        
        response = client.post('/api/auth/forgot-password',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'reset instructions' in data['message']
    
    def test_reset_password(self, client, test_user, db_session):
        """Test password reset with token."""
        # Generate a reset token (in real app this would be sent via email)
        reset_token = test_user.generate_reset_token()
        
        data = {
            'token': reset_token,
            'new_password': 'ResetPassword123!'
        }
        
        response = client.post('/api/auth/reset-password',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Password has been reset' in data['message']
        
        # Verify new password works
        login_data = {
            'email': test_user.email,
            'password': 'ResetPassword123!'
        }
        
        login_response = client.post('/api/auth/login',
                                    json=login_data,
                                    content_type='application/json')
        
        assert login_response.status_code == 200
    
    def test_verify_email(self, client, test_user):
        """Test email verification."""
        # Generate verification token
        verification_token = test_user.generate_verification_token()
        
        response = client.get(f'/api/auth/verify-email/{verification_token}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Email verified successfully' in data['message']
    
    def test_resend_verification_email(self, client, test_user):
        """Test resending verification email."""
        data = {
            'email': test_user.email
        }
        
        response = client.post('/api/auth/resend-verification',
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Verification email sent' in data['message']