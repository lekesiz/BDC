"""
i18n Manager
Central manager for internationalization functionality
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from flask import request, session, g
from werkzeug.datastructures import LanguageAccept

from .config import I18nConfig
from .translator import Translator
from .locale_manager import LocaleManager
from .content_manager import ContentTranslationManager
from .language_detector import LanguageDetector
from .rtl_support import RTLSupport
from app.utils.cache import cache_manager

logger = logging.getLogger(__name__)

class I18nManager:
    """Central manager for i18n functionality."""
    
    def __init__(self):
        """Initialize i18n manager."""
        self.config = I18nConfig()
        self.translators = {}
        self.locale_manager = LocaleManager()
        self.content_manager = ContentTranslationManager()
        self.language_detector = LanguageDetector()
        self.rtl_support = RTLSupport()
        self._translations_cache = {}
        
        # Load all language translations on startup
        self._load_all_translations()
    
    def _load_all_translations(self):
        """Load translations for all supported languages."""
        for language_code in self.config.get_supported_language_codes():
            try:
                self._load_language_translations(language_code)
            except Exception as e:
                logger.error(f"Failed to load translations for {language_code}: {e}")
    
    def _load_language_translations(self, language_code: str) -> Dict[str, Any]:
        """Load translations for a specific language."""
        cache_key = f"{self.config.CACHE_KEY_PREFIX}:translations:{language_code}"
        
        # Check cache first
        if self.config.CACHE_ENABLED:
            cached = cache_manager.get(cache_key)
            if cached:
                return cached
        
        # Load from file
        translations_file = os.path.join(
            self.config.LOCALES_DIR,
            f"{language_code}.json"
        )
        
        translations = {}
        if os.path.exists(translations_file):
            try:
                with open(translations_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
            except Exception as e:
                logger.error(f"Error loading translations from {translations_file}: {e}")
        
        # Cache translations
        if self.config.CACHE_ENABLED and translations:
            cache_manager.set(cache_key, translations, self.config.CACHE_TIMEOUT)
        
        self._translations_cache[language_code] = translations
        return translations
    
    def get_translator(self, language_code: str) -> Translator:
        """Get or create translator for a language."""
        if language_code not in self.translators:
            # Ensure translations are loaded
            if language_code not in self._translations_cache:
                self._load_language_translations(language_code)
            
            self.translators[language_code] = Translator(
                language_code,
                self._translations_cache.get(language_code, {})
            )
        
        return self.translators[language_code]
    
    def translate(self, key: str, language_code: Optional[str] = None, **kwargs) -> str:
        """Translate a key to the specified language."""
        if language_code is None:
            language_code = self.get_current_language()
        
        translator = self.get_translator(language_code)
        return translator.translate(key, **kwargs)
    
    def get_current_language(self) -> str:
        """Get current language from request context."""
        # Check if already set in g
        if hasattr(g, 'language'):
            return g.language
        
        # Detect language
        language = self.detect_language(request)
        
        # Store in g for this request
        g.language = language
        
        return language
    
    def set_current_language(self, language_code: str) -> bool:
        """Set current language in session and cookie."""
        if language_code not in self.config.get_supported_language_codes():
            return False
        
        # Set in session
        session[self.config.LANGUAGE_SESSION_KEY] = language_code
        
        # Set in g
        g.language = language_code
        
        # Set cookie will be handled by response processor
        g.set_language_cookie = language_code
        
        return True
    
    def detect_language(self, request) -> str:
        """Detect language from request."""
        return self.language_detector.detect(request)
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available languages with metadata."""
        languages = []
        
        for code, config in self.config.SUPPORTED_LANGUAGES.items():
            languages.append({
                'code': code,
                'name': config.name,
                'native_name': config.native_name,
                'direction': config.direction,
                'flag': config.flag,
                'locale': config.locale
            })
        
        return languages
    
    def get_language_info(self, language_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a language."""
        config = self.config.get_language_config(language_code)
        if not config:
            return None
        
        return {
            'code': config.code,
            'name': config.name,
            'native_name': config.native_name,
            'direction': config.direction,
            'locale': config.locale,
            'flag': config.flag,
            'date_format': config.date_format,
            'currency': config.currency,
            'number_format': config.number_format,
            'is_rtl': config.direction == 'rtl'
        }
    
    def format_date(self, date, format_type: str = 'medium', 
                   language_code: Optional[str] = None) -> str:
        """Format date according to language locale."""
        if language_code is None:
            language_code = self.get_current_language()
        
        return self.locale_manager.format_date(date, format_type, language_code)
    
    def format_number(self, number, format_type: str = 'decimal',
                     language_code: Optional[str] = None, **kwargs) -> str:
        """Format number according to language locale."""
        if language_code is None:
            language_code = self.get_current_language()
        
        return self.locale_manager.format_number(number, format_type, language_code, **kwargs)
    
    def format_currency(self, amount, currency_code: Optional[str] = None,
                       language_code: Optional[str] = None) -> str:
        """Format currency according to language locale."""
        if language_code is None:
            language_code = self.get_current_language()
        
        return self.locale_manager.format_currency(amount, currency_code, language_code)
    
    def get_rtl_info(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """Get RTL information for a language."""
        if language_code is None:
            language_code = self.get_current_language()
        
        return self.rtl_support.get_rtl_info(language_code)
    
    def translate_content(self, entity_type: str, entity_id: str,
                         field_name: str, language_code: Optional[str] = None) -> Optional[str]:
        """Get translated content for an entity field."""
        if language_code is None:
            language_code = self.get_current_language()
        
        return self.content_manager.get_translation(
            entity_type, entity_id, field_name, language_code
        )
    
    def save_content_translation(self, entity_type: str, entity_id: str,
                                field_name: str, content: str,
                                language_code: Optional[str] = None,
                                user_id: Optional[int] = None) -> bool:
        """Save translated content for an entity field."""
        if language_code is None:
            language_code = self.get_current_language()
        
        return self.content_manager.save_translation(
            entity_type, entity_id, field_name, content, language_code, user_id
        )
    
    def get_missing_translations(self, language_code: Optional[str] = None) -> List[str]:
        """Get list of missing translation keys for a language."""
        if language_code is None:
            language_code = self.get_current_language()
        
        translator = self.get_translator(language_code)
        return translator.get_missing_keys()
    
    def reload_translations(self, language_code: Optional[str] = None):
        """Reload translations from files."""
        if language_code:
            # Reload specific language
            self._load_language_translations(language_code)
            if language_code in self.translators:
                del self.translators[language_code]
        else:
            # Reload all languages
            self._translations_cache.clear()
            self.translators.clear()
            self._load_all_translations()
        
        # Clear cache
        if self.config.CACHE_ENABLED:
            pattern = f"{self.config.CACHE_KEY_PREFIX}:translations:*"
            cache_manager.delete_pattern(pattern)
    
    def export_translations(self, language_code: str, format: str = 'json') -> Union[str, bytes]:
        """Export translations for a language."""
        translations = self._translations_cache.get(language_code, {})
        
        if format == 'json':
            return json.dumps(translations, ensure_ascii=False, indent=2)
        elif format == 'csv':
            # Implement CSV export
            pass
        elif format == 'xliff':
            # Implement XLIFF export
            pass
        elif format == 'po':
            # Implement PO export
            pass
        
        raise ValueError(f"Unsupported export format: {format}")
    
    def import_translations(self, language_code: str, data: Union[str, bytes], 
                          format: str = 'json') -> bool:
        """Import translations for a language."""
        try:
            if format == 'json':
                translations = json.loads(data)
            elif format == 'csv':
                # Implement CSV import
                pass
            elif format == 'xliff':
                # Implement XLIFF import
                pass
            elif format == 'po':
                # Implement PO import
                pass
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            # Save to file
            translations_file = os.path.join(
                self.config.LOCALES_DIR,
                f"{language_code}.json"
            )
            
            with open(translations_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            
            # Reload translations
            self.reload_translations(language_code)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to import translations: {e}")
            return False
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation statistics."""
        stats = {
            'languages': {},
            'total_keys': 0,
            'coverage': {}
        }
        
        # Get reference language (English)
        reference_translations = self._translations_cache.get('en', {})
        total_keys = self._count_keys(reference_translations)
        stats['total_keys'] = total_keys
        
        # Calculate coverage for each language
        for language_code in self.config.get_supported_language_codes():
            translations = self._translations_cache.get(language_code, {})
            translated_keys = self._count_keys(translations)
            
            coverage = (translated_keys / total_keys * 100) if total_keys > 0 else 0
            
            stats['languages'][language_code] = {
                'translated_keys': translated_keys,
                'missing_keys': total_keys - translated_keys,
                'coverage': round(coverage, 2)
            }
            
            stats['coverage'][language_code] = round(coverage, 2)
        
        return stats
    
    def _count_keys(self, obj: Dict[str, Any], prefix: str = '') -> int:
        """Count translation keys in nested dictionary."""
        count = 0
        
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                count += self._count_keys(value, full_key)
            else:
                count += 1
        
        return count