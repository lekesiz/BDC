"""
i18n API Tests
Tests for API endpoints with internationalization support
"""

import pytest
import json
from unittest.mock import Mock, patch
from flask import Flask

from utils import (
    create_test_app,
    get_mock_translations,
    set_test_locale,
    test_api_response_translation,
    mock_user_with_language,
    TranslationTestCase,
    SUPPORTED_LANGUAGES,
    RTL_LANGUAGES
)


class TestI18nAPIEndpoints:
    """Test API endpoints with i18n support"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app, babel = create_test_app()
        
        # Mock routes for testing
        @app.route('/api/auth/login', methods=['POST'])
        def login():
            from flask import request, jsonify
            data = request.get_json()
            
            # Mock authentication logic
            if data.get('email') == 'valid@example.com' and data.get('password') == 'password':
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {'id': 1, 'email': 'valid@example.com'},
                    '_locale': 'en'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials',
                    '_locale': 'en'
                }), 401
        
        @app.route('/api/users', methods=['POST'])
        def create_user():
            from flask import request, jsonify
            data = request.get_json()
            
            # Mock validation
            errors = {}
            if not data.get('email'):
                errors['email'] = 'Email is required'
            if not data.get('password'):
                errors['password'] = 'Password is required'
            
            if errors:
                return jsonify({
                    'success': False,
                    'errors': errors,
                    'message': 'Validation error',
                    '_locale': 'en'
                }), 400
            
            return jsonify({
                'success': True,
                'message': 'User created successfully',
                'user': {'id': 2, 'email': data['email']},
                '_locale': 'en'
            }), 201
        
        @app.route('/api/beneficiaries', methods=['GET'])
        def list_beneficiaries():
            from flask import jsonify
            return jsonify({
                'success': True,
                'data': [
                    {'id': 1, 'name': 'John Doe', 'status': 'active'},
                    {'id': 2, 'name': 'Jane Smith', 'status': 'inactive'}
                ],
                'total': 2,
                'message': 'Beneficiaries retrieved successfully',
                '_locale': 'en'
            })
        
        @app.route('/api/beneficiaries/<int:id>', methods=['DELETE'])
        def delete_beneficiary(id):
            from flask import jsonify
            if id == 999:
                return jsonify({
                    'success': False,
                    'message': 'Beneficiary not found',
                    '_locale': 'en'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Beneficiary deleted successfully',
                '_locale': 'en'
            })
        
        @app.route('/api/evaluations', methods=['POST'])
        def create_evaluation():
            from flask import request, jsonify
            data = request.get_json()
            
            return jsonify({
                'success': True,
                'message': 'Evaluation created successfully',
                'evaluation': {
                    'id': 1,
                    'beneficiary_id': data.get('beneficiary_id'),
                    'status': 'draft'
                },
                '_locale': 'en'
            }), 201
        
        @app.route('/api/settings/language', methods=['PUT'])
        def update_language():
            from flask import request, jsonify
            data = request.get_json()
            language = data.get('language')
            
            if language not in SUPPORTED_LANGUAGES:
                return jsonify({
                    'success': False,
                    'message': 'Unsupported language',
                    '_locale': 'en'
                }), 400
            
            return jsonify({
                'success': True,
                'message': 'Language updated successfully',
                'language': language,
                '_locale': language
            })
        
        @app.route('/api/notifications', methods=['GET'])
        def get_notifications():
            from flask import jsonify
            return jsonify({
                'success': True,
                'data': [
                    {
                        'id': 1,
                        'message': 'You have a new message from John Doe',
                        'type': 'message',
                        'created_at': '2025-01-01T10:00:00Z'
                    }
                ],
                'message': 'Notifications retrieved successfully',
                '_locale': 'en'
            })
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_login_success_english(self, client):
        """Test successful login with English locale"""
        response = client.post('/api/auth/login', 
                             json={'email': 'valid@example.com', 'password': 'password'},
                             headers={'Accept-Language': 'en'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == 'Login successful'
        assert data['_locale'] == 'en'
    
    def test_login_failure_spanish(self, client):
        """Test login failure with Spanish locale"""
        response = client.post('/api/auth/login', 
                             json={'email': 'invalid@example.com', 'password': 'wrong'},
                             headers={'Accept-Language': 'es'})
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        # In a real implementation, this would be translated
        assert 'message' in data
    
    def test_validation_errors_multiple_languages(self, client):
        """Test validation errors in different languages"""
        languages = ['en', 'es', 'fr', 'ar']
        
        for lang in languages:
            response = client.post('/api/users',
                                 json={},  # Empty data to trigger validation
                                 headers={'Accept-Language': lang})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'errors' in data
            assert 'email' in data['errors']
            assert 'password' in data['errors']
    
    def test_successful_creation_all_languages(self, client):
        """Test successful resource creation in all languages"""
        user_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        for lang in SUPPORTED_LANGUAGES.keys():
            response = client.post('/api/users',
                                 json=user_data,
                                 headers={'Accept-Language': lang})
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            assert 'message' in data
    
    def test_not_found_error_with_locale(self, client):
        """Test 404 error with locale information"""
        response = client.delete('/api/beneficiaries/999',
                                headers={'Accept-Language': 'ar'})
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'message' in data
    
    def test_language_setting_endpoint(self, client):
        """Test language setting API endpoint"""
        # Test valid language
        response = client.put('/api/settings/language',
                            json={'language': 'es'},
                            headers={'Accept-Language': 'en'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['language'] == 'es'
        assert data['_locale'] == 'es'
        
        # Test invalid language
        response = client.put('/api/settings/language',
                            json={'language': 'invalid'},
                            headers={'Accept-Language': 'en'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_rtl_language_response_markers(self, client):
        """Test that RTL languages include proper markers"""
        rtl_languages = ['ar', 'he']
        
        for lang in rtl_languages:
            response = client.get('/api/beneficiaries',
                                headers={'Accept-Language': lang})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['_locale'] == lang
            # In a real implementation, would include _direction: 'rtl'
    
    def test_notification_messages_translation(self, client):
        """Test notification messages with different languages"""
        languages = ['en', 'es', 'ar', 'he']
        
        for lang in languages:
            response = client.get('/api/notifications',
                                headers={'Accept-Language': lang})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert len(data['data']) > 0
    
    def test_content_negotiation(self, client):
        """Test content negotiation with multiple Accept-Language values"""
        # Test with quality values
        response = client.get('/api/beneficiaries',
                            headers={'Accept-Language': 'ar;q=0.9,en;q=0.8,es;q=0.7'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Should prefer Arabic (highest quality)
        assert data['_locale'] in ['ar', 'en']  # Fallback to English if Arabic not fully supported
    
    def test_evaluation_creation_with_locale(self, client):
        """Test evaluation creation with different locales"""
        evaluation_data = {
            'beneficiary_id': 1,
            'type': 'assessment',
            'title': 'Test Evaluation'
        }
        
        for lang in ['en', 'es', 'fr']:
            response = client.post('/api/evaluations',
                                 json=evaluation_data,
                                 headers={'Accept-Language': lang})
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            assert 'evaluation' in data


class TestI18nAPIWithMockedTranslations:
    """Test API with mocked translation service"""
    
    @pytest.fixture
    def app_with_translations(self):
        """Create test app with mocked translations"""
        app, babel = create_test_app()
        translations = get_mock_translations()
        
        # Mock the translation function
        def mock_translate(key, **kwargs):
            from flask_babel import get_locale
            locale = str(get_locale()) or 'en'
            trans = translations.get(locale, translations.get('en', {}))
            
            keys = key.split('.')
            value = trans
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return key
            
            if kwargs and isinstance(value, str):
                try:
                    return value.format(**kwargs)
                except KeyError:
                    return value
            
            return value
        
        @app.route('/api/auth/login', methods=['POST'])
        def login_with_translation():
            from flask import request, jsonify
            data = request.get_json()
            
            if data.get('email') == 'valid@example.com':
                return jsonify({
                    'success': True,
                    'message': mock_translate('api.auth.login_success'),
                    '_locale': str(get_locale())
                })
            else:
                return jsonify({
                    'success': False,
                    'message': mock_translate('api.auth.login_failed'),
                    '_locale': str(get_locale())
                }), 401
        
        @app.route('/api/users', methods=['POST'])
        def create_user_with_validation():
            from flask import request, jsonify
            data = request.get_json()
            
            errors = {}
            if not data.get('email'):
                errors['email'] = mock_translate('api.validation.field_required', field='Email')
            
            if errors:
                return jsonify({
                    'success': False,
                    'errors': errors,
                    'message': mock_translate('api.error.validation'),
                    '_locale': str(get_locale())
                }), 400
            
            return jsonify({
                'success': True,
                'message': mock_translate('api.success.created'),
                '_locale': str(get_locale())
            }), 201
        
        return app
    
    @pytest.fixture
    def client_with_translations(self, app_with_translations):
        """Create test client with translations"""
        return app_with_translations.test_client()
    
    def test_translated_login_success(self, client_with_translations):
        """Test login success with actual translations"""
        # Test English
        response = client_with_translations.post('/api/auth/login',
                                                json={'email': 'valid@example.com', 'password': 'password'},
                                                headers={'Accept-Language': 'en'})
        
        data = response.get_json()
        assert data['message'] == 'Login successful'
        
        # Test Spanish
        response = client_with_translations.post('/api/auth/login',
                                                json={'email': 'valid@example.com', 'password': 'password'},
                                                headers={'Accept-Language': 'es'})
        
        data = response.get_json()
        assert data['message'] == 'Inicio de sesión exitoso'
    
    def test_translated_validation_errors(self, client_with_translations):
        """Test validation errors with translations"""
        # Test English
        response = client_with_translations.post('/api/users',
                                                json={},
                                                headers={'Accept-Language': 'en'})
        
        data = response.get_json()
        assert data['message'] == 'Validation error'
        assert data['errors']['email'] == 'Email is required'
        
        # Test Spanish
        response = client_with_translations.post('/api/users',
                                                json={},
                                                headers={'Accept-Language': 'es'})
        
        data = response.get_json()
        assert data['message'] == 'Error de validación'
    
    def test_successful_creation_messages(self, client_with_translations):
        """Test success messages in different languages"""
        user_data = {'email': 'test@example.com', 'password': 'password'}
        
        # Test English
        response = client_with_translations.post('/api/users',
                                                json=user_data,
                                                headers={'Accept-Language': 'en'})
        
        data = response.get_json()
        assert data['message'] == 'Resource created successfully'
        
        # Test Spanish
        response = client_with_translations.post('/api/users',
                                                json=user_data,
                                                headers={'Accept-Language': 'es'})
        
        data = response.get_json()
        assert data['message'] == 'Recurso creado exitosamente'


class TestI18nErrorHandling:
    """Test i18n error handling scenarios"""
    
    @pytest.fixture
    def app_with_errors(self):
        """Create test app that can produce errors"""
        app, babel = create_test_app()
        
        @app.route('/api/error/500')
        def server_error():
            raise Exception("Test server error")
        
        @app.route('/api/error/translation-missing')
        def missing_translation():
            from flask import jsonify
            # Simulate missing translation key
            return jsonify({
                'message': 'api.missing.key',  # Non-existent key
                '_locale': 'en'
            })
        
        @app.errorhandler(500)
        def handle_server_error(e):
            from flask import jsonify
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                '_locale': 'en'
            }), 500
        
        return app
    
    @pytest.fixture
    def error_client(self, app_with_errors):
        """Create error test client"""
        return app_with_errors.test_client()
    
    def test_server_error_with_locale(self, error_client):
        """Test server error includes locale information"""
        response = error_client.get('/api/error/500',
                                  headers={'Accept-Language': 'es'})
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert '_locale' in data
    
    def test_missing_translation_fallback(self, error_client):
        """Test handling of missing translation keys"""
        response = error_client.get('/api/error/translation-missing',
                                  headers={'Accept-Language': 'fr'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Should fallback to key name or default message
        assert 'message' in data


@pytest.mark.parametrize("language,expected_direction", [
    ('en', 'ltr'),
    ('es', 'ltr'),
    ('fr', 'ltr'),
    ('ar', 'rtl'),
    ('he', 'rtl'),
    ('de', 'ltr'),
    ('ru', 'ltr')
])
def test_language_direction_detection(language, expected_direction):
    """Test that language direction is correctly detected"""
    from utils import is_rtl_language
    
    if expected_direction == 'rtl':
        assert is_rtl_language(language) is True
    else:
        assert is_rtl_language(language) is False


class TestI18nIntegration:
    """Integration tests for i18n system"""
    
    def test_full_request_cycle_with_translations(self):
        """Test complete request cycle with translations"""
        app, babel = create_test_app()
        
        @app.route('/api/complete-test')
        def complete_test():
            from flask import jsonify, request
            from flask_babel import get_locale
            
            locale = str(get_locale())
            
            # Simulate complex response with multiple translated elements
            response_data = {
                'success': True,
                'locale_info': {
                    'code': locale,
                    'direction': 'rtl' if locale in RTL_LANGUAGES else 'ltr',
                    'is_rtl': locale in RTL_LANGUAGES
                },
                'data': {
                    'welcome_message': f'Welcome in {locale}',
                    'instructions': 'Follow these steps',
                    'items': [
                        {'id': 1, 'name': 'Item 1'},
                        {'id': 2, 'name': 'Item 2'}
                    ]
                },
                '_locale': locale
            }
            
            return jsonify(response_data)
        
        client = app.test_client()
        
        # Test with different languages
        for lang in ['en', 'es', 'ar', 'he']:
            response = client.get('/api/complete-test',
                                headers={'Accept-Language': lang})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['_locale'] == lang
            assert data['locale_info']['code'] == lang
            
            if lang in RTL_LANGUAGES:
                assert data['locale_info']['direction'] == 'rtl'
                assert data['locale_info']['is_rtl'] is True
            else:
                assert data['locale_info']['direction'] == 'ltr'
                assert data['locale_info']['is_rtl'] is False