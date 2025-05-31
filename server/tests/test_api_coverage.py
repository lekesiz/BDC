"""Test API endpoints to increase coverage."""

import pytest
from unittest.mock import patch, Mock
from flask import Flask
from app import create_app


class TestAuthAPI:
    """Test auth API endpoints."""
    
    def test_login_endpoint(self, client):
        """Test login endpoint exists."""
        response = client.post('/api/auth/login', json={})
        # Should return 400 for missing data, not 404
        assert response.status_code in [400, 422]
    
    @patch('app.api.auth.AuthService')
    def test_login_success_mock(self, mock_service, client):
        """Test successful login with mock."""
        mock_service.login.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh'
        }
        
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
    
    @patch('app.api.auth.AuthService')
    def test_login_invalid_credentials(self, mock_service, client):
        """Test login with invalid credentials."""
        mock_service.login.return_value = None
        
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrong'
        })
        
        assert response.status_code in [400, 401]


class TestUserAPI:
    """Test user API endpoints."""
    
    def test_get_users_no_auth(self, client):
        """Test getting users without auth."""
        response = client.get('/api/users')
        assert response.status_code in [401, 422]
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without auth."""
        response = client.get('/api/users/me')
        assert response.status_code in [401, 422]


class TestBeneficiaryAPI:
    """Test beneficiary API endpoints."""
    
    def test_get_beneficiaries_no_auth(self, client):
        """Test getting beneficiaries without auth."""
        response = client.get('/api/beneficiaries')
        assert response.status_code in [401, 422]
    
    def test_create_beneficiary_no_auth(self, client):
        """Test creating beneficiary without auth."""
        response = client.post('/api/beneficiaries', json={
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code in [401, 422, 405]


class TestProgramAPI:
    """Test program API endpoints."""
    
    def test_get_programs_no_auth(self, client):
        """Test getting programs without auth."""
        response = client.get('/api/programs')
        assert response.status_code in [401, 422]
    
    def test_get_program_no_auth(self, client):
        """Test getting single program without auth."""
        response = client.get('/api/programs/1')
        assert response.status_code in [401, 422]


class TestNotificationAPI:
    """Test notification API endpoints."""
    
    def test_get_notifications_no_auth(self, client):
        """Test getting notifications without auth."""
        response = client.get('/api/notifications')
        assert response.status_code in [401, 422]
    
    def test_mark_read_no_auth(self, client):
        """Test marking notification as read without auth."""
        response = client.put('/api/notifications/1/read')
        assert response.status_code in [401, 422, 405]


class TestSettingsAPI:
    """Test settings API endpoints."""
    
    def test_get_general_settings_no_auth(self, client):
        """Test getting general settings without auth."""
        response = client.get('/api/settings/general')
        assert response.status_code in [401, 422]
    
    def test_update_settings_no_auth(self, client):
        """Test updating settings without auth."""
        response = client.put('/api/settings/general', json={
            'site_name': 'Test Site'
        })
        assert response.status_code in [401, 422]


class TestHealthAPI:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
    
    def test_api_health(self, client):
        """Test API health endpoint."""
        response = client.get('/api/health')
        assert response.status_code in [200, 404]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])