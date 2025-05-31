"""Unit tests for v2 services using dependency injection."""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from app.services.v2.auth_service import AuthServiceV2
from app.services.v2.user_service import UserServiceV2
from app.services.v2.beneficiary_service import BeneficiaryServiceV2
from app.core.security import SecurityManager
from app.models import User, Beneficiary


class TestAuthServiceV2:
    """Test AuthServiceV2 with mocked dependencies."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.user_repository = Mock()
        self.security_manager = Mock(spec=SecurityManager)
        self.db_session = Mock()
        
        self.service = AuthServiceV2(
            user_repository=self.user_repository,
            security_manager=self.security_manager,
            db_session=self.db_session
        )
    
    def test_authenticate_success(self):
        """Test successful authentication."""
        # Arrange
        test_user = Mock(spec=User)
        test_user.id = 1
        test_user.email = 'test@example.com'
        test_user.password_hash = 'hashed_password'
        test_user.is_active = True
        test_user.failed_login_attempts = 0
        
        self.user_repository.find_by_email.return_value = test_user
        self.security_manager.verify_password.return_value = True
        self.security_manager.generate_access_token.return_value = 'access_token'
        self.security_manager.generate_refresh_token.return_value = 'refresh_token'
        
        # Act
        result = self.service.authenticate('test@example.com', 'password123')
        
        # Assert
        assert result is not None
        assert result['user'] == test_user
        assert result['access_token'] == 'access_token'
        assert result['refresh_token'] == 'refresh_token'
        
        self.user_repository.find_by_email.assert_called_once_with('test@example.com')
        self.security_manager.verify_password.assert_called_once_with('password123', 'hashed_password')
        self.user_repository.update.assert_called_once_with(test_user)
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        # Arrange
        test_user = Mock(spec=User)
        test_user.is_active = True
        test_user.password_hash = 'hashed_password'
        test_user.failed_login_attempts = 0
        
        self.user_repository.find_by_email.return_value = test_user
        self.security_manager.verify_password.return_value = False
        
        # Act
        result = self.service.authenticate('test@example.com', 'wrong_password')
        
        # Assert
        assert result is None
        assert test_user.failed_login_attempts == 1
        self.user_repository.update.assert_called_once_with(test_user)
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        # Arrange
        test_user = Mock(spec=User)
        test_user.is_active = False
        
        self.user_repository.find_by_email.return_value = test_user
        
        # Act
        result = self.service.authenticate('test@example.com', 'password123')
        
        # Assert
        assert result is None
        self.security_manager.verify_password.assert_not_called()
    
    def test_register_new_user(self):
        """Test registering a new user."""
        # Arrange
        user_data = {
            'email': 'new@example.com',
            'password': 'Password123!',
            'name': 'New',
            'surname': 'User',
            'role': 'user'
        }
        
        created_user = Mock(spec=User)
        created_user.id = 1
        
        self.user_repository.find_by_email.return_value = None
        self.security_manager.hash_password.return_value = 'hashed_password'
        self.user_repository.create.return_value = created_user
        
        # Act
        result = self.service.register(user_data)
        
        # Assert
        assert result == created_user
        self.user_repository.find_by_email.assert_called_once_with('new@example.com')
        self.security_manager.hash_password.assert_called_once_with('Password123!')
        self.user_repository.create.assert_called_once()
    
    def test_register_existing_user(self):
        """Test registering with existing email."""
        # Arrange
        user_data = {'email': 'existing@example.com', 'password': 'Password123!'}
        existing_user = Mock(spec=User)
        
        self.user_repository.find_by_email.return_value = existing_user
        
        # Act
        result = self.service.register(user_data)
        
        # Assert
        assert result is None
        self.user_repository.create.assert_not_called()


class TestUserServiceV2:
    """Test UserServiceV2 with mocked dependencies."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.user_repository = Mock()
        self.security_manager = Mock(spec=SecurityManager)
        self.db_session = Mock()
        
        self.service = UserServiceV2(
            user_repository=self.user_repository,
            security_manager=self.security_manager,
            db_session=self.db_session
        )
    
    def test_create_user(self):
        """Test creating a user."""
        # Arrange
        user_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user'
        }
        
        created_user = Mock(spec=User)
        created_user.id = 1
        
        self.user_repository.find_by_email.return_value = None
        self.security_manager.hash_password.return_value = 'hashed_password'
        self.user_repository.create.return_value = created_user
        
        # Mock cache
        with patch('app.services.v2.user_service.cache'):
            # Act
            result = self.service.create_user(user_data)
        
        # Assert
        assert result == created_user
        self.security_manager.hash_password.assert_called_once_with('Password123!')
    
    def test_get_user_from_cache(self):
        """Test getting user from cache."""
        # Arrange
        user_id = 1
        cached_user = Mock(spec=User)
        
        # Mock cache
        with patch('app.services.v2.user_service.cache') as mock_cache:
            mock_cache.get.return_value = cached_user
            
            # Act
            result = self.service.get_user(user_id)
        
        # Assert
        assert result == cached_user
        self.user_repository.find_by_id.assert_not_called()
    
    def test_update_user_role(self):
        """Test updating user role."""
        # Arrange
        user_id = 1
        test_user = Mock(spec=User)
        test_user.role = 'user'
        
        self.user_repository.find_by_id.return_value = test_user
        self.user_repository.update.return_value = test_user
        
        # Mock cache
        with patch('app.services.v2.user_service.cache'):
            # Act
            result = self.service.update_user_role(user_id, 'trainer')
        
        # Assert
        assert result is True
        assert test_user.role == 'trainer'
        self.user_repository.update.assert_called_once_with(test_user)


class TestBeneficiaryServiceV2:
    """Test BeneficiaryServiceV2 with mocked dependencies."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.beneficiary_repository = Mock()
        self.db_session = Mock()
        
        self.service = BeneficiaryServiceV2(
            beneficiary_repository=self.beneficiary_repository,
            db_session=self.db_session
        )
    
    def test_create_beneficiary(self):
        """Test creating a beneficiary."""
        # Arrange
        beneficiary_data = {
            'name': 'Test',
            'surname': 'Beneficiary',
            'email': 'test@example.com',
            'status': 'active'
        }
        
        created_beneficiary = Mock(spec=Beneficiary)
        created_beneficiary.id = 1
        
        self.beneficiary_repository.find_by_email.return_value = None
        self.beneficiary_repository.find_by_national_id.return_value = None
        self.beneficiary_repository.create.return_value = created_beneficiary
        
        # Mock cache
        with patch('app.services.v2.beneficiary_service.cache'):
            # Act
            result = self.service.create_beneficiary(beneficiary_data)
        
        # Assert
        assert result == created_beneficiary
        self.beneficiary_repository.create.assert_called_once()
    
    def test_create_beneficiary_duplicate_email(self):
        """Test creating beneficiary with duplicate email."""
        # Arrange
        beneficiary_data = {'email': 'existing@example.com'}
        existing_beneficiary = Mock(spec=Beneficiary)
        
        self.beneficiary_repository.find_by_email.return_value = existing_beneficiary
        
        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            self.service.create_beneficiary(beneficiary_data)
    
    def test_search_beneficiaries(self):
        """Test searching beneficiaries with pagination."""
        # Arrange
        beneficiaries = [Mock(spec=Beneficiary) for _ in range(5)]
        self.beneficiary_repository.search.return_value = beneficiaries
        
        # Act
        result = self.service.search_beneficiaries('test', page=1, per_page=3)
        
        # Assert
        assert result['total'] == 5
        assert len(result['items']) == 3
        assert result['pages'] == 2
        self.beneficiary_repository.search.assert_called_once_with('test', None)
    
    def test_get_beneficiary_statistics(self):
        """Test getting beneficiary statistics."""
        # Arrange
        self.beneficiary_repository.count.return_value = 100
        self.beneficiary_repository.count_by_status.return_value = {
            'active': 80,
            'inactive': 20
        }
        self.beneficiary_repository.count_by_city.return_value = {
            'City1': 50,
            'City2': 30,
            'City3': 20
        }
        self.beneficiary_repository.get_active_beneficiaries.return_value = [Mock() for _ in range(80)]
        self.beneficiary_repository.get_inactive_beneficiaries.return_value = [Mock() for _ in range(20)]
        self.beneficiary_repository.get_recently_updated.return_value = [Mock() for _ in range(10)]
        
        # Mock cache
        with patch('app.services.v2.beneficiary_service.cache') as mock_cache:
            mock_cache.get.return_value = None
            
            # Act
            result = self.service.get_beneficiary_statistics()
        
        # Assert
        assert result['total'] == 100
        assert result['by_status']['active'] == 80
        assert result['by_status']['inactive'] == 20
        assert result['active'] == 80
        assert result['inactive'] == 20
        assert result['recently_updated'] == 10


# Patch import for cache
from unittest.mock import patch