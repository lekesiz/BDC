"""Enhanced rate limiting configuration."""

from flask import request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from typing import Optional, Callable


def get_identifier() -> str:
    """Get unique identifier for rate limiting."""
    # Try to get authenticated user ID from JWT
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
    except:
        pass
    
    # Fall back to IP address
    return get_remote_address()


# Initialize limiter
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="redis://localhost:6379",
    strategy="fixed-window-elastic-expiry"
)


# Rate limit decorators for different endpoints
class RateLimits:
    """Common rate limit configurations."""
    
    # Authentication endpoints
    LOGIN = "5 per minute"
    REGISTER = "3 per hour"
    PASSWORD_RESET = "3 per hour"
    TWO_FACTOR = "10 per hour"
    
    # API endpoints
    API_DEFAULT = "100 per hour"
    API_HEAVY = "20 per hour"  # For resource-intensive operations
    API_SEARCH = "30 per minute"
    API_UPLOAD = "10 per hour"
    
    # Public endpoints
    PUBLIC = "30 per minute"
    HEALTH_CHECK = "60 per minute"


def configure_rate_limiting(app):
    """Configure rate limiting for the application."""
    limiter.init_app(app)
    
    # Configure error messages
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {e.description}",
            "retry_after": e.retry_after if hasattr(e, 'retry_after') else None
        }, 429
    
    # Apply rate limits to specific endpoints
    apply_endpoint_limits(app)


def apply_endpoint_limits(app):
    """Apply rate limits to specific endpoints."""
    
    # Authentication endpoints
    auth_endpoints = [
        ('/api/auth/login', RateLimits.LOGIN),
        ('/api/auth/register', RateLimits.REGISTER),
        ('/api/auth/reset-password', RateLimits.PASSWORD_RESET),
        ('/api/auth/verify-2fa', RateLimits.TWO_FACTOR),
    ]
    
    # Heavy API endpoints
    heavy_endpoints = [
        ('/api/reports/generate', RateLimits.API_HEAVY),
        ('/api/evaluations/analyze', RateLimits.API_HEAVY),
        ('/api/ai/generate', RateLimits.API_HEAVY),
    ]
    
    # Upload endpoints
    upload_endpoints = [
        ('/api/documents/upload', RateLimits.API_UPLOAD),
        ('/api/users/avatar', RateLimits.API_UPLOAD),
    ]
    
    # Search endpoints
    search_endpoints = [
        ('/api/search', RateLimits.API_SEARCH),
        ('/api/beneficiaries/search', RateLimits.API_SEARCH),
    ]
    
    # Apply limits
    for endpoint, limit in auth_endpoints + heavy_endpoints + upload_endpoints + search_endpoints:
        limiter.limit(limit, endpoint=endpoint)


def dynamic_rate_limit(user_role: Optional[str] = None) -> str:
    """Get dynamic rate limit based on user role."""
    role_limits = {
        'super_admin': "1000 per hour",
        'tenant_admin': "500 per hour",
        'trainer': "300 per hour",
        'student': "100 per hour",
        None: "50 per hour"  # Anonymous users
    }
    
    return role_limits.get(user_role, role_limits[None])


def exempt_when(condition: Callable[[], bool]):
    """Conditionally exempt from rate limiting."""
    def decorator(f):
        @limiter.exempt
        def wrapped(*args, **kwargs):
            if condition():
                return f(*args, **kwargs)
            return limiter.limit(RateLimits.API_DEFAULT)(f)(*args, **kwargs)
        return wrapped
    return decorator


def get_rate_limit_status():
    """Get current rate limit status for the requester."""
    try:
        key = get_identifier()
        # Get Redis connection from limiter
        storage = limiter._storage
        
        # Check various windows
        windows = {
            'minute': 60,
            'hour': 3600,
        }
        
        status = {}
        for window_name, window_seconds in windows.items():
            window_key = f"LIMITER/{key}/{window_seconds}"
            current = storage.get(window_key)
            
            if current:
                current_count = int(current)
                # Get limit for this window
                if window_name == 'minute':
                    limit = 50  # Default minute limit
                else:
                    limit = 200  # Default hour limit
                
                status[window_name] = {
                    'count': current_count,
                    'limit': limit,
                    'remaining': max(0, limit - current_count)
                }
            else:
                status[window_name] = {
                    'count': 0,
                    'limit': 50 if window_name == 'minute' else 200,
                    'remaining': 50 if window_name == 'minute' else 200
                }
        
        return status
    except Exception as e:
        current_app.logger.error(f"Error getting rate limit status: {str(e)}")
        return None


# Utility functions
def is_whitelisted_ip(ip: str) -> bool:
    """Check if IP is whitelisted from rate limiting."""
    whitelist = current_app.config.get('RATELIMIT_WHITELIST', [])
    return ip in whitelist


def is_blacklisted_ip(ip: str) -> bool:
    """Check if IP is blacklisted (always rate limited)."""
    blacklist = current_app.config.get('RATELIMIT_BLACKLIST', [])
    return ip in blacklist


def temporary_increase_limit(user_id: int, multiplier: float = 2.0, duration: int = 3600):
    """Temporarily increase rate limit for a user."""
    # This would need custom implementation with Redis
    # to store temporary multipliers
    pass