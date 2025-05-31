"""Comprehensive tests for User model."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from werkzeug.security import generate_password_hash
from app.models.user import User, UserRole, TokenBlocklist
from app.extensions import db


class TestUserRole:
    """Test the UserRole class."""
    
    def test_user_roles(self):
        """Test UserRole constants."""
        assert UserRole.SUPER_ADMIN == 'super_admin'
        assert UserRole.TENANT_ADMIN == 'tenant_admin'
        assert UserRole.TRAINER == 'trainer'
        assert UserRole.STUDENT == 'student'
        assert UserRole.TRAINEE == 'trainee'
    
    def test_roles_list(self):
        """Test ROLES list contains all roles."""
        expected_roles = ['super_admin', 'tenant_admin', 'trainer', 'student', 'trainee']
        assert UserRole.ROLES == expected_roles


class TestUserModel:
    """Test the User model."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        user = User(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            role=UserRole.STUDENT,
            tenant_id=1
        )
        user.password = 'password123'
        return user
    
    def test_user_creation(self, user):
        """Test user creation with basic fields."""
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.role == 'student'
        assert user.is_active is True
        assert user.tenant_id == 1
    
    def test_full_name_property(self, user):
        """Test full_name property."""
        assert user.full_name == 'Test User'
    
    def test_password_setter(self, user):
        """Test password setter creates hash."""
        assert user.password_hash is not None
        assert user.password_hash != 'password123'
        assert user.password_hash.startswith('pbkdf2:sha256:') or user.password_hash.startswith('scrypt:')
    
    def test_password_getter(self, user):
        """Test password getter raises AttributeError."""
        with pytest.raises(AttributeError, match='password is not a readable attribute'):
            _ = user.password
    
    def test_verify_password(self, user):
        """Test password verification."""
        assert user.verify_password('password123') is True
        assert user.verify_password('wrongpassword') is False
    
    def test_to_dict_basic(self, user):
        """Test to_dict method without profile."""
        user_dict = user.to_dict()
        
        assert user_dict['id'] == user.id
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['username'] == 'testuser'
        assert user_dict['first_name'] == 'Test'
        assert user_dict['last_name'] == 'User'
        assert user_dict['full_name'] == 'Test User'
        assert user_dict['role'] == 'student'
        assert user_dict['tenant_id'] == 1
        assert user_dict['is_active'] is True
        assert user_dict['last_login'] is None
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict
        
        # Profile fields should not be included
        assert 'phone' not in user_dict
        assert 'address' not in user_dict
    
    def test_to_dict_with_profile(self, user):
        """Test to_dict method with profile."""
        user.phone = '+1234567890'
        user.address = '123 Test St'
        user.city = 'Test City'
        user.state = 'TS'
        user.zip_code = '12345'
        user.country = 'Test Country'
        user.organization = 'Test Org'
        user.bio = 'Test bio'
        user.profile_picture = 'test.jpg'
        
        user_dict = user.to_dict(include_profile=True)
        
        # Basic fields
        assert user_dict['email'] == 'test@example.com'
        
        # Profile fields
        assert user_dict['phone'] == '+1234567890'
        assert user_dict['address'] == '123 Test St'
        assert user_dict['city'] == 'Test City'
        assert user_dict['state'] == 'TS'
        assert user_dict['zip_code'] == '12345'
        assert user_dict['country'] == 'Test Country'
        assert user_dict['organization'] == 'Test Org'
        assert user_dict['bio'] == 'Test bio'
        assert user_dict['profile_picture'] == 'test.jpg'
    
    def test_to_dict_with_last_login(self, user):
        """Test to_dict with last_login set."""
        last_login = datetime(2023, 1, 1, 12, 0, 0)
        user.last_login = last_login
        
        user_dict = user.to_dict()
        assert user_dict['last_login'] == '2023-01-01T12:00:00'
    
    def test_repr(self, user):
        """Test string representation."""
        assert repr(user) == '<User test@example.com>'
    
    def test_default_preferences(self, user):
        """Test default preference values."""
        assert user.email_notifications is True
        assert user.push_notifications is False
        assert user.sms_notifications is False
        assert user.language == 'en'
        assert user.theme == 'light'
    
    def test_relationships(self, user):
        """Test model relationships are defined."""
        # Check that relationships exist (they'll be None/empty without database)
        assert hasattr(user, 'tenants')
        assert hasattr(user, 'folders')
        assert hasattr(user, 'reports')
        assert hasattr(user, 'programs_created')
        assert hasattr(user, 'training_sessions')
    
    @pytest.fixture
    def db_session(self):
        """Create a database session for testing."""
        # This would be mocked in unit tests
        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.query = Mock()
        return session
    
    def test_user_with_db_operations(self, db_session):
        """Test user with database operations."""
        user = User(
            email='db_test@example.com',
            first_name='DB',
            last_name='Test',
            role=UserRole.TRAINER
        )
        user.password = 'testpass'
        
        db_session.add(user)
        db_session.commit()
        
        assert db_session.add.called
        assert db_session.commit.called


class TestTokenBlocklist:
    """Test the TokenBlocklist model."""
    
    @pytest.fixture
    def token_entry(self):
        """Create a test token blocklist entry."""
        expires_at = datetime(2024, 1, 1, 12, 0, 0)
        return TokenBlocklist(
            jti='test-jti-123',
            token_type='access',
            user_id=1,
            expires_at=expires_at
        )
    
    def test_token_blocklist_creation(self, token_entry):
        """Test token blocklist entry creation."""
        assert token_entry.jti == 'test-jti-123'
        assert token_entry.token_type == 'access'
        assert token_entry.user_id == 1
        assert token_entry.expires_at == datetime(2024, 1, 1, 12, 0, 0)
        assert isinstance(token_entry.revoked_at, datetime)
    
    def test_token_blocklist_to_dict(self, token_entry):
        """Test token blocklist to_dict method."""
        token_dict = token_entry.to_dict()
        
        assert token_dict['jti'] == 'test-jti-123'
        assert token_dict['token_type'] == 'access'
        assert token_dict['user_id'] == 1
        assert token_dict['expires_at'] == '2024-01-01T12:00:00'
        assert 'revoked_at' in token_dict
        assert 'id' in token_dict
    
    def test_token_blocklist_defaults(self):
        """Test token blocklist default values."""
        token = TokenBlocklist(
            jti='minimal-jti',
            token_type='refresh',
            user_id=2,
            expires_at=datetime.now()
        )
        
        # revoked_at should be set automatically
        assert token.revoked_at is not None
        assert isinstance(token.revoked_at, datetime)