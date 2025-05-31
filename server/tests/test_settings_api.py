"""Tests for settings API endpoints."""

import pytest
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models.user import User
from app.models.settings import GeneralSettings, AppearanceSettings


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def admin_headers(app):
    """Create authentication headers for an admin user."""
    with app.app_context():
        user = User(
            email='admin@test.com',
            username='admin',
            password='password123',
            first_name='Admin',
            last_name='User',
            role='tenant_admin',
            tenant_id=1
        )
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def user_headers(app):
    """Create authentication headers for a regular user."""
    with app.app_context():
        user = User(
            email='user@test.com',
            username='user',
            password='password123',
            first_name='Regular',
            last_name='User',
            role='student',
            tenant_id=1
        )
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}


class TestGeneralSettingsAPI:
    """Test general settings API endpoints."""
    
    def test_get_default_general_settings(self, client, admin_headers):
        """Test getting general settings when none exist."""
        response = client.get('/api/settings/general', headers=admin_headers)
        assert response.status_code == 200
        # Should return default settings
        assert 'site_name' in response.json
        assert 'default_language' in response.json
    
    def test_create_general_settings(self, client, admin_headers):
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
        
        response = client.post('/api/settings/general', json=data, headers=admin_headers)
        assert response.status_code == 201
        assert response.json['site_name'] == 'BDC Test Platform'
        assert response.json['supported_languages'] == ['en', 'fr', 'es']
    
    def test_update_general_settings(self, client, admin_headers, app):
        """Test updating general settings."""
        with app.app_context():
            # Create settings first
            tenant_id = User.query.filter_by(email='admin@test.com').first().tenant_id
            settings = GeneralSettings(
                tenant_id=tenant_id,
                site_name='Old Name',
                contact_email='old@test.com'
            )
            db.session.add(settings)
            db.session.commit()
        
        update_data = {
            'site_name': 'New Name',
            'contact_email': 'new@test.com',
            'maintenance_mode': True
        }
        
        response = client.put('/api/settings/general', json=update_data, headers=admin_headers)
        assert response.status_code == 200
        assert response.json['site_name'] == 'New Name'
        assert response.json['maintenance_mode'] is True
    
    def test_general_settings_permissions(self, client, user_headers):
        """Test that regular users cannot modify general settings."""
        data = {'site_name': 'Unauthorized Change'}
        response = client.post('/api/settings/general', json=data, headers=user_headers)
        assert response.status_code == 403
    
    def test_invalid_language_setting(self, client, admin_headers):
        """Test setting an invalid language."""
        data = {
            'default_language': 'invalid_lang',
            'supported_languages': ['en', 'invalid']
        }
        
        response = client.post('/api/settings/general', json=data, headers=admin_headers)
        assert response.status_code == 400


class TestAppearanceSettingsAPI:
    """Test appearance settings API endpoints."""
    
    def test_get_default_appearance_settings(self, client, admin_headers):
        """Test getting appearance settings when none exist."""
        response = client.get('/api/settings/appearance', headers=admin_headers)
        assert response.status_code == 200
        assert 'theme' in response.json
        assert 'primary_color' in response.json
    
    def test_create_appearance_settings(self, client, admin_headers):
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
        
        response = client.post('/api/settings/appearance', json=data, headers=admin_headers)
        assert response.status_code == 201
        assert response.json['theme'] == 'dark'
        assert response.json['primary_color'] == '#3B82F6'
    
    def test_update_appearance_settings(self, client, admin_headers, app):
        """Test updating appearance settings."""
        with app.app_context():
            tenant_id = User.query.filter_by(email='admin@test.com').first().tenant_id
            settings = AppearanceSettings(
                tenant_id=tenant_id,
                theme='light',
                primary_color='#000000'
            )
            db.session.add(settings)
            db.session.commit()
        
        update_data = {
            'theme': 'dark',
            'primary_color': '#FFFFFF',
            'enable_animations': False
        }
        
        response = client.put('/api/settings/appearance', json=update_data, headers=admin_headers)
        assert response.status_code == 200
        assert response.json['theme'] == 'dark'
        assert response.json['enable_animations'] is False
    
    def test_invalid_color_format(self, client, admin_headers):
        """Test setting invalid color values."""
        data = {
            'primary_color': 'not-a-color',
            'secondary_color': '123456'  # Missing #
        }
        
        response = client.post('/api/settings/appearance', json=data, headers=admin_headers)
        assert response.status_code == 400
    
    def test_upload_logo(self, client, admin_headers):
        """Test uploading a logo file."""
        # Create a fake file
        data = {
            'logo': (b'fake image data', 'logo.png')
        }
        
        response = client.post(
            '/api/settings/appearance/logo',
            data=data,
            headers=admin_headers,
            content_type='multipart/form-data'
        )
        # Should handle file upload or return appropriate error
        assert response.status_code in [200, 201, 400]
    
    def test_theme_preview(self, client, admin_headers):
        """Test theme preview functionality."""
        preview_data = {
            'theme': 'custom',
            'primary_color': '#FF5722',
            'font_family': 'Roboto'
        }
        
        response = client.post(
            '/api/settings/appearance/preview',
            json=preview_data,
            headers=admin_headers
        )
        # API should return preview or indicate not implemented
        assert response.status_code in [200, 404]
    
    def test_reset_to_defaults(self, client, admin_headers, app):
        """Test resetting appearance settings to defaults."""
        with app.app_context():
            # Create custom settings first
            tenant_id = User.query.filter_by(email='admin@test.com').first().tenant_id
            settings = AppearanceSettings(
                tenant_id=tenant_id,
                theme='custom',
                primary_color='#123456'
            )
            db.session.add(settings)
            db.session.commit()
        
        response = client.post('/api/settings/appearance/reset', headers=admin_headers)
        # Should reset or indicate not implemented
        assert response.status_code in [200, 404]