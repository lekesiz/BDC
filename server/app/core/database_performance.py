"""
Enhanced Database Performance Optimization Module
Provides comprehensive database optimization including connection pooling,
query caching, index management, and performance monitoring.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Callable
from contextlib import contextmanager
from functools import wraps
from datetime import datetime, timedelta

from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.sql import func

from app.extensions import db
from app.core.cache_manager import CacheManager
from app.utils.logging import logger


class DatabasePerformanceOptimizer:
    """Comprehensive database performance optimization"""
    
    def __init__(self, app=None, cache_manager=None):
        self.app = app
        self.cache_manager = cache_manager or CacheManager()
        self.query_cache = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'slow_queries': 0,
            'average_query_time': 0.0,
            'connection_pool_hits': 0,
            'connection_pool_misses': 0
        }
        self.slow_query_threshold = 1.0  # seconds
        self.slow_queries = []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Configure connection pooling
        self._configure_connection_pooling()
        
        # Set up query performance monitoring
        self._setup_query_monitoring()
        
        # Configure session optimization
        self._configure_session_optimization()
        
        # Register cleanup handlers
        app.teardown_appcontext(self._cleanup_session)
    
    def _configure_connection_pooling(self):
        """Configure optimized database connection pooling"""
        if not self.app:
            return
        
        database_url = self.app.config.get('SQLALCHEMY_DATABASE_URI')
        if not database_url:
            return
        
        # Enhanced connection pool configuration
        pool_config = {
            'poolclass': QueuePool,
            'pool_size': self.app.config.get('DB_POOL_SIZE', 20),
            'max_overflow': self.app.config.get('DB_MAX_OVERFLOW', 30),
            'pool_timeout': self.app.config.get('DB_POOL_TIMEOUT', 30),
            'pool_recycle': self.app.config.get('DB_POOL_RECYCLE', 3600),
            'pool_pre_ping': True,  # Validate connections before use
            'pool_reset_on_return': 'commit'  # Reset connections on return
        }
        
        # Update SQLAlchemy engine options
        engine_options = self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        engine_options.update(pool_config)
        self.app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
        
        logger.info(f"Configured database connection pool: {pool_config}")
    
    def _setup_query_monitoring(self):
        """Set up query performance monitoring"""
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            # Update statistics
            self.performance_stats['total_queries'] += 1
            
            # Update average query time
            current_avg = self.performance_stats['average_query_time']
            query_count = self.performance_stats['total_queries']
            new_avg = ((current_avg * (query_count - 1)) + total_time) / query_count
            self.performance_stats['average_query_time'] = new_avg
            
            # Track slow queries
            if total_time > self.slow_query_threshold:
                self.performance_stats['slow_queries'] += 1
                self._log_slow_query(statement, parameters, total_time)
    
    def _configure_session_optimization(self):
        """Configure session-level optimizations"""
        # Configure default session options for better performance
        session_options = {
            'expire_on_commit': False,  # Don't expire objects on commit
            'autoflush': False,  # Manual flush control for better performance
        }
        
        # Apply to existing db session
        if hasattr(db, 'session') and db.session:
            for key, value in session_options.items():
                setattr(db.session, key, value)
    
    def _log_slow_query(self, statement: str, parameters: Any, execution_time: float):
        """Log slow queries for analysis"""
        slow_query_info = {
            'statement': str(statement)[:500],  # Truncate long statements
            'parameters': str(parameters)[:200] if parameters else None,
            'execution_time': execution_time,
            'timestamp': datetime.utcnow()
        }
        
        self.slow_queries.append(slow_query_info)
        
        # Keep only last 100 slow queries
        if len(self.slow_queries) > 100:
            self.slow_queries.pop(0)
        
        logger.warning(f"Slow query detected: {execution_time:.3f}s - {statement[:100]}")
    
    def _cleanup_session(self, exception=None):
        """Clean up database session"""
        try:
            if exception:
                db.session.rollback()
            else:
                db.session.commit()
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            db.session.rollback()
        finally:
            db.session.close()
    
    @contextmanager
    def optimized_session(self):
        """Context manager for optimized database sessions"""
        session = db.session
        
        # Disable autoflush for bulk operations
        original_autoflush = session.autoflush
        session.autoflush = False
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.autoflush = original_autoflush
            session.close()
    
    def cached_query(self, cache_key: str, query_func: Callable, ttl: int = 300):
        """Execute a query with caching"""
        # Check cache first
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            self.performance_stats['cache_hits'] += 1
            return cached_result
        
        # Execute query
        start_time = time.time()
        result = query_func()
        execution_time = time.time() - start_time
        
        # Update statistics
        self.performance_stats['cache_misses'] += 1
        
        # Cache the result
        self.cache_manager.set(cache_key, result, ttl)
        
        logger.debug(f"Query cached: {cache_key} (execution: {execution_time:.3f}s)")
        return result
    
    def bulk_insert_optimized(self, model_class, data: List[Dict], batch_size: int = 1000):
        """Optimized bulk insert with batching"""
        total_inserted = 0
        
        with self.optimized_session() as session:
            try:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    session.bulk_insert_mappings(model_class, batch)
                    total_inserted += len(batch)
                    
                    # Periodic commit for large datasets
                    if i % (batch_size * 10) == 0:
                        session.commit()
                
                session.commit()
                logger.info(f"Bulk inserted {total_inserted} records")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Bulk insert failed: {e}")
                raise
        
        return total_inserted
    
    def bulk_update_optimized(self, model_class, updates: List[Dict], batch_size: int = 1000):
        """Optimized bulk update with batching"""
        total_updated = 0
        
        with self.optimized_session() as session:
            try:
                for i in range(0, len(updates), batch_size):
                    batch = updates[i:i + batch_size]
                    session.bulk_update_mappings(model_class, batch)
                    total_updated += len(batch)
                    
                    # Periodic commit for large datasets
                    if i % (batch_size * 10) == 0:
                        session.commit()
                
                session.commit()
                logger.info(f"Bulk updated {total_updated} records")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Bulk update failed: {e}")
                raise
        
        return total_updated
    
    def analyze_query_performance(self, query_sql: str) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN"""
        if not db.engine:
            return {'error': 'Database engine not available'}
        
        try:
            # Execute EXPLAIN for the query
            if 'postgresql' in str(db.engine.url):
                explain_sql = f"EXPLAIN ANALYZE {query_sql}"
            else:
                explain_sql = f"EXPLAIN QUERY PLAN {query_sql}"
            
            result = db.session.execute(text(explain_sql))
            plan = [row[0] for row in result]
            
            # Analyze the execution plan
            analysis = self._analyze_execution_plan(plan)
            
            return {
                'query': query_sql,
                'execution_plan': plan,
                'analysis': analysis,
                'database_type': str(db.engine.url).split('://')[0]
            }
        
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_execution_plan(self, plan: List[str]) -> Dict[str, Any]:
        """Analyze execution plan and provide recommendations"""
        analysis = {
            'recommendations': [],
            'performance_issues': [],
            'estimated_cost': None
        }
        
        for line in plan:
            line_lower = line.lower()
            
            # Check for sequential scans
            if 'seq scan' in line_lower or 'full table scan' in line_lower:
                analysis['performance_issues'].append('Sequential scan detected')
                analysis['recommendations'].append('Consider adding an index')
            
            # Check for sorts
            if 'sort' in line_lower and 'external' in line_lower:
                analysis['performance_issues'].append('External sort operation')
                analysis['recommendations'].append('Consider increasing work_mem or adding an index')
            
            # Extract cost information
            if 'cost=' in line_lower:
                try:
                    cost_part = line.split('cost=')[1].split()[0]
                    if '..' in cost_part:
                        analysis['estimated_cost'] = float(cost_part.split('..')[1])
                except (IndexError, ValueError):
                    pass
        
        return analysis
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database performance statistics"""
        stats = {
            'performance_stats': self.performance_stats.copy(),
            'slow_queries': self.slow_queries[-10:],  # Last 10 slow queries
            'cache_hit_rate': 0.0,
            'connection_pool_info': {}
        }
        
        # Calculate cache hit rate
        total_cache_requests = stats['performance_stats']['cache_hits'] + stats['performance_stats']['cache_misses']
        if total_cache_requests > 0:
            stats['cache_hit_rate'] = (stats['performance_stats']['cache_hits'] / total_cache_requests) * 100
        
        # Get connection pool information
        if db.engine and hasattr(db.engine.pool, 'size'):
            stats['connection_pool_info'] = {
                'pool_size': db.engine.pool.size(),
                'checked_in': db.engine.pool.checkedin(),
                'checked_out': db.engine.pool.checkedout(),
                'overflow': db.engine.pool.overflow(),
                'invalid': db.engine.pool.invalidated()
            }
        
        return stats
    
    def optimize_table_statistics(self, table_names: List[str] = None):
        """Update table statistics for query optimizer"""
        if not table_names:
            # Get all table names
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
        
        for table_name in table_names:
            try:
                if 'postgresql' in str(db.engine.url):
                    db.session.execute(text(f"ANALYZE {table_name}"))
                elif 'sqlite' in str(db.engine.url):
                    db.session.execute(text(f"ANALYZE {table_name}"))
                
                logger.info(f"Updated statistics for table: {table_name}")
            
            except Exception as e:
                logger.error(f"Failed to update statistics for {table_name}: {e}")
        
        db.session.commit()
    
    def create_performance_indexes(self, force_recreate: bool = False):
        """Create performance-critical indexes"""
        from app.services.optimization.db_indexing import db_indexing_strategy
        
        try:
            results = db_indexing_strategy.optimize_database_indexes(db.session)
            
            # Update statistics after index creation
            self.optimize_table_statistics()
            
            logger.info(f"Database indexes optimized: {results}")
            return results
        
        except Exception as e:
            logger.error(f"Index optimization failed: {e}")
            return {'error': str(e)}
    
    def clear_query_cache(self):
        """Clear the query cache"""
        self.query_cache.clear()
        self.cache_manager.clear_pattern('query:*')
        logger.info("Query cache cleared")


# Global performance optimizer instance
db_performance_optimizer = DatabasePerformanceOptimizer()


def performance_monitor(operation_name: str):
    """Decorator for monitoring database operation performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"DB Operation '{operation_name}' completed in {execution_time:.3f}s")
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"DB Operation '{operation_name}' failed after {execution_time:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator


@contextmanager
def transaction_scope():
    """Provide a transactional scope around a series of operations"""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction failed: {e}")
        raise
    finally:
        session.close()