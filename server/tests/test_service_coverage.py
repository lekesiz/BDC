"""Test service methods to increase coverage."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from flask import Flask
from app import create_app


class TestAuthService:
    """Test AuthService methods."""
    
    def test_auth_service_import(self):
        """Test that AuthService can be imported."""
        from app.services.auth_service import AuthService
        assert AuthService is not None
    
    @patch('app.models.User')
    def test_login_mock(self, mock_user, test_app):
        """Test login with mocked User."""
        with test_app.app_context():
            from app.services.auth_service import AuthService
            
            # Mock user
            mock_user_instance = Mock()
            mock_user_instance.verify_password.return_value = True
            mock_user_instance.id = 1
            mock_user_instance.email = 'test@example.com'
            
            # Mock query
            mock_user.query.filter_by.return_value.first.return_value = mock_user_instance
            
            # Mock JWT
            with patch('app.services.auth_service.create_access_token') as mock_access:
                with patch('app.services.auth_service.create_refresh_token') as mock_refresh:
                    mock_access.return_value = 'access_123'
                    mock_refresh.return_value = 'refresh_123'
                    
                    result = AuthService.login('test@example.com', 'password')
                    assert result is not None
                    assert 'access_token' in result
                    assert 'refresh_token' in result


class TestProgramService:
    """Test ProgramService methods."""
    
    def test_program_service_import(self):
        """Test that ProgramService can be imported."""
        from app.services.program_service import ProgramService
        assert ProgramService is not None
    
    @patch('app.models.Program')
    def test_get_active_programs_mock(self, mock_program, test_app):
        """Test getting active programs with mock."""
        with test_app.app_context():
            from app.services.program_service import ProgramService
            
            # Mock programs
            programs = [Mock(id=1, name='Program 1'), Mock(id=2, name='Program 2')]
            mock_program.query.filter_by.return_value.all.return_value = programs
            
            result = ProgramService.get_active_programs()
            assert len(result) == 2
            mock_program.query.filter_by.assert_called_with(is_active=True)


class TestEmailService:
    """Test EmailService methods."""
    
    def test_email_service_import(self):
        """Test that EmailService can be imported."""
        from app.services.email_service import EmailService
        assert EmailService is not None
    
    @patch('app.extensions.mail')
    def test_send_email_mock(self, mock_mail, test_app):
        """Test sending email with mock."""
        with test_app.app_context():
            from app.services.email_service import EmailService
            
            # Mock mail send
            mock_mail.send.return_value = None
            
            with patch('app.services.email_service.Message') as mock_message:
                result = EmailService.send_email(
                    'test@example.com',
                    'Test Subject',
                    'Test body'
                )
                assert result is True
                mock_mail.send.assert_called_once()


class TestNotificationService:
    """Test NotificationService methods."""
    
    def test_notification_service_import(self):
        """Test that NotificationService can be imported."""
        from app.services.notification_service import NotificationService
        assert NotificationService is not None
    
    @patch('app.models.Notification')
    @patch('app.extensions.db')
    def test_create_notification_mock(self, mock_db, mock_notification, test_app):
        """Test creating notification with mock."""
        with test_app.app_context():
            from app.services.notification_service import NotificationService
            
            # Mock notification
            notification_instance = Mock(id=1)
            mock_notification.return_value = notification_instance
            
            result = NotificationService.create_notification(
                user_id=1,
                title='Test',
                message='Test message'
            )
            
            assert result == notification_instance
            mock_db.session.add.assert_called_with(notification_instance)
            mock_db.session.commit.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])