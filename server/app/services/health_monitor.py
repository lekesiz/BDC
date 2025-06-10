"""
Comprehensive Health Monitoring Service for BDC Platform
Provides system health checks, performance monitoring, and alerting capabilities.
"""

import os
import time
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import current_app
from sqlalchemy import text
from redis import Redis
import requests
import logging
from threading import Thread
import json

logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    """Data class for health metrics"""
    name: str
    value: Any
    status: str  # 'healthy', 'warning', 'critical'
    threshold: Optional[float] = None
    unit: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class ServiceStatus:
    """Data class for service status"""
    name: str
    status: str
    response_time: Optional[float] = None
    last_check: datetime = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.last_check is None:
            self.last_check = datetime.utcnow()

class HealthMonitorService:
    """Comprehensive health monitoring service"""
    
    def __init__(self, app=None):
        self.app = app
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 2000.0,  # ms
            'error_rate': 5.0,  # %
            'db_connection_time': 1000.0  # ms
        }
        self.health_history = []
        self.max_history = 1000
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.health_monitor = self
    
    def get_basic_health(self) -> Dict[str, Any]:
        """Get basic health status"""
        try:
            start_time = time.time()
            
            # Basic checks
            db_status = self._check_database()
            redis_status = self._check_redis()
            disk_status = self._check_disk_space()
            
            # Overall status
            overall_status = 'healthy'
            if not db_status['healthy'] or not redis_status['healthy']:
                overall_status = 'critical'
            elif disk_status['usage_percent'] > 85:
                overall_status = 'warning'
            
            response_time = (time.time() - start_time) * 1000
            
            health_data = {
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'response_time_ms': round(response_time, 2),
                'services': {
                    'database': db_status,
                    'redis': redis_status,
                    'disk': disk_status
                },
                'uptime': self._get_uptime(),
                'version': self._get_app_version()
            }
            
            return health_data
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'critical',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def get_detailed_health(self) -> Dict[str, Any]:
        """Get comprehensive health status with detailed metrics"""
        try:
            start_time = time.time()
            
            # System metrics
            system_metrics = self._get_system_metrics()
            
            # Service checks
            service_statuses = self._check_all_services()
            
            # Performance metrics
            performance_metrics = self._get_performance_metrics()
            
            # Application metrics
            app_metrics = self._get_application_metrics()
            
            # Determine overall status
            overall_status = self._calculate_overall_status(
                system_metrics, service_statuses, performance_metrics
            )
            
            response_time = (time.time() - start_time) * 1000
            
            detailed_health = {
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'response_time_ms': round(response_time, 2),
                'system': system_metrics,
                'services': service_statuses,
                'performance': performance_metrics,
                'application': app_metrics,
                'alerts': self._get_active_alerts(),
                'environment': self._get_environment_info()
            }
            
            # Store in history
            self._store_health_history(detailed_health)
            
            return detailed_health
            
        except Exception as e:
            logger.error(f"Detailed health check failed: {str(e)}")
            return {
                'status': 'critical',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            from app import db
            start_time = time.time()
            
            # Test connection with simple query
            result = db.session.execute(text('SELECT 1')).scalar()
            connection_time = (time.time() - start_time) * 1000
            
            # Check active connections
            connection_count = db.session.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            ).scalar()
            
            return {
                'healthy': True,
                'connection_time_ms': round(connection_time, 2),
                'active_connections': connection_count,
                'status': 'healthy' if connection_time < 1000 else 'warning'
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'healthy': False,
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            from app.extensions import redis_client
            start_time = time.time()
            
            # Test Redis connection
            redis_client.ping()
            connection_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = redis_client.info()
            memory_usage = info.get('used_memory', 0)
            connected_clients = info.get('connected_clients', 0)
            
            return {
                'healthy': True,
                'connection_time_ms': round(connection_time, 2),
                'memory_usage_mb': round(memory_usage / 1024 / 1024, 2),
                'connected_clients': connected_clients,
                'status': 'healthy' if connection_time < 100 else 'warning'
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {
                'healthy': False,
                'status': 'critical',
                'error': str(e)
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space usage"""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            status = 'healthy'
            if usage_percent > 90:
                status = 'critical'
            elif usage_percent > 80:
                status = 'warning'
            
            return {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'used_gb': round(disk_usage.used / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'usage_percent': round(usage_percent, 2),
                'status': status
            }
            
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': list(load_avg),
                    'status': 'critical' if cpu_percent > 90 else 'warning' if cpu_percent > 80 else 'healthy'
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'percent': memory.percent,
                    'status': 'critical' if memory.percent > 90 else 'warning' if memory.percent > 80 else 'healthy'
                },
                'swap': {
                    'total_gb': round(swap.total / (1024**3), 2),
                    'used_gb': round(swap.used / (1024**3), 2),
                    'percent': swap.percent
                },
                'disk_io': {
                    'read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                    'write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0
                },
                'network_io': {
                    'bytes_sent_mb': round(network_io.bytes_sent / (1024**2), 2) if network_io else 0,
                    'bytes_recv_mb': round(network_io.bytes_recv / (1024**2), 2) if network_io else 0,
                    'packets_sent': network_io.packets_sent if network_io else 0,
                    'packets_recv': network_io.packets_recv if network_io else 0
                }
            }
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {str(e)}")
            return {'error': str(e)}
    
    def _check_all_services(self) -> Dict[str, ServiceStatus]:
        """Check all external services"""
        services = {}
        
        # Database check
        db_result = self._check_database()
        services['database'] = ServiceStatus(
            name='PostgreSQL Database',
            status='healthy' if db_result.get('healthy') else 'critical',
            response_time=db_result.get('connection_time_ms'),
            error_message=db_result.get('error')
        )
        
        # Redis check
        redis_result = self._check_redis()
        services['redis'] = ServiceStatus(
            name='Redis Cache',
            status='healthy' if redis_result.get('healthy') else 'critical',
            response_time=redis_result.get('connection_time_ms'),
            error_message=redis_result.get('error')
        )
        
        # External service checks (if configured)
        external_services = current_app.config.get('HEALTH_CHECK_SERVICES', {})
        for service_name, service_config in external_services.items():
            services[service_name] = self._check_external_service(
                service_name, service_config
            )
        
        return {k: asdict(v) for k, v in services.items()}
    
    def _check_external_service(self, name: str, config: Dict) -> ServiceStatus:
        """Check external service health"""
        try:
            start_time = time.time()
            response = requests.get(
                config['url'],
                timeout=config.get('timeout', 10),
                headers=config.get('headers', {})
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return ServiceStatus(
                    name=name,
                    status='healthy',
                    response_time=response_time
                )
            else:
                return ServiceStatus(
                    name=name,
                    status='warning',
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            return ServiceStatus(
                name=name,
                status='critical',
                error_message=str(e)
            )
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get application performance metrics"""
        try:
            # This would integrate with your metrics collection system
            # For now, we'll return sample data structure
            return {
                'api_response_time': {
                    'avg_ms': 250.5,
                    'p95_ms': 450.2,
                    'p99_ms': 850.1
                },
                'request_rate': {
                    'requests_per_minute': 150,
                    'error_rate_percent': 1.2
                },
                'database_performance': {
                    'avg_query_time_ms': 85.3,
                    'slow_queries_count': 2,
                    'connection_pool_usage': 0.65
                }
            }
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            from app import db
            from app.models import User, Beneficiary, Evaluation
            
            # Database counts
            user_count = db.session.query(User).count()
            beneficiary_count = db.session.query(Beneficiary).count()
            evaluation_count = db.session.query(Evaluation).count()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_users = db.session.query(User).filter(
                User.created_at >= yesterday
            ).count()
            recent_evaluations = db.session.query(Evaluation).filter(
                Evaluation.created_at >= yesterday
            ).count()
            
            return {
                'total_counts': {
                    'users': user_count,
                    'beneficiaries': beneficiary_count,
                    'evaluations': evaluation_count
                },
                'recent_activity': {
                    'new_users_24h': recent_users,
                    'new_evaluations_24h': recent_evaluations
                },
                'system_info': {
                    'python_version': platform.python_version(),
                    'platform': platform.platform(),
                    'uptime': self._get_uptime()
                }
            }
            
        except Exception as e:
            logger.error(f"Application metrics collection failed: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_overall_status(self, system_metrics, service_statuses, performance_metrics) -> str:
        """Calculate overall health status"""
        critical_count = 0
        warning_count = 0
        
        # Check system metrics
        if system_metrics.get('cpu', {}).get('status') == 'critical':
            critical_count += 1
        elif system_metrics.get('cpu', {}).get('status') == 'warning':
            warning_count += 1
        
        if system_metrics.get('memory', {}).get('status') == 'critical':
            critical_count += 1
        elif system_metrics.get('memory', {}).get('status') == 'warning':
            warning_count += 1
        
        # Check service statuses
        for service in service_statuses.values():
            if service.get('status') == 'critical':
                critical_count += 1
            elif service.get('status') == 'warning':
                warning_count += 1
        
        # Determine overall status
        if critical_count > 0:
            return 'critical'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'healthy'
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        alerts = []
        
        # Check system thresholds
        try:
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'type': 'system',
                    'severity': 'critical' if cpu_percent > 90 else 'warning',
                    'message': f"High CPU usage: {cpu_percent}%",
                    'threshold': self.alert_thresholds['cpu_percent'],
                    'current_value': cpu_percent,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            memory = psutil.virtual_memory()
            if memory.percent > self.alert_thresholds['memory_percent']:
                alerts.append({
                    'type': 'system',
                    'severity': 'critical' if memory.percent > 90 else 'warning',
                    'message': f"High memory usage: {memory.percent}%",
                    'threshold': self.alert_thresholds['memory_percent'],
                    'current_value': memory.percent,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            if disk_percent > self.alert_thresholds['disk_percent']:
                alerts.append({
                    'type': 'system',
                    'severity': 'critical',
                    'message': f"High disk usage: {disk_percent:.1f}%",
                    'threshold': self.alert_thresholds['disk_percent'],
                    'current_value': disk_percent,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Alert checking failed: {str(e)}")
        
        return alerts
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        return {
            'hostname': platform.node(),
            'os': platform.system(),
            'os_version': platform.release(),
            'python_version': platform.python_version(),
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'timezone': str(datetime.now().astimezone().tzinfo)
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = uptime_seconds / 3600
            
            if uptime_hours < 24:
                return f"{uptime_hours:.1f} hours"
            else:
                uptime_days = uptime_hours / 24
                return f"{uptime_days:.1f} days"
                
        except Exception:
            return "Unknown"
    
    def _get_app_version(self) -> str:
        """Get application version"""
        try:
            # Try to read version from package.json or version file
            version_file = os.path.join(os.path.dirname(__file__), '../../VERSION')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    return f.read().strip()
            return "1.0.0"
        except Exception:
            return "Unknown"
    
    def _store_health_history(self, health_data: Dict[str, Any]):
        """Store health data in history"""
        try:
            self.health_history.append({
                'timestamp': health_data['timestamp'],
                'status': health_data['status'],
                'response_time_ms': health_data['response_time_ms'],
                'cpu_percent': health_data.get('system', {}).get('cpu', {}).get('percent', 0),
                'memory_percent': health_data.get('system', {}).get('memory', {}).get('percent', 0)
            })
            
            # Keep only recent history
            if len(self.health_history) > self.max_history:
                self.health_history = self.health_history[-self.max_history:]
                
        except Exception as e:
            logger.error(f"Failed to store health history: {str(e)}")
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            entry for entry in self.health_history
            if datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')) >= cutoff_time
        ]
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold for a metric"""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            logger.info(f"Updated alert threshold for {metric}: {threshold}")
        else:
            logger.warning(f"Unknown metric for threshold: {metric}")
    
    def get_alert_thresholds(self) -> Dict[str, float]:
        """Get current alert thresholds"""
        return self.alert_thresholds.copy()

# Global instance
health_monitor = HealthMonitorService()