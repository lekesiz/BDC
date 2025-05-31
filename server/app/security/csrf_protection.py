"""
CSRF (Cross-Site Request Forgery) protection implementation.
"""

import secrets
import hmac
import hashlib
import time
from typing import Optional, Dict, Any
from flask import Flask, request, session, g, abort, current_app
from functools import wraps

class CSRFProtection:
    """CSRF protection service for Flask applications."""
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize CSRF protection."""
        self.app = app
        self.secret_key = None
        self.token_lifetime = 3600  # 1 hour default
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize CSRF protection for Flask app."""
        self.secret_key = app.config.get('SECRET_KEY')
        self.token_lifetime = app.config.get('CSRF_TOKEN_LIFETIME', 3600)
        
        # Add CSRF protection to all state-changing requests
        app.before_request(self.protect)
        
        # Add CSRF token to template context
        app.jinja_env.globals['csrf_token'] = self.generate_token
    
    def generate_token(self, user_id: Optional[str] = None) -> str:
        """Generate CSRF token for the current session."""
        if not self.secret_key:
            raise ValueError("Secret key not configured")
        
        # Use session ID or user ID as part of token
        session_id = session.get('session_id', session.sid)
        if user_id:
            session_id = f"{session_id}:{user_id}"
        
        # Current timestamp for token expiration
        timestamp = str(int(time.time()))
        
        # Create token data
        token_data = f"{session_id}:{timestamp}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key.encode(),
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine token data and signature
        token = f"{token_data}:{signature}"
        
        # Store in session for validation
        session['csrf_token'] = token
        
        return token
    
    def validate_token(self, token: str, user_id: Optional[str] = None) -> bool:
        """Validate CSRF token."""
        if not token or not self.secret_key:
            return False
        
        try:
            # Split token components
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            session_part, timestamp_part, signature_part = parts
            
            # Reconstruct expected session ID
            session_id = session.get('session_id', session.sid)
            if user_id:
                expected_session = f"{session_id}:{user_id}"
            else:
                expected_session = session_id
            
            # Check session ID match
            if session_part != expected_session:
                return False
            
            # Check token expiration
            timestamp = int(timestamp_part)
            current_time = int(time.time())
            
            if current_time - timestamp > self.token_lifetime:
                return False
            
            # Verify signature
            token_data = f"{session_part}:{timestamp_part}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature_part, expected_signature)
            
        except (ValueError, TypeError):
            return False
    
    def protect(self):
        """CSRF protection middleware."""
        # Skip protection for safe HTTP methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return
        
        # Skip protection for specific endpoints
        exempt_endpoints = current_app.config.get('CSRF_EXEMPT_ENDPOINTS', [])
        if request.endpoint in exempt_endpoints:
            return
        
        # Skip protection for API endpoints with proper authentication
        if self._is_api_request() and self._has_valid_api_auth():
            return
        
        # Get token from various sources
        token = self._get_token_from_request()
        
        if not token:
            self._csrf_error("CSRF token missing")
            return
        
        # Validate token
        user_id = self._get_current_user_id()
        if not self.validate_token(token, user_id):
            self._csrf_error("CSRF token invalid")
            return
    
    def _get_token_from_request(self) -> Optional[str]:
        """Get CSRF token from request headers or form data."""
        # Check X-CSRF-Token header first
        token = request.headers.get('X-CSRF-Token')
        if token:
            return token
        
        # Check X-CSRFToken header (alternative)
        token = request.headers.get('X-CSRFToken')
        if token:
            return token
        
        # Check form data
        if request.form:
            token = request.form.get('csrf_token')
            if token:
                return token
        
        # Check JSON data
        if request.is_json and request.get_json():
            token = request.get_json().get('csrf_token')
            if token:
                return token
        
        return None
    
    def _is_api_request(self) -> bool:
        """Check if request is an API request."""
        # Check if URL starts with /api/
        if request.path.startswith('/api/'):
            return True
        
        # Check Accept header
        accept_header = request.headers.get('Accept', '')
        if 'application/json' in accept_header:
            return True
        
        # Check Content-Type header
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return True
        
        return False
    
    def _has_valid_api_auth(self) -> bool:
        """Check if request has valid API authentication."""
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return False
        
        # Check for Bearer token
        if auth_header.startswith('Bearer '):
            return True
        
        # Check for API key
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return True
        
        return False
    
    def _get_current_user_id(self) -> Optional[str]:
        """Get current user ID from session or context."""
        # Try to get from Flask-Login
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                return str(current_user.id)
        except ImportError:
            pass
        
        # Try to get from session
        return session.get('user_id')
    
    def _csrf_error(self, message: str):
        """Handle CSRF validation error."""
        current_app.logger.warning(f"CSRF protection error: {message}")
        g.csrf_error = message
        abort(403)
    
    def exempt(self, view_func):
        """Decorator to exempt a view from CSRF protection."""
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            g.csrf_exempt = True
            return view_func(*args, **kwargs)
        return wrapper
    
    def get_token_for_user(self, user_id: str) -> str:
        """Generate CSRF token for specific user."""
        return self.generate_token(user_id)
    
    def refresh_token(self) -> str:
        """Refresh CSRF token in current session."""
        user_id = self._get_current_user_id()
        return self.generate_token(user_id)
    
    @staticmethod
    def double_submit_cookie_token() -> str:
        """Generate token for double-submit cookie pattern."""
        return secrets.token_urlsafe(32)
    
    def validate_double_submit_token(self, cookie_token: str, form_token: str) -> bool:
        """Validate double-submit cookie tokens."""
        if not cookie_token or not form_token:
            return False
        
        return hmac.compare_digest(cookie_token, form_token)
    
    def get_signed_token(self, data: str) -> str:
        """Generate signed token with custom data."""
        timestamp = str(int(time.time()))
        token_data = f"{data}:{timestamp}"
        
        signature = hmac.new(
            self.secret_key.encode(),
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{token_data}:{signature}"
    
    def validate_signed_token(self, token: str, expected_data: str) -> bool:
        """Validate signed token with custom data."""
        if not token:
            return False
        
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            data_part, timestamp_part, signature_part = parts
            
            # Verify data matches
            if data_part != expected_data:
                return False
            
            # Check expiration
            timestamp = int(timestamp_part)
            current_time = int(time.time())
            
            if current_time - timestamp > self.token_lifetime:
                return False
            
            # Verify signature
            token_data = f"{data_part}:{timestamp_part}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature_part, expected_signature)
            
        except (ValueError, TypeError):
            return False


def csrf_protect(f):
    """Decorator for explicit CSRF protection on specific routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if hasattr(g, 'csrf_exempt'):
            return f(*args, **kwargs)
        
        csrf = CSRFProtection()
        csrf.protect()
        return f(*args, **kwargs)
    
    return decorated_function