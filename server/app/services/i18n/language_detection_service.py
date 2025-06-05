"""Language detection service for multi-language support."""

import re
import logging
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from app.utils.cache import cache_manager

logger = logging.getLogger(__name__)


@dataclass
class LanguageDetectionResult:
    """Language detection result."""
    language: str
    confidence: float
    source: str  # 'browser', 'user_preference', 'content', 'geolocation'


class LanguageDetectionService:
    """Service for detecting user's preferred language."""
    
    # Supported languages with their metadata
    SUPPORTED_LANGUAGES = {
        'en': {
            'name': 'English',
            'native_name': 'English',
            'direction': 'ltr',
            'region': 'en-US',
            'fallback': None
        },
        'tr': {
            'name': 'Turkish',
            'native_name': 'Türkçe',
            'direction': 'ltr',
            'region': 'tr-TR',
            'fallback': 'en'
        },
        'ar': {
            'name': 'Arabic',
            'native_name': 'العربية',
            'direction': 'rtl',
            'region': 'ar-SA',
            'fallback': 'en'
        },
        'es': {
            'name': 'Spanish',
            'native_name': 'Español',
            'direction': 'ltr',
            'region': 'es-ES',
            'fallback': 'en'
        },
        'fr': {
            'name': 'French',
            'native_name': 'Français',
            'direction': 'ltr',
            'region': 'fr-FR',
            'fallback': 'en'
        },
        'de': {
            'name': 'German',
            'native_name': 'Deutsch',
            'direction': 'ltr',
            'region': 'de-DE',
            'fallback': 'en'
        },
        'ru': {
            'name': 'Russian',
            'native_name': 'Русский',
            'direction': 'ltr',
            'region': 'ru-RU',
            'fallback': 'en'
        }
    }
    
    # RTL languages
    RTL_LANGUAGES = {'ar'}
    
    # Default language
    DEFAULT_LANGUAGE = 'en'
    
    # Language patterns for content detection
    LANGUAGE_PATTERNS = {
        'ar': [
            r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
            r'(والله|الحمد|أللهم|السلام|مرحبا|شكرا)'
        ],
        'tr': [
            r'[çğıöşüÇĞIİÖŞÜ]',
            r'(merhaba|teşekkürler|günaydın|iyi|nasıl|nerede)'
        ],
        'es': [
            r'[ñáéíóúüÑÁÉÍÓÚÜ]',
            r'(hola|gracias|buenos|como|donde|que|por)'
        ],
        'fr': [
            r'[àâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]',
            r'(bonjour|merci|comment|ou|que|pour|avec)'
        ],
        'de': [
            r'[äöüßÄÖÜ]',
            r'(hallo|danke|guten|wie|wo|was|für|mit)'
        ],
        'ru': [
            r'[а-яё]',
            r'(привет|спасибо|доброе|как|где|что|для)'
        ]
    }
    
    def __init__(self):
        """Initialize language detection service."""
        self.cache_timeout = 3600  # 1 hour
    
    def detect_from_browser(self, accept_language_header: str) -> Optional[LanguageDetectionResult]:
        """
        Detect language from browser Accept-Language header.
        
        Args:
            accept_language_header: Browser's Accept-Language header
            
        Returns:
            Language detection result or None
        """
        try:
            if not accept_language_header:
                return None
            
            # Parse Accept-Language header: "en-US,en;q=0.9,tr;q=0.8"
            languages = []
            for lang_item in accept_language_header.split(','):
                parts = lang_item.strip().split(';')
                language = parts[0].strip().lower()
                
                # Extract quality value
                quality = 1.0
                if len(parts) > 1:
                    q_part = parts[1].strip()
                    if q_part.startswith('q='):
                        try:
                            quality = float(q_part[2:])
                        except ValueError:
                            quality = 1.0
                
                # Normalize language code
                if '-' in language:
                    language = language.split('-')[0]
                
                if language in self.SUPPORTED_LANGUAGES:
                    languages.append((language, quality))
            
            # Sort by quality and return highest supported language
            if languages:
                languages.sort(key=lambda x: x[1], reverse=True)
                best_language, confidence = languages[0]
                
                return LanguageDetectionResult(
                    language=best_language,
                    confidence=confidence,
                    source='browser'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting language from browser header: {e}")
            return None
    
    def detect_from_content(self, text: str) -> Optional[LanguageDetectionResult]:
        """
        Detect language from text content using pattern matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language detection result or None
        """
        try:
            if not text or len(text.strip()) < 10:
                return None
            
            text = text.lower()
            scores = {}
            
            # Score each language based on pattern matches
            for lang, patterns in self.LANGUAGE_PATTERNS.items():
                score = 0
                
                for pattern in patterns:
                    matches = len(re.findall(pattern, text, re.IGNORECASE))
                    score += matches
                
                if score > 0:
                    scores[lang] = score / len(text) * 100  # Normalize by text length
            
            # Return language with highest score if above threshold
            if scores:
                best_language = max(scores, key=scores.get)
                confidence = min(scores[best_language], 1.0)  # Cap at 1.0
                
                if confidence > 0.01:  # Minimum confidence threshold
                    return LanguageDetectionResult(
                        language=best_language,
                        confidence=confidence,
                        source='content'
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting language from content: {e}")
            return None
    
    def detect_from_geolocation(self, country_code: str) -> Optional[LanguageDetectionResult]:
        """
        Detect language from country code.
        
        Args:
            country_code: ISO country code (e.g., 'US', 'TR', 'SA')
            
        Returns:
            Language detection result or None
        """
        try:
            # Country to language mapping
            country_language_map = {
                'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en', 'NZ': 'en',
                'TR': 'tr',
                'SA': 'ar', 'AE': 'ar', 'EG': 'ar', 'JO': 'ar', 'LB': 'ar',
                'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es', 'PE': 'es',
                'FR': 'fr', 'BE': 'fr', 'CH': 'fr', 'CA': 'fr',
                'DE': 'de', 'AT': 'de', 'CH': 'de',
                'RU': 'ru', 'BY': 'ru', 'KZ': 'ru'
            }
            
            country_code = country_code.upper()
            if country_code in country_language_map:
                language = country_language_map[country_code]
                
                return LanguageDetectionResult(
                    language=language,
                    confidence=0.7,  # Medium confidence for geolocation
                    source='geolocation'
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting language from geolocation: {e}")
            return None
    
    def detect_best_language(self, 
                           user_preference: Optional[str] = None,
                           accept_language: Optional[str] = None,
                           content: Optional[str] = None,
                           country_code: Optional[str] = None) -> str:
        """
        Detect the best language for a user using multiple sources.
        
        Args:
            user_preference: User's saved language preference
            accept_language: Browser's Accept-Language header
            content: Content to analyze
            country_code: User's country code
            
        Returns:
            Best detected language code
        """
        try:
            # Priority order: user preference > browser > content > geolocation > default
            
            # 1. User preference (highest priority)
            if user_preference and user_preference in self.SUPPORTED_LANGUAGES:
                return user_preference
            
            # 2. Browser detection
            if accept_language:
                browser_result = self.detect_from_browser(accept_language)
                if browser_result and browser_result.confidence > 0.8:
                    return browser_result.language
            
            # 3. Content detection
            if content:
                content_result = self.detect_from_content(content)
                if content_result and content_result.confidence > 0.05:
                    return content_result.language
            
            # 4. Geolocation detection
            if country_code:
                geo_result = self.detect_from_geolocation(country_code)
                if geo_result:
                    return geo_result.language
            
            # 5. Fall back to browser with lower confidence
            if accept_language:
                browser_result = self.detect_from_browser(accept_language)
                if browser_result:
                    return browser_result.language
            
            # 6. Default language
            return self.DEFAULT_LANGUAGE
            
        except Exception as e:
            logger.error(f"Error in detect_best_language: {e}")
            return self.DEFAULT_LANGUAGE
    
    def get_language_info(self, language_code: str) -> Dict:
        """
        Get comprehensive information about a language.
        
        Args:
            language_code: Language code
            
        Returns:
            Language information dictionary
        """
        if language_code not in self.SUPPORTED_LANGUAGES:
            language_code = self.DEFAULT_LANGUAGE
        
        info = self.SUPPORTED_LANGUAGES[language_code].copy()
        info['code'] = language_code
        info['is_rtl'] = language_code in self.RTL_LANGUAGES
        
        return info
    
    def get_supported_languages(self) -> List[Dict]:
        """
        Get list of all supported languages.
        
        Returns:
            List of language information dictionaries
        """
        return [
            {
                'code': code,
                'name': info['name'],
                'native_name': info['native_name'],
                'direction': info['direction'],
                'region': info['region'],
                'is_rtl': code in self.RTL_LANGUAGES
            }
            for code, info in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def get_fallback_language(self, language_code: str) -> str:
        """
        Get fallback language for a given language.
        
        Args:
            language_code: Language code
            
        Returns:
            Fallback language code
        """
        if language_code in self.SUPPORTED_LANGUAGES:
            fallback = self.SUPPORTED_LANGUAGES[language_code]['fallback']
            return fallback if fallback else self.DEFAULT_LANGUAGE
        
        return self.DEFAULT_LANGUAGE
    
    @cache_manager.memoize(timeout=3600)
    def is_rtl_language(self, language_code: str) -> bool:
        """
        Check if a language is right-to-left.
        
        Args:
            language_code: Language code
            
        Returns:
            True if RTL, False otherwise
        """
        return language_code in self.RTL_LANGUAGES
    
    def normalize_language_code(self, language_code: str) -> str:
        """
        Normalize language code to supported format.
        
        Args:
            language_code: Raw language code
            
        Returns:
            Normalized language code
        """
        if not language_code:
            return self.DEFAULT_LANGUAGE
        
        # Handle locale codes like 'en-US', 'tr-TR'
        base_code = language_code.lower().split('-')[0].split('_')[0]
        
        if base_code in self.SUPPORTED_LANGUAGES:
            return base_code
        
        return self.DEFAULT_LANGUAGE