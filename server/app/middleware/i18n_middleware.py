"""Internationalization middleware for automatic language detection and content localization."""

import logging
from flask import request, g, current_app, session
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from werkzeug.exceptions import BadRequest

from app.models.user import User
from app.models.i18n import UserLanguagePreference
from app.services.i18n import LanguageDetectionService
from app.extensions import db

logger = logging.getLogger(__name__)


class I18nMiddleware:
    """Middleware for handling internationalization."""
    
    def __init__(self, app=None):
        """Initialize i18n middleware."""
        self.app = app
        self.language_service = LanguageDetectionService()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Add template globals for i18n
        app.jinja_env.globals.update(
            get_user_language=self.get_user_language,
            is_rtl_language=self.language_service.is_rtl_language,
            get_language_info=self.language_service.get_language_info
        )
    
    def before_request(self):
        """Process request before route handler."""
        try:
            # Skip i18n processing for certain routes
            if self._should_skip_i18n():
                return
            
            # Detect and set user language
            language = self._detect_user_language()
            g.user_language = language
            g.language_info = self.language_service.get_language_info(language)
            
            # Set RTL direction flag
            g.is_rtl = self.language_service.is_rtl_language(language)
            
            # Store language in session for consistency
            session['user_language'] = language
            
            # Log language detection for debugging
            logger.debug(f"Detected language: {language} for IP: {request.remote_addr}")
            
        except Exception as e:
            logger.error(f"Error in i18n middleware before_request: {e}")
            # Fallback to default language
            g.user_language = self.language_service.DEFAULT_LANGUAGE
            g.language_info = self.language_service.get_language_info(g.user_language)
            g.is_rtl = False
    
    def after_request(self, response):
        """Process response after route handler."""
        try:
            # Add language information to response headers
            if hasattr(g, 'user_language'):
                response.headers['Content-Language'] = g.user_language
                response.headers['X-User-Language'] = g.user_language
                
                if hasattr(g, 'is_rtl') and g.is_rtl:
                    response.headers['X-Text-Direction'] = 'rtl'
                else:
                    response.headers['X-Text-Direction'] = 'ltr'
            
            # Add CORS headers for i18n data
            if request.method == 'OPTIONS':
                response.headers['Access-Control-Allow-Headers'] += ', Accept-Language, Content-Language'
            
            return response
            
        except Exception as e:
            logger.error(f"Error in i18n middleware after_request: {e}")
            return response
    
    def _should_skip_i18n(self):
        """Check if i18n processing should be skipped for this request."""
        # Skip for static files
        if request.endpoint == 'static':
            return True
        
        # Skip for health checks
        if request.path in ['/health', '/api/health']:
            return True
        
        # Skip for API documentation
        if request.path.startswith('/api/docs'):
            return True
        
        # Skip for websocket connections
        if request.path.startswith('/socket.io'):
            return True
        
        return False
    
    def _detect_user_language(self):
        """Detect the best language for the current user."""
        try:
            # 1. Check for explicit language parameter in request
            explicit_language = self._get_explicit_language()
            if explicit_language:
                return explicit_language
            
            # 2. Check user preferences (for authenticated users)
            user_preference = self._get_user_preference_language()
            if user_preference:
                return user_preference
            
            # 3. Check session language
            session_language = session.get('user_language')
            if session_language and session_language in self.language_service.SUPPORTED_LANGUAGES:
                return session_language
            
            # 4. Browser language detection
            browser_language = self._get_browser_language()
            if browser_language:
                return browser_language
            
            # 5. Geolocation-based detection (if available)
            geo_language = self._get_geolocation_language()
            if geo_language:
                return geo_language
            
            # 6. Fallback to default
            return self.language_service.DEFAULT_LANGUAGE
            
        except Exception as e:
            logger.error(f"Error detecting user language: {e}")
            return self.language_service.DEFAULT_LANGUAGE
    
    def _get_explicit_language(self):
        """Get explicitly requested language from request parameters."""
        try:
            # Check query parameters
            lang_param = request.args.get('lang') or request.args.get('language')
            if lang_param:
                normalized = self.language_service.normalize_language_code(lang_param)
                if normalized in self.language_service.SUPPORTED_LANGUAGES:
                    return normalized
            
            # Check form data
            if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
                json_data = request.get_json(silent=True)
                if json_data and 'language' in json_data:
                    lang_param = json_data['language']
                    normalized = self.language_service.normalize_language_code(lang_param)
                    if normalized in self.language_service.SUPPORTED_LANGUAGES:
                        return normalized
            
            # Check custom headers
            lang_header = request.headers.get('X-Language') or request.headers.get('X-User-Language')
            if lang_header:
                normalized = self.language_service.normalize_language_code(lang_header)
                if normalized in self.language_service.SUPPORTED_LANGUAGES:
                    return normalized
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting explicit language: {e}")
            return None
    
    def _get_user_preference_language(self):
        """Get language from authenticated user's preferences."""
        try:
            # Check if user is authenticated
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                if not user_id:
                    return None
            except:
                return None
            
            # Get user preferences
            preferences = UserLanguagePreference.query.filter_by(user_id=user_id).first()
            if preferences and preferences.enable_auto_detection:
                return self.language_service.normalize_language_code(preferences.primary_language)
            
            # Fallback to user.language field
            user = User.query.get(user_id)
            if user and user.language:
                return self.language_service.normalize_language_code(user.language)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user preference language: {e}")
            return None
    
    def _get_browser_language(self):
        """Get language from browser Accept-Language header."""
        try:
            accept_language = request.headers.get('Accept-Language')
            if not accept_language:
                return None
            
            result = self.language_service.detect_from_browser(accept_language)
            return result.language if result else None
            
        except Exception as e:
            logger.error(f"Error getting browser language: {e}")
            return None
    
    def _get_geolocation_language(self):
        """Get language based on geolocation (if available)."""
        try:
            # Check for country code in various headers
            country_code = (
                request.headers.get('CF-IPCountry') or  # Cloudflare
                request.headers.get('X-Country-Code') or  # Custom header
                request.headers.get('X-Forwarded-Country')  # Custom header
            )
            
            if country_code:
                result = self.language_service.detect_from_geolocation(country_code)
                return result.language if result else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting geolocation language: {e}")
            return None
    
    def get_user_language(self):
        """Get the current user's language (for use in templates)."""
        return getattr(g, 'user_language', self.language_service.DEFAULT_LANGUAGE)
    
    def get_fallback_language(self, language=None):
        """Get fallback language for a given language."""
        if not language:
            language = self.get_user_language()
        return self.language_service.get_fallback_language(language)


class ContentLocalizationMiddleware:
    """Middleware for automatic content localization."""
    
    def __init__(self, app=None):
        """Initialize content localization middleware."""
        self.app = app
        self.language_service = LanguageDetectionService()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        app.after_request(self.localize_response_content)
    
    def localize_response_content(self, response):
        """Localize response content if applicable."""
        try:
            # Only process JSON responses
            if not response.is_json or not hasattr(g, 'user_language'):
                return response
            
            # Skip if not a successful response
            if response.status_code >= 400:
                return response
            
            # Get response data
            try:
                data = response.get_json()
            except:
                return response
            
            # Localize the data
            localized_data = self._localize_data(data, g.user_language)
            
            # Update response with localized data
            if localized_data != data:
                response.data = current_app.json.dumps(localized_data)
                response.headers['Content-Length'] = len(response.data)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in content localization middleware: {e}")
            return response
    
    def _localize_data(self, data, language):
        """Recursively localize data structure."""
        try:
            if isinstance(data, dict):
                # Check for translatable fields
                localized = {}
                for key, value in data.items():
                    if self._is_translatable_field(key):
                        localized[key] = self._translate_field(value, language)
                    elif isinstance(value, (dict, list)):
                        localized[key] = self._localize_data(value, language)
                    else:
                        localized[key] = value
                return localized
            
            elif isinstance(data, list):
                return [self._localize_data(item, language) for item in data]
            
            else:
                return data
                
        except Exception as e:
            logger.error(f"Error localizing data: {e}")
            return data
    
    def _is_translatable_field(self, field_name):
        """Check if a field should be translated."""
        translatable_fields = {
            'title', 'name', 'description', 'content', 'message', 
            'text', 'label', 'placeholder', 'tooltip', 'error_message',
            'success_message', 'warning_message', 'info_message'
        }
        return field_name.lower() in translatable_fields
    
    def _translate_field(self, value, language):
        """Translate a field value."""
        try:
            if not isinstance(value, str) or len(value.strip()) == 0:
                return value
            
            # For now, return original value
            # In a full implementation, this would use the translation service
            # to translate the content or look up multilingual content
            return value
            
        except Exception as e:
            logger.error(f"Error translating field: {e}")
            return value


class RTLSupportMiddleware:
    """Middleware for Right-to-Left (RTL) language support."""
    
    def __init__(self, app=None):
        """Initialize RTL support middleware."""
        self.app = app
        self.language_service = LanguageDetectionService()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        app.after_request(self.add_rtl_support)
    
    def add_rtl_support(self, response):
        """Add RTL support to response."""
        try:
            # Only process HTML responses
            if not response.content_type.startswith('text/html'):
                return response
            
            # Check if current language is RTL
            if not hasattr(g, 'is_rtl') or not g.is_rtl:
                return response
            
            # Add RTL class to HTML
            content = response.get_data(as_text=True)
            
            # Add dir="rtl" to html tag
            if '<html' in content and 'dir=' not in content:
                content = content.replace('<html', '<html dir="rtl"', 1)
            
            # Add RTL class to body
            if '<body' in content and 'rtl' not in content:
                if 'class="' in content:
                    content = content.replace('class="', 'class="rtl ', 1)
                else:
                    content = content.replace('<body', '<body class="rtl"', 1)
            
            # Update response
            response.set_data(content)
            response.headers['Content-Length'] = len(response.get_data())
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RTL support middleware: {e}")
            return response


# Initialize middleware instances
i18n_middleware = I18nMiddleware()
content_localization_middleware = ContentLocalizationMiddleware()
rtl_support_middleware = RTLSupportMiddleware()