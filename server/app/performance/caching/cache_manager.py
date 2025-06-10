"""
Advanced Cache Manager

Provides comprehensive caching strategies including multi-level caching,
intelligent cache warming, and automatic cache invalidation.
"""

import time
import json
import pickle
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import redis
from flask import Flask, request, g
from flask_caching import Cache


class CacheLevel(Enum):
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"


class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    READ_THROUGH = "read_through"


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    default_ttl: int = 3600
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    redis_url: str = "redis://localhost:6379/0"
    enable_compression: bool = True
    enable_serialization: bool = True
    cache_key_prefix: str = "bdc"
    strategies: List[CacheStrategy] = None
    
    def __post_init__(self):
        if self.strategies is None:
            self.strategies = [CacheStrategy.LRU, CacheStrategy.TTL]


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    ttl: int
    created_at: float
    last_accessed: float
    access_count: int
    size_bytes: int
    tags: List[str]


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    memory_usage: int = 0
    hit_rate: float = 0.0


class CacheManager:
    """
    Advanced multi-level cache manager with intelligent caching strategies.
    """
    
    def __init__(self, app: Optional[Flask] = None, config: Optional[CacheConfig] = None):
        self.app = app
        self.config = config or CacheConfig()
        self.l1_cache = {}  # In-memory cache
        self.l2_cache = None  # Redis cache
        self.cache_stats = defaultdict(CacheStats)
        self.cache_metadata = {}
        self.invalidation_callbacks = defaultdict(list)
        self.warming_functions = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize cache manager with Flask app"""
        self.app = app
        
        # Initialize Flask-Caching for L1 cache
        self.flask_cache = Cache(app, config={
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': self.config.default_ttl
        })
        
        # Initialize Redis for L2 cache
        try:
            self.l2_cache = redis.from_url(
                self.config.redis_url,
                decode_responses=False  # We'll handle serialization
            )
            # Test connection
            self.l2_cache.ping()
            logging.info("Redis cache initialized successfully")
        except Exception as e:
            logging.warning(f"Redis cache initialization failed: {e}")
            self.l2_cache = None
        
        # Register middleware
        self._register_middleware()
        
        # Store in app extensions
        app.extensions['cache_manager'] = self
    
    def get(self, key: str, default: Any = None, 
            levels: List[CacheLevel] = None) -> Any:
        """
        Get value from cache with multi-level lookup.
        """
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        full_key = self._generate_key(key)
        
        # Try each cache level
        for level in levels:
            value = self._get_from_level(full_key, level)
            if value is not None:
                self._record_hit(level)
                self._update_access_metadata(full_key)
                
                # Promote to higher levels if needed
                self._promote_to_higher_levels(full_key, value, level, levels)
                
                return value
        
        # Cache miss
        for level in levels:
            self._record_miss(level)
        
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            levels: List[CacheLevel] = None, tags: List[str] = None) -> bool:
        """
        Set value in cache across multiple levels.
        """
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        full_key = self._generate_key(key)
        ttl = ttl or self.config.default_ttl
        tags = tags or []
        
        success = True
        serialized_value = self._serialize_value(value)
        
        # Set in all specified levels
        for level in levels:
            level_success = self._set_in_level(full_key, serialized_value, ttl, level)
            success = success and level_success
            
            if level_success:
                self._record_set(level)
        
        # Update metadata
        self._update_set_metadata(full_key, value, ttl, tags)
        
        return success
    
    def delete(self, key: str, levels: List[CacheLevel] = None) -> bool:
        """
        Delete value from cache across multiple levels.
        """
        if levels is None:
            levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        full_key = self._generate_key(key)
        success = True
        
        for level in levels:
            level_success = self._delete_from_level(full_key, level)
            success = success and level_success
            
            if level_success:
                self._record_delete(level)
        
        # Remove metadata
        self.cache_metadata.pop(full_key, None)
        
        return success
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """
        Invalidate all cache entries with specific tags.
        """
        invalidated_count = 0
        
        # Find keys with matching tags
        keys_to_invalidate = []
        for key, metadata in self.cache_metadata.items():
            if hasattr(metadata, 'tags') and any(tag in metadata.tags for tag in tags):
                keys_to_invalidate.append(key)
        
        # Invalidate found keys
        for key in keys_to_invalidate:
            if self.delete(key.replace(f"{self.config.cache_key_prefix}:", "")):
                invalidated_count += 1
        
        return invalidated_count
    
    def warm_cache(self, warming_functions: Dict[str, Callable] = None):
        """
        Warm cache with pre-computed values.
        """
        functions = warming_functions or self.warming_functions
        
        for key, func in functions.items():
            try:
                value = func()
                self.set(key, value, tags=['warmed'])
                logging.info(f"Cache warmed for key: {key}")
            except Exception as e:
                logging.error(f"Cache warming failed for key {key}: {e}")
    
    def clear_level(self, level: CacheLevel) -> bool:
        """
        Clear entire cache level.
        """
        try:
            if level == CacheLevel.L1_MEMORY:
                self.l1_cache.clear()
                if hasattr(self, 'flask_cache'):
                    self.flask_cache.clear()
                
            elif level == CacheLevel.L2_REDIS and self.l2_cache:
                # Clear only keys with our prefix
                pattern = f"{self.config.cache_key_prefix}:*"
                keys = self.l2_cache.keys(pattern)
                if keys:
                    self.l2_cache.delete(*keys)
            
            # Clear metadata for this level
            self._clear_level_metadata(level)
            
            logging.info(f"Cleared cache level: {level.value}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to clear cache level {level.value}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all cache levels.
        """
        success = True
        for level in CacheLevel:
            success = success and self.clear_level(level)
        
        self.cache_metadata.clear()
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        """
        stats = {}
        
        for level in CacheLevel:
            level_stats = self.cache_stats[level]
            total_requests = level_stats.hits + level_stats.misses
            hit_rate = level_stats.hits / total_requests if total_requests > 0 else 0
            
            stats[level.value] = {
                'hits': level_stats.hits,
                'misses': level_stats.misses,
                'sets': level_stats.sets,
                'deletes': level_stats.deletes,
                'evictions': level_stats.evictions,
                'hit_rate': round(hit_rate * 100, 2),
                'memory_usage_mb': round(level_stats.memory_usage / (1024 * 1024), 2)
            }
        
        # Overall statistics
        total_hits = sum(stats[level]['hits'] for level in stats)
        total_misses = sum(stats[level]['misses'] for level in stats)
        overall_hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        stats['overall'] = {
            'total_keys': len(self.cache_metadata),
            'hit_rate': round(overall_hit_rate * 100, 2),
            'total_memory_usage_mb': sum(stats[level]['memory_usage_mb'] for level in stats if level != 'overall')
        }
        
        return stats
    
    def register_warming_function(self, key: str, func: Callable):
        """
        Register a function for cache warming.
        """
        self.warming_functions[key] = func
    
    def register_invalidation_callback(self, pattern: str, callback: Callable):
        """
        Register callback for cache invalidation events.
        """
        self.invalidation_callbacks[pattern].append(callback)
    
    def cache_function(self, ttl: Optional[int] = None, 
                      key_func: Optional[Callable] = None,
                      tags: List[str] = None):
        """
        Decorator for function result caching.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{self._hash_args(args, kwargs)}"
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl=ttl, tags=tags)
                
                return result
            
            return wrapper
        return decorator
    
    # Private methods
    def _register_middleware(self):
        """Register cache middleware"""
        if not self.app:
            return
        
        @self.app.before_request
        def before_request():
            g.cache_keys_accessed = []
        
        @self.app.after_request
        def after_request(response):
            # Log cache access patterns for analysis
            if hasattr(g, 'cache_keys_accessed'):
                self._analyze_cache_patterns(g.cache_keys_accessed)
            return response
    
    def _get_from_level(self, key: str, level: CacheLevel) -> Any:
        """Get value from specific cache level"""
        try:
            if level == CacheLevel.L1_MEMORY:
                return self.l1_cache.get(key)
            
            elif level == CacheLevel.L2_REDIS and self.l2_cache:
                value = self.l2_cache.get(key)
                if value:
                    return self._deserialize_value(value)
            
        except Exception as e:
            logging.error(f"Error getting from {level.value}: {e}")
        
        return None
    
    def _set_in_level(self, key: str, value: bytes, ttl: int, level: CacheLevel) -> bool:
        """Set value in specific cache level"""
        try:
            if level == CacheLevel.L1_MEMORY:
                # Simple in-memory storage (could be improved with size limits)
                self.l1_cache[key] = self._deserialize_value(value)
                return True
            
            elif level == CacheLevel.L2_REDIS and self.l2_cache:
                return self.l2_cache.setex(key, ttl, value)
            
        except Exception as e:
            logging.error(f"Error setting in {level.value}: {e}")
        
        return False
    
    def _delete_from_level(self, key: str, level: CacheLevel) -> bool:
        """Delete value from specific cache level"""
        try:
            if level == CacheLevel.L1_MEMORY:
                return self.l1_cache.pop(key, None) is not None
            
            elif level == CacheLevel.L2_REDIS and self.l2_cache:
                return bool(self.l2_cache.delete(key))
            
        except Exception as e:
            logging.error(f"Error deleting from {level.value}: {e}")
        
        return False
    
    def _generate_key(self, key: str) -> str:
        """Generate full cache key with prefix"""
        return f"{self.config.cache_key_prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        if not self.config.enable_serialization:
            return str(value).encode()
        
        try:
            # Use pickle for complex objects, JSON for simple ones
            if isinstance(value, (str, int, float, bool, list, dict)):
                return json.dumps(value).encode()
            else:
                return pickle.dumps(value)
        except Exception:
            return str(value).encode()
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from storage"""
        if not self.config.enable_serialization:
            return value.decode() if isinstance(value, bytes) else value
        
        try:
            # Try JSON first, then pickle
            try:
                return json.loads(value.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(value)
        except Exception:
            return value.decode() if isinstance(value, bytes) else value
    
    def _hash_args(self, args: tuple, kwargs: dict) -> str:
        """Generate hash for function arguments"""
        arg_string = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(arg_string.encode()).hexdigest()[:16]
    
    def _record_hit(self, level: CacheLevel):
        """Record cache hit"""
        self.cache_stats[level].hits += 1
    
    def _record_miss(self, level: CacheLevel):
        """Record cache miss"""
        self.cache_stats[level].misses += 1
    
    def _record_set(self, level: CacheLevel):
        """Record cache set"""
        self.cache_stats[level].sets += 1
    
    def _record_delete(self, level: CacheLevel):
        """Record cache delete"""
        self.cache_stats[level].deletes += 1
    
    def _update_access_metadata(self, key: str):
        """Update access metadata for cache entry"""
        if key in self.cache_metadata:
            metadata = self.cache_metadata[key]
            metadata.last_accessed = time.time()
            metadata.access_count += 1
    
    def _update_set_metadata(self, key: str, value: Any, ttl: int, tags: List[str]):
        """Update set metadata for cache entry"""
        now = time.time()
        size_bytes = len(self._serialize_value(value))
        
        self.cache_metadata[key] = CacheEntry(
            key=key,
            value=value,
            ttl=ttl,
            created_at=now,
            last_accessed=now,
            access_count=1,
            size_bytes=size_bytes,
            tags=tags
        )
    
    def _promote_to_higher_levels(self, key: str, value: Any, current_level: CacheLevel, levels: List[CacheLevel]):
        """Promote frequently accessed items to higher cache levels"""
        # Find higher levels
        level_priorities = {CacheLevel.L1_MEMORY: 1, CacheLevel.L2_REDIS: 2, CacheLevel.L3_DATABASE: 3}
        current_priority = level_priorities[current_level]
        
        higher_levels = [level for level in levels if level_priorities[level] < current_priority]
        
        if higher_levels and key in self.cache_metadata:
            metadata = self.cache_metadata[key]
            # Promote if accessed frequently
            if metadata.access_count >= 5:  # Configurable threshold
                serialized_value = self._serialize_value(value)
                for level in higher_levels:
                    self._set_in_level(key, serialized_value, metadata.ttl, level)
    
    def _clear_level_metadata(self, level: CacheLevel):
        """Clear metadata for specific cache level"""
        # This is simplified - in practice, you'd track which level each key is in
        pass
    
    def _analyze_cache_patterns(self, accessed_keys: List[str]):
        """Analyze cache access patterns for optimization"""
        # This could be expanded to provide intelligent cache warming suggestions
        pass