"""Advanced cache management for API responses."""
import json
import hashlib
from typing import Any, Optional, Union, Callable
from functools import wraps
from datetime import datetime, timedelta
import pickle

from flask import request, current_app
from app.utils.cache import cache as redis_cache


class CacheManager:
    """Manages caching strategies for API responses."""
    
    def __init__(self, cache_backend=None):
        """Initialize cache manager."""
        self.cache = cache_backend or redis_cache
        self.default_ttl = 300  # 5 minutes
        self.cache_prefix = "api_response"
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key based on function arguments."""
        # Include request path, method, and args
        key_parts = [
            self.cache_prefix,
            prefix,
            request.method if request else 'GET',
            request.path if request else '',
        ]
        
        # Add query parameters if present
        if request and request.args:
            sorted_args = sorted(request.args.items())
            key_parts.append(str(sorted_args))
        
        # Add function arguments
        if args:
            key_parts.extend(str(arg) for arg in args)
        
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(str(sorted_kwargs))
        
        # Create hash of all parts
        key_string = ':'.join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.cache_prefix}:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            cached_value = self.cache.get(key)
            if cached_value:
                # Try to deserialize as JSON first
                try:
                    return json.loads(cached_value)
                except (json.JSONDecodeError, TypeError):
                    # Fall back to pickle for complex objects
                    try:
                        return pickle.loads(cached_value)
                    except:
                        return cached_value
        except Exception as e:
            current_app.logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            
            # Try to serialize as JSON first (more portable)
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fall back to pickle for complex objects
                serialized = pickle.dumps(value)
            
            return self.cache.set(key, serialized, timeout=ttl)
        except Exception as e:
            current_app.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return self.cache.delete(key)
        except Exception as e:
            current_app.logger.error(f"Cache delete error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        try:
            # Get all keys matching pattern
            keys = self.cache.get_many(pattern)
            if keys:
                for key in keys:
                    self.cache.delete(key)
                return len(keys)
            return 0
        except Exception as e:
            current_app.logger.error(f"Cache invalidate pattern error: {e}")
            return 0
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all cache entries matching a pattern."""
        return self.invalidate_pattern(pattern)
    
    def clear_all(self) -> bool:
        """Clear all cache entries."""
        try:
            self.cache.clear()
            return True
        except Exception as e:
            current_app.logger.error(f"Cache clear all error: {e}")
            return False
    
    def cache_response(self, ttl: Optional[int] = None, 
                      key_prefix: Optional[str] = None,
                      unless: Optional[Callable] = None,
                      vary_on_headers: Optional[list] = None):
        """Decorator to cache API responses."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check if caching should be skipped
                if unless and unless():
                    return f(*args, **kwargs)
                
                # Generate cache key
                prefix = key_prefix or f.__name__
                
                # Include varying headers in cache key if specified
                if vary_on_headers and request:
                    header_values = {h: request.headers.get(h, '') for h in vary_on_headers}
                    kwargs['_headers'] = header_values
                
                cache_key = self.generate_cache_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_response = self.get(cache_key)
                if cached_response is not None:
                    current_app.logger.debug(f"Cache hit for key: {cache_key}")
                    # Add cache hit header
                    from flask import make_response
                    if isinstance(cached_response, tuple):
                        data, status = cached_response[:2]
                        response = make_response(data, status)
                    else:
                        response = make_response(cached_response)
                    response.headers['X-Cache'] = 'HIT'
                    return response
                
                # Execute function and cache result
                current_app.logger.debug(f"Cache miss for key: {cache_key}")
                result = f(*args, **kwargs)
                
                # Add cache miss header
                from flask import make_response
                if isinstance(result, tuple):
                    data, status = result[:2]
                    response = make_response(data, status)
                    # Only cache successful responses
                    if 200 <= status < 300:
                        self.set(cache_key, result, ttl)
                else:
                    response = make_response(result)
                    self.set(cache_key, result, ttl)
                
                response.headers['X-Cache'] = 'MISS'
                response.headers['Cache-Control'] = f'private, max-age={ttl or self.default_ttl}'
                return response
            
            return decorated_function
        return decorator
    
    def cache_key_wrapper(self, key_func: Callable):
        """Decorator with custom cache key generation."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Generate custom cache key
                cache_key = key_func(*args, **kwargs)
                
                # Try to get from cache
                cached_response = self.get(cache_key)
                if cached_response is not None:
                    return cached_response
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                self.set(cache_key, result)
                
                return result
            
            return decorated_function
        return decorator


# Global cache manager instance
cache_manager = CacheManager()


# Cache invalidation helpers
def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user."""
    patterns = [
        f"api_response:user:{user_id}:*",
        f"api_response:*:user_{user_id}_*"
    ]
    
    for pattern in patterns:
        cache_manager.invalidate_pattern(pattern)


def invalidate_beneficiary_cache(beneficiary_id: int):
    """Invalidate all cache entries for a beneficiary."""
    patterns = [
        f"api_response:beneficiary:{beneficiary_id}:*",
        f"api_response:*:beneficiary_{beneficiary_id}_*"
    ]
    
    for pattern in patterns:
        cache_manager.invalidate_pattern(pattern)


def invalidate_tenant_cache(tenant_id: int):
    """Invalidate all cache entries for a tenant."""
    patterns = [
        f"api_response:tenant:{tenant_id}:*",
        f"api_response:*:tenant_{tenant_id}_*"
    ]
    
    for pattern in patterns:
        cache_manager.invalidate_pattern(pattern)


# Conditional caching helpers
def should_skip_cache():
    """Check if caching should be skipped for current request."""
    # Skip cache for POST, PUT, DELETE requests
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        return True
    
    # Skip cache if no-cache header is present
    if request.headers.get('Cache-Control') == 'no-cache':
        return True
    
    # Skip cache if user is admin (always fresh data)
    # This would need actual implementation based on your auth
    # from flask_jwt_extended import get_jwt_identity, current_user
    # if current_user and current_user.role == 'admin':
    #     return True
    
    return False