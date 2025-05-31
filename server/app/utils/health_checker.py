"""Health check utilities for production monitoring."""

import time
import psutil
import redis
from flask import current_app, jsonify
from sqlalchemy import text
from app.extensions import db


class HealthChecker:
    """Comprehensive health checking for production deployment."""
    
    def __init__(self):
        self.checks = {
            'database': self._check_database,
            'redis': self._check_redis,
            'disk_space': self._check_disk_space,
            'memory': self._check_memory,
            'cpu': self._check_cpu,
            'dependencies': self._check_dependencies
        }
    
    def get_health_status(self, detailed=False):
        """Get overall health status."""
        start_time = time.time()
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_func in self.checks.items():
            try:
                result = check_func()
                results[check_name] = result
                
                if result['status'] != 'healthy':
                    overall_status = 'unhealthy' if result['status'] == 'unhealthy' else 'degraded'
                    
            except Exception as e:
                results[check_name] = {
                    'status': 'unhealthy',
                    'message': f'Health check failed: {str(e)}',
                    'timestamp': time.time()
                }
                overall_status = 'unhealthy'
        
        health_response = {
            'status': overall_status,
            'timestamp': time.time(),
            'response_time': round((time.time() - start_time) * 1000, 2),
            'version': current_app.config.get('VERSION', '1.0.0')
        }
        
        if detailed:
            health_response['checks'] = results
        
        return health_response
    
    def _check_database(self):
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = db.session.execute(text('SELECT 1'))
            result.fetchone()
            
            # Test write capability
            db.session.execute(text('SELECT COUNT(*) FROM users LIMIT 1'))
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            # Check for slow response
            if response_time > 1000:  # 1 second
                return {
                    'status': 'degraded',
                    'message': f'Database responding slowly: {response_time}ms',
                    'response_time': response_time,
                    'timestamp': time.time()
                }
            
            return {
                'status': 'healthy',
                'message': 'Database is responsive',
                'response_time': response_time,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_redis(self):
        """Check Redis connectivity and performance."""
        try:
            redis_url = current_app.config.get('REDIS_URL')
            if not redis_url:
                return {
                    'status': 'healthy',
                    'message': 'Redis not configured',
                    'timestamp': time.time()
                }
            
            start_time = time.time()
            redis_client = redis.Redis.from_url(redis_url)
            
            # Test basic connectivity
            redis_client.ping()
            
            # Test read/write
            test_key = 'health_check_test'
            redis_client.setex(test_key, 10, 'test_value')
            value = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            if value != b'test_value':
                raise Exception("Redis read/write test failed")
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            # Get Redis info
            info = redis_client.info()
            memory_usage = info.get('used_memory_human', 'unknown')
            
            return {
                'status': 'healthy',
                'message': 'Redis is responsive',
                'response_time': response_time,
                'memory_usage': memory_usage,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Redis connection failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_disk_space(self):
        """Check available disk space."""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_percent < 10:
                status = 'unhealthy'
                message = f'Critical: Only {free_percent:.1f}% disk space remaining'
            elif free_percent < 20:
                status = 'degraded'
                message = f'Warning: Only {free_percent:.1f}% disk space remaining'
            else:
                status = 'healthy'
                message = f'Sufficient disk space: {free_percent:.1f}% available'
            
            return {
                'status': status,
                'message': message,
                'free_percent': round(free_percent, 1),
                'free_gb': round(disk_usage.free / (1024**3), 1),
                'total_gb': round(disk_usage.total / (1024**3), 1),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Disk space check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_memory(self):
        """Check system memory usage."""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent > 90:
                status = 'unhealthy'
                message = f'Critical: {memory_percent}% memory usage'
            elif memory_percent > 80:
                status = 'degraded'
                message = f'Warning: {memory_percent}% memory usage'
            else:
                status = 'healthy'
                message = f'Normal memory usage: {memory_percent}%'
            
            return {
                'status': status,
                'message': message,
                'usage_percent': memory_percent,
                'available_gb': round(memory.available / (1024**3), 1),
                'total_gb': round(memory.total / (1024**3), 1),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Memory check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_cpu(self):
        """Check CPU usage."""
        try:
            # Get CPU usage over a short interval
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                status = 'unhealthy'
                message = f'Critical: {cpu_percent}% CPU usage'
            elif cpu_percent > 80:
                status = 'degraded'
                message = f'Warning: {cpu_percent}% CPU usage'
            else:
                status = 'healthy'
                message = f'Normal CPU usage: {cpu_percent}%'
            
            return {
                'status': status,
                'message': message,
                'usage_percent': cpu_percent,
                'cpu_count': psutil.cpu_count(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'CPU check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_dependencies(self):
        """Check critical external dependencies."""
        try:
            issues = []
            
            # Check if required environment variables are set
            required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL']
            for var in required_vars:
                if not current_app.config.get(var):
                    issues.append(f'Missing required environment variable: {var}')
            
            # Check file system permissions
            import os
            upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            if not os.path.exists(upload_dir):
                try:
                    os.makedirs(upload_dir, exist_ok=True)
                except Exception as e:
                    issues.append(f'Cannot create upload directory: {e}')
            elif not os.access(upload_dir, os.W_OK):
                issues.append(f'Upload directory not writable: {upload_dir}')
            
            if issues:
                return {
                    'status': 'degraded',
                    'message': 'Some dependencies have issues',
                    'issues': issues,
                    'timestamp': time.time()
                }
            
            return {
                'status': 'healthy',
                'message': 'All dependencies are available',
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Dependency check failed: {str(e)}',
                'timestamp': time.time()
            }


def create_health_endpoints(app):
    """Create health check endpoints."""
    
    health_checker = HealthChecker()
    
    @app.route('/health')
    def health():
        """Basic health check endpoint."""
        health_status = health_checker.get_health_status()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    
    @app.route('/health/detailed')
    def health_detailed():
        """Detailed health check endpoint."""
        health_status = health_checker.get_health_status(detailed=True)
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    
    @app.route('/ready')
    def readiness():
        """Kubernetes readiness probe endpoint."""
        health_status = health_checker.get_health_status()
        
        # Only check critical components for readiness
        critical_checks = ['database']
        for check_name in critical_checks:
            check_result = health_status.get('checks', {}).get(check_name)
            if check_result and check_result['status'] == 'unhealthy':
                return jsonify({
                    'status': 'not_ready',
                    'message': f'{check_name} is not healthy',
                    'timestamp': time.time()
                }), 503
        
        return jsonify({
            'status': 'ready',
            'message': 'Application is ready to serve traffic',
            'timestamp': time.time()
        }), 200
    
    @app.route('/live')
    def liveness():
        """Kubernetes liveness probe endpoint."""
        return jsonify({
            'status': 'alive',
            'message': 'Application is alive',
            'timestamp': time.time()
        }), 200