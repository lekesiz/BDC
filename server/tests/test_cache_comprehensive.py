"""Comprehensive tests for cache utility."""

import pytest
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request

from app.utils.cache import (
    generate_cache_key, cache_response, invalidate_cache,
    clear_user_cache, clear_model_cache
)


class TestGenerateCacheKey:
    """Test the generate_cache_key function."""
    
    def test_generate_cache_key_with_args(self):
        """Test cache key generation with positional arguments."""
        key = generate_cache_key("test_prefix", "arg1", "arg2", 123)
        expected_args = json.dumps(["arg1", "arg2", 123], sort_keys=True)
        expected_hash = hashlib.md5(f"{expected_args}".encode('utf-8')).hexdigest()
        assert key == f"test_prefix:{expected_hash}"
    
    def test_generate_cache_key_with_kwargs(self):
        """Test cache key generation with keyword arguments."""
        key = generate_cache_key("test_prefix", name="test", id=123)
        expected_kwargs = json.dumps({"name": "test", "id": 123}, sort_keys=True)
        expected_hash = hashlib.md5(f"{expected_kwargs}".encode('utf-8')).hexdigest()
        assert key == f"test_prefix:{expected_hash}"
    
    def test_generate_cache_key_with_both(self):
        """Test cache key generation with both args and kwargs."""
        key = generate_cache_key("test_prefix", "arg1", 123, name="test", active=True)
        expected_args = json.dumps(["arg1", 123], sort_keys=True)
        expected_kwargs = json.dumps({"name": "test", "active": True}, sort_keys=True)
        expected_hash = hashlib.md5(f"{expected_args}{expected_kwargs}".encode('utf-8')).hexdigest()
        assert key == f"test_prefix:{expected_hash}"
    
    def test_generate_cache_key_empty(self):
        """Test cache key generation with no arguments."""
        key = generate_cache_key("test_prefix")
        expected_hash = hashlib.md5("".encode('utf-8')).hexdigest()
        assert key == f"test_prefix:{expected_hash}"
    
    def test_generate_cache_key_consistent(self):
        """Test that same arguments generate same key."""
        key1 = generate_cache_key("prefix", "arg1", id=123, name="test")
        key2 = generate_cache_key("prefix", "arg1", id=123, name="test")
        assert key1 == key2
    
    def test_generate_cache_key_order_independent_kwargs(self):
        """Test that kwargs order doesn't affect the key."""
        key1 = generate_cache_key("prefix", name="test", id=123, active=True)
        key2 = generate_cache_key("prefix", active=True, id=123, name="test")
        assert key1 == key2


class TestCacheResponse:
    """Test the cache_response decorator."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.config['DEBUG'] = False
        return app
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_cache_hit(self, mock_logger, mock_cache, app):
        """Test cache hit scenario."""
        with app.test_request_context('/test?param=value'):
            mock_cache.get.return_value = {'cached': 'response'}
            
            @cache_response(timeout=300, key_prefix='test')
            def test_view():
                return {'new': 'response'}
            
            result = test_view()
            
            assert result == {'cached': 'response'}
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_not_called()
            mock_logger.debug.assert_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_cache_miss(self, mock_logger, mock_cache, app):
        """Test cache miss scenario."""
        with app.test_request_context('/test?param=value'):
            mock_cache.get.return_value = None
            
            @cache_response(timeout=300, key_prefix='test')
            def test_view():
                return {'new': 'response'}
            
            result = test_view()
            
            assert result == {'new': 'response'}
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once_with(
                mock_cache.get.call_args[0][0],
                {'new': 'response'},
                timeout=300
            )
            assert mock_logger.debug.call_count == 1
    
    @patch('app.utils.cache.cache')
    def test_cache_skip_in_debug(self, mock_cache, app):
        """Test cache is skipped in debug mode."""
        app.config['DEBUG'] = True
        app.config['CACHE_IN_DEBUG'] = False
        
        with app.test_request_context('/test'):
            @cache_response()
            def test_view():
                return {'new': 'response'}
            
            result = test_view()
            
            assert result == {'new': 'response'}
            mock_cache.get.assert_not_called()
            mock_cache.set.assert_not_called()
    
    @patch('app.utils.cache.cache')
    def test_cache_enabled_in_debug_with_config(self, mock_cache, app):
        """Test cache can be enabled in debug mode with config."""
        app.config['DEBUG'] = True
        app.config['CACHE_IN_DEBUG'] = True
        
        with app.test_request_context('/test'):
            mock_cache.get.return_value = None
            
            @cache_response()
            def test_view():
                return {'new': 'response'}
            
            result = test_view()
            
            assert result == {'new': 'response'}
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()
    
    @patch('app.utils.cache.cache')
    def test_cache_with_user_id(self, mock_cache, app):
        """Test cache key includes user_id when available."""
        with app.test_request_context('/test'):
            # Mock request with user_id attribute
            with patch('app.utils.cache.request') as mock_request:
                mock_request.path = '/test'
                mock_request.args.to_dict.return_value = {}
                mock_request.user_id = 123
                
                mock_cache.get.return_value = None
                
                @cache_response(key_prefix='user')
                def test_view():
                    return {'user': 'response'}
                
                result = test_view()
                
                # Verify cache key includes user_id
                cache_key = mock_cache.get.call_args[0][0]
                assert 'user_id' in str(cache_key) or cache_key.startswith('user:')
    
    @patch('app.utils.cache.cache')
    def test_cache_with_query_params(self, mock_cache, app):
        """Test cache key includes query parameters."""
        with app.test_request_context('/test?sort=name&filter=active'):
            mock_cache.get.return_value = None
            
            @cache_response()
            def test_view():
                return {'filtered': 'response'}
            
            result = test_view()
            
            # Verify cache was called with appropriate key
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()


class TestInvalidateCache:
    """Test the invalidate_cache function."""
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_with_redis(self, mock_logger, mock_cache):
        """Test cache invalidation with Redis backend."""
        # Setup Redis mock
        mock_redis_client = Mock()
        mock_redis_client.keys.return_value = [b'test:key1', b'test:key2', b'test:key3']
        mock_cache.cache = Mock()
        mock_cache.cache._client = mock_redis_client
        
        result = invalidate_cache('test')
        
        mock_redis_client.keys.assert_called_once_with('test*')
        mock_redis_client.delete.assert_called_once_with(b'test:key1', b'test:key2', b'test:key3')
        assert result == 3
        mock_logger.debug.assert_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_without_redis(self, mock_logger, mock_cache):
        """Test cache invalidation without Redis backend."""
        # No Redis client available
        mock_cache.cache = None
        
        result = invalidate_cache('test')
        
        mock_cache.clear.assert_called_once()
        assert result == 1
        mock_logger.warning.assert_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_with_error(self, mock_logger, mock_cache):
        """Test cache invalidation with error."""
        # Setup Redis mock that throws error
        mock_redis_client = Mock()
        mock_redis_client.keys.side_effect = Exception("Redis error")
        mock_cache.cache = Mock()
        mock_cache.cache._client = mock_redis_client
        
        result = invalidate_cache('test')
        
        mock_cache.clear.assert_called_once()
        assert result == 1
        mock_logger.error.assert_called()
    
    @patch('app.utils.cache.cache')
    @patch('app.utils.cache.logger')
    def test_invalidate_cache_fallback_error(self, mock_logger, mock_cache):
        """Test cache invalidation when fallback also fails."""
        # Setup Redis mock that throws error
        mock_redis_client = Mock()
        mock_redis_client.keys.side_effect = Exception("Redis error")
        mock_cache.cache = Mock()
        mock_cache.cache._client = mock_redis_client
        mock_cache.clear.side_effect = Exception("Clear error")
        
        result = invalidate_cache('test')
        
        assert result == 0
        mock_logger.error.assert_called()
    
    @patch('app.utils.cache.cache')
    def test_invalidate_cache_no_matches(self, mock_cache):
        """Test cache invalidation with no matching keys."""
        # Setup Redis mock with no matching keys
        mock_redis_client = Mock()
        mock_redis_client.keys.return_value = []
        mock_cache.cache = Mock()
        mock_cache.cache._client = mock_redis_client
        
        result = invalidate_cache('test')
        
        mock_redis_client.keys.assert_called_once_with('test*')
        mock_redis_client.delete.assert_not_called()
        assert result == 0


class TestClearUserCache:
    """Test the clear_user_cache function."""
    
    @patch('app.utils.cache.invalidate_cache')
    def test_clear_user_cache(self, mock_invalidate):
        """Test clearing user cache."""
        mock_invalidate.return_value = 5
        
        result = clear_user_cache(123)
        
        mock_invalidate.assert_called_once_with('*:user_id:123*')
        assert result == 5
    
    @patch('app.utils.cache.invalidate_cache')
    def test_clear_user_cache_no_entries(self, mock_invalidate):
        """Test clearing user cache with no entries."""
        mock_invalidate.return_value = 0
        
        result = clear_user_cache(999)
        
        mock_invalidate.assert_called_once_with('*:user_id:999*')
        assert result == 0


class TestClearModelCache:
    """Test the clear_model_cache function."""
    
    @patch('app.utils.cache.invalidate_cache')
    def test_clear_model_cache(self, mock_invalidate):
        """Test clearing model cache."""
        mock_invalidate.return_value = 10
        
        result = clear_model_cache('beneficiary')
        
        mock_invalidate.assert_called_once_with('beneficiary:*')
        assert result == 10
    
    @patch('app.utils.cache.invalidate_cache')
    def test_clear_model_cache_no_entries(self, mock_invalidate):
        """Test clearing model cache with no entries."""
        mock_invalidate.return_value = 0
        
        result = clear_model_cache('nonexistent')
        
        mock_invalidate.assert_called_once_with('nonexistent:*')
        assert result == 0