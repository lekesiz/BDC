"""
Internationalization (i18n) module for BDC backend
Provides translation support for API responses, emails, and messages
"""

from flask import request, current_app
from flask_babel import Babel, lazy_gettext, ngettext, get_locale
import os
import json
from functools import wraps

# Initialize Babel
babel = Babel()

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'tr': 'Türkçe',
    'ar': 'العربية',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ru': 'Русский',
    'he': 'עברית'
}

DEFAULT_LANGUAGE = 'en'


def init_babel(app):
    """Initialize Babel with the Flask app"""
    babel.init_app(app)
    
    # Configure Babel
    app.config['BABEL_DEFAULT_LOCALE'] = DEFAULT_LANGUAGE
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    @babel.localeselector
    def get_locale():
        """Select the best matching locale based on request"""
        # 1. Check if user has a preferred language in session
        if hasattr(request, 'user') and request.user and hasattr(request.user, 'language'):
            return request.user.language
        
        # 2. Check Accept-Language header
        requested = request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys())
        if requested:
            return requested
            
        # 3. Check if language is specified in query params
        lang = request.args.get('lang')
        if lang in SUPPORTED_LANGUAGES:
            return lang
            
        # 4. Return default language
        return DEFAULT_LANGUAGE
    
    return babel


def get_user_language():
    """Get the current user's language preference"""
    locale = get_locale()
    return str(locale) if locale else DEFAULT_LANGUAGE


def set_user_language(user, language):
    """Set user's language preference"""
    if language in SUPPORTED_LANGUAGES:
        user.language = language
        from app.extensions import db
        db.session.commit()
        return True
    return False


def translate(key, **kwargs):
    """
    Translate a message key
    
    Args:
        key: Translation key (e.g., 'auth.login_success')
        **kwargs: Variables to interpolate in the translation
    
    Returns:
        Translated string
    """
    # Load translations for current locale
    locale = get_user_language()
    translations = load_translations(locale)
    
    # Get translation by key (supports nested keys with dot notation)
    translation = get_nested_value(translations, key)
    
    if translation:
        # Interpolate variables if any
        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError:
                # If interpolation fails, return translation without interpolation
                return translation
        return translation
    
    # Fallback to key if translation not found
    return key


def translate_lazy(key, **kwargs):
    """Lazy translation for messages that need to be translated at request time"""
    return lazy_gettext(key, **kwargs)


def pluralize(singular, plural, count, **kwargs):
    """
    Handle pluralization
    
    Args:
        singular: Singular form key
        plural: Plural form key  
        count: Number for determining plural form
        **kwargs: Variables to interpolate
    
    Returns:
        Translated and pluralized string
    """
    return ngettext(singular, plural, count, **kwargs)


def load_translations(locale):
    """Load translation file for a specific locale"""
    translations_dir = os.path.join(current_app.root_path, 'translations', locale)
    messages_file = os.path.join(translations_dir, 'messages.json')
    
    if os.path.exists(messages_file):
        with open(messages_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Fallback to English if locale file doesn't exist
    if locale != DEFAULT_LANGUAGE:
        return load_translations(DEFAULT_LANGUAGE)
    
    return {}


def get_nested_value(data, key):
    """Get value from nested dict using dot notation"""
    keys = key.split('.')
    value = data
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    
    return value


def get_available_languages():
    """Get list of available languages"""
    return [
        {
            'code': code,
            'name': name,
            'native_name': name,
            'active': code == get_user_language()
        }
        for code, name in SUPPORTED_LANGUAGES.items()
    ]


def localized_response(f):
    """
    Decorator to automatically add locale info to API responses
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Add locale info to response if it's a dict
        if isinstance(response, dict):
            response['_locale'] = get_user_language()
        elif isinstance(response, tuple) and isinstance(response[0], dict):
            response[0]['_locale'] = get_user_language()
            
        return response
    
    return decorated_function


# Common translations for API responses
class Messages:
    """Common translated messages for API responses"""
    
    # Success messages
    SUCCESS_CREATED = lambda: translate('api.success.created')
    SUCCESS_UPDATED = lambda: translate('api.success.updated')
    SUCCESS_DELETED = lambda: translate('api.success.deleted')
    SUCCESS_GENERIC = lambda: translate('api.success.generic')
    
    # Error messages
    ERROR_NOT_FOUND = lambda: translate('api.error.not_found')
    ERROR_UNAUTHORIZED = lambda: translate('api.error.unauthorized')
    ERROR_FORBIDDEN = lambda: translate('api.error.forbidden')
    ERROR_VALIDATION = lambda: translate('api.error.validation')
    ERROR_GENERIC = lambda: translate('api.error.generic')
    ERROR_SERVER = lambda: translate('api.error.server')
    
    # Auth messages
    AUTH_LOGIN_SUCCESS = lambda: translate('api.auth.login_success')
    AUTH_LOGIN_FAILED = lambda: translate('api.auth.login_failed')
    AUTH_LOGOUT_SUCCESS = lambda: translate('api.auth.logout_success')
    AUTH_REGISTER_SUCCESS = lambda: translate('api.auth.register_success')
    AUTH_TOKEN_EXPIRED = lambda: translate('api.auth.token_expired')
    AUTH_INVALID_TOKEN = lambda: translate('api.auth.invalid_token')
    
    # Validation messages
    FIELD_REQUIRED = lambda field: translate('api.validation.field_required', field=field)
    INVALID_EMAIL = lambda: translate('api.validation.invalid_email')
    INVALID_PHONE = lambda: translate('api.validation.invalid_phone')
    INVALID_DATE = lambda: translate('api.validation.invalid_date')
    MIN_LENGTH = lambda field, length: translate('api.validation.min_length', field=field, length=length)
    MAX_LENGTH = lambda field, length: translate('api.validation.max_length', field=field, length=length)


# Export main functions
__all__ = [
    'babel',
    'init_babel',
    'translate',
    'translate_lazy',
    'pluralize',
    'get_user_language',
    'set_user_language',
    'get_available_languages',
    'localized_response',
    'Messages',
    'SUPPORTED_LANGUAGES',
    'DEFAULT_LANGUAGE'
]