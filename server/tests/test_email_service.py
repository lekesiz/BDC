"""Tests for email service."""

import pytest
import os
from unittest.mock import patch, MagicMock, call
from threading import Thread
from flask import current_app
from app.services.email_service import (
    send_async_email,
    send_email,
    generate_email_token,
    verify_email_token,
    send_password_reset_email,
    send_welcome_email,
    send_notification_email
)
from app.extensions import mail
from app.models import User
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadTimeSignature


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock()
    user.id = 1
    user.email = 'test@example.com'
    user.first_name = 'Test'
    user.last_name = 'User'
    return user


class TestSendAsyncEmail:
    """Test send_async_email function."""
    
    @patch('app.services.email_service.mail.send')
    def test_send_async_email_success(self, mock_mail_send, app):
        """Test successful async email sending."""
        msg = MagicMock()
        
        send_async_email(app, msg)
        
        mock_mail_send.assert_called_once_with(msg)


class TestSendEmail:
    """Test send_email function."""
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_basic(self, mock_message, mock_thread, app):
        """Test basic email sending."""
        with app.app_context():
            result = send_email(
                subject='Test Subject',
                recipients=['recipient@example.com'],
                text_body='Test body'
            )
            
            assert result is True
            
            # Check Message was created correctly
            mock_message.assert_called_once_with(
                'Test Subject',
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=['recipient@example.com']
            )
            
            # Check that async thread was started
            mock_thread.assert_called_once()
            thread_instance = mock_thread.return_value
            thread_instance.start.assert_called_once()
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_with_html_body(self, mock_message, mock_thread, app):
        """Test email sending with HTML body."""
        with app.app_context():
            result = send_email(
                subject='Test Subject',
                recipients=['recipient@example.com'],
                text_body='Test body',
                html_body='<p>Test HTML</p>'
            )
            
            assert result is True
            msg_instance = mock_message.return_value
            assert msg_instance.html == '<p>Test HTML</p>'
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_with_custom_sender(self, mock_message, mock_thread, app):
        """Test email sending with custom sender."""
        with app.app_context():
            result = send_email(
                subject='Test Subject',
                recipients=['recipient@example.com'],
                text_body='Test body',
                sender='custom@example.com'
            )
            
            assert result is True
            mock_message.assert_called_once_with(
                'Test Subject',
                sender='custom@example.com',
                recipients=['recipient@example.com']
            )
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_with_attachments(self, mock_message, mock_thread, app):
        """Test email sending with attachments."""
        with app.app_context():
            attachments = [
                ('test.pdf', 'application/pdf', b'PDF content'),
                ('test.csv', 'text/csv', b'CSV content')
            ]
            
            result = send_email(
                subject='Test Subject',
                recipients=['recipient@example.com'],
                text_body='Test body',
                attachments=attachments
            )
            
            assert result is True
            msg_instance = mock_message.return_value
            # Verify attach was called for each attachment
            assert msg_instance.attach.call_count == 2
            msg_instance.attach.assert_any_call('test.pdf', 'application/pdf', b'PDF content')
            msg_instance.attach.assert_any_call('test.csv', 'text/csv', b'CSV content')
    
    @patch('app.services.email_service.Thread')
    @patch('app.services.email_service.Message')
    def test_send_email_exception_handling(self, mock_message, mock_thread, app):
        """Test email sending with exception."""
        with app.app_context():
            # Make Message constructor raise an exception
            mock_message.side_effect = Exception('Email error')
            
            with patch.object(current_app.logger, 'error') as mock_logger:
                result = send_email(
                    subject='Test Subject',
                    recipients=['recipient@example.com'],
                    text_body='Test body'
                )
                
                assert result is False
                mock_logger.assert_called_once_with("Email sending error: Email error")


class TestEmailTokens:
    """Test email token generation and verification."""
    
    def test_generate_email_token(self, app):
        """Test token generation."""
        with app.app_context():
            data = {'user_id': 123}
            token = generate_email_token(data)
            
            assert token is not None
            assert isinstance(token, str)
    
    def test_generate_email_token_with_custom_salt(self, app):
        """Test token generation with custom salt."""
        with app.app_context():
            data = {'user_id': 123}
            token = generate_email_token(data, salt='custom-salt')
            
            assert token is not None
            assert isinstance(token, str)
    
    def test_verify_email_token_success(self, app):
        """Test successful token verification."""
        with app.app_context():
            data = {'user_id': 123}
            token = generate_email_token(data)
            
            verified_data = verify_email_token(token)
            
            assert verified_data == data
    
    def test_verify_email_token_with_custom_salt(self, app):
        """Test token verification with custom salt."""
        with app.app_context():
            data = {'user_id': 123}
            salt = 'custom-salt'
            token = generate_email_token(data, salt=salt)
            
            verified_data = verify_email_token(token, salt=salt)
            
            assert verified_data == data
    
    def test_verify_email_token_wrong_salt(self, app):
        """Test token verification with wrong salt."""
        with app.app_context():
            data = {'user_id': 123}
            token = generate_email_token(data, salt='salt1')
            
            verified_data = verify_email_token(token, salt='salt2')
            
            assert verified_data is None
    
    @patch('app.services.email_service.URLSafeTimedSerializer.loads')
    def test_verify_email_token_expired(self, mock_loads, app):
        """Test token verification with expired token."""
        with app.app_context():
            mock_loads.side_effect = SignatureExpired('Token expired')
            
            verified_data = verify_email_token('some_token')
            
            assert verified_data is None
    
    @patch('app.services.email_service.URLSafeTimedSerializer.loads')
    def test_verify_email_token_bad_signature(self, mock_loads, app):
        """Test token verification with bad signature."""
        with app.app_context():
            mock_loads.side_effect = BadTimeSignature('Bad signature')
            
            verified_data = verify_email_token('some_token')
            
            assert verified_data is None


class TestPasswordResetEmail:
    """Test password reset email functionality."""
    
    @patch('app.services.email_service.send_email')
    @patch('app.services.email_service.generate_email_token')
    def test_send_password_reset_email(self, mock_generate_token, mock_send_email, app, mock_user):
        """Test sending password reset email."""
        with app.app_context():
            app.config['FRONTEND_URL'] = 'http://frontend.com'
            mock_generate_token.return_value = 'test-token'
            mock_send_email.return_value = True
            
            result = send_password_reset_email(mock_user)
            
            assert result is True
            
            # Verify token generation
            mock_generate_token.assert_called_once_with(
                {'user_id': mock_user.id},
                salt='password-reset-salt',
                expires_in=3600
            )
            
            # Verify email sending
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['subject'] == 'Reset Your Password'
            assert call_args['recipients'] == [mock_user.email]
            assert 'http://frontend.com/reset-password?token=test-token' in call_args['text_body']
            assert 'http://frontend.com/reset-password?token=test-token' in call_args['html_body']
    
    @patch('app.services.email_service.send_email')
    @patch('app.services.email_service.generate_email_token')
    def test_send_password_reset_email_default_frontend_url(self, mock_generate_token, mock_send_email, app, mock_user):
        """Test sending password reset email with default frontend URL."""
        with app.app_context():
            # Remove FRONTEND_URL from config to test default behavior
            app.config.pop('FRONTEND_URL', None)
            mock_generate_token.return_value = 'test-token'
            mock_send_email.return_value = True
            
            result = send_password_reset_email(mock_user)
            
            assert result is True
            
            # Verify default URL is used
            call_args = mock_send_email.call_args[1]
            assert 'http://localhost:5173/reset-password?token=test-token' in call_args['text_body']


class TestWelcomeEmail:
    """Test welcome email functionality."""
    
    @patch('app.services.email_service.send_email')
    def test_send_welcome_email(self, mock_send_email, app, mock_user):
        """Test sending welcome email."""
        with app.app_context():
            mock_send_email.return_value = True
            
            result = send_welcome_email(mock_user)
            
            assert result is True
            
            # Verify email sending
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['subject'] == 'Welcome to BDC'
            assert call_args['recipients'] == [mock_user.email]
            assert f'Dear {mock_user.first_name} {mock_user.last_name}' in call_args['text_body']
            assert f'Dear {mock_user.first_name} {mock_user.last_name}' in call_args['html_body']
            assert 'Welcome to BDC!' in call_args['text_body']


class TestNotificationEmail:
    """Test notification email functionality."""
    
    @patch('app.services.email_service.send_email')
    def test_send_notification_email_with_full_notification(self, mock_send_email, app, mock_user):
        """Test sending notification email with full notification data."""
        with app.app_context():
            mock_send_email.return_value = True
            
            notification = {
                'subject': 'Custom Subject',
                'message': 'Custom notification message'
            }
            
            result = send_notification_email(mock_user, notification)
            
            assert result is True
            
            # Verify email sending
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['subject'] == 'Custom Subject'
            assert call_args['recipients'] == [mock_user.email]
            assert 'Custom notification message' in call_args['text_body']
            assert 'Custom notification message' in call_args['html_body']
    
    @patch('app.services.email_service.send_email')
    def test_send_notification_email_with_default_values(self, mock_send_email, app, mock_user):
        """Test sending notification email with default values."""
        with app.app_context():
            mock_send_email.return_value = True
            
            notification = {}
            
            result = send_notification_email(mock_user, notification)
            
            assert result is True
            
            # Verify email sending with defaults
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['subject'] == 'New Notification'
            assert call_args['recipients'] == [mock_user.email]
            assert 'You have a new notification.' in call_args['text_body']
            assert 'You have a new notification.' in call_args['html_body']
    
    @patch('app.services.email_service.send_email')
    def test_send_notification_email_partial_notification(self, mock_send_email, app, mock_user):
        """Test sending notification email with partial notification data."""
        with app.app_context():
            mock_send_email.return_value = True
            
            notification = {
                'message': 'Custom message only'
            }
            
            result = send_notification_email(mock_user, notification)
            
            assert result is True
            
            # Verify email sending
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['subject'] == 'New Notification'  # Default subject
            assert call_args['recipients'] == [mock_user.email]
            assert 'Custom message only' in call_args['text_body']
            assert 'Custom message only' in call_args['html_body']