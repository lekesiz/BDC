"""Tests for refactored auth service demonstrating improved testability."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.auth_service_refactored import AuthServiceRefactored
from app.services.interfaces.user_repository_interface import IUserRepository
from app.models import User


class TestAuthServiceRefactored:
    """Test suite for refactored authentication service."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return Mock(spec=IUserRepository)
    
    @pytest.fixture
    def auth_service(self, mock_user_repository):
        """Create auth service with mocked dependencies."""
        return AuthServiceRefactored(mock_user_repository)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = 1
        user.email = 'test@example.com'
        user.role = 'student'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.verify_password = Mock(return_value=True)
        return user
    
    def test_login_successful(self, auth_service, mock_user_repository, mock_user):
        """Test successful login."""
        # Arrange
        mock_user_repository.find_by_email.return_value = mock_user
        
        # Act
        result = auth_service.login('test@example.com', 'password123')
        
        # Assert
        assert result is not None
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['expires_in'] == 3600
        assert result['user']['email'] == 'test@example.com'
        
        mock_user_repository.find_by_email.assert_called_once_with('test@example.com')
        mock_user.verify_password.assert_called_once_with('password123')
    
    def test_login_invalid_credentials(self, auth_service, mock_user_repository, mock_user):
        """Test login with invalid credentials."""
        # Arrange
        mock_user.verify_password.return_value = False
        mock_user_repository.find_by_email.return_value = mock_user
        
        # Act
        result = auth_service.login('test@example.com', 'wrong_password')
        
        # Assert
        assert result is None
        mock_user_repository.find_by_email.assert_called_once_with('test@example.com')
        mock_user.verify_password.assert_called_once_with('wrong_password')
    
    def test_login_user_not_found(self, auth_service, mock_user_repository):
        """Test login with non-existent user."""
        # Arrange
        mock_user_repository.find_by_email.return_value = None
        
        # Act
        result = auth_service.login('nonexistent@example.com', 'password')
        
        # Assert
        assert result is None
        mock_user_repository.find_by_email.assert_called_once_with('nonexistent@example.com')
    
    def test_register_successful(self, auth_service, mock_user_repository):
        """Test successful user registration."""
        # Arrange
        mock_user_repository.exists_by_email.return_value = False
        new_user = Mock(spec=User)
        new_user.id = 2
        new_user.email = 'new@example.com'
        mock_user_repository.create.return_value = new_user
        
        # Act
        result = auth_service.register(
            email='new@example.com',
            password='password123',
            first_name='New',
            last_name='User'
        )
        
        # Assert
        assert result == new_user
        mock_user_repository.exists_by_email.assert_called_once_with('new@example.com')
        mock_user_repository.create.assert_called_once()
        
        # Check that password was hashed
        create_args = mock_user_repository.create.call_args[1]
        assert 'password_hash' in create_args
        assert create_args['password_hash'] != 'password123'  # Should be hashed
    
    def test_register_email_already_exists(self, auth_service, mock_user_repository):
        """Test registration with existing email."""
        # Arrange
        mock_user_repository.exists_by_email.return_value = True
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.register('existing@example.com', 'password123')
        
        mock_user_repository.exists_by_email.assert_called_once_with('existing@example.com')
        mock_user_repository.create.assert_not_called()
    
    @patch('app.services.auth_service_refactored.db')
    @patch('app.services.auth_service_refactored.TokenBlocklist')
    def test_logout_successful(self, mock_blocklist, mock_db, auth_service):
        """Test successful logout."""
        # Arrange
        mock_token = Mock()
        mock_db.session = Mock()
        
        # Act
        result = auth_service.logout(1, 'test_jti')
        
        # Assert
        assert result is True
        mock_blocklist.assert_called_once()
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    def test_get_user_by_email(self, auth_service, mock_user_repository, mock_user):
        """Test getting user by email."""
        # Arrange
        mock_user_repository.find_by_email.return_value = mock_user
        
        # Act
        result = auth_service.get_user_by_email('test@example.com')
        
        # Assert
        assert result == mock_user
        mock_user_repository.find_by_email.assert_called_once_with('test@example.com')
    
    def test_get_user_by_id(self, auth_service, mock_user_repository, mock_user):
        """Test getting user by ID."""
        # Arrange
        mock_user_repository.find_by_id.return_value = mock_user
        
        # Act
        result = auth_service.get_user_by_id(1)
        
        # Assert
        assert result == mock_user
        mock_user_repository.find_by_id.assert_called_once_with(1)
    
    def test_update_last_login(self, auth_service, mock_user_repository, mock_user):
        """Test updating user's last login."""
        # Act
        auth_service.update_last_login(mock_user)
        
        # Assert
        assert isinstance(mock_user.last_login, datetime)
        mock_user_repository.save.assert_called_once_with(mock_user)
    
    def test_change_password_successful(self, auth_service, mock_user_repository, mock_user):
        """Test successful password change."""
        # Arrange
        mock_user_repository.find_by_id.return_value = mock_user
        mock_user.verify_password.return_value = True
        mock_user.set_password = Mock()
        
        # Act
        result = auth_service.change_password(1, 'current_password', 'new_password')
        
        # Assert
        assert result is True
        mock_user_repository.find_by_id.assert_called_once_with(1)
        mock_user.verify_password.assert_called_once_with('current_password')
        mock_user.set_password.assert_called_once_with('new_password')
        mock_user_repository.save.assert_called_once_with(mock_user)
    
    def test_change_password_wrong_current(self, auth_service, mock_user_repository, mock_user):
        """Test password change with wrong current password."""
        # Arrange
        mock_user_repository.find_by_id.return_value = mock_user
        mock_user.verify_password.return_value = False
        
        # Act
        result = auth_service.change_password(1, 'wrong_password', 'new_password')
        
        # Assert
        assert result is False
        mock_user.verify_password.assert_called_once_with('wrong_password')
        mock_user_repository.save.assert_not_called()
    
    def test_request_password_reset_user_exists(self, auth_service, mock_user_repository, mock_user):
        """Test password reset request for existing user."""
        # Arrange
        mock_user_repository.find_by_email.return_value = mock_user
        
        # Act
        result = auth_service.request_password_reset('test@example.com')
        
        # Assert
        assert result is True
        mock_user_repository.find_by_email.assert_called_once_with('test@example.com')
    
    def test_request_password_reset_user_not_exists(self, auth_service, mock_user_repository):
        """Test password reset request for non-existent user."""
        # Arrange
        mock_user_repository.find_by_email.return_value = None
        
        # Act
        result = auth_service.request_password_reset('nonexistent@example.com')
        
        # Assert
        assert result is True  # Should still return True to prevent email enumeration
        mock_user_repository.find_by_email.assert_called_once_with('nonexistent@example.com')
    
    def test_reset_password_not_implemented(self, auth_service):
        """Test password reset (currently not implemented)."""
        # Act
        result = auth_service.reset_password('test_token', 'new_password')
        
        # Assert
        assert result is False  # Currently returns False as not implemented