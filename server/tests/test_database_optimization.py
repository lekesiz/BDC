"""Comprehensive tests for database optimization utilities."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone, timedelta
import json


class TestDatabaseOptimization:
    """Test cases for database optimization."""
    
    @pytest.fixture
    def db_config(self):
        """Create database optimization configuration."""
        return {
            'auto_vacuum': True,
            'auto_analyze': True,
            'index_optimization': True,
            'query_timeout': 30000,
            'connection_pool_size': 20,
            'enable_query_stats': True,
            'slow_query_log': True,
            'maintenance_window': {'start': '02:00', 'end': '04:00'}
        }
    
    def test_database_optimizer_init(self, db_config):
        """Test database optimizer initialization."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        assert optimizer.config == db_config
        assert optimizer.optimization_history == []
        assert optimizer.is_maintenance_mode is False
    
    @patch('app.utils.database.optimization.db')
    def test_analyze_table_statistics(self, mock_db, db_config):
        """Test analyzing table statistics."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Mock table statistics
        mock_db.session.execute.return_value.fetchall.return_value = [
            {'table_name': 'users', 'row_count': 10000, 'dead_tuples': 500},
            {'table_name': 'beneficiaries', 'row_count': 5000, 'dead_tuples': 100}
        ]
        
        stats = optimizer.analyze_table_statistics()
        
        assert len(stats) == 2
        assert stats[0]['table_name'] == 'users'
        assert stats[0]['fragmentation'] > 0
    
    @patch('app.utils.database.optimization.db')
    def test_vacuum_tables(self, mock_db, db_config):
        """Test vacuum operation on tables."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Execute vacuum
        result = optimizer.vacuum_tables(['users', 'beneficiaries'])
        
        assert result['success'] is True
        assert result['tables_vacuumed'] == 2
        mock_db.session.execute.assert_called()
    
    @patch('app.utils.database.optimization.db')
    def test_optimize_indexes(self, mock_db, db_config):
        """Test index optimization."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Mock index usage stats
        mock_db.session.execute.return_value.fetchall.return_value = [
            {
                'indexname': 'users_email_idx',
                'idx_scan': 1000,
                'idx_tup_read': 5000,
                'idx_tup_fetch': 4500
            },
            {
                'indexname': 'unused_idx',
                'idx_scan': 0,
                'idx_tup_read': 0,
                'idx_tup_fetch': 0
            }
        ]
        
        recommendations = optimizer.optimize_indexes()
        
        assert len(recommendations) > 0
        assert any('remove' in r.lower() and 'unused_idx' in r for r in recommendations)
    
    @patch('app.utils.database.optimization.db')
    def test_connection_pool_optimization(self, mock_db, db_config):
        """Test connection pool optimization."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Mock connection stats
        mock_db.engine.pool.size.return_value = 20
        mock_db.engine.pool.checked_in.return_value = 15
        mock_db.engine.pool.checked_out.return_value = 5
        mock_db.engine.pool.overflow.return_value = 0
        
        stats = optimizer.analyze_connection_pool()
        
        assert stats['pool_size'] == 20
        assert stats['active_connections'] == 5
        assert stats['idle_connections'] == 15
        assert stats['utilization'] == 25.0
    
    @patch('app.utils.database.optimization.db')
    def test_slow_query_analysis(self, mock_db, db_config):
        """Test slow query analysis."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Mock slow queries
        mock_db.session.execute.return_value.fetchall.return_value = [
            {
                'query': 'SELECT * FROM large_table',
                'total_time': 5000,
                'calls': 100,
                'mean_time': 50
            }
        ]
        
        slow_queries = optimizer.analyze_slow_queries()
        
        assert len(slow_queries) == 1
        assert slow_queries[0]['optimization_suggestions'] is not None
    
    def test_maintenance_window_check(self, db_config):
        """Test maintenance window checking."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Test during maintenance window
        with patch('app.utils.database.optimization.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 2, 30)
            assert optimizer.is_maintenance_window() is True
            
            # Test outside maintenance window
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0)
            assert optimizer.is_maintenance_window() is False
    
    @patch('app.utils.database.optimization.db')
    def test_auto_maintenance(self, mock_db, db_config):
        """Test automatic maintenance execution."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        with patch.object(optimizer, 'is_maintenance_window', return_value=True):
            results = optimizer.run_auto_maintenance()
            
            assert 'vacuum' in results
            assert 'analyze' in results
            assert 'index_optimization' in results
    
    @patch('app.utils.database.optimization.db')
    def test_table_bloat_detection(self, mock_db, db_config):
        """Test table bloat detection."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Mock bloated tables
        mock_db.session.execute.return_value.fetchall.return_value = [
            {
                'schemaname': 'public',
                'tablename': 'users',
                'bloat_ratio': 1.5,
                'wasted_bytes': 10485760  # 10MB
            }
        ]
        
        bloated_tables = optimizer.detect_table_bloat()
        
        assert len(bloated_tables) == 1
        assert bloated_tables[0]['requires_vacuum'] is True
    
    @patch('app.utils.database.optimization.db')
    def test_query_plan_cache_optimization(self, mock_db, db_config):
        """Test query plan cache optimization."""
        from app.utils.database.optimization import DatabaseOptimizer
        
        optimizer = DatabaseOptimizer(db_config)
        
        # Mock cache stats
        mock_db.session.execute.return_value.fetchone.return_value = {
            'generic_plans': 1000,
            'custom_plans': 500,
            'cache_hits': 800,
            'cache_misses': 200
        }
        
        cache_stats = optimizer.optimize_query_plan_cache()
        
        assert cache_stats['hit_rate'] == 80.0
        assert 'recommendations' in cache_stats


class TestIndexingStrategy:
    """Test cases for indexing strategy."""
    
    @pytest.fixture
    def indexing_config(self):
        """Create indexing configuration."""
        return {
            'auto_create_indexes': True,
            'analyze_query_patterns': True,
            'index_maintenance': True,
            'covering_indexes': True,
            'partial_indexes': True
        }
    
    def test_indexing_strategy_init(self, indexing_config):
        """Test indexing strategy initialization."""
        from app.utils.database.indexing_strategy import IndexingStrategy
        
        strategy = IndexingStrategy(indexing_config)
        
        assert strategy.config == indexing_config
        assert strategy.index_recommendations == []
    
    @patch('app.utils.database.indexing_strategy.db')
    def test_analyze_missing_indexes(self, mock_db, indexing_config):
        """Test missing index analysis."""
        from app.utils.database.indexing_strategy import IndexingStrategy
        
        strategy = IndexingStrategy(indexing_config)
        
        # Mock query patterns
        mock_db.session.execute.return_value.fetchall.return_value = [
            {
                'table': 'users',
                'column': 'email',
                'usage_count': 1000,
                'avg_rows_examined': 5000
            }
        ]
        
        missing_indexes = strategy.analyze_missing_indexes()
        
        assert len(missing_indexes) > 0
        assert missing_indexes[0]['table'] == 'users'
        assert missing_indexes[0]['columns'] == ['email']
    
    @patch('app.utils.database.indexing_strategy.db')
    def test_create_covering_index(self, mock_db, indexing_config):
        """Test covering index creation."""
        from app.utils.database.indexing_strategy import IndexingStrategy
        
        strategy = IndexingStrategy(indexing_config)
        
        # Create covering index
        result = strategy.create_covering_index(
            'users',
            key_columns=['user_id'],
            include_columns=['name', 'email']
        )
        
        assert result['success'] is True
        mock_db.session.execute.assert_called()
    
    @patch('app.utils.database.indexing_strategy.db')
    def test_create_partial_index(self, mock_db, indexing_config):
        """Test partial index creation."""
        from app.utils.database.indexing_strategy import IndexingStrategy
        
        strategy = IndexingStrategy(indexing_config)
        
        # Create partial index
        result = strategy.create_partial_index(
            'orders',
            columns=['user_id', 'created_at'],
            where_clause="status = 'active'"
        )
        
        assert result['success'] is True
        assert 'WHERE' in mock_db.session.execute.call_args[0][0]
    
    @patch('app.utils.database.indexing_strategy.db')
    def test_index_usage_analysis(self, mock_db, indexing_config):
        """Test index usage analysis."""
        from app.utils.database.indexing_strategy import IndexingStrategy
        
        strategy = IndexingStrategy(indexing_config)
        
        # Mock index usage data
        mock_db.session.execute.return_value.fetchall.return_value = [
            {
                'indexname': 'users_pkey',
                'index_scans': 10000,
                'index_size': '1024 KB',
                'table_size': '10 MB'
            }
        ]
        
        usage_stats = strategy.analyze_index_usage()
        
        assert len(usage_stats) == 1
        assert usage_stats[0]['efficiency_score'] > 0
    
    def test_index_recommendation_engine(self, indexing_config):
        """Test index recommendation engine."""
        from app.utils.database.indexing_strategy import IndexingStrategy
        
        strategy = IndexingStrategy(indexing_config)
        
        # Provide query workload
        workload = [
            "SELECT * FROM users WHERE email = 'test@example.com'",
            "SELECT * FROM users WHERE created_at > '2024-01-01' ORDER BY created_at",
            "SELECT * FROM orders o JOIN users u ON o.user_id = u.id WHERE o.status = 'pending'"
        ]
        
        recommendations = strategy.generate_index_recommendations(workload)
        
        assert len(recommendations) > 0
        assert any('email' in r['columns'] for r in recommendations)


class TestDatabaseBackup:
    """Test cases for database backup functionality."""
    
    @pytest.fixture
    def backup_config(self):
        """Create backup configuration."""
        return {
            'backup_method': 'pg_dump',
            'backup_location': '/backups',
            'retention_days': 7,
            'compression': True,
            'parallel_jobs': 4,
            'incremental': True
        }
    
    def test_backup_manager_init(self, backup_config):
        """Test backup manager initialization."""
        from app.utils.database.backup import BackupManager
        
        manager = BackupManager(backup_config)
        
        assert manager.config == backup_config
        assert manager.backup_history == []
    
    @patch('subprocess.run')
    def test_create_full_backup(self, mock_subprocess, backup_config):
        """Test full database backup creation."""
        from app.utils.database.backup import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock successful backup
        mock_subprocess.return_value = Mock(returncode=0)
        
        backup_info = manager.create_full_backup('mydb')
        
        assert backup_info['type'] == 'full'
        assert backup_info['status'] == 'success'
        assert 'filename' in backup_info
    
    @patch('subprocess.run')
    def test_create_incremental_backup(self, mock_subprocess, backup_config):
        """Test incremental backup creation."""
        from app.utils.database.backup import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock successful backup
        mock_subprocess.return_value = Mock(returncode=0)
        
        # Set last backup info
        manager.last_backup = {
            'timestamp': datetime.now() - timedelta(hours=6),
            'lsn': '1/23456789'
        }
        
        backup_info = manager.create_incremental_backup('mydb')
        
        assert backup_info['type'] == 'incremental'
        assert backup_info['base_backup'] is not None
    
    def test_backup_retention_policy(self, backup_config):
        """Test backup retention policy enforcement."""
        from app.utils.database.backup import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Add old backups
        old_date = datetime.now() - timedelta(days=10)
        manager.backup_history = [
            {'filename': 'old_backup.sql', 'timestamp': old_date},
            {'filename': 'recent_backup.sql', 'timestamp': datetime.now()}
        ]
        
        with patch('os.remove') as mock_remove:
            manager.enforce_retention_policy()
            
            # Should remove old backup
            mock_remove.assert_called_once_with('/backups/old_backup.sql')
    
    @patch('subprocess.run')
    def test_restore_backup(self, mock_subprocess, backup_config):
        """Test database restoration from backup."""
        from app.utils.database.backup import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock successful restore
        mock_subprocess.return_value = Mock(returncode=0)
        
        result = manager.restore_backup('backup_20240101.sql', 'mydb')
        
        assert result['status'] == 'success'
        mock_subprocess.assert_called()
    
    def test_backup_verification(self, backup_config):
        """Test backup file verification."""
        from app.utils.database.backup import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.getsize', return_value=1048576):
                with patch('subprocess.run') as mock_subprocess:
                    mock_subprocess.return_value = Mock(
                        returncode=0,
                        stdout='Backup file is valid'
                    )
                    
                    is_valid = manager.verify_backup('backup.sql')
                    
                    assert is_valid is True