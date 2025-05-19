#!/usr/bin/env python
"""Test simple beneficiary creation."""

import pytest
import json
from app import create_app
from config import DevelopmentConfig


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(DevelopmentConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers."""
    response = client.post('/api/auth/login', 
                          json={'email': 'test.admin@bdc.com', 'password': 'Test123!'},
                          content_type='application/json')
    
    assert response.status_code == 200, "Failed to login"
    token = json.loads(response.data)['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_simple_beneficiary_creation(client, auth_headers):
    """Test creating a simple beneficiary."""
    beneficiary_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+33123456789'
    }
    
    response = client.post('/api/beneficiaries',
                          json=beneficiary_data,
                          headers=auth_headers,
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['first_name'] == 'John'
    assert data['last_name'] == 'Doe'
    assert data['email'] == 'john.doe@example.com'