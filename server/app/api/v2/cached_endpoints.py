"""Example of cached API endpoints using v2 architecture."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.core.container import get_beneficiary_service, get_user_service
from app.core.cache_manager import cache_manager, invalidate_beneficiary_cache
from app.schemas.beneficiary import BeneficiarySchema
from app.schemas.user import UserSchema

from app.utils.logging import logger


cached_bp = Blueprint('cached_v2', __name__, url_prefix='/api/v2/cached')
beneficiary_schema = BeneficiarySchema()
beneficiaries_schema = BeneficiarySchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@cached_bp.route('/beneficiaries', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(ttl=300, key_prefix='beneficiaries_list')
def list_beneficiaries():
    """List beneficiaries with caching."""
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    query = request.args.get('q', '')
    
    # Get filters
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('city'):
        filters['city'] = request.args.get('city')
    
    service = get_beneficiary_service()
    result = service.search_beneficiaries(query, filters, page, per_page)
    
    return jsonify({
        'beneficiaries': beneficiaries_schema.dump(result['items']),
        'pagination': {
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }
    }), 200


@cached_bp.route('/beneficiaries/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(ttl=600, key_prefix='beneficiary_detail')
def get_beneficiary(beneficiary_id):
    """Get beneficiary with caching (10 min TTL)."""
    service = get_beneficiary_service()
    beneficiary = service.get_beneficiary(beneficiary_id)
    
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    return jsonify({
        'beneficiary': beneficiary_schema.dump(beneficiary)
    }), 200


@cached_bp.route('/beneficiaries/<int:beneficiary_id>', methods=['PUT'])
@jwt_required()
def update_beneficiary(beneficiary_id):
    """Update beneficiary and invalidate cache."""
    data = request.get_json()
    service = get_beneficiary_service()
    
    beneficiary = service.update_beneficiary(beneficiary_id, data)
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    # Invalidate cache for this beneficiary
    invalidate_beneficiary_cache(beneficiary_id)
    
    return jsonify({
        'message': 'Beneficiary updated successfully',
        'beneficiary': beneficiary_schema.dump(beneficiary)
    }), 200


@cached_bp.route('/users', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(
    ttl=300, 
    key_prefix='users_list',
    vary_on_headers=['Authorization']  # Different cache per user
)
def list_users():
    """List users with per-user caching."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    query = request.args.get('q', '')
    
    filters = {}
    if request.args.get('role'):
        filters['role'] = request.args.get('role')
    if request.args.get('is_active'):
        filters['is_active'] = request.args.get('is_active').lower() == 'true'
    
    service = get_user_service()
    result = service.search_users(query, filters, page, per_page)
    
    return jsonify({
        'users': users_schema.dump(result['items']),
        'pagination': {
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }
    }), 200


@cached_bp.route('/statistics/beneficiaries', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(ttl=900, key_prefix='beneficiary_stats')  # 15 min cache
def get_beneficiary_statistics():
    """Get beneficiary statistics with longer cache."""
    service = get_beneficiary_service()
    stats = service.get_beneficiary_statistics()
    
    return jsonify(stats), 200


@cached_bp.route('/statistics/users', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(ttl=900, key_prefix='user_stats')  # 15 min cache
def get_user_statistics():
    """Get user statistics with longer cache."""
    service = get_user_service()
    stats = service.get_users_statistics()
    
    return jsonify(stats), 200


# Custom cache key example
def generate_user_cache_key(*args, **kwargs):
    """Generate cache key that includes user ID."""
    user_id = get_jwt_identity()
    return f"api_response:user_specific:{user_id}:{request.path}"


@cached_bp.route('/my-profile', methods=['GET'])
@jwt_required()
@cache_manager.cache_key_wrapper(generate_user_cache_key)
def get_my_profile():
    """Get current user profile with user-specific caching."""
    user_id = get_jwt_identity()
    service = get_user_service()
    
    user = service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = service.get_user_profile(user_id)
    
    return jsonify({
        'user': user_schema.dump(user),
        'profile': profile.to_dict() if profile else None
    }), 200


@cached_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """Clear cache for specific resources (admin only)."""
    # In production, check for admin role
    # if not current_user.is_admin:
    #     return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    resource_type = data.get('resource_type')
    resource_id = data.get('resource_id')
    
    if resource_type == 'beneficiary' and resource_id:
        invalidate_beneficiary_cache(resource_id)
        return jsonify({'message': f'Cache cleared for beneficiary {resource_id}'}), 200
    
    elif resource_type == 'user' and resource_id:
        from app.core.cache_manager import invalidate_user_cache
        invalidate_user_cache(resource_id)
        return jsonify({'message': f'Cache cleared for user {resource_id}'}), 200
    
    elif resource_type == 'all':
        # Clear all API response cache
        cache_manager.invalidate_pattern('api_response:*')
        return jsonify({'message': 'All API response cache cleared'}), 200
    
    return jsonify({'error': 'Invalid cache clear request'}), 400


@cached_bp.route('/beneficiaries', methods=['POST'])
@jwt_required()
def create_beneficiary():
    """Create a new beneficiary."""
    data = request.get_json()
    service = get_beneficiary_service()
    
    try:
        beneficiary = service.create_beneficiary(data)
        
        # Clear list cache as we have a new beneficiary
        cache_manager.clear_pattern('beneficiaries_list:*')
        
        return jsonify({
            'message': 'Beneficiary created successfully',
            'beneficiary': beneficiary_schema.dump(beneficiary)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@cached_bp.route('/test-short-ttl', methods=['GET'])
@jwt_required()
@cache_manager.cache_response(ttl=2, key_prefix='test_short_ttl')
def test_short_ttl():
    """Test endpoint with short TTL for testing cache expiration."""
    return jsonify({
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'This response has a 2-second TTL'
    })