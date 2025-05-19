from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError

from app.middleware.request_context import role_required
from app.services import BeneficiaryService, NoteService
from app.schemas import NoteSchema, NoteCreateSchema

from . import beneficiaries_bp


def _can_access_notes(beneficiary):
    """Permissions helper for notes."""
    if current_user.role == 'super_admin':
        return True
    if current_user.role == 'tenant_admin':
        tenant_id = current_user.tenants[0].id if current_user.tenants else None
        return tenant_id and beneficiary.tenant_id == tenant_id
    if current_user.role == 'trainer':
        return beneficiary.trainer_id == current_user.id
    if current_user.role == 'student':
        return beneficiary.user_id == current_user.id
    return False


@beneficiaries_bp.route('/<int:beneficiary_id>/notes', methods=['GET'])
@jwt_required()
def list_notes(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        if not _can_access_notes(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        user_id = request.args.get('user_id', type=int)
        note_type = request.args.get('type')
        is_private = request.args.get('is_private', type=lambda v: v.lower() == 'true' if v else None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # students can only see their own non-private notes
        if current_user.role == 'student':
            is_private = False
            user_id = current_user.id

        notes, total, pages = NoteService.get_notes(
            beneficiary_id=beneficiary_id,
            user_id=user_id,
            type=note_type,
            is_private=is_private,
            page=page,
            per_page=per_page,
        )

        return (
            jsonify({
                'items': NoteSchema(many=True).dump(notes),
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
            }),
            200,
        )
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/notes', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def create_note(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        if not _can_access_notes(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        data = NoteCreateSchema().load(request.json)
        data['beneficiary_id'] = beneficiary_id
        note = NoteService.create_note(current_user.id, data)
        if not note:
            return jsonify({'error': 'creation_failed', 'message': 'Failed to create note'}), 400
        return NoteSchema().jsonify(note), 201
    except ValidationError as ve:
        return jsonify({'error': 'validation_error', 'message': 'Validation failed', 'errors': ve.messages}), 400
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/notes/<int:note_id>', methods=['PATCH'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def update_note(note_id):
    try:
        note = NoteService.get_note(note_id)
        if not note:
            return jsonify({'error': 'not_found', 'message': 'Note not found'}), 404

        beneficiary = BeneficiaryService.get_beneficiary(note.beneficiary_id)
        if not beneficiary or not _can_access_notes(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        updated = NoteService.update_note(note_id, request.json)
        return NoteSchema().jsonify(updated), 200
    except ValidationError as ve:
        return jsonify({'error': 'validation_error', 'message': 'Validation failed', 'errors': ve.messages}), 400
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def delete_note(note_id):
    try:
        note = NoteService.get_note(note_id)
        if not note:
            return jsonify({'error': 'not_found', 'message': 'Note not found'}), 404

        beneficiary = BeneficiaryService.get_beneficiary(note.beneficiary_id)
        if not beneficiary or not _can_access_notes(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        if not NoteService.delete_note(note_id):
            return jsonify({'error': 'deletion_failed', 'message': 'Failed to delete'}), 400
        return jsonify({'message': 'Note deleted'}), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500 