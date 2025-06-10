"""
i18n Configuration
Language and localization settings
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class LanguageConfig:
    """Configuration for a single language."""
    code: str
    name: str
    native_name: str
    direction: str = 'ltr'
    locale: str = None
    flag: str = ''
    date_format: str = 'MM/DD/YYYY'
    currency: str = 'USD'
    number_format: Dict[str, str] = field(default_factory=lambda: {
        'decimal': '.',
        'thousand': ',',
        'precision': '2'
    })
    pluralization_rules: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.locale is None:
            self.locale = f"{self.code}-{self.code.upper()}"

class I18nConfig:
    """Main i18n configuration."""
    
    # Default language
    DEFAULT_LANGUAGE = 'en'
    
    # Translation namespace
    TRANSLATION_NAMESPACE = 'translation'
    
    # Cache settings
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 3600  # 1 hour
    CACHE_KEY_PREFIX = 'i18n'
    
    # File paths
    LOCALES_DIR = os.path.join(os.path.dirname(__file__), '..', 'locales')
    TRANSLATIONS_DIR = os.path.join(LOCALES_DIR, 'translations')
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': LanguageConfig(
            code='en',
            name='English',
            native_name='English',
            direction='ltr',
            locale='en-US',
            flag='🇺🇸',
            date_format='MM/DD/YYYY',
            currency='USD',
            pluralization_rules={'one': 'n == 1', 'other': 'true'}
        ),
        'es': LanguageConfig(
            code='es',
            name='Spanish',
            native_name='Español',
            direction='ltr',
            locale='es-ES',
            flag='🇪🇸',
            date_format='DD/MM/YYYY',
            currency='EUR',
            number_format={'decimal': ',', 'thousand': '.', 'precision': '2'},
            pluralization_rules={'one': 'n == 1', 'other': 'true'}
        ),
        'fr': LanguageConfig(
            code='fr',
            name='French',
            native_name='Français',
            direction='ltr',
            locale='fr-FR',
            flag='🇫🇷',
            date_format='DD/MM/YYYY',
            currency='EUR',
            number_format={'decimal': ',', 'thousand': ' ', 'precision': '2'},
            pluralization_rules={'one': 'n == 0 or n == 1', 'other': 'true'}
        ),
        'tr': LanguageConfig(
            code='tr',
            name='Turkish',
            native_name='Türkçe',
            direction='ltr',
            locale='tr-TR',
            flag='🇹🇷',
            date_format='DD.MM.YYYY',
            currency='TRY',
            number_format={'decimal': ',', 'thousand': '.', 'precision': '2'},
            pluralization_rules={'one': 'n == 1', 'other': 'true'}
        ),
        'ar': LanguageConfig(
            code='ar',
            name='Arabic',
            native_name='العربية',
            direction='rtl',
            locale='ar-SA',
            flag='🇸🇦',
            date_format='DD/MM/YYYY',
            currency='SAR',
            pluralization_rules={
                'zero': 'n == 0',
                'one': 'n == 1',
                'two': 'n == 2',
                'few': 'n % 100 >= 3 and n % 100 <= 10',
                'many': 'n % 100 >= 11',
                'other': 'true'
            }
        ),
        'he': LanguageConfig(
            code='he',
            name='Hebrew',
            native_name='עברית',
            direction='rtl',
            locale='he-IL',
            flag='🇮🇱',
            date_format='DD/MM/YYYY',
            currency='ILS',
            pluralization_rules={
                'one': 'n == 1',
                'two': 'n == 2',
                'many': 'n > 10 and n % 10 == 0',
                'other': 'true'
            }
        ),
        'de': LanguageConfig(
            code='de',
            name='German',
            native_name='Deutsch',
            direction='ltr',
            locale='de-DE',
            flag='🇩🇪',
            date_format='DD.MM.YYYY',
            currency='EUR',
            number_format={'decimal': ',', 'thousand': '.', 'precision': '2'},
            pluralization_rules={'one': 'n == 1', 'other': 'true'}
        ),
        'ru': LanguageConfig(
            code='ru',
            name='Russian',
            native_name='Русский',
            direction='ltr',
            locale='ru-RU',
            flag='🇷🇺',
            date_format='DD.MM.YYYY',
            currency='RUB',
            number_format={'decimal': ',', 'thousand': ' ', 'precision': '2'},
            pluralization_rules={
                'one': 'n % 10 == 1 and n % 100 != 11',
                'few': 'n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20)',
                'many': 'n % 10 == 0 or (n % 10 >= 5 and n % 10 <= 9) or (n % 100 >= 11 and n % 100 <= 14)',
                'other': 'true'
            }
        ),
        'zh': LanguageConfig(
            code='zh',
            name='Chinese',
            native_name='中文',
            direction='ltr',
            locale='zh-CN',
            flag='🇨🇳',
            date_format='YYYY/MM/DD',
            currency='CNY',
            pluralization_rules={'other': 'true'}
        ),
        'ja': LanguageConfig(
            code='ja',
            name='Japanese',
            native_name='日本語',
            direction='ltr',
            locale='ja-JP',
            flag='🇯🇵',
            date_format='YYYY/MM/DD',
            currency='JPY',
            number_format={'decimal': '.', 'thousand': ',', 'precision': '0'},
            pluralization_rules={'other': 'true'}
        )
    }
    
    # RTL languages
    RTL_LANGUAGES = ['ar', 'he']
    
    # Language detection settings
    LANGUAGE_DETECTION_ORDER = [
        'user_preference',
        'session',
        'cookie',
        'accept_language',
        'default'
    ]
    
    # Cookie settings
    LANGUAGE_COOKIE_NAME = 'bdc_language'
    LANGUAGE_COOKIE_HTTPONLY = False
    LANGUAGE_COOKIE_SECURE = True
    LANGUAGE_COOKIE_SAMESITE = 'Lax'
    LANGUAGE_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year
    
    # Session settings
    LANGUAGE_SESSION_KEY = 'language'
    
    # Translation settings
    TRANSLATION_MISSING_KEY_PREFIX = '[MISSING]'
    TRANSLATION_ERROR_PREFIX = '[ERROR]'
    TRANSLATION_FALLBACK_ENABLED = True
    
    # Content translation settings
    CONTENT_TRANSLATION_CACHE_ENABLED = True
    CONTENT_TRANSLATION_CACHE_TIMEOUT = 3600
    
    # Locale settings
    LOCALE_FORMATS = {
        'date': {
            'short': '%d/%m/%Y',
            'medium': '%d %b %Y',
            'long': '%d %B %Y',
            'full': '%A, %d %B %Y'
        },
        'time': {
            'short': '%H:%M',
            'medium': '%H:%M:%S',
            'long': '%H:%M:%S %Z',
            'full': '%H:%M:%S %z'
        },
        'datetime': {
            'short': '%d/%m/%Y %H:%M',
            'medium': '%d %b %Y %H:%M',
            'long': '%d %B %Y %H:%M:%S',
            'full': '%A, %d %B %Y %H:%M:%S %z'
        }
    }
    
    # Number formatting
    NUMBER_FORMATS = {
        'decimal': 'decimal',
        'currency': 'currency',
        'percent': 'percent',
        'scientific': 'scientific'
    }
    
    # Translation key patterns
    TRANSLATION_KEY_PATTERN = r'^[a-zA-Z0-9_.]+$'
    
    # Auto-translation settings
    AUTO_TRANSLATION_ENABLED = False
    AUTO_TRANSLATION_SERVICE = 'google'  # google, deepl, azure
    AUTO_TRANSLATION_API_KEY = os.getenv('TRANSLATION_API_KEY')
    
    # Import/Export settings
    IMPORT_EXPORT_FORMATS = ['json', 'csv', 'xliff', 'po']
    
    @classmethod
    def get_language_config(cls, language_code: str) -> Optional[LanguageConfig]:
        """Get configuration for a specific language."""
        return cls.SUPPORTED_LANGUAGES.get(language_code)
    
    @classmethod
    def get_supported_language_codes(cls) -> List[str]:
        """Get list of supported language codes."""
        return list(cls.SUPPORTED_LANGUAGES.keys())
    
    @classmethod
    def is_rtl_language(cls, language_code: str) -> bool:
        """Check if a language is RTL."""
        return language_code in cls.RTL_LANGUAGES
    
    @classmethod
    def get_default_language_config(cls) -> LanguageConfig:
        """Get default language configuration."""
        return cls.SUPPORTED_LANGUAGES[cls.DEFAULT_LANGUAGE]