"""Tests for authentication service."""

import pytest
from datetime import datetime, timezone
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.security import TokenBlocklist


class TestAuthServiceV2:
    """Test authentication service methods."""
    
    def test_login_success(self, test_user, test_app):
        """Test successful user login."""
        with test_app.app_context():
            # Test with correct credentials
            tokens = AuthService.login(test_user.email, 'password123')
            
            assert tokens is not None
            assert 'access_token' in tokens
            assert 'refresh_token' in tokens
            assert tokens['token_type'] == 'bearer'
            assert tokens['expires_in'] == 3600
    
    def test_login_wrong_password(self, test_user, test_app):
        """Test login with wrong password."""
        with test_app.app_context():
            tokens = AuthService.login(test_user.email, 'wrongpassword')
            assert tokens is None
    
    def test_login_nonexistent_user(self, test_app):
        """Test login with non-existent user."""
        with test_app.app_context():
            tokens = AuthService.login('nonexistent@test.com', 'password123')
            assert tokens is None
    
    def test_login_inactive_user(self, test_user, test_app, db_session):
        """Test login with inactive user."""
        with test_app.app_context():
            test_user.is_active = False
            db_session.commit()
            
            tokens = AuthService.login(test_user.email, 'password123')
            assert tokens is None
    
    def test_login_updates_last_login(self, test_user, test_app):
        """Test that login updates last_login timestamp."""
        with test_app.app_context():
            original_last_login = test_user.last_login
            
            tokens = AuthService.login(test_user.email, 'password123')
            
            assert tokens is not None
            assert test_user.last_login is not None
            if original_last_login:
                assert test_user.last_login > original_last_login
    
    def test_login_with_remember(self, test_user, test_app):
        """Test login with remember me option."""
        with test_app.app_context():
            tokens = AuthService.login(test_user.email, 'password123', remember=True)
            
            assert tokens is not None
            # Remember option might affect token expiry or create a longer-lived refresh token
    
    def test_register_new_user(self, test_app, test_tenant):
        """Test registering a new user."""
        with test_app.app_context():
            user_data = {
                'email': 'newuser@test.com',
                'password': 'NewPass123!',
                'first_name': 'New',
                'last_name': 'User',
                'tenant_id': test_tenant.id
            }
            
            user = AuthService.register(user_data)
            
            assert user is not None
            assert user.email == 'newuser@test.com'
            assert user.verify_password('NewPass123!')
            assert user.tenant_id == test_tenant.id
    
    def test_register_duplicate_email(self, test_user, test_app):
        """Test registering with duplicate email."""
        with test_app.app_context():
            user_data = {
                'email': test_user.email,  # Duplicate email
                'password': 'NewPass123!',
                'first_name': 'Duplicate',
                'last_name': 'User'
            }
            
            with pytest.raises(ValueError):
                AuthService.register(user_data)
    
    def test_logout_user(self, test_user, test_app):
        """Test user logout."""
        with test_app.app_context():
            # First login to get tokens
            tokens = AuthService.login(test_user.email, 'password123')
            assert tokens is not None
            
            # Extract token JTI (if available)
            # Note: This test assumes logout implementation exists
            success = AuthService.logout(tokens['access_token'])
            assert success is True
    
    def test_refresh_token(self, test_user, test_app):
        """Test refreshing access token."""
        with test_app.app_context():
            # Get initial tokens
            tokens = AuthService.login(test_user.email, 'password123')
            refresh_token = tokens['refresh_token']
            
            # Refresh the access token
            new_access_token = AuthService.refresh_token(refresh_token)
            
            assert new_access_token is not None
            assert isinstance(new_access_token, str)
    
    def test_change_password(self, test_user, test_app, db_session):
        """Test changing user password."""
        with test_app.app_context():
            # Change password
            success = AuthService.change_password(test_user, 'password123', 'NewPass456!')
            assert success is True
            
            # Old password should not work
            tokens = AuthService.login(test_user.email, 'password123')
            assert tokens is None
            
            # New password should work
            tokens = AuthService.login(test_user.email, 'NewPass456!')
            assert tokens is not None
    
    def test_reset_password_request(self, test_user, test_app):
        """Test password reset request."""
        with test_app.app_context():
            # Request password reset
            reset_token = AuthService.request_password_reset(test_user.email)
            
            assert reset_token is not None
            assert isinstance(reset_token, str)
    
    def test_reset_password_complete(self, test_user, test_app):
        """Test completing password reset."""
        with test_app.app_context():
            # Request reset token
            reset_token = AuthService.request_password_reset(test_user.email)
            
            # Reset password with token
            success = AuthService.reset_password(reset_token, 'ResetPass789!')
            assert success is True
            
            # Old password should not work
            tokens = AuthService.login(test_user.email, 'password123')
            assert tokens is None
            
            # New password should work
            tokens = AuthService.login(test_user.email, 'ResetPass789!')
            assert tokens is not None
    
    def test_verify_token(self, test_user, test_app):
        """Test token verification."""
        with test_app.app_context():
            # Get tokens
            tokens = AuthService.login(test_user.email, 'password123')
            access_token = tokens['access_token']
            
            # Verify valid token
            is_valid = AuthService.verify_token(access_token)
            assert is_valid is True
            
            # Verify invalid token
            is_valid = AuthService.verify_token('invalid-token')
            assert is_valid is False
    
    def test_get_current_user(self, test_user, test_app):
        """Test getting current user from token."""
        with test_app.app_context():
            # Get tokens
            tokens = AuthService.login(test_user.email, 'password123')
            access_token = tokens['access_token']
            
            # Get user from token
            current_user = AuthService.get_current_user(access_token)
            
            assert current_user is not None
            assert current_user.id == test_user.id
            assert current_user.email == test_user.email