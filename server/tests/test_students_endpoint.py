"""Test the /programs/<id>/students endpoint independently."""

import json
import pytest

from app import create_app
from config import TestingConfig


@pytest.fixture
def auth_client():
    """Create an authenticated client."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    # Login as admin
    response = client.post('/api/auth/login', json={
        'email': 'admin@bdc.com',
        'password': 'Admin123!'
    })
    
    token = json.loads(response.data)['access_token']
    return client, token


def test_unauthorized_access(auth_client):
    """Test that unauthorized access is properly rejected."""
    client, _ = auth_client
    
    # Try accessing without token
    response = client.get('/api/programs/1/students')
    assert response.status_code == 401


def test_nonexistent_program(auth_client):
    """Test accessing a nonexistent program."""
    client, token = auth_client
    
    # Try accessing a nonexistent program
    response = client.get(
        '/api/programs/9999/students',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404