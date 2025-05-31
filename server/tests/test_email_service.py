import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from flask_mail import Message

from app import create_app
from app.services.email_service import (
    send_email, send_async_email, send_welcome_email, 
    send_password_reset_email, send_notification_email,
    generate_email_token, verify_email_token
)
from app.models import User


class TestEmailService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test user
        self.test_user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student',
            is_active=True,
            id=1
        )
        
        yield
        
        self.app_context.pop()
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_basic(self, mock_message_class, mock_thread_class):
        """Test basic email sending"""
        mock_message = MagicMock()
        mock_message_class.return_value = mock_message
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        result = send_email(
            subject='Test Subject',
            recipients=['test@example.com'],
            text_body='Test body'
        )
        
        assert result is True
        mock_message_class.assert_called_once()
        mock_thread_class.assert_called_once()
        mock_thread.start.assert_called_once()
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_with_html(self, mock_message_class, mock_thread_class):
        """Test sending email with HTML body"""
        mock_message = MagicMock()
        mock_message_class.return_value = mock_message
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        result = send_email(
            subject='Test Subject',
            recipients=['test@example.com'],
            text_body='Test body',
            html_body='<p>Test HTML body</p>'
        )
        
        assert result is True
        assert mock_message.html == '<p>Test HTML body</p>'
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_with_attachments(self, mock_message_class, mock_thread_class):
        """Test sending email with attachments"""
        mock_message = MagicMock()
        mock_message_class.return_value = mock_message
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        attachments = [
            ('test.pdf', 'application/pdf', b'PDF content'),
            ('test.txt', 'text/plain', b'Text content')
        ]
        
        result = send_email(
            subject='Test Subject',
            recipients=['test@example.com'],
            text_body='Test body',
            attachments=attachments
        )
        
        assert result is True
        assert mock_message.attach.call_count == 2
    
    @patch('app.services.email_service.send_email')
    def test_send_welcome_email(self, mock_send_email):
        """Test sending welcome email"""
        mock_send_email.return_value = True
        
        result = send_welcome_email(self.test_user)
        
        assert result is True
        mock_send_email.assert_called_once()
        
        # Check email content
        call_args = mock_send_email.call_args
        assert call_args[1]['subject'] == 'Welcome to BDC Platform'
        assert call_args[1]['recipients'] == ['test@example.com']
        assert 'Test User' in call_args[1]['text_body']
    
    @patch('app.services.email_service.send_email')
    @patch('app.services.email_service.generate_email_token')
    def test_send_password_reset_email(self, mock_generate_token, mock_send_email):
        """Test sending password reset email"""
        mock_generate_token.return_value = 'test-token-123'
        mock_send_email.return_value = True
        
        result = send_password_reset_email(self.test_user)
        
        assert result is True
        mock_generate_token.assert_called_once()
        mock_send_email.assert_called_once()
        
        # Check email content
        call_args = mock_send_email.call_args
        assert call_args[1]['subject'] == 'Reset Your Password'
        assert 'test-token-123' in call_args[1]['text_body']
    
    @patch('app.services.email_service.send_email')
    def test_send_notification_email(self, mock_send_email):
        """Test sending notification email"""
        mock_send_email.return_value = True
        
        result = send_notification_email(
            user=self.test_user,
            notification_type='appointment',
            data={'appointment_date': '2025-05-26', 'time': '10:00 AM'}
        )
        
        assert result is True
        mock_send_email.assert_called_once()
        
        # Check email content
        call_args = mock_send_email.call_args
        assert 'appointment' in call_args[1]['subject'].lower()
        assert call_args[1]['recipients'] == ['test@example.com']
    
    def test_generate_email_token(self):
        """Test generating email token"""
        data = {'user_id': 123, 'action': 'verify_email'}
        
        token = generate_email_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_email_token_with_salt(self):
        """Test generating email token with custom salt"""
        data = {'user_id': 123}
        salt = 'password-reset-salt'
        
        token = generate_email_token(data, salt=salt)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_email_token_valid(self):
        """Test verifying valid email token"""
        data = {'user_id': 123, 'action': 'verify_email'}
        token = generate_email_token(data)
        
        verified_data = verify_email_token(token)
        
        assert verified_data is not None
        assert verified_data['user_id'] == 123
        assert verified_data['action'] == 'verify_email'
    
    def test_verify_email_token_with_salt(self):
        """Test verifying token with custom salt"""
        data = {'user_id': 123}
        salt = 'password-reset-salt'
        token = generate_email_token(data, salt=salt)
        
        verified_data = verify_email_token(token, salt=salt)
        
        assert verified_data is not None
        assert verified_data['user_id'] == 123
    
    def test_verify_email_token_invalid(self):
        """Test verifying invalid email token"""
        verified_data = verify_email_token('invalid-token')
        
        assert verified_data is None
    
    def test_verify_email_token_expired(self):
        """Test verifying expired email token"""
        data = {'user_id': 123}
        # Generate token with very short expiration
        token = generate_email_token(data, expires_in=0)
        
        # Wait a moment to ensure expiration
        import time
        time.sleep(0.1)
        
        verified_data = verify_email_token(token, expires_in=0)
        
        assert verified_data is None
    
    @patch('app.services.email_service.mail')
    def test_send_async_email(self, mock_mail):
        """Test async email sending"""
        mock_msg = MagicMock()
        
        with self.app.app_context():
            send_async_email(self.app, mock_msg)
        
        mock_mail.send.assert_called_once_with(mock_msg)
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_exception_handling(self, mock_message_class, mock_thread_class):
        """Test email sending with exception"""
        mock_message_class.side_effect = Exception('Email error')
        
        result = send_email(
            subject='Test Subject',
            recipients=['test@example.com'],
            text_body='Test body'
        )
        
        assert result is False
    
    @patch('app.services.email_service.send_email')
    def test_send_notification_email_appointment_reminder(self, mock_send_email):
        """Test sending appointment reminder notification"""
        mock_send_email.return_value = True
        
        result = send_notification_email(
            user=self.test_user,
            notification_type='appointment_reminder',
            data={
                'appointment_date': '2025-05-26',
                'time': '2:00 PM',
                'trainer': 'John Doe',
                'location': 'Room 101'
            }
        )
        
        assert result is True
        call_args = mock_send_email.call_args
        assert 'reminder' in call_args[1]['subject'].lower()
        assert 'John Doe' in call_args[1]['text_body']
        assert 'Room 101' in call_args[1]['text_body']