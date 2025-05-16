"""Tests for notification endpoints and service."""

import json
from datetime import datetime
import pytest
from app.models import User, Notification
from app.services.notification_service import NotificationService
from app.extensions import db

@pytest.fixture
def setup_notification_data(session, app):
    """Setup test data for notification tests."""
    with app.app_context():
        # Create test users
        user1 = User(
            username='user1',
            email='user1@test.com',
            is_active=True,
            role='user',
            tenant_id=1
        )
        user1.password = 'password123'
        
        user2 = User(
            username='user2',
            email='user2@test.com',
            is_active=True,
            role='admin',
            tenant_id=1
        )
        user2.password = 'password123'
        
        # Create notifications
        notification1 = Notification(
            user_id=user1.id,
            title='Test Notification 1',
            content='This is a test notification',
            type='info',
            priority='low',
            is_read=False,
            tenant_id=1
        )
        
        notification2 = Notification(
            user_id=user1.id,
            title='Test Notification 2',
            content='This is another test notification',
            type='warning',
            priority='medium',
            is_read=True,
            tenant_id=1
        )
        
        notification3 = Notification(
            user_id=user2.id,
            title='Admin Notification',
            content='Admin notification content',
            type='error',
            priority='high',
            is_read=False,
            tenant_id=1
        )
        
        session.add_all([user1, user2, notification1, notification2, notification3])
        session.commit()
        
        return {
            'user1': user1,
            'user2': user2,
            'notification1': notification1,
            'notification2': notification2,
            'notification3': notification3
        }


def test_get_notifications(client, setup_notification_data, app):
    """Test getting user notifications."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user1'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/notifications', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'notifications' in data
        assert len(data['notifications']) == 2
        assert 'pagination' in data


def test_get_unread_notifications(client, setup_notification_data, app):
    """Test getting unread notifications."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user1'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/notifications?unread=true', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'notifications' in data
        assert len(data['notifications']) == 1
        assert data['notifications'][0]['is_read'] == False


def test_get_notification_by_id(client, setup_notification_data, app):
    """Test getting a specific notification."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user1'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        notification_id = setup_notification_data['notification1'].id
        response = client.get(f'/api/notifications/{notification_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == notification_id
        assert data['title'] == 'Test Notification 1'


def test_mark_notification_as_read(client, setup_notification_data, app):
    """Test marking a notification as read."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user1'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        notification_id = setup_notification_data['notification1'].id
        response = client.put(
            f'/api/notifications/{notification_id}/read',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['is_read'] == True


def test_mark_all_notifications_as_read(client, setup_notification_data, app):
    """Test marking all notifications as read."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user1'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.put('/api/notifications/read-all', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['message'] == 'All notifications marked as read'
        assert data['updated_count'] >= 1


def test_delete_notification(client, setup_notification_data, app):
    """Test deleting a notification."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user1'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        notification_id = setup_notification_data['notification1'].id
        response = client.delete(
            f'/api/notifications/{notification_id}',
            headers=headers
        )
        
        assert response.status_code == 204


def test_notification_access_forbidden(client, setup_notification_data, app):
    """Test accessing another user's notification is forbidden."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_notification_data['user2'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Try to access user1's notification
        notification_id = setup_notification_data['notification1'].id
        response = client.get(f'/api/notifications/{notification_id}', headers=headers)
        
        assert response.status_code == 404  # Should not be able to see other user's notifications


def test_notification_service_create(session, setup_notification_data, app):
    """Test notification service create method."""
    with app.app_context():
        service = NotificationService()
        notification = service.create_notification(
            user_id=setup_notification_data['user1'].id,
            title='Service Test Notification',
            content='Created via service',
            type='info',
            priority='medium'
        )
        
        assert notification is not None
        assert notification.title == 'Service Test Notification'
        assert notification.user_id == setup_notification_data['user1'].id
        assert notification.is_read == False


def test_notification_service_bulk_create(session, app):
    """Test notification service bulk create method."""
    with app.app_context():
        # Create multiple users
        users = []
        for i in range(3):
            user = User(
                username=f'bulk_user_{i}',
                email=f'bulk{i}@test.com',
                is_active=True,
                role='user',
                tenant_id=1
            )
            user.password = 'password123'
            users.append(user)
        
        session.add_all(users)
        session.commit()
        
        user_ids = [u.id for u in users]
        
        service = NotificationService()
        notifications = service.create_bulk_notifications(
            user_ids=user_ids,
            title='Bulk Notification',
            content='Sent to multiple users',
            type='info',
            priority='low'
        )
        
        assert len(notifications) == 3
        for notification in notifications:
            assert notification.title == 'Bulk Notification'
            assert notification.user_id in user_ids