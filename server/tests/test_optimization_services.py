"""Comprehensive tests for optimization services."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone, timedelta
import json


class TestAPIOptimizer:
    """Test cases for API optimizer."""
    
    @pytest.fixture
    def optimizer_config(self):
        """Create optimizer configuration."""
        return {
            'cache_enabled': True,
            'cache_ttl': 3600,
            'compression_enabled': True,
            'pagination_default': 20,
            'rate_limiting': True,
            'response_optimization': True,
            'query_optimization': True
        }
    
    def test_api_optimizer_init(self, optimizer_config):
        """Test API optimizer initialization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        assert optimizer.config == optimizer_config
        assert optimizer.cache_enabled is True
        assert optimizer.compression_enabled is True
    
    def test_optimize_response(self, optimizer_config):
        """Test response optimization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Large response data
        response_data = {
            'users': [
                {
                    'id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com',
                    'unnecessary_field': 'x' * 1000
                }
                for i in range(100)
            ]
        }
        
        optimized = optimizer.optimize_response(response_data, fields=['id', 'name', 'email'])
        
        # Should remove unnecessary fields
        assert 'unnecessary_field' not in optimized['users'][0]
        assert len(optimized['users']) == 100
    
    def test_apply_pagination(self, optimizer_config):
        """Test pagination optimization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Large dataset
        data = list(range(1000))
        
        paginated = optimizer.apply_pagination(data, page=2, per_page=20)
        
        assert paginated['items'] == list(range(20, 40))
        assert paginated['total'] == 1000
        assert paginated['pages'] == 50
        assert paginated['current_page'] == 2
    
    def test_cache_optimization(self, optimizer_config):
        """Test cache optimization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        with patch('app.services.optimization.api_optimizer.cache') as mock_cache:
            # First call - cache miss
            mock_cache.get.return_value = None
            
            @optimizer.cached_endpoint('test_key', ttl=3600)
            def expensive_operation():
                return {'data': 'expensive result'}
            
            result1 = expensive_operation()
            
            # Should set cache
            mock_cache.set.assert_called_once()
            
            # Second call - cache hit
            mock_cache.get.return_value = {'data': 'cached result'}
            result2 = expensive_operation()
            
            assert result2['data'] == 'cached result'
    
    def test_compression(self, optimizer_config):
        """Test response compression."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Large response
        large_data = {'content': 'x' * 10000}
        
        compressed = optimizer.compress_response(large_data)
        
        assert len(str(compressed)) < len(str(large_data))
    
    def test_query_parameter_validation(self, optimizer_config):
        """Test query parameter validation and optimization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Raw query parameters
        params = {
            'page': '2',
            'per_page': '100',
            'sort': 'name',
            'filter': 'active',
            'invalid_param': 'should_be_removed'
        }
        
        validated = optimizer.validate_query_params(
            params,
            allowed=['page', 'per_page', 'sort', 'filter'],
            max_per_page=50
        )
        
        assert validated['page'] == 2
        assert validated['per_page'] == 50  # Limited to max
        assert 'invalid_param' not in validated
    
    def test_response_field_filtering(self, optimizer_config):
        """Test response field filtering."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        data = {
            'id': 1,
            'name': 'Test',
            'email': 'test@example.com',
            'password': 'secret',
            'internal_field': 'internal'
        }
        
        filtered = optimizer.filter_response_fields(
            data,
            allowed_fields=['id', 'name', 'email'],
            exclude_fields=['password', 'internal_field']
        )
        
        assert 'password' not in filtered
        assert 'internal_field' not in filtered
        assert filtered['name'] == 'Test'
    
    def test_batch_request_optimization(self, optimizer_config):
        """Test batch request optimization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Multiple individual requests
        requests = [
            {'method': 'GET', 'endpoint': '/users/1'},
            {'method': 'GET', 'endpoint': '/users/2'},
            {'method': 'GET', 'endpoint': '/users/3'}
        ]
        
        batched = optimizer.optimize_batch_requests(requests)
        
        assert batched['method'] == 'GET'
        assert batched['endpoint'] == '/users'
        assert batched['ids'] == [1, 2, 3]
    
    def test_response_caching_strategy(self, optimizer_config):
        """Test intelligent response caching strategy."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Determine cache strategy based on endpoint
        strategy = optimizer.get_cache_strategy('/api/users')
        assert strategy['ttl'] == 3600
        assert strategy['cache_key_params'] == ['page', 'per_page', 'filter']
        
        strategy = optimizer.get_cache_strategy('/api/notifications')
        assert strategy['ttl'] == 60  # Shorter for real-time data
    
    def test_api_versioning_optimization(self, optimizer_config):
        """Test API versioning optimization."""
        from app.services.optimization.api_optimizer import APIOptimizer
        
        optimizer = APIOptimizer(optimizer_config)
        
        # Transform response based on API version
        data = {'user': {'id': 1, 'fullName': 'John Doe'}}
        
        # V1 uses snake_case
        v1_data = optimizer.transform_for_version(data, version='v1')
        assert 'full_name' in v1_data['user']
        
        # V2 uses camelCase
        v2_data = optimizer.transform_for_version(data, version='v2')
        assert 'fullName' in v2_data['user']


class TestQueryOptimizer:
    """Test cases for query optimizer."""
    
    @pytest.fixture
    def query_config(self):
        """Create query optimizer configuration."""
        return {
            'enable_query_cache': True,
            'enable_query_analysis': True,
            'slow_query_threshold': 1000,
            'optimize_joins': True,
            'optimize_pagination': True,
            'enable_query_rewriting': True
        }
    
    def test_query_optimizer_init(self, query_config):
        """Test query optimizer initialization."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        assert optimizer.config == query_config
        assert optimizer.query_cache == {}
        assert optimizer.query_stats == {}
    
    def test_optimize_select_query(self, query_config):
        """Test SELECT query optimization."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # Unoptimized query
        query = Mock()
        query._raw_query = "SELECT * FROM users WHERE status = 'active'"
        
        optimized = optimizer.optimize_query(query)
        
        # Should add specific column selection
        assert optimized != query
    
    def test_optimize_join_query(self, query_config):
        """Test JOIN query optimization."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # Query with multiple joins
        query = Mock()
        query.join.return_value = query
        query.outerjoin.return_value = query
        
        optimized = optimizer.optimize_joins(query, join_hints={
            'users': 'inner',
            'profiles': 'left',
            'unnecessary_table': None
        })
        
        # Should optimize join order and types
        assert query.join.called
    
    def test_optimize_pagination(self, query_config):
        """Test pagination optimization."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # Large dataset query
        query = Mock()
        query.count.return_value = 10000
        
        optimized = optimizer.optimize_pagination(query, page=100, per_page=20)
        
        # Should use efficient pagination strategy
        assert optimized.limit.called
        assert optimized.offset.called
    
    def test_query_caching(self, query_config):
        """Test query result caching."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # First execution
        query_key = "SELECT * FROM users WHERE id = 1"
        result1 = optimizer.execute_cached_query(
            query_key,
            lambda: [{'id': 1, 'name': 'Test'}]
        )
        
        # Second execution - should hit cache
        result2 = optimizer.execute_cached_query(
            query_key,
            lambda: [{'id': 1, 'name': 'Should not execute'}]
        )
        
        assert result1 == result2
        assert result2[0]['name'] == 'Test'
    
    def test_query_analysis(self, query_config):
        """Test query performance analysis."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # Simulate query execution
        with optimizer.analyze_query('complex_query') as analysis:
            # Simulate slow query
            import time
            time.sleep(0.1)
        
        stats = optimizer.get_query_stats('complex_query')
        
        assert stats['execution_count'] == 1
        assert stats['avg_duration'] >= 100  # milliseconds
        assert stats['is_slow'] is False  # Below threshold
    
    def test_query_rewriting(self, query_config):
        """Test automatic query rewriting."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # Inefficient query
        inefficient = """
        SELECT * FROM users u
        WHERE u.id IN (SELECT user_id FROM orders WHERE status = 'completed')
        """
        
        rewritten = optimizer.rewrite_query(inefficient)
        
        # Should rewrite to use JOIN
        assert 'JOIN' in rewritten
        assert 'IN (SELECT' not in rewritten
    
    def test_index_suggestions(self, query_config):
        """Test index suggestion generation."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        # Query without proper indexes
        query = "SELECT * FROM users WHERE email = 'test@example.com' AND status = 'active'"
        
        suggestions = optimizer.suggest_indexes(query)
        
        assert len(suggestions) > 0
        assert any('email' in s for s in suggestions)
        assert any('status' in s for s in suggestions)
    
    def test_query_plan_optimization(self, query_config):
        """Test query execution plan optimization."""
        from app.services.optimization.query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer(query_config)
        
        with patch('app.services.optimization.query_optimizer.db') as mock_db:
            # Mock query plan
            mock_db.session.execute.return_value = Mock(
                fetchall=Mock(return_value=[
                    {'QUERY PLAN': 'Seq Scan on users (cost=0.00..1000.00)'}
                ])
            )
            
            plan = optimizer.analyze_query_plan("SELECT * FROM users")
            suggestions = optimizer.optimize_query_plan(plan)
            
            assert len(suggestions) > 0
            assert any('index' in s.lower() for s in suggestions)


class TestCacheStrategy:
    """Test cases for cache strategy."""
    
    @pytest.fixture
    def cache_config(self):
        """Create cache strategy configuration."""
        return {
            'default_ttl': 3600,
            'max_cache_size': 1000,
            'eviction_policy': 'lru',
            'cache_warming': True,
            'distributed_cache': True,
            'cache_invalidation': True
        }
    
    def test_cache_strategy_init(self, cache_config):
        """Test cache strategy initialization."""
        from app.services.optimization.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(cache_config)
        
        assert strategy.config == cache_config
        assert strategy.cache_stats['hits'] == 0
        assert strategy.cache_stats['misses'] == 0
    
    def test_cache_key_generation(self, cache_config):
        """Test intelligent cache key generation."""
        from app.services.optimization.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(cache_config)
        
        # Generate cache key with various parameters
        key = strategy.generate_cache_key(
            'users',
            user_id=123,
            page=1,
            filters={'status': 'active'},
            tenant_id=1
        )
        
        assert 'users' in key
        assert '123' in key
        assert 'active' in key
    
    def test_cache_warming(self, cache_config):
        """Test cache warming functionality."""
        from app.services.optimization.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(cache_config)
        
        # Define warmup queries
        warmup_queries = [
            {'key': 'popular_users', 'query': lambda: ['user1', 'user2']},
            {'key': 'active_programs', 'query': lambda: ['program1', 'program2']}
        ]
        
        with patch('app.services.optimization.cache_strategy.cache') as mock_cache:
            strategy.warm_cache(warmup_queries)
            
            # Should cache all warmup queries
            assert mock_cache.set.call_count == 2
    
    def test_cache_invalidation_patterns(self, cache_config):
        """Test cache invalidation patterns."""
        from app.services.optimization.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(cache_config)
        
        with patch('app.services.optimization.cache_strategy.cache') as mock_cache:
            # Invalidate by pattern
            strategy.invalidate_pattern('users:*')
            mock_cache.delete_pattern.assert_called_with('users:*')
            
            # Invalidate related caches
            strategy.invalidate_related('user', user_id=123)
            assert mock_cache.delete.call_count >= 1
    
    def test_cache_ttl_strategy(self, cache_config):
        """Test dynamic TTL strategy."""
        from app.services.optimization.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(cache_config)
        
        # Different TTLs for different data types
        assert strategy.get_ttl('static_content') == 86400  # 24 hours
        assert strategy.get_ttl('user_session') == 1800    # 30 minutes
        assert strategy.get_ttl('real_time_data') == 60    # 1 minute
    
    def test_distributed_cache_sync(self, cache_config):
        """Test distributed cache synchronization."""
        from app.services.optimization.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(cache_config)
        
        with patch('app.services.optimization.cache_strategy.redis_client') as mock_redis:
            # Sync cache across instances
            strategy.sync_distributed_cache('key1', 'value1')
            
            mock_redis.publish.assert_called_once()
            
            # Handle cache sync message
            strategy.handle_cache_sync_message({
                'action': 'invalidate',
                'key': 'key1'
            })
            
            # Should invalidate local cache
            assert strategy.local_cache.get('key1') is None