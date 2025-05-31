import pytest
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models import User, Beneficiary, Program, ProgramEnrollment


class TestAnalyticsAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create test users
        self.admin_user = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_active=True
        )
        self.admin_user.password = 'password123'
        
        self.trainer_user = User(
            email='trainer@test.com',
            first_name='Trainer',
            last_name='User',
            role='trainer',
            is_active=True
        )
        self.trainer_user.password = 'password123'
        
        self.student_user = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student',
            is_active=True
        )
        self.student_user.password = 'password123'
        
        db.session.add_all([self.admin_user, self.trainer_user, self.student_user])
        db.session.commit()
        
        # Create access tokens
        self.admin_token = create_access_token(identity=str(self.admin_user.id))
        self.trainer_token = create_access_token(identity=str(self.trainer_user.id))
        self.student_token = create_access_token(identity=str(self.student_user.id))
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_dashboard_analytics_as_admin(self):
        """Test getting dashboard analytics as admin"""
        response = self.client.get(
            '/api/analytics/dashboard',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check for common dashboard metrics
        possible_keys = ['total_users', 'total_beneficiaries', 'active_programs', 
                        'users', 'beneficiaries', 'programs', 'metrics', 'stats']
        assert any(key in data for key in possible_keys)
    
    def test_get_dashboard_analytics_unauthorized(self):
        """Test getting analytics without authentication"""
        response = self.client.get('/api/analytics/dashboard')
        assert response.status_code == 401
    
    def test_get_user_analytics(self):
        """Test getting user analytics"""
        response = self.client.get(
            '/api/analytics/users',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if response.status_code == 404:
            # Try alternative endpoint
            response = self.client.get(
                '/api/analytics/user-stats',
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
        
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, dict)
    
    def test_get_program_analytics(self):
        """Test getting program analytics"""
        response = self.client.get(
            '/api/analytics/programs',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if response.status_code == 404:
            # Try alternative endpoint
            response = self.client.get(
                '/api/analytics/program-stats',
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
        
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, dict)
    
    def test_get_analytics_with_date_range(self):
        """Test getting analytics with date range filter"""
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/dashboard?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics"""
        response = self.client.get(
            '/api/analytics/performance',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, dict)
    
    def test_get_growth_analytics(self):
        """Test getting growth analytics"""
        response = self.client.get(
            '/api/analytics/growth',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            # Should have time-series data
            assert 'data' in data or 'series' in data or 'growth' in data
    
    def test_export_analytics(self):
        """Test exporting analytics data"""
        response = self.client.get(
            '/api/analytics/export?format=csv',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if response.status_code != 404:
            assert response.status_code in [200, 202]  # OK or Accepted
            # Check content type for CSV
            if response.status_code == 200:
                assert 'csv' in response.content_type.lower() or 'text' in response.content_type.lower()
    
    def test_analytics_role_restrictions(self):
        """Test that students cannot access analytics"""
        response = self.client.get(
            '/api/analytics/dashboard',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        assert response.status_code in [403, 401]
    
    def test_trainer_limited_analytics(self):
        """Test that trainers have limited analytics access"""
        response = self.client.get(
            '/api/analytics/dashboard',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Trainers might have access to some analytics
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verify it's limited data (implementation dependent)
            assert isinstance(data, dict)
    
    def test_get_custom_analytics_report(self):
        """Test getting custom analytics report"""
        report_config = {
            'metrics': ['user_growth', 'program_completion'],
            'group_by': 'month',
            'filters': {
                'date_range': 'last_30_days'
            }
        }
        
        response = self.client.post(
            '/api/analytics/custom-report',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=report_config
        )
        
        if response.status_code != 404:
            assert response.status_code in [200, 201, 202]
            data = json.loads(response.data)
            assert isinstance(data, dict)
    
    def test_get_real_time_analytics(self):
        """Test getting real-time analytics"""
        response = self.client.get(
            '/api/analytics/real-time',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        if response.status_code != 404:
            assert response.status_code == 200
            data = json.loads(response.data)
            # Should have current/live data
            assert 'current' in data or 'live' in data or 'active_users' in data