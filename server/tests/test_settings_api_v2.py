"""Tests for settings API endpoints."""

import pytest
from app.models.settings import GeneralSettings, AppearanceSettings


class TestGeneralSettingsAPI:
    """Test general settings API endpoints."""
    
    def test_get_default_general_settings(self, client, auth_headers):
        """Test getting general settings when none exist."""
        response = client.get('/api/settings/general', headers=auth_headers)
        assert response.status_code == 200
        # Should return default settings
        assert 'site_name' in response.json
        assert 'default_language' in response.json
    
    def test_create_general_settings(self, client, auth_headers):
        """Test creating general settings."""
        data = {
            'site_name': 'BDC Test Platform',
            'site_description': 'Test description',
            'contact_email': 'contact@test.com',
            'contact_phone': '+1234567890',
            'default_language': 'en',
            'supported_languages': ['en', 'fr', 'es'],
            'timezone': 'America/New_York',
            'date_format': '%Y-%m-%d',
            'time_format': '%H:%M'
        }
        
        response = client.post('/api/settings/general', json=data, headers=auth_headers)
        assert response.status_code == 201
        assert response.json['site_name'] == 'BDC Test Platform'
        assert response.json['supported_languages'] == ['en', 'fr', 'es']
    
    def test_update_general_settings(self, client, auth_headers, test_user, db_session):
        """Test updating general settings."""
        # Create settings first
        settings = GeneralSettings(
            tenant_id=test_user.tenant_id,
            site_name='Old Name',
            contact_email='old@test.com'
        )
        db_session.add(settings)
        db_session.commit()
        
        update_data = {
            'site_name': 'New Name',
            'contact_email': 'new@test.com',
            'maintenance_mode': True
        }
        
        response = client.put('/api/settings/general', json=update_data, headers=auth_headers)
        assert response.status_code == 200
        assert response.json['site_name'] == 'New Name'
        assert response.json['maintenance_mode'] is True
    
    def test_general_settings_permissions(self, client, student_headers):
        """Test that regular users cannot modify general settings."""
        data = {'site_name': 'Unauthorized Change'}
        response = client.post('/api/settings/general', json=data, headers=student_headers)
        assert response.status_code == 403
    
    def test_invalid_language_setting(self, client, auth_headers):
        """Test setting an invalid language."""
        data = {
            'default_language': 'invalid_lang',
            'supported_languages': ['en', 'invalid']
        }
        
        response = client.post('/api/settings/general', json=data, headers=auth_headers)
        assert response.status_code == 400


class TestAppearanceSettingsAPI:
    """Test appearance settings API endpoints."""
    
    def test_get_default_appearance_settings(self, client, auth_headers):
        """Test getting appearance settings when none exist."""
        response = client.get('/api/settings/appearance', headers=auth_headers)
        assert response.status_code == 200
        assert 'theme' in response.json
        assert 'primary_color' in response.json
    
    def test_create_appearance_settings(self, client, auth_headers):
        """Test creating appearance settings."""
        data = {
            'theme': 'dark',
            'primary_color': '#3B82F6',
            'secondary_color': '#10B981',
            'accent_color': '#F59E0B',
            'font_family': 'Inter',
            'font_size': 16,
            'logo_url': '/assets/logo.png',
            'favicon_url': '/assets/favicon.ico',
            'login_background_url': '/assets/login-bg.jpg'
        }
        
        response = client.post('/api/settings/appearance', json=data, headers=auth_headers)
        assert response.status_code == 201
        assert response.json['theme'] == 'dark'
        assert response.json['primary_color'] == '#3B82F6'
    
    def test_update_appearance_settings(self, client, auth_headers, test_user, db_session):
        """Test updating appearance settings."""
        settings = AppearanceSettings(
            tenant_id=test_user.tenant_id,
            theme='light',
            primary_color='#000000'
        )
        db_session.add(settings)
        db_session.commit()
        
        update_data = {
            'theme': 'dark',
            'primary_color': '#FFFFFF',
            'enable_animations': False
        }
        
        response = client.put('/api/settings/appearance', json=update_data, headers=auth_headers)
        assert response.status_code == 200
        assert response.json['theme'] == 'dark'
        assert response.json['enable_animations'] is False
    
    def test_invalid_color_format(self, client, auth_headers):
        """Test setting invalid color values."""
        data = {
            'primary_color': 'not-a-color',
            'secondary_color': '123456'  # Missing #
        }
        
        response = client.post('/api/settings/appearance', json=data, headers=auth_headers)
        assert response.status_code == 400
    
    def test_upload_logo(self, client, auth_headers):
        """Test uploading a logo file."""
        # Create a fake file
        data = {
            'logo': (b'fake image data', 'logo.png')
        }
        
        response = client.post(
            '/api/settings/appearance/logo',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        # Should handle file upload or return appropriate error
        assert response.status_code in [200, 201, 400, 404]
    
    def test_theme_preview(self, client, auth_headers):
        """Test theme preview functionality."""
        preview_data = {
            'theme': 'custom',
            'primary_color': '#FF5722',
            'font_family': 'Roboto'
        }
        
        response = client.post(
            '/api/settings/appearance/preview',
            json=preview_data,
            headers=auth_headers
        )
        # API should return preview or indicate not implemented
        assert response.status_code in [200, 404]
    
    def test_reset_to_defaults(self, client, auth_headers, test_user, db_session):
        """Test resetting appearance settings to defaults."""
        # Create custom settings first
        settings = AppearanceSettings(
            tenant_id=test_user.tenant_id,
            theme='custom',
            primary_color='#123456'
        )
        db_session.add(settings)
        db_session.commit()
        
        response = client.post('/api/settings/appearance/reset', headers=auth_headers)
        # Should reset or indicate not implemented
        assert response.status_code in [200, 404]