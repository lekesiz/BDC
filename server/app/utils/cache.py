"""Cache utility module."""

from functools import wraps
from flask import request, current_app
import json
import hashlib

from app.extensions import cache, logger


def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate a unique cache key based on the provided arguments.
    
    Args:
        prefix (str): Prefix for the cache key
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
        
    Returns:
        str: A unique cache key
    """
    # Convert args and kwargs to a string representation
    args_str = json.dumps(args, sort_keys=True) if args else ''
    kwargs_str = json.dumps(kwargs, sort_keys=True) if kwargs else ''
    
    # Create a hash of the arguments
    args_hash = hashlib.md5(f"{args_str}{kwargs_str}".encode('utf-8')).hexdigest()
    
    # Return the cache key
    return f"{prefix}:{args_hash}"


def cache_response(timeout=300, key_prefix='view'):
    """
    Decorator to cache API responses.
    
    Args:
        timeout (int): Cache timeout in seconds
        key_prefix (str): Prefix for the cache key
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip cache in debug mode if configured
            if current_app.config.get('DEBUG') and not current_app.config.get('CACHE_IN_DEBUG', False):
                return f(*args, **kwargs)
            
            # Get cache key from request path and query parameters
            path = request.path
            query_args = request.args.to_dict(flat=False)
            
            # Add user identity to the cache key if authenticated
            user_id = getattr(request, 'user_id', None)
            
            # Generate cache key
            cache_key = generate_cache_key(
                f"{key_prefix}:{path}",
                query_args=query_args,
                user_id=user_id
            )
            
            # Try to get the cached response
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_response
            
            # Get the response from the function
            response = f(*args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, response, timeout=timeout)
            logger.debug(f"Cached response with key: {cache_key}, timeout: {timeout}")
            
            return response
        return decorated_function
    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        key_pattern (str): Pattern to match cache keys
        
    Returns:
        int: Number of keys invalidated
    """
    try:
        # Try to access the Redis client
        if hasattr(cache, 'cache') and hasattr(cache.cache, '_client'):
            # Flask-Caching with Redis
            keys = cache.cache._client.keys(f"{key_pattern}*")
            if keys:
                cache.cache._client.delete(*keys)
                logger.debug(f"Invalidated {len(keys)} cache entries with pattern: {key_pattern}")
                return len(keys)
        else:
            # Fallback - clear the entire cache (less efficient)
            logger.warning(f"Cannot access Redis client, clearing entire cache instead of pattern: {key_pattern}")
            cache.clear()
            return 1
    except Exception as e:
        logger.error(f"Error invalidating cache for pattern {key_pattern}: {str(e)}")
        # Fallback - clear the entire cache
        try:
            cache.clear()
            return 1
        except:
            return 0
    return 0


def clear_user_cache(user_id):
    """
    Clear all cache entries for a specific user.
    
    Args:
        user_id (int): User ID
        
    Returns:
        int: Number of keys invalidated
    """
    return invalidate_cache(f"*:user_id:{user_id}*")


def clear_model_cache(model_name):
    """
    Clear all cache entries for a specific model.
    
    Args:
        model_name (str): Model name
        
    Returns:
        int: Number of keys invalidated
    """
    return invalidate_cache(f"{model_name}:*")