"""Test the /programs/<id>/students API endpoint."""

import json
import pytest

from app import create_app
from config import TestingConfig


@pytest.fixture()
def auth_client():
    """Create test client with admin authentication."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    # Login as admin
    response = client.post('/api/auth/login', json={
        'email': 'admin@bdc.com',
        'password': 'Admin123!'
    })
    
    token = json.loads(response.data)['access_token']
    return client, token


@pytest.fixture()
def tenant_client():
    """Create test client with tenant_admin authentication."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    # Login as tenant admin
    response = client.post('/api/auth/login', json={
        'email': 'tenant@bdc.com',
        'password': 'Tenant123!'
    })
    
    token = json.loads(response.data)['access_token']
    return client, token


def test_list_program_students_unauthorized(auth_client):
    """Test unauthorized access to student list."""
    client, _ = auth_client
    
    # Try to access endpoint without token
    response = client.get('/api/programs/1/students')
    assert response.status_code == 401


def test_list_program_students_nonexistent(auth_client):
    """Test accessing students for non-existent program."""
    client, token = auth_client
    
    # Try to access non-existent program
    response = client.get(
        '/api/programs/9999/students',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404


def test_list_program_students_wrong_tenant(tenant_client, auth_client):
    """Test accessing program from wrong tenant."""
    # First, create a program with the super_admin
    admin_client, admin_token = auth_client
    
    # Create a program
    program_data = {
        'name': 'Admin Program',
        'description': 'Program created by admin',
        'category': 'technical',
        'level': 'intermediate',
        'status': 'active',
        'duration': 30
    }
    
    response = admin_client.post(
        '/api/programs',
        json=program_data,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    assert response.status_code == 201
    program = json.loads(response.data)
    
    # Now try to access this program with tenant_admin
    tenant_client, tenant_token = tenant_client
    
    response = tenant_client.get(
        f'/api/programs/{program["id"]}/students',
        headers={'Authorization': f'Bearer {tenant_token}'}
    )
    
    # Should be forbidden since program belongs to different tenant
    assert response.status_code == 403


def test_list_program_students_empty(auth_client):
    """Test getting empty student list."""
    client, token = auth_client
    
    # Create a program
    program_data = {
        'name': 'Test Program',
        'description': 'Program with no students',
        'category': 'technical',
        'level': 'beginner',
        'status': 'active',
        'duration': 14
    }
    
    response = client.post(
        '/api/programs',
        json=program_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 201
    program = json.loads(response.data)
    
    # Get students (should be empty)
    response = client.get(
        f'/api/programs/{program["id"]}/students',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    students = json.loads(response.data)
    assert isinstance(students, list)
    assert len(students) == 0