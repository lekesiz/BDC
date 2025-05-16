"""Tests for cache utility."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from flask import Flask, request
from app.utils.cache import generate_cache_key, cache_response, invalidate_cache, clear_user_cache, clear_model_cache
from app.extensions import cache

class TestCacheUtility:
    """Test cache utility functions."""
    
    def test_generate_cache_key_basic(self):
        """Test basic cache key generation."""
        key = generate_cache_key('users')
        assert key.startswith('users:')
        
        key = generate_cache_key('users', 1, 2, 3)
        assert key.startswith('users:')
        
        key = generate_cache_key('test', foo='bar', baz='qux')
        assert key.startswith('test:')
    
    def test_generate_cache_key_consistency(self):
        """Test cache key generation consistency."""
        key1 = generate_cache_key('test', 1, 2, foo='bar')
        key2 = generate_cache_key('test', 1, 2, foo='bar')
        assert key1 == key2
        
        key3 = generate_cache_key('test', 1, 2, foo='baz')
        assert key1 != key3
    
    def test_generate_cache_key_order_independence(self):
        """Test cache key generation is order independent for kwargs."""
        key1 = generate_cache_key('test', foo='bar', baz='qux')
        key2 = generate_cache_key('test', baz='qux', foo='bar')
        assert key1 == key2
    
    @patch('app.utils.cache.cache')
    def test_cache_response_decorator(self, mock_cache):
        """Test cache response decorator."""
        app = Flask(__name__)
        app.config['DEBUG'] = False
        
        @cache_response(timeout=300, key_prefix='test')
        def dummy_function():
            return {'result': 'test'}
        
        with app.app_context():
            with app.test_request_context('/test?foo=bar'):
                # First call - cache miss
                mock_cache.get.return_value = None
                result = dummy_function()
                
                assert result == {'result': 'test'}
                mock_cache.get.assert_called_once()
                mock_cache.set.assert_called_once()
                
                # Second call - cache hit
                mock_cache.reset_mock()
                mock_cache.get.return_value = {'cached': 'result'}
                result = dummy_function()
                
                assert result == {'cached': 'result'}
                mock_cache.get.assert_called_once()
                mock_cache.set.assert_not_called()
    
    @patch('app.utils.cache.cache')
    def test_cache_response_debug_mode(self, mock_cache):
        """Test cache response decorator in debug mode."""
        app = Flask(__name__)
        app.config['DEBUG'] = True
        
        @cache_response(timeout=300, key_prefix='test')
        def dummy_function():
            return {'result': 'test'}
        
        with app.app_context():
            with app.test_request_context('/test'):
                result = dummy_function()
                
                assert result == {'result': 'test'}
                # Cache should not be used in debug mode
                mock_cache.get.assert_not_called()
                mock_cache.set.assert_not_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_with_redis(self, mock_logger, mock_cache):
        """Test invalidate cache with Redis client."""
        # Mock Redis client
        mock_redis_client = MagicMock()
        mock_redis_client.keys.return_value = ['key1', 'key2', 'key3']
        mock_cache.cache._client = mock_redis_client
        
        result = invalidate_cache('test_pattern')
        
        assert result == 3
        mock_redis_client.keys.assert_called_once_with('test_pattern*')
        mock_redis_client.delete.assert_called_once_with('key1', 'key2', 'key3')
        mock_logger.debug.assert_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_without_redis(self, mock_logger, mock_cache):
        """Test invalidate cache without Redis client."""
        # Remove Redis client
        mock_cache.cache = MagicMock()
        del mock_cache.cache._client
        
        result = invalidate_cache('test_pattern')
        
        assert result == 1
        mock_cache.clear.assert_called_once()
        mock_logger.warning.assert_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_error(self, mock_logger, mock_cache):
        """Test invalidate cache with error."""
        # Mock Redis client with error
        mock_redis_client = MagicMock()
        mock_redis_client.keys.side_effect = Exception('Redis error')
        mock_cache.cache._client = mock_redis_client
        
        result = invalidate_cache('test_pattern')
        
        assert result == 1
        mock_cache.clear.assert_called_once()
        mock_logger.error.assert_called()
    
    def test_clear_user_cache(self):
        """Test clear user cache."""
        with patch('app.utils.cache.invalidate_cache') as mock_invalidate:
            mock_invalidate.return_value = 5
            
            result = clear_user_cache(123)
            
            assert result == 5
            mock_invalidate.assert_called_once_with('*:user_id:123*')
    
    def test_clear_model_cache(self):
        """Test clear model cache."""
        with patch('app.utils.cache.invalidate_cache') as mock_invalidate:
            mock_invalidate.return_value = 3
            
            result = clear_model_cache('beneficiary')
            
            assert result == 3
            mock_invalidate.assert_called_once_with('beneficiary:*')