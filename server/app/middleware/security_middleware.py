"""Security middleware for production deployment."""

import os
import time
import hashlib
from flask import request, g, current_app, abort, make_response
from functools import wraps
from collections import defaultdict, deque
import redis


class SecurityMiddleware:
    """Comprehensive security middleware for production."""
    
    def __init__(self, app=None, redis_client=None):
        self.app = app
        self.redis_client = redis_client
        self.failed_attempts = defaultdict(lambda: deque(maxlen=10))
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app."""
        self.app = app
        
        # Configure Redis for rate limiting if not provided
        if not self.redis_client:
            try:
                self.redis_client = redis.Redis.from_url(
                    app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                )
            except Exception:
                app.logger.warning("Redis not available for security middleware")
        
        # Register middleware
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Execute security checks before each request."""
        # Skip security checks for health endpoints
        if request.endpoint in ['health.health', 'health.ready']:
            return
        
        # Check trusted hosts
        if not self._check_trusted_host():
            abort(400, "Untrusted host")
        
        # Force HTTPS in production
        if self._should_force_https():
            if not request.is_secure and not self._is_local_request():
                return self._redirect_to_https()
        
        # Rate limiting
        if self._is_rate_limited():
            abort(429, "Rate limit exceeded")
        
        # Check for suspicious requests
        if self._is_suspicious_request():
            abort(400, "Suspicious request detected")
        
        # Store request start time for monitoring
        g.start_time = time.time()
    
    def after_request(self, response):
        """Execute security enhancements after each request."""
        # Add security headers
        self._add_security_headers(response)
        
        # Log slow requests
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            if duration > 5.0:  # Log requests taking more than 5 seconds
                current_app.logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration:.2f}s"
                )
        
        return response
    
    def _check_trusted_host(self):
        """Verify request comes from trusted host."""
        if not current_app.config.get('TRUSTED_HOSTS'):
            return True
        
        host = request.headers.get('Host', '').split(':')[0]
        trusted_hosts = current_app.config.get('TRUSTED_HOSTS', [])
        
        # Allow localhost and 127.0.0.1 in development
        if current_app.debug:
            trusted_hosts.extend(['localhost', '127.0.0.1'])
        
        return host in trusted_hosts
    
    def _should_force_https(self):
        """Check if HTTPS should be enforced."""
        return current_app.config.get('FORCE_HTTPS', False)
    
    def _is_local_request(self):
        """Check if request is from localhost."""
        remote_addr = request.environ.get('REMOTE_ADDR', '')
        return remote_addr in ['127.0.0.1', '::1'] or remote_addr.startswith('192.168.')
    
    def _redirect_to_https(self):
        """Redirect HTTP request to HTTPS."""
        url = request.url.replace('http://', 'https://', 1)
        return f'<script>window.location.href="{url}";</script>', 301
    
    def _is_rate_limited(self):
        """Check if request should be rate limited."""
        if not self.redis_client:
            return False
        
        # Get client identifier
        client_id = self._get_client_identifier()
        
        # Define rate limits based on endpoint
        rate_limits = {
            'auth.login': (5, 300),      # 5 attempts per 5 minutes
            'auth.register': (3, 3600),   # 3 attempts per hour
            'auth.reset_password': (3, 3600),  # 3 attempts per hour
            'default': (100, 60)          # 100 requests per minute
        }
        
        endpoint = request.endpoint or 'default'
        limit, window = rate_limits.get(endpoint, rate_limits['default'])
        
        # Check rate limit
        key = f"rate_limit:{endpoint}:{client_id}"
        
        try:
            current_count = self.redis_client.get(key)
            if current_count is None:
                self.redis_client.setex(key, window, 1)
                return False
            
            if int(current_count) >= limit:
                return True
            
            self.redis_client.incr(key)
            return False
            
        except Exception as e:
            current_app.logger.error(f"Rate limiting error: {e}")
            return False
    
    def _is_suspicious_request(self):
        """Detect potentially suspicious requests."""
        # Check for common attack patterns
        suspicious_patterns = [
            'script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            '../', '..\\', '/etc/passwd', '/proc/', 'cmd.exe', 'powershell'
        ]
        
        # Check URL and query parameters
        full_path = request.full_path.lower()
        for pattern in suspicious_patterns:
            if pattern in full_path:
                current_app.logger.warning(
                    f"Suspicious request detected: {request.remote_addr} - {request.full_path}"
                )
                return True
        
        # Check request headers for suspicious content
        for header, value in request.headers:
            if any(pattern in value.lower() for pattern in suspicious_patterns):
                current_app.logger.warning(
                    f"Suspicious header detected: {request.remote_addr} - {header}: {value}"
                )
                return True
        
        # Check for unusually large requests
        if request.content_length and request.content_length > 50 * 1024 * 1024:  # 50MB
            return True
        
        return False
    
    def _get_client_identifier(self):
        """Get unique identifier for rate limiting."""
        # Try to get real IP from headers (for proxy/load balancer scenarios)
        real_ip = (
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            request.headers.get('X-Real-IP', '') or
            request.remote_addr
        )
        
        # Create hash to anonymize IP while maintaining uniqueness
        return hashlib.sha256(f"{real_ip}:{request.user_agent.string}".encode()).hexdigest()[:16]
    
    def _add_security_headers(self, response):
        """Add security headers to response."""
        # Content Security Policy
        if current_app.config.get('CONTENT_SECURITY_POLICY'):
            response.headers['Content-Security-Policy'] = current_app.config['CONTENT_SECURITY_POLICY']
        
        # X-Frame-Options
        response.headers['X-Frame-Options'] = current_app.config.get('X_FRAME_OPTIONS', 'DENY')
        
        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = current_app.config.get('X_CONTENT_TYPE_OPTIONS', 'nosniff')
        
        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = current_app.config.get('REFERRER_POLICY', 'strict-origin-when-cross-origin')
        
        # Strict Transport Security (HSTS)
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Additional security headers
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        response.headers['X-Download-Options'] = 'noopen'
        response.headers['X-DNS-Prefetch-Control'] = 'off'
        
        return response


def require_api_key(f):
    """Decorator to require API key for certain endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = current_app.config.get('API_KEY')
        
        if not api_key or not expected_key or api_key != expected_key:
            abort(401, "Invalid or missing API key")
        
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import get_jwt_identity, jwt_required
        from app.models.user import User
        
        @jwt_required()
        def check_admin():
            current_user = User.query.get(get_jwt_identity())
            if not current_user or current_user.role not in ['admin', 'super_admin']:
                abort(403, "Admin access required")
            return f(*args, **kwargs)
        
        return check_admin()
    return decorated_function


class CSRFProtection:
    """CSRF protection middleware."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection."""
        app.before_request(self._csrf_protect)
    
    def _csrf_protect(self):
        """Protect against CSRF attacks."""
        # Skip CSRF protection for safe methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return
        
        # Skip for API endpoints that use JWT
        if request.path.startswith('/api/'):
            return
        
        # Check CSRF token
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        if not token or not self._validate_csrf_token(token):
            abort(400, "CSRF token missing or invalid")
    
    def _validate_csrf_token(self, token):
        """Validate CSRF token."""
        # Implement CSRF token validation logic
        # This is a simplified version - use a proper CSRF library in production
        return True  # Placeholder