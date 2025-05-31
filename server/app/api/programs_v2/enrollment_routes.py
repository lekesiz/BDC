"""Program enrollment API endpoints."""

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.models.program import Program, ProgramEnrollment
from app.models.beneficiary import Beneficiary

from . import programs_bp


@programs_bp.route('/programs/<int:program_id>/enrollments', methods=['GET'])
@jwt_required()
def get_program_enrollments(program_id):
    """Get all enrollments for a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user is authorized
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ensure program exists and belongs to same tenant
    program = Program.query.get_or_404(program_id)
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get enrollments
    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    
    return jsonify([enrollment.to_dict() for enrollment in enrollments]), 200


@programs_bp.route('/programs/<int:program_id>/students', methods=['GET'])
@jwt_required() 
def get_program_students(program_id):
    """Get enrolled students (beneficiaries) for a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user is authorized
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ensure program exists and belongs to same tenant
    program = Program.query.get_or_404(program_id)
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get enrollments and extract student info
    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    students = []
    
    for enrollment in enrollments:
        beneficiary = enrollment.beneficiary
        if beneficiary and beneficiary.user:
            students.append({
                'id': beneficiary.id,
                'full_name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                'email': beneficiary.user.email,
                'status': enrollment.status,
                'enrollment_date': enrollment.enrollment_date.isoformat() if enrollment.enrollment_date else None,
                'progress': enrollment.progress
            })
    
    return jsonify(students), 200


@programs_bp.route('/programs/<int:program_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_beneficiary(program_id):
    """Enroll a beneficiary in a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user is authorized (admin or trainer)
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ensure program exists and belongs to same tenant
    program = Program.query.get_or_404(program_id)
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get request data
    data = request.get_json()
    beneficiary_id = data.get('beneficiary_id')
    
    # Check beneficiary exists
    beneficiary = Beneficiary.query.get(beneficiary_id)
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    # Check if beneficiary belongs to same tenant
    if beneficiary.tenant_id != program.tenant_id:
        return jsonify({'error': 'Beneficiary must belong to same tenant as program'}), 400
    
    # Check if already enrolled
    existing_enrollment = ProgramEnrollment.query.filter_by(
        program_id=program_id,
        beneficiary_id=beneficiary_id
    ).first()
    
    if existing_enrollment:
        return jsonify({'error': 'Beneficiary is already enrolled in this program'}), 400
    
    # Check if program has max participants and if it's reached
    if program.max_participants and program.enrollments.count() >= program.max_participants:
        return jsonify({'error': 'Maximum number of participants reached'}), 400
    
    # Create enrollment
    enrollment = ProgramEnrollment(
        program_id=program_id,
        beneficiary_id=beneficiary_id,
        enrollment_date=datetime.utcnow(),
        status='enrolled'
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify(enrollment.to_dict()), 201