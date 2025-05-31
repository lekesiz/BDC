"""Tests for the refactored notifications API endpoints."""

import pytest
import json
from unittest.mock import Mock, patch
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.container import get_container
from app.models.user import User
from app.models.notification import Notification


class TestNotificationsAPIRefactored:
    """Test class for refactored notifications API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create and configure a test Flask application."""
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client for the Flask application."""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        """Create authorization headers with a valid JWT token."""
        with app.app_context():
            token = create_access_token(identity=1)
            return {'Authorization': f'Bearer {token}'}
    
    @pytest.fixture
    def mock_notification_service(self):
        """Create a mock notification service."""
        return Mock()
    
    @pytest.fixture(autouse=True)
    def setup_container(self, app, mock_notification_service):
        """Set up the DI container with mock services."""
        with app.app_context():
            container = get_container()
            # Override the notification service with mock
            container.register('notification_service', lambda: mock_notification_service, singleton=True)
            yield
            # Clean up after test
            container.clear_singletons()
    
    def test_get_notifications(self, client, auth_headers, mock_notification_service):
        """Test getting user notifications."""
        # Arrange
        mock_notifications = [
            {'id': 1, 'title': 'Notification 1'},
            {'id': 2, 'title': 'Notification 2'}
        ]
        mock_notification_service.get_user_notifications.return_value = mock_notifications
        mock_notification_service.get_unread_count.return_value = 5
        
        # Act
        response = client.get('/api/notifications', headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['notifications'] == mock_notifications
        assert data['unread_count'] == 5
        assert data['limit'] == 20
        assert data['offset'] == 0
        
        mock_notification_service.get_user_notifications.assert_called_once_with(
            user_id=1,
            limit=20,
            offset=0,
            unread_only=False,
            type=None
        )
    
    def test_get_notifications_with_params(self, client, auth_headers, mock_notification_service):
        """Test getting notifications with query parameters."""
        # Arrange
        mock_notification_service.get_user_notifications.return_value = []
        mock_notification_service.get_unread_count.return_value = 0
        
        # Act
        response = client.get(
            '/api/notifications?limit=10&offset=5&unread_only=true&type=info',
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        
        mock_notification_service.get_user_notifications.assert_called_once_with(
            user_id=1,
            limit=10,
            offset=5,
            unread_only=True,
            type='info'
        )
    
    def test_get_unread_count(self, client, auth_headers, mock_notification_service):
        """Test getting unread notification count."""
        # Arrange
        mock_notification_service.get_unread_count.return_value = 7
        
        # Act
        response = client.get('/api/notifications/unread-count', headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['unread_count'] == 7
        
        mock_notification_service.get_unread_count.assert_called_once_with(1)
    
    def test_mark_notification_as_read(self, client, auth_headers, mock_notification_service):
        """Test marking a notification as read."""
        # Arrange
        mock_notification_service.mark_as_read.return_value = True
        
        # Act
        response = client.post('/api/notifications/1/read', headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Notification marked as read'
        
        mock_notification_service.mark_as_read.assert_called_once_with(1, 1)
    
    def test_mark_notification_as_read_not_found(self, client, auth_headers, mock_notification_service):
        """Test marking non-existent notification as read."""
        # Arrange
        mock_notification_service.mark_as_read.return_value = False
        
        # Act
        response = client.post('/api/notifications/999/read', headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'notification_not_found'
    
    def test_mark_all_notifications_as_read(self, client, auth_headers, mock_notification_service):
        """Test marking all notifications as read."""
        # Arrange
        mock_notification_service.mark_all_as_read.return_value = 5
        
        # Act
        response = client.post(
            '/api/notifications/read-all',
            headers=auth_headers,
            json={'type': 'info'}
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == '5 notifications marked as read'
        
        mock_notification_service.mark_all_as_read.assert_called_once_with(1, 'info')
    
    def test_delete_notification(self, client, auth_headers, mock_notification_service):
        """Test deleting a notification."""
        # Arrange
        mock_notification_service.delete_notification.return_value = True
        
        # Act
        response = client.delete('/api/notifications/1', headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Notification deleted'
        
        mock_notification_service.delete_notification.assert_called_once_with(1, 1)
    
    def test_delete_notification_not_found(self, client, auth_headers, mock_notification_service):
        """Test deleting non-existent notification."""
        # Arrange
        mock_notification_service.delete_notification.return_value = False
        
        # Act
        response = client.delete('/api/notifications/999', headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'notification_not_found'
    
    def test_create_notification(self, client, auth_headers, mock_notification_service):
        """Test creating a notification."""
        # Arrange
        mock_notification = Mock()
        mock_notification.to_dict.return_value = {'id': 1, 'title': 'New Notification'}
        mock_notification_service.create_notification.return_value = mock_notification
        
        request_data = {
            'title': 'Test Notification',
            'message': 'This is a test',
            'type': 'info',
            'priority': 'high'
        }
        
        # Act
        response = client.post(
            '/api/notifications',
            headers=auth_headers,
            json=request_data
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Notification created successfully'
        assert data['notification']['id'] == 1
        
        mock_notification_service.create_notification.assert_called_once()
    
    def test_create_notification_missing_fields(self, client, auth_headers):
        """Test creating notification with missing required fields."""
        # Act
        response = client.post(
            '/api/notifications',
            headers=auth_headers,
            json={'type': 'info'}
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'
        assert 'Title and message are required' in data['message']
    
    def test_create_bulk_notifications(self, client, auth_headers, mock_notification_service):
        """Test creating bulk notifications."""
        # Arrange
        mock_notifications = [Mock(), Mock()]
        mock_notification_service.create_bulk_notifications.return_value = mock_notifications
        
        request_data = {
            'user_ids': [1, 2, 3],
            'title': 'Bulk Notification',
            'message': 'This is a bulk notification',
            'type': 'announcement'
        }
        
        # Act
        response = client.post(
            '/api/notifications/bulk',
            headers=auth_headers,
            json=request_data
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == '2 notifications created'
        assert data['count'] == 2
    
    def test_create_bulk_notifications_invalid_user_ids(self, client, auth_headers):
        """Test creating bulk notifications with invalid user IDs."""
        # Act
        response = client.post(
            '/api/notifications/bulk',
            headers=auth_headers,
            json={'user_ids': 'invalid', 'title': 'Test', 'message': 'Test'}
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'
        assert 'user_ids must be a non-empty list' in data['message']
    
    def test_create_role_notification(self, client, auth_headers, mock_notification_service):
        """Test creating role-based notification."""
        # Arrange
        mock_notifications = [Mock(), Mock(), Mock()]
        mock_notification_service.create_role_notification.return_value = mock_notifications
        
        request_data = {
            'role': 'admin',
            'title': 'Admin Notification',
            'message': 'This is for all admins',
            'type': 'system'
        }
        
        # Act
        response = client.post(
            '/api/notifications/role',
            headers=auth_headers,
            json=request_data
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == '3 notifications created for role: admin'
        assert data['count'] == 3
    
    def test_create_role_notification_missing_role(self, client, auth_headers):
        """Test creating role notification without role."""
        # Act
        response = client.post(
            '/api/notifications/role',
            headers=auth_headers,
            json={'title': 'Test', 'message': 'Test'}
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'
        assert 'Role is required' in data['message']
    
    def test_create_tenant_notification(self, client, auth_headers, mock_notification_service):
        """Test creating tenant-based notification."""
        # Arrange
        mock_notifications = [Mock(), Mock(), Mock(), Mock()]
        mock_notification_service.create_tenant_notification.return_value = mock_notifications
        
        request_data = {
            'tenant_id': 123,
            'title': 'Tenant Notification',
            'message': 'This is for all tenant users',
            'type': 'announcement',
            'exclude_roles': ['super_admin']
        }
        
        # Act
        response = client.post(
            '/api/notifications/tenant',
            headers=auth_headers,
            json=request_data
        )
        
        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == '4 notifications created for tenant: 123'
        assert data['count'] == 4
    
    def test_create_tenant_notification_missing_tenant_id(self, client, auth_headers):
        """Test creating tenant notification without tenant_id."""
        # Act
        response = client.post(
            '/api/notifications/tenant',
            headers=auth_headers,
            json={'title': 'Test', 'message': 'Test'}
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_error'
        assert 'tenant_id is required' in data['message']
    
    def test_unauthorized_request(self, client):
        """Test accessing endpoints without authentication."""
        # Act
        response = client.get('/api/notifications')
        
        # Assert
        assert response.status_code == 401