"""
Language Detector
Detects user's preferred language from various sources
"""

import re
import logging
from typing import Optional, List, Tuple
from flask import Request, session

from .config import I18nConfig
from app.models.user import User
from app.models.i18n import UserLanguagePreference

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Detects user's preferred language."""
    
    def __init__(self):
        """Initialize language detector."""
        self.config = I18nConfig()
        self._supported_languages = set(self.config.get_supported_language_codes())
    
    def detect(self, request: Request, user_id: Optional[int] = None) -> str:
        """
        Detect language from various sources in order of preference.
        
        Args:
            request: Flask request object
            user_id: Optional user ID for authenticated users
            
        Returns:
            Detected language code
        """
        for method in self.config.LANGUAGE_DETECTION_ORDER:
            language = None
            
            if method == 'user_preference' and user_id:
                language = self._detect_from_user_preference(user_id)
            elif method == 'session':
                language = self._detect_from_session()
            elif method == 'cookie':
                language = self._detect_from_cookie(request)
            elif method == 'accept_language':
                language = self._detect_from_accept_language(request)
            elif method == 'default':
                language = self.config.DEFAULT_LANGUAGE
            
            if language and language in self._supported_languages:
                return language
        
        return self.config.DEFAULT_LANGUAGE
    
    def _detect_from_user_preference(self, user_id: int) -> Optional[str]:
        """Detect language from user's saved preference."""
        try:
            # Check user language preference
            preference = UserLanguagePreference.query.filter_by(
                user_id=user_id
            ).first()
            
            if preference and preference.primary_language:
                return preference.primary_language
            
            # Check user model if it has language field
            user = User.query.get(user_id)
            if user and hasattr(user, 'language') and user.language:
                return user.language
                
        except Exception as e:
            logger.error(f"Error detecting language from user preference: {e}")
        
        return None
    
    def _detect_from_session(self) -> Optional[str]:
        """Detect language from session."""
        try:
            return session.get(self.config.LANGUAGE_SESSION_KEY)
        except Exception as e:
            logger.error(f"Error detecting language from session: {e}")
            return None
    
    def _detect_from_cookie(self, request: Request) -> Optional[str]:
        """Detect language from cookie."""
        try:
            return request.cookies.get(self.config.LANGUAGE_COOKIE_NAME)
        except Exception as e:
            logger.error(f"Error detecting language from cookie: {e}")
            return None
    
    def _detect_from_accept_language(self, request: Request) -> Optional[str]:
        """Detect language from Accept-Language header."""
        try:
            accept_language = request.headers.get('Accept-Language', '')
            if not accept_language:
                return None
            
            # Parse Accept-Language header
            languages = self._parse_accept_language(accept_language)
            
            # Find first supported language
            for lang, _ in languages:
                # Try exact match
                if lang in self._supported_languages:
                    return lang
                
                # Try language part only (e.g., 'en' from 'en-US')
                lang_part = lang.split('-')[0]
                if lang_part in self._supported_languages:
                    return lang_part
                
                # Try to find a language with the same prefix
                for supported in self._supported_languages:
                    if supported.startswith(lang_part + '-') or lang.startswith(supported + '-'):
                        return supported
            
        except Exception as e:
            logger.error(f"Error detecting language from Accept-Language: {e}")
        
        return None
    
    def _parse_accept_language(self, accept_language: str) -> List[Tuple[str, float]]:
        """
        Parse Accept-Language header value.
        
        Args:
            accept_language: Accept-Language header value
            
        Returns:
            List of (language, quality) tuples sorted by quality
        """
        languages = []
        
        # Split by comma
        for item in accept_language.split(','):
            item = item.strip()
            if not item:
                continue
            
            # Check for quality value
            if ';' in item:
                lang, q = item.split(';', 1)
                lang = lang.strip()
                
                # Parse quality value
                match = re.match(r'q\s*=\s*(\d*\.?\d+)', q)
                if match:
                    quality = float(match.group(1))
                else:
                    quality = 1.0
            else:
                lang = item
                quality = 1.0
            
            # Normalize language code
            lang = lang.lower().replace('_', '-')
            
            languages.append((lang, quality))
        
        # Sort by quality (descending)
        languages.sort(key=lambda x: x[1], reverse=True)
        
        return languages
    
    def detect_from_content(self, text: str) -> Optional[str]:
        """
        Detect language from text content.
        
        This is a simplified version - in production, you might want to use
        a library like langdetect or textblob.
        """
        if not text or len(text) < 20:
            return None
        
        # Simple heuristics based on character sets
        # Arabic
        if re.search(r'[\u0600-\u06FF]', text):
            return 'ar'
        
        # Hebrew
        if re.search(r'[\u0590-\u05FF]', text):
            return 'he'
        
        # Chinese
        if re.search(r'[\u4E00-\u9FFF]', text):
            return 'zh'
        
        # Japanese (Hiragana or Katakana)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return 'ja'
        
        # Cyrillic (Russian)
        if re.search(r'[\u0400-\u04FF]', text):
            return 'ru'
        
        # Turkish specific characters
        if re.search(r'[ğĞıİöÖşŞüÜçÇ]', text):
            return 'tr'
        
        # German specific characters
        if re.search(r'[äÄöÖüÜßẞ]', text):
            return 'de'
        
        # French specific patterns
        if re.search(r'[àâæçéèêëîïôùûüÿœ]', text):
            return 'fr'
        
        # Spanish specific patterns
        if re.search(r'[áéíóúüñ¿¡]', text):
            return 'es'
        
        # Default to English
        return 'en'
    
    def get_browser_languages(self, request: Request) -> List[str]:
        """Get list of languages accepted by the browser."""
        accept_language = request.headers.get('Accept-Language', '')
        languages = self._parse_accept_language(accept_language)
        
        # Return only the language codes
        return [lang for lang, _ in languages]
    
    def negotiate_language(self, available_languages: List[str],
                         preferred_languages: List[str]) -> Optional[str]:
        """
        Negotiate best language from available options.
        
        Args:
            available_languages: List of available language codes
            preferred_languages: List of preferred language codes in order
            
        Returns:
            Best matching language code or None
        """
        available_set = set(available_languages)
        
        for preferred in preferred_languages:
            # Exact match
            if preferred in available_set:
                return preferred
            
            # Try language part only
            lang_part = preferred.split('-')[0]
            if lang_part in available_set:
                return lang_part
            
            # Try to find variant
            for available in available_languages:
                if available.startswith(lang_part + '-'):
                    return available
        
        return None