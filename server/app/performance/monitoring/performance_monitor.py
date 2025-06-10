"""
Performance Monitor

Real-time performance monitoring with metrics collection,
alerting, and performance analytics.
"""

import time
import psutil
import threading
import logging
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from datetime import datetime, timedelta
import json


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Individual metric data"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class Alert:
    """Performance alert"""
    name: str
    level: AlertLevel
    message: str
    timestamp: float
    metric_name: str
    threshold: float
    current_value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """System performance snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent: float
    network_bytes_recv: float
    active_connections: int
    response_time_avg: float
    request_rate: float


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    """
    
    def __init__(self, collection_interval: int = 5, history_size: int = 1000):
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        # Metrics storage
        self.metrics = defaultdict(lambda: deque(maxlen=history_size))
        self.counters = defaultdict(float)
        self.timers = defaultdict(list)
        self.histograms = defaultdict(list)
        
        # System metrics
        self.system_snapshots = deque(maxlen=history_size)
        self.request_times = deque(maxlen=1000)
        self.request_count = 0
        self.error_count = 0
        
        # Alerting
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_callbacks = []
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.start_time = time.time()
        
        # Request tracking
        self.active_requests = {}
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0
        })
        
        self._initialize_default_alerts()
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logging.info("Performance monitoring stopped")
    
    def record_metric(self, name: str, value: float, 
                     metric_type: MetricType = MetricType.GAUGE,
                     tags: Dict[str, str] = None):
        """Record a custom metric"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            metric_type=metric_type
        )
        
        self.metrics[name].append(metric)
        
        # Handle different metric types
        if metric_type == MetricType.COUNTER:
            self.counters[name] += value
        elif metric_type == MetricType.HISTOGRAM:
            self.histograms[name].append(value)
        
        # Check alert rules
        self._check_alerts(name, value)
    
    def start_request_monitoring(self) -> str:
        """Start monitoring a request"""
        request_id = f"req_{int(time.time() * 1000000)}"
        self.active_requests[request_id] = {
            'start_time': time.time(),
            'endpoint': None,
            'method': None
        }
        return request_id
    
    def record_request(self, endpoint: str, method: str, duration: float, 
                      status_code: int, request_id: str = None):
        """Record request completion"""
        self.request_count += 1
        
        if status_code >= 400:
            self.error_count += 1
        
        # Update request times
        self.request_times.append(duration)
        
        # Update endpoint statistics
        stats = self.endpoint_stats[f"{method} {endpoint}"]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        
        if status_code >= 400:
            stats['errors'] += 1
        
        # Clean up active request
        if request_id and request_id in self.active_requests:
            del self.active_requests[request_id]
        
        # Record metrics
        self.record_metric('request_duration', duration, MetricType.HISTOGRAM)
        self.record_metric('request_count', 1, MetricType.COUNTER)
        
        if status_code >= 400:
            self.record_metric('error_count', 1, MetricType.COUNTER)
    
    def add_alert_rule(self, name: str, metric_name: str, threshold: float,
                      comparison: str = 'gt', level: AlertLevel = AlertLevel.WARNING,
                      callback: Optional[Callable] = None):
        """Add alert rule for a metric"""
        self.alert_rules[name] = {
            'metric_name': metric_name,
            'threshold': threshold,
            'comparison': comparison,  # 'gt', 'lt', 'eq'
            'level': level,
            'callback': callback,
            'cooldown': 300,  # 5 minutes
            'last_triggered': 0
        }
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        now = time.time()
        uptime = now - self.start_time
        
        # Calculate request rate
        recent_requests = [t for t in self.request_times if now - t <= 60]  # Last minute
        request_rate = len(recent_requests) / 60.0
        
        # Calculate average response time
        avg_response_time = statistics.mean(self.request_times) if self.request_times else 0
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_io_counters()
        network = psutil.net_io_counters()
        
        return {
            'system': {
                'uptime_seconds': uptime,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / 1024 / 1024,
                'memory_available_mb': memory.available / 1024 / 1024,
                'disk_read_mb': disk.read_bytes / 1024 / 1024 if disk else 0,
                'disk_write_mb': disk.write_bytes / 1024 / 1024 if disk else 0,
                'network_sent_mb': network.bytes_sent / 1024 / 1024 if network else 0,
                'network_recv_mb': network.bytes_recv / 1024 / 1024 if network else 0
            },
            'application': {
                'total_requests': self.request_count,
                'total_errors': self.error_count,
                'error_rate': self.error_count / max(self.request_count, 1) * 100,
                'request_rate_per_minute': request_rate * 60,
                'avg_response_time_ms': avg_response_time * 1000,
                'active_requests': len(self.active_requests),
                'p95_response_time_ms': self._calculate_percentile(95) * 1000,
                'p99_response_time_ms': self._calculate_percentile(99) * 1000
            },
            'custom_metrics': {
                name: {
                    'current': metrics[-1].value if metrics else 0,
                    'count': len(metrics)
                } for name, metrics in self.metrics.items()
            }
        }
    
    def get_endpoint_statistics(self) -> Dict[str, Any]:
        """Get detailed endpoint statistics"""
        stats = {}
        
        for endpoint, endpoint_stats in self.endpoint_stats.items():
            if endpoint_stats['count'] > 0:
                stats[endpoint] = {
                    'total_requests': endpoint_stats['count'],
                    'avg_response_time_ms': endpoint_stats['avg_time'] * 1000,
                    'min_response_time_ms': endpoint_stats['min_time'] * 1000,
                    'max_response_time_ms': endpoint_stats['max_time'] * 1000,
                    'error_count': endpoint_stats['errors'],
                    'error_rate': endpoint_stats['errors'] / endpoint_stats['count'] * 100,
                    'requests_per_minute': self._calculate_endpoint_rate(endpoint)
                }
        
        return stats
    
    def get_performance_trends(self, duration_minutes: int = 60) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        cutoff_time = time.time() - (duration_minutes * 60)
        trends = {}
        
        # System metrics trends
        recent_snapshots = [s for s in self.system_snapshots if s.timestamp >= cutoff_time]
        
        if recent_snapshots:
            trends['cpu_percent'] = [s.cpu_percent for s in recent_snapshots]
            trends['memory_percent'] = [s.memory_percent for s in recent_snapshots]
            trends['response_time_avg'] = [s.response_time_avg for s in recent_snapshots]
            trends['request_rate'] = [s.request_rate for s in recent_snapshots]
        
        # Custom metrics trends
        for name, metrics in self.metrics.items():
            recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            if recent_metrics:
                trends[f'custom_{name}'] = [m.value for m in recent_metrics]
        
        return trends
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alerts"""
        return {
            'active_alerts': len(self.active_alerts),
            'alert_rules': len(self.alert_rules),
            'alerts_by_level': {
                level.value: sum(1 for alert in self.active_alerts.values() 
                               if alert.level == level)
                for level in AlertLevel
            },
            'recent_alerts': list(self.active_alerts.values())[-10:]  # Last 10 alerts
        }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_metrics = self.get_current_metrics()
        endpoint_stats = self.get_endpoint_statistics()
        trends = self.get_performance_trends()
        alerts = self.get_alert_summary()
        
        # Performance score calculation
        performance_score = self._calculate_performance_score(current_metrics)
        
        # Recommendations
        recommendations = self._generate_recommendations(current_metrics, endpoint_stats)
        
        return {
            'timestamp': time.time(),
            'performance_score': performance_score,
            'current_metrics': current_metrics,
            'endpoint_statistics': endpoint_stats,
            'trends': trends,
            'alerts': alerts,
            'recommendations': recommendations,
            'monitoring_duration_hours': (time.time() - self.start_time) / 3600
        }
    
    # Private methods
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logging.error(f"Monitoring loop error: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_io_counters()
            network = psutil.net_io_counters()
            
            # Calculate request rate
            now = time.time()
            recent_requests = [t for t in self.request_times if now - t <= 60]
            request_rate = len(recent_requests) / 60.0
            
            # Calculate average response time
            avg_response_time = statistics.mean(self.request_times) if self.request_times else 0
            
            # Create snapshot
            snapshot = PerformanceSnapshot(
                timestamp=now,
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_io_read_mb=disk.read_bytes / 1024 / 1024 if disk else 0,
                disk_io_write_mb=disk.write_bytes / 1024 / 1024 if disk else 0,
                network_bytes_sent=network.bytes_sent if network else 0,
                network_bytes_recv=network.bytes_recv if network else 0,
                active_connections=len(self.active_requests),
                response_time_avg=avg_response_time,
                request_rate=request_rate
            )
            
            self.system_snapshots.append(snapshot)
            
            # Record as metrics
            self.record_metric('cpu_percent', cpu_percent)
            self.record_metric('memory_percent', memory.percent)
            self.record_metric('request_rate', request_rate)
            self.record_metric('avg_response_time', avg_response_time)
            
        except Exception as e:
            logging.error(f"System metrics collection failed: {e}")
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if metric value triggers any alerts"""
        for alert_name, rule in self.alert_rules.items():
            if rule['metric_name'] != metric_name:
                continue
            
            # Check cooldown
            if time.time() - rule['last_triggered'] < rule['cooldown']:
                continue
            
            # Check threshold
            triggered = False
            if rule['comparison'] == 'gt' and value > rule['threshold']:
                triggered = True
            elif rule['comparison'] == 'lt' and value < rule['threshold']:
                triggered = True
            elif rule['comparison'] == 'eq' and abs(value - rule['threshold']) < 0.001:
                triggered = True
            
            if triggered:
                self._trigger_alert(alert_name, rule, value)
    
    def _trigger_alert(self, alert_name: str, rule: Dict, current_value: float):
        """Trigger an alert"""
        alert = Alert(
            name=alert_name,
            level=rule['level'],
            message=f"Metric {rule['metric_name']} exceeded threshold: {current_value} > {rule['threshold']}",
            timestamp=time.time(),
            metric_name=rule['metric_name'],
            threshold=rule['threshold'],
            current_value=current_value
        )
        
        self.active_alerts[alert_name] = alert
        rule['last_triggered'] = time.time()
        
        # Execute callbacks
        if rule['callback']:
            try:
                rule['callback'](alert)
            except Exception as e:
                logging.error(f"Alert callback failed: {e}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logging.error(f"Alert callback failed: {e}")
        
        logging.warning(f"Performance alert triggered: {alert.message}")
    
    def _calculate_percentile(self, percentile: int) -> float:
        """Calculate response time percentile"""
        if not self.request_times:
            return 0.0
        
        sorted_times = sorted(self.request_times)
        index = int((percentile / 100.0) * len(sorted_times))
        index = min(index, len(sorted_times) - 1)
        return sorted_times[index]
    
    def _calculate_endpoint_rate(self, endpoint: str) -> float:
        """Calculate requests per minute for endpoint"""
        # This is simplified - in practice, you'd track timestamps per endpoint
        return 0.0
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100.0
        
        # CPU penalty
        cpu_percent = metrics['system']['cpu_percent']
        if cpu_percent > 80:
            score -= (cpu_percent - 80) * 2
        
        # Memory penalty
        memory_percent = metrics['system']['memory_percent']
        if memory_percent > 85:
            score -= (memory_percent - 85) * 3
        
        # Response time penalty
        avg_response_time = metrics['application']['avg_response_time_ms']
        if avg_response_time > 1000:  # > 1 second
            score -= (avg_response_time - 1000) / 100
        
        # Error rate penalty
        error_rate = metrics['application']['error_rate']
        score -= error_rate * 5
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, current_metrics: Dict, endpoint_stats: Dict) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # System recommendations
        if current_metrics['system']['cpu_percent'] > 80:
            recommendations.append("High CPU usage detected - consider scaling or optimizing CPU-intensive operations")
        
        if current_metrics['system']['memory_percent'] > 85:
            recommendations.append("High memory usage detected - consider increasing memory or optimizing memory usage")
        
        # Application recommendations
        if current_metrics['application']['avg_response_time_ms'] > 1000:
            recommendations.append("High average response time - consider optimizing slow endpoints or adding caching")
        
        if current_metrics['application']['error_rate'] > 5:
            recommendations.append("High error rate detected - investigate error logs and fix failing endpoints")
        
        # Endpoint-specific recommendations
        slow_endpoints = [
            endpoint for endpoint, stats in endpoint_stats.items()
            if stats['avg_response_time_ms'] > 2000
        ]
        
        if slow_endpoints:
            recommendations.append(f"Slow endpoints detected: {', '.join(slow_endpoints[:3])}")
        
        return recommendations
    
    def _initialize_default_alerts(self):
        """Initialize default alert rules"""
        self.add_alert_rule(
            'high_cpu',
            'cpu_percent',
            80,
            'gt',
            AlertLevel.WARNING
        )
        
        self.add_alert_rule(
            'high_memory',
            'memory_percent',
            85,
            'gt',
            AlertLevel.WARNING
        )
        
        self.add_alert_rule(
            'slow_response',
            'avg_response_time',
            2.0,  # 2 seconds
            'gt',
            AlertLevel.WARNING
        )