"""Focused API tests to increase coverage."""

import pytest
from flask import json


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_api_health(self, client):
        """Test API health endpoint."""
        response = client.get('/api/health')
        assert response.status_code in [200, 404]  # Might not exist


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_login_no_data(self, client):
        """Test login with no data."""
        response = client.post('/api/auth/login', 
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login',
                               json={'email': 'wrong@test.com', 'password': 'wrong'})
        assert response.status_code in [401, 400]
    
    def test_register_no_data(self, client):
        """Test register with no data."""
        response = client.post('/api/auth/register',
                              json={},
                              content_type='application/json')
        assert response.status_code in [400, 404]
    
    def test_logout_no_auth(self, client):
        """Test logout without authentication."""
        response = client.post('/api/auth/logout')
        assert response.status_code in [401, 422]


class TestUserEndpoints:
    """Test user endpoints without authentication."""
    
    def test_get_users_no_auth(self, client):
        """Test getting users without authentication."""
        response = client.get('/api/users')
        assert response.status_code in [401, 422]
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get('/api/users/me')
        assert response.status_code in [401, 422]
    
    def test_update_user_no_auth(self, client):
        """Test updating user without authentication."""
        response = client.put('/api/users/me', json={'name': 'Test'})
        assert response.status_code in [401, 422, 405]


class TestBeneficiaryEndpoints:
    """Test beneficiary endpoints without authentication."""
    
    def test_get_beneficiaries_no_auth(self, client):
        """Test getting beneficiaries without authentication."""
        response = client.get('/api/beneficiaries')
        assert response.status_code in [401, 422]
    
    def test_create_beneficiary_no_auth(self, client):
        """Test creating beneficiary without authentication."""
        response = client.post('/api/beneficiaries', json={'name': 'Test'})
        assert response.status_code in [401, 422, 405]
    
    def test_get_beneficiary_no_auth(self, client):
        """Test getting specific beneficiary without authentication."""
        response = client.get('/api/beneficiaries/1')
        assert response.status_code in [401, 422]


class TestProgramEndpoints:
    """Test program endpoints without authentication."""
    
    def test_get_programs_no_auth(self, client):
        """Test getting programs without authentication."""
        response = client.get('/api/programs')
        assert response.status_code in [401, 422]
    
    def test_create_program_no_auth(self, client):
        """Test creating program without authentication."""
        response = client.post('/api/programs', json={'name': 'Test'})
        assert response.status_code in [401, 422]


class TestEvaluationEndpoints:
    """Test evaluation endpoints without authentication."""
    
    def test_get_evaluations_no_auth(self, client):
        """Test getting evaluations without authentication."""
        response = client.get('/api/evaluations')
        assert response.status_code in [401, 422]
    
    def test_create_evaluation_no_auth(self, client):
        """Test creating evaluation without authentication."""
        response = client.post('/api/evaluations', json={'test': 'data'})
        assert response.status_code in [401, 422]


class TestDocumentEndpoints:
    """Test document endpoints without authentication."""
    
    def test_get_documents_no_auth(self, client):
        """Test getting documents without authentication."""
        response = client.get('/api/documents')
        assert response.status_code in [401, 422]
    
    def test_upload_document_no_auth(self, client):
        """Test uploading document without authentication."""
        response = client.post('/api/documents/upload')
        assert response.status_code in [401, 422]


class TestNotificationEndpoints:
    """Test notification endpoints without authentication."""
    
    def test_get_notifications_no_auth(self, client):
        """Test getting notifications without authentication."""
        response = client.get('/api/notifications')
        assert response.status_code in [401, 422]
    
    def test_mark_notification_read_no_auth(self, client):
        """Test marking notification as read without authentication."""
        response = client.put('/api/notifications/1/read')
        assert response.status_code in [401, 422, 405]


class TestCalendarEndpoints:
    """Test calendar endpoints without authentication."""
    
    def test_get_calendar_events_no_auth(self, client):
        """Test getting calendar events without authentication."""
        response = client.get('/api/calendar/events')
        assert response.status_code in [401, 422]
    
    def test_create_appointment_no_auth(self, client):
        """Test creating appointment without authentication."""
        response = client.post('/api/appointments', json={'date': '2024-01-01'})
        assert response.status_code in [401, 422]


class TestReportEndpoints:
    """Test report endpoints without authentication."""
    
    def test_get_reports_no_auth(self, client):
        """Test getting reports without authentication."""
        response = client.get('/api/reports')
        assert response.status_code in [401, 422, 405]
    
    def test_generate_report_no_auth(self, client):
        """Test generating report without authentication."""
        response = client.post('/api/reports/generate', json={'type': 'test'})
        assert response.status_code in [401, 422]


class TestSettingsEndpoints:
    """Test settings endpoints without authentication."""
    
    def test_get_general_settings_no_auth(self, client):
        """Test getting general settings without authentication."""
        response = client.get('/api/settings/general')
        assert response.status_code in [401, 422]
    
    def test_update_settings_no_auth(self, client):
        """Test updating settings without authentication."""
        response = client.put('/api/settings/general', json={'site_name': 'Test'})
        assert response.status_code in [401, 422]
    
    def test_get_appearance_settings_no_auth(self, client):
        """Test getting appearance settings without authentication."""
        response = client.get('/api/settings/appearance')
        assert response.status_code in [401, 422]


class TestAvailabilityEndpoints:
    """Test availability endpoints without authentication."""
    
    def test_get_availability_no_auth(self, client):
        """Test getting availability without authentication."""
        response = client.get('/api/calendars/availability')
        assert response.status_code in [401, 422]
    
    def test_create_availability_no_auth(self, client):
        """Test creating availability without authentication."""
        response = client.post('/api/calendars/availability', json={'slots': []})
        assert response.status_code in [401, 422]


class TestAssessmentEndpoints:
    """Test assessment endpoints without authentication."""
    
    def test_get_templates_no_auth(self, client):
        """Test getting assessment templates without authentication."""
        response = client.get('/api/assessment/templates')
        assert response.status_code in [401, 422]
    
    def test_create_template_no_auth(self, client):
        """Test creating assessment template without authentication."""
        response = client.post('/api/assessment/templates', json={'title': 'Test'})
        assert response.status_code in [401, 422]


class TestProfileEndpoints:
    """Test profile endpoints without authentication."""
    
    def test_get_profile_no_auth(self, client):
        """Test getting user profile without authentication."""
        response = client.get('/api/users/me/profile')
        assert response.status_code in [401, 422]
    
    def test_update_profile_no_auth(self, client):
        """Test updating user profile without authentication."""
        response = client.put('/api/users/me/profile', json={'bio': 'Test'})
        assert response.status_code in [401, 422]
    
    def test_upload_avatar_no_auth(self, client):
        """Test uploading avatar without authentication."""
        response = client.post('/api/users/me/profile/avatar')
        assert response.status_code in [401, 422]