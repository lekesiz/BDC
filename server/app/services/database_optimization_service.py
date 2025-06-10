"""Database optimization service for monitoring and improving query performance."""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query
from flask import current_app, g
from app.extensions import db
redis_client = None  # TODO: Add Redis client to extensions
from sqlalchemy import func
import json

logger = logging.getLogger(__name__)


class DatabaseOptimizationService:
    """Service for database query optimization and monitoring."""
    
    SLOW_QUERY_THRESHOLD = 0.5  # 500ms
    QUERY_CACHE_TTL = 300  # 5 minutes
    
    def __init__(self):
        self.slow_queries = []
        self.query_stats = {}
        self._setup_query_monitoring()
    
    def _setup_query_monitoring(self):
        """Set up SQLAlchemy event listeners for query monitoring."""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record query start time."""
            conn.info.setdefault('query_start_time', []).append(time.time())
            try:
                if current_app:
                    g.db_query_count = getattr(g, 'db_query_count', 0) + 1
            except RuntimeError:
                # Outside of request context
                pass
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Calculate query execution time and log slow queries."""
            total_time = time.time() - conn.info['query_start_time'].pop(-1)
            
            if total_time > self.SLOW_QUERY_THRESHOLD:
                self._log_slow_query(statement, parameters, total_time)
            
            # Update query statistics
            self._update_query_stats(statement, total_time)
    
    def _log_slow_query(self, query: str, parameters: Any, execution_time: float):
        """Log slow queries for analysis."""
        slow_query = {
            'query': query,
            'parameters': str(parameters)[:200],  # Truncate long parameters
            'execution_time': execution_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.slow_queries.append(slow_query)
        
        # Keep only last 100 slow queries in memory
        if len(self.slow_queries) > 100:
            self.slow_queries.pop(0)
        
        # Log to file
        logger.warning(f"Slow query detected ({execution_time:.3f}s): {query[:100]}...")
        
        # Store in Redis for persistence
        if redis_client:
            key = f"slow_query:{datetime.utcnow().timestamp()}"
            redis_client.setex(key, 86400, json.dumps(slow_query))  # 24 hour TTL
    
    def _update_query_stats(self, query: str, execution_time: float):
        """Update query statistics."""
        # Normalize query for statistics (remove specific values)
        normalized_query = self._normalize_query(query)
        
        if normalized_query not in self.query_stats:
            self.query_stats[normalized_query] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'avg_time': 0
            }
        
        stats = self.query_stats[normalized_query]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['avg_time'] = stats['total_time'] / stats['count']
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing specific values."""
        import re
        
        # Remove numbers
        query = re.sub(r'\b\d+\b', '?', query)
        
        # Remove string literals
        query = re.sub(r"'[^']*'", '?', query)
        query = re.sub(r'"[^"]*"', '?', query)
        
        # Remove excessive whitespace
        query = ' '.join(query.split())
        
        return query[:200]  # Truncate for storage
    
    def analyze_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Analyze table statistics for optimization."""
        inspector = inspect(db.engine)
        
        # Get table info
        columns = inspector.get_columns(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # Get row count
        row_count = db.session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()
        
        # Get table size (PostgreSQL specific)
        if db.engine.dialect.name == 'postgresql':
            size_query = text("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size(:table)) as total_size,
                    pg_size_pretty(pg_relation_size(:table)) as table_size,
                    pg_size_pretty(pg_indexes_size(:table)) as indexes_size
            """)
            size_info = db.session.execute(
                size_query, {'table': table_name}
            ).first()
        else:
            size_info = None
        
        return {
            'table_name': table_name,
            'row_count': row_count,
            'column_count': len(columns),
            'index_count': len(indexes),
            'indexes': [idx['name'] for idx in indexes],
            'size_info': dict(size_info) if size_info else None
        }
    
    def suggest_missing_indexes(self) -> List[Dict[str, Any]]:
        """Suggest missing indexes based on slow queries."""
        suggestions = []
        
        # Analyze slow queries for missing indexes
        for query_info in self.slow_queries[-50:]:  # Last 50 slow queries
            query = query_info['query'].lower()
            
            # Look for WHERE clauses without indexes
            if 'where' in query:
                # Extract table and column from WHERE clause
                # This is a simplified analysis
                import re
                
                # Find patterns like "table.column = ?"
                matches = re.findall(r'(\w+)\.(\w+)\s*=', query)
                for table, column in matches:
                    suggestion = {
                        'table': table,
                        'column': column,
                        'reason': 'Frequently used in WHERE clause',
                        'query_count': 1
                    }
                    
                    # Check if index already exists
                    if not self._index_exists(table, column):
                        suggestions.append(suggestion)
        
        # Deduplicate and count occurrences
        unique_suggestions = {}
        for s in suggestions:
            key = f"{s['table']}.{s['column']}"
            if key in unique_suggestions:
                unique_suggestions[key]['query_count'] += 1
            else:
                unique_suggestions[key] = s
        
        return sorted(
            unique_suggestions.values(),
            key=lambda x: x['query_count'],
            reverse=True
        )[:10]  # Top 10 suggestions
    
    def _index_exists(self, table: str, column: str) -> bool:
        """Check if an index exists on a column."""
        try:
            inspector = inspect(db.engine)
            indexes = inspector.get_indexes(table)
            
            for idx in indexes:
                if column in idx.get('column_names', []):
                    return True
            return False
        except:
            return False
    
    def optimize_query(self, query: Query) -> Query:
        """Apply optimizations to a query."""
        # Example optimizations
        
        # 1. Add query hints for better execution plans
        if hasattr(query, 'execution_options'):
            query = query.execution_options(synchronize_session=False)
        
        # 2. Enable query result caching
        if redis_client:
            # Generate cache key from query
            cache_key = f"query_cache:{hash(str(query))}"
            
            # Check cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        
        return query
    
    def vacuum_analyze_tables(self, tables: Optional[List[str]] = None):
        """Run VACUUM ANALYZE on tables (PostgreSQL specific)."""
        if db.engine.dialect.name != 'postgresql':
            logger.info("VACUUM ANALYZE is PostgreSQL specific")
            return
        
        if not tables:
            # Get all tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
        
        for table in tables:
            try:
                db.session.execute(text(f"VACUUM ANALYZE {table}"))
                db.session.commit()
                logger.info(f"VACUUM ANALYZE completed for {table}")
            except Exception as e:
                logger.error(f"Error running VACUUM ANALYZE on {table}: {e}")
                db.session.rollback()
    
    def get_query_performance_report(self) -> Dict[str, Any]:
        """Generate a query performance report."""
        # Get slow queries from Redis
        slow_queries_from_redis = []
        if redis_client:
            keys = redis_client.keys('slow_query:*')
            for key in keys[-20:]:  # Last 20
                data = redis_client.get(key)
                if data:
                    slow_queries_from_redis.append(json.loads(data))
        
        # Sort query stats by total time
        sorted_stats = sorted(
            [
                {
                    'query': query,
                    **stats
                }
                for query, stats in self.query_stats.items()
            ],
            key=lambda x: x['total_time'],
            reverse=True
        )[:20]  # Top 20 queries by total time
        
        return {
            'summary': {
                'total_queries': sum(s['count'] for s in self.query_stats.values()),
                'unique_queries': len(self.query_stats),
                'slow_queries_count': len(slow_queries_from_redis)
            },
            'top_queries_by_time': sorted_stats,
            'recent_slow_queries': slow_queries_from_redis[-10:],
            'missing_indexes': self.suggest_missing_indexes()
        }
    
    def create_suggested_indexes(self, dry_run: bool = True) -> List[str]:
        """Create suggested indexes."""
        suggestions = self.suggest_missing_indexes()
        created_indexes = []
        
        for suggestion in suggestions:
            index_name = f"idx_{suggestion['table']}_{suggestion['column']}"
            create_sql = f"CREATE INDEX {index_name} ON {suggestion['table']} ({suggestion['column']})"
            
            if dry_run:
                created_indexes.append(create_sql)
            else:
                try:
                    db.session.execute(text(create_sql))
                    db.session.commit()
                    created_indexes.append(f"Created: {create_sql}")
                    logger.info(f"Created index: {index_name}")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Failed to create index {index_name}: {e}")
        
        return created_indexes


# Global instance (lazy initialization)
db_optimization_service = None

def get_db_optimization_service():
    """Get or create the database optimization service instance."""
    global db_optimization_service
    if db_optimization_service is None:
        db_optimization_service = DatabaseOptimizationService()
    return db_optimization_service


# Utility functions
def cache_query_result(cache_key: str, ttl: int = 300):
    """Decorator to cache query results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if redis_client:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            # Execute query
            result = func(*args, **kwargs)
            
            # Cache result
            if redis_client and result is not None:
                redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)
                )
            
            return result
        return wrapper
    return decorator


def batch_process(items: List[Any], batch_size: int = 100):
    """Process items in batches to avoid memory issues."""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def explain_query(query: Query) -> str:
    """Get query execution plan (PostgreSQL/MySQL)."""
    compiled = query.statement.compile(compile_kwargs={"literal_binds": True})
    sql = str(compiled)
    
    if db.engine.dialect.name == 'postgresql':
        explain_sql = f"EXPLAIN ANALYZE {sql}"
    elif db.engine.dialect.name == 'mysql':
        explain_sql = f"EXPLAIN {sql}"
    else:
        return "EXPLAIN not supported for this database"
    
    result = db.session.execute(text(explain_sql))
    return '\n'.join(row[0] for row in result)