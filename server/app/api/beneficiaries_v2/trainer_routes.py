from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, current_user

from app.middleware.request_context import role_required
from app.services import BeneficiaryService
from app.schemas import BeneficiarySchema

from . import beneficiaries_bp


@beneficiaries_bp.route('/<int:beneficiary_id>/trainers', methods=['GET'])
@jwt_required()
def get_beneficiary_trainers(beneficiary_id):
    """Return assigned trainer(s) for a beneficiary."""
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        trainer_info = []
        if beneficiary.trainer:
            trainer_info.append({
                'id': beneficiary.trainer.id,
                'email': beneficiary.trainer.email,
                'first_name': beneficiary.trainer.first_name,
                'last_name': beneficiary.trainer.last_name,
                'role': beneficiary.trainer.role,
            })
        return jsonify(trainer_info), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/assign-trainer', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin'])
def assign_trainer(beneficiary_id):
    """Assign a trainer to beneficiary."""
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        trainer_id = request.json.get('trainer_id')
        if not trainer_id:
            return jsonify({'error': 'validation_error', 'message': 'Trainer ID required'}), 400

        updated = BeneficiaryService.assign_trainer(beneficiary_id, trainer_id)
        if not updated:
            return jsonify({'error': 'assign_failed', 'message': 'Failed to assign trainer'}), 400

        return jsonify(BeneficiarySchema().dump(updated)), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500 