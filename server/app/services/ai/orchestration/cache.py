"""Result caching and optimization system."""

import json
import hashlib
import logging
import pickle
import gzip
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor


logger = logging.getLogger(__name__)


class CacheStrategy(str, Enum):
    """Cache strategies for different types of data."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on access patterns


class CompressionType(str, Enum):
    """Compression types for cached data."""
    NONE = "none"
    GZIP = "gzip"
    PICKLE = "pickle"
    JSON = "json"


class CacheEntry:
    """Represents a cached entry with metadata."""
    
    def __init__(self,
                 key: str,
                 value: Any,
                 ttl: Optional[int] = None,
                 compression: CompressionType = CompressionType.JSON,
                 tags: Optional[List[str]] = None):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl else None
        self.last_accessed = self.created_at
        self.access_count = 1
        self.compression = compression
        self.tags = tags or []
        self.size_bytes = self._calculate_size()
    
    def _calculate_size(self) -> int:
        """Calculate the size of the cached value."""
        try:
            if self.compression == CompressionType.JSON:
                return len(json.dumps(self.value).encode('utf-8'))
            elif self.compression == CompressionType.PICKLE:
                return len(pickle.dumps(self.value))
            else:
                return len(str(self.value).encode('utf-8'))
        except Exception:
            return 0
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def update_access(self):
        """Update access metadata."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def serialize(self) -> bytes:
        """Serialize the cached value based on compression type."""
        if self.compression == CompressionType.NONE:
            return str(self.value).encode('utf-8')
        elif self.compression == CompressionType.JSON:
            data = json.dumps(self.value).encode('utf-8')
            return gzip.compress(data) if self.compression == CompressionType.GZIP else data
        elif self.compression == CompressionType.PICKLE:
            data = pickle.dumps(self.value)
            return gzip.compress(data) if self.compression == CompressionType.GZIP else data
        elif self.compression == CompressionType.GZIP:
            return gzip.compress(json.dumps(self.value).encode('utf-8'))
        else:
            return json.dumps(self.value).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes, compression: CompressionType) -> Any:
        """Deserialize cached data."""
        if compression == CompressionType.NONE:
            return data.decode('utf-8')
        elif compression == CompressionType.JSON:
            return json.loads(data.decode('utf-8'))
        elif compression == CompressionType.PICKLE:
            return pickle.loads(data)
        elif compression == CompressionType.GZIP:
            decompressed = gzip.decompress(data)
            return json.loads(decompressed.decode('utf-8'))
        else:
            return json.loads(data.decode('utf-8'))


class CacheStats:
    """Cache statistics and metrics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.total_size = 0
        self.entry_count = 0
        self.start_time = datetime.utcnow()
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.hits + self.misses
        return self.hits / total_requests if total_requests > 0 else 0.0
    
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate()
    
    def average_size(self) -> float:
        """Calculate average entry size."""
        return self.total_size / self.entry_count if self.entry_count > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "evictions": self.evictions,
            "hit_rate": self.hit_rate(),
            "miss_rate": self.miss_rate(),
            "total_size": self.total_size,
            "entry_count": self.entry_count,
            "average_size": self.average_size(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }


class ResultCache:
    """Advanced result caching system with optimization features."""
    
    def __init__(self,
                 redis_client,
                 default_ttl: int = 3600,
                 max_size: int = 1000000,  # 1MB
                 strategy: CacheStrategy = CacheStrategy.LRU,
                 compression: CompressionType = CompressionType.JSON):
        """Initialize the cache system."""
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.strategy = strategy
        self.compression = compression
        
        # Cache namespace
        self.cache_prefix = "cache:results:"
        self.metadata_prefix = "cache:meta:"
        self.stats_key = "cache:stats"
        
        # Local cache for frequently accessed items
        self.local_cache: Dict[str, CacheEntry] = {}
        self.local_cache_max_size = 100
        
        # Background cleanup
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.cleanup_interval = 300  # 5 minutes
        
        # Statistics
        self.stats = CacheStats()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        asyncio.create_task(self._periodic_cleanup())
        asyncio.create_task(self._periodic_stats_update())
    
    async def _periodic_cleanup(self):
        """Periodically clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {str(e)}")
    
    async def _periodic_stats_update(self):
        """Periodically update cache statistics."""
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                self._update_stats()
            except Exception as e:
                logger.error(f"Error updating stats: {str(e)}")
    
    def _generate_key(self, key_data: Union[str, Dict[str, Any]]) -> str:
        """Generate a cache key from input data."""
        if isinstance(key_data, str):
            return key_data
        
        # Create deterministic hash from dictionary
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return key_hash
    
    def set(self,
            key: Union[str, Dict[str, Any]],
            value: Any,
            ttl: Optional[int] = None,
            tags: Optional[List[str]] = None,
            compression: Optional[CompressionType] = None) -> bool:
        """Store a value in the cache."""
        try:
            cache_key = self._generate_key(key)
            full_key = self.cache_prefix + cache_key
            ttl = ttl or self.default_ttl
            compression = compression or self.compression
            
            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                ttl=ttl,
                compression=compression,
                tags=tags
            )
            
            # Check size limits
            if entry.size_bytes > self.max_size:
                logger.warning(f"Entry size ({entry.size_bytes}) exceeds max size ({self.max_size})")
                return False
            
            # Serialize and store in Redis
            serialized_data = entry.serialize()
            
            # Store data and metadata separately
            pipe = self.redis_client.pipeline()
            pipe.setex(full_key, ttl, serialized_data)
            pipe.setex(
                self.metadata_prefix + cache_key,
                ttl,
                json.dumps({
                    "created_at": entry.created_at.isoformat(),
                    "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                    "compression": compression.value,
                    "size_bytes": entry.size_bytes,
                    "tags": tags or [],
                    "access_count": 1
                })
            )
            pipe.execute()
            
            # Update local cache
            self._update_local_cache(cache_key, entry)
            
            # Update statistics
            self.stats.sets += 1
            self.stats.total_size += entry.size_bytes
            self.stats.entry_count += 1
            
            logger.debug(f"Cached value with key: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache value: {str(e)}")
            return False
    
    def get(self,
            key: Union[str, Dict[str, Any]],
            default: Any = None) -> Any:
        """Retrieve a value from the cache."""
        try:
            cache_key = self._generate_key(key)
            
            # Check local cache first
            if cache_key in self.local_cache:
                entry = self.local_cache[cache_key]
                if not entry.is_expired():
                    entry.update_access()
                    self.stats.hits += 1
                    return entry.value
                else:
                    # Remove expired entry from local cache
                    del self.local_cache[cache_key]
            
            # Check Redis cache
            full_key = self.cache_prefix + cache_key
            cached_data = self.redis_client.get(full_key)
            
            if cached_data is None:
                self.stats.misses += 1
                return default
            
            # Get metadata
            metadata = self._get_metadata(cache_key)
            if not metadata:
                self.stats.misses += 1
                return default
            
            # Deserialize data
            compression = CompressionType(metadata.get("compression", CompressionType.JSON.value))
            value = CacheEntry.deserialize(cached_data, compression)
            
            # Update access statistics
            self._update_access_stats(cache_key, metadata)
            
            # Update local cache
            entry = CacheEntry(
                key=cache_key,
                value=value,
                compression=compression
            )
            self._update_local_cache(cache_key, entry)
            
            self.stats.hits += 1
            return value
            
        except Exception as e:
            logger.error(f"Error getting cache value: {str(e)}")
            self.stats.misses += 1
            return default
    
    def get_or_set(self,
                   key: Union[str, Dict[str, Any]],
                   func: Callable[[], Any],
                   ttl: Optional[int] = None,
                   tags: Optional[List[str]] = None) -> Any:
        """Get value from cache or set it using the provided function."""
        value = self.get(key)
        if value is not None:
            return value
        
        # Generate value and cache it
        value = func()
        self.set(key, value, ttl=ttl, tags=tags)
        return value
    
    def delete(self, key: Union[str, Dict[str, Any]]) -> bool:
        """Delete a value from the cache."""
        try:
            cache_key = self._generate_key(key)
            full_key = self.cache_prefix + cache_key
            
            # Delete from Redis
            pipe = self.redis_client.pipeline()
            pipe.delete(full_key)
            pipe.delete(self.metadata_prefix + cache_key)
            result = pipe.execute()
            
            # Delete from local cache
            if cache_key in self.local_cache:
                entry = self.local_cache.pop(cache_key)
                self.stats.total_size -= entry.size_bytes
                self.stats.entry_count -= 1
            
            self.stats.deletes += 1
            return bool(result[0])
            
        except Exception as e:
            logger.error(f"Error deleting cache value: {str(e)}")
            return False
    
    def delete_by_tags(self, tags: List[str]) -> int:
        """Delete all entries with specified tags."""
        deleted_count = 0
        
        try:
            # Find all keys with matching tags
            pattern = self.metadata_prefix + "*"
            for key in self.redis_client.scan_iter(match=pattern):
                metadata = json.loads(self.redis_client.get(key))
                entry_tags = set(metadata.get("tags", []))
                
                if any(tag in entry_tags for tag in tags):
                    # Extract cache key and delete
                    cache_key = key.decode().replace(self.metadata_prefix, "")
                    if self.delete(cache_key):
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting by tags: {str(e)}")
            return 0
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            # Delete all cache keys
            cache_pattern = self.cache_prefix + "*"
            meta_pattern = self.metadata_prefix + "*"
            
            for pattern in [cache_pattern, meta_pattern]:
                keys = list(self.redis_client.scan_iter(match=pattern))
                if keys:
                    self.redis_client.delete(*keys)
            
            # Clear local cache
            self.local_cache.clear()
            
            # Reset statistics
            self.stats = CacheStats()
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        cleaned_count = 0
        
        try:
            # Check Redis entries
            pattern = self.metadata_prefix + "*"
            for key in self.redis_client.scan_iter(match=pattern):
                metadata_str = self.redis_client.get(key)
                if not metadata_str:
                    continue
                
                metadata = json.loads(metadata_str)
                expires_at = metadata.get("expires_at")
                
                if expires_at and datetime.fromisoformat(expires_at) < datetime.utcnow():
                    # Entry has expired, delete it
                    cache_key = key.decode().replace(self.metadata_prefix, "")
                    if self.delete(cache_key):
                        cleaned_count += 1
            
            # Clean local cache
            expired_keys = []
            for cache_key, entry in self.local_cache.items():
                if entry.is_expired():
                    expired_keys.append(cache_key)
            
            for cache_key in expired_keys:
                del self.local_cache[cache_key]
                cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired cache entries")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return 0
    
    def evict_lru(self, target_size: int) -> int:
        """Evict least recently used entries to reach target size."""
        evicted_count = 0
        
        try:
            # Get all entries with their access times
            entries = []
            pattern = self.metadata_prefix + "*"
            
            for key in self.redis_client.scan_iter(match=pattern):
                metadata_str = self.redis_client.get(key)
                if not metadata_str:
                    continue
                
                metadata = json.loads(metadata_str)
                cache_key = key.decode().replace(self.metadata_prefix, "")
                
                entries.append({
                    "key": cache_key,
                    "last_accessed": metadata.get("last_accessed", metadata["created_at"]),
                    "size": metadata.get("size_bytes", 0)
                })
            
            # Sort by last accessed time (oldest first)
            entries.sort(key=lambda x: x["last_accessed"])
            
            # Evict entries until we reach target size
            current_size = sum(e["size"] for e in entries)
            
            for entry in entries:
                if current_size <= target_size:
                    break
                
                if self.delete(entry["key"]):
                    current_size -= entry["size"]
                    evicted_count += 1
                    self.stats.evictions += 1
            
            return evicted_count
            
        except Exception as e:
            logger.error(f"Error during LRU eviction: {str(e)}")
            return 0
    
    def _get_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a cache entry."""
        try:
            metadata_str = self.redis_client.get(self.metadata_prefix + cache_key)
            if metadata_str:
                return json.loads(metadata_str)
            return None
        except Exception:
            return None
    
    def _update_access_stats(self, cache_key: str, metadata: Dict[str, Any]):
        """Update access statistics for a cache entry."""
        try:
            metadata["last_accessed"] = datetime.utcnow().isoformat()
            metadata["access_count"] = metadata.get("access_count", 0) + 1
            
            # Update in Redis
            ttl = self.redis_client.ttl(self.metadata_prefix + cache_key)
            if ttl > 0:
                self.redis_client.setex(
                    self.metadata_prefix + cache_key,
                    ttl,
                    json.dumps(metadata)
                )
        except Exception as e:
            logger.error(f"Error updating access stats: {str(e)}")
    
    def _update_local_cache(self, cache_key: str, entry: CacheEntry):
        """Update local cache with size limits."""
        # Remove if already exists
        if cache_key in self.local_cache:
            del self.local_cache[cache_key]
        
        # Check size limit
        if len(self.local_cache) >= self.local_cache_max_size:
            # Remove oldest entry
            oldest_key = min(
                self.local_cache.keys(),
                key=lambda k: self.local_cache[k].last_accessed
            )
            del self.local_cache[oldest_key]
        
        # Add new entry
        self.local_cache[cache_key] = entry
    
    def _update_stats(self):
        """Update cache statistics in Redis."""
        try:
            stats_data = self.stats.to_dict()
            self.redis_client.setex(
                self.stats_key,
                3600,  # 1 hour TTL
                json.dumps(stats_data)
            )
        except Exception as e:
            logger.error(f"Error updating cache stats: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.stats.to_dict()
    
    def optimize(self) -> Dict[str, Any]:
        """Optimize cache performance."""
        optimization_results = {
            "cleaned_expired": 0,
            "evicted_lru": 0,
            "total_entries": 0,
            "total_size": 0
        }
        
        try:
            # Clean expired entries
            optimization_results["cleaned_expired"] = self.cleanup_expired()
            
            # Check if we need to evict entries
            current_size = self._calculate_total_size()
            optimization_results["total_size"] = current_size
            
            if current_size > self.max_size * 0.8:  # 80% threshold
                target_size = int(self.max_size * 0.6)  # Reduce to 60%
                optimization_results["evicted_lru"] = self.evict_lru(target_size)
            
            # Count total entries
            pattern = self.cache_prefix + "*"
            optimization_results["total_entries"] = len(list(
                self.redis_client.scan_iter(match=pattern)
            ))
            
            logger.info(f"Cache optimization completed: {optimization_results}")
            
        except Exception as e:
            logger.error(f"Error during cache optimization: {str(e)}")
        
        return optimization_results
    
    def _calculate_total_size(self) -> int:
        """Calculate total size of all cache entries."""
        total_size = 0
        
        try:
            pattern = self.metadata_prefix + "*"
            for key in self.redis_client.scan_iter(match=pattern):
                metadata_str = self.redis_client.get(key)
                if metadata_str:
                    metadata = json.loads(metadata_str)
                    total_size += metadata.get("size_bytes", 0)
        except Exception as e:
            logger.error(f"Error calculating total size: {str(e)}")
        
        return total_size