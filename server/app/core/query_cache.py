"""
Advanced Query Caching System with Redis
Provides intelligent query caching, cache invalidation, and performance optimization.
"""

import json
import pickle
import hashlib
import time
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from functools import wraps

import redis
from sqlalchemy.orm import Query
from sqlalchemy import inspect

from app.core.cache_manager import CacheManager
from app.core.cache_config import CacheConfig
from app.utils.logging import logger


class QueryCacheManager:
    """Advanced query caching with Redis backend"""
    
    def __init__(self, redis_client=None, default_ttl: int = 300):
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0,
            'errors': 0
        }
        self.query_patterns = {}
        
        # Cache key prefixes
        self.QUERY_PREFIX = "query_cache:"
        self.INVALIDATION_PREFIX = "invalidation:"
        self.STATS_PREFIX = "cache_stats:"
    
    def _generate_cache_key(self, query: Union[Query, str], params: Dict = None) -> str:
        """Generate a unique cache key for a query"""
        if isinstance(query, Query):
            query_str = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        else:
            query_str = str(query)
        
        # Include parameters in the key
        if params:
            query_str += json.dumps(params, sort_keys=True)
        
        # Create hash for consistent key length
        key_hash = hashlib.md5(query_str.encode()).hexdigest()
        return f"{self.QUERY_PREFIX}{key_hash}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        try:
            # Try JSON first for simple types
            if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
                return json.dumps(data).encode()
            else:
                # Use pickle for complex objects
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis"""
        try:
            # Try JSON first
            return json.loads(data.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Deserialization error: {e}")
                return None
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Get cached query result"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                self.cache_stats['hits'] += 1
                result = self._deserialize_data(cached_data)
                
                # Update access time for LRU tracking
                self.redis_client.expire(cache_key, self.default_ttl)
                
                logger.debug(f"Cache hit: {cache_key}")
                return result
            else:
                self.cache_stats['misses'] += 1
                return None
        
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, cache_key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set cached query result"""
        if not self.redis_client:
            return False
        
        ttl = ttl or self.default_ttl
        
        try:
            serialized_data = self._serialize_data(data)
            result = self.redis_client.setex(cache_key, ttl, serialized_data)
            
            if result:
                self.cache_stats['sets'] += 1
                logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s)")
            
            return result
        
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, cache_key: str) -> bool:
        """Delete cached query result"""
        if not self.redis_client:
            return False
        
        try:
            result = self.redis_client.delete(cache_key)
            if result:
                self.cache_stats['invalidations'] += 1
                logger.debug(f"Cache deleted: {cache_key}")
            return bool(result)
        
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Cache delete error: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache keys matching a pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(f"{self.QUERY_PREFIX}*{pattern}*")
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.cache_stats['invalidations'] += deleted_count
                logger.info(f"Invalidated {deleted_count} cache entries matching pattern: {pattern}")
                return deleted_count
            return 0
        
        except Exception as e:
            self.cache_stats['errors'] += 1
            logger.error(f"Cache pattern invalidation error: {e}")
            return 0
    
    def cached_query(self, query: Union[Query, Callable], 
                    cache_key: Optional[str] = None, 
                    ttl: Optional[int] = None,
                    invalidation_tags: List[str] = None) -> Any:
        """Execute a query with caching"""
        
        # Generate cache key if not provided
        if cache_key is None:
            if isinstance(query, Query):
                cache_key = self._generate_cache_key(query)
            else:
                # For callable queries, use function name and args
                cache_key = f"{self.QUERY_PREFIX}{query.__name__}_{hash(str(query))}"
        
        # Check cache first
        cached_result = self.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute query
        start_time = time.time()
        
        if isinstance(query, Query):
            result = query.all()
        elif callable(query):
            result = query()
        else:
            raise ValueError("Query must be a SQLAlchemy Query or callable")
        
        execution_time = time.time() - start_time
        
        # Cache the result
        self.set(cache_key, result, ttl)
        
        # Store invalidation tags for smart invalidation
        if invalidation_tags:
            self._store_invalidation_tags(cache_key, invalidation_tags)
        
        logger.debug(f"Query executed and cached: {cache_key} (execution: {execution_time:.3f}s)")
        return result
    
    def _store_invalidation_tags(self, cache_key: str, tags: List[str]):
        """Store cache invalidation tags"""
        for tag in tags:
            tag_key = f"{self.INVALIDATION_PREFIX}{tag}"
            try:
                self.redis_client.sadd(tag_key, cache_key)
                self.redis_client.expire(tag_key, self.default_ttl * 2)  # Tags live longer
            except Exception as e:
                logger.error(f"Error storing invalidation tag {tag}: {e}")
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        total_invalidated = 0
        
        for tag in tags:
            tag_key = f"{self.INVALIDATION_PREFIX}{tag}"
            try:
                cache_keys = self.redis_client.smembers(tag_key)
                if cache_keys:
                    # Delete cached entries
                    deleted_count = self.redis_client.delete(*cache_keys)
                    total_invalidated += deleted_count
                    
                    # Clean up the tag set
                    self.redis_client.delete(tag_key)
                    
                    logger.info(f"Invalidated {deleted_count} entries for tag: {tag}")
            
            except Exception as e:
                logger.error(f"Error invalidating by tag {tag}: {e}")
        
        return total_invalidated
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'cache_stats': self.cache_stats.copy(),
            'hit_rate_percentage': round(hit_rate, 2),
            'total_requests': total_requests
        }
        
        # Get Redis memory usage if available
        if self.redis_client:
            try:
                redis_info = self.redis_client.info('memory')
                stats['redis_memory'] = {
                    'used_memory': redis_info.get('used_memory'),
                    'used_memory_human': redis_info.get('used_memory_human'),
                    'maxmemory': redis_info.get('maxmemory'),
                    'maxmemory_human': redis_info.get('maxmemory_human')
                }
            except Exception as e:
                logger.error(f"Error getting Redis memory info: {e}")
        
        return stats
    
    def warm_cache(self, warm_queries: List[Dict[str, Any]]):
        """Pre-warm cache with important queries"""
        logger.info(f"Starting cache warming with {len(warm_queries)} queries")
        
        for query_config in warm_queries:
            try:
                query_func = query_config['query']
                cache_key = query_config.get('cache_key')
                ttl = query_config.get('ttl', self.default_ttl)
                
                # Execute and cache the query
                self.cached_query(query_func, cache_key, ttl)
                
                logger.debug(f"Warmed cache for: {cache_key or query_func.__name__}")
            
            except Exception as e:
                logger.error(f"Error warming cache for query: {e}")
        
        logger.info("Cache warming completed")
    
    def cleanup_expired_entries(self):
        """Clean up expired cache entries (maintenance task)"""
        if not self.redis_client:
            return
        
        try:
            # Get all cache keys
            cache_keys = self.redis_client.keys(f"{self.QUERY_PREFIX}*")
            expired_count = 0
            
            for key in cache_keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -2:  # Key has expired
                    self.redis_client.delete(key)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache entries")
        
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")


class SmartCacheInvalidator:
    """Intelligent cache invalidation based on data changes"""
    
    def __init__(self, query_cache: QueryCacheManager):
        self.query_cache = query_cache
        
        # Define invalidation rules for different models
        self.invalidation_rules = {
            'User': {
                'patterns': ['user_list', 'user_detail', 'user_stats'],
                'tags': ['users', 'authentication']
            },
            'Beneficiary': {
                'patterns': ['beneficiary_list', 'beneficiary_detail', 'beneficiary_stats'],
                'tags': ['beneficiaries', 'students']
            },
            'Appointment': {
                'patterns': ['appointment_list', 'calendar', 'schedule'],
                'tags': ['appointments', 'calendar', 'schedule']
            },
            'Evaluation': {
                'patterns': ['evaluation_list', 'evaluation_results', 'analytics'],
                'tags': ['evaluations', 'assessments', 'analytics']
            },
            'Program': {
                'patterns': ['program_list', 'program_detail', 'enrollment'],
                'tags': ['programs', 'training']
            }
        }
    
    def invalidate_for_model(self, model_name: str, action: str = 'update'):
        """Invalidate cache entries for a specific model change"""
        rules = self.invalidation_rules.get(model_name, {})
        
        # Invalidate by patterns
        patterns = rules.get('patterns', [])
        total_invalidated = 0
        
        for pattern in patterns:
            count = self.query_cache.invalidate_pattern(pattern)
            total_invalidated += count
        
        # Invalidate by tags
        tags = rules.get('tags', [])
        if tags:
            count = self.query_cache.invalidate_by_tags(tags)
            total_invalidated += count
        
        logger.info(f"Invalidated {total_invalidated} cache entries for {model_name} {action}")
        return total_invalidated
    
    def on_model_change(self, model_instance, action: str):
        """Handle model change events"""
        model_name = model_instance.__class__.__name__
        return self.invalidate_for_model(model_name, action)


# Decorator for caching query results
def cached_query(ttl: int = 300, invalidation_tags: List[str] = None):
    """Decorator for caching query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key based on function name and arguments
            cache_key = f"query:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Get or create query cache manager
            cache_manager = query_cache_manager
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            # Store invalidation tags if provided
            if invalidation_tags:
                cache_manager._store_invalidation_tags(cache_key, invalidation_tags)
            
            return result
        
        return wrapper
    return decorator


# Global instances
query_cache_manager = QueryCacheManager()
cache_invalidator = SmartCacheInvalidator(query_cache_manager)


def init_query_cache(app):
    """Initialize query cache with Flask app"""
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        redis_client = redis.from_url(redis_url, decode_responses=False)
        query_cache_manager.redis_client = redis_client
        
        # Test connection
        redis_client.ping()
        logger.info(f"Query cache initialized with Redis: {redis_url}")
        
    except Exception as e:
        logger.error(f"Failed to initialize query cache: {e}")
        query_cache_manager.redis_client = None