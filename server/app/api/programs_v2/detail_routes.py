from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.program import Program
from app.models.program import ProgramEnrollment  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.beneficiary import Beneficiary  # noqa: E402

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


# New: list enrollments for program (parity with legacy API)

@programs_bp.route('/programs/<int:program_id>/enrollments', methods=['GET'])
@jwt_required()
def list_program_enrollments(program_id):
    """Return enrollments for a program (v2 alias)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Ensure program exists and belongs to same tenant if applicable
    program = Program.query.get_or_404(program_id)
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403

    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    return jsonify([e.to_dict() for e in enrollments]), 200


@programs_bp.route('/programs/<int:program_id>/students', methods=['GET'])
@jwt_required()
def list_program_students(program_id):
    """Return enrolled students for a program.
    
    This endpoint returns a simplified list of students (beneficiaries)
    enrolled in a program with only id, full_name, and email fields.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Ensure program exists and belongs to same tenant if applicable
    program = Program.query.get_or_404(program_id)
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all enrollments for the program
    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    
    # Extract beneficiary IDs
    beneficiary_ids = [enrollment.beneficiary_id for enrollment in enrollments]
    
    # Get beneficiary details
    beneficiaries = Beneficiary.query.filter(Beneficiary.id.in_(beneficiary_ids)).all()
    
    # Format response with simplified data
    students = []
    for beneficiary in beneficiaries:
        if beneficiary.user:
            students.append({
                'id': beneficiary.id,
                'full_name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                'email': beneficiary.user.email
            })
    
    return jsonify(students), 200