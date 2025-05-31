"""Test utility functions and classes to increase coverage."""

import pytest
from app.utils.logger import configure_logger, get_logger, RequestFormatter
from app.utils.cache import generate_cache_key, cache_response, invalidate_cache, clear_user_cache, clear_model_cache
from app import create_app
import time
import logging
from flask import Flask, Request
from werkzeug.test import EnvironBuilder
from unittest.mock import patch, MagicMock


class TestLogger:
    """Test logger utility functions."""
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_logger")
        assert logger is not None
    
    def test_configure_logger(self, tmp_path):
        """Test configuring the application logger."""
        # Create a test app
        app = Flask(__name__)
        app.root_path = str(tmp_path)
        app.config['LOG_FORMAT'] = 'standard'
        app.config['LOG_LEVEL'] = 'INFO'
        
        # Configure logger
        configure_logger(app)
        
        # Check that logger is configured
        assert app.logger.level == logging.INFO
        assert len(app.logger.handlers) > 0
    
    def test_configure_logger_json_format(self, tmp_path):
        """Test configuring logger with JSON format."""
        app = Flask(__name__)
        app.root_path = str(tmp_path)
        app.config['LOG_FORMAT'] = 'json'
        app.config['LOG_LEVEL'] = 'DEBUG'
        
        configure_logger(app)
        
        assert app.logger.level == logging.DEBUG
    
    def test_request_formatter(self):
        """Test the RequestFormatter class."""
        formatter = RequestFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Format without request context
        formatted = formatter.format(record)
        assert "Test message" in formatted
        
    def test_request_formatter_with_exception(self):
        """Test formatter with exception."""
        formatter = RequestFormatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s [%(request_id)s] [%(user_id)s]'
        )
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=(Exception, Exception("Test exception"), None)
        )
        
        formatted = formatter.format(record)
        assert "Error message" in formatted


class TestCache:
    """Test cache utility functions."""
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        key = generate_cache_key("test_prefix", "arg1", "arg2", kwarg1="value1")
        assert key.startswith("test_prefix:")
        assert len(key) > len("test_prefix:")  # Should have a hash appended
    
    def test_generate_cache_key_empty_args(self):
        """Test cache key generation with no args."""
        key = generate_cache_key("test_prefix")
        assert key.startswith("test_prefix:")
    
    def test_cache_response_decorator(self, test_app):
        """Test cache response decorator."""
        with test_app.app_context():
            with test_app.test_request_context('/test?param=value'):
                call_count = 0
                
                @cache_response(timeout=60)
                def test_view():
                    nonlocal call_count
                    call_count += 1
                    return {"result": "test", "count": call_count}
                
                # Mock cache to test the decorator
                with patch('app.utils.cache.cache') as mock_cache:
                    mock_cache.get.return_value = None
                    
                    # First call should execute the function
                    result1 = test_view()
                    assert result1["count"] == 1
                    assert call_count == 1
                    mock_cache.set.assert_called_once()
                    
                    # Second call with cache hit
                    mock_cache.get.return_value = {"result": "cached", "count": 1}
                    result2 = test_view()
                    assert result2["count"] == 1
                    assert call_count == 1  # Function not called again
    
    def test_cache_response_debug_mode(self, test_app):
        """Test cache response in debug mode."""
        with test_app.app_context():
            test_app.config['DEBUG'] = True
            test_app.config['CACHE_IN_DEBUG'] = False
            
            with test_app.test_request_context('/test'):
                @cache_response(timeout=60)
                def test_view():
                    return {"result": "test"}
                
                # Should bypass cache in debug mode
                result = test_view()
                assert result["result"] == "test"
    
    def test_invalidate_cache(self):
        """Test cache invalidation."""
        with patch('app.utils.cache.cache') as mock_cache:
            # Mock Redis client
            mock_redis = MagicMock()
            mock_redis.keys.return_value = [b'test:key1', b'test:key2']
            mock_cache.cache._client = mock_redis
            
            count = invalidate_cache("test")
            assert count == 2
            mock_redis.delete.assert_called_once()
    
    def test_invalidate_cache_fallback(self):
        """Test cache invalidation fallback."""
        with patch('app.utils.cache.cache') as mock_cache:
            # Simulate no Redis client
            mock_cache.cache = {}
            
            count = invalidate_cache("test")
            assert count == 1
            mock_cache.clear.assert_called_once()
    
    def test_clear_user_cache(self):
        """Test clearing user-specific cache."""
        with patch('app.utils.cache.invalidate_cache') as mock_invalidate:
            mock_invalidate.return_value = 5
            
            count = clear_user_cache(123)
            assert count == 5
            mock_invalidate.assert_called_once_with("*:user_id:123*")
    
    def test_clear_model_cache(self):
        """Test clearing model-specific cache."""
        with patch('app.utils.cache.invalidate_cache') as mock_invalidate:
            mock_invalidate.return_value = 3
            
            count = clear_model_cache("User")
            assert count == 3
            mock_invalidate.assert_called_once_with("User:*")


class TestAppFactory:
    """Test app factory function."""
    
    def test_create_app_development(self):
        """Test creating app with development config."""
        app = create_app('development')
        assert app is not None
        assert app.config['DEBUG'] is True
    
    def test_create_app_testing(self):
        """Test creating app with testing config."""
        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_create_app_production(self):
        """Test creating app with production config."""
        app = create_app('production')
        assert app is not None
        assert app.config['DEBUG'] is False
    
    def test_create_app_default(self):
        """Test creating app with default config."""
        import os
        original_env = os.environ.get('FLASK_ENV')
        try:
            # Set environment variable
            os.environ['FLASK_ENV'] = 'testing'
            app = create_app()
            assert app is not None
            assert app.config['TESTING'] is True
        finally:
            # Restore original environment
            if original_env:
                os.environ['FLASK_ENV'] = original_env
            else:
                os.environ.pop('FLASK_ENV', None)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])