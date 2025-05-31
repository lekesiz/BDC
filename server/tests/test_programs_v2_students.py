"""Tests for the /programs/<id>/students endpoint."""

import json
import pytest
from app import create_app, db
from config import TestingConfig
from app.models.user import User
from app.models.tenant import Tenant
from app.models.program import Program, ProgramEnrollment
from app.models.beneficiary import Beneficiary


@pytest.fixture()
def auth_client():
    """Create test client with authentication token."""
    app = create_app(TestingConfig)
    
    client = app.test_client()
    
    # Login to get admin token
    response = client.post('/api/auth/login', json={
        'email': 'admin@bdc.com',
        'password': 'Admin123!'
    })
    
    token = json.loads(response.data)['access_token']
    return client, token


@pytest.fixture()
def setup_test_data():
    """Set up test data for program students tests."""
    app = create_app(TestingConfig)
    with app.app_context():
        # Create test tenant
        tenant = Tenant(
            name="Test Tenant", 
            slug="test-tenant",
            email="test@tenant.com"
        )
        db.session.add(tenant)
        db.session.commit()
        
        # Create users
        admin = User(
            email="test_admin@bdc.com",
            password="Admin123!",
            first_name="Test",
            last_name="Admin",
            role="super_admin",
            tenant_id=tenant.id
        )
        
        user1 = User(
            email="student1@bdc.com",
            password="Password123!",
            first_name="Student",
            last_name="One",
            role="user",
            tenant_id=tenant.id
        )
        
        user2 = User(
            email="student2@bdc.com",
            password="Password123!",
            first_name="Student",
            last_name="Two",
            role="user",
            tenant_id=tenant.id
        )
        
        db.session.add_all([admin, user1, user2])
        db.session.commit()
        
        # Create program
        program = Program(
            name="Test Program",
            description="Test program description",
            duration=30,
            level="beginner",
            category="technical",
            status="active",
            tenant_id=tenant.id,
            created_by_id=admin.id
        )
        db.session.add(program)
        db.session.commit()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            user_id=user1.id,
            tenant_id=tenant.id,
            trainer_id=admin.id
        )
        
        beneficiary2 = Beneficiary(
            user_id=user2.id,
            tenant_id=tenant.id,
            trainer_id=admin.id
        )
        
        db.session.add_all([beneficiary1, beneficiary2])
        db.session.commit()
        
        # Create enrollments
        enrollment1 = ProgramEnrollment(
            program_id=program.id,
            beneficiary_id=beneficiary1.id
        )
        
        enrollment2 = ProgramEnrollment(
            program_id=program.id,
            beneficiary_id=beneficiary2.id
        )
        
        db.session.add_all([enrollment1, enrollment2])
        db.session.commit()
        
        return {
            'app': app,
            'tenant': tenant,
            'admin': admin,
            'users': [user1, user2],
            'program': program,
            'beneficiaries': [beneficiary1, beneficiary2],
            'enrollments': [enrollment1, enrollment2]
        }


def test_list_program_students_unauthorized(auth_client):
    """Test that unauthorized access is rejected."""
    client, _ = auth_client
    
    # Attempt to access endpoint without token
    response = client.get('/api/programs/1/students')
    assert response.status_code == 401


def test_list_program_students_nonexistent_program(auth_client):
    """Test response for non-existent program."""
    client, token = auth_client
    
    response = client.get(
        '/api/programs/9999/students',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404


def test_list_program_students_success(auth_client, setup_test_data):
    """Test successful retrieval of program students."""
    client, token = auth_client
    test_data = setup_test_data
    app = test_data['app']
    
    with app.app_context():
        response = client.get(
            f'/api/programs/{test_data["program"].id}/students',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Check if the response contains expected data
        student_ids = [student['id'] for student in data]
        expected_ids = [b.id for b in test_data['beneficiaries']]
        assert sorted(student_ids) == sorted(expected_ids)
        
        # Check for required fields
        for student in data:
            assert 'id' in student
            assert 'full_name' in student
            assert 'email' in student
            
            # Verify that the name format is correct
            for user, beneficiary in zip(test_data['users'], test_data['beneficiaries']):
                if student['id'] == beneficiary.id:
                    expected_name = f"{user.first_name} {user.last_name}"
                    assert student['full_name'] == expected_name
                    assert student['email'] == user.email


def test_list_program_students_different_tenant(auth_client, setup_test_data):
    """Test that access is restricted for users from different tenants."""
    client, _ = auth_client
    test_data = setup_test_data
    app = test_data['app']
    
    with app.app_context():
        # Create a user from a different tenant
        other_tenant = Tenant(
            name="Other Tenant",
            slug="other-tenant",
            email="other@tenant.com"
        )
        db.session.add(other_tenant)
        db.session.commit()
        
        other_user = User(
            email="other@tenant.com",
            password="Password123!",
            first_name="Other",
            last_name="User",
            role="tenant_admin",
            tenant_id=other_tenant.id
        )
        db.session.add(other_user)
        db.session.commit()
        
        # Login with this user
        response = client.post('/api/auth/login', json={
            'email': other_user.email,
            'password': 'Password123!'
        })
        
        other_token = json.loads(response.data)['access_token']
        
        # Try to access program from different tenant
        response = client.get(
            f'/api/programs/{test_data["program"].id}/students',
            headers={'Authorization': f'Bearer {other_token}'}
        )
        
        # Should be forbidden since program is from a different tenant
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unauthorized'