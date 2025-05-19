#!/usr/bin/env python
"""Test beneficiaries endpoint with sorting."""

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


def test_beneficiaries_sorting(client, auth_headers):
    """Test beneficiaries endpoint with sorting parameters."""
    params = {
        'page': 1,
        'per_page': 10,
        'sort_by': 'created_at',
        'sort_dir': 'desc'
    }
    
    response = client.get('/api/beneficiaries',
                         query_string=params,
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'beneficiaries' in data
    assert 'total' in data