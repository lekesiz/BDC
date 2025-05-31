"""Cache middleware for automatic response caching."""
import json
from functools import wraps
from flask import request, make_response, current_app
from werkzeug.http import parse_etags, generate_etag

from app.core.cache_manager import cache_manager


def init_cache_middleware(app):
    """Initialize cache middleware for the Flask app."""
    middleware = CacheMiddleware()
    middleware.init_app(app)


class CacheMiddleware:
    """Middleware for HTTP caching headers and ETags."""
    
    def __init__(self, app=None):
        """Initialize cache middleware."""
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Check for conditional requests (If-None-Match)."""
        if request.method != 'GET':
            return
        
        # Check for If-None-Match header
        if_none_match = request.headers.get('If-None-Match')
        if not if_none_match:
            return
        
        # Generate cache key for current request
        cache_key = f"etag:{request.path}:{request.query_string.decode()}"
        cached_etag = cache_manager.get(cache_key)
        
        if cached_etag and cached_etag in parse_etags(if_none_match):
            # Return 304 Not Modified
            response = make_response('', 304)
            response.headers['ETag'] = cached_etag
            return response
    
    def after_request(self, response):
        """Add cache headers and ETags to responses."""
        # Only process successful GET requests
        if request.method != 'GET' or response.status_code != 200:
            return response
        
        # Skip if explicitly marked as no-cache
        if response.headers.get('Cache-Control') == 'no-cache':
            return response
        
        # Generate ETag from response data
        try:
            response_data = response.get_data(as_text=True)
            etag = generate_etag(response_data.encode())
            
            # Store ETag in cache
            cache_key = f"etag:{request.path}:{request.query_string.decode()}"
            cache_manager.set(cache_key, etag, ttl=300)  # 5 min
            
            # Add ETag header
            response.headers['ETag'] = etag
            
            # Add Cache-Control headers
            if not response.headers.get('Cache-Control'):
                # Default cache control for different endpoints
                if '/api/v2/cached/' in request.path:
                    response.headers['Cache-Control'] = 'public, max-age=300'
                elif '/static/' in request.path:
                    response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day
                else:
                    response.headers['Cache-Control'] = 'private, max-age=60'
            
            # Add Vary header for proper caching
            if 'Authorization' in request.headers:
                response.headers['Vary'] = 'Authorization'
                
        except Exception as e:
            current_app.logger.error(f"Error generating ETag: {e}")
        
        return response


def cache_control(max_age=None, no_cache=False, no_store=False, 
                 must_revalidate=False, public=False, private=False):
    """Decorator to set Cache-Control headers."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            # Build Cache-Control header
            directives = []
            
            if no_cache:
                directives.append('no-cache')
            if no_store:
                directives.append('no-store')
            if must_revalidate:
                directives.append('must-revalidate')
            if public:
                directives.append('public')
            elif private:
                directives.append('private')
            if max_age is not None:
                directives.append(f'max-age={max_age}')
            
            if directives:
                response.headers['Cache-Control'] = ', '.join(directives)
            
            return response
        return decorated_function
    return decorator


def etag(func):
    """Decorator to add ETag support to endpoints."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Check If-None-Match header
        if_none_match = request.headers.get('If-None-Match')
        
        # Generate response
        response = make_response(func(*args, **kwargs))
        
        # Generate ETag
        response_data = response.get_data(as_text=True)
        current_etag = generate_etag(response_data.encode())
        
        # Check if ETag matches
        if if_none_match and current_etag in parse_etags(if_none_match):
            response = make_response('', 304)
        
        response.headers['ETag'] = current_etag
        return response
    
    return decorated_function


def vary_on(*headers):
    """Decorator to add Vary header."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['Vary'] = ', '.join(headers)
            return response
        return decorated_function
    return decorator


# Conditional request helpers
def check_etag(etag_value):
    """Check if provided ETag matches current request."""
    if_none_match = request.headers.get('If-None-Match')
    if if_none_match and etag_value in parse_etags(if_none_match):
        return True
    return False


def check_last_modified(last_modified):
    """Check if resource was modified since provided date."""
    if_modified_since = request.headers.get('If-Modified-Since')
    if if_modified_since:
        # Parse and compare dates
        # Implementation would depend on date format
        pass
    return False