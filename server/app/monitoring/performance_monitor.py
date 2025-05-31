"""
Performance Monitoring System
Implements APM, metrics collection, and performance tracking
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from flask import g, request, current_app
from functools import wraps
import json
from typing import Dict, Any, List, Optional
import statistics

class PerformanceMonitor:
    """Application Performance Monitoring"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = {
            'requests': [],
            'database_queries': [],
            'cache_operations': [],
            'errors': [],
            'system_metrics': []
        }
        self.thresholds = {
            'response_time': 1.0,  # 1 second
            'database_query': 0.1,  # 100ms
            'memory_usage': 80,    # 80%
            'cpu_usage': 70        # 70%
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize performance monitoring with Flask app"""
        self.app = app
        
        # Setup request monitoring
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
        
        # Start background monitoring
        if app.config.get('ENABLE_PERFORMANCE_MONITORING', True):
            self._start_background_monitoring()
    
    def _before_request(self):
        """Track request start time"""
        g.start_time = time.time()
        g.db_query_count = 0
        g.db_query_time = 0
        g.cache_hits = 0
        g.cache_misses = 0
    
    def _after_request(self, response):
        """Track request completion and metrics"""
        if hasattr(g, 'start_time'):
            # Calculate request duration
            duration = time.time() - g.start_time
            
            # Record metrics
            metric = {
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'endpoint': request.endpoint,
                'path': request.path,
                'status_code': response.status_code,
                'duration': duration,
                'db_queries': getattr(g, 'db_query_count', 0),
                'db_time': getattr(g, 'db_query_time', 0),
                'cache_hits': getattr(g, 'cache_hits', 0),
                'cache_misses': getattr(g, 'cache_misses', 0),
                'user_id': getattr(g, 'current_user_id', None)
            }
            
            # Store metric
            self._store_metric('requests', metric)
            
            # Check for slow requests
            if duration > self.thresholds['response_time']:
                self._alert_slow_request(metric)
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            response.headers['X-DB-Queries'] = str(metric['db_queries'])
        
        return response
    
    def _teardown_request(self, exception=None):
        """Clean up request context"""
        if exception:
            self._record_error(exception)
    
    def _store_metric(self, metric_type: str, metric: Dict[str, Any]):
        """Store metric with automatic cleanup"""
        if metric_type in self.metrics:
            self.metrics[metric_type].append(metric)
            
            # Keep only last hour of metrics
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            self.metrics[metric_type] = [
                m for m in self.metrics[metric_type]
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
    
    def _alert_slow_request(self, metric: Dict[str, Any]):
        """Alert on slow requests"""
        self.app.logger.warning(
            f"Slow request detected: {metric['method']} {metric['path']} "
            f"took {metric['duration']:.3f}s (DB: {metric['db_time']:.3f}s)"
        )
    
    def _record_error(self, exception):
        """Record application errors"""
        error_metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': type(exception).__name__,
            'message': str(exception),
            'endpoint': request.endpoint if request else None,
            'path': request.path if request else None,
            'method': request.method if request else None,
            'user_id': getattr(g, 'current_user_id', None)
        }
        
        self._store_metric('errors', error_metric)
    
    def _start_background_monitoring(self):
        """Start background system monitoring"""
        def monitor_system():
            while True:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    system_metric = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available': memory.available,
                        'disk_percent': disk.percent,
                        'disk_free': disk.free
                    }
                    
                    self._store_metric('system_metrics', system_metric)
                    
                    # Check thresholds
                    if cpu_percent > self.thresholds['cpu_usage']:
                        self.app.logger.warning(f"High CPU usage: {cpu_percent}%")
                    
                    if memory.percent > self.thresholds['memory_usage']:
                        self.app.logger.warning(f"High memory usage: {memory.percent}%")
                    
                except Exception as e:
                    self.app.logger.error(f"System monitoring error: {e}")
                
                # Sleep for 30 seconds
                time.sleep(30)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    def get_metrics_summary(self, metric_type: str = None, 
                          minutes: int = 60) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        if metric_type:
            metrics = [
                m for m in self.metrics.get(metric_type, [])
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
            return self._calculate_summary(metric_type, metrics)
        
        # Return all metrics summaries
        summaries = {}
        for m_type in self.metrics:
            metrics = [
                m for m in self.metrics[m_type]
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
            summaries[m_type] = self._calculate_summary(m_type, metrics)
        
        return summaries
    
    def _calculate_summary(self, metric_type: str, 
                          metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics"""
        if not metrics:
            return {'count': 0}
        
        summary = {'count': len(metrics)}
        
        if metric_type == 'requests':
            durations = [m['duration'] for m in metrics]
            summary.update({
                'avg_duration': statistics.mean(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'p50_duration': statistics.median(durations),
                'p95_duration': self._percentile(durations, 95),
                'p99_duration': self._percentile(durations, 99),
                'total_db_queries': sum(m['db_queries'] for m in metrics),
                'avg_db_queries': statistics.mean([m['db_queries'] for m in metrics]),
                'cache_hit_rate': self._calculate_cache_hit_rate(metrics),
                'error_rate': self._calculate_error_rate(metrics),
                'requests_per_minute': len(metrics) / (minutes / 60)
            })
        
        elif metric_type == 'system_metrics':
            summary.update({
                'avg_cpu': statistics.mean([m['cpu_percent'] for m in metrics]),
                'max_cpu': max(m['cpu_percent'] for m in metrics),
                'avg_memory': statistics.mean([m['memory_percent'] for m in metrics]),
                'max_memory': max(m['memory_percent'] for m in metrics),
                'current_memory_available': metrics[-1]['memory_available'] if metrics else 0,
                'current_disk_free': metrics[-1]['disk_free'] if metrics else 0
            })
        
        elif metric_type == 'errors':
            error_types = {}
            for error in metrics:
                error_type = error['type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            summary.update({
                'error_types': error_types,
                'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
            })
        
        return summary
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _calculate_cache_hit_rate(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate cache hit rate from metrics"""
        total_hits = sum(m.get('cache_hits', 0) for m in metrics)
        total_misses = sum(m.get('cache_misses', 0) for m in metrics)
        
        total_requests = total_hits + total_misses
        if total_requests == 0:
            return 0
        
        return (total_hits / total_requests) * 100
    
    def _calculate_error_rate(self, metrics: List[Dict[str, Any]]) -> float:
        """Calculate error rate from metrics"""
        error_count = sum(1 for m in metrics if m['status_code'] >= 500)
        if len(metrics) == 0:
            return 0
        
        return (error_count / len(metrics)) * 100

def monitor_performance(name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record successful execution
                duration = time.time() - start_time
                
                if hasattr(current_app, 'performance_monitor'):
                    metric = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'function': name or func.__name__,
                        'duration': duration,
                        'success': True
                    }
                    current_app.performance_monitor._store_metric('functions', metric)
                
                return result
            
            except Exception as e:
                # Record failed execution
                duration = time.time() - start_time
                
                if hasattr(current_app, 'performance_monitor'):
                    metric = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'function': name or func.__name__,
                        'duration': duration,
                        'success': False,
                        'error': str(e)
                    }
                    current_app.performance_monitor._store_metric('functions', metric)
                
                raise
        
        return wrapper
    return decorator

class DatabaseQueryMonitor:
    """Monitor database query performance"""
    
    @staticmethod
    def record_query(query: str, duration: float):
        """Record database query execution"""
        if hasattr(g, 'db_query_count'):
            g.db_query_count += 1
            g.db_query_time += duration
        
        # Log slow queries
        if duration > 0.1:  # 100ms
            current_app.logger.warning(
                f"Slow query ({duration:.3f}s): {query[:100]}..."
            )

class CacheMonitor:
    """Monitor cache performance"""
    
    @staticmethod
    def record_hit():
        """Record cache hit"""
        if hasattr(g, 'cache_hits'):
            g.cache_hits += 1
    
    @staticmethod
    def record_miss():
        """Record cache miss"""
        if hasattr(g, 'cache_misses'):
            g.cache_misses += 1

# Health check endpoint data
def get_health_metrics() -> Dict[str, Any]:
    """Get health check metrics"""
    monitor = current_app.extensions.get('performance_monitor')
    
    if not monitor:
        return {'status': 'unknown'}
    
    # Get recent metrics
    summary = monitor.get_metrics_summary(minutes=5)
    
    # Determine health status
    status = 'healthy'
    issues = []
    
    # Check response times
    if summary.get('requests', {}).get('p95_duration', 0) > 2.0:
        status = 'degraded'
        issues.append('High response times')
    
    # Check error rate
    if summary.get('requests', {}).get('error_rate', 0) > 5:
        status = 'unhealthy'
        issues.append('High error rate')
    
    # Check system resources
    system = summary.get('system_metrics', {})
    if system.get('avg_cpu', 0) > 80:
        status = 'degraded'
        issues.append('High CPU usage')
    
    if system.get('avg_memory', 0) > 85:
        status = 'degraded'
        issues.append('High memory usage')
    
    return {
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'issues': issues,
        'metrics': {
            'response_time_p95': summary.get('requests', {}).get('p95_duration', 0),
            'error_rate': summary.get('requests', {}).get('error_rate', 0),
            'requests_per_minute': summary.get('requests', {}).get('requests_per_minute', 0),
            'cpu_usage': system.get('avg_cpu', 0),
            'memory_usage': system.get('avg_memory', 0)
        }
    }