import os
import time
import logging
import psutil
import json
from datetime import datetime
from typing import Dict, List, Optional
from functools import wraps
from flask import Flask, request, g
from prometheus_client import Counter, Gauge, Histogram, generate_latest
import redis
from dataclasses import dataclass, asdict

from app.utils.logging import logger

# Prometheus metrics
request_count = Counter('app_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('app_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
active_users = Gauge('app_active_users', 'Number of active users')
db_connections = Gauge('app_db_connections', 'Number of database connections')
cache_hits = Counter('app_cache_hits_total', 'Cache hit count', ['cache_type'])
cache_misses = Counter('app_cache_misses_total', 'Cache miss count', ['cache_type'])
error_count = Counter('app_errors_total', 'Total application errors', ['error_type'])

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict
    process_count: int
    thread_count: int

class ApplicationMonitor:
    """Application monitoring and metrics collection"""
    
    def __init__(self, app: Optional[Flask] = None, redis_client: Optional[redis.Redis] = None):
        self.app = app
        self.redis_client = redis_client
        self.start_time = time.time()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize monitoring for Flask app"""
        self.app = app
        
        # Register before/after request handlers
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.errorhandler(Exception)(self._handle_error)
        
        # Add metrics endpoint
        @app.route('/metrics')
        def metrics():
            return generate_latest()
    
    def _before_request(self):
        """Log request start"""
        g.start_time = time.time()
        g.request_id = self._generate_request_id()
        
        logger.info(f"Request started: {request.method} {request.path} [{g.request_id}]")
    
    def _after_request(self, response):
        """Log request completion and metrics"""
        duration = time.time() - g.start_time
        
        # Record metrics
        request_count.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown'
        ).observe(duration)
        
        logger.info(
            f"Request completed: {request.method} {request.path} "
            f"[{response.status_code}] [{duration:.3f}s] [{g.request_id}]"
        )
        
        return response
    
    def _handle_error(self, error):
        """Log errors and record metrics"""
        error_type = type(error).__name__
        error_count.labels(error_type=error_type).inc()
        
        logger.error(
            f"Error in request {request.method} {request.path}: {error}",
            exc_info=True
        )
        
        return {'error': str(error)}, 500
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        process = psutil.Process()
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_usage=disk.percent,
            network_io={
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            process_count=len(psutil.pids()),
            thread_count=process.num_threads()
        )
    
    def record_cache_hit(self, cache_type: str = 'redis'):
        """Record cache hit"""
        cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str = 'redis'):
        """Record cache miss"""
        cache_misses.labels(cache_type=cache_type).inc()
    
    def update_active_users(self, count: int):
        """Update active users gauge"""
        active_users.set(count)
    
    def update_db_connections(self, count: int):
        """Update database connections gauge"""
        db_connections.set(count)
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time
    
    def get_health_status(self) -> Dict:
        """Get application health status"""
        try:
            system_metrics = self.collect_system_metrics()
            
            # Check database connection
            db_healthy = self._check_database()
            
            # Check cache connection
            cache_healthy = self._check_cache()
            
            # Overall health
            healthy = all([
                db_healthy,
                cache_healthy,
                system_metrics.cpu_percent < 90,
                system_metrics.memory_percent < 90,
                system_metrics.disk_usage < 90
            ])
            
            return {
                'status': 'healthy' if healthy else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': self.get_uptime(),
                'checks': {
                    'database': 'ok' if db_healthy else 'error',
                    'cache': 'ok' if cache_healthy else 'error',
                    'cpu': 'ok' if system_metrics.cpu_percent < 90 else 'warning',
                    'memory': 'ok' if system_metrics.memory_percent < 90 else 'warning',
                    'disk': 'ok' if system_metrics.disk_usage < 90 else 'warning'
                },
                'metrics': asdict(system_metrics)
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            if self.app:
                from app.extensions import db
                db.session.execute('SELECT 1')
                return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
        return False
    
    def _check_cache(self) -> bool:
        """Check cache connectivity"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception as e:
            logger.error(f"Cache check failed: {e}")
        return False
    
    def performance_monitor(self, func):
        """Decorator to monitor function performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"{func.__name__} completed in {duration:.3f}s")
                
                # Record metric if it's a known function
                if hasattr(func, '__name__'):
                    request_duration.labels(
                        method='function',
                        endpoint=func.__name__
                    ).observe(duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_count.labels(error_type=type(e).__name__).inc()
                
                logger.error(
                    f"{func.__name__} failed after {duration:.3f}s: {e}",
                    exc_info=True
                )
                raise
        
        return wrapper


class PerformanceProfiler:
    """Performance profiling utilities"""
    
    def __init__(self):
        self.profiles = {}
    
    def profile_function(self, func):
        """Profile function execution"""
        import cProfile
        import pstats
        from io import StringIO
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func()
        finally:
            profiler.disable()
            
            # Generate stats
            stream = StringIO()
            stats = pstats.Stats(profiler, stream=stream)
            stats.sort_stats('cumulative')
            stats.print_stats(20)  # Top 20 functions
            
            profile_data = stream.getvalue()
            self.profiles[func.__name__] = profile_data
            
        return result
    
    def get_profile(self, function_name: str) -> Optional[str]:
        """Get profile data for function"""
        return self.profiles.get(function_name)
    
    def save_profiles(self, filepath: str):
        """Save profiles to file"""
        with open(filepath, 'w') as f:
            json.dump(self.profiles, f, indent=2)


class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.metrics_key_prefix = "metrics:"
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """Record a metric value"""
        timestamp = int(time.time())
        key = f"{self.metrics_key_prefix}{metric_name}:{timestamp}"
        
        data = {
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        }
        
        # Store in Redis with 24 hour expiration
        self.redis_client.setex(key, 86400, json.dumps(data))
        
        # Add to sorted set for time-based queries
        self.redis_client.zadd(
            f"{self.metrics_key_prefix}{metric_name}:timeline",
            {key: timestamp}
        )
    
    def get_metrics(self, metric_name: str, start_time: int, end_time: int) -> List[Dict]:
        """Get metrics within time range"""
        timeline_key = f"{self.metrics_key_prefix}{metric_name}:timeline"
        
        # Get keys within time range
        keys = self.redis_client.zrangebyscore(
            timeline_key,
            start_time,
            end_time
        )
        
        metrics = []
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                metrics.append(json.loads(data))
        
        return metrics
    
    def aggregate_metrics(self, metric_name: str, start_time: int, end_time: int, 
                         aggregation: str = 'avg') -> float:
        """Aggregate metrics within time range"""
        metrics = self.get_metrics(metric_name, start_time, end_time)
        
        if not metrics:
            return 0.0
        
        values = [m['value'] for m in metrics]
        
        if aggregation == 'avg':
            return sum(values) / len(values)
        elif aggregation == 'sum':
            return sum(values)
        elif aggregation == 'max':
            return max(values)
        elif aggregation == 'min':
            return min(values)
        elif aggregation == 'count':
            return len(values)
        
        return 0.0


# Health check endpoint
def create_health_endpoint(app: Flask, monitor: ApplicationMonitor):
    """Create health check endpoint"""
    @app.route('/health')
    def health():
        return monitor.get_health_status()


if __name__ == "__main__":
    # Example usage
    app = Flask(__name__)
    monitor = ApplicationMonitor(app)
    
    # Example endpoint with monitoring
    @app.route('/api/example')
    @monitor.performance_monitor
    def example_endpoint():
        time.sleep(0.1)  # Simulate work
        return {'status': 'ok'}
    
    # Create health endpoint
    create_health_endpoint(app, monitor)
    
    # Run app
    app.run(debug=True) 