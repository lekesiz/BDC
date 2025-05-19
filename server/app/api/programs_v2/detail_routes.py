from flask import jsonify
from flask_jwt_extended import jwt_required

from app.models.program import Program

from . import programs_bp


@programs_bp.route('/programs/<int:program_id>', methods=['GET'])
@jwt_required()
def get_program(program_id):
    """Retrieve single program with modules."""
    program = Program.query.get_or_404(program_id)
    result = program.to_dict()
    if hasattr(program, 'modules'):
        result['modules'] = [m.to_dict() for m in program.modules]
    return jsonify(result), 200 