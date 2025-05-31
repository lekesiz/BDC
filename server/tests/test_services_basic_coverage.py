"""
Basic service tests to improve coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app import db
from app.models import User, Beneficiary, Tenant
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.beneficiary_service import BeneficiaryService


class TestAuthServiceBasic:
    """Test AuthService basic functionality."""
    
    def test_auth_service_init(self):
        """Test AuthService initialization."""
        service = AuthService()
        assert service is not None
    
    @patch('app.services.auth_service.User')
    def test_authenticate_user(self, mock_user_class):
        """Test user authentication."""
        # Mock user
        mock_user = Mock()
        mock_user.verify_password.return_value = True
        mock_user.is_active = True
        mock_user.id = 1
        
        # Mock query
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_class.query = mock_query
        
        service = AuthService()
        result = service.authenticate('test@example.com', 'password')
        
        assert result == mock_user
        mock_query.filter_by.assert_called_with(email='test@example.com')
        mock_user.verify_password.assert_called_with('password')
    
    @patch('app.services.auth_service.User')
    def test_authenticate_invalid_password(self, mock_user_class):
        """Test authentication with invalid password."""
        mock_user = Mock()
        mock_user.verify_password.return_value = False
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_class.query = mock_query
        
        service = AuthService()
        result = service.authenticate('test@example.com', 'wrong')
        
        assert result is None
    
    @patch('app.services.auth_service.User')
    def test_authenticate_inactive_user(self, mock_user_class):
        """Test authentication with inactive user."""
        mock_user = Mock()
        mock_user.verify_password.return_value = True
        mock_user.is_active = False
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_user
        mock_user_class.query = mock_query
        
        service = AuthService()
        result = service.authenticate('test@example.com', 'password')
        
        assert result is None


class TestEmailServiceBasic:
    """Test EmailService basic functionality."""
    
    def test_email_service_init(self):
        """Test EmailService initialization."""
        with patch('app.services.email_service.Mail'):
            service = EmailService()
            assert service is not None
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    @patch('app.services.email_service.Mail')
    def test_send_email(self, mock_mail_class, mock_message_class, mock_thread_class):
        """Test sending email."""
        # Mock mail instance
        mock_mail = Mock()
        mock_mail_class.return_value = mock_mail
        
        # Mock message
        mock_message = Mock()
        mock_message_class.return_value = mock_message
        
        # Mock thread
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread
        
        service = EmailService()
        service.mail = mock_mail
        
        # Send email
        service.send_email(
            to='test@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        # Verify message was created
        mock_message_class.assert_called_once()
        
        # Verify thread was started
        mock_thread.start.assert_called_once()
    
    @patch('app.services.email_service.render_template')
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    @patch('app.services.email_service.Mail')
    def test_send_welcome_email(self, mock_mail_class, mock_message_class, 
                               mock_thread_class, mock_render):
        """Test sending welcome email."""
        mock_mail = Mock()
        mock_mail_class.return_value = mock_mail
        
        mock_message = Mock()
        mock_message_class.return_value = mock_message
        
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread
        
        mock_render.return_value = '<html>Welcome!</html>'
        
        service = EmailService()
        service.mail = mock_mail
        
        mock_user = Mock()
        mock_user.email = 'new@example.com'
        mock_user.first_name = 'John'
        
        service.send_welcome_email(mock_user)
        
        # Verify render_template was called
        mock_render.assert_called()
        
        # Verify email was sent
        mock_thread.start.assert_called_once()


class TestBeneficiaryServiceBasic:
    """Test BeneficiaryService basic functionality."""
    
    def test_beneficiary_service_init(self):
        """Test BeneficiaryService initialization."""
        service = BeneficiaryService()
        assert service is not None
    
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_get_beneficiary_by_id(self, mock_beneficiary_class):
        """Test getting beneficiary by ID."""
        mock_beneficiary = Mock()
        mock_beneficiary.id = 1
        mock_beneficiary.is_active = True
        
        mock_query = Mock()
        mock_query.get.return_value = mock_beneficiary
        mock_beneficiary_class.query = mock_query
        
        service = BeneficiaryService()
        result = service.get_by_id(1)
        
        assert result == mock_beneficiary
        mock_query.get.assert_called_with(1)
    
    @patch('app.services.beneficiary_service.db')
    @patch('app.services.beneficiary_service.User')
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_create_beneficiary(self, mock_beneficiary_class, mock_user_class, mock_db):
        """Test creating a beneficiary."""
        # Mock user creation
        mock_user = Mock()
        mock_user.id = 1
        mock_user_class.return_value = mock_user
        
        # Mock beneficiary
        mock_beneficiary = Mock()
        mock_beneficiary.id = 1
        mock_beneficiary_class.return_value = mock_beneficiary
        
        service = BeneficiaryService()
        
        data = {
            'email': 'ben@example.com',
            'first_name': 'Ben',
            'last_name': 'Test',
            'password': 'test123',
            'tenant_id': 1,
            'gender': 'male',
            'birth_date': '1990-01-01'
        }
        
        result = service.create_beneficiary(data)
        
        assert result == mock_beneficiary
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()
    
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_get_beneficiaries_paginated(self, mock_beneficiary_class):
        """Test getting paginated beneficiaries."""
        # Mock beneficiaries
        mock_beneficiaries = [Mock(id=i) for i in range(5)]
        
        # Mock pagination
        mock_pagination = Mock()
        mock_pagination.items = mock_beneficiaries
        mock_pagination.total = 5
        mock_pagination.pages = 1
        mock_pagination.page = 1
        
        mock_query = Mock()
        mock_query.filter_by.return_value.paginate.return_value = mock_pagination
        mock_beneficiary_class.query = mock_query
        
        service = BeneficiaryService()
        result = service.get_all_paginated(page=1, per_page=10)
        
        assert result == mock_pagination
        mock_query.filter_by.assert_called_with(is_active=True)


class TestServiceHelpers:
    """Test service helper methods."""
    
    def test_auth_service_generate_tokens(self):
        """Test token generation in auth service."""
        service = AuthService()
        
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.role = 'staff'
        
        with patch('app.services.auth_service.create_access_token') as mock_create:
            mock_create.return_value = 'test_token'
            
            tokens = service.generate_tokens(mock_user)
            
            assert 'access_token' in tokens
            assert tokens['access_token'] == 'test_token'
            mock_create.assert_called()
    
    def test_email_service_format_email(self):
        """Test email formatting."""
        with patch('app.services.email_service.Mail'):
            service = EmailService()
            
            # Test email address formatting
            formatted = service._format_email_address('John Doe', 'john@example.com')
            assert 'john@example.com' in formatted
    
    def test_beneficiary_service_validate_data(self):
        """Test data validation in beneficiary service."""
        service = BeneficiaryService()
        
        # Valid data
        valid_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'tenant_id': 1
        }
        
        is_valid = service._validate_beneficiary_data(valid_data)
        assert is_valid is True
        
        # Invalid data (missing email)
        invalid_data = {
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        is_valid = service._validate_beneficiary_data(invalid_data)
        assert is_valid is False