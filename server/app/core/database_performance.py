"""Database performance optimization utilities."""

import time
import logging
from functools import wraps
from typing import Dict, Any, Callable
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import Pool
from flask import current_app

logger = logging.getLogger(__name__)


class DatabasePerformanceOptimizer:
    """Database performance optimization strategies."""
    
    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
        self.query_stats = {}
        self.enable_monitoring = True
        self.app = None
    
    def init_app(self, app):
        """Initialize with Flask app."""
        self.app = app
        if hasattr(app, 'extensions') and 'sqlalchemy' in app.extensions:
            db = app.extensions['sqlalchemy']
            if hasattr(db, 'engine'):
                setup_sqlalchemy_monitoring(db.engine)
        logger.info("Database performance optimizer initialized")
        
    def analyze_query_performance(self, query: str, execution_time: float):
        """Analyze query performance and log slow queries."""
        if execution_time > self.slow_query_threshold:
            logger.warning(
                f"Slow query detected ({execution_time:.2f}s): {query[:100]}..."
            )
            
        # Track query statistics
        query_hash = hash(query)
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                'query': query[:100],
                'count': 0,
                'total_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            }
            
        stats = self.query_stats[query_hash]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report for all tracked queries."""
        report = []
        
        for query_hash, stats in self.query_stats.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            report.append({
                'query': stats['query'],
                'count': stats['count'],
                'avg_time': avg_time,
                'max_time': stats['max_time'],
                'min_time': stats['min_time'] if stats['min_time'] != float('inf') else 0,
                'total_time': stats['total_time']
            })
            
        # Sort by total time descending
        report.sort(key=lambda x: x['total_time'], reverse=True)
        
        return {
            'slow_query_threshold': self.slow_query_threshold,
            'total_queries': sum(s['count'] for s in self.query_stats.values()),
            'unique_queries': len(self.query_stats),
            'top_queries': report[:10]  # Top 10 most time-consuming queries
        }
        
    def optimize_database_configuration(self, db_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database configuration for performance."""
        optimized_config = db_config.copy()
        
        # Connection pool optimization
        optimized_config.setdefault('pool_size', 10)
        optimized_config.setdefault('max_overflow', 20)
        optimized_config.setdefault('pool_timeout', 30)
        optimized_config.setdefault('pool_recycle', 3600)
        optimized_config.setdefault('pool_pre_ping', True)
        
        # Query optimization
        optimized_config.setdefault('echo', False)  # Disable SQL logging in production
        optimized_config.setdefault('echo_pool', False)
        optimized_config.setdefault('connect_args', {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 second statement timeout
        })
        
        return optimized_config
    
    def create_performance_indexes(self) -> Dict[str, Any]:
        """Create performance indexes for the database."""
        from app.services.optimization import db_indexing_strategy
        from app.extensions import db
        
        if db and hasattr(db, 'engine'):
            return db_indexing_strategy.analyze_and_create_indexes(db.engine)
        return {'error': 'Database engine not available'}
    
    def optimize_table_statistics(self) -> None:
        """Update database table statistics for query optimization."""
        from app.extensions import db
        
        try:
            with db.engine.connect() as conn:
                # PostgreSQL ANALYZE command
                conn.execute(text("ANALYZE"))
                logger.info("Database table statistics updated")
        except Exception as e:
            logger.error(f"Failed to update table statistics: {str(e)}")
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        stats = {
            'performance_stats': self.get_performance_report(),
            'connection_pool_stats': self._get_connection_pool_stats(),
            'table_stats': self._get_table_stats(),
            'index_stats': self._get_index_stats()
        }
        return stats
    
    def _get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        from app.extensions import db
        
        if db and hasattr(db, 'engine') and hasattr(db.engine.pool, 'size'):
            pool = db.engine.pool
            return {
                'pool_size': pool.size(),
                'checked_out_connections': pool.checkedout(),
                'overflow': pool.overflow(),
                'total': pool.size() + pool.overflow()
            }
        return {}
    
    def _get_table_stats(self) -> list:
        """Get table statistics."""
        from app.extensions import db
        
        stats = []
        try:
            query = """
            SELECT 
                schemaname,
                tablename,
                n_live_tup as row_count,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY n_live_tup DESC
            LIMIT 10
            """
            
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                for row in result:
                    stats.append({
                        'schema': row[0],
                        'table': row[1],
                        'row_count': row[2],
                        'total_size': row[3]
                    })
        except Exception as e:
            logger.error(f"Failed to get table stats: {str(e)}")
            
        return stats
    
    def _get_index_stats(self) -> list:
        """Get index statistics."""
        from app.extensions import db
        
        stats = []
        try:
            query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan as scan_count,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
            LIMIT 10
            """
            
            with db.engine.connect() as conn:
                result = conn.execute(text(query))
                for row in result:
                    stats.append({
                        'schema': row[0],
                        'table': row[1],
                        'index': row[2],
                        'scan_count': row[3],
                        'size': row[4]
                    })
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            
        return stats


# Global instance
db_performance_optimizer = DatabasePerformanceOptimizer()


def performance_monitor(operation_name: str) -> Callable:
    """Decorator to monitor database operation performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if db_performance_optimizer.enable_monitoring:
                    logger.debug(
                        f"Operation '{operation_name}' completed in {execution_time:.3f}s"
                    )
                    
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Operation '{operation_name}' failed after {execution_time:.3f}s: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator


def setup_sqlalchemy_monitoring(engine: Engine):
    """Set up SQLAlchemy event listeners for performance monitoring."""
    
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        db_performance_optimizer.analyze_query_performance(statement, total)
        
    @event.listens_for(Pool, "connect")
    def on_connect(dbapi_conn, connection_record):
        """Configure connection for optimal performance."""
        # PostgreSQL specific optimizations
        with dbapi_conn.cursor() as cursor:
            # Set work_mem for better sorting/hashing performance
            cursor.execute("SET work_mem = '8MB'")
            # Enable parallel query execution
            cursor.execute("SET max_parallel_workers_per_gather = 2")
            # Optimize for read-heavy workloads
            cursor.execute("SET random_page_cost = 1.1")
            
    @event.listens_for(Pool, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy):
        """Reset connection state on checkout."""
        # Reset any session-specific settings if needed
        pass


def analyze_explain_plan(query: str, bind_params: Dict = None) -> Dict[str, Any]:
    """Analyze query execution plan."""
    from app.extensions import db
    
    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(explain_query), bind_params or {})
            plan = result.fetchone()[0]
            
        # Extract key metrics from the plan
        return {
            'execution_time': plan[0]['Execution Time'],
            'planning_time': plan[0]['Planning Time'],
            'total_cost': plan[0]['Plan']['Total Cost'],
            'plan_rows': plan[0]['Plan']['Plan Rows'],
            'plan_width': plan[0]['Plan']['Plan Width'],
            'shared_blocks_hit': plan[0]['Plan'].get('Shared Hit Blocks', 0),
            'shared_blocks_read': plan[0]['Plan'].get('Shared Read Blocks', 0),
            'temp_blocks_written': plan[0]['Plan'].get('Temp Written Blocks', 0)
        }
    except Exception as e:
        logger.error(f"Failed to analyze query plan: {str(e)}")
        return {}


def get_table_statistics(table_name: str) -> Dict[str, Any]:
    """Get table statistics for optimization."""
    from app.extensions import db
    
    stats_query = """
    SELECT 
        schemaname,
        tablename,
        n_live_tup as live_rows,
        n_dead_tup as dead_rows,
        n_mod_since_analyze as modifications_since_analyze,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze
    FROM pg_stat_user_tables
    WHERE tablename = :table_name
    """
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(stats_query), {'table_name': table_name})
            row = result.fetchone()
            
        if row:
            return {
                'schema': row[0],
                'table': row[1],
                'live_rows': row[2],
                'dead_rows': row[3],
                'modifications_since_analyze': row[4],
                'last_vacuum': row[5],
                'last_autovacuum': row[6],
                'last_analyze': row[7],
                'last_autoanalyze': row[8],
                'bloat_ratio': row[3] / row[2] if row[2] > 0 else 0
            }
    except Exception as e:
        logger.error(f"Failed to get table statistics: {str(e)}")
        
    return {}


def get_missing_indexes_recommendations() -> list:
    """Get recommendations for missing indexes based on query patterns."""
    from app.extensions import db
    
    # Query to find missing indexes based on pg_stat_user_tables
    missing_indexes_query = """
    SELECT 
        schemaname,
        tablename,
        attname,
        n_distinct,
        correlation
    FROM pg_stats
    WHERE schemaname = 'public'
    AND n_distinct > 100
    AND correlation < 0.1
    ORDER BY n_distinct DESC
    LIMIT 20
    """
    
    recommendations = []
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(missing_indexes_query))
            
            for row in result:
                recommendations.append({
                    'table': f"{row[0]}.{row[1]}",
                    'column': row[2],
                    'distinct_values': row[3],
                    'correlation': row[4],
                    'recommendation': f"CREATE INDEX idx_{row[1]}_{row[2]} ON {row[0]}.{row[1]} ({row[2]})"
                })
                
    except Exception as e:
        logger.error(f"Failed to get index recommendations: {str(e)}")
        
    return recommendations