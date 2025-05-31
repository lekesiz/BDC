import pytest
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request

from app import create_app
from app.utils.cache import generate_cache_key, cache_response, invalidate_cache, clear_user_cache, clear_model_cache


class TestGenerateCacheKey:
    def test_generate_cache_key_basic(self):
        """Test basic cache key generation"""
        key = generate_cache_key('test_prefix')
        assert key.startswith('test_prefix:')
        assert len(key) > len('test_prefix:')
    
    def test_generate_cache_key_with_args(self):
        """Test cache key generation with args"""
        key1 = generate_cache_key('prefix', 1, 2, 3)
        key2 = generate_cache_key('prefix', 1, 2, 3)
        key3 = generate_cache_key('prefix', 1, 2, 4)
        
        # Same args should produce same key
        assert key1 == key2
        # Different args should produce different keys
        assert key1 != key3
    
    def test_generate_cache_key_with_kwargs(self):
        """Test cache key generation with kwargs"""
        key1 = generate_cache_key('prefix', user_id=1, role='admin')
        key2 = generate_cache_key('prefix', role='admin', user_id=1)  # Different order
        key3 = generate_cache_key('prefix', user_id=2, role='admin')
        
        # Same kwargs (regardless of order) should produce same key
        assert key1 == key2
        # Different kwargs should produce different keys
        assert key1 != key3
    
    def test_generate_cache_key_mixed(self):
        """Test cache key generation with both args and kwargs"""
        key = generate_cache_key('prefix', 1, 2, user_id=3, name='test')
        
        # Verify it creates a valid hash
        assert ':' in key
        prefix, hash_part = key.split(':', 1)
        assert prefix == 'prefix'
        assert len(hash_part) == 32  # MD5 hash length


class TestCacheResponse:
    @pytest.fixture
    def app(self):
        app = create_app('config.TestingConfig')
        return app
    
    @pytest.fixture
    def mock_cache(self):
        with patch('app.utils.cache.cache') as mock:
            mock.get.return_value = None  # Default to cache miss
            yield mock
    
    def test_cache_response_decorator_basic(self, app, mock_cache):
        """Test basic cache response decorator functionality"""
        
        @cache_response(timeout=60, key_prefix='test')
        def test_view():
            return {'data': 'test'}
        
        with app.test_request_context('/test'):
            # First call - cache miss
            result = test_view()
            assert result == {'data': 'test'}
            
            # Verify cache.set was called
            mock_cache.set.assert_called_once()
            call_args = mock_cache.set.call_args
            assert call_args[0][1] == {'data': 'test'}  # Cached value
            assert call_args[1]['timeout'] == 60
    
    def test_cache_response_cache_hit(self, app, mock_cache):
        """Test cache hit scenario"""
        mock_cache.get.return_value = {'cached': 'data'}
        
        @cache_response()
        def test_view():
            return {'data': 'test'}
        
        with app.test_request_context('/test'):
            result = test_view()
            assert result == {'cached': 'data'}
            
            # Function should not be called on cache hit
            mock_cache.set.assert_not_called()
    
    def test_cache_response_skip_in_debug(self, app, mock_cache):
        """Test cache is skipped in debug mode"""
        app.config['DEBUG'] = True
        app.config['CACHE_IN_DEBUG'] = False
        
        @cache_response()
        def test_view():
            return {'data': 'test'}
        
        with app.test_request_context('/test'):
            with app.app_context():
                result = test_view()
                assert result == {'data': 'test'}
                
                # Cache should not be used
                mock_cache.get.assert_not_called()
                mock_cache.set.assert_not_called()


class TestInvalidateCache:
    @pytest.fixture
    def mock_cache(self):
        with patch('app.utils.cache.cache') as mock:
            # Create nested mock for Redis client
            mock.cache._client = MagicMock()
            mock.cache._client.keys.return_value = [b'key1', b'key2', b'key3']
            yield mock
    
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_with_redis(self, mock_logger, mock_cache):
        """Test cache invalidation with Redis backend"""
        result = invalidate_cache('test_pattern')
        
        assert result == 3
        mock_cache.cache._client.keys.assert_called_once_with('test_pattern*')
        mock_cache.cache._client.delete.assert_called_once()
        mock_logger.debug.assert_called()
    
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_fallback(self, mock_logger):
        """Test cache invalidation fallback when Redis not available"""
        with patch('app.utils.cache.cache') as mock_cache:
            # No Redis client
            mock_cache.cache = None
            
            result = invalidate_cache('test_pattern')
            
            assert result == 1
            mock_cache.clear.assert_called_once()
            mock_logger.warning.assert_called()
    
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_error_handling(self, mock_logger):
        """Test error handling in cache invalidation"""
        with patch('app.utils.cache.cache') as mock_cache:
            # Simulate error
            mock_cache.cache._client.keys.side_effect = Exception('Redis error')
            
            result = invalidate_cache('test_pattern')
            
            # Should fallback to clear
            assert result == 1
            mock_cache.clear.assert_called()
            mock_logger.error.assert_called()


class TestClearCacheFunctions:
    @patch('app.utils.cache.invalidate_cache')
    def test_clear_user_cache(self, mock_invalidate):
        """Test clearing user-specific cache"""
        mock_invalidate.return_value = 5
        
        result = clear_user_cache(123)
        
        assert result == 5
        mock_invalidate.assert_called_once_with('*:user_id:123*')
    
    @patch('app.utils.cache.invalidate_cache')
    def test_clear_model_cache(self, mock_invalidate):
        """Test clearing model-specific cache"""
        mock_invalidate.return_value = 10
        
        result = clear_model_cache('User')
        
        assert result == 10
        mock_invalidate.assert_called_once_with('User:*')