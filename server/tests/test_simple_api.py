"""Simple API tests to verify endpoints are working."""

import pytest
import json
from datetime import datetime, timedelta


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_api_test_endpoint(client):
    """Test API test endpoint."""
    response = client.get('/api/test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data


def test_users_endpoint_requires_auth(client):
    """Test that users endpoint requires authentication."""
    response = client.get('/api/users')
    # Should return 401 or 422 without auth
    assert response.status_code in [401, 422]


def test_beneficiaries_endpoint_requires_auth(client):
    """Test that beneficiaries endpoint requires authentication."""
    response = client.get('/api/beneficiaries')
    # Should return 401 or 422 without auth
    assert response.status_code in [401, 422]


def test_appointments_endpoint_requires_auth(client):
    """Test that appointments endpoint requires authentication."""
    response = client.get('/api/appointments')
    # Should return 401 or 422 without auth
    assert response.status_code in [401, 422]


def test_evaluations_endpoint_requires_auth(client):
    """Test that evaluations endpoint requires authentication."""
    response = client.get('/api/evaluations')
    # Should return 401 or 422 without auth
    assert response.status_code in [401, 422]


def test_login_endpoint_exists(client):
    """Test that login endpoint exists."""
    response = client.post('/api/auth/login', 
                          json={'email': 'test@test.com', 'password': 'test'})
    # Should return 401 for invalid credentials, not 404
    assert response.status_code != 404


def test_register_endpoint_exists(client):
    """Test that register endpoint exists."""
    response = client.post('/api/auth/register',
                          json={'email': 'test@test.com', 'password': 'test'})
    # Should return some error, not 404
    assert response.status_code != 404


class TestAPIWithMockAuth:
    """Test API endpoints with mocked authentication."""
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers."""
        return {
            'Authorization': 'Bearer fake-token',
            'Content-Type': 'application/json'
        }
    
    def test_create_appointment_endpoint_structure(self, client, auth_headers):
        """Test appointment creation endpoint structure."""
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'end_time': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'beneficiary_id': 1
        }
        
        response = client.post('/api/appointments',
                              json=appointment_data,
                              headers=auth_headers)
        
        # Even with fake token, endpoint should exist
        assert response.status_code != 404
    
    def test_create_evaluation_endpoint_structure(self, client, auth_headers):
        """Test evaluation creation endpoint structure."""
        evaluation_data = {
            'title': 'Test Evaluation',
            'type': 'quiz',
            'tenant_id': 1
        }
        
        response = client.post('/api/evaluations',
                              json=evaluation_data,
                              headers=auth_headers)
        
        # Even with fake token, endpoint should exist
        assert response.status_code != 404
    
    def test_api_error_format(self, client):
        """Test that API errors follow consistent format."""
        response = client.get('/api/users')
        
        if response.status_code != 200:
            data = json.loads(response.data)
            # Should have either 'error' or 'msg' or 'message' field
            assert any(key in data for key in ['error', 'msg', 'message'])


class TestAPIEndpointAvailability:
    """Test that all documented API endpoints are available."""
    
    endpoints = [
        ('GET', '/health'),
        ('GET', '/api/test'),
        ('POST', '/api/auth/login'),
        ('POST', '/api/auth/register'),
        ('POST', '/api/auth/logout'),
        ('GET', '/api/users'),
        ('GET', '/api/beneficiaries'),
        ('GET', '/api/appointments'),
        ('GET', '/api/evaluations'),
        ('GET', '/api/programs'),
        ('GET', '/api/calendar'),
        ('GET', '/api/notifications'),
        ('GET', '/api/documents'),
        ('GET', '/api/reports'),
        ('GET', '/api/analytics'),
    ]
    
    @pytest.mark.parametrize("method,endpoint", endpoints)
    def test_endpoint_exists(self, client, method, endpoint):
        """Test that endpoint exists (not 404)."""
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, json={})
        else:
            response = client.get(endpoint)
        
        # Endpoint should exist (not return 404)
        # It may return 401/422 for auth or 400 for bad request
        assert response.status_code != 404, f"{method} {endpoint} returned 404"


class TestRefactoredServices:
    """Test that refactored services are being used."""
    
    def test_appointment_service_loaded(self):
        """Test that appointment service can be imported."""
        try:
            from app.services.appointment_service_refactored import AppointmentServiceRefactored
            assert AppointmentServiceRefactored is not None
        except ImportError:
            pytest.fail("Could not import AppointmentServiceRefactored")
    
    def test_evaluation_service_loaded(self):
        """Test that evaluation service can be imported."""
        try:
            from app.services.evaluation_service_refactored import EvaluationServiceRefactored
            assert EvaluationServiceRefactored is not None
        except ImportError:
            pytest.fail("Could not import EvaluationServiceRefactored")
    
    def test_appointment_factory_uses_refactored(self):
        """Test that appointment factory uses refactored service."""
        from app.services.appointment_service_factory import AppointmentServiceFactory
        from app.services.appointment_service_refactored import AppointmentServiceRefactored
        
        service = AppointmentServiceFactory.create()
        assert isinstance(service, AppointmentServiceRefactored)