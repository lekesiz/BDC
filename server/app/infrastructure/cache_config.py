"""
Cache Configuration and Strategy
Implements multi-level caching for optimal performance
"""

import redis
from flask_caching import Cache
from functools import wraps
import json
import time
from typing import Any, Optional, Dict
import hashlib

class CacheConfig:
    """Cache configuration settings"""
    
    # Cache TTL settings (in seconds)
    TTL_SHORT = 300        # 5 minutes
    TTL_MEDIUM = 3600      # 1 hour
    TTL_LONG = 86400       # 24 hours
    TTL_EXTRA_LONG = 604800  # 7 days
    
    # Cache key prefixes
    PREFIX_USER = "user:"
    PREFIX_BENEFICIARY = "beneficiary:"
    PREFIX_PROGRAM = "program:"
    PREFIX_APPOINTMENT = "appointment:"
    PREFIX_DOCUMENT = "document:"
    PREFIX_EVALUATION = "evaluation:"
    PREFIX_ANALYTICS = "analytics:"
    PREFIX_LIST = "list:"
    PREFIX_COUNT = "count:"
    
    @staticmethod
    def get_redis_config():
        """Get Redis configuration"""
        return {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': 'redis',
            'CACHE_REDIS_PORT': 6379,
            'CACHE_REDIS_DB': 0,
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'bdc:',
        }
    
    @staticmethod
    def get_simple_config():
        """Get simple cache configuration for development"""
        return {
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 300,
        }

class CacheManager:
    """Advanced cache management with multiple strategies"""
    
    def __init__(self, app=None, redis_client=None):
        self.cache = None
        self.redis_client = redis_client
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize cache with Flask app"""
        self.app = app
        
        # Initialize Flask-Caching
        cache_config = CacheConfig.get_redis_config() if app.config.get('USE_REDIS', True) else CacheConfig.get_simple_config()
        self.cache = Cache(app, config=cache_config)
        
        # Initialize Redis client for advanced operations
        if app.config.get('USE_REDIS', True):
            try:
                self.redis_client = redis.Redis(
                    host=cache_config.get('CACHE_REDIS_HOST', 'localhost'),
                    port=cache_config.get('CACHE_REDIS_PORT', 6379),
                    db=cache_config.get('CACHE_REDIS_DB', 0),
                    decode_responses=True
                )
                self.redis_client.ping()
            except Exception as e:
                app.logger.warning(f"Redis connection failed: {e}. Falling back to simple cache.")
                self.redis_client = None
    
    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate a consistent cache key"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    def get_or_set(self, key: str, func, ttl: int = CacheConfig.TTL_SHORT):
        """Get from cache or compute and set"""
        value = self.get(key)
        if value is None:
            value = func()
            self.set(key, value, ttl)
        return value
    
    def get(self, key: str) -> Any:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                return self.cache.get(key)
        except Exception as e:
            self.app.logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = CacheConfig.TTL_SHORT):
        """Set value in cache with TTL"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                self.cache.set(key, value, timeout=ttl)
        except Exception as e:
            self.app.logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.cache.delete(key)
        except Exception as e:
            self.app.logger.error(f"Cache delete error: {e}")
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        try:
            if self.redis_client:
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            else:
                # Simple cache doesn't support pattern deletion
                self.cache.clear()
        except Exception as e:
            self.app.logger.error(f"Cache delete pattern error: {e}")
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache"""
        try:
            if self.redis_client:
                return self.redis_client.incr(key, amount)
            else:
                current = self.get(key) or 0
                new_value = current + amount
                self.set(key, new_value)
                return new_value
        except Exception as e:
            self.app.logger.error(f"Cache increment error: {e}")
            return 0
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """Get multiple values from cache"""
        try:
            if self.redis_client:
                values = self.redis_client.mget(keys)
                return {
                    key: json.loads(value) if value else None 
                    for key, value in zip(keys, values)
                }
            else:
                return {key: self.cache.get(key) for key in keys}
        except Exception as e:
            self.app.logger.error(f"Cache get_many error: {e}")
            return {}
    
    def set_many(self, mapping: Dict[str, Any], ttl: int = CacheConfig.TTL_SHORT):
        """Set multiple values in cache"""
        try:
            if self.redis_client:
                pipe = self.redis_client.pipeline()
                for key, value in mapping.items():
                    pipe.setex(key, ttl, json.dumps(value))
                pipe.execute()
            else:
                for key, value in mapping.items():
                    self.cache.set(key, value, timeout=ttl)
        except Exception as e:
            self.app.logger.error(f"Cache set_many error: {e}")

def cache_key_wrapper(prefix: str, ttl: int = CacheConfig.TTL_SHORT):
    """Decorator for caching function results with custom key generation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key_parts = [prefix, func.__name__]
            
            # Add positional arguments to key
            for arg in args:
                if hasattr(arg, 'id'):
                    cache_key_parts.append(str(arg.id))
                else:
                    cache_key_parts.append(str(arg))
            
            # Add keyword arguments to key
            for k, v in sorted(kwargs.items()):
                cache_key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if cache_manager:
                cached_value = cache_manager.get(cache_key)
                if cached_value is not None:
                    return cached_value
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            if cache_manager and result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """Decorator to invalidate cache keys matching pattern after function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if cache_manager:
                cache_manager.delete_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator

# Cache warming strategies
class CacheWarmer:
    """Warm cache with frequently accessed data"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def warm_user_cache(self, user_ids: list):
        """Pre-load user data into cache"""
        from app.models import User
        
        users = User.query.filter(User.id.in_(user_ids)).all()
        mapping = {}
        
        for user in users:
            key = CacheConfig.PREFIX_USER + str(user.id)
            mapping[key] = user.to_dict()
        
        self.cache_manager.set_many(mapping, CacheConfig.TTL_MEDIUM)
    
    def warm_beneficiary_cache(self, beneficiary_ids: list):
        """Pre-load beneficiary data into cache"""
        from app.models import Beneficiary
        
        beneficiaries = Beneficiary.query.filter(Beneficiary.id.in_(beneficiary_ids)).all()
        mapping = {}
        
        for beneficiary in beneficiaries:
            key = CacheConfig.PREFIX_BENEFICIARY + str(beneficiary.id)
            mapping[key] = beneficiary.to_dict()
        
        self.cache_manager.set_many(mapping, CacheConfig.TTL_MEDIUM)
    
    def warm_program_cache(self):
        """Pre-load active programs into cache"""
        from app.models import Program
        
        programs = Program.query.filter_by(status='active').all()
        mapping = {}
        
        for program in programs:
            key = CacheConfig.PREFIX_PROGRAM + str(program.id)
            mapping[key] = program.to_dict()
        
        self.cache_manager.set_many(mapping, CacheConfig.TTL_LONG)