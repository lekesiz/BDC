"""
Performance Optimization Module for BDC Application

This module provides comprehensive performance optimization tools including:
- Database query optimization
- Caching strategies
- API response optimization
- Asset optimization
- Performance monitoring and profiling
- Load testing and benchmarking
"""

from .core.optimizer import PerformanceOptimizer
from .database.query_optimizer import QueryOptimizer
from .database.index_manager import IndexManager
from .caching.cache_manager import CacheManager
from .caching.redis_optimizer import RedisOptimizer
from .api.response_optimizer import ResponseOptimizer
from .api.compression_manager import CompressionManager
from .api.pagination_optimizer import PaginationOptimizer
from .monitoring.performance_monitor import PerformanceMonitor
from .monitoring.profiler import Profiler
from .assets.image_optimizer import ImageOptimizer
from .assets.cdn_manager import CDNManager
from .testing.load_tester import LoadTester
from .testing.benchmark_runner import BenchmarkRunner

__all__ = [
    'PerformanceOptimizer',
    'QueryOptimizer',
    'IndexManager',
    'CacheManager',
    'RedisOptimizer',
    'ResponseOptimizer',
    'CompressionManager',
    'PaginationOptimizer',
    'PerformanceMonitor',
    'Profiler',
    'ImageOptimizer',
    'CDNManager',
    'LoadTester',
    'BenchmarkRunner'
]