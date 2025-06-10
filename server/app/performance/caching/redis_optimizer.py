"""
Redis Cache Optimizer

Specialized optimization for Redis caching including connection pooling,
pipeline optimization, and Redis-specific performance tuning.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from collections import defaultdict
import redis
from redis.connection import ConnectionPool
from redis.sentinel import Sentinel


@dataclass
class RedisConfig:
    """Redis optimization configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    socket_keepalive_options: Dict = None
    compression_threshold: int = 1024  # Compress values larger than 1KB
    pipeline_size: int = 100
    enable_sentinel: bool = False
    sentinel_hosts: List[Tuple[str, int]] = None
    sentinel_service: str = "mymaster"
    
    def __post_init__(self):
        if self.socket_keepalive_options is None:
            self.socket_keepalive_options = {
                1: 1,  # TCP_KEEPIDLE
                2: 3,  # TCP_KEEPINTVL
                3: 5,  # TCP_KEEPCNT
            }
        if self.sentinel_hosts is None:
            self.sentinel_hosts = [("localhost", 26379)]


@dataclass
class RedisStats:
    """Redis performance statistics"""
    commands_processed: int = 0
    pipeline_commands: int = 0
    compression_saves: int = 0
    memory_usage: int = 0
    hit_rate: float = 0.0
    avg_response_time: float = 0.0
    connection_pool_stats: Dict = None


class RedisOptimizer:
    """
    Advanced Redis optimizer for high-performance caching.
    """
    
    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or RedisConfig()
        self.redis_client = None
        self.connection_pool = None
        self.pipeline_buffer = []
        self.stats = RedisStats()
        self.command_times = []
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with optimization"""
        try:
            if self.config.enable_sentinel:
                self._initialize_sentinel()
            else:
                self._initialize_standalone()
            
            # Test connection
            self.redis_client.ping()
            logging.info("Redis optimizer initialized successfully")
            
        except Exception as e:
            logging.error(f"Redis optimizer initialization failed: {e}")
            raise
    
    def _initialize_standalone(self):
        """Initialize standalone Redis connection"""
        # Create optimized connection pool
        self.connection_pool = ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
            max_connections=self.config.max_connections,
            retry_on_timeout=self.config.retry_on_timeout,
            socket_keepalive=self.config.socket_keepalive,
            socket_keepalive_options=self.config.socket_keepalive_options,
            decode_responses=False  # We handle encoding/decoding
        )
        
        self.redis_client = redis.Redis(connection_pool=self.connection_pool)
    
    def _initialize_sentinel(self):
        """Initialize Redis Sentinel for high availability"""
        sentinel = Sentinel(
            self.config.sentinel_hosts,
            socket_timeout=0.1,
            socket_keepalive=True,
            socket_keepalive_options=self.config.socket_keepalive_options
        )
        
        self.redis_client = sentinel.master_for(
            self.config.sentinel_service,
            socket_timeout=0.1,
            password=self.config.password,
            db=self.config.db
        )
    
    def optimized_set(self, key: str, value: Any, ttl: Optional[int] = None, 
                     compress: bool = True) -> bool:
        """
        Optimized SET operation with compression and pipelining.
        """
        start_time = time.time()
        
        try:
            # Prepare value
            processed_value = self._prepare_value(value, compress)
            
            # Use pipeline for better performance
            pipe = self.redis_client.pipeline()
            
            if ttl:
                pipe.setex(key, ttl, processed_value)
            else:
                pipe.set(key, processed_value)
            
            result = pipe.execute()
            
            # Update statistics
            self._record_command_time(time.time() - start_time)
            self.stats.commands_processed += 1
            
            return bool(result[0])
            
        except Exception as e:
            logging.error(f"Optimized SET failed for key {key}: {e}")
            return False
    
    def optimized_get(self, key: str, decompress: bool = True) -> Any:
        """
        Optimized GET operation with decompression.
        """
        start_time = time.time()
        
        try:
            value = self.redis_client.get(key)
            
            # Update statistics
            self._record_command_time(time.time() - start_time)
            self.stats.commands_processed += 1
            
            if value is None:
                return None
            
            return self._process_retrieved_value(value, decompress)
            
        except Exception as e:
            logging.error(f"Optimized GET failed for key {key}: {e}")
            return None
    
    def batch_set(self, key_value_pairs: Dict[str, Any], ttl: Optional[int] = None,
                  compress: bool = True) -> Dict[str, bool]:
        """
        Batch SET operation using pipeline for better performance.
        """
        results = {}
        
        try:
            pipe = self.redis_client.pipeline()
            
            # Prepare all operations
            for key, value in key_value_pairs.items():
                processed_value = self._prepare_value(value, compress)
                
                if ttl:
                    pipe.setex(key, ttl, processed_value)
                else:
                    pipe.set(key, processed_value)
            
            # Execute pipeline
            pipeline_results = pipe.execute()
            
            # Map results
            for i, key in enumerate(key_value_pairs.keys()):
                results[key] = bool(pipeline_results[i])
            
            # Update statistics
            self.stats.commands_processed += len(key_value_pairs)
            self.stats.pipeline_commands += 1
            
        except Exception as e:
            logging.error(f"Batch SET failed: {e}")
            # Return failure for all keys
            results = {key: False for key in key_value_pairs.keys()}
        
        return results
    
    def batch_get(self, keys: List[str], decompress: bool = True) -> Dict[str, Any]:
        """
        Batch GET operation using MGET for better performance.
        """
        results = {}
        
        try:
            start_time = time.time()
            values = self.redis_client.mget(keys)
            
            # Process results
            for i, key in enumerate(keys):
                value = values[i]
                if value is not None:
                    results[key] = self._process_retrieved_value(value, decompress)
                else:
                    results[key] = None
            
            # Update statistics
            self._record_command_time(time.time() - start_time)
            self.stats.commands_processed += len(keys)
            
        except Exception as e:
            logging.error(f"Batch GET failed: {e}")
            results = {key: None for key in keys}
        
        return results
    
    def optimized_delete(self, keys: Union[str, List[str]]) -> int:
        """
        Optimized DELETE operation.
        """
        if isinstance(keys, str):
            keys = [keys]
        
        try:
            start_time = time.time()
            deleted_count = self.redis_client.delete(*keys)
            
            # Update statistics
            self._record_command_time(time.time() - start_time)
            self.stats.commands_processed += 1
            
            return deleted_count
            
        except Exception as e:
            logging.error(f"Optimized DELETE failed: {e}")
            return 0
    
    def scan_and_process(self, pattern: str, processor_func: callable, 
                        batch_size: int = 1000) -> int:
        """
        Efficiently scan and process keys matching a pattern.
        """
        processed_count = 0
        
        try:
            cursor = 0
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor=cursor, 
                    match=pattern, 
                    count=batch_size
                )
                
                if keys:
                    # Process batch
                    processor_func(keys)
                    processed_count += len(keys)
                
                if cursor == 0:
                    break
            
            logging.info(f"Processed {processed_count} keys matching pattern: {pattern}")
            
        except Exception as e:
            logging.error(f"Scan and process failed: {e}")
        
        return processed_count
    
    def memory_optimization(self) -> Dict[str, Any]:
        """
        Perform Redis memory optimization.
        """
        optimization_results = {
            'expired_keys_cleaned': 0,
            'memory_before': 0,
            'memory_after': 0,
            'optimization_applied': []
        }
        
        try:
            # Get memory usage before optimization
            memory_info = self.redis_client.memory_usage()
            optimization_results['memory_before'] = memory_info if memory_info else 0
            
            # Force expire cleanup
            expired_count = self._cleanup_expired_keys()
            optimization_results['expired_keys_cleaned'] = expired_count
            
            # Suggest memory optimization settings
            config_suggestions = self._analyze_memory_config()
            optimization_results['optimization_applied'] = config_suggestions
            
            # Get memory usage after optimization
            memory_info_after = self.redis_client.memory_usage()
            optimization_results['memory_after'] = memory_info_after if memory_info_after else 0
            
        except Exception as e:
            logging.error(f"Memory optimization failed: {e}")
        
        return optimization_results
    
    def connection_pool_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        """
        if not self.connection_pool:
            return {}
        
        return {
            'max_connections': self.connection_pool.max_connections,
            'created_connections': getattr(self.connection_pool, 'created_connections', 0),
            'available_connections': getattr(self.connection_pool, 'available_connections', 0),
            'in_use_connections': getattr(self.connection_pool, 'in_use_connections', 0)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive Redis performance metrics.
        """
        # Update average response time
        if self.command_times:
            self.stats.avg_response_time = sum(self.command_times) / len(self.command_times)
        
        # Get Redis INFO
        redis_info = {}
        try:
            info = self.redis_client.info()
            redis_info = {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'connected_clients': info.get('connected_clients', 0),
                'maxmemory': info.get('maxmemory', 0),
                'maxmemory_human': info.get('maxmemory_human', '0B')
            }
            
            # Calculate hit rate
            hits = redis_info['keyspace_hits']
            misses = redis_info['keyspace_misses']
            if hits + misses > 0:
                self.stats.hit_rate = hits / (hits + misses) * 100
            
        except Exception as e:
            logging.error(f"Failed to get Redis info: {e}")
        
        return {
            'optimizer_stats': {
                'commands_processed': self.stats.commands_processed,
                'pipeline_commands': self.stats.pipeline_commands,
                'compression_saves': self.stats.compression_saves,
                'avg_response_time_ms': round(self.stats.avg_response_time * 1000, 2),
                'hit_rate_percent': round(self.stats.hit_rate, 2)
            },
            'redis_info': redis_info,
            'connection_pool': self.connection_pool_stats()
        }
    
    def benchmark_operations(self, iterations: int = 1000) -> Dict[str, float]:
        """
        Benchmark Redis operations for performance analysis.
        """
        results = {}
        
        # Benchmark SET operations
        start_time = time.time()
        for i in range(iterations):
            self.redis_client.set(f"benchmark_set_{i}", f"value_{i}")
        set_time = (time.time() - start_time) / iterations
        results['set_avg_ms'] = round(set_time * 1000, 4)
        
        # Benchmark GET operations
        start_time = time.time()
        for i in range(iterations):
            self.redis_client.get(f"benchmark_set_{i}")
        get_time = (time.time() - start_time) / iterations
        results['get_avg_ms'] = round(get_time * 1000, 4)
        
        # Benchmark pipeline operations
        start_time = time.time()
        pipe = self.redis_client.pipeline()
        for i in range(iterations):
            pipe.set(f"benchmark_pipe_{i}", f"value_{i}")
        pipe.execute()
        pipeline_time = (time.time() - start_time) / iterations
        results['pipeline_set_avg_ms'] = round(pipeline_time * 1000, 4)
        
        # Cleanup benchmark keys
        self.scan_and_process("benchmark_*", lambda keys: self.redis_client.delete(*keys))
        
        return results
    
    # Private methods
    def _prepare_value(self, value: Any, compress: bool) -> bytes:
        """Prepare value for storage with optional compression"""
        import json
        import pickle
        import gzip
        
        # Serialize value
        if isinstance(value, (str, int, float, bool)):
            serialized = json.dumps(value).encode()
        else:
            serialized = pickle.dumps(value)
        
        # Compress if enabled and value is large enough
        if compress and len(serialized) > self.config.compression_threshold:
            compressed = gzip.compress(serialized)
            if len(compressed) < len(serialized):
                self.stats.compression_saves += 1
                return b'COMPRESSED:' + compressed
        
        return serialized
    
    def _process_retrieved_value(self, value: bytes, decompress: bool) -> Any:
        """Process retrieved value with optional decompression"""
        import json
        import pickle
        import gzip
        
        # Check if value is compressed
        if decompress and value.startswith(b'COMPRESSED:'):
            try:
                value = gzip.decompress(value[11:])  # Remove 'COMPRESSED:' prefix
            except Exception as e:
                logging.error(f"Decompression failed: {e}")
                return None
        
        # Deserialize value
        try:
            try:
                return json.loads(value.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(value)
        except Exception as e:
            logging.error(f"Deserialization failed: {e}")
            return value.decode() if isinstance(value, bytes) else value
    
    def _record_command_time(self, execution_time: float):
        """Record command execution time"""
        self.command_times.append(execution_time)
        
        # Keep only recent measurements
        if len(self.command_times) > 1000:
            self.command_times = self.command_times[-500:]
    
    def _cleanup_expired_keys(self) -> int:
        """Force cleanup of expired keys"""
        try:
            # This is Redis-specific and may not work on all versions
            result = self.redis_client.execute_command('MEMORY', 'PURGE')
            return 1 if result else 0
        except Exception:
            # Fallback: scan for keys and check TTL
            return 0
    
    def _analyze_memory_config(self) -> List[str]:
        """Analyze and suggest memory configuration optimizations"""
        suggestions = []
        
        try:
            config = self.redis_client.config_get('*memory*')
            
            # Check maxmemory policy
            policy = config.get('maxmemory-policy', 'noeviction')
            if policy == 'noeviction':
                suggestions.append("Consider setting maxmemory-policy to allkeys-lru or volatile-lru")
            
            # Check maxmemory setting
            maxmemory = config.get('maxmemory', '0')
            if maxmemory == '0':
                suggestions.append("Consider setting maxmemory to prevent out-of-memory conditions")
            
        except Exception as e:
            logging.error(f"Memory config analysis failed: {e}")
        
        return suggestions