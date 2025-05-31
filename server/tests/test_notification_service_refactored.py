"""Unit tests for refactored notification service."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.orm import Session

from app.services.notification_service_refactored import (
    NotificationServiceRefactored,
    NotificationType,
    NotificationPriority,
    IEmailService,
    IRealtimeService
)
from app.models.notification import Notification
from app.models.user import User, user_tenant


class TestNotificationServiceRefactored:
    """Test cases for refactored notification service."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        session = Mock()
        session.query = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.refresh = Mock()
        session.delete = Mock()
        return session
    
    @pytest.fixture
    def mock_email_service(self):
        """Create mock email service."""
        service = Mock()
        service.send_notification_email = Mock(return_value=True)
        return service
    
    @pytest.fixture
    def mock_realtime_service(self):
        """Create mock realtime service."""
        service = Mock()
        service.emit_to_user = Mock()
        service.emit_to_role = Mock()
        service.emit_to_tenant = Mock()
        service.user_is_online = Mock(return_value=True)
        return service
    
    @pytest.fixture
    def service(self, mock_db_session, mock_email_service, mock_realtime_service):
        """Create notification service instance."""
        return NotificationServiceRefactored(
            db_session=mock_db_session,
            email_service=mock_email_service,
            realtime_service=mock_realtime_service
        )
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        user.first_name = "Test"
        user.last_name = "User"
        user.is_active = True
        user.role = "trainer"
        return user
    
    @pytest.fixture
    def mock_notification(self):
        """Create mock notification."""
        notification = Mock()
        notification.id = 1
        notification.user_id = 1
        notification.sender_id = 2
        notification.title = "Test Notification"
        notification.message = "Test message"
        notification.type = NotificationType.SYSTEM.value
        notification.priority = NotificationPriority.NORMAL.value
        notification.read = False
        notification.read_at = None
        notification.link = None
        notification.data = None
        notification.related_id = None
        notification.related_type = None
        notification.tenant_id = None
        notification.created_at = datetime.now(timezone.utc)
        notification.updated_at = datetime.now(timezone.utc)
        return notification
    
    def test_create_notification_success(self, service, mock_db_session, mock_user, mock_notification):
        """Test successful notification creation."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute
        result = service.create_notification(
            user_id=1,
            type=NotificationType.SYSTEM.value,
            title="Test Notification",
            message="Test message",
            send_email=True
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        service.email_service.send_notification_email.assert_called_once_with(
            user_email="test@example.com",
            subject="Test Notification",
            message="Test message"
        )
        service.realtime_service.emit_to_user.assert_called_once()
        assert isinstance(result, dict)
    
    def test_create_notification_invalid_user(self, service, mock_db_session):
        """Test notification creation with invalid user."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="User with id 999 not found"):
            service.create_notification(
                user_id=999,
                type=NotificationType.SYSTEM.value,
                title="Test",
                message="Test"
            )
    
    def test_create_notification_invalid_type(self, service, mock_db_session, mock_user):
        """Test notification creation with invalid type."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid notification type"):
            service.create_notification(
                user_id=1,
                type="invalid_type",
                title="Test",
                message="Test"
            )
    
    def test_create_notification_invalid_priority(self, service, mock_db_session, mock_user):
        """Test notification creation with invalid priority."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid notification priority"):
            service.create_notification(
                user_id=1,
                type=NotificationType.SYSTEM.value,
                title="Test",
                message="Test",
                priority="invalid_priority"
            )
    
    def test_create_notification_database_error(self, service, mock_db_session, mock_user):
        """Test notification creation with database error."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Execute & Assert
        with pytest.raises(Exception, match="Failed to create notification"):
            service.create_notification(
                user_id=1,
                type=NotificationType.SYSTEM.value,
                title="Test",
                message="Test"
            )
        mock_db_session.rollback.assert_called_once()
    
    def test_create_notification_no_email_service(self, mock_db_session, mock_realtime_service, mock_user):
        """Test notification creation without email service."""
        # Setup
        service = NotificationServiceRefactored(
            db_session=mock_db_session,
            realtime_service=mock_realtime_service
        )
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute
        result = service.create_notification(
            user_id=1,
            type=NotificationType.SYSTEM.value,
            title="Test",
            message="Test",
            send_email=True
        )
        
        # Assert - Should not fail even without email service
        assert isinstance(result, dict)
    
    def test_create_notification_user_offline(self, service, mock_db_session, mock_user):
        """Test notification creation when user is offline."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        service.realtime_service.user_is_online.return_value = False
        
        # Execute
        result = service.create_notification(
            user_id=1,
            type=NotificationType.SYSTEM.value,
            title="Test",
            message="Test"
        )
        
        # Assert
        service.realtime_service.emit_to_user.assert_not_called()
        assert isinstance(result, dict)
    
    def test_create_bulk_notifications(self, service, mock_db_session, mock_user):
        """Test bulk notification creation."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        user_ids = [1, 2, 3]
        
        # Execute
        results = service.create_bulk_notifications(
            user_ids=user_ids,
            type=NotificationType.SYSTEM.value,
            title="Bulk Test",
            message="Bulk message"
        )
        
        # Assert
        assert len(results) == 3
        assert mock_db_session.add.call_count == 3
        assert mock_db_session.commit.call_count == 3
    
    def test_create_bulk_notifications_partial_failure(self, service, mock_db_session, mock_user):
        """Test bulk notification creation with partial failure."""
        # Setup
        mock_db_session.query().filter_by().first.side_effect = [mock_user, None, mock_user]
        user_ids = [1, 999, 3]
        
        # Execute
        results = service.create_bulk_notifications(
            user_ids=user_ids,
            type=NotificationType.SYSTEM.value,
            title="Bulk Test",
            message="Bulk message"
        )
        
        # Assert - Should create 2 notifications, skip the invalid user
        assert len(results) == 2
    
    def test_create_role_notification(self, service, mock_db_session, mock_user):
        """Test role-based notification creation."""
        # Setup
        mock_users = [mock_user, Mock(id=2, email="user2@example.com")]
        mock_query = Mock()
        mock_query.all.return_value = mock_users
        mock_db_session.query().filter().all.return_value = mock_users
        mock_db_session.query().filter.return_value = mock_query
        mock_db_session.query().filter_by().first.side_effect = mock_users
        
        # Execute
        results = service.create_role_notification(
            role="trainer",
            type=NotificationType.SYSTEM.value,
            title="Role Test",
            message="Role message"
        )
        
        # Assert
        assert len(results) == 2
        service.realtime_service.emit_to_role.assert_called_once_with(
            "trainer",
            "notification",
            {
                'type': NotificationType.SYSTEM.value,
                'title': "Role Test",
                'message': "Role message",
                'data': None,
                'related_id': None,
                'related_type': None,
                'sender_id': None,
                'priority': NotificationPriority.NORMAL.value,
                'tenant_id': None,
                'created_at': service.realtime_service.emit_to_role.call_args[0][2]['created_at']
            }
        )
    
    def test_create_role_notification_with_tenant(self, service, mock_db_session, mock_user):
        """Test role-based notification creation with tenant filter."""
        # Setup
        mock_users = [mock_user]
        mock_query = Mock()
        mock_query.all.return_value = mock_users
        mock_join = Mock()
        mock_join.filter.return_value = mock_query
        mock_db_session.query().filter().join.return_value = mock_join
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute
        results = service.create_role_notification(
            role="trainer",
            type=NotificationType.SYSTEM.value,
            title="Role Test",
            message="Role message",
            tenant_id=1
        )
        
        # Assert
        assert len(results) == 1
    
    def test_create_tenant_notification(self, service, mock_db_session, mock_user):
        """Test tenant-wide notification creation."""
        # Setup
        mock_users = [mock_user, Mock(id=2, email="user2@example.com")]
        mock_query = Mock()
        mock_query.all.return_value = mock_users
        mock_filter = Mock()
        mock_filter.all.return_value = mock_users
        mock_join = Mock()
        mock_join.filter.return_value = mock_filter
        mock_db_session.query().join.return_value = mock_join
        mock_db_session.query().filter_by().first.side_effect = mock_users
        
        # Execute
        results = service.create_tenant_notification(
            tenant_id=1,
            type=NotificationType.SYSTEM.value,
            title="Tenant Test",
            message="Tenant message"
        )
        
        # Assert
        assert len(results) == 2
        service.realtime_service.emit_to_tenant.assert_called_once()
    
    def test_create_tenant_notification_exclude_roles(self, service, mock_db_session, mock_user):
        """Test tenant notification with excluded roles."""
        # Setup
        mock_users = [mock_user]
        mock_query = Mock()
        mock_query.all.return_value = mock_users
        mock_filter_notin = Mock()
        mock_filter_notin.all.return_value = mock_users
        mock_filter = Mock()
        mock_filter.filter.return_value = mock_filter_notin
        mock_join = Mock()
        mock_join.filter.return_value = mock_filter
        mock_db_session.query().join.return_value = mock_join
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute
        results = service.create_tenant_notification(
            tenant_id=1,
            type=NotificationType.SYSTEM.value,
            title="Tenant Test",
            message="Tenant message",
            exclude_roles=["admin"]
        )
        
        # Assert
        assert len(results) == 1
    
    def test_mark_as_read_success(self, service, mock_db_session, mock_notification):
        """Test marking notification as read."""
        # Setup
        mock_db_session.query().filter().first.return_value = mock_notification
        
        # Execute
        result = service.mark_as_read(notification_id=1, user_id=1)
        
        # Assert
        assert result is True
        assert mock_notification.read is True
        assert mock_notification.read_at is not None
        mock_db_session.commit.assert_called_once()
    
    def test_mark_as_read_not_found(self, service, mock_db_session):
        """Test marking non-existent notification as read."""
        # Setup
        mock_db_session.query().filter().first.return_value = None
        
        # Execute
        result = service.mark_as_read(notification_id=999, user_id=1)
        
        # Assert
        assert result is False
        mock_db_session.commit.assert_not_called()
    
    def test_mark_as_read_database_error(self, service, mock_db_session, mock_notification):
        """Test marking notification as read with database error."""
        # Setup
        mock_db_session.query().filter().first.return_value = mock_notification
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Execute
        result = service.mark_as_read(notification_id=1, user_id=1)
        
        # Assert
        assert result is False
        mock_db_session.rollback.assert_called_once()
    
    def test_mark_all_as_read_success(self, service, mock_db_session):
        """Test marking all notifications as read."""
        # Setup
        mock_query = Mock()
        mock_query.update.return_value = 5
        mock_db_session.query().filter.return_value = mock_query
        
        # Execute
        result = service.mark_all_as_read(user_id=1)
        
        # Assert
        assert result == 5
        mock_query.update.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_mark_all_as_read_with_type_filter(self, service, mock_db_session):
        """Test marking all notifications of specific type as read."""
        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.update.return_value = 3
        mock_query.filter.return_value = mock_filter
        mock_db_session.query().filter.return_value = mock_query
        
        # Execute
        result = service.mark_all_as_read(user_id=1, type=NotificationType.APPOINTMENT.value)
        
        # Assert
        assert result == 3
        assert mock_query.filter.call_count == 1
    
    def test_mark_all_as_read_database_error(self, service, mock_db_session):
        """Test marking all as read with database error."""
        # Setup
        mock_query = Mock()
        mock_query.update.side_effect = Exception("Database error")
        mock_db_session.query().filter.return_value = mock_query
        
        # Execute
        result = service.mark_all_as_read(user_id=1)
        
        # Assert
        assert result == 0
        mock_db_session.rollback.assert_called_once()
    
    def test_delete_notification_success(self, service, mock_db_session, mock_notification):
        """Test deleting notification."""
        # Setup
        mock_db_session.query().filter().first.return_value = mock_notification
        
        # Execute
        result = service.delete_notification(notification_id=1, user_id=1)
        
        # Assert
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_notification)
        mock_db_session.commit.assert_called_once()
    
    def test_delete_notification_not_found(self, service, mock_db_session):
        """Test deleting non-existent notification."""
        # Setup
        mock_db_session.query().filter().first.return_value = None
        
        # Execute
        result = service.delete_notification(notification_id=999, user_id=1)
        
        # Assert
        assert result is False
        mock_db_session.delete.assert_not_called()
    
    def test_delete_notification_database_error(self, service, mock_db_session, mock_notification):
        """Test deleting notification with database error."""
        # Setup
        mock_db_session.query().filter().first.return_value = mock_notification
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Execute
        result = service.delete_notification(notification_id=1, user_id=1)
        
        # Assert
        assert result is False
        mock_db_session.rollback.assert_called_once()
    
    def test_get_user_notifications_success(self, service, mock_db_session, mock_notification):
        """Test getting user notifications."""
        # Setup
        notifications = [mock_notification, Mock(spec=Notification, id=2)]
        mock_query = Mock()
        mock_query.order_by().limit().offset().all.return_value = notifications
        mock_db_session.query().filter.return_value = mock_query
        mock_db_session.query().filter_by().first.return_value = Mock()  # For sender
        
        # Execute
        results = service.get_user_notifications(user_id=1, limit=10, offset=0)
        
        # Assert
        assert len(results) == 2
        assert all(isinstance(r, dict) for r in results)
    
    def test_get_user_notifications_unread_only(self, service, mock_db_session, mock_notification):
        """Test getting only unread notifications."""
        # Setup
        mock_notification.read = False
        notifications = [mock_notification]
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.order_by().limit().offset().all.return_value = notifications
        mock_query.filter.return_value = mock_filter
        mock_db_session.query().filter.return_value = mock_query
        mock_db_session.query().filter_by().first.return_value = None  # No sender
        
        # Execute
        results = service.get_user_notifications(user_id=1, unread_only=True)
        
        # Assert
        assert len(results) == 1
        assert mock_query.filter.call_count == 1
    
    def test_get_user_notifications_with_type_filter(self, service, mock_db_session, mock_notification):
        """Test getting notifications with type filter."""
        # Setup
        notifications = [mock_notification]
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.order_by().limit().offset().all.return_value = notifications
        mock_query.filter.return_value = mock_filter
        mock_db_session.query().filter.return_value = mock_query
        
        # Execute
        results = service.get_user_notifications(
            user_id=1,
            type=NotificationType.SYSTEM.value
        )
        
        # Assert
        assert len(results) == 1
        assert mock_query.filter.call_count == 1
    
    def test_get_user_notifications_database_error(self, service, mock_db_session):
        """Test getting notifications with database error."""
        # Setup
        mock_db_session.query().filter.side_effect = Exception("Database error")
        
        # Execute
        results = service.get_user_notifications(user_id=1)
        
        # Assert
        assert results == []
    
    def test_get_unread_count_success(self, service, mock_db_session):
        """Test getting unread notification count."""
        # Setup
        mock_query = Mock()
        mock_query.count.return_value = 7
        mock_db_session.query().filter.return_value = mock_query
        
        # Execute
        result = service.get_unread_count(user_id=1)
        
        # Assert
        assert result == 7
        mock_query.count.assert_called_once()
    
    def test_get_unread_count_with_type_filter(self, service, mock_db_session):
        """Test getting unread count with type filter."""
        # Setup
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.count.return_value = 3
        mock_query.filter.return_value = mock_filter
        mock_db_session.query().filter.return_value = mock_query
        
        # Execute
        result = service.get_unread_count(
            user_id=1,
            type=NotificationType.MESSAGE.value
        )
        
        # Assert
        assert result == 3
        assert mock_query.filter.call_count == 1
    
    def test_get_unread_count_database_error(self, service, mock_db_session):
        """Test getting unread count with database error."""
        # Setup
        mock_db_session.query().filter.side_effect = Exception("Database error")
        
        # Execute
        result = service.get_unread_count(user_id=1)
        
        # Assert
        assert result == 0
    
    def test_serialize_notification_with_sender(self, service, mock_db_session, mock_notification, mock_user):
        """Test notification serialization with sender info."""
        # Setup
        mock_sender = Mock()
        mock_sender.id = 2
        mock_sender.first_name = "Sender"
        mock_sender.last_name = "User"
        mock_sender.email = "sender@example.com"
        mock_db_session.query().filter_by().first.return_value = mock_sender
        
        # Execute
        result = service._serialize_notification(mock_notification)
        
        # Assert
        assert result['id'] == 1
        assert result['sender'] is not None
        assert result['sender']['id'] == 2
        assert result['sender']['name'] == "Sender User"
        assert result['sender']['email'] == "sender@example.com"
    
    def test_serialize_notification_without_sender(self, service, mock_db_session, mock_notification):
        """Test notification serialization without sender."""
        # Setup
        mock_notification.sender_id = None
        
        # Execute
        result = service._serialize_notification(mock_notification)
        
        # Assert
        assert result['sender'] is None
        assert result['sender_id'] is None
    
    def test_notification_with_all_fields(self, service, mock_db_session, mock_user):
        """Test creating notification with all optional fields."""
        # Setup
        mock_db_session.query().filter_by().first.return_value = mock_user
        
        # Execute
        result = service.create_notification(
            user_id=1,
            type=NotificationType.APPOINTMENT.value,
            title="Full Test",
            message="Full message",
            data={"key": "value"},
            related_id=123,
            related_type="appointment",
            sender_id=2,
            priority=NotificationPriority.HIGH.value,
            send_email=True,
            tenant_id=1
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        notification_arg = mock_db_session.add.call_args[0][0]
        assert notification_arg.data == {"key": "value"}
        assert notification_arg.related_id == 123
        assert notification_arg.related_type == "appointment"
        assert notification_arg.sender_id == 2
        assert notification_arg.priority == NotificationPriority.HIGH.value
        assert notification_arg.tenant_id == 1