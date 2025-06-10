"""
Pagination Optimizer

Advanced pagination strategies including cursor-based pagination,
keyset pagination, and intelligent prefetching for optimal performance.
"""

import base64
import json
import hashlib
import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Query
from flask import request, url_for


class PaginationType(Enum):
    OFFSET = "offset"
    CURSOR = "cursor"
    KEYSET = "keyset"
    SEARCH = "search"


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class PaginationConfig:
    """Pagination configuration"""
    default_page_size: int = 25
    max_page_size: int = 100
    enable_cursor_pagination: bool = True
    enable_keyset_pagination: bool = True
    enable_count_optimization: bool = True
    enable_prefetch: bool = True
    prefetch_pages: int = 2
    cache_ttl: int = 300  # 5 minutes
    enable_total_count: bool = True
    count_threshold: int = 10000  # Switch to estimated count above this


@dataclass
class CursorInfo:
    """Cursor pagination information"""
    value: Any
    column: str
    direction: SortDirection
    is_unique: bool = False


@dataclass
class PaginationMetadata:
    """Pagination metadata"""
    current_page: int
    page_size: int
    total_count: Optional[int]
    total_pages: Optional[int]
    has_next: bool
    has_previous: bool
    next_cursor: Optional[str]
    previous_cursor: Optional[str]
    estimated_total: bool = False
    query_time: float = 0.0


@dataclass
class PaginationResult:
    """Pagination result with data and metadata"""
    data: List[Any]
    metadata: PaginationMetadata
    links: Dict[str, str]
    cache_info: Dict[str, Any]


class PaginationOptimizer:
    """
    Advanced pagination optimizer with multiple pagination strategies.
    """
    
    def __init__(self, config: Optional[PaginationConfig] = None):
        self.config = config or PaginationConfig()
        self.pagination_cache = {}
        self.query_stats = {}
        self.prefetch_cache = {}
    
    def paginate_query(self, query: Query, page: int = 1, per_page: Optional[int] = None,
                      pagination_type: PaginationType = PaginationType.OFFSET,
                      cursor: Optional[str] = None, sort_column: str = 'id',
                      sort_direction: SortDirection = SortDirection.ASC,
                      endpoint: str = None) -> PaginationResult:
        """
        Paginate query using the specified pagination strategy.
        """
        start_time = time.time()
        per_page = per_page or self.config.default_page_size
        per_page = min(per_page, self.config.max_page_size)
        
        # Choose pagination strategy
        if pagination_type == PaginationType.CURSOR and cursor:
            result = self._cursor_paginate(query, cursor, per_page, sort_column, sort_direction)
        elif pagination_type == PaginationType.KEYSET:
            result = self._keyset_paginate(query, page, per_page, sort_column, sort_direction)
        else:
            result = self._offset_paginate(query, page, per_page, sort_column, sort_direction)
        
        # Add timing information
        result.metadata.query_time = time.time() - start_time
        
        # Generate navigation links
        if endpoint:
            result.links = self._generate_navigation_links(result, endpoint, pagination_type)
        
        # Prefetch next pages if enabled
        if self.config.enable_prefetch and result.metadata.has_next:
            self._prefetch_pages(query, result, pagination_type, sort_column, sort_direction)
        
        # Update query statistics
        self._update_query_stats(pagination_type, result.metadata.query_time, len(result.data))
        
        return result
    
    def paginate_search_results(self, search_results: List[Dict], query: str, 
                              page: int = 1, per_page: Optional[int] = None,
                              sort_key: str = 'relevance') -> PaginationResult:
        """
        Paginate search results with relevance scoring.
        """
        per_page = per_page or self.config.default_page_size
        per_page = min(per_page, self.config.max_page_size)
        
        start_time = time.time()
        
        # Sort by relevance or specified key
        if sort_key == 'relevance':
            search_results = self._sort_by_relevance(search_results, query)
        else:
            search_results = sorted(search_results, key=lambda x: x.get(sort_key, 0), reverse=True)
        
        # Calculate pagination
        total_count = len(search_results)
        total_pages = (total_count + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_data = search_results[start_idx:end_idx]
        
        metadata = PaginationMetadata(
            current_page=page,
            page_size=per_page,
            total_count=total_count,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
            next_cursor=None,
            previous_cursor=None,
            query_time=time.time() - start_time
        )
        
        return PaginationResult(
            data=paginated_data,
            metadata=metadata,
            links={},
            cache_info={'cached': False, 'cache_key': None}
        )
    
    def create_cursor(self, value: Any, column: str, 
                     direction: SortDirection = SortDirection.ASC) -> str:
        """
        Create a cursor for cursor-based pagination.
        """
        cursor_data = {
            'value': value,
            'column': column,
            'direction': direction.value,
            'timestamp': time.time()
        }
        
        cursor_json = json.dumps(cursor_data, default=str)
        return base64.b64encode(cursor_json.encode()).decode()
    
    def parse_cursor(self, cursor: str) -> Optional[CursorInfo]:
        """
        Parse a cursor string back to cursor information.
        """
        try:
            cursor_json = base64.b64decode(cursor.encode()).decode()
            cursor_data = json.loads(cursor_json)
            
            return CursorInfo(
                value=cursor_data['value'],
                column=cursor_data['column'],
                direction=SortDirection(cursor_data['direction'])
            )
        except Exception as e:
            logging.error(f"Failed to parse cursor: {e}")
            return None
    
    def estimate_total_count(self, query: Query) -> Tuple[int, bool]:
        """
        Estimate total count for large datasets.
        """
        try:
            # Try exact count first
            exact_count = query.count()
            
            if exact_count <= self.config.count_threshold:
                return exact_count, False
            
            # For large datasets, use estimation techniques
            # This is a simplified estimation - in practice, you might use
            # database-specific techniques like EXPLAIN or table statistics
            estimated_count = self._estimate_count_from_sample(query)
            return estimated_count, True
            
        except Exception as e:
            logging.error(f"Count estimation failed: {e}")
            return 0, True
    
    def optimize_pagination_query(self, query: Query, pagination_type: PaginationType,
                                 sort_column: str) -> Query:
        """
        Optimize query for specific pagination type.
        """
        if pagination_type == PaginationType.CURSOR:
            # For cursor pagination, ensure proper indexing
            return self._optimize_for_cursor(query, sort_column)
        elif pagination_type == PaginationType.KEYSET:
            # For keyset pagination, optimize for range queries
            return self._optimize_for_keyset(query, sort_column)
        else:
            # For offset pagination, optimize for counting
            return self._optimize_for_offset(query)
    
    def get_pagination_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive pagination statistics.
        """
        stats = {}
        
        for pagination_type, type_stats in self.query_stats.items():
            if type_stats['total_queries'] > 0:
                stats[pagination_type.value] = {
                    'total_queries': type_stats['total_queries'],
                    'avg_query_time_ms': round(
                        type_stats['total_time'] / type_stats['total_queries'] * 1000, 2
                    ),
                    'avg_results_per_page': round(
                        type_stats['total_results'] / type_stats['total_queries'], 1
                    ),
                    'cache_hit_rate': round(
                        type_stats['cache_hits'] / type_stats['total_queries'] * 100, 1
                    )
                }
        
        # Add overall statistics
        total_queries = sum(stats.get('total_queries', 0) for stats in self.query_stats.values())
        if total_queries > 0:
            total_time = sum(stats.get('total_time', 0) for stats in self.query_stats.values())
            stats['overall'] = {
                'total_queries': total_queries,
                'avg_query_time_ms': round(total_time / total_queries * 1000, 2),
                'prefetch_cache_size': len(self.prefetch_cache)
            }
        
        return stats
    
    # Private methods
    def _offset_paginate(self, query: Query, page: int, per_page: int,
                        sort_column: str, sort_direction: SortDirection) -> PaginationResult:
        """Implement offset-based pagination"""
        # Apply sorting
        if sort_direction == SortDirection.DESC:
            query = query.order_by(desc(getattr(query.column_descriptions[0]['type'], sort_column, None)))
        else:
            query = query.order_by(asc(getattr(query.column_descriptions[0]['type'], sort_column, None)))
        
        # Get total count (with optimization)
        if self.config.enable_total_count:
            total_count, estimated = self.estimate_total_count(query)
        else:
            total_count, estimated = None, False
        
        # Calculate pagination
        total_pages = None
        if total_count is not None:
            total_pages = (total_count + per_page - 1) // per_page
        
        # Apply offset and limit
        offset = (page - 1) * per_page
        paginated_query = query.offset(offset).limit(per_page + 1)  # +1 to check has_next
        
        results = paginated_query.all()
        has_next = len(results) > per_page
        if has_next:
            results = results[:-1]  # Remove extra item
        
        metadata = PaginationMetadata(
            current_page=page,
            page_size=per_page,
            total_count=total_count,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=page > 1,
            next_cursor=None,
            previous_cursor=None,
            estimated_total=estimated
        )
        
        return PaginationResult(
            data=results,
            metadata=metadata,
            links={},
            cache_info={'cached': False, 'cache_key': None}
        )
    
    def _cursor_paginate(self, query: Query, cursor: str, per_page: int,
                        sort_column: str, sort_direction: SortDirection) -> PaginationResult:
        """Implement cursor-based pagination"""
        cursor_info = self.parse_cursor(cursor)
        if not cursor_info:
            # Fallback to first page
            return self._offset_paginate(query, 1, per_page, sort_column, sort_direction)
        
        # Apply cursor filtering
        column_attr = getattr(query.column_descriptions[0]['type'], cursor_info.column, None)
        if column_attr is None:
            raise ValueError(f"Invalid sort column: {cursor_info.column}")
        
        if cursor_info.direction == SortDirection.DESC:
            query = query.filter(column_attr < cursor_info.value).order_by(desc(column_attr))
        else:
            query = query.filter(column_attr > cursor_info.value).order_by(asc(column_attr))
        
        # Get results
        results = query.limit(per_page + 1).all()  # +1 to check has_next
        has_next = len(results) > per_page
        if has_next:
            results = results[:-1]
        
        # Create next cursor
        next_cursor = None
        if has_next and results:
            last_item = results[-1]
            next_value = getattr(last_item, cursor_info.column)
            next_cursor = self.create_cursor(next_value, cursor_info.column, cursor_info.direction)
        
        metadata = PaginationMetadata(
            current_page=1,  # Cursor pagination doesn't use page numbers
            page_size=per_page,
            total_count=None,  # Not available with cursor pagination
            total_pages=None,
            has_next=has_next,
            has_previous=False,  # Would need previous cursor logic
            next_cursor=next_cursor,
            previous_cursor=None
        )
        
        return PaginationResult(
            data=results,
            metadata=metadata,
            links={},
            cache_info={'cached': False, 'cache_key': None}
        )
    
    def _keyset_paginate(self, query: Query, page: int, per_page: int,
                        sort_column: str, sort_direction: SortDirection) -> PaginationResult:
        """Implement keyset pagination (seek method)"""
        # This is a simplified implementation
        # In practice, you'd cache the boundary values for each page
        
        # For now, fall back to offset pagination
        # Real keyset pagination would store page boundaries
        return self._offset_paginate(query, page, per_page, sort_column, sort_direction)
    
    def _sort_by_relevance(self, results: List[Dict], query: str) -> List[Dict]:
        """Sort search results by relevance to query"""
        query_terms = query.lower().split()
        
        def calculate_relevance(item):
            score = 0
            text_fields = ['title', 'description', 'content', 'name']
            
            for field in text_fields:
                if field in item and isinstance(item[field], str):
                    field_text = item[field].lower()
                    for term in query_terms:
                        # Exact match bonus
                        if term in field_text:
                            score += 10
                        # Fuzzy match bonus
                        if any(term in word for word in field_text.split()):
                            score += 5
            
            return score
        
        return sorted(results, key=calculate_relevance, reverse=True)
    
    def _estimate_count_from_sample(self, query: Query) -> int:
        """Estimate total count from a sample"""
        try:
            # Take a sample and estimate
            sample_size = 1000
            sample = query.limit(sample_size).all()
            
            if len(sample) < sample_size:
                return len(sample)
            
            # Very rough estimation - in practice, you'd use more sophisticated methods
            estimated_total = len(sample) * 10  # Assume sample is 10% of total
            return estimated_total
            
        except Exception:
            return 0
    
    def _optimize_for_cursor(self, query: Query, sort_column: str) -> Query:
        """Optimize query for cursor pagination"""
        # Add hints for proper index usage
        # This is database-specific and would be implemented accordingly
        return query
    
    def _optimize_for_keyset(self, query: Query, sort_column: str) -> Query:
        """Optimize query for keyset pagination"""
        # Optimize for range queries
        return query
    
    def _optimize_for_offset(self, query: Query) -> Query:
        """Optimize query for offset pagination"""
        # Optimize for counting and offset operations
        return query
    
    def _generate_navigation_links(self, result: PaginationResult, endpoint: str,
                                  pagination_type: PaginationType) -> Dict[str, str]:
        """Generate navigation links for pagination"""
        links = {}
        
        if pagination_type == PaginationType.CURSOR:
            if result.metadata.next_cursor:
                links['next'] = url_for(endpoint, cursor=result.metadata.next_cursor)
            if result.metadata.previous_cursor:
                links['prev'] = url_for(endpoint, cursor=result.metadata.previous_cursor)
        else:
            # Offset-based links
            if result.metadata.has_next:
                links['next'] = url_for(endpoint, page=result.metadata.current_page + 1)
            if result.metadata.has_previous:
                links['prev'] = url_for(endpoint, page=result.metadata.current_page - 1)
            
            if result.metadata.total_pages:
                links['first'] = url_for(endpoint, page=1)
                links['last'] = url_for(endpoint, page=result.metadata.total_pages)
        
        return links
    
    def _prefetch_pages(self, query: Query, result: PaginationResult,
                       pagination_type: PaginationType, sort_column: str,
                       sort_direction: SortDirection):
        """Prefetch next pages for better performance"""
        if not self.config.enable_prefetch:
            return
        
        # This would implement intelligent prefetching
        # For now, it's a placeholder
        pass
    
    def _update_query_stats(self, pagination_type: PaginationType, 
                           query_time: float, result_count: int):
        """Update pagination query statistics"""
        if pagination_type not in self.query_stats:
            self.query_stats[pagination_type] = {
                'total_queries': 0,
                'total_time': 0.0,
                'total_results': 0,
                'cache_hits': 0
            }
        
        stats = self.query_stats[pagination_type]
        stats['total_queries'] += 1
        stats['total_time'] += query_time
        stats['total_results'] += result_count