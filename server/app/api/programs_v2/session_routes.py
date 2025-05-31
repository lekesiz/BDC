"""Program sessions and session attendance API endpoints."""

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.user import User
from app.models.program import Program, TrainingSession, SessionAttendance
from app.models.beneficiary import Beneficiary

from . import programs_bp


@programs_bp.route('/programs/<int:program_id>/sessions', methods=['GET'])
@jwt_required()
def get_program_sessions(program_id):
    """Get all sessions for a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Ensure program exists and belongs to same tenant
    program = Program.query.get_or_404(program_id)
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Query sessions
    sessions = TrainingSession.query.filter_by(program_id=program_id).order_by(
        TrainingSession.session_date.asc()
    ).all()
    
    return jsonify([session.to_dict() for session in sessions]), 200


@programs_bp.route('/programs/<int:program_id>/sessions', methods=['POST'])
@jwt_required()
def create_program_session(program_id):
    """Create a new session for a program."""
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
    
    # Create new session
    session = TrainingSession(
        program_id=program_id,
        trainer_id=user_id,
        title=data.get('title'),
        description=data.get('description'),
        session_date=data.get('date'),
        time=data.get('time'),
        duration=data.get('duration'),
        location=data.get('location'),
        online_link=data.get('online_link'),
        max_participants=data.get('max_participants'),
        type=data.get('type', 'regular')
    )
    
    # Set module if provided
    if data.get('module_id'):
        session.module_id = data.get('module_id')
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201


@programs_bp.route('/sessions/<int:session_id>/attendance', methods=['POST'])
@jwt_required()
def record_session_attendance(session_id):
    """Record attendance for a session."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check if user is authorized (admin or trainer)
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ensure session exists
    session = TrainingSession.query.get_or_404(session_id)
    
    # Check tenant access
    if user.tenant_id and session.program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get request data
    data = request.get_json()
    attendance_records = data.get('attendance', [])
    
    # Process attendance records
    for record in attendance_records:
        beneficiary_id = record.get('beneficiary_id')
        status = record.get('status', 'present')
        notes = record.get('notes', '')
        
        # Verify beneficiary exists
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            continue
        
        # Check if attendance record already exists
        attendance = SessionAttendance.query.filter_by(
            session_id=session_id,
            beneficiary_id=beneficiary_id
        ).first()
        
        if attendance:
            # Update existing record
            attendance.status = status
            attendance.notes = notes
        else:
            # Create new record
            attendance = SessionAttendance(
                session_id=session_id,
                beneficiary_id=beneficiary_id,
                status=status,
                notes=notes
            )
            db.session.add(attendance)
    
    # Update session status if needed
    if data.get('session_status'):
        session.status = data.get('session_status')
    
    db.session.commit()
    
    return jsonify({'message': 'Attendance recorded successfully'}), 200