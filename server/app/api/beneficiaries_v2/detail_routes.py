from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from marshmallow import ValidationError

from app.middleware.request_context import role_required
from app.services import BeneficiaryService
from app.schemas import (
    BeneficiarySchema,
    BeneficiaryUpdateSchema,
    BeneficiaryCreateSchema,
)
from app.utils import cache_response
from app.models import Beneficiary

from . import beneficiaries_bp


@beneficiaries_bp.route('/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@cache_response(timeout=300, key_prefix='beneficiary')
def get_beneficiary(beneficiary_id):
    """Retrieve single beneficiary by ID (v2 refactor)."""
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        # Permissions
        if current_user.role == 'trainer' and beneficiary.trainer_id != current_user.id:
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403
        if current_user.role == 'student' and beneficiary.user_id != current_user.id:
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        return jsonify(BeneficiarySchema().dump(beneficiary)), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>', methods=['PUT'])
@jwt_required()
def put_beneficiary(beneficiary_id):
    """Full update beneficiary."""
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        # Permission checks similar to GET logic
        if current_user.role == 'trainer' and beneficiary.trainer_id != current_user.id:
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403
        if current_user.role == 'student' and beneficiary.user_id != current_user.id:
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        data = request.get_json()
        validated = BeneficiaryUpdateSchema().load(data)
        updated = BeneficiaryService.update_beneficiary(beneficiary_id, validated)
        return jsonify(BeneficiarySchema().dump(updated)), 200
    except ValidationError as ve:
        return jsonify({'error': 'validation_error', 'message': 'Validation failed', 'errors': ve.messages}), 400
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>', methods=['PATCH'])
@jwt_required()
def patch_beneficiary(beneficiary_id):
    """Partial update beneficiary."""
    return put_beneficiary(beneficiary_id)


@beneficiaries_bp.route('/<int:beneficiary_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def delete_beneficiary(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        if not BeneficiaryService.delete_beneficiary(beneficiary_id):
            return jsonify({'error': 'deletion_failed', 'message': 'Failed to delete'}), 400
        return jsonify({'message': 'Beneficiary deleted'}), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500 