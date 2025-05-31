"""Comprehensive tests for the refactored UserService with dependency injection."""

import os
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from io import BytesIO

from sqlalchemy.orm import Session
from werkzeug.datastructures import FileStorage
from passlib.context import CryptContext

from app.services.user_service_refactored import (
    UserServiceRefactored, UserRole, UserStatus, PaginationResult
)
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.test import TestSet
from app.models.document import Document
from app.exceptions import NotFoundException, ValidationException, ForbiddenException


@pytest.fixture
def db_session():
    """Create a mock database session."""
    session = Mock(spec=Session)
    session.query.return_value = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.refresh = Mock()
    return session


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repository = Mock()
    repository.get_by_id = Mock()
    repository.get_by_email = Mock()
    repository.create = Mock()
    repository.update = Mock()
    repository.get_all = Mock()
    return repository


@pytest.fixture
def mock_beneficiary_repository():
    """Create a mock beneficiary repository."""
    repository = Mock()
    repository.get_by_caregiver_id = Mock()
    return repository


@pytest.fixture
def user_service(db_session, mock_user_repository, mock_beneficiary_repository):
    """Create UserService instance with mocked dependencies."""
    return UserServiceRefactored(
        db_session=db_session,
        user_repository=mock_user_repository,
        beneficiary_repository=mock_beneficiary_repository,
        upload_folder='/tmp/test_uploads'
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(
        id=1,
        email='test@example.com',
        password='hashed_password',
        first_name='John',
        last_name='Doe',
        role='trainer',
        phone='1234567890',
        organization='Test Org',
        tenant_id=1,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return user


@pytest.fixture
def pwd_context():
    """Create password context for testing."""
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestUserServiceRefactored:
    """Test cases for refactored UserService."""
    
    def test_create_user_success(self, user_service, db_session):
        """Test successful user creation."""
        # Arrange
        user_data = {
            'email': 'new@example.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'trainer',
            'phone': '0987654321',
            'organization': 'New Org',
            'tenant_id': 1
        }
        
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        result = user_service.create_user(user_data)
        
        # Assert
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
        
        # Verify user was created with correct data
        created_user = db_session.add.call_args[0][0]
        assert created_user.email == user_data['email']
        assert created_user.first_name == user_data['first_name']
        assert created_user.is_active is True
    
    def test_create_user_already_exists(self, user_service, db_session, sample_user):
        """Test user creation when user already exists."""
        # Arrange
        user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'trainer',
            'tenant_id': 1
        }
        
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act & Assert
        with pytest.raises(ValidationException, match="User with this email already exists"):
            user_service.create_user(user_data)
        
        db_session.rollback.assert_called_once()
    
    def test_create_user_invalid_role(self, user_service, db_session):
        """Test user creation with invalid role."""
        # Arrange
        user_data = {
            'email': 'new@example.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'invalid_role',
            'tenant_id': 1
        }
        
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValidationException, match="Invalid role"):
            user_service.create_user(user_data)
        
        db_session.rollback.assert_called_once()
    
    def test_get_user_by_id(self, user_service, db_session, sample_user):
        """Test getting a user by ID."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.get_user(1)
        
        # Assert
        assert result['email'] == sample_user.email
        assert result['id'] == sample_user.id
        db_session.query.assert_called_with(User)
    
    def test_get_user_not_found(self, user_service, db_session):
        """Test getting a non-existent user."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        result = user_service.get_user(999)
        
        # Assert
        assert result is None
    
    def test_get_user_by_email(self, user_service, db_session, sample_user):
        """Test getting a user by email."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.get_user_by_email('test@example.com')
        
        # Assert
        assert result['email'] == sample_user.email
        db_session.query.assert_called_with(User)
    
    def test_update_user(self, user_service, db_session, sample_user):
        """Test updating a user."""
        # Arrange
        user_update = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '5555555555'
        }
        
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.update_user(1, user_update)
        
        # Assert
        assert sample_user.first_name == 'Updated'
        assert sample_user.last_name == 'Name'
        assert sample_user.phone == '5555555555'
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
    
    def test_update_user_with_password(self, user_service, db_session, sample_user):
        """Test updating a user with password change."""
        # Arrange
        user_update = {
            'first_name': 'Updated',
            'password': 'new_password123'
        }
        
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.update_user(1, user_update)
        
        # Assert
        assert sample_user.first_name == 'Updated'
        # Password should be set to something (the hash)
        assert hasattr(sample_user, 'password_hash')
        # The service should have called the hash method
        assert result is not None
        db_session.commit.assert_called_once()
    
    def test_update_user_not_found(self, user_service, db_session):
        """Test updating a non-existent user."""
        # Arrange
        user_update = {'first_name': 'Updated'}
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            user_service.update_user(999, user_update)
        
        db_session.rollback.assert_called_once()
    
    def test_delete_user(self, user_service, db_session, sample_user):
        """Test deleting a user (soft delete)."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.delete_user(1)
        
        # Assert
        assert result is True
        assert sample_user.is_active is False
        db_session.commit.assert_called_once()
    
    def test_delete_user_not_found(self, user_service, db_session):
        """Test deleting a non-existent user."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        result = user_service.delete_user(999)
        
        # Assert
        assert result is False
        db_session.commit.assert_not_called()
    
    def test_verify_password(self, user_service):
        """Test password verification."""
        # Test with actual bcrypt hashing
        plain_password = 'test_password_123'
        hashed_password = user_service.pwd_context.hash(plain_password)
        
        # Verify correct password
        assert user_service.verify_password(plain_password, hashed_password) is True
        
        # Verify incorrect password
        assert user_service.verify_password('wrong_password', hashed_password) is False
    
    def test_authenticate_user_success(self, user_service, db_session, sample_user, pwd_context):
        """Test successful user authentication."""
        # Arrange
        sample_user.password_hash = pwd_context.hash('password123')
        sample_user.is_active = True
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.authenticate_user('test@example.com', 'password123')
        
        # Assert
        assert result == sample_user
        assert sample_user.last_login is not None
        db_session.commit.assert_called_once()
    
    def test_authenticate_user_wrong_password(self, user_service, db_session, sample_user):
        """Test failed authentication due to wrong password."""
        # Arrange
        sample_user.password_hash = user_service.pwd_context.hash('correct_password')
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.authenticate_user('test@example.com', 'wrong_password')
        
        # Assert
        assert result is None
    
    def test_authenticate_user_inactive(self, user_service, db_session, sample_user):
        """Test authentication for inactive user."""
        # Arrange
        sample_user.is_active = False
        sample_user.password_hash = user_service.pwd_context.hash('password123')
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.authenticate_user('test@example.com', 'password123')
        
        # Assert
        assert result is None
    
    def test_authenticate_user_not_found(self, user_service, db_session):
        """Test authentication for non-existent user."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        result = user_service.authenticate_user('nonexistent@example.com', 'password')
        
        # Assert
        assert result is None
    
    def test_update_user_password_success(self, user_service, db_session, sample_user):
        """Test updating a user's password."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        new_password = 'new_secure_password123'
        
        # Act
        result = user_service.update_user_password(1, new_password)
        
        # Assert
        assert result is True
        assert user_service.pwd_context.verify(new_password, sample_user.password_hash)
        db_session.commit.assert_called_once()
    
    def test_update_user_password_too_short(self, user_service, db_session, sample_user):
        """Test updating password with too short password."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act & Assert
        with pytest.raises(ValidationException, match="Password must be at least 8 characters"):
            user_service.update_user_password(1, 'short')
        
        db_session.rollback.assert_called_once()
    
    def test_get_current_user(self, user_service, db_session, sample_user):
        """Test getting current user profile."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service.get_current_user(1)
        
        # Assert
        assert result is not None
        assert result['email'] == sample_user.email
    
    def test_get_users_with_filters(self, user_service, db_session):
        """Test getting users with filters and pagination."""
        # Arrange
        users = [
            User(id=1, email='user1@example.com', role='trainer', is_active=True),
            User(id=2, email='user2@example.com', role='admin', is_active=True)
        ]
        
        query_mock = Mock()
        query_mock.filter_by.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.count.return_value = 2
        query_mock.offset.return_value.limit.return_value.all.return_value = users
        
        db_session.query.return_value = query_mock
        
        # Act
        result = user_service.get_users(
            page=1,
            per_page=10,
            role='trainer',
            is_active=True,
            sort_by='created_at',
            sort_direction='desc'
        )
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert len(result.items) == 2
        assert result.total == 2
        assert result.current_page == 1
        query_mock.filter_by.assert_called()
    
    def test_get_users_with_status_filter(self, user_service, db_session):
        """Test getting users with status filter."""
        # Arrange
        query_mock = Mock()
        query_mock.filter_by.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.count.return_value = 0
        query_mock.offset.return_value.limit.return_value.all.return_value = []
        
        db_session.query.return_value = query_mock
        
        # Act
        result = user_service.get_users(status='active')
        
        # Assert
        # Should filter by is_active=True
        query_mock.filter_by.assert_any_call(is_active=True)
    
    def test_get_user_profile_trainer(self, user_service, db_session, sample_user):
        """Test getting user profile for a trainer."""
        # Arrange
        sample_user.role = 'trainer'
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Mock appointment count
        appointment_query = Mock()
        appointment_query.count.return_value = 5
        
        # Mock evaluation count
        evaluation_query = Mock()
        evaluation_query.count.return_value = 3
        
        # Mock document count
        document_query = Mock()
        document_query.count.return_value = 10
        
        # Setup query mocking for different models
        def query_side_effect(model):
            if model == User:
                return Mock(filter_by=lambda **kwargs: Mock(first=lambda: sample_user))
            elif model == Appointment:
                return Mock(filter_by=lambda **kwargs: appointment_query)
            elif model == TestSet:
                return Mock(filter_by=lambda **kwargs: evaluation_query)
            elif model == Document:
                return Mock(filter_by=lambda **kwargs: document_query)
            return Mock()
        
        db_session.query.side_effect = query_side_effect
        
        # Act
        result = user_service.get_user_profile(1)
        
        # Assert
        assert result is not None
        assert result['stats']['appointments_count'] == 5
        assert result['stats']['evaluations_count'] == 3
        assert result['stats']['documents_count'] == 10
    
    def test_get_user_profile_caregiver(self, user_service, db_session, sample_user):
        """Test getting user profile for a caregiver."""
        # Arrange
        sample_user.role = 'caregiver'
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Mock beneficiary repository
        mock_beneficiaries = [Mock(), Mock()]  # 2 beneficiaries
        user_service.beneficiary_repository.get_by_caregiver_id.return_value = mock_beneficiaries
        
        # Mock document count
        document_query = Mock()
        document_query.count.return_value = 0
        
        # Setup query mocking
        def query_side_effect(model):
            if model == User:
                return Mock(filter_by=lambda **kwargs: Mock(first=lambda: sample_user))
            elif hasattr(model, '__name__') and model.__name__ == 'Document':
                return Mock(filter_by=lambda **kwargs: document_query)
            return Mock()
        
        db_session.query.side_effect = query_side_effect
        
        # Act
        result = user_service.get_user_profile(1)
        
        # Assert
        assert result is not None
        assert result['stats']['beneficiaries_count'] == 2
    
    def test_update_user_profile(self, user_service, db_session, sample_user):
        """Test updating user profile."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Profile',
            'phone': '9999999999',
            'bio': 'Updated bio',
            'timezone': 'UTC',
            'email_notifications': False
        }
        
        # Act
        result = user_service.update_user_profile(1, update_data)
        
        # Assert
        assert sample_user.first_name == 'Updated'
        assert sample_user.last_name == 'Profile'
        assert sample_user.phone == '9999999999'
        assert sample_user.bio == 'Updated bio'
        db_session.commit.assert_called_once()
    
    def test_update_user_profile_not_found(self, user_service, db_session):
        """Test updating profile for non-existent user."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            user_service.update_user_profile(999, {'first_name': 'Test'})
        
        db_session.rollback.assert_called_once()
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_upload_profile_picture_success(self, mock_makedirs, mock_exists, 
                                          user_service, db_session, sample_user):
        """Test successful profile picture upload."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        mock_exists.return_value = False
        
        # Create a mock file
        file = MagicMock(spec=FileStorage)
        file.filename = 'profile.jpg'
        file.seek = MagicMock()
        file.tell = MagicMock(return_value=1024 * 1024)  # 1MB
        file.save = MagicMock()
        
        # Act
        result = user_service.upload_profile_picture(1, file)
        
        # Assert
        assert 'message' in result
        assert 'profile_picture' in result
        assert result['message'] == 'Profile picture uploaded successfully'
        assert sample_user.profile_picture is not None
        file.save.assert_called_once()
        db_session.commit.assert_called_once()
    
    def test_upload_profile_picture_no_file(self, user_service, db_session, sample_user):
        """Test profile picture upload with no file."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act & Assert
        with pytest.raises(ValidationException, match="No file provided"):
            user_service.upload_profile_picture(1, None)
        
        db_session.rollback.assert_called_once()
    
    def test_upload_profile_picture_invalid_type(self, user_service, db_session, sample_user):
        """Test profile picture upload with invalid file type."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Create a mock file with invalid extension
        file = MagicMock(spec=FileStorage)
        file.filename = 'profile.txt'
        file.seek = MagicMock()
        file.tell = MagicMock()
        
        # Act & Assert
        with pytest.raises(ValidationException, match="Invalid file type"):
            user_service.upload_profile_picture(1, file)
        
        db_session.rollback.assert_called_once()
    
    def test_upload_profile_picture_too_large(self, user_service, db_session, sample_user):
        """Test profile picture upload with file too large."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Create a mock file that's too large
        file = MagicMock(spec=FileStorage)
        file.filename = 'profile.jpg'
        file.seek = MagicMock()
        file.tell = MagicMock(return_value=10 * 1024 * 1024)  # 10MB
        
        # Act & Assert
        with pytest.raises(ValidationException, match="File too large"):
            user_service.upload_profile_picture(1, file)
        
        db_session.rollback.assert_called_once()
    
    def test_allowed_file(self, user_service):
        """Test the allowed file checker."""
        # Test valid extensions
        assert user_service._allowed_file('image.jpg') is True
        assert user_service._allowed_file('photo.png') is True
        assert user_service._allowed_file('avatar.gif') is True
        assert user_service._allowed_file('picture.jpeg') is True
        assert user_service._allowed_file('IMAGE.JPG') is True  # Case insensitive
        
        # Test invalid extensions
        assert user_service._allowed_file('document.pdf') is False
        assert user_service._allowed_file('script.js') is False
        assert user_service._allowed_file('noextension') is False
        assert user_service._allowed_file('') is False
    
    def test_get_user_or_404_found(self, user_service, db_session, sample_user):
        """Test helper method when user is found."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service._get_user_or_404(1)
        
        # Assert
        assert result == sample_user
    
    def test_get_user_or_404_not_found(self, user_service, db_session):
        """Test helper method when user is not found."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundException, match="User with ID 999 not found"):
            user_service._get_user_or_404(999)
    
    def test_get_user_by_email_helper(self, user_service, db_session, sample_user):
        """Test helper method for getting user by email."""
        # Arrange
        db_session.query.return_value.filter_by.return_value.first.return_value = sample_user
        
        # Act
        result = user_service._get_user_by_email('test@example.com')
        
        # Assert
        assert result == sample_user
    
    def test_get_user_statistics_comprehensive(self, user_service, db_session, sample_user):
        """Test comprehensive statistics generation."""
        # Arrange
        sample_user.role = 'trainer'
        
        # Setup complex query mocking
        appointment_query = Mock()
        appointment_query.count.return_value = 15
        
        evaluation_query = Mock()
        evaluation_query.count.return_value = 8
        
        document_query = Mock()
        document_query.count.return_value = 25
        
        def query_side_effect(model):
            if model == Appointment:
                return Mock(filter_by=lambda **kwargs: appointment_query)
            elif model == TestSet:
                return Mock(filter_by=lambda **kwargs: evaluation_query)
            elif model == Document:
                return Mock(filter_by=lambda **kwargs: document_query)
            return Mock()
        
        db_session.query.side_effect = query_side_effect
        
        # Act
        result = user_service._get_user_statistics(sample_user)
        
        # Assert
        assert result['appointments_count'] == 15
        assert result['evaluations_count'] == 8
        assert result['documents_count'] == 25