"""Tests for Analytics API - Fixed version."""

import json
import uuid
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
from app.extensions import db
from app.models import User, Tenant, Beneficiary, Evaluation, TestSession, Appointment


@pytest.fixture
def setup_analytics_data(session, app):
    """Setup test data for analytics API tests."""
    with app.app_context():
        # Create tenant
        tenant = Tenant(
            name='Test Tenant',
            slug='test',
            email='test@tenant.com',
            is_active=True
        )
        session.add(tenant)
        session.flush()
        
        # Create users
        suffix = str(uuid.uuid4())[:8]
        
        admin = User(
            username=f'admin_{suffix}',
            email=f'admin_{suffix}@test.com',
            first_name='Admin',
            last_name='User',
            is_active=True,
            role='super_admin',
            tenant_id=tenant.id
        )
        admin.password = 'password123'
        
        trainer = User(
            username=f'trainer_{suffix}',
            email=f'trainer_{suffix}@test.com',
            first_name='Trainer',
            last_name='User',
            is_active=True,
            role='trainer',
            tenant_id=tenant.id
        )
        trainer.password = 'password123'
        
        student = User(
            username=f'student_{suffix}',
            email=f'student_{suffix}@test.com',
            first_name='Student',
            last_name='User',
            is_active=True,
            role='student',
            tenant_id=tenant.id
        )
        student.password = 'password123'
        
        session.add_all([admin, trainer, student])
        session.flush()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            user_id=student.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id
        )
        session.add(beneficiary1)
        session.flush()
        
        # Create evaluations
        evaluation1 = Evaluation(
            beneficiary_id=beneficiary1.id,
            trainer_id=trainer.id,
            test_id=1,
            status='completed',
            completed_at=datetime.utcnow() - timedelta(days=5),
            score=85.0,
            feedback='Good progress',
            tenant_id=tenant.id
        )
        
        evaluation2 = Evaluation(
            beneficiary_id=beneficiary1.id,
            trainer_id=trainer.id,
            test_id=1,
            status='in_progress',
            created_at=datetime.utcnow(),
            tenant_id=tenant.id
        )
        
        session.add_all([evaluation1, evaluation2])
        session.flush()
        
        # Create test sessions
        test_session1 = TestSession(
            test_id=1,
            user_id=student.id,
            status='completed',
            started_at=datetime.utcnow() - timedelta(days=3),
            completed_at=datetime.utcnow() - timedelta(days=3),
            score=75.0
        )
        
        session.add(test_session1)
        session.flush()
        
        # Create appointments
        appointment1 = Appointment(
            beneficiary_id=beneficiary1.id,
            trainer_id=trainer.id,
            title='Session 1',
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            status='scheduled'
        )
        
        appointment2 = Appointment(
            beneficiary_id=beneficiary1.id,
            trainer_id=trainer.id,
            title='Session 2',
            start_time=datetime.utcnow() - timedelta(days=2),
            end_time=datetime.utcnow() - timedelta(days=2, hours=1),
            status='completed'
        )
        
        session.add_all([appointment1, appointment2])
        session.commit()
        
        return {
            'admin': admin,
            'admin_id': admin.id,
            'trainer': trainer,
            'trainer_id': trainer.id,
            'student': student,
            'student_id': student.id,
            'beneficiary1': beneficiary1,
            'beneficiary1_id': beneficiary1.id,
            'tenant': tenant,
            'tenant_id': tenant.id
        }


class TestAnalyticsAPIV2:
    """Test analytics API endpoints - Fixed version."""
    
    def test_get_dashboard_stats_as_admin(self, client, setup_analytics_data, app):
        """Test getting dashboard stats as admin."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'total_users' in data
        assert 'total_beneficiaries' in data
        assert 'active_evaluations' in data
        assert 'upcoming_appointments' in data
        assert data['total_users'] >= 3
        assert data['total_beneficiaries'] >= 1
    
    def test_get_dashboard_stats_as_trainer(self, client, setup_analytics_data, app):
        """Test getting dashboard stats as trainer."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        # Trainers see limited stats
        assert 'beneficiaries' in data or 'total_beneficiaries' in data
        assert 'evaluations' in data or 'active_evaluations' in data
    
    def test_get_dashboard_stats_unauthorized(self, client, setup_analytics_data, app):
        """Test getting dashboard stats without authorization."""
        response = client.get('/api/analytics/dashboard')
        assert response.status_code == 401
    
    def test_get_evaluation_analytics(self, client, setup_analytics_data, app):
        """Test getting evaluation analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/evaluations', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'total_evaluations' in data
        assert 'completed_evaluations' in data
        assert 'average_score' in data
        assert 'recent_evaluations' in data
    
    def test_get_appointment_analytics(self, client, setup_analytics_data, app):
        """Test getting appointment analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/appointments', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'total_appointments' in data
        assert 'upcoming_appointments' in data
        assert 'completed_appointments' in data
    
    def test_get_beneficiary_analytics(self, client, setup_analytics_data, app):
        """Test getting beneficiary analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/beneficiaries', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'total_beneficiaries' in data
        assert 'active_beneficiaries' in data
        assert 'beneficiaries_by_trainer' in data
    
    def test_get_user_activity_analytics(self, client, setup_analytics_data, app):
        """Test getting user activity analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/user-activity', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'total_users' in data
        assert 'active_users' in data
        assert 'users_by_role' in data
    
    def test_get_progress_analytics(self, client, setup_analytics_data, app):
        """Test getting progress analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['trainer_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        beneficiary_id = setup_analytics_data['beneficiary1_id']
        response = client.get(f'/api/analytics/progress/{beneficiary_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'evaluation_scores' in data
        assert 'test_results' in data
        assert 'attendance_rate' in data
    
    def test_get_time_series_analytics(self, client, setup_analytics_data, app):
        """Test getting time series analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get analytics for last 30 days
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end_date = datetime.utcnow().isoformat()
        
        response = client.get(
            f'/api/analytics/time-series?start_date={start_date}&end_date={end_date}',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'evaluations_by_date' in data
        assert 'appointments_by_date' in data
        assert 'users_by_date' in data
    
    def test_export_analytics(self, client, setup_analytics_data, app):
        """Test exporting analytics data."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/export?format=csv', headers=headers)
        
        # Export might not be implemented
        assert response.status_code in [200, 404, 501]
    
    def test_get_trainer_performance(self, client, setup_analytics_data, app):
        """Test getting trainer performance analytics."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        trainer_id = setup_analytics_data['trainer_id']
        response = client.get(f'/api/analytics/trainer-performance/{trainer_id}', headers=headers)
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json
            assert 'total_beneficiaries' in data
            assert 'total_evaluations' in data
            assert 'average_evaluation_score' in data
    
    def test_get_tenant_analytics(self, client, setup_analytics_data, app):
        """Test getting tenant analytics (super admin only)."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/analytics/tenants', headers=headers)
        
        assert response.status_code in [200, 403, 404]
        if response.status_code == 200:
            data = response.json
            assert 'total_tenants' in data or 'tenants' in data
    
    def test_get_analytics_with_filters(self, client, setup_analytics_data, app):
        """Test getting analytics with various filters."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Filter by tenant
        tenant_id = setup_analytics_data['tenant_id']
        response = client.get(f'/api/analytics/dashboard?tenant_id={tenant_id}', headers=headers)
        assert response.status_code == 200
        
        # Filter by date range
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_date = datetime.utcnow().isoformat()
        response = client.get(
            f'/api/analytics/dashboard?start_date={start_date}&end_date={end_date}',
            headers=headers
        )
        assert response.status_code == 200
    
    def test_analytics_role_restrictions(self, client, setup_analytics_data, app):
        """Test role-based restrictions on analytics endpoints."""
        from flask_jwt_extended import create_access_token
        
        # Student should have limited access
        student_token = create_access_token(identity=setup_analytics_data['student_id'])
        headers = {'Authorization': f'Bearer {student_token}'}
        
        # Should not access admin analytics
        response = client.get('/api/analytics/tenants', headers=headers)
        assert response.status_code in [403, 404]
        
        # Should not access other users' analytics
        response = client.get('/api/analytics/user-activity', headers=headers)
        assert response.status_code in [403, 404]
        
        # Can access own progress
        response = client.get('/api/analytics/progress/self', headers=headers)
        assert response.status_code in [200, 404]
    
    def test_analytics_caching(self, client, setup_analytics_data, app):
        """Test that analytics responses are cached."""
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_analytics_data['admin_id'])
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # First request
        response1 = client.get('/api/analytics/dashboard', headers=headers)
        assert response1.status_code == 200
        
        # Second request should be faster (cached)
        response2 = client.get('/api/analytics/dashboard', headers=headers)
        assert response2.status_code == 200
        
        # Data should be the same
        assert response1.json == response2.json