"""Health check endpoints for monitoring."""

from flask import Blueprint, jsonify
from datetime import datetime
from app.extensions import db
import redis
import os

from app.utils.logging import logger

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'bdc-backend',
        'version': '1.0.0'
    }), 200


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
    """Prometheus-style metrics endpoint."""
    try:
        # Basic metrics
        metrics_data = []
        
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
        
        return '\n'.join(metrics_data) + '\n', 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f'# Error generating metrics: {str(e)}\n', 500, {'Content-Type': 'text/plain'}