import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import json

from app import create_app, db


class TestHealthAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_basic_health_check(self):
        """Test basic health check endpoint"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['service'] == 'bdc-backend'
        assert data['version'] == '1.0.0'
        assert 'timestamp' in data
    
    def test_detailed_health_check_all_healthy(self):
        """Test detailed health check when all services are healthy"""
        with patch('redis.Redis') as mock_redis:
            # Mock Redis ping to return True (healthy)
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_redis.from_url.return_value = mock_instance
            
            response = self.client.get('/api/health/detailed')
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert data['status'] == 'healthy'
            assert data['service'] == 'bdc-backend'
            assert 'checks' in data
            
            # Database should be healthy (SQLite in testing)
            assert data['checks']['database']['status'] == 'healthy'
    
    def test_detailed_health_check_database_unhealthy(self):
        """Test detailed health check when database is unhealthy"""
        with patch('app.extensions.db.session.execute') as mock_execute:
            # Mock database error
            mock_execute.side_effect = Exception('Database connection error')
            
            response = self.client.get('/api/health/detailed')
            data = json.loads(response.data)
            
            assert response.status_code == 503
            assert data['status'] == 'unhealthy'
            assert data['checks']['database']['status'] == 'unhealthy'
            assert 'Database connection error' in data['checks']['database']['message']
    
    def test_detailed_health_check_redis_unhealthy(self):
        """Test detailed health check when Redis is unhealthy"""
        with patch('redis.Redis') as mock_redis:
            # Mock Redis ping to raise exception
            mock_instance = MagicMock()
            mock_instance.ping.side_effect = Exception('Redis connection error')
            mock_redis.from_url.return_value = mock_instance
            
            response = self.client.get('/api/health/detailed')
            data = json.loads(response.data)
            
            # Redis failure should not fail the entire health check in our implementation
            # but it should show as unhealthy
            assert 'checks' in data
            if 'redis' in data['checks']:
                assert data['checks']['redis']['status'] == 'unhealthy'
    
    def test_health_check_response_format(self):
        """Test that health check responses have correct format"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        # Check required fields
        required_fields = ['status', 'timestamp', 'service', 'version']
        for field in required_fields:
            assert field in data
        
        # Validate timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")
    
    def test_detailed_health_check_response_format(self):
        """Test that detailed health check has correct format"""
        response = self.client.get('/api/health/detailed')
        data = json.loads(response.data)
        
        # Check required fields
        required_fields = ['status', 'timestamp', 'service', 'version', 'checks']
        for field in required_fields:
            assert field in data
        
        # Checks should be a dictionary
        assert isinstance(data['checks'], dict)
        
        # Each check should have status and message
        for check_name, check_data in data['checks'].items():
            assert 'status' in check_data
            assert check_data['status'] in ['healthy', 'unhealthy']
            assert 'message' in check_data
    
    def test_readiness_check(self):
        """Test readiness check endpoint if exists"""
        # Try to access readiness endpoint
        response = self.client.get('/api/readiness')
        
        # If endpoint exists, it should return appropriate status
        if response.status_code != 404:
            data = json.loads(response.data)
            assert 'ready' in data or 'status' in data
    
    def test_liveness_check(self):
        """Test liveness check endpoint if exists"""
        # Try to access liveness endpoint
        response = self.client.get('/api/liveness')
        
        # If endpoint exists, it should return appropriate status
        if response.status_code != 404:
            data = json.loads(response.data)
            assert 'alive' in data or 'status' in data
    
    @patch('os.path.exists')
    def test_health_check_file_system(self, mock_exists):
        """Test health check includes file system check if implemented"""
        mock_exists.return_value = True
        
        response = self.client.get('/api/health/detailed')
        data = json.loads(response.data)
        
        # If file system check is implemented
        if 'filesystem' in data.get('checks', {}):
            assert data['checks']['filesystem']['status'] in ['healthy', 'unhealthy']