"""Tests for authentication service."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token, decode_token
from app.models import User, TokenBlocklist
from app.services.auth_service import AuthService
from app.extensions import db
from werkzeug.security import generate_password_hash

@pytest.fixture
def auth_service():
    """Create auth service instance."""
    return AuthService()


@pytest.fixture
def setup_auth_data(session, app):
    """Setup test data for auth service tests."""
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True,
            role='user',
            tenant_id=1
        )
        user.password = 'password123'
        
        # Create inactive user
        inactive_user = User(
            username='inactiveuser',
            email='inactive@example.com',
            first_name='Inactive',
            last_name='User',
            is_active=False,
            role='user',
            tenant_id=1
        )
        inactive_user.password = 'password123'
        
        session.add_all([user, inactive_user])
        session.commit()
        
        # Refresh to ensure they're properly attached to the session
        session.refresh(user)
        session.refresh(inactive_user)
        
        # Get the IDs before closing the session
        user_id = user.id
        inactive_user_id = inactive_user.id
        
        return {
            'user': user,
            'inactive_user': inactive_user,
            'user_id': user_id,
            'inactive_user_id': inactive_user_id
        }


@patch('app.services.email_service.send_welcome_email')
def test_register_user(mock_send_email, auth_service, session, app):
    """Test user registration."""
    with app.app_context():
        user = auth_service.register(
            email='newuser@example.com',
            password='SecurePassword123!',
            first_name='New',
            last_name='User',
            role='user'
        )
        
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.role == 'user'
        mock_send_email.assert_called_once()


@patch('app.services.email_service.send_welcome_email')
def test_register_duplicate_email(mock_send_email, auth_service, setup_auth_data, session, app):
    """Test registration with duplicate email."""
    with app.app_context():
        user = auth_service.register(
            email='test@example.com',  # Already exists
            password='SecurePassword123!',
            first_name='Another',
            last_name='User',
            role='user'
        )
        
        assert user is None


def test_login_success(auth_service, setup_auth_data, app):
    """Test successful login."""
    with app.app_context():
        result = auth_service.login('test@example.com', 'password123')
        
        assert result is not None
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'bearer'


def test_login_invalid_password(auth_service, setup_auth_data, app):
    """Test login with invalid password."""
    with app.app_context():
        result = auth_service.login('test@example.com', 'wrongpassword')
        
        assert result is None


def test_login_nonexistent_user(auth_service, session, app):
    """Test login with non-existent user."""
    with app.app_context():
        result = auth_service.login('nonexistent@example.com', 'password123')
        
        assert result is None


def test_login_inactive_user(auth_service, setup_auth_data, app):
    """Test login with inactive user."""
    with app.app_context():
        result = auth_service.login('inactive@example.com', 'password123')
        
        assert result is None


def test_logout(auth_service, setup_auth_data, app):
    """Test logout."""
    with app.app_context():
        # Create a mock token
        token = {
            'jti': 'test_jti_123',
            'type': 'access',
            'sub': setup_auth_data['user_id'],
            'exp': int((datetime.utcnow().timestamp()) + 3600)
        }
        
        result = auth_service.logout(token)
        
        assert result is True


def test_change_password(auth_service, setup_auth_data, app):
    """Test password change."""
    with app.app_context():
        user_id = setup_auth_data['user_id']
        result = auth_service.change_password(
            user_id,
            'password123',
            'NewPassword123!'
        )
        
        assert result is True
        
        # Verify new password works
        login_result = auth_service.login('test@example.com', 'NewPassword123!')
        assert login_result is not None


def test_change_password_wrong_current(auth_service, setup_auth_data, app):
    """Test password change with wrong current password."""
    with app.app_context():
        user_id = setup_auth_data['user_id']
        result = auth_service.change_password(
            user_id,
            'wrongpassword',
            'NewPassword123!'
        )
        
        assert result is False


@patch('app.services.email_service.send_password_reset_email')
def test_request_password_reset(mock_send_email, auth_service, setup_auth_data, app):
    """Test password reset request."""
    with app.app_context():
        mock_send_email.return_value = True
        
        result = auth_service.request_password_reset('test@example.com')
        
        assert result is True
        mock_send_email.assert_called_once()


@patch('app.services.email_service.send_password_reset_email')
def test_request_password_reset_nonexistent_user(mock_send_email, auth_service, session, app):
    """Test password reset request for non-existent user."""
    with app.app_context():
        result = auth_service.request_password_reset('nonexistent@example.com')
        
        assert result is False
        mock_send_email.assert_not_called()


@patch('app.services.email_service.verify_email_token')
def test_reset_password(mock_verify_token, auth_service, setup_auth_data, app):
    """Test password reset."""
    with app.app_context():
        mock_verify_token.return_value = {'user_id': setup_auth_data['user_id']}
        
        result = auth_service.reset_password(
            'valid_token',
            'NewPassword123!'
        )
        
        assert result is True
        
        # Verify new password works
        login_result = auth_service.login('test@example.com', 'NewPassword123!')
        assert login_result is not None


@patch('app.services.email_service.verify_email_token')
def test_reset_password_invalid_token(mock_verify_token, auth_service, app):
    """Test password reset with invalid token."""
    with app.app_context():
        mock_verify_token.return_value = None
        
        result = auth_service.reset_password(
            'invalid_token',
            'NewPassword123!'
        )
        
        assert result is False