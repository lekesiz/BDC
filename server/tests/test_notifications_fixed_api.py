"""Comprehensive tests for the fixed notifications API endpoints."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import g
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.notification import Notification


class TestNotificationsFixedAPI:
    """Test suite for the fixed notifications API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, app, client):
        """Set up test environment."""
        self.app = app
        self.client = client
        
        # Create test users
        with self.app.app_context():
            self.super_admin = User(
                email='superadmin@test.com',
                username='superadmin',
                first_name='Super',
                last_name='Admin',
                role='super_admin',
                is_active=True
            )
            self.super_admin.set_password('password123')
            
            self.tenant_admin = User(
                email='tenantadmin@test.com',
                username='tenantadmin',
                first_name='Tenant',
                last_name='Admin',
                role='tenant_admin',
                is_active=True
            )
            self.tenant_admin.set_password('password123')
            
            self.regular_user = User(
                email='user@test.com',
                username='user',
                first_name='Regular',
                last_name='User',
                role='student',
                is_active=True
            )
            self.regular_user.set_password('password123')
            
            self.inactive_user = User(
                email='inactive@test.com',
                username='inactive',
                first_name='Inactive',
                last_name='User',
                role='student',
                is_active=False
            )
            self.inactive_user.set_password('password123')
            
            db.session.add_all([self.super_admin, self.tenant_admin, self.regular_user, self.inactive_user])
            db.session.commit()
            
            # Create access tokens
            self.super_admin_token = create_access_token(identity=self.super_admin.id)
            self.tenant_admin_token = create_access_token(identity=self.tenant_admin.id)
            self.regular_user_token = create_access_token(identity=self.regular_user.id)
            
            # Mock notification service
            self.mock_notification_service = Mock()
            
            # Patch get_container to return mock service
            self.patcher = patch('app.api.notifications_fixed.get_container')
            self.mock_get_container = self.patcher.start()
            self.mock_container = Mock()
            self.mock_container.resolve.return_value = self.mock_notification_service
            self.mock_get_container.return_value = self.mock_container
    
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'patcher'):
            self.patcher.stop()
        
        # Clear g
        with self.app.app_context():
            if hasattr(g, '_notification_service'):
                delattr(g, '_notification_service')
    
    def test_get_notifications_success(self):
        """Test successfully getting notifications."""
        # Mock service response
        mock_notifications = [
            {'id': 1, 'title': 'Test 1', 'message': 'Message 1', 'read': False},
            {'id': 2, 'title': 'Test 2', 'message': 'Message 2', 'read': True}
        ]
        self.mock_notification_service.get_user_notifications.return_value = mock_notifications
        self.mock_notification_service.get_unread_count.return_value = 1
        
        response = self.client.get(
            '/api/notifications',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['notifications'] == mock_notifications
        assert data['unread_count'] == 1
        assert data['limit'] == 20
        assert data['offset'] == 0
        assert data['total'] == 2
        
        # Verify service was called correctly
        self.mock_notification_service.get_user_notifications.assert_called_once_with(
            user_id=self.regular_user.id,
            limit=20,
            offset=0,
            unread_only=False,
            type=None
        )
    
    def test_get_notifications_with_filters(self):
        """Test getting notifications with query parameters."""
        self.mock_notification_service.get_user_notifications.return_value = []
        self.mock_notification_service.get_unread_count.return_value = 0
        
        response = self.client.get(
            '/api/notifications?limit=10&offset=5&unread_only=true&type=system',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify service was called with correct parameters
        self.mock_notification_service.get_user_notifications.assert_called_once_with(
            user_id=self.regular_user.id,
            limit=10,
            offset=5,
            unread_only=True,
            type='system'
        )
    
    def test_get_notifications_unauthorized(self):
        """Test getting notifications without authentication."""
        response = self.client.get('/api/notifications')
        assert response.status_code == 401
    
    def test_get_unread_count_success(self):
        """Test getting unread notification count."""
        self.mock_notification_service.get_unread_count.return_value = 5
        
        response = self.client.get(
            '/api/notifications/unread-count',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['unread_count'] == 5
        
        self.mock_notification_service.get_unread_count.assert_called_once_with(
            self.regular_user.id
        )
    
    def test_mark_notification_as_read_success(self):
        """Test marking a notification as read."""
        self.mock_notification_service.mark_as_read.return_value = True
        
        response = self.client.post(
            '/api/notifications/123/read',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Notification marked as read'
        
        self.mock_notification_service.mark_as_read.assert_called_once_with(
            123, self.regular_user.id
        )
    
    def test_mark_notification_as_read_not_found(self):
        """Test marking a non-existent notification as read."""
        self.mock_notification_service.mark_as_read.return_value = False
        
        response = self.client.post(
            '/api/notifications/999/read',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'notification_not_found'
    
    def test_mark_all_notifications_as_read_success(self):
        """Test marking all notifications as read."""
        self.mock_notification_service.mark_all_as_read.return_value = 10
        
        response = self.client.post(
            '/api/notifications/read-all',
            headers={'Authorization': f'Bearer {self.regular_user_token}'},
            json={'type': 'system'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '10 notifications marked as read'
        
        self.mock_notification_service.mark_all_as_read.assert_called_once_with(
            self.regular_user.id, 'system'
        )
    
    def test_mark_all_notifications_as_read_no_type(self):
        """Test marking all notifications as read without type filter."""
        self.mock_notification_service.mark_all_as_read.return_value = 5
        
        response = self.client.post(
            '/api/notifications/read-all',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 200
        
        self.mock_notification_service.mark_all_as_read.assert_called_once_with(
            self.regular_user.id, None
        )
    
    def test_delete_notification_success(self):
        """Test deleting a notification."""
        self.mock_notification_service.delete_notification.return_value = True
        
        response = self.client.delete(
            '/api/notifications/123',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Notification deleted'
        
        self.mock_notification_service.delete_notification.assert_called_once_with(
            123, self.regular_user.id
        )
    
    def test_delete_notification_not_found(self):
        """Test deleting a non-existent notification."""
        self.mock_notification_service.delete_notification.return_value = False
        
        response = self.client.delete(
            '/api/notifications/999',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == 'notification_not_found'
    
    @patch('app.api.notifications_fixed.current_app')
    def test_create_test_notification_development(self, mock_current_app):
        """Test creating a test notification in development mode."""
        mock_current_app.config.get.return_value = 'development'
        
        mock_notification = Mock()
        mock_notification.to_dict.return_value = {'id': 1, 'title': 'Test'}
        self.mock_notification_service.create_notification.return_value = mock_notification
        
        with self.app.app_context():
            response = self.client.post(
                '/api/notifications/test',
                headers={'Authorization': f'Bearer {self.regular_user_token}'},
                json={'send_email': True}
            )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Test notification created'
        assert data['notification'] == {'id': 1, 'title': 'Test'}
        
        self.mock_notification_service.create_notification.assert_called_once()
        call_args = self.mock_notification_service.create_notification.call_args[1]
        assert call_args['user_id'] == self.regular_user.id
        assert call_args['type'] == 'test'
        assert call_args['title'] == 'Test Notification'
        assert call_args['send_email'] is True
    
    @patch('app.api.notifications_fixed.current_app')
    def test_create_test_notification_production(self, mock_current_app):
        """Test creating a test notification is blocked in production."""
        mock_current_app.config.get.return_value = 'production'
        
        with self.app.app_context():
            response = self.client.post(
                '/api/notifications/test',
                headers={'Authorization': f'Bearer {self.regular_user_token}'}
            )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == 'not_allowed'
    
    def test_send_notification_success(self):
        """Test sending a notification."""
        mock_notification = Mock()
        mock_notification.to_dict.return_value = {'id': 1, 'title': 'Sent'}
        self.mock_notification_service.create_notification.return_value = mock_notification
        
        response = self.client.post(
            '/api/notifications/send',
            headers={'Authorization': f'Bearer {self.regular_user_token}'},
            json={
                'type': 'info',
                'title': 'Test Title',
                'message': 'Test Message',
                'data': {'key': 'value'},
                'priority': 'high',
                'send_email': True
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Notification sent successfully'
        
        self.mock_notification_service.create_notification.assert_called_once()
        call_args = self.mock_notification_service.create_notification.call_args[1]
        assert call_args['user_id'] == self.regular_user.id  # Sending to self
        assert call_args['type'] == 'info'
        assert call_args['title'] == 'Test Title'
        assert call_args['message'] == 'Test Message'
        assert call_args['sender_id'] == self.regular_user.id
        assert call_args['priority'] == 'high'
        assert call_args['send_email'] is True
    
    def test_send_notification_to_other_user(self):
        """Test sending a notification to another user."""
        mock_notification = Mock()
        mock_notification.to_dict.return_value = {'id': 1}
        self.mock_notification_service.create_notification.return_value = mock_notification
        
        response = self.client.post(
            '/api/notifications/send',
            headers={'Authorization': f'Bearer {self.regular_user_token}'},
            json={
                'recipient_id': self.tenant_admin.id,
                'type': 'message',
                'title': 'New Message',
                'message': 'You have a new message'
            }
        )
        
        assert response.status_code == 201
        
        call_args = self.mock_notification_service.create_notification.call_args[1]
        assert call_args['user_id'] == self.tenant_admin.id
        assert call_args['sender_id'] == self.regular_user.id
    
    def test_send_notification_invalid_data(self):
        """Test sending a notification with invalid data."""
        response = self.client.post(
            '/api/notifications/send',
            headers={'Authorization': f'Bearer {self.regular_user_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'invalid_request'
    
    def test_send_notification_failure(self):
        """Test handling notification creation failure."""
        self.mock_notification_service.create_notification.return_value = None
        
        response = self.client.post(
            '/api/notifications/send',
            headers={'Authorization': f'Bearer {self.regular_user_token}'},
            json={'title': 'Test'}
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['error'] == 'notification_creation_failed'
    
    def test_broadcast_notification_as_super_admin(self):
        """Test broadcasting notification as super admin."""
        mock_notification = Mock()
        self.mock_notification_service.create_notification.return_value = mock_notification
        
        with self.app.app_context():
            response = self.client.post(
                '/api/notifications/broadcast',
                headers={'Authorization': f'Bearer {self.super_admin_token}'},
                json={
                    'type': 'announcement',
                    'title': 'System Update',
                    'message': 'System will be updated tonight',
                    'priority': 'high',
                    'send_email': True
                }
            )
        
        assert response.status_code == 201
        data = response.get_json()
        # 3 active users (super_admin, tenant_admin, regular_user)
        assert 'Broadcast sent to' in data['message']
        assert data['count'] == 3
    
    def test_broadcast_notification_as_tenant_admin(self):
        """Test broadcasting notification as tenant admin."""
        mock_notification = Mock()
        self.mock_notification_service.create_notification.return_value = mock_notification
        
        with self.app.app_context():
            response = self.client.post(
                '/api/notifications/broadcast',
                headers={'Authorization': f'Bearer {self.tenant_admin_token}'},
                json={'title': 'Tenant Update'}
            )
        
        assert response.status_code == 201
    
    def test_broadcast_notification_as_regular_user(self):
        """Test regular user cannot broadcast notifications."""
        response = self.client.post(
            '/api/notifications/broadcast',
            headers={'Authorization': f'Bearer {self.regular_user_token}'},
            json={'title': 'Unauthorized Broadcast'}
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == 'not_authorized'
    
    def test_broadcast_notification_invalid_data(self):
        """Test broadcasting with invalid data."""
        response = self.client.post(
            '/api/notifications/broadcast',
            headers={'Authorization': f'Bearer {self.super_admin_token}'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'invalid_request'
    
    def test_admin_create_notification_as_super_admin(self):
        """Test admin creating notification for another user."""
        mock_notification = Mock()
        mock_notification.to_dict.return_value = {'id': 1}
        self.mock_notification_service.create_notification.return_value = mock_notification
        
        response = self.client.post(
            '/api/admin/notifications',
            headers={'Authorization': f'Bearer {self.super_admin_token}'},
            json={
                'user_id': self.regular_user.id,
                'type': 'system',
                'title': 'Admin Notification',
                'message': 'This is from admin',
                'priority': 'high',
                'send_email': True,
                'tenant_id': 1
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Notification created'
        
        call_args = self.mock_notification_service.create_notification.call_args[1]
        assert call_args['user_id'] == self.regular_user.id
        assert call_args['sender_id'] == self.super_admin.id
        assert call_args['tenant_id'] == 1
    
    def test_admin_create_notification_as_regular_user(self):
        """Test regular user cannot use admin endpoint."""
        response = self.client.post(
            '/api/admin/notifications',
            headers={'Authorization': f'Bearer {self.regular_user_token}'},
            json={'user_id': 1}
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == 'not_authorized'
    
    def test_admin_create_notification_missing_user_id(self):
        """Test admin endpoint requires user_id."""
        response = self.client.post(
            '/api/admin/notifications',
            headers={'Authorization': f'Bearer {self.super_admin_token}'},
            json={'title': 'Missing User ID'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'user_id_required'
    
    def test_admin_create_bulk_notifications_success(self):
        """Test creating bulk notifications."""
        mock_notifications = [Mock(), Mock()]
        self.mock_notification_service.create_bulk_notifications.return_value = mock_notifications
        
        response = self.client.post(
            '/api/admin/notifications/bulk',
            headers={'Authorization': f'Bearer {self.super_admin_token}'},
            json={
                'user_ids': [1, 2, 3],
                'type': 'announcement',
                'title': 'Bulk Notification',
                'message': 'This goes to multiple users',
                'send_email': False
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == '2 notifications created'
        
        self.mock_notification_service.create_bulk_notifications.assert_called_once()
        call_args = self.mock_notification_service.create_bulk_notifications.call_args[1]
        assert call_args['user_ids'] == [1, 2, 3]
        assert call_args['type'] == 'announcement'
    
    def test_admin_create_bulk_notifications_invalid_user_ids(self):
        """Test bulk notifications with invalid user_ids."""
        response = self.client.post(
            '/api/admin/notifications/bulk',
            headers={'Authorization': f'Bearer {self.super_admin_token}'},
            json={'user_ids': 'not-a-list'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'user_ids_required'
    
    def test_admin_create_role_notification_success(self):
        """Test creating notification for all users with a role."""
        mock_notifications = [Mock(), Mock(), Mock()]
        self.mock_notification_service.create_role_notification.return_value = mock_notifications
        
        response = self.client.post(
            '/api/admin/notifications/role',
            headers={'Authorization': f'Bearer {self.super_admin_token}'},
            json={
                'role': 'student',
                'type': 'info',
                'title': 'Student Announcement',
                'message': 'All students please note',
                'priority': 'normal'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == '3 notifications created for students'
        
        self.mock_notification_service.create_role_notification.assert_called_once()
        call_args = self.mock_notification_service.create_role_notification.call_args[1]
        assert call_args['role'] == 'student'
        assert call_args['sender_id'] == self.super_admin.id
    
    def test_admin_create_role_notification_missing_role(self):
        """Test role notification requires role parameter."""
        response = self.client.post(
            '/api/admin/notifications/role',
            headers={'Authorization': f'Bearer {self.super_admin_token}'},
            json={'title': 'Missing Role'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'role_required'
    
    def test_notification_service_caching(self):
        """Test that notification service is cached in g."""
        with self.app.app_context():
            # First call should create the service
            from app.api.notifications_fixed import get_notification_service
            service1 = get_notification_service()
            
            # Second call should return the same instance
            service2 = get_notification_service()
            
            assert service1 is service2
            assert hasattr(g, '_notification_service')
            
            # Verify container was only called once
            self.mock_get_container.assert_called_once()
            self.mock_container.resolve.assert_called_once_with('notification_service')