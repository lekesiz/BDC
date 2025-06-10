"""
Core Performance Optimizer

Central orchestrator for all performance optimization features.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from flask import Flask, request, g
from ..database.query_optimizer import QueryOptimizer
from ..database.index_manager import IndexManager
from ..caching.cache_manager import CacheManager
from ..api.response_optimizer import ResponseOptimizer
from ..monitoring.performance_monitor import PerformanceMonitor


class OptimizationLevel(Enum):
    BASIC = "basic"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization"""
    level: OptimizationLevel = OptimizationLevel.MODERATE
    enable_query_optimization: bool = True
    enable_caching: bool = True
    enable_response_compression: bool = True
    enable_auto_indexing: bool = True
    enable_monitoring: bool = True
    cache_ttl: int = 3600
    max_query_time: float = 1.0
    max_response_size: int = 1024 * 1024  # 1MB


class PerformanceOptimizer:
    """
    Central performance optimization manager that coordinates all optimization strategies.
    """
    
    def __init__(self, app: Optional[Flask] = None, config: Optional[OptimizationConfig] = None):
        self.app = app
        self.config = config or OptimizationConfig()
        self.query_optimizer = None
        self.index_manager = None
        self.cache_manager = None
        self.response_optimizer = None
        self.performance_monitor = None
        self.optimization_stats = {
            'queries_optimized': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'responses_compressed': 0,
            'avg_response_time': 0.0
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the performance optimizer with Flask app"""
        self.app = app
        
        # Initialize components
        if self.config.enable_query_optimization:
            self.query_optimizer = QueryOptimizer()
        
        if self.config.enable_auto_indexing:
            self.index_manager = IndexManager()
        
        if self.config.enable_caching:
            self.cache_manager = CacheManager(app)
        
        if self.config.enable_response_compression:
            self.response_optimizer = ResponseOptimizer()
        
        if self.config.enable_monitoring:
            self.performance_monitor = PerformanceMonitor()
        
        # Register middleware
        self._register_middleware()
        
        # Store in app extensions
        app.extensions['performance_optimizer'] = self
        
        logging.info("Performance Optimizer initialized successfully")
    
    def _register_middleware(self):
        """Register performance middleware with the Flask app"""
        
        @self.app.before_request
        def before_request():
            g.start_time = time.time()
            if self.performance_monitor:
                self.performance_monitor.start_request_monitoring()
        
        @self.app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                request_duration = time.time() - g.start_time
                
                # Update stats
                self._update_response_time_stats(request_duration)
                
                # Apply response optimization
                if self.response_optimizer:
                    response = self.response_optimizer.optimize_response(response)
                    if response.status_code == 200:
                        self.optimization_stats['responses_compressed'] += 1
                
                # Monitor performance
                if self.performance_monitor:
                    self.performance_monitor.record_request(
                        endpoint=request.endpoint,
                        method=request.method,
                        duration=request_duration,
                        status_code=response.status_code
                    )
                
                # Add performance headers
                response.headers['X-Response-Time'] = f"{request_duration:.3f}s"
                response.headers['X-Optimization-Level'] = self.config.level.value
                
            return response
    
    def optimize_query(self, query: str, params: Optional[Dict] = None) -> str:
        """Optimize a database query"""
        if self.query_optimizer:
            optimized_query = self.query_optimizer.optimize(query, params)
            if optimized_query != query:
                self.optimization_stats['queries_optimized'] += 1
            return optimized_query
        return query
    
    def cache_get(self, key: str) -> Any:
        """Get value from cache"""
        if self.cache_manager:
            value = self.cache_manager.get(key)
            if value is not None:
                self.optimization_stats['cache_hits'] += 1
            else:
                self.optimization_stats['cache_misses'] += 1
            return value
        return None
    
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if self.cache_manager:
            return self.cache_manager.set(key, value, ttl or self.config.cache_ttl)
        return False
    
    def analyze_slow_queries(self) -> List[Dict[str, Any]]:
        """Analyze slow queries and suggest optimizations"""
        if self.query_optimizer:
            return self.query_optimizer.analyze_slow_queries(self.config.max_query_time)
        return []
    
    def suggest_indexes(self) -> List[Dict[str, Any]]:
        """Suggest database indexes for optimization"""
        if self.index_manager:
            return self.index_manager.suggest_indexes()
        return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        metrics = {
            'optimization_stats': self.optimization_stats.copy(),
            'config': {
                'level': self.config.level.value,
                'cache_ttl': self.config.cache_ttl,
                'max_query_time': self.config.max_query_time
            }
        }
        
        if self.performance_monitor:
            metrics['monitoring'] = self.performance_monitor.get_metrics()
        
        if self.cache_manager:
            metrics['cache'] = self.cache_manager.get_stats()
        
        return metrics
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate a comprehensive optimization report"""
        report = {
            'timestamp': time.time(),
            'optimization_level': self.config.level.value,
            'metrics': self.get_performance_metrics(),
            'recommendations': []
        }
        
        # Add recommendations based on metrics
        if self.optimization_stats['cache_misses'] > self.optimization_stats['cache_hits']:
            report['recommendations'].append({
                'type': 'caching',
                'message': 'Consider increasing cache TTL or reviewing cache strategy',
                'priority': 'high'
            })
        
        if self.optimization_stats['avg_response_time'] > 1.0:
            report['recommendations'].append({
                'type': 'response_time',
                'message': 'Average response time is high, consider query optimization',
                'priority': 'high'
            })
        
        # Add slow query recommendations
        slow_queries = self.analyze_slow_queries()
        if slow_queries:
            report['recommendations'].append({
                'type': 'slow_queries',
                'message': f'Found {len(slow_queries)} slow queries requiring optimization',
                'priority': 'high',
                'details': slow_queries
            })
        
        # Add index recommendations
        index_suggestions = self.suggest_indexes()
        if index_suggestions:
            report['recommendations'].append({
                'type': 'indexing',
                'message': f'Found {len(index_suggestions)} index suggestions',
                'priority': 'medium',
                'details': index_suggestions
            })
        
        return report
    
    def _update_response_time_stats(self, duration: float):
        """Update response time statistics"""
        current_avg = self.optimization_stats['avg_response_time']
        total_requests = sum([
            self.optimization_stats['queries_optimized'],
            self.optimization_stats['cache_hits'],
            self.optimization_stats['cache_misses']
        ]) or 1
        
        self.optimization_stats['avg_response_time'] = (
            (current_avg * (total_requests - 1) + duration) / total_requests
        )
    
    def enable_aggressive_optimization(self):
        """Enable aggressive optimization mode"""
        self.config.level = OptimizationLevel.AGGRESSIVE
        self.config.cache_ttl = 7200  # 2 hours
        self.config.max_query_time = 0.5
        logging.info("Aggressive optimization mode enabled")
    
    def enable_basic_optimization(self):
        """Enable basic optimization mode"""
        self.config.level = OptimizationLevel.BASIC
        self.config.cache_ttl = 1800  # 30 minutes
        self.config.max_query_time = 2.0
        logging.info("Basic optimization mode enabled")
    
    def clear_all_caches(self):
        """Clear all caches"""
        if self.cache_manager:
            self.cache_manager.clear_all()
            logging.info("All caches cleared")
    
    def warmup_cache(self, endpoints: List[str]):
        """Warmup cache for specific endpoints"""
        if self.cache_manager:
            for endpoint in endpoints:
                # Trigger cache warmup logic here
                logging.info(f"Warming up cache for endpoint: {endpoint}")