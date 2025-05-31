from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.program import Program, ProgramEnrollment, ProgramModule
from app.models.user import User

from . import programs_bp


@programs_bp.route('/programs/<int:program_id>/progress', methods=['GET'])
@jwt_required()
def get_program_progress(program_id):
    """Get overall progress statistics for a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant if applicable
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all enrollments for this program
    enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).all()
    
    # Calculate progress statistics
    progress_stats = {
        'total_enrollments': len(enrollments),
        'completed': sum(1 for e in enrollments if e.status == 'completed'),
        'in_progress': sum(1 for e in enrollments if e.status in ['enrolled', 'active']),
        'withdrawn': sum(1 for e in enrollments if e.status == 'withdrawn'),
        'average_progress': sum(e.progress for e in enrollments) / len(enrollments) if enrollments else 0,
        'average_attendance': sum(e.attendance_rate for e in enrollments) / len(enrollments) if enrollments else 0,
        'average_score': sum(e.overall_score for e in enrollments) / len(enrollments) if enrollments else 0,
        'completion_rate': (sum(1 for e in enrollments if e.status == 'completed') / len(enrollments) * 100) if enrollments else 0,
    }
    
    # Enhance with module-level statistics
    modules = ProgramModule.query.filter_by(program_id=program_id).order_by(ProgramModule.order).all()
    progress_stats['modules'] = [
        {
            'id': module.id,
            'name': module.name,
            # These would be calculated from actual module tracking data in a real implementation
            'completion_rate': 0,  # Placeholder for actual module completion tracking
            'average_score': 0,    # Placeholder for actual module scores
        }
        for module in modules
    ]
    
    return jsonify(progress_stats), 200


@programs_bp.route('/programs/<int:program_id>/enrollments/<int:enrollment_id>/progress', methods=['GET'])
@jwt_required()
def get_enrollment_progress(program_id, enrollment_id):
    """Get detailed progress for a specific enrollment."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant if applicable
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollment = ProgramEnrollment.query.filter_by(id=enrollment_id, program_id=program_id).first_or_404()
    
    # Get modules for this program
    modules = ProgramModule.query.filter_by(program_id=program_id).order_by(ProgramModule.order).all()
    
    # In a real implementation, we would fetch actual module progress data from a tracking table
    # For now, we'll return placeholder data
    module_progress = [
        {
            'module_id': module.id,
            'name': module.name,
            'completed': False,
            'progress': 0,
            'score': 0,
            'last_activity': None
        }
        for module in modules
    ]
    
    progress_data = {
        'enrollment': enrollment.to_dict(),
        'module_progress': module_progress,
        'overall_progress': enrollment.progress,
        'overall_score': enrollment.overall_score,
        'attendance_rate': enrollment.attendance_rate,
        'status': enrollment.status
    }
    
    return jsonify(progress_data), 200


@programs_bp.route('/programs/<int:program_id>/enrollments/<int:enrollment_id>/progress', methods=['PUT'])
@jwt_required()
def update_enrollment_progress(program_id, enrollment_id):
    """Update progress for a specific enrollment."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Only trainers and admins can update progress
    if user.role not in ['trainer', 'tenant_admin', 'super_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant if applicable
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollment = ProgramEnrollment.query.filter_by(id=enrollment_id, program_id=program_id).first_or_404()
    data = request.get_json()
    
    # Update enrollment progress fields
    if 'progress' in data:
        enrollment.progress = data['progress']
    if 'attendance_rate' in data:
        enrollment.attendance_rate = data['attendance_rate']
    if 'overall_score' in data:
        enrollment.overall_score = data['overall_score']
    if 'status' in data:
        enrollment.status = data['status']
        
        # If marked as completed, set completion_date
        if data['status'] == 'completed' and not enrollment.completion_date:
            enrollment.completion_date = datetime.utcnow()
    
    # Update individual module progress in a real implementation
    # This would involve updating records in a module progress tracking table
    
    db.session.commit()
    
    # Emit real-time event
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(
            program.tenant_id,
            'enrollment_progress_updated',
            {
                'program_id': program_id,
                'enrollment': enrollment.to_dict()
            }
        )
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed to emit enrollment_progress_updated event: {e}")
    
    return jsonify(enrollment.to_dict()), 200


@programs_bp.route('/programs/<int:program_id>/enrollments/<int:enrollment_id>/module-progress', methods=['PUT'])
@jwt_required()
def update_module_progress(program_id, enrollment_id):
    """Update progress for a specific module within an enrollment."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Only trainers and admins can update progress
    if user.role not in ['trainer', 'tenant_admin', 'super_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant if applicable
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollment = ProgramEnrollment.query.filter_by(id=enrollment_id, program_id=program_id).first_or_404()
    data = request.get_json()
    
    if not data or 'module_id' not in data:
        return jsonify({'error': 'Module ID is required'}), 400
    
    module_id = data['module_id']
    module = ProgramModule.query.filter_by(id=module_id, program_id=program_id).first_or_404()
    
    # In a real implementation, we would update or create a record in a module progress tracking table
    # For now, we'll just update the overall enrollment progress as a demonstration
    
    # Update overall enrollment progress based on module data
    if 'completed' in data and data['completed']:
        # Real implementation would recalculate overall progress based on all modules
        # For demonstration, we'll just increment progress by a percentage based on module count
        module_count = ProgramModule.query.filter_by(program_id=program_id).count()
        if module_count > 0:
            enrollment.progress = min(100, enrollment.progress + (100.0 / module_count))
    
    # If score data provided, update overall score (simple average for demo)
    if 'score' in data:
        # Real implementation would calculate weighted average based on all module scores
        module_count = ProgramModule.query.filter_by(program_id=program_id).count()
        current_score_total = enrollment.overall_score * (module_count - 1) if module_count > 1 else 0
        enrollment.overall_score = (current_score_total + data['score']) / module_count
    
    db.session.commit()
    
    # Emit real-time event (would contain actual module progress data in real implementation)
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(
            program.tenant_id,
            'module_progress_updated',
            {
                'program_id': program_id,
                'enrollment_id': enrollment_id,
                'module_id': module_id,
                'progress_data': {
                    'completed': data.get('completed', False),
                    'progress': data.get('progress', 0),
                    'score': data.get('score', 0),
                }
            }
        )
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed to emit module_progress_updated event: {e}")
    
    # Return the updated enrollment with placeholder module progress data
    return jsonify({
        'enrollment': enrollment.to_dict(),
        'module_progress': {
            'module_id': module.id,
            'name': module.name,
            'completed': data.get('completed', False),
            'progress': data.get('progress', 0),
            'score': data.get('score', 0),
            'last_activity': datetime.utcnow().isoformat()
        }
    }), 200