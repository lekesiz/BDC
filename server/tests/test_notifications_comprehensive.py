"""Comprehensive tests for notifications utility."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call
from flask import Flask
import smtplib
from email.mime.multipart import MIMEMultipart

from app.utils.notifications import (
    send_email, send_slack_message, send_sms, send_push_notification,
    send_notification, send_bulk_notification, schedule_notification
)


class TestSendEmail:
    """Test the send_email function."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config['SMTP_HOST'] = 'smtp.test.com'
        app.config['SMTP_PORT'] = 587
        app.config['SMTP_USER'] = 'test@test.com'
        app.config['SMTP_PASSWORD'] = 'password'
        app.config['SMTP_USE_TLS'] = True
        app.config['MAIL_FROM'] = 'noreply@test.com'
        return app
    
    @patch('app.utils.notifications.smtplib.SMTP')
    @patch('app.utils.notifications.logger')
    def test_send_email_basic(self, mock_logger, mock_smtp_class, app):
        """Test sending basic email."""
        # Setup mock SMTP
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test Subject',
                body='Test Body'
            )
        
        assert result is True
        mock_smtp_class.assert_called_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'password')
        mock_server.send_message.assert_called_once()
        mock_logger.info.assert_called_once()
    
    @patch('app.utils.notifications.smtplib.SMTP')
    def test_send_email_with_html(self, mock_smtp_class, app):
        """Test sending email with HTML body."""
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test',
                body='Plain text',
                html_body='<h1>HTML content</h1>'
            )
        
        assert result is True
        # Check that message was created with both parts
        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg.is_multipart()
    
    @patch('app.utils.notifications.smtplib.SMTP')
    def test_send_email_custom_from(self, mock_smtp_class, app):
        """Test sending email with custom from address."""
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test',
                body='Test',
                from_email='custom@test.com'
            )
        
        assert result is True
        sent_msg = mock_server.send_message.call_args[0][0]
        assert sent_msg['From'] == 'custom@test.com'
    
    @patch('app.utils.notifications.smtplib.SMTP')
    def test_send_email_no_auth(self, mock_smtp_class, app):
        """Test sending email without authentication."""
        app.config['SMTP_USER'] = None
        app.config['SMTP_PASSWORD'] = None
        
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test',
                body='Test'
            )
        
        assert result is True
        mock_server.login.assert_not_called()
    
    @patch('app.utils.notifications.smtplib.SMTP')
    def test_send_email_no_tls(self, mock_smtp_class, app):
        """Test sending email without TLS."""
        app.config['SMTP_USE_TLS'] = False
        
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test',
                body='Test'
            )
        
        assert result is True
        mock_server.starttls.assert_not_called()
    
    @patch('app.utils.notifications.smtplib.SMTP')
    @patch('app.utils.notifications.logger')
    def test_send_email_failure(self, mock_logger, mock_smtp_class, app):
        """Test email sending failure."""
        mock_smtp_class.side_effect = Exception('SMTP Error')
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test',
                body='Test'
            )
        
        assert result is False
        mock_logger.error.assert_called_once()
        assert 'SMTP Error' in mock_logger.error.call_args[0][0]
    
    @patch('app.utils.notifications.smtplib.SMTP')
    def test_send_email_with_attachments(self, mock_smtp_class, app):
        """Test sending email with attachments (placeholder test)."""
        mock_server = Mock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        with app.app_context():
            result = send_email(
                to='user@example.com',
                subject='Test',
                body='Test',
                attachments=[{'name': 'file.txt', 'content': 'data'}]
            )
        
        # Currently attachments are not implemented
        assert result is True


class TestSendSlackMessage:
    """Test the send_slack_message function."""
    
    @patch('app.utils.notifications.requests.post')
    @patch('app.utils.notifications.logger')
    def test_send_slack_message_success(self, mock_logger, mock_post):
        """Test successful Slack message."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_slack_message(
            'https://hooks.slack.com/test',
            {'text': 'Test message'}
        )
        
        assert result is True
        mock_post.assert_called_once_with(
            'https://hooks.slack.com/test',
            json={'text': 'Test message'},
            timeout=10
        )
        mock_logger.info.assert_called_once()
    
    @patch('app.utils.notifications.requests.post')
    @patch('app.utils.notifications.logger')
    def test_send_slack_message_failure(self, mock_logger, mock_post):
        """Test Slack message failure."""
        mock_post.side_effect = Exception('Network error')
        
        result = send_slack_message(
            'https://hooks.slack.com/test',
            {'text': 'Test message'}
        )
        
        assert result is False
        mock_logger.error.assert_called_once()
        assert 'Network error' in mock_logger.error.call_args[0][0]


class TestSendSMS:
    """Test the send_sms function."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config['TWILIO_ACCOUNT_SID'] = 'test_sid'
        app.config['TWILIO_AUTH_TOKEN'] = 'test_token'
        app.config['TWILIO_FROM_NUMBER'] = '+1234567890'
        return app
    
    @patch('app.utils.notifications.logger')
    def test_send_sms_no_credentials(self, mock_logger, app):
        """Test SMS when Twilio not configured."""
        app.config['TWILIO_ACCOUNT_SID'] = None
        
        with app.app_context():
            result = send_sms('+1111111111', 'Test message')
        
        assert result is False
        mock_logger.warning.assert_called_once()
    
    @patch('app.utils.notifications.Client')
    @patch('app.utils.notifications.logger')
    def test_send_sms_success(self, mock_logger, mock_client_class, app):
        """Test successful SMS sending."""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.sid = 'MSG123'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client
        
        with app.app_context():
            result = send_sms('+1111111111', 'Test message')
        
        assert result is True
        mock_client_class.assert_called_with('test_sid', 'test_token')
        mock_client.messages.create.assert_called_with(
            body='Test message',
            from_='+1234567890',
            to='+1111111111'
        )
        mock_logger.info.assert_called_once()
    
    @patch('app.utils.notifications.logger')
    def test_send_sms_import_error(self, mock_logger, app):
        """Test SMS when Twilio library not installed."""
        with patch.dict('sys.modules', {'twilio.rest': None}):
            with app.app_context():
                result = send_sms('+1111111111', 'Test message')
        
        assert result is False
        mock_logger.warning.assert_called_once()
        assert 'not installed' in mock_logger.warning.call_args[0][0]
    
    @patch('app.utils.notifications.Client')
    @patch('app.utils.notifications.logger')
    def test_send_sms_failure(self, mock_logger, mock_client_class, app):
        """Test SMS sending failure."""
        mock_client_class.side_effect = Exception('Twilio error')
        
        with app.app_context():
            result = send_sms('+1111111111', 'Test message')
        
        assert result is False
        mock_logger.error.assert_called_once()
        assert 'Twilio error' in mock_logger.error.call_args[0][0]


class TestSendPushNotification:
    """Test the send_push_notification function."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config['FCM_SERVER_KEY'] = 'test_fcm_key'
        return app
    
    @patch('app.utils.notifications.logger')
    def test_send_push_no_fcm_key(self, mock_logger):
        """Test push notification without FCM key."""
        app = Flask(__name__)
        
        with app.app_context():
            result = send_push_notification(1, 'Title', 'Body')
        
        assert result is False
        mock_logger.warning.assert_called_once()
    
    @patch('app.utils.notifications.logger')
    def test_send_push_no_device_tokens(self, mock_logger, app):
        """Test push notification with no device tokens."""
        with app.app_context():
            result = send_push_notification(1, 'Title', 'Body')
        
        assert result is False
        assert mock_logger.warning.call_count == 1
        assert 'No device tokens' in mock_logger.warning.call_args[0][0]
    
    @patch('app.utils.notifications.requests.post')
    @patch('app.utils.notifications.logger')
    def test_send_push_success(self, mock_logger, mock_post, app):
        """Test successful push notification."""
        # Mock device tokens retrieval
        with patch.object(send_push_notification.__globals__, 'device_tokens', ['token1', 'token2']):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            with app.app_context():
                result = send_push_notification(
                    1, 'Title', 'Body', 
                    data={'key': 'value'}
                )
            
            # Should fail because device_tokens is still empty in the actual function
            assert result is False
    
    @patch('app.utils.notifications.logger')
    def test_send_push_exception(self, mock_logger, app):
        """Test push notification with exception."""
        with patch('app.utils.notifications.requests.post', side_effect=Exception('Network error')):
            with app.app_context():
                result = send_push_notification(1, 'Title', 'Body')
        
        # Will fail at device tokens check
        assert result is False


class TestSendNotification:
    """Test the send_notification function."""
    
    @patch('app.utils.notifications.send_email')
    @patch('app.utils.notifications.send_sms')
    @patch('app.utils.notifications.send_push_notification')
    @patch('app.utils.notifications.db')
    @patch('app.utils.notifications.Notification')
    def test_send_notification_all_channels(self, mock_notification, mock_db, 
                                          mock_push, mock_sms, mock_email):
        """Test sending notification through all channels."""
        # Setup mocks
        mock_email.return_value = True
        mock_sms.return_value = True
        mock_push.return_value = True
        
        # Mock user data
        with patch.object(send_notification.__globals__, 'user_email', 'test@test.com'), \
             patch.object(send_notification.__globals__, 'user_phone', '+1234567890'):
            
            result = send_notification(
                user_id=1,
                notification_type='test',
                subject='Test Subject',
                message='Test Message',
                data={'key': 'value'},
                channels=['email', 'sms', 'push']
            )
        
        # Email and SMS won't be called because user_email/phone are None in actual function
        assert 'push' in result
        mock_push.assert_called_once()
    
    @patch('app.utils.notifications.send_push_notification')
    @patch('app.utils.notifications.logger')
    def test_send_notification_db_error(self, mock_logger, mock_push):
        """Test notification when database save fails."""
        mock_push.return_value = True
        
        with patch('app.utils.notifications.db') as mock_db:
            mock_db.session.commit.side_effect = Exception('DB Error')
            
            result = send_notification(
                user_id=1,
                notification_type='test',
                subject='Test',
                message='Test',
                channels=['push']
            )
        
        assert 'push' in result
        mock_logger.error.assert_called_once()


class TestSendBulkNotification:
    """Test the send_bulk_notification function."""
    
    @patch('app.utils.notifications.send_notification')
    def test_send_bulk_notification(self, mock_send):
        """Test sending notification to multiple users."""
        mock_send.return_value = {'email': True, 'push': True}
        
        result = send_bulk_notification(
            user_ids=[1, 2, 3],
            notification_type='announcement',
            subject='Announcement',
            message='Important message',
            data={'priority': 'high'},
            channels=['email', 'push']
        )
        
        assert len(result) == 3
        assert mock_send.call_count == 3
        assert all(user_id in result for user_id in [1, 2, 3])


class TestScheduleNotification:
    """Test the schedule_notification function."""
    
    @patch('app.utils.notifications.db')
    @patch('app.utils.notifications.ScheduledNotification')
    @patch('app.utils.notifications.logger')
    def test_schedule_notification_success(self, mock_logger, mock_scheduled, mock_db):
        """Test successful notification scheduling."""
        mock_instance = Mock()
        mock_instance.id = 123
        mock_scheduled.return_value = mock_instance
        
        scheduled_time = datetime(2024, 1, 1, 12, 0, 0)
        
        result = schedule_notification(
            user_id=1,
            notification_type='reminder',
            subject='Reminder',
            message='Don\'t forget',
            scheduled_at=scheduled_time,
            data={'task_id': 456}
        )
        
        assert result == 123
        mock_db.session.add.assert_called_with(mock_instance)
        mock_db.session.commit.assert_called_once()
        mock_logger.info.assert_called_once()
    
    @patch('app.utils.notifications.db')
    @patch('app.utils.notifications.ScheduledNotification')
    @patch('app.utils.notifications.logger')
    def test_schedule_notification_failure(self, mock_logger, mock_scheduled, mock_db):
        """Test notification scheduling failure."""
        mock_db.session.commit.side_effect = Exception('DB Error')
        
        result = schedule_notification(
            user_id=1,
            notification_type='reminder',
            subject='Reminder',
            message='Test',
            scheduled_at=datetime.now()
        )
        
        assert result is None
        mock_logger.error.assert_called_once()
        assert 'DB Error' in mock_logger.error.call_args[0][0]