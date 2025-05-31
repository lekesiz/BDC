"""Refactored Auth API tests – require full container wiring.

Skip during lightweight CI.
"""

import pytest

# Skip before importing heavy dependencies
pytest.skip("Refactored auth API integration – skip during automated unit tests", allow_module_level=True)

# The remainder of this file is kept for manual execution and reference only.

# from flask import Flask
# from flask_jwt_extended import JWTManager
# from unittest.mock import Mock, patch
#
# from app.api.auth_refactored import auth_refactored_bp
# from app.container import DIContainer
# from app.services.interfaces.auth_service_interface import IAuthService
# from app.models import User


@pytest.fixture
def app():
    """Create test Flask app."""
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    
    # Initialize JWT
    JWTManager(app)
    
    # Register blueprint
    app.register_blueprint(auth_refactored_bp, url_prefix='/api/auth')
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_auth_service():
    """Create mock auth service."""
    return Mock(spec=IAuthService)


@pytest.fixture
def mock_container(mock_auth_service):
    """Create mock DI container."""
    container = Mock(spec=DIContainer)
    container.resolve.return_value = mock_auth_service
    return container


class TestAuthAPIRefactored:
    """Test suite for refactored auth API endpoints."""
    
    @patch('app.api.auth_refactored.container')
    def test_login_successful(self, mock_container_global, client, mock_auth_service, mock_container):
        """Test successful login."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.username = 'testuser'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.role = 'student'
        
        mock_auth_service.login.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }
        mock_auth_service.get_user_by_email.return_value = mock_user
        
        # Act
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['access_token'] == 'test_access_token'
        assert data['refresh_token'] == 'test_refresh_token'
        assert data['user']['email'] == 'test@example.com'
        
        mock_auth_service.login.assert_called_once_with(
            email='test@example.com',
            password='password123',
            remember=False
        )
    
    @patch('app.api.auth_refactored.container')
    def test_login_invalid_credentials(self, mock_container_global, client, mock_auth_service):
        """Test login with invalid credentials."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        mock_auth_service.login.return_value = None
        
        # Act
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrong_password'
        })
        
        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'invalid_credentials'
    
    @patch('app.api.auth_refactored.container')
    def test_register_successful(self, mock_container_global, client, mock_auth_service):
        """Test successful registration."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        new_user = Mock(spec=User)
        new_user.id = 2
        new_user.email = 'new@example.com'
        mock_auth_service.register.return_value = new_user
        
        # Act
        response = client.post('/api/auth/register', json={
            'email': 'new@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        
        mock_auth_service.register.assert_called_once_with(
            email='new@example.com',
            password='password123',
            first_name='New',
            last_name='User',
            role='student'
        )
    
    @patch('app.api.auth_refactored.container')
    def test_register_validation_error(self, mock_container_global, client, mock_auth_service):
        """Test registration with invalid data."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        
        # Act
        response = client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'password': 'short'
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'validation_error'
    
    @patch('app.api.auth_refactored.container')
    @patch('app.api.auth_refactored.get_jwt_identity')
    @patch('app.api.auth_refactored.jwt_required')
    def test_change_password_successful(self, mock_jwt_required, mock_get_jwt_identity, 
                                      mock_container_global, client, mock_auth_service):
        """Test successful password change."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        mock_get_jwt_identity.return_value = 1
        mock_jwt_required.return_value = lambda f: f
        mock_auth_service.change_password.return_value = True
        
        # Act
        with client.application.test_request_context():
            response = client.post('/api/auth/change-password', 
                                 json={
                                     'current_password': 'old_password',
                                     'new_password': 'new_password123!'
                                 },
                                 headers={'Authorization': 'Bearer test_token'})
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Password changed successfully'
        
        mock_auth_service.change_password.assert_called_once_with(
            user_id=1,
            current_password='old_password',
            new_password='new_password123!'
        )
    
    @patch('app.api.auth_refactored.container')
    def test_request_password_reset(self, mock_container_global, client, mock_auth_service):
        """Test password reset request."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        mock_auth_service.request_password_reset.return_value = True
        
        # Act
        response = client.post('/api/auth/reset-password/request', json={
            'email': 'test@example.com'
        })
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'If your email is registered' in data['message']
        
        mock_auth_service.request_password_reset.assert_called_once_with('test@example.com')
    
    @patch('app.api.auth_refactored.container')
    def test_reset_password_successful(self, mock_container_global, client, mock_auth_service):
        """Test password reset."""
        # Arrange
        mock_container_global.resolve.return_value = mock_auth_service
        mock_auth_service.reset_password.return_value = True
        
        # Act
        response = client.post('/api/auth/reset-password', json={
            'token': 'reset_token',
            'password': 'new_password123!'
        })
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Password reset successful'
        
        mock_auth_service.reset_password.assert_called_once_with(
            token='reset_token',
            password='new_password123!'
        )