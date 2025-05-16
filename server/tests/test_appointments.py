"""Tests for appointments endpoints."""

import json
from datetime import datetime, timedelta
import pytest
from app.models import User, Beneficiary, Appointment
from app.extensions import db

@pytest.fixture
def setup_appointment_data(session, app):
    """Setup test data for appointment tests."""
    with app.app_context():
        # Create test users
        psychologist = User(
            username='psychologist',
            email='psychologist@test.com',
            first_name='Test',
            last_name='Psychologist',
            is_active=True,
            role='psychologist',
            tenant_id=1
        )
        psychologist.password = 'password123'
        
        admin = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            is_active=True,
            role='admin',
            tenant_id=1
        )
        admin.password = 'password123'
        
        # Create beneficiary users
        beneficiary_user1 = User(
            username='bene1',
            email='beneficiary1@test.com',
            first_name='Test',
            last_name='Beneficiary 1',
            is_active=True,
            role='student',
            tenant_id=1
        )
        beneficiary_user1.password = 'password123'
        
        beneficiary_user2 = User(
            username='bene2',
            email='beneficiary2@test.com',
            first_name='Test',
            last_name='Beneficiary 2',
            is_active=True,
            role='student',
            tenant_id=1
        )
        beneficiary_user2.password = 'password123'
        
        session.add_all([psychologist, admin, beneficiary_user1, beneficiary_user2])
        session.flush()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            user_id=beneficiary_user1.id,
            trainer_id=psychologist.id,
            tenant_id=1,
            phone='1234567890'
        )
        
        beneficiary2 = Beneficiary(
            user_id=beneficiary_user2.id,
            trainer_id=psychologist.id,
            tenant_id=1,
            phone='0987654321'
        )
        
        # Create appointments
        now = datetime.utcnow()
        appointment1 = Appointment(
            beneficiary_id=beneficiary1.id,
            trainer_id=psychologist.id,
            title='Test Appointment 1',
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1),
            status='scheduled',
            notes='Test appointment 1'
        )
        
        appointment2 = Appointment(
            beneficiary_id=beneficiary2.id,
            trainer_id=psychologist.id,
            title='Test Appointment 2',
            start_time=now + timedelta(days=2),
            end_time=now + timedelta(days=2, hours=1),
            status='scheduled',
            notes='Test appointment 2'
        )
        
        session.add_all([beneficiary1, beneficiary2, appointment1, appointment2])
        session.commit()
        
        return {
            'psychologist': psychologist,
            'admin': admin,
            'beneficiary_user1': beneficiary_user1,
            'beneficiary_user2': beneficiary_user2,
            'beneficiary1': beneficiary1,
            'beneficiary2': beneficiary2,
            'appointment1': appointment1,
            'appointment2': appointment2
        }


def test_list_appointments(client, setup_appointment_data, app):
    """Test listing appointments."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/appointments', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'appointments' in data
        assert len(data['appointments']) >= 2


def test_get_appointment(client, setup_appointment_data, app):
    """Test getting a single appointment."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        appointment_id = setup_appointment_data['appointment1'].id
        response = client.get(f'/api/appointments/{appointment_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == appointment_id
        assert data['notes'] == 'Test appointment 1'


def test_create_appointment(client, setup_appointment_data, app):
    """Test creating a new appointment."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['psychologist'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        now = datetime.utcnow()
        appointment_data = {
            'beneficiary_id': setup_appointment_data['beneficiary1'].id,
            'title': 'New Test Appointment',
            'start_time': (now + timedelta(days=3)).isoformat(),
            'end_time': (now + timedelta(days=3, hours=1)).isoformat(),
            'notes': 'New test appointment'
        }
        
        response = client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['notes'] == 'New test appointment'
        assert data['status'] == 'scheduled'


def test_update_appointment(client, setup_appointment_data, app):
    """Test updating an appointment."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['psychologist'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        appointment_id = setup_appointment_data['appointment1'].id
        update_data = {
            'notes': 'Updated appointment notes',
            'status': 'confirmed'
        }
        
        response = client.put(
            f'/api/appointments/{appointment_id}',
            data=json.dumps(update_data),
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['notes'] == 'Updated appointment notes'
        assert data['status'] == 'confirmed'


def test_cancel_appointment(client, setup_appointment_data, app):
    """Test canceling an appointment."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        appointment_id = setup_appointment_data['appointment1'].id
        response = client.post(
            f'/api/appointments/{appointment_id}/cancel',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'cancelled'


def test_delete_appointment(client, setup_appointment_data, app):
    """Test deleting an appointment."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['admin'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        appointment_id = setup_appointment_data['appointment1'].id
        response = client.delete(
            f'/api/appointments/{appointment_id}',
            headers=headers
        )
        
        assert response.status_code == 204


def test_appointment_conflict(client, setup_appointment_data, app):
    """Test appointment conflict detection."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_appointment_data['psychologist'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Try to create an appointment that conflicts with an existing one
        existing = setup_appointment_data['appointment1']
        conflict_data = {
            'beneficiary_id': setup_appointment_data['beneficiary2'].id,
            'title': 'Conflicting Appointment',
            'start_time': existing.start_time.isoformat(),
            'end_time': existing.end_time.isoformat(),
            'notes': 'Conflicting appointment'
        }
        
        response = client.post(
            '/api/appointments',
            data=json.dumps(conflict_data),
            headers=headers
        )
        
        assert response.status_code == 400
        assert 'conflict' in response.json.get('error', '').lower()


def test_appointment_wrong_user(client, setup_appointment_data, app):
    """Test appointment access by wrong user."""
    with app.app_context():
        # Create another psychologist
        other_psych = User(
            username='other_psych',
            email='other@test.com',
            first_name='Other',
            last_name='Psychologist',
            is_active=True,
            role='psychologist',
            tenant_id=2  # Different tenant
        )
        other_psych.password = 'password123'
        session = db.session
        session.add(other_psych)
        session.commit()
        
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=other_psych.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        appointment_id = setup_appointment_data['appointment1'].id
        response = client.get(f'/api/appointments/{appointment_id}', headers=headers)
        
        assert response.status_code == 404  # Should not be able to see other tenant's appointments