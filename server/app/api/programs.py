"""Programs API endpoints."""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.user import User
from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession, SessionAttendance
from app.models.beneficiary import Beneficiary

programs_bp = Blueprint('programs', __name__)

@programs_bp.route('/programs', methods=['GET'])
@jwt_required()
def get_programs():
    """Get all programs."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Query programs
    query = Program.query
    
    # Filter by tenant
    if user.tenant_id:
        query = query.filter_by(tenant_id=user.tenant_id)
    
    # Filter active programs
    query = query.filter_by(is_active=True)
    
    programs = query.order_by(Program.created_at.desc()).all()
    
    return jsonify([program.to_dict() for program in programs]), 200


@programs_bp.route('/programs/<int:program_id>', methods=['GET'])
@jwt_required()
def get_program(program_id):
    """Get a specific program."""
    program = Program.query.get_or_404(program_id)
    
    # Get modules
    modules = ProgramModule.query.filter_by(program_id=program_id)\
        .order_by(ProgramModule.order).all()
    
    result = program.to_dict()
    result['modules'] = [module.to_dict() for module in modules]
    
    return jsonify(result), 200


@programs_bp.route('/programs', methods=['POST'])
@jwt_required()
def create_program():
    """Create a new program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check permissions
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        program = Program(
            name=data['name'],
            description=data.get('description'),
            code=data.get('code'),
            duration=data.get('duration'),
            level=data.get('level'),
            category=data.get('category'),
            prerequisites=data.get('prerequisites'),
            minimum_attendance=data.get('minimum_attendance', 80.0),
            passing_score=data.get('passing_score', 70.0),
            max_participants=data.get('max_participants'),
            tenant_id=user.tenant_id,
            created_by_id=user_id
        )
        
        if 'start_date' in data:
            program.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            program.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        db.session.add(program)
        db.session.commit()
        
        # Emit program creation event via Socket.IO
        try:
            from app.realtime import emit_to_tenant
            emit_to_tenant(user.tenant_id, 'program_created', {
                'program': program.to_dict(),
                'message': f'New program "{program.name}" has been created'
            })
        except Exception as e:
            current_app.logger.warning(f'Failed to emit program_created event: {e}')
        
        return jsonify(program.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@programs_bp.route('/programs/<int:program_id>', methods=['PUT'])
@jwt_required()
def update_program(program_id):
    """Update a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    program = Program.query.get_or_404(program_id)
    
    # Check permissions
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    for field in ['name', 'description', 'duration', 'level', 'category', 
                 'prerequisites', 'minimum_attendance', 'passing_score', 
                 'max_participants', 'status']:
        if field in data:
            setattr(program, field, data[field])
    
    if 'start_date' in data:
        program.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if 'end_date' in data:
        program.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    db.session.commit()
    
    # Emit program update event via Socket.IO
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(program.tenant_id, 'program_updated', {
            'program': program.to_dict(),
            'message': f'Program "{program.name}" has been updated'
        })
    except Exception as e:
        current_app.logger.warning(f'Failed to emit program_updated event: {e}')
    
    return jsonify(program.to_dict()), 200


@programs_bp.route('/programs/<int:program_id>', methods=['DELETE'])
@jwt_required()
def delete_program(program_id):
    """Delete a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    program = Program.query.get_or_404(program_id)
    
    # Check permissions
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if program belongs to user's tenant
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Store program info for the event
        program_data = program.to_dict()
        tenant_id = program.tenant_id
        
        # Delete the program (cascade will handle related records)
        db.session.delete(program)
        db.session.commit()
        
        # Emit program deletion event via Socket.IO
        try:
            from app.realtime import emit_to_tenant
            emit_to_tenant(tenant_id, 'program_deleted', {
                'program': program_data,
                'program_id': program_id,
                'message': f'Program "{program_data["name"]}" has been deleted'
            })
        except Exception as e:
            current_app.logger.warning(f'Failed to emit program_deleted event: {e}')
        
        return jsonify({'message': 'Program deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@programs_bp.route('/programs/<int:program_id>/modules', methods=['POST'])
@jwt_required()
def create_module(program_id):
    """Create a program module."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    program = Program.query.get_or_404(program_id)
    
    # Check permissions
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        module = ProgramModule(
            program_id=program_id,
            name=data['name'],
            description=data.get('description'),
            order=data.get('order', 0),
            content=data.get('content'),
            resources=data.get('resources', []),
            duration=data.get('duration'),
            is_mandatory=data.get('is_mandatory', True)
        )
        
        db.session.add(module)
        db.session.commit()
        
        return jsonify(module.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@programs_bp.route('/programs/<int:program_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_beneficiary(program_id):
    """Enroll a beneficiary in a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    program = Program.query.get_or_404(program_id)
    
    # Check if program is active
    if program.status != 'active':
        return jsonify({'error': 'Program is not active'}), 400
    
    # Get beneficiary
    beneficiary_id = data.get('beneficiary_id')
    
    if user.role == 'trainee':
        # Student enrolling themselves
        beneficiary = Beneficiary.query.filter_by(user_id=user_id).first()
        if not beneficiary:
            return jsonify({'error': 'Beneficiary not found'}), 404
        beneficiary_id = beneficiary.id
    else:
        # Admin/trainer enrolling someone
        if not beneficiary_id:
            return jsonify({'error': 'Beneficiary ID required'}), 400
        beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    
    # Check if already enrolled
    existing = ProgramEnrollment.query.filter_by(
        program_id=program_id,
        beneficiary_id=beneficiary_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already enrolled'}), 400
    
    try:
        enrollment = ProgramEnrollment(
            program_id=program_id,
            beneficiary_id=beneficiary_id,
            status='enrolled'
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify(enrollment.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@programs_bp.route('/programs/<int:program_id>/enrollments', methods=['GET'])
@jwt_required()
def get_enrollments(program_id):
    """Get program enrollments."""
    program = Program.query.get_or_404(program_id)
    
    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    
    return jsonify([enrollment.to_dict() for enrollment in enrollments]), 200


@programs_bp.route('/programs/<int:program_id>/sessions', methods=['GET'])
@jwt_required()
def get_program_sessions(program_id):
    """Get program sessions."""
    program = Program.query.get_or_404(program_id)
    
    sessions = TrainingSession.query.filter_by(program_id=program_id)\
        .order_by(TrainingSession.session_date).all()
    
    return jsonify([session.to_dict() for session in sessions]), 200


@programs_bp.route('/programs/<int:program_id>/sessions', methods=['POST'])
@jwt_required()
def create_session(program_id):
    """Create a training session."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    program = Program.query.get_or_404(program_id)
    
    # Check permissions
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        session = TrainingSession(
            program_id=program_id,
            module_id=data.get('module_id'),
            trainer_id=data.get('trainer_id', user_id),
            title=data['title'],
            description=data.get('description'),
            session_date=datetime.strptime(data['session_date'], '%Y-%m-%d %H:%M'),
            duration=data.get('duration'),
            location=data.get('location'),
            online_link=data.get('online_link'),
            max_participants=data.get('max_participants'),
            attendance_required=data.get('attendance_required', True)
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify(session.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@programs_bp.route('/sessions/<int:session_id>/attendance', methods=['POST'])
@jwt_required()
def record_attendance(session_id):
    """Record session attendance."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    session = TrainingSession.query.get_or_404(session_id)
    
    # Get beneficiary
    if user.role == 'trainee':
        beneficiary = Beneficiary.query.filter_by(user_id=user_id).first()
        if not beneficiary:
            return jsonify({'error': 'Beneficiary not found'}), 404
        beneficiary_id = beneficiary.id
    else:
        beneficiary_id = data.get('beneficiary_id')
        if not beneficiary_id:
            return jsonify({'error': 'Beneficiary ID required'}), 400
    
    # Check if already recorded
    existing = SessionAttendance.query.filter_by(
        session_id=session_id,
        beneficiary_id=beneficiary_id
    ).first()
    
    if existing:
        # Update existing record
        existing.status = data.get('status', existing.status)
        if data.get('status') == 'present':
            existing.check_in_time = datetime.utcnow()
        db.session.commit()
        return jsonify(existing.to_dict()), 200
    
    try:
        attendance = SessionAttendance(
            session_id=session_id,
            beneficiary_id=beneficiary_id,
            status=data.get('status', 'registered')
        )
        
        if data.get('status') == 'present':
            attendance.check_in_time = datetime.utcnow()
        
        db.session.add(attendance)
        db.session.commit()
        
        return jsonify(attendance.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@programs_bp.route('/programs/categories', methods=['GET'])
@jwt_required()
def get_program_categories():
    """Get available program categories."""
    categories = [
        {'value': 'technical', 'label': 'Technical Skills'},
        {'value': 'soft_skills', 'label': 'Soft Skills'},
        {'value': 'leadership', 'label': 'Leadership Development'},
        {'value': 'communication', 'label': 'Communication'},
        {'value': 'management', 'label': 'Management'},
        {'value': 'sales', 'label': 'Sales & Marketing'},
        {'value': 'it', 'label': 'Information Technology'},
        {'value': 'finance', 'label': 'Finance & Accounting'}
    ]
    
    return jsonify(categories), 200


@programs_bp.route('/programs/levels', methods=['GET'])
@jwt_required()
def get_program_levels():
    """Get available program levels."""
    levels = [
        {'value': 'beginner', 'label': 'Beginner'},
        {'value': 'intermediate', 'label': 'Intermediate'},
        {'value': 'advanced', 'label': 'Advanced'},
        {'value': 'expert', 'label': 'Expert'}
    ]
    
    return jsonify(levels), 200


@programs_bp.route('/programs/<int:program_id>/students', methods=['GET'])
@jwt_required()
def get_program_students(program_id):
    """Return enrolled students (beneficiaries) for a program."""
    # Reuse existing enrollments
    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    students = []
    for enrollment in enrollments:
        beneficiary = enrollment.beneficiary
        if not beneficiary or not beneficiary.user:
            continue
        students.append({
            'id': beneficiary.id,
            'full_name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
            'email': beneficiary.user.email
        })
    return jsonify(students), 200