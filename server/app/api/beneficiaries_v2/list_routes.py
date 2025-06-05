from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, current_user

from app.middleware.request_context import role_required
from app.services import BeneficiaryService
from app.schemas import BeneficiarySchema
from app.utils import cache_response

from . import beneficiaries_bp


@beneficiaries_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
@cache_response(timeout=300, key_prefix='beneficiaries')
def get_beneficiaries():
    """Get all beneficiaries with optional filtering. (Refactor v2)"""
    try:
        tenant_id = request.args.get('tenant_id', type=int)
        trainer_id = request.args.get('trainer_id', type=int)
        status = request.args.get('status')
        query = request.args.get('query')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by')
        sort_dir = request.args.get('sort_dir')

        # Role-based filtering
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
        elif current_user.role == 'trainer':
            trainer_id = current_user.id

        beneficiaries, total, pages = BeneficiaryService.get_beneficiaries(
            tenant_id=tenant_id,
            trainer_id=trainer_id,
            status=status,
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        result = BeneficiarySchema(many=True).dump(beneficiaries)
        return (
            jsonify(
                {
                    'items': result,
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': pages,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.exception(f"Get beneficiaries error: {str(e)}")
        return (
            jsonify(
                {
                    'error': 'server_error',
                    'message': 'An unexpected error occurred',
                }
            ),
            500,
        )


@beneficiaries_bp.route('', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def create_beneficiary():
    """Create a new beneficiary."""
    try:
        data = request.get_json()
        
        # Extract user fields
        user_fields = ['email', 'first_name', 'last_name', 'password']
        user_data = {}
        beneficiary_data = {}
        
        for key, value in data.items():
            if key in user_fields:
                user_data[key] = value
            else:
                beneficiary_data[key] = value
        
        # Validate required user fields
        if not user_data.get('email'):
            return jsonify({
                'error': 'validation_error',
                'message': 'Email is required'
            }), 400
            
        if not user_data.get('first_name') or not user_data.get('last_name'):
            return jsonify({
                'error': 'validation_error',
                'message': 'First name and last name are required'
            }), 400
            
        if not user_data.get('password'):
            # Generate a default password if not provided
            import secrets
            user_data['password'] = secrets.token_urlsafe(16)
        
        # Role-based tenant assignment
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            beneficiary_data['tenant_id'] = tenant_id
        elif current_user.role == 'trainer':
            # Trainers can only create beneficiaries within their tenant
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            beneficiary_data['tenant_id'] = tenant_id
            beneficiary_data['trainer_id'] = current_user.id
        elif current_user.role == 'super_admin':
            # Super admin must specify tenant_id
            if not beneficiary_data.get('tenant_id'):
                return jsonify({
                    'error': 'validation_error',
                    'message': 'Tenant ID is required for super admin'
                }), 400
        
        # Create beneficiary
        beneficiary = BeneficiaryService.create_beneficiary(user_data, beneficiary_data)
        
        if not beneficiary:
            return jsonify({
                'error': 'creation_failed',
                'message': 'Failed to create beneficiary. User may already exist with a beneficiary profile.'
            }), 400
        
        result = BeneficiarySchema().dump(beneficiary)
        return jsonify({
            'message': 'Beneficiary created successfully',
            'beneficiary': result
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': 'validation_error',
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.exception(f"Create beneficiary error: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'message': 'An unexpected error occurred'
        }), 500 