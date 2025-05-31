"""Integration tests for authentication service and API."""
import pytest
import json
from datetime import datetime, timedelta

from tests.integration.base_integration_test import BaseIntegrationTest
from app.core.container import get_auth_service
from app.models import User, UserActivity


class TestAuthIntegration(BaseIntegrationTest):
    """Test authentication service integration."""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/api/v2/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test123!'
        })
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post('/api/v2/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })
        
        self.assert_response_error(response, 401)
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_inactive_user(self, client, session, test_user):
        """Test login with inactive user."""
        test_user.is_active = False
        session.commit()
        
        response = client.post('/api/v2/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test123!'
        })
        
        self.assert_response_error(response, 401)
    
    def test_register_new_user(self, client, test_tenant):
        """Test registering a new user."""
        response = client.post('/api/v2/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'NewUser123!',
            'name': 'New',
            'surname': 'User',
            'role': 'user',
            'tenant_id': test_tenant.id
        })
        
        self.assert_response_ok(response, 201)
        data = json.loads(response.data)
        
        assert data['user']['email'] == 'newuser@example.com'
        assert data['message'] == 'User registered successfully'
    
    def test_register_duplicate_email(self, client, test_user, test_tenant):
        """Test registering with duplicate email."""
        response = client.post('/api/v2/auth/register', json={
            'email': 'test@example.com',
            'password': 'Password123!',
            'name': 'Another',
            'surname': 'User',
            'role': 'user',
            'tenant_id': test_tenant.id
        })
        
        self.assert_response_error(response, 400)
    
    def test_refresh_token(self, client, test_user, security_manager):
        """Test refreshing access token."""
        # First login to get refresh token
        response = client.post('/api/v2/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test123!'
        })
        
        data = json.loads(response.data)
        refresh_token = data['refresh_token']
        
        # Use refresh token
        response = client.post('/api/v2/auth/refresh', json={
            'refresh_token': refresh_token
        })
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_logout(self, client, auth_headers):
        """Test logout functionality."""
        response = client.post('/api/v2/auth/logout', headers=auth_headers)
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert data['message'] == 'Logged out successfully'
    
    def test_forgot_password(self, client, test_user):
        """Test forgot password functionality."""
        response = client.post('/api/v2/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert 'reset_token' in data  # Only in dev mode
    
    def test_reset_password(self, client, test_user):
        """Test password reset functionality."""
        # Request reset token
        response = client.post('/api/v2/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        
        data = json.loads(response.data)
        reset_token = data['reset_token']
        
        # Reset password
        response = client.post('/api/v2/auth/reset-password', json={
            'token': reset_token,
            'new_password': 'NewPassword123!'
        })
        
        self.assert_response_ok(response)
        
        # Try logging in with new password
        response = client.post('/api/v2/auth/login', json={
            'email': 'test@example.com',
            'password': 'NewPassword123!'
        })
        
        self.assert_response_ok(response)
    
    def test_change_password(self, client, auth_headers):
        """Test changing password."""
        response = client.post('/api/v2/auth/change-password', 
                             headers=auth_headers,
                             json={
                                 'current_password': 'Test123!',
                                 'new_password': 'NewTest123!'
                             })
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert data['message'] == 'Password changed successfully'
    
    def test_verify_token(self, client, auth_headers):
        """Test token verification."""
        response = client.get('/api/v2/auth/verify', headers=auth_headers)
        
        self.assert_response_ok(response)
        data = json.loads(response.data)
        assert data['valid'] is True
        assert data['user']['email'] == 'test@example.com'
    
    def test_auth_service_directly(self, app, session, test_user):
        """Test auth service methods directly."""
        with app.app_context():
            auth_service = get_auth_service()
            
            # Test authenticate
            result = auth_service.authenticate('test@example.com', 'Test123!')
            assert result is not None
            assert result['user'].id == test_user.id
            
            # Test failed authentication
            result = auth_service.authenticate('test@example.com', 'wrong')
            assert result is None
            
            # Check failed attempts
            session.refresh(test_user)
            assert test_user.failed_login_attempts == 1
    
    def test_account_lockout(self, app, session, test_user):
        """Test account lockout after failed attempts."""
        with app.app_context():
            auth_service = get_auth_service()
            
            # Fail 5 times
            for _ in range(5):
                auth_service.authenticate('test@example.com', 'wrong')
            
            # Check account is locked
            session.refresh(test_user)
            assert test_user.is_active is False
            assert test_user.locked_at is not None
            
            # Try with correct password - should still fail
            result = auth_service.authenticate('test@example.com', 'Test123!')
            assert result is None
    
    def test_user_activity_logging(self, app, session, test_user):
        """Test that user activities are logged."""
        with app.app_context():
            auth_service = get_auth_service()
            
            # Login
            auth_service.authenticate('test@example.com', 'Test123!')
            
            # Check activity was logged
            activity = session.query(UserActivity).filter_by(
                user_id=test_user.id,
                activity_type='login'
            ).first()
            
            assert activity is not None
            assert activity.details['remember'] is False