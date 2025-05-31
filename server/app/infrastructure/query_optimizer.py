"""
Database Query Optimization
Implements query optimization strategies and monitoring
"""

from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, joinedload, selectinload, subqueryload
from flask import current_app
import time
from typing import List, Dict, Any, Optional
from functools import wraps
import logging

class QueryOptimizer:
    """Database query optimization utilities"""
    
    def __init__(self, app=None):
        self.app = app
        self.slow_query_threshold = 0.5  # 500ms
        self.query_stats = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize query optimizer with Flask app"""
        self.app = app
        
        # Enable query logging in development
        if app.debug:
            self.setup_query_logging()
        
        # Setup slow query detection
        self.setup_slow_query_detection()
    
    def setup_query_logging(self):
        """Log all SQL queries in debug mode"""
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    def setup_slow_query_detection(self):
        """Detect and log slow queries"""
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
            if self.app.debug:
                self.app.logger.debug("Start Query: %s", statement)
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            
            # Log slow queries
            if total > self.slow_query_threshold:
                self.app.logger.warning(
                    f"Slow query detected ({total:.3f}s): {statement[:100]}..."
                )
            
            # Track query statistics
            query_type = statement.split()[0].upper()
            if query_type not in self.query_stats:
                self.query_stats[query_type] = {
                    'count': 0,
                    'total_time': 0,
                    'max_time': 0,
                    'min_time': float('inf')
                }
            
            stats = self.query_stats[query_type]
            stats['count'] += 1
            stats['total_time'] += total
            stats['max_time'] = max(stats['max_time'], total)
            stats['min_time'] = min(stats['min_time'], total)

class EagerLoadingStrategies:
    """Strategies for eager loading related data"""
    
    @staticmethod
    def optimize_beneficiary_query(query: Query) -> Query:
        """Optimize beneficiary queries with eager loading"""
        return query.options(
            joinedload('user'),
            selectinload('programs'),
            selectinload('appointments'),
            selectinload('evaluations').selectinload('evaluator')
        )
    
    @staticmethod
    def optimize_program_query(query: Query) -> Query:
        """Optimize program queries with eager loading"""
        return query.options(
            selectinload('beneficiaries').selectinload('user'),
            selectinload('modules'),
            selectinload('sessions'),
            joinedload('created_by')
        )
    
    @staticmethod
    def optimize_appointment_query(query: Query) -> Query:
        """Optimize appointment queries with eager loading"""
        return query.options(
            joinedload('user'),
            joinedload('beneficiary').joinedload('user'),
            selectinload('documents')
        )
    
    @staticmethod
    def optimize_evaluation_query(query: Query) -> Query:
        """Optimize evaluation queries with eager loading"""
        return query.options(
            joinedload('user'),
            joinedload('beneficiary').joinedload('user'),
            joinedload('evaluator'),
            selectinload('questions').selectinload('answers')
        )
    
    @staticmethod
    def optimize_user_query(query: Query) -> Query:
        """Optimize user queries with eager loading"""
        return query.options(
            selectinload('beneficiaries'),
            selectinload('appointments'),
            selectinload('notifications').filter_by(is_read=False),
            selectinload('documents')
        )

class QueryBatcher:
    """Batch multiple queries for efficiency"""
    
    def __init__(self, db_session):
        self.session = db_session
        self.queries = []
        self.results = {}
    
    def add_query(self, name: str, model, filters: Dict[str, Any] = None, 
                  options: List = None, limit: int = None):
        """Add a query to the batch"""
        self.queries.append({
            'name': name,
            'model': model,
            'filters': filters or {},
            'options': options or [],
            'limit': limit
        })
        return self
    
    def execute(self) -> Dict[str, Any]:
        """Execute all batched queries"""
        for query_info in self.queries:
            query = self.session.query(query_info['model'])
            
            # Apply filters
            for key, value in query_info['filters'].items():
                if hasattr(query_info['model'], key):
                    query = query.filter(getattr(query_info['model'], key) == value)
            
            # Apply options (eager loading)
            for option in query_info['options']:
                query = query.options(option)
            
            # Apply limit
            if query_info['limit']:
                query = query.limit(query_info['limit'])
            
            # Execute and store result
            self.results[query_info['name']] = query.all()
        
        return self.results

def optimize_pagination(query: Query, page: int = 1, per_page: int = 20, 
                       max_per_page: int = 100) -> Dict[str, Any]:
    """Optimize pagination with count caching"""
    from app.infrastructure.cache_config import CacheConfig
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, max_per_page)
    
    # Generate cache key for count
    cache_key = f"query_count:{hash(str(query))}"
    
    # Try to get count from cache
    cache_manager = current_app.extensions.get('cache_manager')
    total_count = None
    
    if cache_manager:
        total_count = cache_manager.get(cache_key)
    
    if total_count is None:
        # Count query optimization
        total_count = query.count()
        
        # Cache the count
        if cache_manager:
            cache_manager.set(cache_key, total_count, CacheConfig.TTL_SHORT)
    
    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    
    # Apply pagination
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

def batch_update(model, updates: List[Dict[str, Any]], batch_size: int = 100):
    """Perform batch updates efficiently"""
    from app import db
    
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        
        # Use bulk_update_mappings for efficiency
        db.session.bulk_update_mappings(model, batch)
        
        # Commit each batch
        db.session.commit()

def batch_insert(model, records: List[Dict[str, Any]], batch_size: int = 100):
    """Perform batch inserts efficiently"""
    from app import db
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        # Use bulk_insert_mappings for efficiency
        db.session.bulk_insert_mappings(model, batch)
        
        # Commit each batch
        db.session.commit()

class QueryProfiler:
    """Profile database queries for optimization"""
    
    def __init__(self):
        self.profiles = []
    
    def profile_query(self, query_name: str):
        """Decorator to profile query execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                # Execute query
                result = func(*args, **kwargs)
                
                # Record profile
                execution_time = time.time() - start_time
                self.profiles.append({
                    'name': query_name,
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'timestamp': time.time()
                })
                
                # Log slow queries
                if execution_time > 0.5:
                    current_app.logger.warning(
                        f"Slow query '{query_name}' took {execution_time:.3f}s"
                    )
                
                return result
            
            return wrapper
        return decorator
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get summary of query profiles"""
        if not self.profiles:
            return {}
        
        summary = {}
        
        for profile in self.profiles:
            name = profile['name']
            if name not in summary:
                summary[name] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'max_time': 0,
                    'min_time': float('inf')
                }
            
            stats = summary[name]
            stats['count'] += 1
            stats['total_time'] += profile['execution_time']
            stats['max_time'] = max(stats['max_time'], profile['execution_time'])
            stats['min_time'] = min(stats['min_time'], profile['execution_time'])
        
        # Calculate averages
        for name, stats in summary.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
        
        return summary

# Connection pool optimization
def optimize_connection_pool(app):
    """Optimize database connection pool settings"""
    # PostgreSQL connection pool settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Verify connections before using
        'max_overflow': 20,     # Maximum overflow connections
        'pool_timeout': 30,     # Timeout for getting connection
        'echo_pool': app.debug  # Log pool checkouts/checkins in debug
    }
    
    # Additional PostgreSQL optimizations
    if 'postgresql' in app.config.get('SQLALCHEMY_DATABASE_URI', ''):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'].update({
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'BDC_App',
                'options': '-c statement_timeout=30000'  # 30 second statement timeout
            }
        })

# Query result caching decorator
def cache_query_result(cache_key_prefix: str, ttl: int = 300):
    """Cache query results with automatic invalidation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{cache_key_prefix}:{func.__name__}"
            
            # Add arguments to cache key
            for arg in args[1:]:  # Skip 'self'
                if hasattr(arg, 'id'):
                    cache_key += f":{arg.id}"
                else:
                    cache_key += f":{str(arg)}"
            
            # Check cache
            cache_manager = current_app.extensions.get('cache_manager')
            if cache_manager:
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute query
            result = func(*args, **kwargs)
            
            # Cache result
            if cache_manager and result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator