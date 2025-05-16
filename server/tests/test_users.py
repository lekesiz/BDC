"""Tests for user endpoints."""

import json
from unittest.mock import patch


def test_get_users(client, auth_headers):
    """Test getting list of users."""
    # Mock user service
    with patch('app.api.users.user_service.get_users') as mock_get_users:
        # Configure the mock to return a list of users
        mock_get_users.return_value = [
            {'id': 1, 'email': 'user1@example.com', 'name': 'User One', 'role': 'user'},
            {'id': 2, 'email': 'user2@example.com', 'name': 'User Two', 'role': 'admin'},
        ]
        
        # Send request
        response = client.get(
            '/api/users',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['email'] == 'user1@example.com'


def test_get_user(client, auth_headers):
    """Test getting a specific user."""
    # Mock user service
    with patch('app.api.users.user_service.get_user_by_id') as mock_get_user:
        # Configure the mock to return a user
        mock_get_user.return_value = {
            'id': 1, 
            'email': 'user1@example.com', 
            'name': 'User One', 
            'role': 'user'
        }
        
        # Send request
        response = client.get(
            '/api/users/1',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert response.json['email'] == 'user1@example.com'


def test_create_user(client, auth_headers):
    """Test creating a new user."""
    # Mock user service
    with patch('app.api.users.user_service.create_user') as mock_create_user:
        # Configure the mock to return a new user
        mock_create_user.return_value = {
            'id': 3, 
            'email': 'newuser@example.com', 
            'name': 'New User', 
            'role': 'user'
        }
        
        # Send request
        response = client.post(
            '/api/users',
            data=json.dumps({
                'email': 'newuser@example.com',
                'password': 'password123',
                'name': 'New User',
                'role': 'user'
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 201
        assert response.json['email'] == 'newuser@example.com'


def test_update_user(client, auth_headers):
    """Test updating a user."""
    # Mock user service
    with patch('app.api.users.user_service.update_user') as mock_update_user:
        # Configure the mock to return an updated user
        mock_update_user.return_value = {
            'id': 1, 
            'email': 'user1@example.com', 
            'name': 'Updated Name', 
            'role': 'user'
        }
        
        # Send request
        response = client.put(
            '/api/users/1',
            data=json.dumps({
                'name': 'Updated Name',
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert response.json['name'] == 'Updated Name'


def test_delete_user(client, auth_headers):
    """Test deleting a user."""
    # Mock user service
    with patch('app.api.users.user_service.delete_user') as mock_delete_user:
        # Configure the mock to return success
        mock_delete_user.return_value = True
        
        # Send request
        response = client.delete(
            '/api/users/1',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert 'message' in response.json