"""
Database Query Optimizer

Optimizes SQL queries for better performance by analyzing query patterns,
suggesting improvements, and automatically optimizing common queries.
"""

import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy


@dataclass
class QueryAnalysis:
    """Analysis result for a query"""
    original_query: str
    optimized_query: str
    execution_time_before: float
    execution_time_after: float
    improvement_percentage: float
    recommendations: List[str]


@dataclass
class SlowQuery:
    """Slow query information"""
    query: str
    execution_time: float
    frequency: int
    table_scans: List[str]
    missing_indexes: List[str]


class QueryOptimizer:
    """
    Advanced SQL query optimizer that analyzes and improves database queries.
    """
    
    def __init__(self, db: Optional[SQLAlchemy] = None):
        self.db = db
        self.query_cache = {}
        self.slow_queries = []
        self.query_patterns = {
            'n_plus_one': re.compile(r'SELECT.*FROM.*WHERE.*IN\s*\(SELECT', re.IGNORECASE),
            'missing_limit': re.compile(r'SELECT.*FROM.*(?!.*LIMIT)', re.IGNORECASE),
            'unnecessary_distinct': re.compile(r'SELECT\s+DISTINCT.*FROM.*(?!.*GROUP\s+BY)', re.IGNORECASE),
            'cartesian_join': re.compile(r'FROM.*,.*WHERE(?!.*=)', re.IGNORECASE),
            'function_in_where': re.compile(r'WHERE.*\w+\(.*\)\s*[=<>]', re.IGNORECASE)
        }
        self.optimization_rules = [
            self._optimize_select_star,
            self._optimize_unnecessary_joins,
            self._optimize_subqueries,
            self._add_missing_indexes_hint,
            self._optimize_order_by,
            self._optimize_group_by,
            self._optimize_like_queries,
            self._optimize_date_queries
        ]
    
    def optimize(self, query: str, params: Optional[Dict] = None) -> str:
        """
        Optimize a SQL query using various optimization techniques.
        """
        if not query or not query.strip():
            return query
        
        # Check cache first
        cache_key = self._get_cache_key(query, params)
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        original_query = query.strip()
        optimized_query = original_query
        
        # Apply optimization rules
        for rule in self.optimization_rules:
            try:
                optimized_query = rule(optimized_query)
            except Exception as e:
                logging.warning(f"Query optimization rule failed: {e}")
                continue
        
        # Cache the result
        self.query_cache[cache_key] = optimized_query
        
        return optimized_query
    
    def analyze_query(self, query: str, params: Optional[Dict] = None) -> QueryAnalysis:
        """
        Analyze a query and provide detailed optimization information.
        """
        original_query = query.strip()
        optimized_query = self.optimize(original_query, params)
        
        # Measure execution times (if database is available)
        time_before = time_after = 0.0
        if self.db:
            time_before = self._measure_query_time(original_query, params)
            time_after = self._measure_query_time(optimized_query, params)
        
        improvement = 0.0
        if time_before > 0:
            improvement = ((time_before - time_after) / time_before) * 100
        
        recommendations = self._generate_recommendations(original_query)
        
        return QueryAnalysis(
            original_query=original_query,
            optimized_query=optimized_query,
            execution_time_before=time_before,
            execution_time_after=time_after,
            improvement_percentage=improvement,
            recommendations=recommendations
        )
    
    def analyze_slow_queries(self, max_time: float = 1.0) -> List[SlowQuery]:
        """
        Analyze slow queries and provide optimization suggestions.
        """
        return [q for q in self.slow_queries if q.execution_time > max_time]
    
    def record_query_execution(self, query: str, execution_time: float):
        """
        Record query execution for analysis.
        """
        # Find existing slow query or create new one
        existing_query = None
        for sq in self.slow_queries:
            if self._normalize_query(sq.query) == self._normalize_query(query):
                existing_query = sq
                break
        
        if existing_query:
            # Update frequency and average time
            existing_query.frequency += 1
            existing_query.execution_time = (
                (existing_query.execution_time + execution_time) / 2
            )
        else:
            # Create new slow query record
            slow_query = SlowQuery(
                query=query,
                execution_time=execution_time,
                frequency=1,
                table_scans=self._detect_table_scans(query),
                missing_indexes=self._suggest_missing_indexes(query)
            )
            self.slow_queries.append(slow_query)
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive query statistics.
        """
        total_queries = len(self.slow_queries)
        if total_queries == 0:
            return {'total_queries': 0}
        
        avg_execution_time = sum(q.execution_time for q in self.slow_queries) / total_queries
        most_frequent = max(self.slow_queries, key=lambda q: q.frequency)
        slowest = max(self.slow_queries, key=lambda q: q.execution_time)
        
        return {
            'total_queries': total_queries,
            'average_execution_time': avg_execution_time,
            'most_frequent_query': {
                'query': most_frequent.query[:100] + '...' if len(most_frequent.query) > 100 else most_frequent.query,
                'frequency': most_frequent.frequency
            },
            'slowest_query': {
                'query': slowest.query[:100] + '...' if len(slowest.query) > 100 else slowest.query,
                'execution_time': slowest.execution_time
            },
            'cache_hit_rate': len(self.query_cache) / max(total_queries, 1) * 100
        }
    
    # Optimization rules
    def _optimize_select_star(self, query: str) -> str:
        """Replace SELECT * with specific columns when possible"""
        # This is a placeholder - in practice, you'd need schema information
        if 'SELECT *' in query.upper() and 'COUNT(*)' not in query.upper():
            # For now, just add a comment
            return f"-- Consider replacing SELECT * with specific columns\n{query}"
        return query
    
    def _optimize_unnecessary_joins(self, query: str) -> str:
        """Remove unnecessary joins"""
        # Detect joins that don't contribute to the result
        lines = query.split('\n')
        optimized_lines = []
        
        for line in lines:
            line_upper = line.upper()
            # Skip LEFT JOINs that are not used in SELECT, WHERE, or ORDER BY
            if 'LEFT JOIN' in line_upper:
                # This is a simplified check - real implementation would be more complex
                table_alias = self._extract_table_alias(line)
                if table_alias and not self._table_used_elsewhere(query, table_alias, line):
                    continue
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _optimize_subqueries(self, query: str) -> str:
        """Convert correlated subqueries to JOINs where possible"""
        # Look for EXISTS subqueries that can be converted to JOINs
        exists_pattern = re.compile(r'WHERE\s+EXISTS\s*\((.*?)\)', re.IGNORECASE | re.DOTALL)
        
        def replace_exists(match):
            subquery = match.group(1)
            # Simplified conversion - real implementation would be more sophisticated
            return f"-- Consider converting EXISTS to JOIN: {subquery[:50]}..."
        
        return exists_pattern.sub(replace_exists, query)
    
    def _add_missing_indexes_hint(self, query: str) -> str:
        """Add hints for missing indexes"""
        # Detect WHERE clauses that might benefit from indexes
        where_pattern = re.compile(r'WHERE\s+(\w+)\s*[=<>]', re.IGNORECASE)
        matches = where_pattern.findall(query)
        
        if matches:
            columns = set(matches)
            hint = f"-- Consider adding indexes on: {', '.join(columns)}"
            return f"{hint}\n{query}"
        
        return query
    
    def _optimize_order_by(self, query: str) -> str:
        """Optimize ORDER BY clauses"""
        # Check if ORDER BY matches an existing index
        order_pattern = re.compile(r'ORDER\s+BY\s+([^\\n]+)', re.IGNORECASE)
        match = order_pattern.search(query)
        
        if match:
            order_clause = match.group(1)
            # Add hint about covering indexes
            hint = f"-- Ensure index exists for ORDER BY: {order_clause.strip()}"
            return f"{hint}\n{query}"
        
        return query
    
    def _optimize_group_by(self, query: str) -> str:
        """Optimize GROUP BY clauses"""
        # Check for GROUP BY without proper indexing
        if 'GROUP BY' in query.upper():
            return f"-- Consider composite index for GROUP BY columns\n{query}"
        return query
    
    def _optimize_like_queries(self, query: str) -> str:
        """Optimize LIKE queries"""
        # Detect leading wildcard LIKE queries
        like_pattern = re.compile(r"LIKE\s+['\"]%", re.IGNORECASE)
        if like_pattern.search(query):
            return f"-- Warning: Leading wildcard LIKE query detected - consider full-text search\n{query}"
        return query
    
    def _optimize_date_queries(self, query: str) -> str:
        """Optimize date-based queries"""
        # Detect function calls on date columns in WHERE clauses
        date_function_pattern = re.compile(r'WHERE\s+\w+\([^)]*date[^)]*\)', re.IGNORECASE)
        if date_function_pattern.search(query):
            return f"-- Consider using date ranges instead of date functions in WHERE clause\n{query}"
        return query
    
    # Helper methods
    def _get_cache_key(self, query: str, params: Optional[Dict]) -> str:
        """Generate cache key for query"""
        normalized_query = self._normalize_query(query)
        params_str = str(sorted(params.items())) if params else ""
        return f"{normalized_query}:{params_str}"
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for comparison"""
        # Remove extra whitespace and comments
        normalized = re.sub(r'\s+', ' ', query.strip())
        normalized = re.sub(r'--.*?\n', '', normalized)
        return normalized.lower()
    
    def _measure_query_time(self, query: str, params: Optional[Dict]) -> float:
        """Measure query execution time"""
        if not self.db:
            return 0.0
        
        try:
            start_time = time.time()
            with self.db.engine.connect() as conn:
                if params:
                    conn.execute(text(query), params)
                else:
                    conn.execute(text(query))
            return time.time() - start_time
        except Exception as e:
            logging.warning(f"Query execution measurement failed: {e}")
            return 0.0
    
    def _generate_recommendations(self, query: str) -> List[str]:
        """Generate optimization recommendations for a query"""
        recommendations = []
        
        # Check for common anti-patterns
        for pattern_name, pattern in self.query_patterns.items():
            if pattern.search(query):
                recommendations.append(self._get_recommendation_for_pattern(pattern_name))
        
        # Check for missing LIMIT
        if 'SELECT' in query.upper() and 'LIMIT' not in query.upper():
            recommendations.append("Consider adding LIMIT clause to prevent large result sets")
        
        # Check for table scans
        table_scans = self._detect_table_scans(query)
        if table_scans:
            recommendations.append(f"Potential table scans detected on: {', '.join(table_scans)}")
        
        return recommendations
    
    def _get_recommendation_for_pattern(self, pattern_name: str) -> str:
        """Get recommendation message for a specific pattern"""
        recommendations_map = {
            'n_plus_one': "N+1 query detected - consider using JOINs or batch loading",
            'missing_limit': "Consider adding LIMIT clause for better performance",
            'unnecessary_distinct': "DISTINCT may be unnecessary - verify if GROUP BY is more appropriate",
            'cartesian_join': "Potential cartesian join detected - verify JOIN conditions",
            'function_in_where': "Function in WHERE clause may prevent index usage"
        }
        return recommendations_map.get(pattern_name, f"Pattern detected: {pattern_name}")
    
    def _detect_table_scans(self, query: str) -> List[str]:
        """Detect potential table scans in query"""
        # Extract table names from FROM clauses
        from_pattern = re.compile(r'FROM\s+(\w+)', re.IGNORECASE)
        tables = from_pattern.findall(query)
        
        # Check for WHERE clauses that might cause table scans
        where_pattern = re.compile(r'WHERE\s+.*', re.IGNORECASE)
        where_clause = where_pattern.search(query)
        
        if not where_clause:
            # No WHERE clause means potential full table scan
            return tables
        
        return []  # Simplified - real implementation would analyze index usage
    
    def _suggest_missing_indexes(self, query: str) -> List[str]:
        """Suggest missing indexes for a query"""
        suggestions = []
        
        # Extract columns from WHERE clauses
        where_columns = re.findall(r'WHERE\s+(\w+)', query, re.IGNORECASE)
        for column in where_columns:
            suggestions.append(f"CREATE INDEX idx_{column} ON table_name ({column})")
        
        # Extract columns from JOIN conditions
        join_columns = re.findall(r'ON\s+\w+\.(\w+)\s*=', query, re.IGNORECASE)
        for column in join_columns:
            suggestions.append(f"CREATE INDEX idx_{column} ON table_name ({column})")
        
        return suggestions
    
    def _extract_table_alias(self, join_line: str) -> Optional[str]:
        """Extract table alias from JOIN line"""
        # Match patterns like "LEFT JOIN table_name alias" or "LEFT JOIN table_name AS alias"
        pattern = re.compile(r'JOIN\s+\w+\s+(?:AS\s+)?(\w+)', re.IGNORECASE)
        match = pattern.search(join_line)
        return match.group(1) if match else None
    
    def _table_used_elsewhere(self, query: str, table_alias: str, join_line: str) -> bool:
        """Check if table alias is used elsewhere in the query"""
        # Remove the JOIN line and check if alias appears elsewhere
        query_without_join = query.replace(join_line, '')
        return table_alias in query_without_join