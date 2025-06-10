"""
i18n Testing Utilities for Backend
Comprehensive utilities for testing internationalization features in Flask
"""

import json
import os
from contextlib import contextmanager
from unittest.mock import Mock, patch
from flask import Flask, request
from flask_babel import Babel, get_locale

# Supported languages mapping
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'tr': 'Türkçe',
    'ar': 'العربية',
    'he': 'עברית',
    'de': 'Deutsch',
    'ru': 'Русский'
}

RTL_LANGUAGES = ['ar', 'he']


def create_test_app():
    """Create a test Flask app with i18n support"""
    app = Flask(__name__)
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    babel = Babel(app)
    
    @babel.localeselector
    def get_locale():
        # Mock locale selection for testing
        return request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys()) or 'en'
    
    return app, babel


def get_mock_translations():
    """Get mock translations for testing"""
    return {
        'en': {
            'api': {
                'success': {
                    'created': 'Resource created successfully',
                    'updated': 'Resource updated successfully',
                    'deleted': 'Resource deleted successfully',
                    'generic': 'Operation completed successfully'
                },
                'error': {
                    'not_found': 'Resource not found',
                    'unauthorized': 'Unauthorized access',
                    'forbidden': 'Access forbidden',
                    'validation': 'Validation error',
                    'generic': 'An error occurred',
                    'server': 'Internal server error'
                },
                'auth': {
                    'login_success': 'Login successful',
                    'login_failed': 'Invalid credentials',
                    'logout_success': 'Logout successful',
                    'register_success': 'Registration successful',
                    'token_expired': 'Token has expired',
                    'invalid_token': 'Invalid token'
                },
                'validation': {
                    'field_required': '{field} is required',
                    'invalid_email': 'Invalid email format',
                    'invalid_phone': 'Invalid phone number',
                    'invalid_date': 'Invalid date format',
                    'min_length': '{field} must be at least {length} characters',
                    'max_length': '{field} must not exceed {length} characters'
                }
            },
            'email': {
                'welcome': {
                    'subject': 'Welcome to BDC',
                    'body': 'Hello {name}, welcome to BDC!'
                },
                'password_reset': {
                    'subject': 'Password Reset Request',
                    'body': 'Click here to reset your password: {link}'
                },
                'evaluation_reminder': {
                    'subject': 'Evaluation Reminder',
                    'body': 'You have an evaluation scheduled for {date}'
                }
            },
            'notifications': {
                'new_message': 'You have a new message from {sender}',
                'evaluation_completed': 'Evaluation for {beneficiary} has been completed',
                'appointment_reminder': 'Appointment with {person} at {time}',
                'document_shared': '{user} shared a document with you'
            }
        },
        'es': {
            'api': {
                'success': {
                    'created': 'Recurso creado exitosamente',
                    'updated': 'Recurso actualizado exitosamente',
                    'deleted': 'Recurso eliminado exitosamente',
                    'generic': 'Operación completada exitosamente'
                },
                'error': {
                    'not_found': 'Recurso no encontrado',
                    'unauthorized': 'Acceso no autorizado',
                    'forbidden': 'Acceso prohibido',
                    'validation': 'Error de validación',
                    'generic': 'Ocurrió un error',
                    'server': 'Error interno del servidor'
                },
                'auth': {
                    'login_success': 'Inicio de sesión exitoso',
                    'login_failed': 'Credenciales inválidas',
                    'logout_success': 'Cierre de sesión exitoso',
                    'register_success': 'Registro exitoso'
                }
            }
        },
        'ar': {
            'api': {
                'success': {
                    'created': 'تم إنشاء المورد بنجاح',
                    'updated': 'تم تحديث المورد بنجاح',
                    'deleted': 'تم حذف المورد بنجاح',
                    'generic': 'تمت العملية بنجاح'
                },
                'error': {
                    'not_found': 'المورد غير موجود',
                    'unauthorized': 'غير مصرح بالوصول',
                    'forbidden': 'الوصول محظور',
                    'validation': 'خطأ في التحقق',
                    'generic': 'حدث خطأ',
                    'server': 'خطأ في الخادم الداخلي'
                }
            }
        },
        'he': {
            'api': {
                'success': {
                    'created': 'המשאב נוצר בהצלחה',
                    'updated': 'המשאב עודכן בהצלחה',
                    'deleted': 'המשאב נמחק בהצלחה',
                    'generic': 'הפעולה הושלמה בהצלחה'
                }
            }
        }
    }


@contextmanager
def set_test_locale(app, locale='en'):
    """Context manager to set locale for testing"""
    with app.test_request_context(headers={'Accept-Language': locale}):
        yield


def mock_translate_function(translations_dict):
    """Create a mock translate function"""
    def translate(key, **kwargs):
        locale = get_locale() or 'en'
        translations = translations_dict.get(str(locale), translations_dict.get('en', {}))
        
        # Navigate through nested keys
        keys = key.split('.')
        value = translations
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key  # Return key if translation not found
        
        # Format with kwargs if provided
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return value
    
    return translate


def check_translation_completeness(translations, reference_lang='en'):
    """Check if all languages have complete translations"""
    missing_translations = {}
    reference = translations.get(reference_lang, {})
    
    def get_all_keys(obj, prefix=''):
        keys = []
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(get_all_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys
    
    reference_keys = set(get_all_keys(reference))
    
    for lang, trans in translations.items():
        if lang == reference_lang:
            continue
        
        lang_keys = set(get_all_keys(trans))
        missing = reference_keys - lang_keys
        if missing:
            missing_translations[lang] = list(missing)
    
    return missing_translations


def test_api_response_translation(client, endpoint, method='GET', expected_message_key=None, 
                                headers=None, data=None, locale='en'):
    """Test API endpoint with different locales"""
    headers = headers or {}
    headers['Accept-Language'] = locale
    
    if method == 'GET':
        response = client.get(endpoint, headers=headers)
    elif method == 'POST':
        response = client.post(endpoint, headers=headers, json=data)
    elif method == 'PUT':
        response = client.put(endpoint, headers=headers, json=data)
    elif method == 'DELETE':
        response = client.delete(endpoint, headers=headers)
    
    return response


def mock_user_with_language(language='en'):
    """Create a mock user with language preference"""
    user = Mock()
    user.language = language
    user.id = 1
    user.email = 'test@example.com'
    return user


def is_rtl_language(language):
    """Check if language is RTL"""
    return language in RTL_LANGUAGES


def format_number_for_locale(number, locale='en'):
    """Format number according to locale"""
    # Simple mock implementation
    if locale in ['es', 'fr', 'de', 'ru']:
        return f"{number:,}".replace(',', '.')
    elif locale in ['ar', 'he']:
        return f"{number:,}"
    return f"{number:,}"


def format_currency_for_locale(amount, locale='en', currency=None):
    """Format currency according to locale"""
    currency_map = {
        'en': ('$', 'USD'),
        'es': ('€', 'EUR'),
        'fr': ('€', 'EUR'),
        'de': ('€', 'EUR'),
        'tr': ('₺', 'TRY'),
        'ar': ('ر.س', 'SAR'),
        'he': ('₪', 'ILS'),
        'ru': ('₽', 'RUB')
    }
    
    symbol, code = currency_map.get(locale, ('$', 'USD'))
    if currency:
        code = currency
    
    formatted_amount = format_number_for_locale(amount, locale)
    
    if locale in RTL_LANGUAGES:
        return f"{formatted_amount} {symbol}"
    return f"{symbol}{formatted_amount}"


def format_date_for_locale(date, locale='en'):
    """Format date according to locale"""
    from datetime import datetime
    
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    
    format_map = {
        'en': '%m/%d/%Y',
        'es': '%d/%m/%Y',
        'fr': '%d/%m/%Y',
        'de': '%d.%m.%Y',
        'tr': '%d.%m.%Y',
        'ar': '%d/%m/%Y',
        'he': '%d/%m/%Y',
        'ru': '%d.%m.%Y'
    }
    
    date_format = format_map.get(locale, '%Y-%m-%d')
    return date.strftime(date_format)


def validate_translation_keys(translation_file_path):
    """Validate translation JSON file structure"""
    try:
        with open(translation_file_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        errors = []
        
        # Check for required top-level keys
        required_keys = ['api', 'email', 'notifications']
        for key in required_keys:
            if key not in translations:
                errors.append(f"Missing required key: {key}")
        
        # Check for empty values
        def check_empty_values(obj, path=''):
            for k, v in obj.items():
                full_path = f"{path}.{k}" if path else k
                if isinstance(v, dict):
                    check_empty_values(v, full_path)
                elif v == '' or v is None:
                    errors.append(f"Empty value at: {full_path}")
        
        check_empty_values(translations)
        
        return errors
        
    except Exception as e:
        return [f"Error reading file: {str(e)}"]


def generate_translation_report(translations):
    """Generate a report of translation coverage"""
    report = {
        'total_languages': len(translations),
        'languages': list(translations.keys()),
        'coverage': {}
    }
    
    # Count keys per language
    for lang, trans in translations.items():
        def count_keys(obj):
            count = 0
            for v in obj.values():
                if isinstance(v, dict):
                    count += count_keys(v)
                else:
                    count += 1
            return count
        
        report['coverage'][lang] = count_keys(trans)
    
    # Calculate coverage percentage
    max_keys = max(report['coverage'].values())
    for lang, count in report['coverage'].items():
        percentage = (count / max_keys * 100) if max_keys > 0 else 0
        report['coverage'][lang] = {
            'keys': count,
            'percentage': round(percentage, 2)
        }
    
    return report


class TranslationTestCase:
    """Base class for translation test cases"""
    
    def __init__(self, app, translations=None):
        self.app = app
        self.translations = translations or get_mock_translations()
        self.client = app.test_client()
    
    def test_with_locale(self, locale, test_func):
        """Run test function with specific locale"""
        with set_test_locale(self.app, locale):
            return test_func()
    
    def test_all_locales(self, test_func):
        """Run test function for all supported locales"""
        results = {}
        for locale in SUPPORTED_LANGUAGES.keys():
            results[locale] = self.test_with_locale(locale, test_func)
        return results
    
    def assert_translation_exists(self, key, locale='en'):
        """Assert that a translation key exists"""
        translations = self.translations.get(locale, {})
        keys = key.split('.')
        value = translations
        
        for k in keys:
            assert k in value, f"Translation key '{key}' not found for locale '{locale}'"
            value = value[k]
        
        assert value is not None and value != '', f"Translation for '{key}' is empty in locale '{locale}'"
    
    def assert_rtl_response(self, response_data, locale):
        """Assert that response contains RTL markers for RTL languages"""
        if is_rtl_language(locale):
            assert response_data.get('_direction') == 'rtl', f"Missing RTL direction for locale '{locale}'"
            assert response_data.get('_locale') == locale, f"Incorrect locale in response"


def create_test_translation_file(filepath, language, translations):
    """Create a test translation file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)


def cleanup_test_translation_files(directory):
    """Clean up test translation files"""
    import shutil
    if os.path.exists(directory):
        shutil.rmtree(directory)