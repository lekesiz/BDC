"""Tests for authentication service (simple version)."""

import pytest
from app.services.auth_service import AuthService


class TestAuthServiceSimple:
    """Test authentication service methods."""
    
    def test_login_success(self, test_user, test_app):
        """Test successful user login."""
        with test_app.app_context():
            tokens = AuthService.login(test_user.email, 'password123')
            assert tokens is not None
            assert 'access_token' in tokens
            assert 'refresh_token' in tokens
    
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