import pytest
import json
from datetime import datetime

from app import create_app, db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.program import Program, ProgramModule, ProgramEnrollment


@pytest.fixture()
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    
    with app.app_context():
        db.create_all()
        
        # Create test tenant
        tenant = Tenant(name="Test Tenant")
        db.session.add(tenant)
        
        # Create admin user for testing
        admin = User(
            email="admin@test.com",
            password="password",
            first_name="Admin",
            last_name="User",
            role="tenant_admin",
            tenant_id=1
        )
        db.session.add(admin)
        
        # Create trainer user for testing
        trainer = User(
            email="trainer@test.com",
            password="password",
            first_name="Trainer",
            last_name="User",
            role="trainer",
            tenant_id=1
        )
        db.session.add(trainer)
        
        # Create test beneficiary
        beneficiary = Beneficiary(
            first_name="Test",
            last_name="Beneficiary",
            email="beneficiary@test.com",
            tenant_id=1
        )
        db.session.add(beneficiary)
        
        # Create test program
        program = Program(
            name="Test Program",
            description="Test Description",
            tenant_id=1,
            created_by_id=1,
            is_active=True
        )
        db.session.add(program)
        
        # Create program modules
        module1 = ProgramModule(
            program_id=1,
            name="Module 1",
            description="First module",
            order=1
        )
        module2 = ProgramModule(
            program_id=1,
            name="Module 2",
            description="Second module",
            order=2
        )
        db.session.add_all([module1, module2])
        
        # Create enrollment
        enrollment = ProgramEnrollment(
            program_id=1,
            beneficiary_id=1,
            status="enrolled",
            progress=10.0,
            attendance_rate=80.0,
            overall_score=75.0
        )
        db.session.add(enrollment)
        
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_headers(client):
    response = client.post(
        '/api/auth/login',
        json={'email': 'admin@test.com', 'password': 'password'}
    )
    token = json.loads(response.data)['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def trainer_headers(client):
    response = client.post(
        '/api/auth/login',
        json={'email': 'trainer@test.com', 'password': 'password'}
    )
    token = json.loads(response.data)['token']
    return {'Authorization': f'Bearer {token}'}


def test_get_program_progress(client, admin_headers):
    """Test getting overall program progress."""
    response = client.get('/api/programs/1/progress', headers=admin_headers)
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['total_enrollments'] == 1
    assert data['in_progress'] == 1
    assert data['completed'] == 0
    assert 'average_progress' in data
    assert 'modules' in data
    assert len(data['modules']) == 2


def test_get_enrollment_progress(client, admin_headers):
    """Test getting detailed progress for a specific enrollment."""
    response = client.get('/api/programs/1/enrollments/1/progress', headers=admin_headers)
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'enrollment' in data
    assert 'module_progress' in data
    assert len(data['module_progress']) == 2
    assert data['overall_progress'] == 10.0
    assert data['attendance_rate'] == 80.0
    assert data['overall_score'] == 75.0
    assert data['status'] == 'enrolled'


def test_update_enrollment_progress(client, trainer_headers, app):
    """Test updating progress for a specific enrollment."""
    response = client.put(
        '/api/programs/1/enrollments/1/progress',
        json={
            'progress': 25.0,
            'attendance_rate': 85.0,
            'overall_score': 80.0,
            'status': 'active'
        },
        headers=trainer_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['progress'] == 25.0
    assert data['attendance_rate'] == 85.0
    assert data['overall_score'] == 80.0
    assert data['status'] == 'active'
    
    # Verify in database
    with app.app_context():
        enrollment = ProgramEnrollment.query.get(1)
        assert enrollment.progress == 25.0
        assert enrollment.attendance_rate == 85.0
        assert enrollment.overall_score == 80.0
        assert enrollment.status == 'active'


def test_mark_enrollment_completed(client, trainer_headers, app):
    """Test marking an enrollment as completed."""
    response = client.put(
        '/api/programs/1/enrollments/1/progress',
        json={
            'progress': 100.0,
            'status': 'completed'
        },
        headers=trainer_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['progress'] == 100.0
    assert data['status'] == 'completed'
    
    # Verify in database and check completion_date was set
    with app.app_context():
        enrollment = ProgramEnrollment.query.get(1)
        assert enrollment.progress == 100.0
        assert enrollment.status == 'completed'
        assert enrollment.completion_date is not None


def test_update_module_progress(client, trainer_headers, app):
    """Test updating progress for a specific module within an enrollment."""
    response = client.put(
        '/api/programs/1/enrollments/1/module-progress',
        json={
            'module_id': 1,
            'completed': True,
            'progress': 100.0,
            'score': 90.0
        },
        headers=trainer_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'enrollment' in data
    assert 'module_progress' in data
    assert data['module_progress']['module_id'] == 1
    assert data['module_progress']['completed'] == True
    assert data['module_progress']['score'] == 90.0
    
    # Verify enrollment progress was updated in database
    with app.app_context():
        enrollment = ProgramEnrollment.query.get(1)
        assert enrollment.progress > 10.0  # Should have increased from initial 10%
        # Calculate expected score (initial score was 75, new module score is 90)
        expected_score = (75.0 + 90.0) / 2  # Simple average for 2 modules
        assert abs(enrollment.overall_score - expected_score) < 0.01