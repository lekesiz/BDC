from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.services.program_service import ProgramService

from . import programs_bp


def _check_admin(user):
    return user.role in ['super_admin', 'tenant_admin']


@programs_bp.route('/programs', methods=['POST'])
@jwt_required()
def create_program():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    # Extract name and pass other fields as kwargs
    name = data.pop('name')
    program = ProgramService.create_program(
        name=name, 
        tenant_id=user.tenant_id, 
        created_by_id=user_id,
        **data
    )
    return jsonify(program.to_dict()), 201


@programs_bp.route('/programs/<int:program_id>', methods=['PUT'])
@jwt_required()
def update_program(program_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
    program = ProgramService.get_program(program_id)
    if not program:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json()
    if 'name' in data:
        program.name = data['name']
    program.updated_at = datetime.utcnow()
    ProgramService.update_program(program, **data)
    return jsonify(program.to_dict()), 200


@programs_bp.route('/programs/<int:program_id>', methods=['DELETE'])
@jwt_required()
def delete_program(program_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
    program = ProgramService.get_program(program_id)
    if not program:
        return jsonify({'error': 'Not found'}), 404
    ProgramService.delete_program(program)
    return jsonify({'message': 'deleted'}), 200 