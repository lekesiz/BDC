"""Global search API for searching across multiple entities."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func, text
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    User, Beneficiary, Appointment, Document, 
    Test, TestSession, Program, Notification
)
from app.utils.decorators import requires_permission
from app.core.cache_manager import cache_manager
from app.utils.logging import logger


global_search_bp = Blueprint('global_search', __name__, url_prefix='/api/v2/search')


class SearchService:
    """Service for handling global search operations."""
    
    SEARCH_CONFIGS = {
        'beneficiaries': {
            'model': Beneficiary,
            'searchable_fields': ['first_name', 'last_name', 'email', 'phone', 'city', 'address'],
            'display_fields': ['id', 'first_name', 'last_name', 'email', 'status'],
            'permission': 'beneficiaries.view'
        },
        'users': {
            'model': User,
            'searchable_fields': ['first_name', 'last_name', 'email', 'username'],
            'display_fields': ['id', 'first_name', 'last_name', 'email', 'role'],
            'permission': 'users.view'
        },
        'appointments': {
            'model': Appointment,
            'searchable_fields': ['title', 'description', 'location', 'notes'],
            'display_fields': ['id', 'title', 'appointment_date', 'status', 'beneficiary_id'],
            'permission': 'appointments.view'
        },
        'documents': {
            'model': Document,
            'searchable_fields': ['name', 'description', 'tags'],
            'display_fields': ['id', 'name', 'document_type', 'created_at'],
            'permission': 'documents.view'
        },
        'tests': {
            'model': Test,
            'searchable_fields': ['title', 'description', 'instructions'],
            'display_fields': ['id', 'title', 'test_type', 'is_active'],
            'permission': 'evaluations.view'
        },
        'programs': {
            'model': Program,
            'searchable_fields': ['name', 'description', 'objectives'],
            'display_fields': ['id', 'name', 'status', 'start_date'],
            'permission': 'programs.view'
        }
    }
    
    @staticmethod
    def normalize_query(query: str) -> str:
        """Normalize search query for better matching."""
        # Remove extra spaces and convert to lowercase
        query = ' '.join(query.lower().strip().split())
        
        # Remove special characters except spaces
        query = re.sub(r'[^\w\s]', '', query)
        
        return query
    
    @staticmethod
    def build_search_filters(model, fields: List[str], query: str) -> List:
        """Build OR filters for searchable fields."""
        filters = []
        normalized_query = SearchService.normalize_query(query)
        
        # Split query into words for partial matching
        words = normalized_query.split()
        
        for field in fields:
            if hasattr(model, field):
                column = getattr(model, field)
                
                # Add filters for each word
                for word in words:
                    # Case-insensitive LIKE search
                    filters.append(func.lower(column).like(f'%{word}%'))
        
        return filters
    
    @staticmethod
    def search_entity(
        entity_type: str,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Search within a specific entity type."""
        config = SearchService.SEARCH_CONFIGS.get(entity_type)
        if not config:
            return {'results': [], 'total': 0}
        
        model = config['model']
        searchable_fields = config['searchable_fields']
        
        # Build base query
        base_query = model.query
        
        # Apply search filters
        search_filters = SearchService.build_search_filters(
            model, searchable_fields, query
        )
        
        if search_filters:
            base_query = base_query.filter(or_(*search_filters))
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    base_query = base_query.filter(getattr(model, key) == value)
        
        # Get total count
        total = base_query.count()
        
        # Apply pagination
        results = base_query.limit(limit).offset(offset).all()
        
        # Format results
        formatted_results = []
        for result in results:
            item = {
                'type': entity_type,
                'score': SearchService.calculate_relevance_score(result, query, searchable_fields)
            }
            
            # Add display fields
            for field in config['display_fields']:
                if hasattr(result, field):
                    value = getattr(result, field)
                    # Convert datetime objects to ISO format
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    item[field] = value
            
            # Add matched fields
            item['matched_fields'] = SearchService.get_matched_fields(
                result, query, searchable_fields
            )
            
            formatted_results.append(item)
        
        # Sort by relevance score
        formatted_results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'results': formatted_results,
            'total': total
        }
    
    @staticmethod
    def calculate_relevance_score(entity, query: str, fields: List[str]) -> float:
        """Calculate relevance score for search result."""
        score = 0.0
        normalized_query = SearchService.normalize_query(query)
        words = normalized_query.split()
        
        for field in fields:
            if hasattr(entity, field):
                field_value = getattr(entity, field)
                if field_value:
                    field_value = str(field_value).lower()
                    
                    # Exact match gets highest score
                    if normalized_query in field_value:
                        score += 10.0
                    
                    # Word matches
                    for word in words:
                        if word in field_value:
                            score += 5.0
                    
                    # Partial matches
                    for word in words:
                        if any(word in part for part in field_value.split()):
                            score += 2.0
        
        return score
    
    @staticmethod
    def get_matched_fields(entity, query: str, fields: List[str]) -> List[str]:
        """Get list of fields that matched the query."""
        matched = []
        normalized_query = SearchService.normalize_query(query)
        words = normalized_query.split()
        
        for field in fields:
            if hasattr(entity, field):
                field_value = getattr(entity, field)
                if field_value:
                    field_value = str(field_value).lower()
                    
                    # Check if any word matches
                    if any(word in field_value for word in words):
                        matched.append(field)
        
        return matched


@global_search_bp.route('/global', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(ttl=60, key_prefix='global_search')
def global_search():
    """
    Perform global search across all entities.
    
    Query parameters:
    - q: Search query (required)
    - types: Comma-separated list of entity types to search (optional)
    - limit: Maximum results per type (default: 5)
    - include_inactive: Include inactive records (default: false)
    """
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify({'error': 'Query must be at least 2 characters long'}), 400
    
    # Get search parameters
    requested_types = request.args.get('types', '').split(',') if request.args.get('types') else None
    limit_per_type = int(request.args.get('limit', 5))
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Get current user for permission checking
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    results = {
        'query': query,
        'timestamp': datetime.utcnow().isoformat(),
        'results_by_type': {},
        'total_results': 0
    }
    
    # Search each entity type
    for entity_type, config in SearchService.SEARCH_CONFIGS.items():
        # Skip if not in requested types
        if requested_types and entity_type not in requested_types:
            continue
        
        # Check permissions
        if not user.has_permission(config['permission']):
            continue
        
        # Build filters
        filters = {}
        if not include_inactive and hasattr(config['model'], 'is_active'):
            filters['is_active'] = True
        elif not include_inactive and hasattr(config['model'], 'status'):
            filters['status'] = 'active'
        
        # Perform search
        try:
            entity_results = SearchService.search_entity(
                entity_type,
                query,
                limit=limit_per_type,
                filters=filters
            )
            
            if entity_results['total'] > 0:
                results['results_by_type'][entity_type] = entity_results
                results['total_results'] += entity_results['total']
        
        except Exception as e:
            logger.error(f"Error searching {entity_type}: {str(e)}")
            continue
    
    return jsonify(results), 200


@global_search_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def search_suggestions():
    """Get search suggestions based on partial query."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'suggestions': []}), 200
    
    limit = int(request.args.get('limit', 10))
    
    suggestions = []
    seen = set()
    
    # Get suggestions from recent searches (if implemented)
    # This could be extended to track user searches
    
    # Get suggestions from entity names
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Beneficiaries
    if user.has_permission('beneficiaries.view'):
        beneficiaries = Beneficiary.query.filter(
            or_(
                func.lower(Beneficiary.first_name).like(f'{query.lower()}%'),
                func.lower(Beneficiary.last_name).like(f'{query.lower()}%'),
                func.lower(Beneficiary.email).like(f'{query.lower()}%')
            )
        ).limit(5).all()
        
        for b in beneficiaries:
            suggestion = f"{b.first_name} {b.last_name}"
            if suggestion.lower() not in seen:
                suggestions.append({
                    'text': suggestion,
                    'type': 'beneficiary',
                    'id': b.id
                })
                seen.add(suggestion.lower())
    
    # Add more entity types as needed
    
    return jsonify({
        'suggestions': suggestions[:limit]
    }), 200


@global_search_bp.route('/advanced', methods=['POST'])
@jwt_required()
@requires_permission('search.advanced')
def advanced_search():
    """
    Perform advanced search with complex filters.
    
    Request body:
    {
        "query": "search text",
        "filters": {
            "entity_type": "beneficiaries",
            "date_range": {
                "field": "created_at",
                "start": "2024-01-01",
                "end": "2024-12-31"
            },
            "conditions": [
                {
                    "field": "status",
                    "operator": "equals",
                    "value": "active"
                }
            ]
        },
        "sort": {
            "field": "created_at",
            "direction": "desc"
        },
        "pagination": {
            "page": 1,
            "per_page": 20
        }
    }
    """
    data = request.get_json()
    
    query = data.get('query', '')
    filters = data.get('filters', {})
    sort_config = data.get('sort', {})
    pagination = data.get('pagination', {'page': 1, 'per_page': 20})
    
    entity_type = filters.get('entity_type')
    if not entity_type or entity_type not in SearchService.SEARCH_CONFIGS:
        return jsonify({'error': 'Invalid or missing entity type'}), 400
    
    config = SearchService.SEARCH_CONFIGS[entity_type]
    model = config['model']
    
    # Build query
    base_query = model.query
    
    # Apply text search if provided
    if query:
        search_filters = SearchService.build_search_filters(
            model, config['searchable_fields'], query
        )
        if search_filters:
            base_query = base_query.filter(or_(*search_filters))
    
    # Apply date range filter
    date_range = filters.get('date_range')
    if date_range:
        field = date_range.get('field')
        start = date_range.get('start')
        end = date_range.get('end')
        
        if hasattr(model, field):
            if start:
                base_query = base_query.filter(
                    getattr(model, field) >= datetime.fromisoformat(start)
                )
            if end:
                base_query = base_query.filter(
                    getattr(model, field) <= datetime.fromisoformat(end)
                )
    
    # Apply conditions
    conditions = filters.get('conditions', [])
    for condition in conditions:
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if hasattr(model, field):
            column = getattr(model, field)
            
            if operator == 'equals':
                base_query = base_query.filter(column == value)
            elif operator == 'not_equals':
                base_query = base_query.filter(column != value)
            elif operator == 'contains':
                base_query = base_query.filter(column.like(f'%{value}%'))
            elif operator == 'starts_with':
                base_query = base_query.filter(column.like(f'{value}%'))
            elif operator == 'ends_with':
                base_query = base_query.filter(column.like(f'%{value}'))
            elif operator == 'greater_than':
                base_query = base_query.filter(column > value)
            elif operator == 'less_than':
                base_query = base_query.filter(column < value)
            elif operator == 'in':
                base_query = base_query.filter(column.in_(value))
            elif operator == 'not_in':
                base_query = base_query.filter(~column.in_(value))
    
    # Apply sorting
    if sort_config:
        field = sort_config.get('field', 'id')
        direction = sort_config.get('direction', 'asc')
        
        if hasattr(model, field):
            order_column = getattr(model, field)
            if direction == 'desc':
                base_query = base_query.order_by(order_column.desc())
            else:
                base_query = base_query.order_by(order_column.asc())
    
    # Get total count
    total = base_query.count()
    
    # Apply pagination
    page = pagination.get('page', 1)
    per_page = pagination.get('per_page', 20)
    offset = (page - 1) * per_page
    
    results = base_query.limit(per_page).offset(offset).all()
    
    # Format results
    formatted_results = []
    for result in results:
        item = {'type': entity_type}
        
        # Add all fields from the model
        for column in model.__table__.columns:
            value = getattr(result, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            item[column.name] = value
        
        formatted_results.append(item)
    
    return jsonify({
        'results': formatted_results,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200


@global_search_bp.route('/export', methods=['POST'])
@jwt_required()
@requires_permission('search.export')
def export_search_results():
    """Export search results to CSV or JSON."""
    data = request.get_json()
    export_format = data.get('format', 'csv')
    
    # Perform the search (reuse advanced search logic)
    search_response = advanced_search()
    
    if search_response[1] != 200:
        return search_response
    
    results = search_response[0].get_json()['results']
    
    if export_format == 'json':
        return jsonify({
            'data': results,
            'exported_at': datetime.utcnow().isoformat(),
            'total_records': len(results)
        }), 200
    
    elif export_format == 'csv':
        # Implementation would create CSV file
        # For now, return a message
        return jsonify({
            'message': 'CSV export would be implemented here',
            'total_records': len(results)
        }), 200
    
    else:
        return jsonify({'error': 'Invalid export format'}), 400