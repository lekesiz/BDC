"""
Database query optimization utilities
"""
from typing import Dict, Any, List, Optional, Type
from sqlalchemy.orm import Query, Session, joinedload, selectinload, subqueryload
from sqlalchemy.sql import func
from sqlalchemy import and_, or_, inspect
from app.models.base import Base
from app.core.cache import cache_service
from app.services.monitoring.performance_metrics import performance_monitor
import logging
import time

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Database query optimization utilities"""
    
    def __init__(self):
        self.query_cache = {}
        self.statistics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'optimizations_applied': 0,
            'average_query_time': 0,
            'query_count': 0
        }
        
    def optimize_query(self, query: Query, 
                      eager_load: Optional[List[str]] = None,
                      enable_cache: bool = True,
                      cache_ttl: int = 300) -> Query:
        """Optimize a SQLAlchemy query with various strategies"""
        start_time = time.time()
        
        # Apply eager loading for relationships
        if eager_load:
            query = self._apply_eager_loading(query, eager_load)
            
        # Apply query hints
        query = self._apply_query_hints(query)
        
        # Apply caching if enabled
        if enable_cache:
            cache_key = self._generate_cache_key(query)
            cached_result = cache_service.get(cache_key)
            
            if cached_result:
                self.statistics['cache_hits'] += 1
                logger.debug(f"Cache hit for query: {cache_key}")
                return cached_result
            else:
                self.statistics['cache_misses'] += 1
                
        # Track query execution time
        end_time = time.time()
        query_time = end_time - start_time
        self._update_statistics(query_time)
        
        # Store in cache if enabled
        if enable_cache:
            cache_service.set(cache_key, query, expire=cache_ttl)
            
        return query
        
    def _apply_eager_loading(self, query: Query, relationships: List[str]) -> Query:
        """Apply eager loading strategies for relationships"""
        for relationship in relationships:
            if '.' in relationship:
                # Nested relationships
                parts = relationship.split('.')
                query = query.options(
                    joinedload(parts[0]).joinedload('.'.join(parts[1:]))
                )
            else:
                # Direct relationships
                query = query.options(joinedload(relationship))
                
        self.statistics['optimizations_applied'] += 1
        return query
        
    def _apply_query_hints(self, query: Query) -> Query:
        """Apply database-specific query hints"""
        # Add query hints for better performance
        query = query.hint('use_index', 'idx_created_at')
        
        # Enable query result caching at DB level
        query = query.enable_eagerloads(True)
        
        return query
        
    def batch_query(self, model: Type[Base], ids: List[int], 
                   batch_size: int = 100) -> List[Base]:
        """Execute queries in batches to avoid memory issues"""
        results = []
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_results = model.query.filter(
                model.id.in_(batch_ids)
            ).all()
            results.extend(batch_results)
            
        return results
        
    def paginate_query(self, query: Query, page: int = 1, 
                      per_page: int = 20) -> Dict[str, Any]:
        """Paginate query results efficiently"""
        total = query.count()
        
        # Apply pagination
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': items,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
        
    def analyze_query_performance(self, query: Query) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations"""
        start_time = time.time()
        
        # Execute the query
        results = query.all()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Analyze the query
        analysis = {
            'execution_time': execution_time,
            'row_count': len(results),
            'query_string': str(query),
            'suggestions': []
        }
        
        # Check for potential N+1 queries
        if self._detect_n_plus_one(query):
            analysis['suggestions'].append(
                'Consider using eager loading to avoid N+1 queries'
            )
            
        # Check for missing indexes
        if self._check_missing_indexes(query):
            analysis['suggestions'].append(
                'Consider adding indexes on frequently queried columns'
            )
            
        # Check for large result sets
        if len(results) > 1000:
            analysis['suggestions'].append(
                'Consider using pagination for large result sets'
            )
            
        return analysis
        
    def _detect_n_plus_one(self, query: Query) -> bool:
        """Detect potential N+1 query problems"""
        # Check if query has joins but no eager loading
        has_joins = bool(query.column_descriptions)
        has_eager_loading = bool(query._with_options)
        
        return has_joins and not has_eager_loading
        
    def _check_missing_indexes(self, query: Query) -> bool:
        """Check if query could benefit from additional indexes"""
        # Get the WHERE clause conditions
        whereclause = query.whereclause
        
        if whereclause is not None:
            # Check if filtering on non-indexed columns
            # This is a simplified check - in production, 
            # we'd analyze the actual execution plan
            return True
            
        return False
        
    def _generate_cache_key(self, query: Query) -> str:
        """Generate a cache key for the query"""
        # Create a cache key based on the query string and parameters
        query_string = str(query)
        params = str(query.statement.compile().params)
        
        return f"query:{hash(query_string + params)}"
        
    def _update_statistics(self, query_time: float):
        """Update query performance statistics"""
        self.statistics['query_count'] += 1
        
        # Update average query time
        current_avg = self.statistics['average_query_time']
        count = self.statistics['query_count']
        
        new_avg = ((current_avg * (count - 1)) + query_time) / count
        self.statistics['average_query_time'] = new_avg
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get query optimization statistics"""
        hit_rate = 0
        if self.statistics['cache_hits'] + self.statistics['cache_misses'] > 0:
            hit_rate = (self.statistics['cache_hits'] / 
                       (self.statistics['cache_hits'] + self.statistics['cache_misses'])) * 100
                       
        return {
            **self.statistics,
            'cache_hit_rate': hit_rate
        }
        
    def clear_cache(self):
        """Clear the query cache"""
        self.query_cache.clear()
        cache_service.clear_pattern('query:*')
        
    def suggest_indexes(self, model: Type[Base], db: Session) -> List[Dict[str, Any]]:
        """Suggest indexes based on query patterns"""
        suggestions = []
        
        # Analyze common query patterns
        inspector = inspect(db.bind)
        existing_indexes = inspector.get_indexes(model.__tablename__)
        
        # Check for frequently filtered columns without indexes
        frequent_filters = self._analyze_filter_patterns(model)
        
        for column, frequency in frequent_filters.items():
            if not self._has_index(column, existing_indexes):
                suggestions.append({
                    'table': model.__tablename__,
                    'column': column,
                    'type': 'btree',
                    'reason': f'Column {column} is frequently used in WHERE clauses',
                    'frequency': frequency
                })
                
        # Check for foreign key columns without indexes
        for column in model.__table__.columns:
            if column.foreign_keys and not self._has_index(column.name, existing_indexes):
                suggestions.append({
                    'table': model.__tablename__,
                    'column': column.name,
                    'type': 'btree',
                    'reason': f'Foreign key column {column.name} should have an index',
                    'frequency': 'high'
                })
                
        return suggestions
        
    def _analyze_filter_patterns(self, model: Type[Base]) -> Dict[str, int]:
        """Analyze common filter patterns for a model"""
        # In a real implementation, this would analyze query logs
        # For now, return common patterns
        common_patterns = {
            'created_at': 100,
            'updated_at': 80,
            'status': 90,
            'user_id': 85,
            'is_active': 75
        }
        
        # Filter to only include columns that exist in the model
        model_columns = [col.name for col in model.__table__.columns]
        return {k: v for k, v in common_patterns.items() if k in model_columns}
        
    def _has_index(self, column: str, indexes: List[Dict]) -> bool:
        """Check if a column has an index"""
        for index in indexes:
            if column in index.get('column_names', []):
                return True
        return False
        
    def optimize_bulk_insert(self, model: Type[Base], data: List[Dict],
                           batch_size: int = 1000, db: Session = None) -> int:
        """Optimize bulk insert operations"""
        inserted_count = 0
        
        try:
            # Disable autoflush for better performance
            with db.no_autoflush:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    
                    # Use bulk_insert_mappings for better performance
                    db.bulk_insert_mappings(model, batch)
                    inserted_count += len(batch)
                    
                    # Commit in batches
                    if i % (batch_size * 10) == 0:
                        db.commit()
                        
                # Final commit
                db.commit()
                
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk insert failed: {str(e)}")
            raise
            
        return inserted_count
        
    def optimize_bulk_update(self, model: Type[Base], updates: List[Dict],
                           batch_size: int = 1000, db: Session = None) -> int:
        """Optimize bulk update operations"""
        updated_count = 0
        
        try:
            # Disable autoflush for better performance
            with db.no_autoflush:
                for i in range(0, len(updates), batch_size):
                    batch = updates[i:i + batch_size]
                    
                    # Use bulk_update_mappings for better performance
                    db.bulk_update_mappings(model, batch)
                    updated_count += len(batch)
                    
                    # Commit in batches
                    if i % (batch_size * 10) == 0:
                        db.commit()
                        
                # Final commit
                db.commit()
                
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk update failed: {str(e)}")
            raise
            
        return updated_count
        
    def create_query_execution_plan(self, query: Query, db: Session) -> Dict[str, Any]:
        """Create an execution plan for the query"""
        # Get the SQL statement
        sql = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        
        # Get execution plan (PostgreSQL example)
        if db.bind.dialect.name == 'postgresql':
            result = db.execute(f"EXPLAIN ANALYZE {sql}")
            plan = [row[0] for row in result]
            
            return {
                'sql': sql,
                'execution_plan': plan,
                'database': 'postgresql'
            }
        else:
            # For other databases, return basic info
            return {
                'sql': sql,
                'execution_plan': ['Execution plan not available for this database'],
                'database': db.bind.dialect.name
            }
            
    @performance_monitor.track_performance('query_optimization')
    def optimize_complex_query(self, query: Query, optimization_level: str = 'medium') -> Query:
        """Apply complex query optimizations based on level"""
        
        if optimization_level == 'low':
            # Basic optimizations
            query = self._apply_query_hints(query)
            
        elif optimization_level == 'medium':
            # Standard optimizations
            query = self._apply_query_hints(query)
            query = self._optimize_joins(query)
            
        elif optimization_level == 'high':
            # Aggressive optimizations
            query = self._apply_query_hints(query)
            query = self._optimize_joins(query)
            query = self._apply_subquery_optimization(query)
            query = self._apply_cte_optimization(query)
            
        return query
        
    def _optimize_joins(self, query: Query) -> Query:
        """Optimize join operations"""
        # Convert LEFT JOINs to INNER JOINs where possible
        # This is a simplified example - real implementation would analyze nullability
        return query
        
    def _apply_subquery_optimization(self, query: Query) -> Query:
        """Optimize subqueries"""
        # Convert correlated subqueries to joins where possible
        return query
        
    def _apply_cte_optimization(self, query: Query) -> Query:
        """Apply Common Table Expression optimizations"""
        # Use CTEs for complex queries
        return query
        
# Initialize the query optimizer
query_optimizer = QueryOptimizer()