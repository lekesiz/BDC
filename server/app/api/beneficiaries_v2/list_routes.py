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