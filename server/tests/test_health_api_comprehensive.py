"""Comprehensive tests for health API endpoints."""
import pytest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime
import json


class TestHealthAPI:
    """Test health check endpoints."""
    
    def test_basic_health_check(self, client):
        """Test basic health endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['service'] == 'bdc-backend'
        assert data['version'] == '1.0.0'
    
    @patch('app.api.health.db')
    @patch('app.api.health.redis')
    @patch('app.api.health.shutil')
    @patch('app.api.health.psutil')
    def test_detailed_health_check_all_healthy(self, mock_psutil, mock_shutil, mock_redis, mock_db, client):
        """Test detailed health check when all services are healthy."""
        # Mock database
        mock_db.session.execute.return_value = None
        
        # Mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.from_url.return_value = mock_redis_instance
        
        # Mock disk space
        mock_disk = Mock()
        mock_disk.free = 50 * 1024 * 1024 * 1024  # 50GB free
        mock_disk.total = 100 * 1024 * 1024 * 1024  # 100GB total
        mock_shutil.disk_usage.return_value = mock_disk
        
        # Mock memory
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_psutil.virtual_memory.return_value = mock_memory
        
        response = client.get('/api/health/detailed')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['checks']['database']['status'] == 'healthy'
        assert data['checks']['redis']['status'] == 'healthy'
        assert data['checks']['disk_space']['status'] == 'healthy'
        assert data['checks']['memory']['status'] == 'healthy'
    
    @patch('app.api.health.db')
    def test_detailed_health_check_database_unhealthy(self, mock_db, client):
        """Test detailed health check when database is unhealthy."""
        # Mock database failure
        mock_db.session.execute.side_effect = Exception('Database connection failed')
        
        response = client.get('/api/health/detailed')
        assert response.status_code == 503
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert data['checks']['database']['status'] == 'unhealthy'
        assert 'Database connection failed' in data['checks']['database']['message']
    
    @patch('app.api.health.redis')
    @patch('app.api.health.db')
    def test_detailed_health_check_redis_unhealthy(self, mock_db, mock_redis, client):
        """Test detailed health check when Redis is unhealthy."""
        # Mock database healthy
        mock_db.session.execute.return_value = None
        
        # Mock Redis failure
        mock_redis.from_url.side_effect = Exception('Redis connection failed')
        
        response = client.get('/api/health/detailed')
        assert response.status_code == 503
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert data['checks']['redis']['status'] == 'unhealthy'
        assert 'Redis connection failed' in data['checks']['redis']['message']
    
    @patch('app.api.health.shutil')
    @patch('app.api.health.redis')
    @patch('app.api.health.db')
    def test_detailed_health_check_low_disk_space(self, mock_db, mock_redis, mock_shutil, client):
        """Test detailed health check with low disk space."""
        # Mock healthy services
        mock_db.session.execute.return_value = None
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.from_url.return_value = mock_redis_instance
        
        # Mock low disk space (5% free)
        mock_disk = Mock()
        mock_disk.free = 5 * 1024 * 1024 * 1024  # 5GB free
        mock_disk.total = 100 * 1024 * 1024 * 1024  # 100GB total
        mock_shutil.disk_usage.return_value = mock_disk
        
        response = client.get('/api/health/detailed')
        assert response.status_code == 503
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert data['checks']['disk_space']['status'] == 'unhealthy'
        assert 'critical' in data['checks']['disk_space']['message']
    
    @patch('app.api.health.psutil')
    @patch('app.api.health.shutil')
    @patch('app.api.health.redis')
    @patch('app.api.health.db')
    def test_detailed_health_check_high_memory(self, mock_db, mock_redis, mock_shutil, mock_psutil, client):
        """Test detailed health check with high memory usage."""
        # Mock healthy services
        mock_db.session.execute.return_value = None
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.from_url.return_value = mock_redis_instance
        
        # Mock disk space
        mock_disk = Mock()
        mock_disk.free = 50 * 1024 * 1024 * 1024
        mock_disk.total = 100 * 1024 * 1024 * 1024
        mock_shutil.disk_usage.return_value = mock_disk
        
        # Mock high memory usage (95%)
        mock_memory = Mock()
        mock_memory.percent = 95.0
        mock_psutil.virtual_memory.return_value = mock_memory
        
        response = client.get('/api/health/detailed')
        assert response.status_code == 503
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert data['checks']['memory']['status'] == 'unhealthy'
        assert 'critical' in data['checks']['memory']['message']
    
    @patch('app.api.health.db')
    def test_database_health_check_success(self, mock_db, client):
        """Test database-specific health check success."""
        # Mock database version query
        mock_result = Mock()
        mock_result.fetchone.return_value = ('PostgreSQL 13.0',)
        mock_result.rowcount = 1
        mock_db.session.execute.return_value = mock_result
        
        response = client.get('/api/health/db')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'postgresql'
        assert 'PostgreSQL' in data['version']
    
    @patch('app.api.health.db')
    def test_database_health_check_failure(self, mock_db, client):
        """Test database-specific health check failure."""
        mock_db.session.execute.side_effect = Exception('Connection refused')
        
        response = client.get('/api/health/db')
        assert response.status_code == 503
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert 'Connection refused' in data['error']
    
    @patch('app.api.health.redis')
    def test_redis_health_check_success(self, mock_redis, client):
        """Test Redis-specific health check success."""
        # Mock Redis instance
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.set.return_value = True
        mock_redis_instance.get.return_value = b'test_value'
        mock_redis_instance.delete.return_value = 1
        mock_redis_instance.info.return_value = {
            'redis_version': '6.2.0',
            'connected_clients': 5,
            'used_memory_human': '1.5M'
        }
        mock_redis.from_url.return_value = mock_redis_instance
        
        response = client.get('/api/health/redis')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['ping'] is True
        assert data['test_operation'] == 'test_value'
        assert data['redis_version'] == '6.2.0'
        assert data['connected_clients'] == 5
    
    @patch('app.api.health.redis')
    def test_redis_health_check_failure(self, mock_redis, client):
        """Test Redis-specific health check failure."""
        mock_redis.from_url.side_effect = Exception('Connection to Redis failed')
        
        response = client.get('/api/health/redis')
        assert response.status_code == 503
        
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert 'Connection to Redis failed' in data['error']
    
    @patch('app.api.health.psutil')
    @patch('app.api.health.db')
    def test_metrics_endpoint_success(self, mock_db, mock_psutil, client):
        """Test Prometheus metrics endpoint."""
        # Mock database queries
        mock_results = [
            Mock(fetchone=lambda: (100,), rowcount=1),  # users count
            Mock(fetchone=lambda: (25,), rowcount=1),   # programs count
            Mock(fetchone=lambda: (500,), rowcount=1)   # beneficiaries count
        ]
        mock_db.session.execute.side_effect = mock_results
        
        # Mock system metrics
        mock_memory = Mock()
        mock_memory.percent = 65.5
        mock_memory.used = 8589934592  # 8GB
        mock_memory.total = 17179869184  # 16GB
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_psutil.cpu_percent.return_value = 45.2
        
        mock_disk = Mock()
        mock_disk.used = 50 * 1024 * 1024 * 1024
        mock_disk.total = 100 * 1024 * 1024 * 1024
        mock_disk.free = 50 * 1024 * 1024 * 1024
        mock_psutil.disk_usage.return_value = mock_disk
        
        response = client.get('/api/metrics')
        assert response.status_code == 200
        assert response.content_type == 'text/plain'
        
        metrics = response.data.decode()
        assert 'bdc_users_total 100' in metrics
        assert 'bdc_programs_total 25' in metrics
        assert 'bdc_beneficiaries_total 500' in metrics
        assert 'bdc_memory_usage_percent 65.5' in metrics
        assert 'bdc_cpu_usage_percent 45.2' in metrics
        assert 'bdc_app_info{version="1.0.0",service="bdc-backend"} 1' in metrics
    
    @patch('app.api.health.db')
    def test_metrics_endpoint_with_database_error(self, mock_db, client):
        """Test metrics endpoint when database queries fail."""
        # Mock database failure
        mock_db.session.execute.side_effect = Exception('Database error')
        
        response = client.get('/api/metrics')
        # Should still return 200 but with limited metrics
        assert response.status_code == 200
        
        metrics = response.data.decode()
        # Should still have app info even if database fails
        assert 'bdc_app_info{version="1.0.0",service="bdc-backend"} 1' in metrics
    
    def test_metrics_endpoint_without_psutil(self, client):
        """Test metrics endpoint when psutil is not available."""
        with patch('app.api.health.psutil', side_effect=ImportError):
            response = client.get('/api/metrics')
            assert response.status_code == 200
            
            metrics = response.data.decode()
            # Should still have basic metrics
            assert 'bdc_app_info{version="1.0.0",service="bdc-backend"} 1' in metrics
            # But no system metrics
            assert 'bdc_memory_usage_percent' not in metrics
            assert 'bdc_cpu_usage_percent' not in metrics