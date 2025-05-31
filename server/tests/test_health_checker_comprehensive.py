"""Comprehensive tests for health checker utility."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from app.utils.health_checker import HealthChecker, create_health_endpoints


class TestHealthChecker:
    """Test the HealthChecker class."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config['VERSION'] = '1.0.0'
        app.config['REDIS_URL'] = 'redis://localhost:6379'
        app.config['SECRET_KEY'] = 'test-secret'
        app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
        app.config['DATABASE_URL'] = 'sqlite:///test.db'
        app.config['UPLOAD_FOLDER'] = '/tmp/test_uploads'
        return app
    
    @pytest.fixture
    def health_checker(self):
        """Create a HealthChecker instance."""
        return HealthChecker()
    
    def test_health_checker_initialization(self, health_checker):
        """Test HealthChecker initialization."""
        assert 'database' in health_checker.checks
        assert 'redis' in health_checker.checks
        assert 'disk_space' in health_checker.checks
        assert 'memory' in health_checker.checks
        assert 'cpu' in health_checker.checks
        assert 'dependencies' in health_checker.checks
    
    @patch.object(HealthChecker, '_check_database')
    @patch.object(HealthChecker, '_check_redis')
    @patch.object(HealthChecker, '_check_disk_space')
    @patch.object(HealthChecker, '_check_memory')
    @patch.object(HealthChecker, '_check_cpu')
    @patch.object(HealthChecker, '_check_dependencies')
    def test_get_health_status_all_healthy(self, mock_deps, mock_cpu, mock_mem, 
                                         mock_disk, mock_redis, mock_db, 
                                         health_checker, app):
        """Test health status when all checks are healthy."""
        # Mock all checks to return healthy
        mock_db.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_redis.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_disk.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_mem.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_cpu.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_deps.return_value = {'status': 'healthy', 'message': 'OK'}
        
        with app.app_context():
            result = health_checker.get_health_status()
        
        assert result['status'] == 'healthy'
        assert 'timestamp' in result
        assert 'response_time' in result
        assert result['version'] == '1.0.0'
        assert 'checks' not in result  # No detailed checks by default
    
    @patch.object(HealthChecker, '_check_database')
    @patch.object(HealthChecker, '_check_redis')
    @patch.object(HealthChecker, '_check_disk_space')
    @patch.object(HealthChecker, '_check_memory')
    @patch.object(HealthChecker, '_check_cpu')
    @patch.object(HealthChecker, '_check_dependencies')
    def test_get_health_status_degraded(self, mock_deps, mock_cpu, mock_mem, 
                                      mock_disk, mock_redis, mock_db, 
                                      health_checker, app):
        """Test health status when some checks are degraded."""
        # Mock checks with one degraded
        mock_db.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_redis.return_value = {'status': 'degraded', 'message': 'Slow'}
        mock_disk.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_mem.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_cpu.return_value = {'status': 'healthy', 'message': 'OK'}
        mock_deps.return_value = {'status': 'healthy', 'message': 'OK'}
        
        with app.app_context():
            result = health_checker.get_health_status()
        
        assert result['status'] == 'degraded'
    
    @patch.object(HealthChecker, '_check_database')
    def test_get_health_status_unhealthy(self, mock_db, health_checker, app):
        """Test health status when a check is unhealthy."""
        # Mock database check to fail
        mock_db.return_value = {'status': 'unhealthy', 'message': 'Failed'}
        
        # Mock other checks to succeed
        with patch.object(health_checker, 'checks', {'database': mock_db}):
            with app.app_context():
                result = health_checker.get_health_status()
        
        assert result['status'] == 'unhealthy'
    
    @patch.object(HealthChecker, '_check_database')
    def test_get_health_status_exception(self, mock_db, health_checker, app):
        """Test health status when a check raises an exception."""
        # Mock database check to raise exception
        mock_db.side_effect = Exception('Database error')
        
        # Mock other checks to succeed
        with patch.object(health_checker, 'checks', {'database': mock_db}):
            with app.app_context():
                result = health_checker.get_health_status()
        
        assert result['status'] == 'unhealthy'
    
    @patch.object(HealthChecker, '_check_database')
    def test_get_health_status_detailed(self, mock_db, health_checker, app):
        """Test detailed health status."""
        mock_db.return_value = {'status': 'healthy', 'message': 'OK', 'timestamp': time.time()}
        
        with patch.object(health_checker, 'checks', {'database': mock_db}):
            with app.app_context():
                result = health_checker.get_health_status(detailed=True)
        
        assert 'checks' in result
        assert 'database' in result['checks']
        assert result['checks']['database']['status'] == 'healthy'
    
    @patch('app.utils.health_checker.db')
    def test_check_database_healthy(self, mock_db, health_checker):
        """Test database check when healthy."""
        # Mock successful database queries
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_db.session.execute.return_value = mock_result
        
        with patch('app.utils.health_checker.time.time', side_effect=[100, 100.1]):
            result = health_checker._check_database()
        
        assert result['status'] == 'healthy'
        assert result['message'] == 'Database is responsive'
        assert result['response_time'] == 100.0
        assert mock_db.session.execute.call_count == 2
    
    @patch('app.utils.health_checker.db')
    def test_check_database_slow(self, mock_db, health_checker):
        """Test database check when slow."""
        # Mock successful but slow database queries
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_db.session.execute.return_value = mock_result
        
        with patch('app.utils.health_checker.time.time', side_effect=[100, 101.5]):
            result = health_checker._check_database()
        
        assert result['status'] == 'degraded'
        assert 'slowly' in result['message']
        assert result['response_time'] == 1500.0
    
    @patch('app.utils.health_checker.db')
    def test_check_database_unhealthy(self, mock_db, health_checker):
        """Test database check when unhealthy."""
        # Mock database connection failure
        mock_db.session.execute.side_effect = Exception('Connection failed')
        
        result = health_checker._check_database()
        
        assert result['status'] == 'unhealthy'
        assert 'Connection failed' in result['message']
    
    @patch('app.utils.health_checker.redis.Redis.from_url')
    def test_check_redis_healthy(self, mock_redis_from_url, health_checker, app):
        """Test Redis check when healthy."""
        # Mock Redis client
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True
        mock_redis_client.setex.return_value = True
        mock_redis_client.get.return_value = b'test_value'
        mock_redis_client.delete.return_value = 1
        mock_redis_client.info.return_value = {'used_memory_human': '10M'}
        mock_redis_from_url.return_value = mock_redis_client
        
        with app.app_context():
            result = health_checker._check_redis()
        
        assert result['status'] == 'healthy'
        assert result['message'] == 'Redis is responsive'
        assert result['memory_usage'] == '10M'
    
    def test_check_redis_not_configured(self, health_checker, app):
        """Test Redis check when not configured."""
        app.config['REDIS_URL'] = None
        
        with app.app_context():
            result = health_checker._check_redis()
        
        assert result['status'] == 'healthy'
        assert result['message'] == 'Redis not configured'
    
    @patch('app.utils.health_checker.redis.Redis.from_url')
    def test_check_redis_unhealthy(self, mock_redis_from_url, health_checker, app):
        """Test Redis check when unhealthy."""
        # Mock Redis connection failure
        mock_redis_from_url.side_effect = Exception('Redis connection failed')
        
        with app.app_context():
            result = health_checker._check_redis()
        
        assert result['status'] == 'unhealthy'
        assert 'Redis connection failed' in result['message']
    
    @patch('app.utils.health_checker.psutil.disk_usage')
    def test_check_disk_space_healthy(self, mock_disk_usage, health_checker):
        """Test disk space check when healthy."""
        # Mock disk usage with plenty of space
        mock_usage = Mock()
        mock_usage.free = 50 * 1024**3  # 50 GB
        mock_usage.total = 100 * 1024**3  # 100 GB
        mock_disk_usage.return_value = mock_usage
        
        result = health_checker._check_disk_space()
        
        assert result['status'] == 'healthy'
        assert '50.0%' in result['message']
        assert result['free_percent'] == 50.0
        assert result['free_gb'] == 50.0
        assert result['total_gb'] == 100.0
    
    @patch('app.utils.health_checker.psutil.disk_usage')
    def test_check_disk_space_degraded(self, mock_disk_usage, health_checker):
        """Test disk space check when degraded."""
        # Mock disk usage with low space
        mock_usage = Mock()
        mock_usage.free = 15 * 1024**3  # 15 GB
        mock_usage.total = 100 * 1024**3  # 100 GB
        mock_disk_usage.return_value = mock_usage
        
        result = health_checker._check_disk_space()
        
        assert result['status'] == 'degraded'
        assert 'Warning' in result['message']
        assert result['free_percent'] == 15.0
    
    @patch('app.utils.health_checker.psutil.disk_usage')
    def test_check_disk_space_unhealthy(self, mock_disk_usage, health_checker):
        """Test disk space check when critical."""
        # Mock disk usage with critical space
        mock_usage = Mock()
        mock_usage.free = 5 * 1024**3  # 5 GB
        mock_usage.total = 100 * 1024**3  # 100 GB
        mock_disk_usage.return_value = mock_usage
        
        result = health_checker._check_disk_space()
        
        assert result['status'] == 'unhealthy'
        assert 'Critical' in result['message']
        assert result['free_percent'] == 5.0
    
    @patch('app.utils.health_checker.psutil.virtual_memory')
    def test_check_memory_healthy(self, mock_memory, health_checker):
        """Test memory check when healthy."""
        # Mock memory with normal usage
        mock_mem = Mock()
        mock_mem.percent = 60
        mock_mem.available = 8 * 1024**3  # 8 GB
        mock_mem.total = 16 * 1024**3  # 16 GB
        mock_memory.return_value = mock_mem
        
        result = health_checker._check_memory()
        
        assert result['status'] == 'healthy'
        assert '60%' in result['message']
        assert result['usage_percent'] == 60
        assert result['available_gb'] == 8.0
        assert result['total_gb'] == 16.0
    
    @patch('app.utils.health_checker.psutil.virtual_memory')
    def test_check_memory_degraded(self, mock_memory, health_checker):
        """Test memory check when degraded."""
        # Mock memory with high usage
        mock_mem = Mock()
        mock_mem.percent = 85
        mock_mem.available = 2.4 * 1024**3
        mock_mem.total = 16 * 1024**3
        mock_memory.return_value = mock_mem
        
        result = health_checker._check_memory()
        
        assert result['status'] == 'degraded'
        assert 'Warning' in result['message']
        assert result['usage_percent'] == 85
    
    @patch('app.utils.health_checker.psutil.virtual_memory')
    def test_check_memory_unhealthy(self, mock_memory, health_checker):
        """Test memory check when critical."""
        # Mock memory with critical usage
        mock_mem = Mock()
        mock_mem.percent = 95
        mock_mem.available = 0.8 * 1024**3
        mock_mem.total = 16 * 1024**3
        mock_memory.return_value = mock_mem
        
        result = health_checker._check_memory()
        
        assert result['status'] == 'unhealthy'
        assert 'Critical' in result['message']
        assert result['usage_percent'] == 95
    
    @patch('app.utils.health_checker.psutil.cpu_percent')
    @patch('app.utils.health_checker.psutil.cpu_count')
    def test_check_cpu_healthy(self, mock_cpu_count, mock_cpu_percent, health_checker):
        """Test CPU check when healthy."""
        mock_cpu_percent.return_value = 30
        mock_cpu_count.return_value = 4
        
        result = health_checker._check_cpu()
        
        assert result['status'] == 'healthy'
        assert '30%' in result['message']
        assert result['usage_percent'] == 30
        assert result['cpu_count'] == 4
    
    @patch('app.utils.health_checker.psutil.cpu_percent')
    def test_check_cpu_degraded(self, mock_cpu_percent, health_checker):
        """Test CPU check when degraded."""
        mock_cpu_percent.return_value = 85
        
        result = health_checker._check_cpu()
        
        assert result['status'] == 'degraded'
        assert 'Warning' in result['message']
        assert result['usage_percent'] == 85
    
    @patch('app.utils.health_checker.psutil.cpu_percent')
    def test_check_cpu_unhealthy(self, mock_cpu_percent, health_checker):
        """Test CPU check when critical."""
        mock_cpu_percent.return_value = 95
        
        result = health_checker._check_cpu()
        
        assert result['status'] == 'unhealthy'
        assert 'Critical' in result['message']
        assert result['usage_percent'] == 95
    
    @patch('app.utils.health_checker.os.path.exists')
    @patch('app.utils.health_checker.os.access')
    def test_check_dependencies_healthy(self, mock_access, mock_exists, health_checker, app):
        """Test dependencies check when healthy."""
        mock_exists.return_value = True
        mock_access.return_value = True
        
        with app.app_context():
            result = health_checker._check_dependencies()
        
        assert result['status'] == 'healthy'
        assert result['message'] == 'All dependencies are available'
    
    @patch('app.utils.health_checker.os.path.exists')
    def test_check_dependencies_missing_env_var(self, mock_exists, health_checker, app):
        """Test dependencies check with missing environment variable."""
        app.config['SECRET_KEY'] = None
        mock_exists.return_value = True
        
        with app.app_context():
            result = health_checker._check_dependencies()
        
        assert result['status'] == 'degraded'
        assert 'issues' in result
        assert any('SECRET_KEY' in issue for issue in result['issues'])
    
    @patch('app.utils.health_checker.os.path.exists')
    @patch('app.utils.health_checker.os.makedirs')
    def test_check_dependencies_create_upload_dir(self, mock_makedirs, mock_exists, 
                                                 health_checker, app):
        """Test dependencies check when creating upload directory."""
        mock_exists.return_value = False
        
        with app.app_context():
            result = health_checker._check_dependencies()
        
        assert result['status'] == 'healthy'
        mock_makedirs.assert_called_once_with('/tmp/test_uploads', exist_ok=True)
    
    @patch('app.utils.health_checker.os.path.exists')
    @patch('app.utils.health_checker.os.access')
    def test_check_dependencies_upload_dir_not_writable(self, mock_access, mock_exists, 
                                                       health_checker, app):
        """Test dependencies check when upload directory not writable."""
        mock_exists.return_value = True
        mock_access.return_value = False
        
        with app.app_context():
            result = health_checker._check_dependencies()
        
        assert result['status'] == 'degraded'
        assert 'issues' in result
        assert any('not writable' in issue for issue in result['issues'])


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app with health endpoints."""
        app = Flask(__name__)
        app.config['VERSION'] = '1.0.0'
        create_health_endpoints(app)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    @patch.object(HealthChecker, 'get_health_status')
    def test_health_endpoint_healthy(self, mock_get_health, client):
        """Test /health endpoint when healthy."""
        mock_get_health.return_value = {
            'status': 'healthy',
            'timestamp': time.time(),
            'response_time': 10.5,
            'version': '1.0.0'
        }
        
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    @patch.object(HealthChecker, 'get_health_status')
    def test_health_endpoint_unhealthy(self, mock_get_health, client):
        """Test /health endpoint when unhealthy."""
        mock_get_health.return_value = {
            'status': 'unhealthy',
            'timestamp': time.time(),
            'response_time': 10.5,
            'version': '1.0.0'
        }
        
        response = client.get('/health')
        
        assert response.status_code == 503
        data = response.get_json()
        assert data['status'] == 'unhealthy'
    
    @patch.object(HealthChecker, 'get_health_status')
    def test_health_detailed_endpoint(self, mock_get_health, client):
        """Test /health/detailed endpoint."""
        mock_get_health.return_value = {
            'status': 'healthy',
            'timestamp': time.time(),
            'response_time': 10.5,
            'version': '1.0.0',
            'checks': {
                'database': {'status': 'healthy', 'message': 'OK'},
                'redis': {'status': 'healthy', 'message': 'OK'}
            }
        }
        
        response = client.get('/health/detailed')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'checks' in data
        mock_get_health.assert_called_with(detailed=True)
    
    @patch.object(HealthChecker, 'get_health_status')
    def test_readiness_endpoint_ready(self, mock_get_health, client):
        """Test /ready endpoint when ready."""
        mock_get_health.return_value = {
            'status': 'healthy',
            'checks': {
                'database': {'status': 'healthy', 'message': 'OK'}
            }
        }
        
        response = client.get('/ready')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ready'
    
    @patch.object(HealthChecker, 'get_health_status')
    def test_readiness_endpoint_not_ready(self, mock_get_health, client):
        """Test /ready endpoint when not ready."""
        mock_get_health.return_value = {
            'status': 'unhealthy',
            'checks': {
                'database': {'status': 'unhealthy', 'message': 'Connection failed'}
            }
        }
        
        response = client.get('/ready')
        
        assert response.status_code == 503
        data = response.get_json()
        assert data['status'] == 'not_ready'
        assert 'database' in data['message']
    
    def test_liveness_endpoint(self, client):
        """Test /live endpoint."""
        response = client.get('/live')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'alive'
        assert 'timestamp' in data