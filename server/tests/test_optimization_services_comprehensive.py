"""Comprehensive tests for optimization services."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import time

from app.services.optimization.api_optimizer import APIOptimizer
from app.services.optimization.cache_strategy import CacheStrategyService
from app.services.optimization.db_indexing import DatabaseIndexingService
from app.services.optimization.query_optimizer import QueryOptimizer


class TestAPIOptimizer:
    """Test suite for APIOptimizer."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return APIOptimizer()
    
    @pytest.fixture
    def mock_request_metrics(self):
        """Create mock request metrics."""
        return {
            'endpoint': '/api/users',
            'method': 'GET',
            'response_time': 250,  # ms
            'query_count': 5,
            'cache_hits': 2,
            'cache_misses': 3,
            'payload_size': 1024,  # bytes
            'status_code': 200
        }
    
    def test_analyze_endpoint_performance(self, optimizer):
        """Test analyzing endpoint performance."""
        endpoint = '/api/beneficiaries'
        time_range = {'hours': 24}
        
        with patch.object(optimizer, '_get_endpoint_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'avg_response_time': 350,
                'p95_response_time': 800,
                'p99_response_time': 1200,
                'total_requests': 10000,
                'error_rate': 0.02,
                'slow_queries': 15
            }
            
            analysis = optimizer.analyze_endpoint_performance(endpoint, time_range)
            
            assert analysis['endpoint'] == endpoint
            assert analysis['avg_response_time'] == 350
            assert analysis['performance_grade'] in ['A', 'B', 'C', 'D', 'F']
            assert 'recommendations' in analysis
    
    def test_optimize_pagination_strategy(self, optimizer):
        """Test optimizing pagination strategy."""
        current_config = {
            'default_page_size': 100,
            'max_page_size': 1000,
            'cursor_based': False
        }
        
        usage_patterns = {
            'avg_items_requested': 50,
            'max_items_requested': 500,
            'deep_pagination_frequency': 0.1  # 10% go beyond page 10
        }
        
        with patch.object(optimizer, '_analyze_usage_patterns', return_value=usage_patterns):
            recommendations = optimizer.optimize_pagination_strategy(current_config)
            
            assert 'optimal_page_size' in recommendations
            assert 'use_cursor_pagination' in recommendations
            assert recommendations['optimal_page_size'] <= 100  # Should reduce based on usage
    
    def test_implement_response_compression(self, optimizer):
        """Test implementing response compression."""
        with patch.object(optimizer, '_get_compression_stats') as mock_stats:
            mock_stats.return_value = {
                'uncompressed_size': 1024 * 1024,  # 1MB
                'compressed_size': 100 * 1024,      # 100KB
                'compression_ratio': 0.9,
                'time_overhead': 5  # ms
            }
            
            config = optimizer.implement_response_compression()
            
            assert config['enabled'] is True
            assert 'gzip' in config['algorithms']
            assert config['min_size'] > 0
            assert 'content_types' in config
    
    def test_optimize_database_queries(self, optimizer, mock_request_metrics):
        """Test optimizing database queries."""
        with patch.object(optimizer, '_profile_queries') as mock_profile:
            mock_profile.return_value = [
                {
                    'query': 'SELECT * FROM users WHERE ...',
                    'duration': 150,
                    'rows_examined': 10000,
                    'rows_returned': 10,
                    'uses_index': False
                },
                {
                    'query': 'SELECT * FROM beneficiaries WHERE ...',
                    'duration': 200,
                    'rows_examined': 5000,
                    'rows_returned': 20,
                    'uses_index': True
                }
            ]
            
            optimizations = optimizer.optimize_database_queries(mock_request_metrics)
            
            assert len(optimizations) >= 1
            assert optimizations[0]['issue'] == 'missing_index'
            assert 'recommendation' in optimizations[0]
    
    def test_implement_request_batching(self, optimizer):
        """Test implementing request batching."""
        endpoints = ['/api/users/{id}', '/api/beneficiaries/{id}']
        
        with patch.object(optimizer, '_analyze_request_patterns') as mock_analyze:
            mock_analyze.return_value = {
                'common_sequences': [
                    ['/api/users/1', '/api/users/2', '/api/users/3'],
                    ['/api/beneficiaries/1', '/api/beneficiaries/1/evaluations']
                ],
                'avg_requests_per_session': 15
            }
            
            batching_config = optimizer.implement_request_batching(endpoints)
            
            assert batching_config['enabled'] is True
            assert '/api/users/batch' in batching_config['batch_endpoints']
            assert batching_config['max_batch_size'] > 0
    
    def test_monitor_api_health(self, optimizer):
        """Test monitoring API health."""
        with patch.object(optimizer, '_collect_health_metrics') as mock_collect:
            mock_collect.return_value = {
                'uptime': 0.999,
                'error_rate': 0.001,
                'avg_response_time': 200,
                'active_connections': 150,
                'queue_depth': 10,
                'cpu_usage': 0.65,
                'memory_usage': 0.70
            }
            
            health_status = optimizer.monitor_api_health()
            
            assert health_status['status'] in ['healthy', 'degraded', 'critical']
            assert 'metrics' in health_status
            assert 'alerts' in health_status
            
            # Should alert on high memory usage
            if health_status['metrics']['memory_usage'] > 0.7:
                assert any('memory' in alert.lower() for alert in health_status['alerts'])


class TestCacheStrategyService:
    """Test suite for CacheStrategyService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CacheStrategyService()
    
    @pytest.fixture
    def mock_cache_config(self):
        """Create mock cache configuration."""
        return {
            'backend': 'redis',
            'default_ttl': 3600,
            'max_memory': '1GB',
            'eviction_policy': 'lru',
            'key_prefix': 'bdc'
        }
    
    def test_analyze_cache_effectiveness(self, service):
        """Test analyzing cache effectiveness."""
        time_period = {'days': 7}
        
        with patch.object(service, '_get_cache_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'hit_rate': 0.75,
                'miss_rate': 0.25,
                'eviction_rate': 0.05,
                'avg_get_time': 2,  # ms
                'avg_set_time': 5,  # ms
                'memory_usage': 0.6,
                'key_count': 50000
            }
            
            analysis = service.analyze_cache_effectiveness(time_period)
            
            assert analysis['hit_rate'] == 0.75
            assert analysis['effectiveness_score'] > 0
            assert 'recommendations' in analysis
    
    def test_optimize_cache_keys(self, service):
        """Test optimizing cache key strategy."""
        current_patterns = [
            'user:{id}',
            'beneficiary:{id}:evaluations',
            'report:type:{type}:date:{date}'
        ]
        
        with patch.object(service, '_analyze_key_patterns') as mock_analyze:
            mock_analyze.return_value = {
                'redundant_patterns': ['user:{id}:profile', 'user:{id}:settings'],
                'inefficient_patterns': ['report:*'],
                'suggested_patterns': ['user:{id}:*', 'beneficiary:{id}:*']
            }
            
            optimized = service.optimize_cache_keys(current_patterns)
            
            assert 'new_patterns' in optimized
            assert 'namespace_strategy' in optimized
            assert len(optimized['new_patterns']) > 0
    
    def test_implement_cache_warming(self, service):
        """Test implementing cache warming strategy."""
        critical_endpoints = [
            '/api/dashboard',
            '/api/beneficiaries',
            '/api/reports/recent'
        ]
        
        with patch.object(service, '_identify_cold_start_issues') as mock_identify:
            mock_identify.return_value = {
                'cold_start_penalty': 500,  # ms
                'affected_users_percent': 0.15
            }
            
            warming_strategy = service.implement_cache_warming(critical_endpoints)
            
            assert warming_strategy['enabled'] is True
            assert len(warming_strategy['warming_tasks']) > 0
            assert 'schedule' in warming_strategy
    
    def test_configure_cache_layers(self, service, mock_cache_config):
        """Test configuring multi-layer cache."""
        with patch.object(service, '_analyze_access_patterns') as mock_patterns:
            mock_patterns.return_value = {
                'hot_data_percent': 0.2,  # 20% of data gets 80% of requests
                'ttl_distribution': {
                    'short': 0.3,   # < 5 min
                    'medium': 0.5,  # 5 min - 1 hour
                    'long': 0.2     # > 1 hour
                }
            }
            
            layers = service.configure_cache_layers(mock_cache_config)
            
            assert len(layers) >= 2  # At least L1 and L2
            assert layers[0]['name'] == 'L1'
            assert layers[0]['type'] == 'memory'
            assert layers[1]['name'] == 'L2'
            assert layers[1]['type'] in ['redis', 'memcached']
    
    def test_implement_cache_invalidation(self, service):
        """Test implementing cache invalidation strategy."""
        dependencies = {
            'user': ['profile', 'settings', 'notifications'],
            'beneficiary': ['evaluations', 'documents', 'progress'],
            'report': ['data', 'visualization']
        }
        
        strategy = service.implement_cache_invalidation(dependencies)
        
        assert strategy['method'] in ['event-based', 'ttl-based', 'hybrid']
        assert 'invalidation_rules' in strategy
        assert len(strategy['invalidation_rules']) > 0
        
        # Test cascade invalidation
        assert 'cascade' in strategy
        assert strategy['cascade']['user'] == ['profile', 'settings', 'notifications']
    
    def test_monitor_cache_performance(self, service):
        """Test monitoring cache performance."""
        with patch.object(service, '_collect_performance_metrics') as mock_collect:
            mock_collect.return_value = {
                'operations': {
                    'get': {'count': 100000, 'avg_time': 2},
                    'set': {'count': 20000, 'avg_time': 5},
                    'delete': {'count': 5000, 'avg_time': 3}
                },
                'errors': {
                    'connection_errors': 10,
                    'timeout_errors': 5
                },
                'saturation': 0.75
            }
            
            monitoring = service.monitor_cache_performance()
            
            assert monitoring['health'] in ['healthy', 'warning', 'critical']
            assert 'metrics' in monitoring
            assert 'alerts' in monitoring


class TestDatabaseIndexingService:
    """Test suite for DatabaseIndexingService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return DatabaseIndexingService()
    
    @pytest.fixture
    def mock_table_stats(self):
        """Create mock table statistics."""
        return {
            'users': {
                'row_count': 50000,
                'avg_row_length': 1024,
                'index_count': 3,
                'primary_key': 'id'
            },
            'beneficiaries': {
                'row_count': 100000,
                'avg_row_length': 2048,
                'index_count': 5,
                'primary_key': 'id'
            },
            'evaluations': {
                'row_count': 500000,
                'avg_row_length': 4096,
                'index_count': 4,
                'primary_key': 'id'
            }
        }
    
    def test_analyze_missing_indexes(self, service, mock_table_stats):
        """Test analyzing missing indexes."""
        with patch.object(service, '_get_query_patterns') as mock_patterns:
            mock_patterns.return_value = [
                {
                    'query': 'SELECT * FROM users WHERE email = ?',
                    'frequency': 1000,
                    'avg_time': 50,
                    'table': 'users',
                    'columns': ['email']
                },
                {
                    'query': 'SELECT * FROM beneficiaries WHERE tenant_id = ? AND status = ?',
                    'frequency': 500,
                    'avg_time': 100,
                    'table': 'beneficiaries',
                    'columns': ['tenant_id', 'status']
                }
            ]
            
            missing_indexes = service.analyze_missing_indexes(mock_table_stats)
            
            assert len(missing_indexes) >= 1
            assert missing_indexes[0]['table'] in ['users', 'beneficiaries']
            assert 'columns' in missing_indexes[0]
            assert 'impact_score' in missing_indexes[0]
    
    def test_optimize_existing_indexes(self, service):
        """Test optimizing existing indexes."""
        current_indexes = {
            'users': [
                {'name': 'idx_email', 'columns': ['email'], 'unique': True},
                {'name': 'idx_created', 'columns': ['created_at'], 'unique': False}
            ],
            'beneficiaries': [
                {'name': 'idx_tenant', 'columns': ['tenant_id'], 'unique': False},
                {'name': 'idx_status', 'columns': ['status'], 'unique': False}
            ]
        }
        
        with patch.object(service, '_analyze_index_usage') as mock_usage:
            mock_usage.return_value = {
                'idx_created': {'usage_count': 10, 'selectivity': 0.99},
                'idx_status': {'usage_count': 1000, 'selectivity': 0.1}
            }
            
            optimizations = service.optimize_existing_indexes(current_indexes)
            
            assert 'drop' in optimizations
            assert 'modify' in optimizations
            assert 'idx_created' in optimizations['drop']  # Low usage
    
    def test_implement_composite_indexes(self, service):
        """Test implementing composite indexes."""
        query_patterns = [
            {
                'table': 'evaluations',
                'columns': ['beneficiary_id', 'created_at'],
                'frequency': 2000,
                'filter_type': 'range'
            },
            {
                'table': 'evaluations',
                'columns': ['program_id', 'status', 'score'],
                'frequency': 1500,
                'filter_type': 'equality'
            }
        ]
        
        composite_indexes = service.implement_composite_indexes(query_patterns)
        
        assert len(composite_indexes) >= 1
        assert composite_indexes[0]['table'] == 'evaluations'
        assert len(composite_indexes[0]['columns']) > 1
        assert 'column_order' in composite_indexes[0]
    
    def test_calculate_index_maintenance_cost(self, service):
        """Test calculating index maintenance cost."""
        index = {
            'table': 'evaluations',
            'columns': ['beneficiary_id', 'program_id', 'created_at'],
            'type': 'btree',
            'size': 100 * 1024 * 1024  # 100MB
        }
        
        table_activity = {
            'inserts_per_hour': 1000,
            'updates_per_hour': 500,
            'deletes_per_hour': 100
        }
        
        cost = service.calculate_index_maintenance_cost(index, table_activity)
        
        assert cost['storage_cost'] > 0
        assert cost['write_overhead'] > 0
        assert cost['total_cost'] == cost['storage_cost'] + cost['write_overhead']
        assert 'recommendation' in cost
    
    def test_generate_index_migration_plan(self, service):
        """Test generating index migration plan."""
        changes = {
            'add': [
                {'table': 'users', 'name': 'idx_email_active', 'columns': ['email', 'is_active']},
                {'table': 'beneficiaries', 'name': 'idx_tenant_status', 'columns': ['tenant_id', 'status']}
            ],
            'drop': [
                {'table': 'users', 'name': 'idx_old_field'}
            ],
            'modify': [
                {'table': 'evaluations', 'name': 'idx_composite', 'action': 'rebuild'}
            ]
        }
        
        plan = service.generate_index_migration_plan(changes)
        
        assert 'phases' in plan
        assert len(plan['phases']) > 0
        assert plan['phases'][0]['name'] == 'preparation'
        assert 'estimated_time' in plan
        assert 'rollback_plan' in plan
    
    def test_monitor_index_performance(self, service):
        """Test monitoring index performance."""
        with patch.object(service, '_collect_index_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'idx_users_email': {
                    'hits': 50000,
                    'scans': 100,
                    'maintenance_time': 50,  # ms
                    'fragmentation': 0.15
                },
                'idx_evaluations_composite': {
                    'hits': 10000,
                    'scans': 5000,
                    'maintenance_time': 200,
                    'fragmentation': 0.45
                }
            }
            
            performance = service.monitor_index_performance()
            
            assert 'healthy_indexes' in performance
            assert 'problematic_indexes' in performance
            assert 'idx_evaluations_composite' in performance['problematic_indexes']


class TestQueryOptimizer:
    """Test suite for QueryOptimizer."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance."""
        return QueryOptimizer()
    
    @pytest.fixture
    def mock_slow_query(self):
        """Create mock slow query."""
        return {
            'query': '''
                SELECT u.*, b.*, e.*
                FROM users u
                JOIN beneficiaries b ON u.id = b.user_id
                LEFT JOIN evaluations e ON b.id = e.beneficiary_id
                WHERE u.tenant_id = ? AND b.status = 'active'
                ORDER BY e.created_at DESC
                LIMIT 100
            ''',
            'execution_time': 2500,  # ms
            'rows_examined': 50000,
            'rows_returned': 100,
            'temporary_tables': True
        }
    
    def test_analyze_query_execution_plan(self, optimizer, mock_slow_query):
        """Test analyzing query execution plan."""
        with patch.object(optimizer, '_get_execution_plan') as mock_plan:
            mock_plan.return_value = {
                'type': 'nested_loop',
                'steps': [
                    {'table': 'users', 'access_type': 'full_scan', 'rows': 10000},
                    {'table': 'beneficiaries', 'access_type': 'ref', 'rows': 5},
                    {'table': 'evaluations', 'access_type': 'full_scan', 'rows': 1000}
                ],
                'cost': 50000
            }
            
            analysis = optimizer.analyze_query_execution_plan(mock_slow_query['query'])
            
            assert analysis['issues'] != []
            assert any('full_scan' in issue for issue in analysis['issues'])
            assert 'optimized_query' in analysis
    
    def test_optimize_join_order(self, optimizer):
        """Test optimizing join order."""
        joins = [
            {'table': 'users', 'size': 10000, 'selectivity': 0.1},
            {'table': 'beneficiaries', 'size': 50000, 'selectivity': 0.2},
            {'table': 'evaluations', 'size': 100000, 'selectivity': 0.05}
        ]
        
        optimized_order = optimizer.optimize_join_order(joins)
        
        # Should order by selectivity * size (smallest first)
        assert optimized_order[0]['table'] == 'users'
        assert optimized_order[-1]['table'] == 'evaluations'
    
    def test_implement_query_rewriting(self, optimizer, mock_slow_query):
        """Test implementing query rewriting."""
        rewritten = optimizer.implement_query_rewriting(mock_slow_query['query'])
        
        assert rewritten != mock_slow_query['query']
        assert 'WITH' in rewritten or 'EXISTS' in rewritten  # Common optimizations
        assert rewritten.count('SELECT') <= mock_slow_query['query'].count('SELECT')
    
    def test_suggest_materialized_views(self, optimizer):
        """Test suggesting materialized views."""
        frequent_queries = [
            {
                'query': 'SELECT COUNT(*) FROM evaluations WHERE program_id = ? AND status = ?',
                'frequency': 5000,
                'avg_time': 100
            },
            {
                'query': 'SELECT AVG(score) FROM evaluations WHERE beneficiary_id = ?',
                'frequency': 3000,
                'avg_time': 150
            }
        ]
        
        suggestions = optimizer.suggest_materialized_views(frequent_queries)
        
        assert len(suggestions) > 0
        assert 'view_name' in suggestions[0]
        assert 'definition' in suggestions[0]
        assert 'estimated_benefit' in suggestions[0]
    
    def test_optimize_subqueries(self, optimizer):
        """Test optimizing subqueries."""
        query_with_subqueries = '''
            SELECT * FROM users
            WHERE id IN (
                SELECT user_id FROM beneficiaries
                WHERE status = 'active'
            )
            AND tenant_id = (
                SELECT id FROM tenants WHERE name = 'Test'
            )
        '''
        
        optimized = optimizer.optimize_subqueries(query_with_subqueries)
        
        # Should convert to joins where beneficial
        assert 'JOIN' in optimized
        assert optimized.count('SELECT') < query_with_subqueries.count('SELECT')
    
    def test_implement_query_caching(self, optimizer):
        """Test implementing query result caching."""
        query_stats = {
            'query_hash': 'abc123',
            'frequency': 1000,
            'avg_execution_time': 50,
            'result_size': 1024,
            'volatility': 0.1  # How often results change
        }
        
        caching_strategy = optimizer.implement_query_caching(query_stats)
        
        assert caching_strategy['should_cache'] is True
        assert caching_strategy['ttl'] > 0
        assert 'cache_key_pattern' in caching_strategy
        assert 'invalidation_triggers' in caching_strategy