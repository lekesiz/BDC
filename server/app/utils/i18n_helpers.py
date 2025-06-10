"""Internationalization helper functions."""

from typing import Dict, Any, List, Union
from flask import g
from app.services.i18n import TranslationService


def translate_validation_errors(errors: Dict[str, Union[str, List[str], Dict]]) -> Dict[str, Union[str, List[str], Dict]]:
    """
    Translate validation error messages.
    
    Args:
        errors: Dictionary of validation errors from Marshmallow
        
    Returns:
        Dictionary with translated error messages
    """
    translation_service = TranslationService()
    locale = getattr(g, 'user_language', 'en')
    
    def translate_error(error: Union[str, List[str], Dict]) -> Union[str, List[str], Dict]:
        """Recursively translate error messages."""
        if isinstance(error, str):
            # Check if it's already a translation key
            if error.startswith('$t:'):
                key = error[3:]
                result = translation_service.translate(key, locale)
                return result.text if result else error
            # Try to find a matching translation key
            key = _find_validation_error_key(error)
            if key:
                result = translation_service.translate(key, locale)
                return result.text if result else error
            return error
        elif isinstance(error, list):
            return [translate_error(e) for e in error]
        elif isinstance(error, dict):
            return {k: translate_error(v) for k, v in error.items()}
        return error
    
    return {field: translate_error(error) for field, error in errors.items()}


def _find_validation_error_key(message: str) -> str:
    """Find a translation key for common validation error messages."""
    # Common validation message mappings
    validation_map = {
        # Field validation
        'Missing data for required field.': 'api.validation.field_required',
        'Field may not be null.': 'api.validation.field_required',
        'Not a valid email address.': 'api.validation.invalid_email',
        'Not a valid phone number.': 'api.validation.invalid_phone',
        'Not a valid date.': 'api.validation.invalid_date',
        'Not a valid datetime.': 'api.validation.invalid_date',
        
        # String validation
        'Shorter than minimum length': 'api.validation.min_length',
        'Longer than maximum length': 'api.validation.max_length',
        'String does not match expected pattern.': 'api.validation.invalid_format',
        
        # Number validation
        'Must be greater than or equal to': 'api.validation.min_value',
        'Must be less than or equal to': 'api.validation.max_value',
        
        # Password validation
        'Password is too weak': 'api.validation.password_weak',
        'Passwords do not match': 'api.validation.passwords_not_match',
        
        # Choice validation
        'Not a valid choice.': 'api.validation.invalid_choice',
        'Invalid value.': 'api.validation.invalid_value',
        
        # Unique constraint
        'Already exists.': 'api.validation.unique',
        'This field must be unique.': 'api.validation.unique',
    }
    
    # Check exact matches first
    if message in validation_map:
        return validation_map[message]
    
    # Check partial matches
    for pattern, key in validation_map.items():
        if pattern.lower() in message.lower():
            return key
    
    return None


def format_translated_message(translation_key: str, **kwargs) -> str:
    """
    Format a translated message with parameters.
    
    Args:
        translation_key: The translation key (without $t: prefix)
        **kwargs: Parameters to format the message with
        
    Returns:
        Formatted translated message
    """
    translation_service = TranslationService()
    locale = getattr(g, 'user_language', 'en')
    
    result = translation_service.translate(translation_key, locale)
    if result and result.text:
        try:
            return result.text.format(**kwargs)
        except Exception:
            return result.text
    
    return translation_key


def get_user_locale() -> str:
    """Get the current user's locale."""
    return getattr(g, 'user_language', 'en')


def is_rtl_language(locale: str = None) -> bool:
    """Check if the locale is a right-to-left language."""
    if locale is None:
        locale = get_user_locale()
    
    rtl_languages = ['ar', 'he', 'fa', 'ur']
    return locale[:2] in rtl_languages