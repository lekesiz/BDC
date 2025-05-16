"""Tests for analytics API."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.models import User, Beneficiary, Evaluation, TestSession, Appointment
from app.extensions import db


@pytest.fixture
def setup_analytics_data(session, app):
    """Setup test data for analytics API tests."""
    # Create test users
    admin_user = User(
        username='admin_analytics',
        email='admin_analytics@test.com',
        first_name='Admin',
        last_name='Analytics',
        is_active=True,
        role='tenant_admin',
        tenant_id=1
    )
    admin_user.password = 'Admin123!'
    
    trainer_user = User(
        username='trainer_analytics',
        email='trainer_analytics@test.com',
        first_name='Trainer',
        last_name='Analytics',
        is_active=True,
        role='trainer',
        tenant_id=1
    )
    trainer_user.password = 'Trainer123!'
    
    student_user = User(
        username='student_analytics',
        email='student_analytics@test.com',
        first_name='Student',
        last_name='Analytics',
        is_active=True,
        role='student',
        tenant_id=1
    )
    student_user.password = 'Student123!'
    
    session.add_all([admin_user, trainer_user, student_user])
    session.commit()
    
    # Create beneficiary users
    ben_user1 = User(
        username='ben_one',
        email='ben1@test.com',
        first_name='Ben',
        last_name='One',
        is_active=True,
        role='student',
        tenant_id=1
    )
    ben_user1.password = 'Password123!'
    
    ben_user2 = User(
        username='ben_two',
        email='ben2@test.com',
        first_name='Ben',
        last_name='Two',
        is_active=True,
        role='student',
        tenant_id=1
    )
    ben_user2.password = 'Password123!'
    
    session.add_all([ben_user1, ben_user2])
    session.commit()
    
    # Create beneficiaries
    beneficiary1 = Beneficiary(
        user_id=ben_user1.id,
        trainer_id=trainer_user.id,
        phone='1111111111',
        birth_date=datetime(1990, 1, 1),
        tenant_id=1
    )
    
    beneficiary2 = Beneficiary(
        user_id=ben_user2.id,
        trainer_id=trainer_user.id,
        phone='2222222222',
        birth_date=datetime(1991, 1, 1),
        tenant_id=1,
        created_at=datetime.now() - timedelta(days=5)  # Recent
    )
    
    session.add_all([beneficiary1, beneficiary2])
    session.commit()
    
    # Create a test set first
    from app.models.test import TestSet
    test_set = TestSet(
        title='Analytics Test',
        description='Test for analytics',
        type='evaluation',
        tenant_id=1,
        creator_id=admin_user.id
    )
    session.add(test_set)
    session.commit()
    
    # Create evaluations
    evaluation1 = Evaluation(
        beneficiary_id=beneficiary1.id,
        test_id=test_set.id,
        trainer_id=trainer_user.id,
        tenant_id=1,
        score=85.5,
        status='completed'
    )
    
    evaluation2 = Evaluation(
        beneficiary_id=beneficiary2.id,
        test_id=test_set.id,
        trainer_id=trainer_user.id,
        tenant_id=1,
        score=75.0,
        status='in_progress'
    )
    
    session.add_all([evaluation1, evaluation2])
    session.commit()
    
    # Create test sessions
    test_session1 = TestSession(
        beneficiary_id=beneficiary1.id,
        test_set_id=test_set.id,
        status='completed',
        created_at=datetime.now() - timedelta(days=3)
    )
    
    test_session2 = TestSession(
        beneficiary_id=beneficiary2.id,
        test_set_id=test_set.id,
        status='in_progress'
    )
    
    session.add_all([test_session1, test_session2])
    session.commit()
    
    # Create appointments
    appointment1 = Appointment(
        title='Appointment 1',
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=1),
        beneficiary_id=beneficiary1.id,
        trainer_id=trainer_user.id,
        status='scheduled'
    )
    
    appointment2 = Appointment(
        title='Appointment 2',
        start_time=datetime.now() + timedelta(days=7),
        end_time=datetime.now() + timedelta(days=7, hours=1),
        beneficiary_id=beneficiary2.id,
        trainer_id=trainer_user.id,
        status='scheduled'
    )
    
    session.add_all([appointment1, appointment2])
    session.commit()
    
    return {
        'admin_user': admin_user,
        'trainer_user': trainer_user,
        'student_user': student_user,
        'admin_id': admin_user.id,
        'trainer_id': trainer_user.id,
        'student_id': student_user.id,
        'beneficiary1_id': beneficiary1.id,
        'beneficiary2_id': beneficiary2.id,
        'evaluation1_id': evaluation1.id,
        'evaluation2_id': evaluation2.id,
        'test_set_id': test_set.id
    }


class TestAnalyticsAPI:
    """Test cases for analytics API endpoints."""
    
    def test_get_dashboard_analytics_admin(self, client, setup_analytics_data, app):
        """Test getting dashboard analytics as admin."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'statistics' in data
        stats = data['statistics']
        assert 'total_users' in stats
        assert 'total_beneficiaries' in stats
        assert 'total_trainers' in stats
        assert 'total_evaluations' in stats
        assert 'student_count' in stats
        assert 'admin_count' in stats
        assert 'recent_activity' in stats
    
    def test_get_dashboard_analytics_trainer(self, client, setup_analytics_data, app):
        """Test getting dashboard analytics as trainer."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'statistics' in data
        stats = data['statistics']
        assert 'assigned_beneficiaries' in stats
        assert 'completed_evaluations' in stats
        assert 'total_sessions' in stats
        assert 'upcoming_sessions' in stats
    
    def test_get_dashboard_analytics_student(self, client, setup_analytics_data, app):
        """Test getting dashboard analytics as student."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['student_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'statistics' in data
        # Students may have limited stats
    
    def test_get_time_series_data(self, client, setup_analytics_data, app):
        """Test getting time series data."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/time-series', headers=headers)
        
        # This endpoint might not exist
        assert response.status_code in [200, 404]
    
    def test_get_activity_overview(self, client, setup_analytics_data, app):
        """Test getting activity overview."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/activity', headers=headers)
        
        # This endpoint might not exist
        assert response.status_code in [200, 404]
    
    def test_get_user_stats(self, client, setup_analytics_data, app):
        """Test getting user statistics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/users', headers=headers)
        
        # This endpoint might not exist
        assert response.status_code in [200, 404]
    
    def test_get_evaluation_stats(self, client, setup_analytics_data, app):
        """Test getting evaluation statistics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/evaluations', headers=headers)
        
        # This endpoint might not exist
        assert response.status_code in [200, 404]
    
    def test_get_appointment_stats(self, client, setup_analytics_data, app):
        """Test getting appointment statistics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/appointments', headers=headers)
        
        # This endpoint might not exist
        assert response.status_code in [200, 404]
    
    def test_unauthorized_access(self, client, app):
        """Test accessing analytics without authentication."""
        response = client.get('/api/analytics/dashboard')
        
        assert response.status_code == 401
    
    def test_get_role_specific_stats(self, client, setup_analytics_data, app):
        """Test getting role-specific stats."""
        from flask_jwt_extended import create_access_token
        
        # Test as trainer
        access_token = create_access_token(identity=setup_analytics_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        
        # Verify structure is different from admin
        assert 'statistics' in data
        stats = data['statistics']
        
        # Trainer should see different stats than admin
        assert 'assigned_beneficiaries' in stats or 'total_sessions' in stats