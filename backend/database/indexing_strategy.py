import logging
from typing import List, Dict, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IndexRecommendation:
    table_name: str
    columns: List[str]
    index_type: str
    reason: str
    estimated_improvement: str
    priority: int

class IndexingStrategy:
    """Database indexing strategy analyzer and optimizer"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.inspector = inspect(self.engine)
        self.db_type = self._detect_db_type()
    
    def _detect_db_type(self) -> str:
        """Detect database type"""
        dialect = self.engine.dialect.name
        return dialect
    
    def analyze_query_patterns(self) -> List[Dict]:
        """Analyze query patterns to recommend indexes"""
        patterns = []
        
        with self.engine.connect() as conn:
            if self.db_type == 'postgresql':
                # Analyze pg_stat_statements
                query = """
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements
                    WHERE query NOT LIKE '%pg_stat_statements%'
                    ORDER BY total_time DESC
                    LIMIT 100
                """
                try:
                    result = conn.execute(text(query))
                    for row in result:
                        patterns.append({
                            'query': row.query,
                            'calls': row.calls,
                            'total_time': row.total_time,
                            'mean_time': row.mean_time,
                            'rows': row.rows
                        })
                except Exception as e:
                    logger.error(f"Error analyzing query patterns: {e}")
            
            elif self.db_type == 'mysql':
                # Analyze slow query log
                query = """
                    SELECT 
                        sql_text,
                        execution_count,
                        total_latency,
                        avg_latency,
                        rows_examined
                    FROM performance_schema.events_statements_summary_by_digest
                    ORDER BY total_latency DESC
                    LIMIT 100
                """
                try:
                    result = conn.execute(text(query))
                    for row in result:
                        patterns.append({
                            'query': row.sql_text,
                            'calls': row.execution_count,
                            'total_time': row.total_latency,
                            'mean_time': row.avg_latency,
                            'rows': row.rows_examined
                        })
                except Exception as e:
                    logger.error(f"Error analyzing query patterns: {e}")
        
        return patterns
    
    def get_missing_indexes(self) -> List[IndexRecommendation]:
        """Get recommendations for missing indexes"""
        recommendations = []
        
        # Analyze foreign key columns without indexes
        fk_recommendations = self._analyze_foreign_keys()
        recommendations.extend(fk_recommendations)
        
        # Analyze WHERE clause patterns
        where_recommendations = self._analyze_where_clauses()
        recommendations.extend(where_recommendations)
        
        # Analyze JOIN patterns
        join_recommendations = self._analyze_join_patterns()
        recommendations.extend(join_recommendations)
        
        # Analyze ORDER BY patterns
        order_recommendations = self._analyze_order_by_patterns()
        recommendations.extend(order_recommendations)
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations
    
    def _analyze_foreign_keys(self) -> List[IndexRecommendation]:
        """Find foreign key columns without indexes"""
        recommendations = []
        
        for table_name in self.inspector.get_table_names():
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            indexes = self.inspector.get_indexes(table_name)
            
            # Get indexed columns
            indexed_columns = set()
            for index in indexes:
                indexed_columns.update(index['column_names'])
            
            # Check each foreign key
            for fk in foreign_keys:
                fk_columns = fk['constrained_columns']
                if not all(col in indexed_columns for col in fk_columns):
                    recommendations.append(IndexRecommendation(
                        table_name=table_name,
                        columns=fk_columns,
                        index_type='btree',
                        reason=f"Foreign key to {fk['referred_table']} without index",
                        estimated_improvement='High - improves JOIN performance',
                        priority=8
                    ))
        
        return recommendations
    
    def _analyze_where_clauses(self) -> List[IndexRecommendation]:
        """Analyze WHERE clause patterns for index recommendations"""
        recommendations = []
        query_patterns = self.analyze_query_patterns()
        
        for pattern in query_patterns:
            query = pattern['query']
            
            # Simple pattern matching for WHERE clauses
            import re
            where_pattern = r'WHERE\s+(\w+\.)?(\w+)\s*=\s*'
            matches = re.findall(where_pattern, query, re.IGNORECASE)
            
            for match in matches:
                table_name = match[0].rstrip('.') if match[0] else None
                column_name = match[1]
                
                if table_name and self._should_index_column(table_name, column_name, pattern):
                    recommendations.append(IndexRecommendation(
                        table_name=table_name,
                        columns=[column_name],
                        index_type='btree',
                        reason=f"Frequently used in WHERE clause ({pattern['calls']} calls)",
                        estimated_improvement=f"Could save {pattern['mean_time']}ms per query",
                        priority=self._calculate_priority(pattern)
                    ))
        
        return recommendations
    
    def _analyze_join_patterns(self) -> List[IndexRecommendation]:
        """Analyze JOIN patterns for index recommendations"""
        recommendations = []
        
        with self.engine.connect() as conn:
            if self.db_type == 'postgresql':
                # Analyze joins from query plans
                query = """
                    SELECT 
                        schemaname,
                        tablename,
                        attname,
                        n_distinct,
                        correlation
                    FROM pg_stats
                    WHERE n_distinct > 100
                    AND schemaname = 'public'
                    ORDER BY n_distinct DESC
                """
                
                try:
                    result = conn.execute(text(query))
                    for row in result:
                        if abs(row.correlation or 0) < 0.5:  # Poor correlation
                            recommendations.append(IndexRecommendation(
                                table_name=row.tablename,
                                columns=[row.attname],
                                index_type='btree',
                                reason=f"High cardinality column with poor correlation",
                                estimated_improvement="Could improve JOIN performance",
                                priority=6
                            ))
                except Exception as e:
                    logger.error(f"Error analyzing join patterns: {e}")
        
        return recommendations
    
    def _analyze_order_by_patterns(self) -> List[IndexRecommendation]:
        """Analyze ORDER BY patterns for index recommendations"""
        recommendations = []
        query_patterns = self.analyze_query_patterns()
        
        for pattern in query_patterns:
            query = pattern['query']
            
            # Pattern matching for ORDER BY clauses
            import re
            order_pattern = r'ORDER\s+BY\s+(\w+\.)?(\w+)(?:\s+(ASC|DESC))?'
            matches = re.findall(order_pattern, query, re.IGNORECASE)
            
            for match in matches:
                table_name = match[0].rstrip('.') if match[0] else None
                column_name = match[1]
                direction = match[2] or 'ASC'
                
                if table_name and pattern['rows'] > 1000:  # Only for large result sets
                    recommendations.append(IndexRecommendation(
                        table_name=table_name,
                        columns=[column_name],
                        index_type='btree',
                        reason=f"Used in ORDER BY with {pattern['rows']} rows",
                        estimated_improvement="Could eliminate sorting step",
                        priority=5
                    ))
        
        return recommendations
    
    def _should_index_column(self, table_name: str, column_name: str, pattern: Dict) -> bool:
        """Determine if a column should be indexed"""
        # Check if column already has an index
        indexes = self.inspector.get_indexes(table_name)
        for index in indexes:
            if column_name in index['column_names']:
                return False
        
        # Check selectivity
        with self.engine.connect() as conn:
            query = f"""
                SELECT 
                    COUNT(DISTINCT {column_name}) as distinct_count,
                    COUNT(*) as total_count
                FROM {table_name}
            """
            result = conn.execute(text(query)).fetchone()
            
            if result.total_count > 0:
                selectivity = result.distinct_count / result.total_count
                
                # High selectivity (> 0.1) and frequent usage
                return selectivity > 0.1 and pattern['calls'] > 100
        
        return False
    
    def _calculate_priority(self, pattern: Dict) -> int:
        """Calculate index priority based on query pattern"""
        priority = 5  # Base priority
        
        # Increase priority for frequently called queries
        if pattern['calls'] > 10000:
            priority += 3
        elif pattern['calls'] > 1000:
            priority += 2
        elif pattern['calls'] > 100:
            priority += 1
        
        # Increase priority for slow queries
        if pattern['mean_time'] > 1000:  # > 1 second
            priority += 3
        elif pattern['mean_time'] > 100:  # > 100ms
            priority += 2
        elif pattern['mean_time'] > 10:   # > 10ms
            priority += 1
        
        return min(priority, 10)  # Cap at 10
    
    def get_unused_indexes(self) -> List[Dict]:
        """Find indexes that are not being used"""
        unused_indexes = []
        
        with self.engine.connect() as conn:
            if self.db_type == 'postgresql':
                query = """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE idx_scan = 0
                    AND schemaname = 'public'
                """
                
                try:
                    result = conn.execute(text(query))
                    for row in result:
                        unused_indexes.append({
                            'schema': row.schemaname,
                            'table': row.tablename,
                            'index': row.indexname,
                            'scans': row.idx_scan,
                            'recommendation': 'Consider removing this unused index'
                        })
                except Exception as e:
                    logger.error(f"Error finding unused indexes: {e}")
            
            elif self.db_type == 'mysql':
                # MySQL doesn't track index usage directly
                # Would need to analyze slow query log
                pass
        
        return unused_indexes
    
    def get_duplicate_indexes(self) -> List[Dict]:
        """Find duplicate or redundant indexes"""
        duplicates = []
        
        for table_name in self.inspector.get_table_names():
            indexes = self.inspector.get_indexes(table_name)
            
            # Compare indexes
            for i, index1 in enumerate(indexes):
                for j, index2 in enumerate(indexes[i+1:], i+1):
                    cols1 = index1['column_names']
                    cols2 = index2['column_names']
                    
                    # Check if one index is a prefix of another
                    if (cols1[:len(cols2)] == cols2 or 
                        cols2[:len(cols1)] == cols1):
                        duplicates.append({
                            'table': table_name,
                            'index1': index1['name'],
                            'columns1': cols1,
                            'index2': index2['name'],
                            'columns2': cols2,
                            'recommendation': 'Consider removing redundant index'
                        })
        
        return duplicates
    
    def generate_index_report(self) -> Dict:
        """Generate comprehensive indexing report"""
        report = {
            'missing_indexes': self.get_missing_indexes(),
            'unused_indexes': self.get_unused_indexes(),
            'duplicate_indexes': self.get_duplicate_indexes(),
            'current_indexes': self._get_current_indexes(),
            'recommendations_summary': self._generate_recommendations_summary()
        }
        
        return report
    
    def _get_current_indexes(self) -> Dict[str, List]:
        """Get current indexes by table"""
        current_indexes = {}
        
        for table_name in self.inspector.get_table_names():
            indexes = self.inspector.get_indexes(table_name)
            current_indexes[table_name] = indexes
        
        return current_indexes
    
    def _generate_recommendations_summary(self) -> Dict:
        """Generate summary of recommendations"""
        missing = self.get_missing_indexes()
        unused = self.get_unused_indexes()
        duplicates = self.get_duplicate_indexes()
        
        return {
            'total_missing': len(missing),
            'high_priority_missing': len([r for r in missing if r.priority >= 8]),
            'total_unused': len(unused),
            'total_duplicates': len(duplicates),
            'estimated_space_savings': self._estimate_space_savings(unused, duplicates),
            'top_recommendations': missing[:5] if missing else []
        }
    
    def _estimate_space_savings(self, unused: List, duplicates: List) -> str:
        """Estimate space savings from removing unused/duplicate indexes"""
        with self.engine.connect() as conn:
            total_size = 0
            
            if self.db_type == 'postgresql':
                for index in unused:
                    query = f"""
                        SELECT pg_relation_size('{index["schema"]}.{index["index"]}')
                    """
                    try:
                        result = conn.execute(text(query)).scalar()
                        total_size += result or 0
                    except:
                        pass
                
                for dup in duplicates:
                    query = f"""
                        SELECT pg_relation_size('{dup["table"]}.{dup["index2"]}')
                    """
                    try:
                        result = conn.execute(text(query)).scalar()
                        total_size += result or 0
                    except:
                        pass
            
            # Convert to human readable
            if total_size > 1e9:
                return f"{total_size / 1e9:.2f} GB"
            elif total_size > 1e6:
                return f"{total_size / 1e6:.2f} MB"
            else:
                return f"{total_size / 1e3:.2f} KB"


if __name__ == "__main__":
    # Example usage
    strategy = IndexingStrategy('postgresql://user:pass@localhost/bdc')
    
    # Get missing indexes
    missing = strategy.get_missing_indexes()
    print("Missing Indexes:")
    for rec in missing[:5]:
        print(f"  - {rec.table_name}.{rec.columns}: {rec.reason}")
    
    # Get unused indexes
    unused = strategy.get_unused_indexes()
    print("\nUnused Indexes:")
    for idx in unused[:5]:
        print(f"  - {idx['table']}.{idx['index']}")
    
    # Generate full report
    report = strategy.generate_index_report()
    print(f"\nSummary: {report['recommendations_summary']}")