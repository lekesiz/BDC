"""Query result caching for database performance optimization."""

import json
import hashlib
import logging
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
from functools import wraps

from flask import current_app
from app.extensions import redis_client

logger = logging.getLogger(__name__)


class QueryCacheManager:
    """Manages caching of database query results."""
    
    def __init__(self, cache_backend=None):
        """Initialize query cache manager."""
        self.cache = cache_backend or redis_client
        self.default_ttl = 300  # 5 minutes
        self.cache_prefix = "query_cache"
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'errors': 0
        }
        
    def generate_cache_key(self, query: str, params: Dict = None) -> str:
        """Generate a unique cache key for a query and its parameters."""
        # Create a deterministic string representation
        key_parts = [
            self.cache_prefix,
            query,
            json.dumps(params or {}, sort_keys=True)
        ]
        
        key_string = ":".join(key_parts)
        
        # Generate hash for long keys
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{self.cache_prefix}:hash:{key_hash}"
            
        return key_string
        
    def get(self, query: str, params: Dict = None) -> Optional[Any]:
        """Get cached query result."""
        if not self.cache:
            return None
            
        key = self.generate_cache_key(query, params)
        
        try:
            cached_value = self.cache.get(key)
            
            if cached_value:
                self.stats['hits'] += 1
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return json.loads(cached_value)
            else:
                self.stats['misses'] += 1
                logger.debug(f"Cache miss for query: {query[:50]}...")
                return None
                
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache get error: {str(e)}")
            return None
            
    def set(self, query: str, result: Any, params: Dict = None, ttl: int = None) -> bool:
        """Cache query result."""
        if not self.cache:
            return False
            
        key = self.generate_cache_key(query, params)
        ttl = ttl or self.default_ttl
        
        try:
            # Serialize the result
            serialized = json.dumps(result, default=str)
            
            # Store in cache
            self.cache.setex(key, ttl, serialized)
            
            logger.debug(f"Cached query result: {query[:50]}... (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache set error: {str(e)}")
            return False
            
    def invalidate(self, query: str, params: Dict = None) -> bool:
        """Invalidate cached query result."""
        if not self.cache:
            return False
            
        key = self.generate_cache_key(query, params)
        
        try:
            result = self.cache.delete(key)
            if result:
                self.stats['evictions'] += 1
                logger.debug(f"Invalidated cache for query: {query[:50]}...")
            return bool(result)
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache invalidate error: {str(e)}")
            return False
            
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cached queries matching a pattern."""
        if not self.cache:
            return 0
            
        try:
            # Find all matching keys
            full_pattern = f"{self.cache_prefix}:{pattern}"
            matching_keys = []
            
            # Scan for matching keys
            cursor = 0
            while True:
                cursor, keys = self.cache.scan(cursor, match=full_pattern, count=100)
                matching_keys.extend(keys)
                if cursor == 0:
                    break
                    
            # Delete matching keys
            if matching_keys:
                deleted = self.cache.delete(*matching_keys)
                self.stats['evictions'] += deleted
                logger.info(f"Invalidated {deleted} cached queries matching pattern: {pattern}")
                return deleted
                
            return 0
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache pattern invalidate error: {str(e)}")
            return 0
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': f"{hit_rate:.2f}%",
            'evictions': self.stats['evictions'],
            'errors': self.stats['errors'],
            'total_requests': total_requests
        }
        
    def clear_all(self) -> bool:
        """Clear all cached queries."""
        if not self.cache:
            return False
            
        try:
            # Find all cache keys
            pattern = f"{self.cache_prefix}:*"
            matching_keys = []
            
            cursor = 0
            while True:
                cursor, keys = self.cache.scan(cursor, match=pattern, count=100)
                matching_keys.extend(keys)
                if cursor == 0:
                    break
                    
            # Delete all keys
            if matching_keys:
                deleted = self.cache.delete(*matching_keys)
                logger.info(f"Cleared {deleted} cached queries")
                return True
                
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def warm_cache(self, warm_queries: list) -> None:
        """Warm cache with predefined queries."""
        for query_info in warm_queries:
            try:
                result = query_info['query']()
                self.set(query_info['cache_key'], result, ttl=query_info.get('ttl', self.default_ttl))
                logger.debug(f"Warmed cache: {query_info['cache_key']}")
            except Exception as e:
                logger.error(f"Failed to warm cache for {query_info.get('cache_key', 'unknown')}: {str(e)}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics for reporting."""
        stats = self.get_stats()
        total_requests = stats['total_requests']
        hit_rate = float(stats['hit_rate'].rstrip('%')) if total_requests > 0 else 0.0
        
        return {
            'hit_count': stats['hits'],
            'miss_count': stats['misses'],
            'hit_rate_percentage': hit_rate,
            'eviction_count': stats['evictions'],
            'error_count': stats['errors'],
            'total_requests': total_requests,
            'cache_enabled': self.cache is not None
        }


# Global instance
query_cache_manager = QueryCacheManager()


def cached_query(ttl: int = None, key_prefix: str = None):
    """Decorator to cache query results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [
                key_prefix or func.__name__,
                str(args),
                str(sorted(kwargs.items()))
            ]
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = query_cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Execute query
            result = func(*args, **kwargs)
            
            # Cache the result
            query_cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
            
        return wrapper
    return decorator


def invalidate_on_change(*table_names):
    """Decorator to invalidate cache when certain tables are modified."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the function
            result = func(*args, **kwargs)
            
            # Invalidate cache for affected tables
            for table_name in table_names:
                pattern = f"*{table_name}*"
                invalidated = query_cache_manager.invalidate_pattern(pattern)
                if invalidated:
                    logger.debug(f"Invalidated {invalidated} cache entries for table: {table_name}")
                    
            return result
            
        return wrapper
    return decorator


def init_query_cache(app):
    """Initialize query cache with Flask app."""
    # Query cache is already initialized globally
    # This function is for compatibility with performance_init
    logger.info("Query cache initialized")
    return query_cache_manager