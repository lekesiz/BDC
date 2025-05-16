"""
Advanced caching strategy implementation
"""
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import time

from app.extensions import cache as cache_service
from app.utils.logging import logger

# Geçici servis sınıfı
class PerformanceMonitor:
    def track_performance(self, operation_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # ms
                logger.info(f"Performance: {operation_name} took {execution_time:.2f}ms")
                return result
            return wrapper
        return decorator

performance_monitor = PerformanceMonitor()

class CacheStrategy:
    """Advanced caching strategy implementation"""
    
    def __init__(self):
        self.cache_policies = {
            'frequent': {
                'ttl': 3600,  # 1 hour
                'refresh_on_hit': True,
                'max_size': 1000
            },
            'moderate': {
                'ttl': 1800,  # 30 minutes
                'refresh_on_hit': False,
                'max_size': 500
            },
            'rare': {
                'ttl': 300,  # 5 minutes
                'refresh_on_hit': False,
                'max_size': 100
            }
        }
        
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'refreshes': 0
        }
        
    def cache_decorator(self, 
                       key_prefix: str,
                       ttl: Optional[int] = None,
                       cache_policy: str = 'moderate',
                       key_generator: Optional[Callable] = None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    cache_key = self._generate_cache_key(key_prefix, args, kwargs)
                    
                # Try to get from cache
                cached_value = self.get_cached_value(cache_key, cache_policy)
                
                if cached_value is not None:
                    self.cache_stats['hits'] += 1
                    return cached_value
                    
                # Cache miss - compute value
                self.cache_stats['misses'] += 1
                result = func(*args, **kwargs)
                
                # Store in cache
                policy = self.cache_policies.get(cache_policy, self.cache_policies['moderate'])
                cache_ttl = ttl or policy['ttl']
                
                self.set_cached_value(cache_key, result, cache_ttl, cache_policy)
                
                return result
                
            return wrapper
        return decorator
        
    def get_cached_value(self, key: str, cache_policy: str = 'moderate') -> Optional[Any]:
        """Get value from cache with policy handling"""
        policy = self.cache_policies.get(cache_policy, self.cache_policies['moderate'])
        
        # Get from cache
        cached_data = cache_service.get(key)
        
        if cached_data is not None:
            # Check if we should refresh TTL on hit
            if policy.get('refresh_on_hit', False):
                cache_service.expire(key, policy['ttl'])
                self.cache_stats['refreshes'] += 1
                
            return cached_data
            
        return None
        
    def set_cached_value(self, key: str, value: Any, ttl: int, 
                        cache_policy: str = 'moderate'):
        """Set value in cache with policy handling"""
        policy = self.cache_policies.get(cache_policy, self.cache_policies['moderate'])
        
        # Check cache size limits
        if self._should_evict(cache_policy):
            self._evict_old_entries(cache_policy)
            
        # Set in cache
        cache_service.set(key, value, expire=ttl)
        
        # Track metadata
        metadata_key = f"{key}:metadata"
        metadata = {
            'created_at': datetime.utcnow().isoformat(),
            'ttl': ttl,
            'policy': cache_policy,
            'access_count': 0
        }
        cache_service.set(metadata_key, metadata, expire=ttl)
        
    def invalidate_cache(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        invalidated_count = cache_service.clear_pattern(pattern)
        logger.info(f"Invalidated {invalidated_count} cache entries matching pattern: {pattern}")
        return invalidated_count
        
    def warm_cache(self, data_loader: Callable, keys: List[str], 
                  cache_policy: str = 'frequent'):
        """Pre-populate cache with frequently accessed data"""
        policy = self.cache_policies.get(cache_policy, self.cache_policies['frequent'])
        warmed_count = 0
        
        for key in keys:
            try:
                # Load data
                data = data_loader(key)
                
                # Cache it
                self.set_cached_value(key, data, policy['ttl'], cache_policy)
                warmed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to warm cache for key {key}: {str(e)}")
                
        logger.info(f"Warmed {warmed_count} cache entries")
        return warmed_count
        
    def implement_cache_aside(self, key: str, data_loader: Callable,
                            ttl: int = 3600) -> Any:
        """Implement cache-aside pattern"""
        # Try to get from cache
        cached_value = cache_service.get(key)
        
        if cached_value is not None:
            self.cache_stats['hits'] += 1
            return cached_value
            
        # Load from data source
        self.cache_stats['misses'] += 1
        value = data_loader()
        
        # Store in cache
        cache_service.set(key, value, expire=ttl)
        
        return value
        
    def implement_write_through(self, key: str, value: Any, 
                              data_writer: Callable, ttl: int = 3600):
        """Implement write-through caching pattern"""
        # Write to data source first
        data_writer(value)
        
        # Then update cache
        cache_service.set(key, value, expire=ttl)
        
    def implement_write_behind(self, key: str, value: Any,
                             data_writer: Callable, ttl: int = 3600):
        """Implement write-behind caching pattern"""
        # Update cache immediately
        cache_service.set(key, value, expire=ttl)
        
        # Schedule write to data source (simplified - in production, use a queue)
        self._schedule_write(key, value, data_writer)
        
    def _schedule_write(self, key: str, value: Any, data_writer: Callable):
        """Schedule asynchronous write to data source"""
        # In production, this would use a task queue like Celery
        try:
            data_writer(value)
        except Exception as e:
            logger.error(f"Failed to write {key} to data source: {str(e)}")
            
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get detailed cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'policies': self.cache_policies
        }
        
    def _generate_cache_key(self, prefix: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key from function arguments"""
        # Create a string representation of arguments
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if hasattr(arg, 'id'):  # Handle model instances
                key_parts.append(f"id:{arg.id}")
            else:
                key_parts.append(str(arg))
                
        # Add keyword arguments
        for k, v in sorted(kwargs.items()):
            if hasattr(v, 'id'):  # Handle model instances
                key_parts.append(f"{k}:id:{v.id}")
            else:
                key_parts.append(f"{k}:{v}")
                
        # Generate hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 250:  # Redis key limit
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
            
        return key_string
        
    def _should_evict(self, cache_policy: str) -> bool:
        """Check if cache eviction is needed"""
        policy = self.cache_policies.get(cache_policy, self.cache_policies['moderate'])
        
        # In production, check actual cache size
        # For now, return False
        return False
        
    def _evict_old_entries(self, cache_policy: str):
        """Evict old cache entries based on policy"""
        policy = self.cache_policies.get(cache_policy, self.cache_policies['moderate'])
        
        # In production, implement LRU or other eviction strategy
        self.cache_stats['evictions'] += 1
        
    @performance_monitor.track_performance('cache_operation')
    def optimize_cache_performance(self):
        """Optimize cache performance based on statistics"""
        stats = self.get_cache_statistics()
        
        # Adjust cache policies based on hit rates
        if stats['hit_rate'] < 50:
            # Low hit rate - consider adjusting TTLs or warming cache
            logger.warning(f"Low cache hit rate: {stats['hit_rate']:.2f}%")
            
        # Monitor cache evictions
        if self.cache_stats['evictions'] > 100:
            logger.warning(f"High eviction rate: {self.cache_stats['evictions']} evictions")
            
    def create_tiered_cache(self, tiers: List[Dict[str, Any]]):
        """Create a tiered caching system"""
        self.cache_tiers = []
        
        for tier in tiers:
            self.cache_tiers.append({
                'name': tier['name'],
                'ttl': tier['ttl'],
                'max_size': tier.get('max_size', 1000),
                'eviction_policy': tier.get('eviction_policy', 'lru')
            })
            
    def get_from_tiered_cache(self, key: str) -> Optional[Any]:
        """Get value from tiered cache system"""
        for tier in self.cache_tiers:
            tier_key = f"{tier['name']}:{key}"
            value = cache_service.get(tier_key)
            
            if value is not None:
                # Promote to higher tier if accessed frequently
                self._promote_to_higher_tier(key, value, tier)
                return value
                
        return None
        
    def _promote_to_higher_tier(self, key: str, value: Any, current_tier: Dict):
        """Promote frequently accessed items to higher tier"""
        current_tier_index = self.cache_tiers.index(current_tier)
        
        if current_tier_index > 0:
            higher_tier = self.cache_tiers[current_tier_index - 1]
            higher_tier_key = f"{higher_tier['name']}:{key}"
            
            cache_service.set(higher_tier_key, value, expire=higher_tier['ttl'])
            
    def implement_cache_clustering(self, nodes: List[str]):
        """Implement cache clustering for distributed caching"""
        # In production, this would configure Redis Cluster or similar
        self.cache_nodes = nodes
        logger.info(f"Configured cache clustering with {len(nodes)} nodes")
        
    def implement_cache_partitioning(self, partitions: int = 16):
        """Implement cache partitioning for better performance"""
        self.cache_partitions = partitions
        
    def get_partition_key(self, key: str) -> str:
        """Get partition key based on hash"""
        key_hash = hashlib.md5(key.encode()).digest()
        partition = int.from_bytes(key_hash[:2], 'big') % self.cache_partitions
        return f"partition:{partition}:{key}"

# Initialize cache strategy
cache_strategy = CacheStrategy() 