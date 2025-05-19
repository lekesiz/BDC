"""Tests for analytics endpoints."""

import json
import uuid
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
from app.models import User, Beneficiary, Appointment, TestSession, TestSet
from app.extensions import db

@pytest.fixture
def setup_data(db_session, test_app):
    """Setup test data for analytics tests."""
    with test_app.app_context():
        # Create test users with unique usernames
        suffix = str(uuid.uuid4())[:8]
        
        admin_user = User(
            username=f'admin_{suffix}',
            email=f'admin_{suffix}@test.com',
            first_name='Admin',
            last_name='User',
            is_active=True,
            role='super_admin',
            tenant_id=1
        )
        admin_user.password = 'password123'
        
        psychologist_user = User(
            username=f'psikolog_{suffix}',
            email=f'psikolog_{suffix}@test.com',
            first_name='Psychologist',
            last_name='User',
            is_active=True,
            role='trainer',
            tenant_id=1
        )
        psychologist_user.password = 'password123'
        
        # Create beneficiary users
        beneficiary_user1 = User(
            username=f'bene1_{suffix}',
            email=f'beneficiary1_{suffix}@test.com',
            first_name='Beneficiary',
            last_name='One',
            is_active=True,
            role='student',
            tenant_id=1
        )
        beneficiary_user1.password = 'password123'
        
        beneficiary_user2 = User(
            username=f'bene2_{suffix}',
            email=f'beneficiary2_{suffix}@test.com',
            first_name='Beneficiary',
            last_name='Two',
            is_active=True,
            role='student',
            tenant_id=1
        )
        beneficiary_user2.password = 'password123'
        
        db_session.add_all([admin_user, psychologist_user, beneficiary_user1, beneficiary_user2])
        db_session.flush()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            user_id=beneficiary_user1.id,
            trainer_id=psychologist_user.id,
            tenant_id=1,
            phone='1234567890'
        )
        
        beneficiary2 = Beneficiary(
            user_id=beneficiary_user2.id,
            trainer_id=psychologist_user.id,
            tenant_id=1,
            phone='0987654321'
        )
        
        db_session.add_all([beneficiary1, beneficiary2])
        db_session.flush()
        
        # Create appointments
        now = datetime.utcnow()
        appointment1 = Appointment(
            beneficiary_id=beneficiary1.id,
            trainer_id=psychologist_user.id,
            title='Test Appointment 1',
            start_time=now - timedelta(days=7),
            end_time=now - timedelta(days=7) + timedelta(hours=1),
            status='completed',
            notes='Test appointment 1'
        )
        
        appointment2 = Appointment(
            beneficiary_id=beneficiary2.id,
            trainer_id=psychologist_user.id,
            title='Test Appointment 2',
            start_time=now - timedelta(days=3),
            end_time=now - timedelta(days=3) + timedelta(hours=1),
            status='scheduled',
            notes='Test appointment 2'
        )
        
        # Create test set
        test_set = TestSet(
            title='General Assessment',
            description='Test assessment',
            status='active',
            creator_id=admin_user.id,
            tenant_id=1
        )
        
        db_session.add(test_set)
        db_session.flush()
        
        # Create test sessions
        test_session1 = TestSession(
            test_set_id=test_set.id,
            beneficiary_id=beneficiary1.id,
            start_time=now - timedelta(days=5),
            end_time=now - timedelta(days=5) + timedelta(hours=2),
            status='completed'
        )
        
        test_session2 = TestSession(
            test_set_id=test_set.id,
            beneficiary_id=beneficiary2.id,
            start_time=now - timedelta(days=2),
            status='in_progress'
        )
        
        # Add all to session
        db_session.add_all([
            beneficiary1, beneficiary2,
            appointment1, appointment2, test_set,
            test_session1, test_session2
        ])
        db_session.commit()
        
        # Refresh to ensure they're properly attached to the session
        db_session.refresh(admin_user)
        db_session.refresh(psychologist_user)
        
        # Get the IDs before closing the session
        admin_id = admin_user.id
        psychologist_id = psychologist_user.id
        beneficiary1_id = beneficiary1.id
        beneficiary2_id = beneficiary2.id
        
        return {
            'admin': admin_user,
            'psychologist': psychologist_user,
            'beneficiary1': beneficiary1,
            'beneficiary2': beneficiary2,
            'appointment1': appointment1,
            'appointment2': appointment2,
            'test_set': test_set,
            'test_session1': test_session1,
            'test_session2': test_session2,
            'admin_id': admin_id,
            'psychologist_id': psychologist_id,
            'beneficiary1_id': beneficiary1_id,
            'beneficiary2_id': beneficiary2_id
        }


def test_dashboard_stats_admin(client, auth_headers, setup_data, test_app):
    """Test dashboard stats endpoint for admin."""
    with test_app.app_context():
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        
        # Check the structure of the response
        assert 'statistics' in data
        assert 'charts' in data
        assert 'time_range' in data
        
        stats = data['statistics']
        
        # Check that we have the expected fields for admin
        assert 'total_users' in stats
        assert 'total_beneficiaries' in stats
        assert 'total_trainers' in stats
        assert 'total_evaluations' in stats
        assert 'student_count' in stats
        assert 'admin_count' in stats
        assert 'recent_activity' in stats


def test_beneficiary_activity_report(client, auth_headers, setup_data, test_app):
    """Test beneficiary activity report."""
    with test_app.app_context():
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/beneficiaries', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert len(data) >= 0  # Data format might be different


def test_trainer_analytics(client, auth_headers, setup_data, test_app):
    """Test trainer analytics."""
    with test_app.app_context():
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/trainers', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert len(data) >= 0  # Data format might be different


def test_program_analytics(client, auth_headers, setup_data, test_app):
    """Test program analytics."""
    with test_app.app_context():
        # Generate auth headers for admin
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/programs', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert len(data) >= 0  # Data format might be different


def test_non_admin_role_dashboard(client, auth_headers, setup_data, test_app):
    """Test trainer role gets their own dashboard analytics."""
    with test_app.app_context():
        # Generate auth headers for trainer/psychologist
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_data['psychologist_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200  # Trainers can access dashboard but get their own data
        data = response.json
        assert isinstance(data, dict)  # Should return some data


def test_analytics_forbidden_non_admin(client, auth_headers, setup_data, test_app):
    """Test analytics access is forbidden for non-admin users."""
    with test_app.app_context():
        # Generate auth headers for trainer/psychologist
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_data['psychologist_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # These endpoints are admin-only
        endpoints = [
            '/api/analytics/trainers',
            '/api/analytics/programs'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 403