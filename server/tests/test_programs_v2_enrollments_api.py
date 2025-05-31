"""Test the /programs/<id>/enrollments and /programs/<id>/students API endpoints."""

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
def trainer_client():
    """Create test client with tenant_admin authentication."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    # Login as tenant admin (has program creation permission)
    response = client.post('/api/auth/login', json={
        'email': 'tenant@bdc.com',
        'password': 'Tenant123!'
    })
    
    token = json.loads(response.data)['access_token']
    return client, token


@pytest.fixture()
def student_client():
    """Create test client with student authentication."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    # Login as student
    response = client.post('/api/auth/login', json={
        'email': 'student@bdc.com',
        'password': 'Student123!'
    })
    
    token = json.loads(response.data)['access_token']
    return client, token


def test_get_program_enrollments_unauthorized(student_client, trainer_client):
    """Test unauthorized access to program enrollments."""
    # First create a program using trainer (admin) account
    trainer_cli, trainer_token = trainer_client
    program_data = {
        'name': 'Test Program',
        'description': 'Test program for auth test',
        'category': 'technical',
        'level': 'beginner',
        'status': 'active',
        'duration': 14
    }
    
    response = trainer_cli.post(
        '/api/programs',
        json=program_data,
        headers={'Authorization': f'Bearer {trainer_token}'}
    )
    
    assert response.status_code == 201
    program = json.loads(response.data)
    
    # Now try to access enrollments as student (should fail)
    client, token = student_client
    response = client.get(
        f'/api/programs/{program["id"]}/enrollments',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 403


def test_get_program_enrollments_authorized(trainer_client):
    """Test authorized access to program enrollments."""
    client, token = trainer_client
    
    # First create a program
    program_data = {
        'name': 'Test Program',
        'description': 'Test program for enrollments',
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
    
    # Get enrollments (should be empty)
    response = client.get(
        f'/api/programs/{program["id"]}/enrollments',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    enrollments = json.loads(response.data)
    assert isinstance(enrollments, list)
    assert len(enrollments) == 0


def test_get_program_students_unauthorized(student_client, trainer_client):
    """Test unauthorized access to program students."""
    # First create a program using trainer (admin) account
    trainer_cli, trainer_token = trainer_client
    program_data = {
        'name': 'Test Program for Students',
        'description': 'Test program for student auth test',
        'category': 'technical',
        'level': 'beginner',
        'status': 'active',
        'duration': 14
    }
    
    response = trainer_cli.post(
        '/api/programs',
        json=program_data,
        headers={'Authorization': f'Bearer {trainer_token}'}
    )
    
    assert response.status_code == 201
    program = json.loads(response.data)
    
    # Now try to access students as student (should fail)
    client, token = student_client
    response = client.get(
        f'/api/programs/{program["id"]}/students',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 403


def test_get_program_students_authorized(trainer_client):
    """Test authorized access to program students."""
    client, token = trainer_client
    
    # First create a program
    program_data = {
        'name': 'Test Program Students',
        'description': 'Test program for students',
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


def test_get_program_enrollments_nonexistent(trainer_client):
    """Test accessing enrollments for non-existent program."""
    client, token = trainer_client
    
    # Try to access non-existent program
    response = client.get(
        '/api/programs/9999/enrollments',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404


def test_get_program_students_nonexistent(trainer_client):
    """Test accessing students for non-existent program."""
    client, token = trainer_client
    
    # Try to access non-existent program
    response = client.get(
        '/api/programs/9999/students',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404


def test_enrollments_without_token():
    """Test accessing enrollments without authentication token."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    response = client.get('/api/programs/1/enrollments')
    assert response.status_code == 401


def test_students_without_token():
    """Test accessing students without authentication token."""
    app = create_app(TestingConfig)
    client = app.test_client()
    
    response = client.get('/api/programs/1/students')
    assert response.status_code == 401