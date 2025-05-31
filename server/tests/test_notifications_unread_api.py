"""Tests for notifications unread API."""

import pytest
from unittest.mock import Mock, patch
from flask import Flask

from app.api.notifications_unread import notifications_unread_bp


class TestNotificationsUnreadAPI:
    """Test the notifications unread API."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        app.register_blueprint(notifications_unread_bp, url_prefix='/api/notifications')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    @patch('app.api.notifications_unread.get_jwt_identity')
    @patch('app.api.notifications_unread.Notification')
    def test_get_unread_count(self, mock_notification, mock_get_identity, client):
        """Test getting unread notifications count."""
        # Setup mocks
        mock_get_identity.return_value = 1
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.count.return_value = 5
        mock_notification.query = mock_query
        
        # Make request
        with patch('flask_jwt_extended.verify_jwt_in_request'):
            response = client.get('/api/notifications/unread-count')
        
        # Verify
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 5
        
        # Verify the query was called correctly
        mock_query.filter_by.assert_called_once_with(
            user_id=1,
            read=False
        )
    
    @patch('app.api.notifications_unread.get_jwt_identity')
    @patch('app.api.notifications_unread.Notification')
    def test_get_unread_count_zero(self, mock_notification, mock_get_identity, client):
        """Test getting unread notifications count when zero."""
        # Setup mocks
        mock_get_identity.return_value = 2
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.count.return_value = 0
        mock_notification.query = mock_query
        
        # Make request
        with patch('flask_jwt_extended.verify_jwt_in_request'):
            response = client.get('/api/notifications/unread-count')
        
        # Verify
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 0