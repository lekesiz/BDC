"""
Database Index Manager

Manages database indexes for optimal query performance, including
automatic index suggestions, index monitoring, and maintenance.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
from sqlalchemy import text, inspect, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from flask_sqlalchemy import SQLAlchemy


@dataclass
class IndexSuggestion:
    """Index suggestion with analysis"""
    table_name: str
    columns: List[str]
    index_type: str  # 'btree', 'hash', 'gin', 'gist', etc.
    reason: str
    estimated_benefit: int  # 1-10 scale
    query_patterns: List[str]
    size_estimate: str


@dataclass
class IndexAnalysis:
    """Analysis of existing index"""
    index_name: str
    table_name: str
    columns: List[str]
    index_type: str
    size_bytes: int
    usage_count: int
    last_used: Optional[str]
    redundant_with: Optional[str]
    recommendation: str  # 'keep', 'drop', 'modify'


class IndexManager:
    """
    Advanced database index manager for performance optimization.
    """
    
    def __init__(self, db: Optional[SQLAlchemy] = None):
        self.db = db
        self.query_patterns = defaultdict(list)
        self.column_usage = defaultdict(int)
        self.table_access_patterns = defaultdict(list)
        self.existing_indexes = {}
        self.index_usage_stats = defaultdict(int)
        
        if self.db:
            self._load_existing_indexes()
    
    def suggest_indexes(self) -> List[IndexSuggestion]:
        """
        Generate index suggestions based on query patterns and table access.
        """
        suggestions = []
        
        # Analyze query patterns for index opportunities
        for table_name, patterns in self.table_access_patterns.items():
            table_suggestions = self._analyze_table_patterns(table_name, patterns)
            suggestions.extend(table_suggestions)
        
        # Remove duplicate suggestions
        suggestions = self._deduplicate_suggestions(suggestions)
        
        # Sort by estimated benefit
        suggestions.sort(key=lambda x: x.estimated_benefit, reverse=True)
        
        return suggestions
    
    def analyze_existing_indexes(self) -> List[IndexAnalysis]:
        """
        Analyze existing indexes for optimization opportunities.
        """
        if not self.db:
            return []
        
        analyses = []
        
        for table_name, indexes in self.existing_indexes.items():
            for index_info in indexes:
                analysis = self._analyze_index(table_name, index_info)
                analyses.append(analysis)
        
        return analyses
    
    def record_query_pattern(self, table_name: str, query_type: str, 
                           columns: List[str], conditions: Dict[str, Any]):
        """
        Record query pattern for index analysis.
        """
        pattern = {
            'query_type': query_type,
            'columns': columns,
            'conditions': conditions,
            'timestamp': None  # Would be set in real implementation
        }
        
        self.table_access_patterns[table_name].append(pattern)
        
        # Update column usage statistics
        for column in columns:
            self.column_usage[f"{table_name}.{column}"] += 1
    
    def create_suggested_indexes(self, suggestions: List[IndexSuggestion]) -> Dict[str, bool]:
        """
        Create indexes based on suggestions.
        """
        results = {}
        
        if not self.db:
            return results
        
        for suggestion in suggestions:
            try:
                index_sql = self._generate_create_index_sql(suggestion)
                
                with self.db.engine.connect() as conn:
                    conn.execute(text(index_sql))
                    conn.commit()
                
                results[suggestion.table_name] = True
                logging.info(f"Created index on {suggestion.table_name}({', '.join(suggestion.columns)})")
                
            except Exception as e:
                results[suggestion.table_name] = False
                logging.error(f"Failed to create index on {suggestion.table_name}: {e}")
        
        # Reload existing indexes
        self._load_existing_indexes()
        
        return results
    
    def drop_redundant_indexes(self) -> Dict[str, bool]:
        """
        Drop redundant or unused indexes.
        """
        results = {}
        analyses = self.analyze_existing_indexes()
        
        for analysis in analyses:
            if analysis.recommendation == 'drop':
                try:
                    drop_sql = f"DROP INDEX {analysis.index_name}"
                    
                    with self.db.engine.connect() as conn:
                        conn.execute(text(drop_sql))
                        conn.commit()
                    
                    results[analysis.index_name] = True
                    logging.info(f"Dropped redundant index: {analysis.index_name}")
                    
                except Exception as e:
                    results[analysis.index_name] = False
                    logging.error(f"Failed to drop index {analysis.index_name}: {e}")
        
        return results
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive index statistics.
        """
        total_indexes = sum(len(indexes) for indexes in self.existing_indexes.values())
        total_tables = len(self.existing_indexes)
        
        # Calculate average indexes per table
        avg_indexes_per_table = total_indexes / max(total_tables, 1)
        
        # Find most/least indexed tables
        table_index_counts = {
            table: len(indexes) 
            for table, indexes in self.existing_indexes.items()
        }
        
        most_indexed = max(table_index_counts.items(), key=lambda x: x[1]) if table_index_counts else ('', 0)
        least_indexed = min(table_index_counts.items(), key=lambda x: x[1]) if table_index_counts else ('', 0)
        
        return {
            'total_indexes': total_indexes,
            'total_tables': total_tables,
            'average_indexes_per_table': round(avg_indexes_per_table, 2),
            'most_indexed_table': {
                'name': most_indexed[0],
                'index_count': most_indexed[1]
            },
            'least_indexed_table': {
                'name': least_indexed[0],
                'index_count': least_indexed[1]
            },
            'query_patterns_analyzed': len(self.table_access_patterns),
            'column_usage_tracked': len(self.column_usage)
        }
    
    def generate_index_maintenance_plan(self) -> Dict[str, Any]:
        """
        Generate a comprehensive index maintenance plan.
        """
        plan = {
            'timestamp': None,  # Would be set in real implementation
            'suggestions': self.suggest_indexes(),
            'redundant_indexes': [],
            'maintenance_tasks': [],
            'estimated_impact': {}
        }
        
        # Find redundant indexes
        analyses = self.analyze_existing_indexes()
        redundant_indexes = [a for a in analyses if a.recommendation == 'drop']
        plan['redundant_indexes'] = redundant_indexes
        
        # Generate maintenance tasks
        tasks = []
        
        if plan['suggestions']:
            tasks.append({
                'type': 'create_indexes',
                'priority': 'high',
                'description': f"Create {len(plan['suggestions'])} suggested indexes",
                'estimated_time': len(plan['suggestions']) * 2  # 2 minutes per index
            })
        
        if redundant_indexes:
            tasks.append({
                'type': 'drop_indexes',
                'priority': 'medium',
                'description': f"Drop {len(redundant_indexes)} redundant indexes",
                'estimated_time': len(redundant_indexes) * 1  # 1 minute per index
            })
        
        # Add reindex task if needed
        if total_indexes := sum(len(indexes) for indexes in self.existing_indexes.values()):
            if total_indexes > 10:  # Arbitrary threshold
                tasks.append({
                    'type': 'reindex',
                    'priority': 'low',
                    'description': "Reindex tables for optimal performance",
                    'estimated_time': total_indexes * 5  # 5 minutes per index
                })
        
        plan['maintenance_tasks'] = tasks
        
        # Estimate performance impact
        plan['estimated_impact'] = {
            'query_performance_improvement': f"{len(plan['suggestions']) * 15}%",
            'storage_savings': f"{len(redundant_indexes) * 50}MB",
            'maintenance_window_required': sum(task['estimated_time'] for task in tasks)
        }
        
        return plan
    
    def _load_existing_indexes(self):
        """Load existing indexes from the database"""
        if not self.db:
            return
        
        try:
            inspector = inspect(self.db.engine)
            
            for table_name in inspector.get_table_names():
                indexes = inspector.get_indexes(table_name)
                self.existing_indexes[table_name] = indexes
                
        except Exception as e:
            logging.error(f"Failed to load existing indexes: {e}")
    
    def _analyze_table_patterns(self, table_name: str, patterns: List[Dict]) -> List[IndexSuggestion]:
        """Analyze patterns for a specific table"""
        suggestions = []
        
        # Group patterns by query type
        query_types = defaultdict(list)
        for pattern in patterns:
            query_types[pattern['query_type']].append(pattern)
        
        # Analyze SELECT patterns
        if 'SELECT' in query_types:
            select_suggestions = self._analyze_select_patterns(table_name, query_types['SELECT'])
            suggestions.extend(select_suggestions)
        
        # Analyze WHERE clause patterns
        where_columns = []
        for pattern in patterns:
            if 'conditions' in pattern and pattern['conditions']:
                where_columns.extend(pattern['conditions'].keys())
        
        if where_columns:
            column_frequency = Counter(where_columns)
            for column, frequency in column_frequency.most_common(5):  # Top 5
                if not self._index_exists(table_name, [column]):
                    suggestion = IndexSuggestion(
                        table_name=table_name,
                        columns=[column],
                        index_type='btree',
                        reason=f"Frequently used in WHERE clauses ({frequency} times)",
                        estimated_benefit=min(frequency, 10),
                        query_patterns=[f"WHERE {column} = ?"],
                        size_estimate=f"~{frequency * 10}KB"
                    )
                    suggestions.append(suggestion)
        
        # Analyze composite index opportunities
        composite_suggestions = self._analyze_composite_opportunities(table_name, patterns)
        suggestions.extend(composite_suggestions)
        
        return suggestions
    
    def _analyze_select_patterns(self, table_name: str, select_patterns: List[Dict]) -> List[IndexSuggestion]:
        """Analyze SELECT patterns for index opportunities"""
        suggestions = []
        
        # Look for commonly selected columns
        selected_columns = []
        for pattern in select_patterns:
            selected_columns.extend(pattern.get('columns', []))
        
        column_frequency = Counter(selected_columns)
        
        # Suggest covering indexes for frequently selected columns
        if len(column_frequency) > 1:
            top_columns = [col for col, _ in column_frequency.most_common(3)]
            
            if not self._index_exists(table_name, top_columns):
                suggestion = IndexSuggestion(
                    table_name=table_name,
                    columns=top_columns,
                    index_type='btree',
                    reason="Covering index for frequently selected columns",
                    estimated_benefit=7,
                    query_patterns=[f"SELECT {', '.join(top_columns)} FROM {table_name}"],
                    size_estimate=f"~{len(top_columns) * 20}KB"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_composite_opportunities(self, table_name: str, patterns: List[Dict]) -> List[IndexSuggestion]:
        """Analyze opportunities for composite indexes"""
        suggestions = []
        
        # Find column combinations used together
        column_combinations = []
        for pattern in patterns:
            if 'conditions' in pattern and len(pattern['conditions']) > 1:
                columns = sorted(pattern['conditions'].keys())
                column_combinations.append(tuple(columns))
        
        # Find frequent combinations
        combination_frequency = Counter(column_combinations)
        
        for combination, frequency in combination_frequency.items():
            if frequency >= 2 and len(combination) <= 4:  # Max 4 columns
                columns = list(combination)
                
                if not self._index_exists(table_name, columns):
                    suggestion = IndexSuggestion(
                        table_name=table_name,
                        columns=columns,
                        index_type='btree',
                        reason=f"Composite index for frequent column combination ({frequency} times)",
                        estimated_benefit=min(frequency + len(columns), 10),
                        query_patterns=[f"WHERE {' AND '.join(f'{col} = ?' for col in columns)}"],
                        size_estimate=f"~{len(columns) * frequency * 15}KB"
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_index(self, table_name: str, index_info: Dict) -> IndexAnalysis:
        """Analyze a specific index"""
        index_name = index_info.get('name', '')
        columns = [col['name'] for col in index_info.get('column_names', [])]
        
        # Determine recommendation
        recommendation = 'keep'
        
        # Check for redundancy
        redundant_with = self._find_redundant_index(table_name, columns)
        if redundant_with:
            recommendation = 'drop'
        
        # Check usage (would be implemented with actual usage statistics)
        usage_count = self.index_usage_stats.get(index_name, 0)
        if usage_count == 0:
            recommendation = 'drop'
        
        return IndexAnalysis(
            index_name=index_name,
            table_name=table_name,
            columns=columns,
            index_type=index_info.get('type', 'unknown'),
            size_bytes=0,  # Would be calculated from database statistics
            usage_count=usage_count,
            last_used=None,  # Would be tracked in real implementation
            redundant_with=redundant_with,
            recommendation=recommendation
        )
    
    def _index_exists(self, table_name: str, columns: List[str]) -> bool:
        """Check if an index exists for the given columns"""
        table_indexes = self.existing_indexes.get(table_name, [])
        
        for index_info in table_indexes:
            index_columns = [col['name'] for col in index_info.get('column_names', [])]
            if set(index_columns) == set(columns):
                return True
        
        return False
    
    def _find_redundant_index(self, table_name: str, columns: List[str]) -> Optional[str]:
        """Find if there's a redundant index"""
        table_indexes = self.existing_indexes.get(table_name, [])
        
        for index_info in table_indexes:
            index_columns = [col['name'] for col in index_info.get('column_names', [])]
            
            # Check if this index is a subset of another index
            if len(columns) < len(index_columns) and set(columns).issubset(set(index_columns)):
                return index_info.get('name', '')
        
        return None
    
    def _generate_create_index_sql(self, suggestion: IndexSuggestion) -> str:
        """Generate CREATE INDEX SQL statement"""
        index_name = f"idx_{suggestion.table_name}_{'_'.join(suggestion.columns)}"
        columns_str = ', '.join(suggestion.columns)
        
        return f"CREATE INDEX {index_name} ON {suggestion.table_name} ({columns_str})"
    
    def _deduplicate_suggestions(self, suggestions: List[IndexSuggestion]) -> List[IndexSuggestion]:
        """Remove duplicate index suggestions"""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            key = (suggestion.table_name, tuple(sorted(suggestion.columns)))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions