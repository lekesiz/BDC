"""Enhanced health check endpoints for comprehensive monitoring."""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.extensions import db
import redis
import os
import psutil
import time
import json
import requests
from sqlalchemy import text
from collections import defaultdict

from app.utils.logging import logger

health_bp = Blueprint('health', __name__)

# Store health check metrics
health_metrics = defaultdict(list)
service_checks = {}


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint with response time tracking."""
    start_time = time.time()
    
    try:
        # Quick database ping
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'
    
    response_time = round((time.time() - start_time) * 1000, 2)
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'bdc-backend',
        'version': '1.0.0',
        'response_time_ms': response_time,
        'database': db_status
    }
    
    # Store metrics
    health_metrics['basic_checks'].append({
        'timestamp': time.time(),
        'response_time': response_time,
        'status': health_data['status']
    })
    
    # Keep only last 1000 entries
    if len(health_metrics['basic_checks']) > 1000:
        health_metrics['basic_checks'] = health_metrics['basic_checks'][-1000:]
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with all dependencies."""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'bdc-backend',
        'version': '1.0.0',
        'checks': {}
    }
    
    overall_status = 200
    
    # Database check
    try:
        db.session.execute('SELECT 1')
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
        overall_status = 503
    
    # Redis check
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        health_status['checks']['redis'] = {
            'status': 'healthy',
            'message': 'Redis connection successful'
        }
    except Exception as e:
        health_status['checks']['redis'] = {
            'status': 'unhealthy',
            'message': f'Redis connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
        overall_status = 503
    
    # Disk space check
    try:
        import shutil
        disk_usage = shutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        if free_percent > 20:
            health_status['checks']['disk_space'] = {
                'status': 'healthy',
                'message': f'Disk space OK ({free_percent:.1f}% free)'
            }
        elif free_percent > 10:
            health_status['checks']['disk_space'] = {
                'status': 'warning',
                'message': f'Disk space low ({free_percent:.1f}% free)'
            }
        else:
            health_status['checks']['disk_space'] = {
                'status': 'unhealthy',
                'message': f'Disk space critical ({free_percent:.1f}% free)'
            }
            health_status['status'] = 'unhealthy'
            overall_status = 503
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'unknown',
            'message': f'Could not check disk space: {str(e)}'
        }
    
    # Memory check
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent < 80:
            health_status['checks']['memory'] = {
                'status': 'healthy',
                'message': f'Memory usage OK ({memory_percent:.1f}%)'
            }
        elif memory_percent < 90:
            health_status['checks']['memory'] = {
                'status': 'warning',
                'message': f'Memory usage high ({memory_percent:.1f}%)'
            }
        else:
            health_status['checks']['memory'] = {
                'status': 'unhealthy',
                'message': f'Memory usage critical ({memory_percent:.1f}%)'
            }
            health_status['status'] = 'unhealthy'
            overall_status = 503
    except ImportError:
        health_status['checks']['memory'] = {
            'status': 'unknown',
            'message': 'psutil not available for memory check'
        }
    except Exception as e:
        health_status['checks']['memory'] = {
            'status': 'unknown',
            'message': f'Could not check memory: {str(e)}'
        }
    
    # Store detailed metrics
    health_metrics['detailed_checks'].append({
        'timestamp': time.time(),
        'status': health_status['status'],
        'checks': health_status['checks']
    })
    
    # Keep only last 100 detailed entries
    if len(health_metrics['detailed_checks']) > 100:
        health_metrics['detailed_checks'] = health_metrics['detailed_checks'][-100:]
    
    return jsonify(health_status), overall_status


@health_bp.route('/health/db', methods=['GET'])
def database_health():
    """Database-specific health check."""
    try:
        # Test database connection
        result = db.session.execute('SELECT version()')
        version = result.fetchone()[0] if result.rowcount > 0 else 'Unknown'
        
        # Test a simple query
        db.session.execute('SELECT COUNT(*) FROM users')
        
        return jsonify({
            'status': 'healthy',
            'database': 'postgresql',
            'version': version,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/health/redis', methods=['GET'])
def redis_health():
    """Redis-specific health check."""
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        
        # Test Redis connection
        pong = r.ping()
        
        # Test set/get operations
        test_key = 'health_check_test'
        r.set(test_key, 'test_value', ex=60)
        test_value = r.get(test_key)
        r.delete(test_key)
        
        # Get Redis info
        info = r.info()
        
        return jsonify({
            'status': 'healthy',
            'ping': pong,
            'test_operation': test_value.decode() if test_value else None,
            'redis_version': info.get('redis_version'),
            'connected_clients': info.get('connected_clients'),
            'used_memory_human': info.get('used_memory_human'),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """Enhanced Prometheus-style metrics endpoint."""
    try:
        # Basic metrics
        metrics_data = []
        
        # Health check metrics
        if health_metrics['basic_checks']:
            recent_checks = health_metrics['basic_checks'][-10:]
            avg_response_time = sum(check['response_time'] for check in recent_checks) / len(recent_checks)
            healthy_count = sum(1 for check in recent_checks if check['status'] == 'healthy')
            health_rate = healthy_count / len(recent_checks)
            
            metrics_data.append(f'bdc_health_check_response_time_ms {avg_response_time:.2f}')
            metrics_data.append(f'bdc_health_check_success_rate {health_rate:.2f}')
            metrics_data.append(f'bdc_health_checks_total {len(health_metrics["basic_checks"])}')
        
        # Database metrics
        try:
            result = db.session.execute('SELECT COUNT(*) FROM users')
            user_count = result.fetchone()[0] if result.rowcount > 0 else 0
            metrics_data.append(f'bdc_users_total {user_count}')
            
            result = db.session.execute('SELECT COUNT(*) FROM programs')
            program_count = result.fetchone()[0] if result.rowcount > 0 else 0
            metrics_data.append(f'bdc_programs_total {program_count}')
            
            result = db.session.execute('SELECT COUNT(*) FROM beneficiaries')
            beneficiary_count = result.fetchone()[0] if result.rowcount > 0 else 0
            metrics_data.append(f'bdc_beneficiaries_total {beneficiary_count}')
        except Exception:
            pass
        
        # System metrics
        try:
            import psutil
            
            # Memory
            memory = psutil.virtual_memory()
            metrics_data.append(f'bdc_memory_usage_percent {memory.percent}')
            metrics_data.append(f'bdc_memory_used_bytes {memory.used}')
            metrics_data.append(f'bdc_memory_total_bytes {memory.total}')
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics_data.append(f'bdc_cpu_usage_percent {cpu_percent}')
            
            # Disk
            disk = psutil.disk_usage('/')
            metrics_data.append(f'bdc_disk_usage_percent {(disk.used / disk.total) * 100}')
            metrics_data.append(f'bdc_disk_free_bytes {disk.free}')
            metrics_data.append(f'bdc_disk_total_bytes {disk.total}')
        except ImportError:
            pass
        except Exception:
            pass
        
        # Application metrics
        metrics_data.append(f'bdc_app_info{{version="1.0.0",service="bdc-backend"}} 1')
        metrics_data.append(f'bdc_app_uptime_seconds {(datetime.utcnow() - datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()}')
        
        # Request metrics (if available)
        try:
            from flask import current_app
            if hasattr(current_app, 'performance_collector'):
                collector = current_app.performance_collector
                summary = collector.get_performance_summary(hours=1)
                
                metrics_data.append(f'bdc_requests_total {summary.get("total_requests", 0)}')
                metrics_data.append(f'bdc_requests_failed_total {summary.get("failed_requests", 0)}')
                metrics_data.append(f'bdc_request_duration_seconds {summary.get("average_response_time", 0) / 1000:.3f}')
                metrics_data.append(f'bdc_error_rate {summary.get("error_rate", 0):.3f}')
        except Exception:
            pass
        
        return '\n'.join(metrics_data) + '\n', 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f'# Error generating metrics: {str(e)}\n', 500, {'Content-Type': 'text/plain'}


@health_bp.route('/health/monitoring', methods=['GET'])
def monitoring_endpoints():
    """Get all available monitoring endpoints."""
    endpoints = {
        'basic_health': '/health',
        'detailed_health': '/health/detailed',
        'database_health': '/health/db',
        'redis_health': '/health/redis',
        'external_services': '/health/external',
        'performance_metrics': '/health/performance',
        'security_health': '/health/security',
        'business_metrics': '/health/business',
        'prometheus_metrics': '/metrics',
        'readiness_probe': '/ready',
        'liveness_probe': '/live'
    }
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'available_endpoints': endpoints,
        'monitoring_tools': {
            'prometheus': 'http://localhost:9090',
            'grafana': 'http://localhost:3000',
            'alertmanager': 'http://localhost:9093'
        }
    }), 200


@health_bp.route('/health/external', methods=['GET'])
def external_services_health():
    """Check external service dependencies."""
    external_checks = {}
    overall_status = 'healthy'
    
    # Check external APIs (if configured)
    external_apis = {
        'wedof_api': os.getenv('WEDOF_API_URL'),
        'sms_gateway': os.getenv('SMS_GATEWAY_URL'),
        'email_service': os.getenv('EMAIL_SERVICE_URL')
    }
    
    for service_name, url in external_apis.items():
        if url:
            try:
                start_time = time.time()
                response = requests.get(f"{url}/health", timeout=5)
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    external_checks[service_name] = {
                        'status': 'healthy',
                        'response_time_ms': response_time,
                        'message': 'Service is responsive'
                    }
                else:
                    external_checks[service_name] = {
                        'status': 'unhealthy',
                        'response_time_ms': response_time,
                        'message': f'HTTP {response.status_code}'
                    }
                    overall_status = 'degraded'
            except requests.exceptions.Timeout:
                external_checks[service_name] = {
                    'status': 'unhealthy',
                    'message': 'Service timeout (>5s)'
                }
                overall_status = 'degraded'
            except Exception as e:
                external_checks[service_name] = {
                    'status': 'unhealthy',
                    'message': f'Connection failed: {str(e)}'
                }
                overall_status = 'degraded'
        else:
            external_checks[service_name] = {
                'status': 'not_configured',
                'message': 'Service URL not configured'
            }
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'external_services': external_checks
    }), 200 if overall_status != 'unhealthy' else 503


@health_bp.route('/health/performance', methods=['GET'])
def performance_metrics():
    """Get performance metrics and health trends."""
    try:
        # Calculate recent performance metrics
        current_time = time.time()
        last_hour = current_time - 3600
        
        recent_basic = [
            check for check in health_metrics['basic_checks']
            if check['timestamp'] > last_hour
        ]
        
        recent_detailed = [
            check for check in health_metrics['detailed_checks']
            if check['timestamp'] > last_hour
        ]
        
        # Calculate averages
        avg_response_time = 0
        healthy_percentage = 0
        
        if recent_basic:
            avg_response_time = sum(check['response_time'] for check in recent_basic) / len(recent_basic)
            healthy_count = sum(1 for check in recent_basic if check['status'] == 'healthy')
            healthy_percentage = (healthy_count / len(recent_basic)) * 100
        
        # System performance
        system_perf = {}
        try:
            system_perf = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
        except Exception:
            pass
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'performance': {
                'avg_response_time_ms': round(avg_response_time, 2),
                'health_percentage': round(healthy_percentage, 2),
                'checks_last_hour': len(recent_basic),
                'detailed_checks_last_hour': len(recent_detailed)
            },
            'system': system_perf
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@health_bp.route('/health/security', methods=['GET'])
def security_health():
    """Security-focused health checks."""
    security_checks = {}
    overall_status = 'healthy'
    
    # Check SSL certificate (if HTTPS is configured)
    ssl_status = 'not_applicable'
    if os.getenv('SSL_CERT_PATH'):
        try:
            import ssl
            import socket
            from datetime import datetime
            
            cert_path = os.getenv('SSL_CERT_PATH')
            if os.path.exists(cert_path):
                # Read certificate expiry (simplified check)
                ssl_status = 'configured'
            else:
                ssl_status = 'missing'
                overall_status = 'degraded'
        except Exception:
            ssl_status = 'error'
            overall_status = 'degraded'
    
    security_checks['ssl_certificate'] = {
        'status': ssl_status,
        'message': 'SSL certificate status'
    }
    
    # Check for required security headers
    security_headers = {
        'SECURITY_KEY_ROTATION_DAYS': os.getenv('SECURITY_KEY_ROTATION_DAYS'),
        'RATE_LIMIT_ENABLED': os.getenv('RATE_LIMIT_ENABLED'),
        'TWO_FACTOR_ENABLED': os.getenv('TWO_FACTOR_ENABLED')
    }
    
    missing_config = [key for key, value in security_headers.items() if not value]
    
    if missing_config:
        security_checks['security_config'] = {
            'status': 'warning',
            'message': f'Missing security configuration: {", ".join(missing_config)}'
        }
        overall_status = 'degraded'
    else:
        security_checks['security_config'] = {
            'status': 'healthy',
            'message': 'Security configuration complete'
        }
    
    # Check recent failed login attempts (if available)
    try:
        from sqlalchemy import func
        recent_failures = db.session.execute(
            text("""SELECT COUNT(*) FROM user_activities 
                     WHERE activity_type = 'login_failed' 
                     AND created_at > NOW() - INTERVAL '1 hour'""")
        ).scalar()
        
        if recent_failures > 100:  # Threshold for potential attack
            security_checks['login_failures'] = {
                'status': 'warning',
                'message': f'High number of failed logins: {recent_failures}',
                'count': recent_failures
            }
            overall_status = 'degraded'
        else:
            security_checks['login_failures'] = {
                'status': 'healthy',
                'message': f'Normal failed login rate: {recent_failures}',
                'count': recent_failures
            }
    except Exception:
        security_checks['login_failures'] = {
            'status': 'unknown',
            'message': 'Could not check login failure rate'
        }
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'security_checks': security_checks
    }), 200 if overall_status != 'unhealthy' else 503


@health_bp.route('/health/business', methods=['GET'])
def business_metrics_health():
    """Business logic health checks and metrics."""
    try:
        business_metrics = {}
        
        # Check core business entities
        queries = {
            'total_users': 'SELECT COUNT(*) FROM users',
            'active_users_24h': """SELECT COUNT(DISTINCT user_id) FROM user_activities 
                                   WHERE created_at > NOW() - INTERVAL '24 hours'""",
            'total_beneficiaries': 'SELECT COUNT(*) FROM beneficiaries',
            'active_programs': 'SELECT COUNT(*) FROM programs WHERE status = \'active\'',
            'pending_evaluations': 'SELECT COUNT(*) FROM evaluations WHERE status = \'pending\'',
            'total_documents': 'SELECT COUNT(*) FROM documents',
            'recent_appointments': """SELECT COUNT(*) FROM appointments 
                                     WHERE appointment_date >= CURRENT_DATE"""
        }
        
        for metric_name, query in queries.items():
            try:
                result = db.session.execute(text(query)).scalar()
                business_metrics[metric_name] = result if result is not None else 0
            except Exception as e:
                business_metrics[metric_name] = f'Error: {str(e)}'
        
        # Calculate system health based on business metrics
        status = 'healthy'
        warnings = []
        
        # Check for business anomalies
        if isinstance(business_metrics.get('pending_evaluations'), int):
            if business_metrics['pending_evaluations'] > 1000:
                warnings.append('High number of pending evaluations')
                status = 'degraded'
        
        if isinstance(business_metrics.get('active_users_24h'), int):
            if business_metrics['active_users_24h'] == 0:
                warnings.append('No active users in last 24 hours')
                status = 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'business_metrics': business_metrics,
            'warnings': warnings
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500