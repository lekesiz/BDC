"""
Performance Optimization Service for BDC Platform
Provides query optimization, resource pooling, and performance monitoring.
"""

import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from functools import wraps, lru_cache
from collections import defaultdict, deque
from dataclasses import dataclass, field
from sqlalchemy import event, text
from sqlalchemy.orm import Query
from sqlalchemy.pool import QueuePool
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import psutil
import gc

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query: str
    execution_time: float
    rows_returned: int
    timestamp: datetime
    explain_plan: Optional[str] = None
    optimized: bool = False

@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read: float
    disk_io_write: float
    active_connections: int
    query_count: int
    cache_hit_rate: float
    avg_response_time: float

class PerformanceOptimizer:
    """Comprehensive performance optimization service"""
    
    def __init__(self, app=None):
        self.app = app
        self.query_metrics = deque(maxlen=10000)
        self.performance_metrics = deque(maxlen=1000)
        self.slow_query_threshold = 1.0  # seconds
        self.optimization_rules = []
        self.resource_pools = {}
        self.monitoring_enabled = True
        self._lock = threading.Lock()
        
        # Thread pools
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        
        # Query cache
        self.query_cache = {}
        self.cache_stats = defaultdict(int)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.performance_optimizer = self
        
        # Configure database connection pooling
        self._configure_db_pooling()
        
        # Register query listeners
        self._register_query_listeners()
        
        # Start monitoring
        if self.monitoring_enabled:
            self._start_monitoring()
    
    def _configure_db_pooling(self):
        """Configure database connection pooling"""
        if hasattr(self.app, 'config'):
            # Update SQLAlchemy engine options
            engine_options = {
                'pool_size': 20,
                'max_overflow': 40,
                'pool_timeout': 30,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                'echo_pool': self.app.debug
            }
            
            self.app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {}).update(engine_options)
            
            logger.info("Database connection pooling configured")
    
    def _register_query_listeners(self):
        """Register SQLAlchemy query listeners"""
        try:
            from app import db
            
            @event.listens_for(db.engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                conn.info.setdefault('query_start_time', []).append(time.time())
                conn.info.setdefault('current_query', []).append(statement)
            
            @event.listens_for(db.engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                total_time = time.time() - conn.info['query_start_time'].pop(-1)
                query = conn.info['current_query'].pop(-1)
                
                # Record metrics
                metrics = QueryMetrics(
                    query=query,
                    execution_time=total_time,
                    rows_returned=cursor.rowcount if cursor.rowcount > 0 else 0,
                    timestamp=datetime.utcnow()
                )
                
                self._record_query_metrics(metrics)
                
        except Exception as e:
            logger.error(f"Failed to register query listeners: {str(e)}")
    
    def _record_query_metrics(self, metrics: QueryMetrics):
        """Record query performance metrics"""
        with self._lock:
            self.query_metrics.append(metrics)
            
            # Check for slow queries
            if metrics.execution_time > self.slow_query_threshold:
                self._handle_slow_query(metrics)
            
            # Update cache stats
            self.cache_stats['total_queries'] += 1
    
    def _handle_slow_query(self, metrics: QueryMetrics):
        """Handle slow query detection"""
        logger.warning(
            f"Slow query detected ({metrics.execution_time:.2f}s): "
            f"{metrics.query[:100]}..."
        )
        
        # Try to optimize the query
        optimized_query = self._optimize_query(metrics.query)
        if optimized_query != metrics.query:
            metrics.optimized = True
            logger.info(f"Query optimized: {optimized_query[:100]}...")
    
    def _optimize_query(self, query: str) -> str:
        """Apply query optimization rules"""
        optimized = query
        
        for rule in self.optimization_rules:
            optimized = rule(optimized)
        
        return optimized
    
    def _start_monitoring(self):
        """Start performance monitoring"""
        def monitor():
            while self.monitoring_enabled:
                try:
                    metrics = self._collect_performance_metrics()
                    with self._lock:
                        self.performance_metrics.append(metrics)
                    
                    # Check for performance issues
                    self._check_performance_thresholds(metrics)
                    
                except Exception as e:
                    logger.error(f"Performance monitoring error: {str(e)}")
                
                time.sleep(60)  # Monitor every minute
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        
        # Database metrics
        active_connections = self._get_active_db_connections()
        
        # Cache metrics
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        # Response time metrics
        avg_response_time = self._calculate_avg_response_time()
        
        return PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read=disk_io.read_bytes if disk_io else 0,
            disk_io_write=disk_io.write_bytes if disk_io else 0,
            active_connections=active_connections,
            query_count=len(self.query_metrics),
            cache_hit_rate=cache_hit_rate,
            avg_response_time=avg_response_time
        )
    
    def _get_active_db_connections(self) -> int:
        """Get number of active database connections"""
        try:
            from app import db
            return db.engine.pool.checkedout()
        except:
            return 0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        hits = self.cache_stats.get('cache_hits', 0)
        misses = self.cache_stats.get('cache_misses', 0)
        total = hits + misses
        
        return (hits / total * 100) if total > 0 else 0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.query_metrics:
            return 0
        
        recent_queries = list(self.query_metrics)[-100:]  # Last 100 queries
        total_time = sum(q.execution_time for q in recent_queries)
        
        return (total_time / len(recent_queries)) * 1000  # Convert to ms
    
    def _check_performance_thresholds(self, metrics: PerformanceMetrics):
        """Check performance thresholds and trigger alerts"""
        # CPU threshold
        if metrics.cpu_percent > 80:
            logger.warning(f"High CPU usage: {metrics.cpu_percent}%")
            self._trigger_performance_optimization('cpu')
        
        # Memory threshold
        if metrics.memory_percent > 85:
            logger.warning(f"High memory usage: {metrics.memory_percent}%")
            self._trigger_performance_optimization('memory')
        
        # Query performance
        if metrics.avg_response_time > 500:  # 500ms
            logger.warning(f"High average response time: {metrics.avg_response_time}ms")
            self._trigger_performance_optimization('query')
    
    def _trigger_performance_optimization(self, optimization_type: str):
        """Trigger specific performance optimization"""
        if optimization_type == 'cpu':
            # Reduce thread pool size temporarily
            self.thread_pool._max_workers = max(2, self.thread_pool._max_workers - 2)
        
        elif optimization_type == 'memory':
            # Trigger garbage collection
            gc.collect()
            
            # Clear caches
            self._clear_caches()
        
        elif optimization_type == 'query':
            # Analyze and optimize slow queries
            self._analyze_slow_queries()
    
    def optimize_query_performance(self, query: Query) -> Query:
        """Optimize SQLAlchemy query"""
        # Add query hints
        query = query.execution_options(synchronize_session=False)
        
        # Enable query result caching
        query = query.options(
            # Add specific optimization options based on query type
        )
        
        return query
    
    def cached_query(self, ttl: int = 300):
        """Decorator for caching query results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_query_cache_key(func, args, kwargs)
                
                # Check cache
                cached_result = self.query_cache.get(cache_key)
                if cached_result and cached_result['expires'] > datetime.utcnow():
                    self.cache_stats['cache_hits'] += 1
                    return cached_result['data']
                
                # Execute query
                self.cache_stats['cache_misses'] += 1
                result = func(*args, **kwargs)
                
                # Cache result
                self.query_cache[cache_key] = {
                    'data': result,
                    'expires': datetime.utcnow() + timedelta(seconds=ttl)
                }
                
                return result
            
            return wrapper
        return decorator
    
    def batch_operation(self, batch_size: int = 100):
        """Decorator for batch processing operations"""
        def decorator(func):
            @wraps(func)
            def wrapper(items, *args, **kwargs):
                results = []
                
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    batch_results = func(batch, *args, **kwargs)
                    results.extend(batch_results)
                
                return results
            
            return wrapper
        return decorator
    
    def async_task(self, executor='thread'):
        """Decorator for running tasks asynchronously"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if executor == 'thread':
                    future = self.thread_pool.submit(func, *args, **kwargs)
                elif executor == 'process':
                    future = self.process_pool.submit(func, *args, **kwargs)
                else:
                    raise ValueError(f"Unknown executor: {executor}")
                
                return future
            
            return wrapper
        return decorator
    
    @lru_cache(maxsize=1000)
    def _generate_query_cache_key(self, func, args, kwargs) -> str:
        """Generate cache key for query"""
        import hashlib
        import json
        
        key_data = {
            'func': func.__name__,
            'args': str(args),
            'kwargs': json.dumps(kwargs, sort_keys=True, default=str)
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _clear_caches(self):
        """Clear all caches to free memory"""
        # Clear query cache
        expired_keys = []
        now = datetime.utcnow()
        
        for key, cached in self.query_cache.items():
            if cached['expires'] < now:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.query_cache[key]
        
        # Clear LRU caches
        self._generate_query_cache_key.cache_clear()
        
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")
    
    def _analyze_slow_queries(self):
        """Analyze slow queries and suggest optimizations"""
        slow_queries = [
            q for q in self.query_metrics
            if q.execution_time > self.slow_query_threshold
        ]
        
        if not slow_queries:
            return
        
        # Group by query pattern
        query_patterns = defaultdict(list)
        for query in slow_queries:
            pattern = self._extract_query_pattern(query.query)
            query_patterns[pattern].append(query)
        
        # Generate optimization suggestions
        for pattern, queries in query_patterns.items():
            avg_time = sum(q.execution_time for q in queries) / len(queries)
            logger.info(
                f"Slow query pattern detected ({len(queries)} occurrences, "
                f"avg time: {avg_time:.2f}s): {pattern[:100]}..."
            )
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract query pattern for grouping"""
        # Simple pattern extraction - can be enhanced
        import re
        
        # Remove values from WHERE clauses
        pattern = re.sub(r'=\s*\'[^\']+\'', '= ?', query)
        pattern = re.sub(r'=\s*\d+', '= ?', pattern)
        
        # Remove LIMIT values
        pattern = re.sub(r'LIMIT\s+\d+', 'LIMIT ?', pattern)
        
        return pattern
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        with self._lock:
            # Query statistics
            total_queries = len(self.query_metrics)
            slow_queries = [
                q for q in self.query_metrics
                if q.execution_time > self.slow_query_threshold
            ]
            
            # System metrics
            latest_metrics = (
                self.performance_metrics[-1]
                if self.performance_metrics else None
            )
            
            # Cache statistics
            cache_hit_rate = self._calculate_cache_hit_rate()
            
            return {
                'query_performance': {
                    'total_queries': total_queries,
                    'slow_queries': len(slow_queries),
                    'slow_query_threshold': self.slow_query_threshold,
                    'avg_query_time': self._calculate_avg_response_time(),
                    'optimized_queries': sum(1 for q in self.query_metrics if q.optimized)
                },
                'system_performance': {
                    'cpu_percent': latest_metrics.cpu_percent if latest_metrics else 0,
                    'memory_percent': latest_metrics.memory_percent if latest_metrics else 0,
                    'active_connections': latest_metrics.active_connections if latest_metrics else 0,
                    'thread_pool_size': self.thread_pool._max_workers,
                    'process_pool_size': self.process_pool._max_workers
                },
                'cache_performance': {
                    'hit_rate': cache_hit_rate,
                    'total_hits': self.cache_stats['cache_hits'],
                    'total_misses': self.cache_stats['cache_misses'],
                    'cache_size': len(self.query_cache)
                },
                'recommendations': self._generate_recommendations()
            }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check cache hit rate
        hit_rate = self._calculate_cache_hit_rate()
        if hit_rate < 60:
            recommendations.append(
                f"Low cache hit rate ({hit_rate:.1f}%). Consider increasing cache TTL or size."
            )
        
        # Check slow queries
        slow_queries = [
            q for q in self.query_metrics
            if q.execution_time > self.slow_query_threshold
        ]
        if len(slow_queries) > len(self.query_metrics) * 0.1:
            recommendations.append(
                "More than 10% of queries are slow. Review query optimization and indexing."
            )
        
        # Check system resources
        if self.performance_metrics:
            latest = self.performance_metrics[-1]
            if latest.cpu_percent > 70:
                recommendations.append(
                    "High CPU usage detected. Consider scaling horizontally or optimizing algorithms."
                )
            if latest.memory_percent > 80:
                recommendations.append(
                    "High memory usage detected. Review memory allocations and caching strategy."
                )
        
        return recommendations
    
    def register_optimization_rule(self, rule: Callable[[str], str]):
        """Register a query optimization rule"""
        self.optimization_rules.append(rule)
    
    def shutdown(self):
        """Shutdown performance optimizer"""
        self.monitoring_enabled = False
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logger.info("Performance optimizer shutdown complete")

# Global instance
performance_optimizer = PerformanceOptimizer()

# Convenience decorators
cached_query = performance_optimizer.cached_query
batch_operation = performance_optimizer.batch_operation
async_task = performance_optimizer.async_task