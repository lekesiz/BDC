"""Database indexing strategy for performance optimization."""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import text, inspect
from flask import current_app

logger = logging.getLogger(__name__)


class DatabaseIndexingStrategy:
    """Manages database indexing strategies for optimal performance."""
    
    def __init__(self):
        """Initialize database indexing strategy."""
        self.critical_indexes = {
            'users': [
                {
                    'name': 'idx_users_email',
                    'columns': ['email'],
                    'unique': True,
                    'description': 'Unique email index for fast user lookups'
                },
                {
                    'name': 'idx_users_tenant_role',
                    'columns': ['tenant_id', 'role'],
                    'unique': False,
                    'description': 'Composite index for tenant-based role queries'
                },
                {
                    'name': 'idx_users_role_active',
                    'columns': ['role', 'is_active'],
                    'unique': False,
                    'description': 'Index for filtering active users by role'
                }
            ],
            'beneficiaries': [
                {
                    'name': 'idx_beneficiaries_user_id',
                    'columns': ['user_id'],
                    'unique': True,
                    'description': 'Foreign key index for user relationship'
                },
                {
                    'name': 'idx_beneficiaries_trainer_id',
                    'columns': ['trainer_id'],
                    'unique': False,
                    'description': 'Index for trainer assignments'
                },
                {
                    'name': 'idx_beneficiaries_tenant_status',
                    'columns': ['tenant_id', 'status'],
                    'unique': False,
                    'description': 'Composite index for tenant-based status queries'
                }
            ],
            'appointments': [
                {
                    'name': 'idx_appointments_beneficiary_time',
                    'columns': ['beneficiary_id', 'start_time'],
                    'unique': False,
                    'description': 'Index for beneficiary appointment lookups'
                },
                {
                    'name': 'idx_appointments_trainer_time',
                    'columns': ['trainer_id', 'start_time'],
                    'unique': False,
                    'description': 'Index for trainer schedule queries'
                },
                {
                    'name': 'idx_appointments_status_time',
                    'columns': ['status', 'start_time'],
                    'unique': False,
                    'description': 'Index for appointment status filtering'
                }
            ],
            'documents': [
                {
                    'name': 'idx_documents_beneficiary_created',
                    'columns': ['beneficiary_id', 'created_at'],
                    'unique': False,
                    'description': 'Index for beneficiary document timeline'
                },
                {
                    'name': 'idx_documents_file_type',
                    'columns': ['file_type'],
                    'unique': False,
                    'description': 'Index for document type filtering'
                },
                {
                    'name': 'idx_documents_tenant_type',
                    'columns': ['tenant_id', 'file_type'],
                    'unique': False,
                    'description': 'Composite index for tenant document queries'
                }
            ],
            'test_sessions': [
                {
                    'name': 'idx_test_sessions_beneficiary',
                    'columns': ['beneficiary_id'],
                    'unique': False,
                    'description': 'Index for beneficiary test history'
                },
                {
                    'name': 'idx_test_sessions_test_status',
                    'columns': ['test_id', 'status'],
                    'unique': False,
                    'description': 'Index for test completion tracking'
                },
                {
                    'name': 'idx_test_sessions_created',
                    'columns': ['created_at'],
                    'unique': False,
                    'description': 'Index for time-based queries'
                }
            ],
            'audit_logs': [
                {
                    'name': 'idx_audit_logs_user_time',
                    'columns': ['user_id', 'created_at'],
                    'unique': False,
                    'description': 'Index for user activity tracking'
                },
                {
                    'name': 'idx_audit_logs_entity',
                    'columns': ['entity_type', 'entity_id'],
                    'unique': False,
                    'description': 'Index for entity-based audit queries'
                },
                {
                    'name': 'idx_audit_logs_action',
                    'columns': ['action', 'created_at'],
                    'unique': False,
                    'description': 'Index for action-based filtering'
                }
            ]
        }
        
    def analyze_and_create_indexes(self, db_engine) -> Dict[str, Any]:
        """Analyze database and create missing critical indexes."""
        results = {
            'analyzed_tables': 0,
            'existing_indexes': 0,
            'created_indexes': 0,
            'failed_indexes': 0,
            'recommendations': []
        }
        
        try:
            inspector = inspect(db_engine)
            
            for table_name, required_indexes in self.critical_indexes.items():
                results['analyzed_tables'] += 1
                
                # Check if table exists
                if table_name not in inspector.get_table_names():
                    logger.warning(f"Table '{table_name}' does not exist")
                    continue
                    
                # Get existing indexes
                existing_indexes = inspector.get_indexes(table_name)
                existing_index_names = {idx['name'] for idx in existing_indexes}
                
                # Check and create missing indexes
                for index_config in required_indexes:
                    if index_config['name'] in existing_index_names:
                        results['existing_indexes'] += 1
                        logger.debug(f"Index '{index_config['name']}' already exists")
                    else:
                        # Create missing index
                        if self._create_index(db_engine, table_name, index_config):
                            results['created_indexes'] += 1
                            logger.info(f"Created index '{index_config['name']}' on table '{table_name}'")
                        else:
                            results['failed_indexes'] += 1
                            results['recommendations'].append({
                                'table': table_name,
                                'index': index_config['name'],
                                'action': 'manual_creation_required',
                                'sql': self._generate_index_sql(table_name, index_config)
                            })
                            
        except Exception as e:
            logger.error(f"Error analyzing indexes: {str(e)}")
            
        return results
        
    def _create_index(self, db_engine, table_name: str, index_config: Dict) -> bool:
        """Create a single index."""
        try:
            sql = self._generate_index_sql(table_name, index_config)
            
            with db_engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index '{index_config['name']}': {str(e)}")
            return False
            
    def _generate_index_sql(self, table_name: str, index_config: Dict) -> str:
        """Generate SQL for creating an index."""
        unique = 'UNIQUE' if index_config.get('unique', False) else ''
        columns = ', '.join(index_config['columns'])
        
        return f"""
        CREATE {unique} INDEX IF NOT EXISTS {index_config['name']}
        ON {table_name} ({columns})
        """
        
    def optimize_database_indexes(self, db_engine) -> Dict[str, Any]:
        """Optimize existing indexes and provide recommendations."""
        optimization_results = {
            'analyzed_indexes': 0,
            'unused_indexes': [],
            'duplicate_indexes': [],
            'missing_statistics': [],
            'recommendations': []
        }
        
        try:
            # Analyze index usage
            usage_query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan ASC
            """
            
            with db_engine.connect() as conn:
                result = conn.execute(text(usage_query))
                
                for row in result:
                    optimization_results['analyzed_indexes'] += 1
                    
                    # Identify unused indexes
                    if row[3] == 0:  # idx_scan
                        optimization_results['unused_indexes'].append({
                            'schema': row[0],
                            'table': row[1],
                            'index': row[2],
                            'size': row[6],
                            'recommendation': f"Consider dropping unused index: {row[2]}"
                        })
                        
            # Analyze duplicate indexes
            duplicate_query = """
            SELECT 
                a.indrelid::regclass AS table_name,
                a.indexrelid::regclass AS index1,
                b.indexrelid::regclass AS index2
            FROM pg_index a
            JOIN pg_index b ON a.indrelid = b.indrelid 
                AND a.indexrelid != b.indexrelid
                AND a.indkey = b.indkey
            WHERE a.indexrelid > b.indexrelid
            """
            
            with db_engine.connect() as conn:
                result = conn.execute(text(duplicate_query))
                
                for row in result:
                    optimization_results['duplicate_indexes'].append({
                        'table': str(row[0]),
                        'index1': str(row[1]),
                        'index2': str(row[2]),
                        'recommendation': f"Duplicate indexes found: {row[1]} and {row[2]}"
                    })
                    
        except Exception as e:
            logger.error(f"Error optimizing indexes: {str(e)}")
            
        return optimization_results
        
    def get_index_statistics(self, db_engine, table_name: str = None) -> List[Dict]:
        """Get detailed statistics for indexes."""
        statistics = []
        
        try:
            if table_name:
                stats_query = """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                    pg_stat_get_last_analyze_time(indexrelid) as last_analyze
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public' AND tablename = :table_name
                ORDER BY idx_scan DESC
                """
                params = {'table_name': table_name}
            else:
                stats_query = """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                    pg_stat_get_last_analyze_time(indexrelid) as last_analyze
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
                LIMIT 50
                """
                params = {}
                
            with db_engine.connect() as conn:
                result = conn.execute(text(stats_query), params)
                
                for row in result:
                    statistics.append({
                        'schema': row[0],
                        'table': row[1],
                        'index': row[2],
                        'scan_count': row[3],
                        'tuples_read': row[4],
                        'tuples_fetched': row[5],
                        'size': row[6],
                        'last_analyze': row[7],
                        'efficiency': row[5] / row[4] if row[4] > 0 else 0
                    })
                    
        except Exception as e:
            logger.error(f"Error getting index statistics: {str(e)}")
            
        return statistics
        
    def recommend_indexes_for_query(self, query: str, db_engine) -> List[Dict]:
        """Recommend indexes for a specific query."""
        recommendations = []
        
        try:
            # Use EXPLAIN to analyze query
            explain_query = f"EXPLAIN (FORMAT JSON) {query}"
            
            with db_engine.connect() as conn:
                result = conn.execute(text(explain_query))
                plan = result.fetchone()[0]
                
            # Analyze the plan for potential index improvements
            self._analyze_plan_for_indexes(plan[0]['Plan'], recommendations)
            
        except Exception as e:
            logger.error(f"Error analyzing query for index recommendations: {str(e)}")
            
        return recommendations
        
    def _analyze_plan_for_indexes(self, plan: Dict, recommendations: List[Dict], depth: int = 0):
        """Recursively analyze query plan for index opportunities."""
        node_type = plan.get('Node Type', '')
        
        # Check for sequential scans on large tables
        if node_type == 'Seq Scan':
            table_name = plan.get('Relation Name', '')
            filter_cond = plan.get('Filter', '')
            rows = plan.get('Plan Rows', 0)
            
            if rows > 1000 and filter_cond:
                recommendations.append({
                    'table': table_name,
                    'reason': f'Sequential scan on {rows} rows with filter',
                    'filter': filter_cond,
                    'recommendation': f'Consider adding index on filter columns for table {table_name}'
                })
                
        # Check for expensive sorts
        elif node_type == 'Sort':
            sort_key = plan.get('Sort Key', [])
            rows = plan.get('Plan Rows', 0)
            
            if rows > 5000:
                recommendations.append({
                    'operation': 'Sort',
                    'rows': rows,
                    'sort_key': sort_key,
                    'recommendation': 'Consider adding index on sort columns to avoid sorting'
                })
                
        # Recursively analyze child plans
        if 'Plans' in plan:
            for child_plan in plan['Plans']:
                self._analyze_plan_for_indexes(child_plan, recommendations, depth + 1)


# Global instance
db_indexing_strategy = DatabaseIndexingStrategy()