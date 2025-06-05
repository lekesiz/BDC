"""
Performance metrics collection for BDC application
"""
import time
import psutil
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import contextmanager
import threading

from flask import Flask, request, g
import redis
import numpy as np

logger = logging.getLogger(__name__)


class PerformanceCollector:
    """Collect and analyze performance metrics"""
    
    def __init__(self, app: Optional[Flask] = None,
                 redis_client: Optional[redis.Redis] = None):
        self.app = app
        self.redis_client = redis_client
        
        # Metric storage
        self.request_metrics = deque(maxlen=10000)
        self.response_times = defaultdict(lambda: deque(maxlen=1000))
        self.endpoint_metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'errors': 0,
            'success_rate': 1.0
        })
        
        # System metrics
        self.system_metrics = deque(maxlen=1000)
        self.process_metrics = deque(maxlen=1000)
        
        # Thresholds for alerting
        self.thresholds = {
            'response_time': 1000,  # 1 second
            'cpu_percent': 80,
            'memory_percent': 85,
            'error_rate': 0.05  # 5%
        }
        
        # Background monitoring
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        if app:
            self.init_app(app, redis_client)
    
    def init_app(self, app: Flask, redis_client: redis.Redis):
        """Initialize with Flask app"""
        self.app = app
        self.redis_client = redis_client
        
        # Register request hooks
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Start background monitoring
        self.start_monitoring()
    
    def before_request(self):
        """Track request start time"""
        g.start_time = time.time()
        g.request_metrics = {
            'start_time': g.start_time,
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args),
            'user_agent': request.headers.get('User-Agent'),
            'remote_addr': request.remote_addr
        }
    
    def after_request(self, response):
        """Track request completion"""
        if hasattr(g, 'start_time'):
            elapsed_time = (time.time() - g.start_time) * 1000  # milliseconds
            
            # Update request metrics
            g.request_metrics.update({
                'end_time': time.time(),
                'elapsed_time': elapsed_time,
                'response_status': response.status_code,
                'response_size': len(response.get_data()),
                'successful': 200 <= response.status_code < 400
            })
            
            # Store metrics
            self._store_request_metrics(g.request_metrics)
            
            # Check for slow requests
            if elapsed_time > self.thresholds['response_time']:
                self._handle_slow_request(g.request_metrics)
        
        return response
    
    def _store_request_metrics(self, metrics: Dict[str, Any]):
        """Store request metrics"""
        # Add to in-memory storage
        self.request_metrics.append(metrics)
        
        # Update endpoint metrics
        endpoint = metrics.get('endpoint', 'unknown')
        self.endpoint_metrics[endpoint]['count'] += 1
        self.endpoint_metrics[endpoint]['total_time'] += metrics['elapsed_time']
        
        if not metrics['successful']:
            self.endpoint_metrics[endpoint]['errors'] += 1
        
        # Calculate success rate
        endpoint_data = self.endpoint_metrics[endpoint]
        endpoint_data['success_rate'] = (
            (endpoint_data['count'] - endpoint_data['errors']) / 
            endpoint_data['count']
        )
        
        # Update response time history
        self.response_times[endpoint].append(metrics['elapsed_time'])
        
        # Store in Redis for distributed metrics
        if self.redis_client:
            self._store_redis_metrics(metrics)
    
    def _store_redis_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in Redis"""
        try:
            # Convert to JSON-serializable format
            redis_metrics = {
                'timestamp': metrics['start_time'],
                'endpoint': metrics['endpoint'],
                'method': metrics['method'],
                'elapsed_time': metrics['elapsed_time'],
                'status_code': metrics['response_status'],
                'successful': metrics['successful']
            }
            
            # Store in sorted set
            key = f"metrics:requests:{datetime.now().strftime('%Y%m%d')}"
            self.redis_client.zadd(
                key,
                {json.dumps(redis_metrics): metrics['start_time']}
            )
            
            # Set expiry (7 days)
            self.redis_client.expire(key, 7 * 86400)
            
            # Update counters
            self._update_redis_counters(metrics)
            
        except Exception as e:
            logger.error(f"Failed to store metrics in Redis: {str(e)}")
    
    def _update_redis_counters(self, metrics: Dict[str, Any]):
        """Update Redis counters"""
        endpoint = metrics.get('endpoint', 'unknown')
        hour_key = datetime.now().strftime('%Y%m%d%H')
        
        # Request count
        self.redis_client.hincrby(f"metrics:counts:{hour_key}", endpoint, 1)
        
        # Response time sum
        self.redis_client.hincrbyfloat(
            f"metrics:response_times:{hour_key}",
            endpoint,
            metrics['elapsed_time']
        )
        
        # Error count
        if not metrics['successful']:
            self.redis_client.hincrby(f"metrics:errors:{hour_key}", endpoint, 1)
        
        # Set expiry
        for key_pattern in ['counts', 'response_times', 'errors']:
            key = f"metrics:{key_pattern}:{hour_key}"
            self.redis_client.expire(key, 86400)  # 24 hours
    
    def _handle_slow_request(self, metrics: Dict[str, Any]):
        """Handle slow request detection"""
        logger.warning(
            f"Slow request detected: {metrics['endpoint']} "
            f"took {metrics['elapsed_time']:.2f}ms"
        )
        
        # Store slow request details
        if self.redis_client:
            slow_request = {
                'timestamp': metrics['start_time'],
                'endpoint': metrics['endpoint'],
                'elapsed_time': metrics['elapsed_time'],
                'path': metrics['path'],
                'method': metrics['method']
            }
            
            self.redis_client.lpush(
                'metrics:slow_requests',
                json.dumps(slow_request)
            )
            
            # Keep only last 100 slow requests
            self.redis_client.ltrim('metrics:slow_requests', 0, 99)
    
    @contextmanager
    def measure_performance(self, operation_name: str):
        """Context manager for measuring operation performance"""
        start_time = time.time()
        
        try:
            yield
        finally:
            elapsed_time = (time.time() - start_time) * 1000
            
            # Store operation metrics
            operation_metrics = {
                'operation': operation_name,
                'timestamp': start_time,
                'elapsed_time': elapsed_time
            }
            
            if self.redis_client:
                self.redis_client.lpush(
                    f"metrics:operations:{operation_name}",
                    json.dumps(operation_metrics)
                )
                
                # Keep only last 1000 operations
                self.redis_client.ltrim(
                    f"metrics:operations:{operation_name}",
                    0,
                    999
                )
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            system_metrics = {
                'timestamp': time.time(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': psutil.getloadavg()
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
            # Store metrics
            self.system_metrics.append(system_metrics)
            
            # Check thresholds
            self._check_system_thresholds(system_metrics)
            
            # Store in Redis
            if self.redis_client:
                self._store_system_metrics_redis(system_metrics)
            
            return system_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            return {}
    
    def collect_process_metrics(self):
        """Collect process-level metrics"""
        try:
            process = psutil.Process()
            
            # Process metrics
            with process.oneshot():
                process_metrics = {
                    'timestamp': time.time(),
                    'pid': process.pid,
                    'name': process.name(),
                    'status': process.status(),
                    'cpu_percent': process.cpu_percent(),
                    'memory_info': process.memory_info()._asdict(),
                    'memory_percent': process.memory_percent(),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
                    'connections': len(process.connections()),
                    'create_time': process.create_time()
                }
            
            # Store metrics
            self.process_metrics.append(process_metrics)
            
            # Store in Redis
            if self.redis_client:
                self._store_process_metrics_redis(process_metrics)
            
            return process_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect process metrics: {str(e)}")
            return {}
    
    def _store_system_metrics_redis(self, metrics: Dict[str, Any]):
        """Store system metrics in Redis"""
        try:
            key = f"metrics:system:{datetime.now().strftime('%Y%m%d%H')}"
            
            # Store as time series
            self.redis_client.zadd(
                key,
                {json.dumps(metrics): metrics['timestamp']}
            )
            
            # Set expiry
            self.redis_client.expire(key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to store system metrics in Redis: {str(e)}")
    
    def _store_process_metrics_redis(self, metrics: Dict[str, Any]):
        """Store process metrics in Redis"""
        try:
            key = f"metrics:process:{datetime.now().strftime('%Y%m%d%H')}"
            
            # Convert to serializable format
            redis_metrics = {
                'timestamp': metrics['timestamp'],
                'pid': metrics['pid'],
                'cpu_percent': metrics['cpu_percent'],
                'memory_percent': metrics['memory_percent'],
                'num_threads': metrics['num_threads'],
                'connections': metrics['connections']
            }
            
            # Store as time series
            self.redis_client.zadd(
                key,
                {json.dumps(redis_metrics): metrics['timestamp']}
            )
            
            # Set expiry
            self.redis_client.expire(key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to store process metrics in Redis: {str(e)}")
    
    def _check_system_thresholds(self, metrics: Dict[str, Any]):
        """Check if system metrics exceed thresholds"""
        alerts = []
        
        # CPU threshold
        if metrics['cpu']['percent'] > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu',
                'value': metrics['cpu']['percent'],
                'threshold': self.thresholds['cpu_percent'],
                'message': f"CPU usage is {metrics['cpu']['percent']}%"
            })
        
        # Memory threshold
        if metrics['memory']['percent'] > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory',
                'value': metrics['memory']['percent'],
                'threshold': self.thresholds['memory_percent'],
                'message': f"Memory usage is {metrics['memory']['percent']}%"
            })
        
        # Send alerts
        for alert in alerts:
            self._send_performance_alert(alert)
    
    def _send_performance_alert(self, alert: Dict[str, Any]):
        """Send performance alert"""
        logger.warning(
            f"Performance alert: {alert['type']} - {alert['message']}"
        )
        
        if self.redis_client:
            self.redis_client.lpush(
                'alerts:performance',
                json.dumps({
                    'timestamp': time.time(),
                    **alert
                })
            )
            
            # Keep only last 100 alerts
            self.redis_client.ltrim('alerts:performance', 0, 99)
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter recent metrics
        recent_requests = [
            m for m in self.request_metrics
            if m['start_time'] > cutoff_time
        ]
        
        if not recent_requests:
            return {
                'total_requests': 0,
                'average_response_time': 0,
                'error_rate': 0,
                'endpoints': {}
            }
        
        # Calculate summary
        total_requests = len(recent_requests)
        successful_requests = sum(1 for r in recent_requests if r['successful'])
        total_response_time = sum(r['elapsed_time'] for r in recent_requests)
        
        summary = {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': total_requests - successful_requests,
            'average_response_time': total_response_time / total_requests,
            'error_rate': (total_requests - successful_requests) / total_requests,
            'endpoints': {}
        }
        
        # Endpoint breakdown
        endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'errors': 0
        })
        
        for request in recent_requests:
            endpoint = request.get('endpoint', 'unknown')
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_time'] += request['elapsed_time']
            if not request['successful']:
                endpoint_stats[endpoint]['errors'] += 1
        
        # Calculate endpoint averages
        for endpoint, stats in endpoint_stats.items():
            summary['endpoints'][endpoint] = {
                'count': stats['count'],
                'average_response_time': stats['total_time'] / stats['count'],
                'error_rate': stats['errors'] / stats['count'],
                'errors': stats['errors']
            }
        
        # Add system metrics summary
        recent_system = [
            m for m in self.system_metrics
            if m['timestamp'] > cutoff_time
        ]
        
        if recent_system:
            summary['system'] = {
                'average_cpu': np.mean([m['cpu']['percent'] for m in recent_system]),
                'average_memory': np.mean([m['memory']['percent'] for m in recent_system]),
                'peak_cpu': max(m['cpu']['percent'] for m in recent_system),
                'peak_memory': max(m['memory']['percent'] for m in recent_system)
            }
        
        return summary
    
    def get_endpoint_performance(self, endpoint: str) -> Dict[str, Any]:
        """Get detailed performance metrics for specific endpoint"""
        if endpoint not in self.endpoint_metrics:
            return {'error': 'Endpoint not found'}
        
        metrics = self.endpoint_metrics[endpoint]
        response_times = list(self.response_times[endpoint])
        
        if not response_times:
            return metrics
        
        # Calculate percentiles
        percentiles = np.percentile(response_times, [50, 75, 90, 95, 99])
        
        return {
            **metrics,
            'average_response_time': metrics['total_time'] / metrics['count'],
            'percentiles': {
                'p50': percentiles[0],
                'p75': percentiles[1],
                'p90': percentiles[2],
                'p95': percentiles[3],
                'p99': percentiles[4]
            },
            'min_response_time': min(response_times),
            'max_response_time': max(response_times)
        }
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self._monitoring_thread is None:
            self._monitoring_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self._monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while not self._stop_monitoring.is_set():
            try:
                # Collect system metrics
                self.collect_system_metrics()
                self.collect_process_metrics()
                
                # Sleep for interval
                self._stop_monitoring.wait(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")


def init_performance_monitoring(app: Flask, redis_client: redis.Redis):
    """Initialize performance monitoring"""
    collector = PerformanceCollector(app, redis_client)
    app.performance_collector = collector
    
    # Add CLI commands
    @app.cli.command()
    def performance_summary():
        """Show performance summary"""
        summary = collector.get_performance_summary()
        logger.info(json.dumps(summary, indent=2))
    
    @app.cli.command()
    def system_metrics():
        """Show current system metrics"""
        metrics = collector.collect_system_metrics()
        logger.info(json.dumps(metrics, indent=2))
    
    return collector 