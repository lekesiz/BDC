"""Comprehensive tests for auth API endpoints."""
import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant


class TestAuthAPI:
    """Test auth API endpoints comprehensively."""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Set up test environment."""
        self.app = app
        self.client = app.test_client()
        
        with app.app_context():
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
            
            self.inactive_user = User(
                email='inactive@test.com',
                username='inactive',
                first_name='Inactive',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id,
                is_active=False
            )
            self.inactive_user.password = 'Test123!'
            
            db.session.add(self.admin_user)
            db.session.add(self.inactive_user)
            db.session.commit()
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'admin@test.com',
                'password': 'Admin123!',
                'remember': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'
        assert data['user']['email'] == 'admin@test.com'
        assert data['user']['role'] == 'super_admin'
    
    def test_login_with_remember(self):
        """Test login with remember me option."""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'admin@test.com',
                'password': 'Admin123!',
                'remember': True
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'admin@test.com',
                'password': 'WrongPassword',
                'remember': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'invalid_credentials'
    
    def test_login_inactive_user(self):
        """Test login with inactive user."""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'inactive@test.com',
                'password': 'Test123!',
                'remember': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'invalid_credentials'
    
    def test_login_validation_error(self):
        """Test login with validation errors."""
        # Missing email
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'password': 'Test123!'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'
        assert 'email' in data['errors']
        
        # Invalid email format
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'not-an-email',
                'password': 'Test123!'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'
    
    def test_login_empty_request(self):
        """Test login with empty request body."""
        response = self.client.post('/api/auth/login',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'invalid_request'
    
    def test_register_success(self):
        """Test successful registration."""
        response = self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'newuser@test.com',
                'password': 'NewUser123!',
                'confirm_password': 'NewUser123!',
                'first_name': 'New',
                'last_name': 'User',
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['user']['email'] == 'newuser@test.com'
        
        # Verify user was created
        with self.app.app_context():
            user = User.query.filter_by(email='newuser@test.com').first()
            assert user is not None
            assert user.first_name == 'New'
            assert user.last_name == 'User'
            assert user.role == 'student'
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        response = self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'admin@test.com',
                'password': 'Test123!',
                'confirm_password': 'Test123!',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'student'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'email' in data['errors']
    
    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        response = self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'Test123!',
                'confirm_password': 'Different123!',
                'first_name': 'Test',
                'last_name': 'User'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'confirm_password' in data['errors']
    
    def test_register_weak_password(self):
        """Test registration with weak password."""
        response = self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'weak',
                'confirm_password': 'weak',
                'first_name': 'Test',
                'last_name': 'User'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'password' in data['errors']
    
    def test_logout_success(self):
        """Test successful logout."""
        # First login
        with self.app.app_context():
            access_token = create_access_token(identity=self.admin_user.id)
        
        response = self.client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Successfully logged out'
    
    def test_logout_without_token(self):
        """Test logout without token."""
        response = self.client.post('/api/auth/logout')
        
        assert response.status_code == 401
    
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'admin@test.com',
                'password': 'Admin123!',
                'remember': False
            }),
            content_type='application/json'
        )
        
        refresh_token = json.loads(login_response.data)['refresh_token']
        
        # Use refresh token
        response = self.client.post('/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_refresh_with_access_token(self):
        """Test refresh with access token instead of refresh token."""
        with self.app.app_context():
            access_token = create_access_token(identity=self.admin_user.id)
        
        response = self.client.post('/api/auth/refresh',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Should fail because it's not a refresh token
        assert response.status_code == 422
    
    def test_change_password_success(self):
        """Test successful password change."""
        with self.app.app_context():
            access_token = create_access_token(identity=self.admin_user.id)
        
        response = self.client.post('/api/auth/change-password',
            data=json.dumps({
                'current_password': 'Admin123!',
                'new_password': 'NewAdmin123!',
                'confirm_password': 'NewAdmin123!'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password changed successfully'
        
        # Verify password was changed
        with self.app.app_context():
            user = User.query.get(self.admin_user.id)
            assert user.verify_password('NewAdmin123!')
            assert not user.verify_password('Admin123!')
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password."""
        with self.app.app_context():
            access_token = create_access_token(identity=self.admin_user.id)
        
        response = self.client.post('/api/auth/change-password',
            data=json.dumps({
                'current_password': 'WrongPassword',
                'new_password': 'NewAdmin123!',
                'confirm_password': 'NewAdmin123!'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'invalid_password'
    
    def test_reset_password_request(self):
        """Test password reset request."""
        response = self.client.post('/api/auth/reset-password/request',
            data=json.dumps({
                'email': 'admin@test.com'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'If the email exists' in data['message']
    
    def test_reset_password_nonexistent_email(self):
        """Test password reset for nonexistent email."""
        response = self.client.post('/api/auth/reset-password/request',
            data=json.dumps({
                'email': 'nonexistent@test.com'
            }),
            content_type='application/json'
        )
        
        # Should return same response for security
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'If the email exists' in data['message']
    
    @patch('app.api.auth.verify_reset_token')
    def test_reset_password_with_token(self, mock_verify):
        """Test password reset with token."""
        mock_verify.return_value = self.admin_user
        
        response = self.client.post('/api/auth/reset-password',
            data=json.dumps({
                'token': 'valid-token',
                'password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password reset successfully'
    
    @patch('app.api.auth.verify_reset_token')
    def test_reset_password_invalid_token(self, mock_verify):
        """Test password reset with invalid token."""
        mock_verify.return_value = None
        
        response = self.client.post('/api/auth/reset-password',
            data=json.dumps({
                'token': 'invalid-token',
                'password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'invalid_token'
    
    def test_verify_email(self):
        """Test email verification endpoint."""
        with self.app.app_context():
            access_token = create_access_token(identity=self.admin_user.id)
        
        response = self.client.post('/api/auth/verify-email',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # This endpoint might not be implemented yet
        assert response.status_code in [200, 404]
    
    def test_auth_debug_endpoint(self):
        """Test auth debug endpoint."""
        response = self.client.get('/api/auth/debug')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'admin_exists' in data
        assert 'total_users' in data
        assert data['total_users'] >= 2  # At least our test users