"""
Advanced Caching Service for BDC Platform
Provides multi-level caching, intelligent invalidation, and performance optimization.
"""

import os
import json
import hashlib
import pickle
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
from dataclasses import dataclass, asdict
from threading import Lock
from collections import OrderedDict, defaultdict
import redis
import zlib
import msgpack

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    compression_ratio: float = 1.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed is None:
            self.last_accessed = self.created_at

@dataclass
class CacheStats:
    """Cache statistics"""
    total_entries: int = 0
    total_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    compression_saved_bytes: int = 0
    avg_access_time_ms: float = 0.0
    cache_efficiency: float = 0.0

class CacheService:
    """Advanced multi-level caching service"""
    
    def __init__(self, app=None):
        self.app = app
        self.memory_cache = OrderedDict()
        self.cache_stats = CacheStats()
        self.lock = Lock()
        self.access_times = deque(maxlen=1000)
        self.invalidation_callbacks = defaultdict(list)
        
        # Configuration
        self.config = {
            'memory_max_size': 100 * 1024 * 1024,  # 100MB
            'memory_max_entries': 10000,
            'default_ttl': 3600,  # 1 hour
            'compression_threshold': 1024,  # 1KB
            'enable_compression': True,
            'enable_redis': True,
            'redis_prefix': 'bdc_cache:',
            'serialization': 'msgpack'  # msgpack, pickle, json
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.cache_service = self
        
        # Update config from app
        self.config.update(app.config.get('CACHE_CONFIG', {}))
        
        # Initialize Redis if enabled
        if self.config['enable_redis']:
            try:
                from app.extensions import redis_client
                self.redis_client = redis_client
                logger.info("Redis cache backend initialized")
            except Exception as e:
                logger.warning(f"Redis cache backend not available: {str(e)}")
                self.redis_client = None
        else:
            self.redis_client = None
    
    def get(
        self,
        key: str,
        default: Any = None,
        update_stats: bool = True
    ) -> Any:
        """Get value from cache"""
        start_time = time.time()
        
        try:
            # Try memory cache first
            value = self._get_from_memory(key)
            if value is not None:
                if update_stats:
                    self.cache_stats.hit_count += 1
                    self._update_access_time(time.time() - start_time)
                return value
            
            # Try Redis cache
            if self.redis_client:
                value = self._get_from_redis(key)
                if value is not None:
                    # Promote to memory cache
                    self._set_to_memory(key, value, ttl=300)  # 5 min in memory
                    if update_stats:
                        self.cache_stats.hit_count += 1
                        self._update_access_time(time.time() - start_time)
                    return value
            
            # Cache miss
            if update_stats:
                self.cache_stats.miss_count += 1
                self._update_access_time(time.time() - start_time)
            
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
        compress: Optional[bool] = None
    ) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.config['default_ttl']
            
            # Determine compression
            if compress is None:
                compress = self.config['enable_compression']
            
            # Set in memory cache
            self._set_to_memory(key, value, ttl, tags, compress)
            
            # Set in Redis cache
            if self.redis_client:
                self._set_to_redis(key, value, ttl, tags, compress)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            deleted = False
            
            # Delete from memory cache
            with self.lock:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    deleted = True
            
            # Delete from Redis cache
            if self.redis_client:
                redis_key = self._get_redis_key(key)
                if self.redis_client.delete(redis_key):
                    deleted = True
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def invalidate_by_tags(self, tags: Union[str, List[str]]) -> int:
        """Invalidate cache entries by tags"""
        if isinstance(tags, str):
            tags = [tags]
        
        invalidated = 0
        
        # Invalidate in memory cache
        with self.lock:
            keys_to_delete = []
            for key, entry in self.memory_cache.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                invalidated += 1
        
        # Invalidate in Redis cache
        if self.redis_client:
            for tag in tags:
                tag_key = f"{self.config['redis_prefix']}tag:{tag}"
                keys = self.redis_client.smembers(tag_key)
                if keys:
                    for key in keys:
                        self.redis_client.delete(key)
                        invalidated += 1
                    self.redis_client.delete(tag_key)
        
        # Call invalidation callbacks
        for tag in tags:
            for callback in self.invalidation_callbacks.get(tag, []):
                try:
                    callback(tag)
                except Exception as e:
                    logger.error(f"Invalidation callback error: {str(e)}")
        
        logger.info(f"Invalidated {invalidated} cache entries for tags: {tags}")
        return invalidated
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.memory_cache.clear()
        
        if self.redis_client:
            pattern = f"{self.config['redis_prefix']}*"
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
        
        self.cache_stats.eviction_count += self.cache_stats.total_entries
        self.cache_stats.total_entries = 0
        self.cache_stats.total_size_bytes = 0
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            memory_entries = len(self.memory_cache)
            memory_size = sum(
                entry.size_bytes for entry in self.memory_cache.values()
            )
        
        # Calculate hit rate
        total_requests = self.cache_stats.hit_count + self.cache_stats.miss_count
        hit_rate = (
            (self.cache_stats.hit_count / total_requests * 100)
            if total_requests > 0 else 0
        )
        
        # Calculate compression savings
        compression_ratio = (
            self.cache_stats.compression_saved_bytes /
            (self.cache_stats.total_size_bytes + self.cache_stats.compression_saved_bytes)
            if self.cache_stats.total_size_bytes > 0 else 0
        )
        
        stats = {
            'memory_cache': {
                'entries': memory_entries,
                'size_bytes': memory_size,
                'size_mb': round(memory_size / 1024 / 1024, 2),
                'max_entries': self.config['memory_max_entries'],
                'max_size_mb': round(self.config['memory_max_size'] / 1024 / 1024, 2)
            },
            'performance': {
                'hit_count': self.cache_stats.hit_count,
                'miss_count': self.cache_stats.miss_count,
                'hit_rate_percent': round(hit_rate, 2),
                'avg_access_time_ms': round(self.cache_stats.avg_access_time_ms, 3),
                'eviction_count': self.cache_stats.eviction_count
            },
            'compression': {
                'enabled': self.config['enable_compression'],
                'saved_bytes': self.cache_stats.compression_saved_bytes,
                'saved_mb': round(self.cache_stats.compression_saved_bytes / 1024 / 1024, 2),
                'compression_ratio': round(compression_ratio * 100, 2)
            },
            'redis': {
                'enabled': self.config['enable_redis'],
                'connected': self.redis_client is not None
            }
        }
        
        return stats
    
    def register_invalidation_callback(self, tag: str, callback: Callable):
        """Register callback for cache invalidation"""
        self.invalidation_callbacks[tag].append(callback)
    
    def cached(
        self,
        key_prefix: str = None,
        ttl: int = None,
        tags: List[str] = None,
        key_func: Callable = None,
        compress: bool = None
    ):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_cache_key(
                        key_prefix or func.__name__,
                        args,
                        kwargs
                    )
                
                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache the result
                self.set(cache_key, result, ttl=ttl, tags=tags, compress=compress)
                
                return result
            
            wrapper._cache_key_prefix = key_prefix or func.__name__
            wrapper._cache_tags = tags or []
            
            return wrapper
        return decorator
    
    def _get_from_memory(self, key: str) -> Any:
        """Get value from memory cache"""
        with self.lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                # Check expiration
                if entry.expires_at and entry.expires_at < datetime.utcnow():
                    del self.memory_cache[key]
                    return None
                
                # Update access info
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()
                
                # Move to end (LRU)
                self.memory_cache.move_to_end(key)
                
                return entry.value
        
        return None
    
    def _set_to_memory(
        self,
        key: str,
        value: Any,
        ttl: int,
        tags: List[str] = None,
        compress: bool = True
    ):
        """Set value in memory cache"""
        # Serialize and potentially compress
        serialized, size_bytes, compression_ratio = self._serialize_value(
            value, compress
        )
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl) if ttl else None,
            size_bytes=size_bytes,
            compression_ratio=compression_ratio,
            tags=tags or []
        )
        
        with self.lock:
            # Check size limits and evict if necessary
            self._evict_if_needed(size_bytes)
            
            # Add to cache
            self.memory_cache[key] = entry
            self.cache_stats.total_entries = len(self.memory_cache)
            self.cache_stats.total_size_bytes += size_bytes
            
            if compression_ratio < 1.0:
                saved = int(size_bytes / compression_ratio - size_bytes)
                self.cache_stats.compression_saved_bytes += saved
    
    def _get_from_redis(self, key: str) -> Any:
        """Get value from Redis cache"""
        try:
            redis_key = self._get_redis_key(key)
            data = self.redis_client.get(redis_key)
            
            if data:
                return self._deserialize_value(data)
            
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {str(e)}")
        
        return None
    
    def _set_to_redis(
        self,
        key: str,
        value: Any,
        ttl: int,
        tags: List[str] = None,
        compress: bool = True
    ):
        """Set value in Redis cache"""
        try:
            redis_key = self._get_redis_key(key)
            
            # Serialize value
            serialized, _, _ = self._serialize_value(value, compress)
            
            # Set with expiration
            if ttl:
                self.redis_client.setex(redis_key, ttl, serialized)
            else:
                self.redis_client.set(redis_key, serialized)
            
            # Store tags
            if tags:
                for tag in tags:
                    tag_key = f"{self.config['redis_prefix']}tag:{tag}"
                    self.redis_client.sadd(tag_key, redis_key)
                    if ttl:
                        self.redis_client.expire(tag_key, ttl)
                        
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {str(e)}")
    
    def _serialize_value(
        self,
        value: Any,
        compress: bool
    ) -> tuple[bytes, int, float]:
        """Serialize and optionally compress value"""
        # Serialize based on configured method
        if self.config['serialization'] == 'msgpack':
            serialized = msgpack.packb(value, use_bin_type=True)
        elif self.config['serialization'] == 'pickle':
            serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        else:  # json
            serialized = json.dumps(value).encode('utf-8')
        
        original_size = len(serialized)
        compression_ratio = 1.0
        
        # Compress if enabled and above threshold
        if compress and original_size > self.config['compression_threshold']:
            compressed = zlib.compress(serialized, level=6)
            if len(compressed) < original_size:
                serialized = compressed
                compression_ratio = len(compressed) / original_size
        
        return serialized, len(serialized), compression_ratio
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize and decompress value"""
        # Try decompression
        try:
            data = zlib.decompress(data)
        except:
            pass  # Not compressed
        
        # Deserialize based on configured method
        try:
            if self.config['serialization'] == 'msgpack':
                return msgpack.unpackb(data, raw=False)
            elif self.config['serialization'] == 'pickle':
                return pickle.loads(data)
            else:  # json
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Deserialization error: {str(e)}")
            return None
    
    def _generate_cache_key(
        self,
        prefix: str,
        args: tuple,
        kwargs: dict
    ) -> str:
        """Generate cache key from function arguments"""
        # Create a unique key from args and kwargs
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    def _get_redis_key(self, key: str) -> str:
        """Get Redis key with prefix"""
        return f"{self.config['redis_prefix']}{key}"
    
    def _evict_if_needed(self, new_size: int):
        """Evict entries if cache is full"""
        current_size = sum(
            entry.size_bytes for entry in self.memory_cache.values()
        )
        
        # Check size limit
        while (current_size + new_size > self.config['memory_max_size'] or
               len(self.memory_cache) >= self.config['memory_max_entries']):
            
            if not self.memory_cache:
                break
            
            # Evict least recently used
            key, entry = self.memory_cache.popitem(last=False)
            current_size -= entry.size_bytes
            self.cache_stats.eviction_count += 1
            self.cache_stats.total_size_bytes -= entry.size_bytes
    
    def _update_access_time(self, access_time: float):
        """Update average access time"""
        self.access_times.append(access_time * 1000)  # Convert to ms
        
        if self.access_times:
            self.cache_stats.avg_access_time_ms = (
                sum(self.access_times) / len(self.access_times)
            )

# Global instance
cache_service = CacheService()

# Convenience functions
def cache_get(key: str, default: Any = None) -> Any:
    """Get value from cache"""
    return cache_service.get(key, default)

def cache_set(key: str, value: Any, ttl: Optional[int] = None, tags: Optional[List[str]] = None) -> bool:
    """Set value in cache"""
    return cache_service.set(key, value, ttl, tags)

def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    return cache_service.delete(key)

def cache_invalidate_tags(*tags) -> int:
    """Invalidate cache by tags"""
    return cache_service.invalidate_by_tags(list(tags))