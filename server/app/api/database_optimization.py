"""Database optimization API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.database_optimization_service import get_db_optimization_service
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

database_optimization_bp = Blueprint('database_optimization', __name__, url_prefix='/api/database-optimization')


@database_optimization_bp.route('/performance-report', methods=['GET'])
@jwt_required()
def get_performance_report():
    """Get database performance report."""
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        # Add proper admin check here based on your auth system
        
        report = get_db_optimization_service().get_query_performance_report()
        
        return jsonify({
            'success': True,
            'data': report
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating performance report: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate performance report'
        }), 500


@database_optimization_bp.route('/table-statistics/<table_name>', methods=['GET'])
@jwt_required()
def get_table_statistics(table_name):
    """Get statistics for a specific table."""
    try:
        # Validate table name to prevent SQL injection
        allowed_tables = [
            'users', 'beneficiaries', 'appointments', 'evaluations',
            'documents', 'programs', 'notifications', 'sessions'
        ]
        
        if table_name not in allowed_tables:
            return jsonify({
                'success': False,
                'error': 'Invalid table name'
            }), 400
        
        stats = get_db_optimization_service().analyze_table_statistics(table_name)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting table statistics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get table statistics'
        }), 500


@database_optimization_bp.route('/missing-indexes', methods=['GET'])
@jwt_required()
def get_missing_indexes():
    """Get suggestions for missing indexes."""
    try:
        suggestions = get_db_optimization_service().suggest_missing_indexes()
        
        return jsonify({
            'success': True,
            'data': suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting missing indexes: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get missing indexes'
        }), 500


@database_optimization_bp.route('/create-indexes', methods=['POST'])
@jwt_required()
def create_suggested_indexes():
    """Create suggested indexes."""
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        # Add proper admin check here
        
        dry_run = request.json.get('dry_run', True)
        
        created_indexes = get_db_optimization_service().create_suggested_indexes(dry_run=dry_run)
        
        return jsonify({
            'success': True,
            'data': {
                'dry_run': dry_run,
                'indexes': created_indexes
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create indexes'
        }), 500


@database_optimization_bp.route('/vacuum-analyze', methods=['POST'])
@jwt_required()
def vacuum_analyze():
    """Run VACUUM ANALYZE on specified tables."""
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        # Add proper admin check here
        
        tables = request.json.get('tables', None)
        
        get_db_optimization_service().vacuum_analyze_tables(tables)
        
        return jsonify({
            'success': True,
            'message': 'VACUUM ANALYZE completed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error running VACUUM ANALYZE: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to run VACUUM ANALYZE'
        }), 500


@database_optimization_bp.route('/slow-queries', methods=['GET'])
@jwt_required()
def get_slow_queries():
    """Get recent slow queries."""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Get slow queries from memory (last N queries)
        slow_queries = get_db_optimization_service().slow_queries[-limit:]
        
        return jsonify({
            'success': True,
            'data': slow_queries
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get slow queries'
        }), 500


@database_optimization_bp.route('/query-stats', methods=['GET'])
@jwt_required()
def get_query_stats():
    """Get query statistics."""
    try:
        # Get top N queries by total time
        limit = request.args.get('limit', 20, type=int)
        
        sorted_stats = sorted(
            [
                {
                    'query': query,
                    **stats
                }
                for query, stats in get_db_optimization_service().query_stats.items()
            ],
            key=lambda x: x['total_time'],
            reverse=True
        )[:limit]
        
        return jsonify({
            'success': True,
            'data': sorted_stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting query stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get query statistics'
        }), 500


@database_optimization_bp.route('/optimize-beneficiaries', methods=['POST'])
@jwt_required()
def optimize_beneficiaries_query():
    """Apply optimizations to beneficiaries queries."""
    try:
        from app.models.beneficiary import Beneficiary
        from app.models.optimized_relationships import OptimizedRelationships, optimize_query
        
        # Example: Get beneficiaries with optimized loading
        query_type = request.json.get('query_type', 'list')
        
        if query_type == 'list':
            query = Beneficiary.query
            query = optimize_query(query, OptimizedRelationships.BENEFICIARY_FOR_LIST)
        elif query_type == 'details':
            query = Beneficiary.query
            query = optimize_query(query, OptimizedRelationships.BENEFICIARY_WITH_DETAILS)
        elif query_type == 'progress':
            query = Beneficiary.query
            query = optimize_query(query, OptimizedRelationships.BENEFICIARY_WITH_PROGRESS)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid query type'
            }), 400
        
        # Execute query with limit
        beneficiaries = query.limit(10).all()
        
        # Convert to dict (simplified for example)
        data = []
        for b in beneficiaries:
            data.append({
                'id': b.id,
                'user': {
                    'first_name': b.user.first_name if b.user else None,
                    'last_name': b.user.last_name if b.user else None,
                    'email': b.user.email if b.user else None
                },
                'trainer': {
                    'first_name': b.trainer.first_name if b.trainer else None,
                    'last_name': b.trainer.last_name if b.trainer else None
                } if b.trainer else None,
                'status': b.status,
                'is_active': b.is_active
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'query_type': query_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error optimizing beneficiaries query: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to optimize query'
        }), 500