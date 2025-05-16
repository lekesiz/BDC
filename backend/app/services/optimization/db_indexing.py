"""
Database indexing strategy
"""
from typing import Dict, Any, List, Optional
from sqlalchemy import inspect, Index, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import Table
from app.models.base import Base
from app.core.database import engine
from app.services.monitoring.performance_metrics import performance_monitor
import logging

logger = logging.getLogger(__name__)

class DatabaseIndexingStrategy:
    """Database indexing strategy implementation"""
    
    def __init__(self):
        self.index_stats = {
            'indexes_created': 0,
            'indexes_analyzed': 0,
            'indexes_dropped': 0,
            'query_improvements': []
        }
        
    def analyze_and_create_indexes(self, db: Session, models: List[type] = None):
        """Analyze database and create necessary indexes"""
        if models is None:
            models = Base.__subclasses__()
            
        for model in models:
            self._analyze_model_indexes(model, db)
            
        return self.index_stats
        
    def _analyze_model_indexes(self, model: type, db: Session):
        """Analyze indexes for a specific model"""
        table_name = model.__tablename__
        inspector = inspect(db.bind)
        
        # Get existing indexes
        existing_indexes = inspector.get_indexes(table_name)
        existing_index_columns = {
            tuple(idx['column_names']) for idx in existing_indexes
        }
        
        # Analyze common query patterns
        suggested_indexes = self._get_suggested_indexes(model)
        
        # Create missing indexes
        for index_config in suggested_indexes:
            columns = tuple(index_config['columns'])
            if columns not in existing_index_columns:
                self._create_index(
                    table_name,
                    index_config['columns'],
                    index_config.get('unique', False),
                    index_config.get('name'),
                    db
                )
                
        self.index_stats['indexes_analyzed'] += 1
        
    def _get_suggested_indexes(self, model: type) -> List[Dict[str, Any]]:
        """Get suggested indexes for a model based on common patterns"""
        suggestions = []
        table = model.__table__
        
        # Foreign key indexes
        for column in table.columns:
            if column.foreign_keys:
                suggestions.append({
                    'columns': [column.name],
                    'name': f'idx_{table.name}_{column.name}',
                    'reason': 'Foreign key column'
                })
                
        # Common lookup patterns
        common_patterns = self._get_common_query_patterns(model)
        for pattern in common_patterns:
            suggestions.append({
                'columns': pattern['columns'],
                'name': pattern.get('name', f"idx_{table.name}_{'_'.join(pattern['columns'])}"),
                'reason': pattern.get('reason', 'Common query pattern')
            })
            
        # Composite indexes for common filters
        if hasattr(model, '__search_fields__'):
            search_fields = model.__search_fields__
            if len(search_fields) > 1:
                suggestions.append({
                    'columns': search_fields[:3],  # Limit to 3 columns
                    'name': f'idx_{table.name}_search',
                    'reason': 'Search optimization'
                })
                
        return suggestions
        
    def _get_common_query_patterns(self, model: type) -> List[Dict[str, Any]]:
        """Define common query patterns for models"""
        patterns = []
        table_name = model.__tablename__
        
        # Common patterns for all models
        if 'created_at' in model.__table__.columns:
            patterns.append({
                'columns': ['created_at'],
                'reason': 'Chronological queries'
            })
            
        if 'status' in model.__table__.columns:
            patterns.append({
                'columns': ['status'],
                'reason': 'Status filtering'
            })
            
        if 'is_active' in model.__table__.columns:
            patterns.append({
                'columns': ['is_active'],
                'reason': 'Active record filtering'
            })
            
        # Model-specific patterns
        if table_name == 'users':
            patterns.extend([
                {'columns': ['email'], 'unique': True, 'reason': 'Email lookup'},
                {'columns': ['username'], 'unique': True, 'reason': 'Username lookup'},
                {'columns': ['role', 'is_active'], 'reason': 'Role-based queries'}
            ])
        elif table_name == 'beneficiaries':
            patterns.extend([
                {'columns': ['trainer_id'], 'reason': 'Trainer lookup'},
                {'columns': ['status', 'created_at'], 'reason': 'Status timeline'},
                {'columns': ['program_id', 'status'], 'reason': 'Program filtering'}
            ])
        elif table_name == 'assessments':
            patterns.extend([
                {'columns': ['beneficiary_id', 'status'], 'reason': 'Beneficiary assessments'},
                {'columns': ['assessment_type', 'created_at'], 'reason': 'Type filtering'},
                {'columns': ['completed_at'], 'reason': 'Completion queries'}
            ])
        elif table_name == 'appointments':
            patterns.extend([
                {'columns': ['beneficiary_id', 'scheduled_at'], 'reason': 'Schedule lookup'},
                {'columns': ['trainer_id', 'scheduled_at'], 'reason': 'Trainer schedule'},
                {'columns': ['status', 'scheduled_at'], 'reason': 'Status filtering'}
            ])
        elif table_name == 'notes':
            patterns.extend([
                {'columns': ['beneficiary_id', 'created_at'], 'reason': 'Beneficiary timeline'},
                {'columns': ['author_id', 'created_at'], 'reason': 'Author history'},
                {'columns': ['note_type'], 'reason': 'Type filtering'}
            ])
            
        return patterns
        
    def _create_index(self, table_name: str, columns: List[str], 
                     unique: bool = False, name: Optional[str] = None,
                     db: Session = None):
        """Create an index on specified columns"""
        if not name:
            name = f"idx_{table_name}_{'_'.join(columns)}"
            
        try:
            # Create index using raw SQL for better control
            columns_str = ', '.join(columns)
            unique_str = 'UNIQUE' if unique else ''
            
            sql = f"""
            CREATE {unique_str} INDEX IF NOT EXISTS {name}
            ON {table_name} ({columns_str})
            """
            
            db.execute(text(sql))
            db.commit()
            
            self.index_stats['indexes_created'] += 1
            logger.info(f"Created index {name} on {table_name}({columns_str})")
            
        except Exception as e:
            logger.error(f"Failed to create index {name}: {str(e)}")
            db.rollback()
            
    def drop_unused_indexes(self, db: Session, threshold_days: int = 30):
        """Drop indexes that haven't been used recently"""
        inspector = inspect(db.bind)
        
        # Get index usage statistics (PostgreSQL specific)
        if db.bind.dialect.name == 'postgresql':
            usage_query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_relation_size(indexrelid) as index_size
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
            AND idx_tup_read = 0
            AND indexrelid > 16384
            """
            
            unused_indexes = db.execute(text(usage_query)).fetchall()
            
            for index in unused_indexes:
                if self._should_drop_index(index):
                    self._drop_index(index.indexname, db)
                    
    def _should_drop_index(self, index_stats: Any) -> bool:
        """Determine if an index should be dropped"""
        # Don't drop primary keys or unique constraints
        if 'pkey' in index_stats.indexname or 'unique' in index_stats.indexname:
            return False
            
        # Don't drop small indexes
        if index_stats.index_size < 1024 * 1024:  # 1MB
            return False
            
        # Drop if never used and larger than 10MB
        if index_stats.idx_scan == 0 and index_stats.index_size > 10 * 1024 * 1024:
            return True
            
        return False
        
    def _drop_index(self, index_name: str, db: Session):
        """Drop an index"""
        try:
            sql = f"DROP INDEX IF EXISTS {index_name}"
            db.execute(text(sql))
            db.commit()
            
            self.index_stats['indexes_dropped'] += 1
            logger.info(f"Dropped unused index {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to drop index {index_name}: {str(e)}")
            db.rollback()
            
    def analyze_query_performance(self, query: str, db: Session) -> Dict[str, Any]:
        """Analyze query performance and suggest index improvements"""
        analysis = {}
        
        if db.bind.dialect.name == 'postgresql':
            # Use EXPLAIN ANALYZE
            explain_query = f"EXPLAIN ANALYZE {query}"
            result = db.execute(text(explain_query))
            
            plan = []
            for row in result:
                plan.append(row[0])
                
            analysis['execution_plan'] = plan
            analysis['suggestions'] = self._analyze_execution_plan(plan)
            
        return analysis
        
    def _analyze_execution_plan(self, plan: List[str]) -> List[str]:
        """Analyze execution plan and provide suggestions"""
        suggestions = []
        
        for line in plan:
            # Check for sequential scans
            if 'Seq Scan' in line:
                suggestions.append(
                    "Sequential scan detected - consider adding an index"
                )
                
            # Check for high cost operations
            if 'cost=' in line:
                cost_str = line.split('cost=')[1].split()[0]
                try:
                    cost = float(cost_str.split('..')[1])
                    if cost > 1000:
                        suggestions.append(
                            f"High cost operation detected (cost={cost}) - optimize query or add indexes"
                        )
                except:
                    pass
                    
        return suggestions
        
    @performance_monitor.track_performance('index_optimization')
    def optimize_database_indexes(self, db: Session) -> Dict[str, Any]:
        """Comprehensive database index optimization"""
        results = {
            'indexes_created': 0,
            'indexes_dropped': 0,
            'tables_analyzed': 0,
            'suggestions': []
        }
        
        # Analyze all models
        models = Base.__subclasses__()
        for model in models:
            self._analyze_model_indexes(model, db)
            results['tables_analyzed'] += 1
            
        # Drop unused indexes (PostgreSQL only)
        if db.bind.dialect.name == 'postgresql':
            self.drop_unused_indexes(db)
            
        # Update results
        results['indexes_created'] = self.index_stats['indexes_created']
        results['indexes_dropped'] = self.index_stats['indexes_dropped']
        
        # Add general suggestions
        results['suggestions'] = [
            "Consider partitioning large tables",
            "Use covering indexes for frequently accessed column combinations",
            "Monitor slow query log for optimization opportunities",
            "Consider using partial indexes for filtered queries"
        ]
        
        return results
        
    def create_covering_index(self, table_name: str, columns: List[str],
                            include_columns: List[str], db: Session):
        """Create a covering index (PostgreSQL specific)"""
        if db.bind.dialect.name == 'postgresql':
            name = f"idx_{table_name}_covering_{'_'.join(columns[:2])}"
            columns_str = ', '.join(columns)
            include_str = ', '.join(include_columns)
            
            sql = f"""
            CREATE INDEX {name} ON {table_name} ({columns_str})
            INCLUDE ({include_str})
            """
            
            try:
                db.execute(text(sql))
                db.commit()
                logger.info(f"Created covering index {name}")
            except Exception as e:
                logger.error(f"Failed to create covering index: {str(e)}")
                db.rollback()
                
    def create_partial_index(self, table_name: str, columns: List[str],
                           condition: str, db: Session):
        """Create a partial index with a WHERE clause"""
        name = f"idx_{table_name}_partial_{'_'.join(columns[:2])}"
        columns_str = ', '.join(columns)
        
        sql = f"""
        CREATE INDEX {name} ON {table_name} ({columns_str})
        WHERE {condition}
        """
        
        try:
            db.execute(text(sql))
            db.commit()
            logger.info(f"Created partial index {name}")
        except Exception as e:
            logger.error(f"Failed to create partial index: {str(e)}")
            db.rollback()
            
    def get_index_statistics(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        stats = {}
        
        if db.bind.dialect.name == 'postgresql':
            # Get index usage statistics
            query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                pg_relation_size(indexrelid) as size_bytes,
                pg_size_pretty(pg_relation_size(indexrelid)) as size_pretty
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
            """
            
            result = db.execute(text(query))
            
            stats['index_usage'] = []
            for row in result:
                stats['index_usage'].append({
                    'table': row.tablename,
                    'index': row.indexname,
                    'scans': row.idx_scan,
                    'tuples_read': row.idx_tup_read,
                    'size': row.size_pretty
                })
                
        return stats

# Initialize the database indexing strategy
db_indexing_strategy = DatabaseIndexingStrategy()