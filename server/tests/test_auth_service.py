import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app, db
from app.models import User, TokenBlocklist
from app.services.auth_service import AuthService


class TestAuthService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create test user
        self.test_user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True
        )
        self.test_user.password = 'password123'
        db.session.add(self.test_user)
        db.session.commit()
        
        self.auth_service = AuthService()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_success(self):
        """Test successful login"""
        result = self.auth_service.login('test@example.com', 'password123')
        
        assert result is not None
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert 'token_type' in result
        assert result['token_type'] == 'bearer'
        assert result['expires_in'] == 3600
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        result = self.auth_service.login('test@example.com', 'wrongpassword')
        assert result is None
    
    def test_login_user_not_found(self):
        """Test login with non-existent user"""
        result = self.auth_service.login('nonexistent@example.com', 'password123')
        assert result is None
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.test_user.is_active = False
        db.session.commit()
        
        result = self.auth_service.login('test@example.com', 'password123')
        assert result is None
    
    @patch('app.services.email_service.send_welcome_email')
    def test_register_success(self, mock_send_email):
        """Test successful user registration"""
        result = self.auth_service.register(
            email='newuser@example.com',
            password='password123',
            first_name='New',
            last_name='User',
            role='student'
        )
        
        assert result is not None
        assert isinstance(result, User)
        assert result.email == 'newuser@example.com'
        assert result.first_name == 'New'
        assert result.last_name == 'User'
        assert result.role == 'student'
        
        # Check user was created in database
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.verify_password('password123')
        
        # Check email was sent
        mock_send_email.assert_called_once_with(result)
    
    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        result = self.auth_service.register(
            email='test@example.com',
            password='password123',
            first_name='Another',
            last_name='User',
            role='student'
        )
        
        # Should return None due to database constraint
        assert result is None
    
    def test_logout_success(self):
        """Test successful logout"""
        # Create a mock token
        token = {
            'jti': 'test-jti',
            'type': 'access',
            'sub': str(self.test_user.id),
            'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        
        result = self.auth_service.logout(token)
        
        assert result is True
        
        # Check token was blacklisted
        blacklisted = TokenBlocklist.query.filter_by(jti='test-jti').first()
        assert blacklisted is not None
        assert blacklisted.token_type == 'access'
        assert blacklisted.user_id == self.test_user.id
    
    def test_logout_failure(self):
        """Test logout failure"""
        # Create a mock token without proper data
        token = {
            'jti': None,  # Invalid jti
            'type': 'access',
            'sub': str(self.test_user.id),
            'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        
        result = self.auth_service.logout(token)
        
        assert result is False
    
    @patch('app.services.email_service.send_password_reset_email')
    def test_request_password_reset_success(self, mock_send_email):
        """Test successful password reset request"""
        mock_send_email.return_value = True
        
        result = self.auth_service.request_password_reset('test@example.com')
        
        assert result is True
        mock_send_email.assert_called_once()
    
    def test_request_password_reset_user_not_found(self):
        """Test password reset for non-existent user"""
        result = self.auth_service.request_password_reset('nonexistent@example.com')
        assert result is False
    
    @patch('app.services.email_service.verify_email_token')
    def test_reset_password_success(self, mock_verify_token):
        """Test successful password reset"""
        # Mock token verification
        mock_verify_token.return_value = {'user_id': self.test_user.id}
        
        result = self.auth_service.reset_password('valid-token', 'newpassword123')
        
        assert result is True
        
        # Check password was changed
        user = User.query.get(self.test_user.id)
        assert user.verify_password('newpassword123')
    
    @patch('app.services.email_service.verify_email_token')
    def test_reset_password_invalid_token(self, mock_verify_token):
        """Test password reset with invalid token"""
        # Mock token verification failure
        mock_verify_token.return_value = None
        
        result = self.auth_service.reset_password('invalid-token', 'newpassword123')
        
        assert result is False
    
    @patch('app.services.email_service.verify_email_token')
    def test_reset_password_user_not_found(self, mock_verify_token):
        """Test password reset with valid token but non-existent user"""
        # Mock token verification with non-existent user
        mock_verify_token.return_value = {'user_id': 999999}
        
        result = self.auth_service.reset_password('valid-token', 'newpassword123')
        
        assert result is False
    
    def test_register_with_tenant(self):
        """Test registration with tenant assignment"""
        from app.models import Tenant
        
        # Create a test tenant
        tenant = Tenant(
            name='Test Tenant',
            slug='test-tenant',
            email='tenant@test.com',
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
        
        with patch('app.services.email_service.send_welcome_email'):
            result = self.auth_service.register(
                email='tenant_user@example.com',
                password='password123',
                first_name='Tenant',
                last_name='User',
                role='student',
                tenant_id=tenant.id
            )
        
        assert result is not None
        assert tenant in result.tenants
    
    def test_last_login_update(self):
        """Test that last login time is updated on successful login"""
        # Get initial last_login
        initial_last_login = self.test_user.last_login
        
        # Login
        result = self.auth_service.login('test@example.com', 'password123')
        
        assert result is not None
        
        # Refresh user from database
        user = User.query.get(self.test_user.id)
        assert user.last_login is not None
        assert user.last_login > initial_last_login if initial_last_login else True