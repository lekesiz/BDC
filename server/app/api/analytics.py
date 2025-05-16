"""Analytics API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.evaluation import Evaluation
from app.models.test import TestSession
from app.models.appointment import Appointment

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get dashboard analytics for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Base statistics
    stats = {}
    
    if user.role in ['super_admin', 'tenant_admin']:
        # Admin statistics
        stats['total_users'] = User.query.filter_by(tenant_id=user.tenant_id).count()
        stats['total_beneficiaries'] = Beneficiary.query.filter_by(tenant_id=user.tenant_id).count()
        stats['total_trainers'] = User.query.filter_by(tenant_id=user.tenant_id, role='trainer').count()
        stats['total_evaluations'] = Evaluation.query.filter_by(tenant_id=user.tenant_id).count()
        
        # Role distribution for pie chart
        stats['student_count'] = User.query.filter_by(tenant_id=user.tenant_id, role='student').count()
        stats['admin_count'] = User.query.filter_by(tenant_id=user.tenant_id, role='tenant_admin').count() + \
                              User.query.filter_by(tenant_id=user.tenant_id, role='super_admin').count()
        
        # Recent activity
        stats['recent_activity'] = {
            'new_users_week': User.query.filter(
                User.tenant_id == user.tenant_id,
                User.created_at >= datetime.now() - timedelta(days=7)
            ).count(),
            'new_beneficiaries_week': Beneficiary.query.filter(
                Beneficiary.tenant_id == user.tenant_id,
                Beneficiary.created_at >= datetime.now() - timedelta(days=7)
            ).count(),
            'evaluations_completed_week': TestSession.query.join(Beneficiary).filter(
                Beneficiary.tenant_id == user.tenant_id,
                TestSession.status == 'completed',
                TestSession.end_time >= datetime.now() - timedelta(days=7)
            ).count()
        }
        
    elif user.role == 'trainer':
        # Trainer statistics
        stats['assigned_beneficiaries'] = Beneficiary.query.filter_by(trainer_id=user_id).count()
        stats['total_sessions'] = Appointment.query.filter_by(trainer_id=user_id).count()
        stats['completed_evaluations'] = TestSession.query.join(Beneficiary).filter(
            Beneficiary.trainer_id == user_id,
            TestSession.status == 'completed'
        ).count()
        stats['upcoming_sessions'] = Appointment.query.filter(
            Appointment.trainer_id == user_id,
            Appointment.start_time >= datetime.now(),
            Appointment.status == 'scheduled'
        ).count()
        
    else:  # Student/Beneficiary
        beneficiary = Beneficiary.query.filter_by(user_id=user_id).first()
        if beneficiary:
            stats['completed_tests'] = TestSession.query.filter_by(
                beneficiary_id=beneficiary.id,
                status='completed'
            ).count()
            stats['upcoming_sessions'] = Appointment.query.filter(
                Appointment.beneficiary_id == beneficiary.id,
                Appointment.start_time >= datetime.now(),
                Appointment.status == 'scheduled'
            ).count()
            stats['average_score'] = db.session.query(func.avg(TestSession.score)).filter(
                TestSession.beneficiary_id == beneficiary.id,
                TestSession.status == 'completed'
            ).scalar() or 0
    
    # Time-based analytics
    time_range = request.args.get('range', '7days')
    
    if time_range == '7days':
        start_date = datetime.now() - timedelta(days=7)
    elif time_range == '30days':
        start_date = datetime.now() - timedelta(days=30)
    else:
        start_date = datetime.now() - timedelta(days=90)
    
    # Chart data based on role
    chart_data = {}
    
    if user.role in ['super_admin', 'tenant_admin']:
        # User growth chart
        user_growth = db.session.query(
            func.date(User.created_at),
            func.count(User.id)
        ).filter(
            User.tenant_id == user.tenant_id,
            User.created_at >= start_date
        ).group_by(func.date(User.created_at)).all()
        
        chart_data['user_growth'] = [{
            'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
            'count': count
        } for date, count in user_growth if date]
        
        # Evaluation completion chart
        evaluation_completion = db.session.query(
            func.date(TestSession.end_time),
            func.count(TestSession.id)
        ).select_from(TestSession)\
        .join(Beneficiary, TestSession.beneficiary_id == Beneficiary.id)\
        .join(User, Beneficiary.user_id == User.id)\
        .filter(
            User.tenant_id == user.tenant_id,
            TestSession.status == 'completed',
            TestSession.end_time >= start_date
        ).group_by(func.date(TestSession.end_time)).all()
        
        chart_data['evaluation_completion'] = [{
            'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
            'count': count
        } for date, count in evaluation_completion if date]
    
    elif user.role == 'trainer':
        # Session completion chart
        session_completion = db.session.query(
            func.date(Appointment.start_time),
            func.count(Appointment.id)
        ).filter(
            Appointment.trainer_id == user_id,
            Appointment.status == 'completed',
            Appointment.start_time >= start_date
        ).group_by(func.date(Appointment.start_time)).all()
        
        chart_data['session_completion'] = [{
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        } for date, count in session_completion if date]
    
    return jsonify({
        'statistics': stats,
        'charts': chart_data,
        'time_range': time_range
    }), 200


@analytics_bp.route('/analytics/beneficiaries', methods=['GET'])
@jwt_required()
def get_beneficiary_analytics():
    """Get beneficiary analytics."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Query parameters
    beneficiary_id = request.args.get('beneficiary_id', type=int)
    
    if beneficiary_id:
        # Specific beneficiary analytics
        beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
        
        # Check permissions
        if user.role == 'trainer' and beneficiary.trainer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        analytics = {
            'beneficiary': {
                'id': beneficiary.id,
                'name': f"{beneficiary.first_name} {beneficiary.last_name}",
                'email': beneficiary.email
            },
            'test_performance': {
                'total_tests': TestSession.query.filter_by(beneficiary_id=beneficiary_id).count(),
                'completed_tests': TestSession.query.filter_by(
                    beneficiary_id=beneficiary_id,
                    status='completed'
                ).count(),
                'average_score': db.session.query(func.avg(TestSession.score)).filter(
                    TestSession.beneficiary_id == beneficiary_id,
                    TestSession.status == 'completed'
                ).scalar() or 0,
                'best_score': db.session.query(func.max(TestSession.score)).filter(
                    TestSession.beneficiary_id == beneficiary_id,
                    TestSession.status == 'completed'
                ).scalar() or 0
            },
            'session_attendance': {
                'total_sessions': Appointment.query.filter_by(beneficiary_id=beneficiary_id).count(),
                'attended_sessions': Appointment.query.filter_by(
                    beneficiary_id=beneficiary_id,
                    status='completed'
                ).count(),
                'missed_sessions': Appointment.query.filter_by(
                    beneficiary_id=beneficiary_id,
                    status='missed'
                ).count()
            }
        }
        
        # Progress over time
        progress_data = db.session.query(
            TestSession.completed_at,
            TestSession.score
        ).filter(
            TestSession.beneficiary_id == beneficiary_id,
            TestSession.status == 'completed'
        ).order_by(TestSession.completed_at).all()
        
        analytics['progress_chart'] = [{
            'date': completed_at.isoformat(),
            'score': score
        } for completed_at, score in progress_data]
        
        return jsonify(analytics), 200
    
    else:
        # All beneficiaries analytics
        query = Beneficiary.query
        
        if user.role == 'trainer':
            query = query.filter_by(trainer_id=user_id)
        elif user.role == 'tenant_admin':
            query = query.filter_by(tenant_id=user.tenant_id)
        
        beneficiaries = query.all()
        
        result = []
        for beneficiary in beneficiaries:
            test_stats = db.session.query(
                func.count(TestSession.id),
                func.avg(TestSession.score)
            ).filter(
                TestSession.beneficiary_id == beneficiary.id,
                TestSession.status == 'completed'
            ).first()
            
            result.append({
                'id': beneficiary.id,
                'name': f"{beneficiary.first_name} {beneficiary.last_name}",
                'email': beneficiary.email,
                'completed_tests': test_stats[0] or 0,
                'average_score': float(test_stats[1] or 0),
                'trainer': {
                    'id': beneficiary.trainer.id,
                    'name': f"{beneficiary.trainer.first_name} {beneficiary.trainer.last_name}"
                } if beneficiary.trainer else None
            })
        
        return jsonify({
            'beneficiaries': result,
            'total': len(result)
        }), 200


@analytics_bp.route('/analytics/trainers', methods=['GET'])
@jwt_required()
def get_trainer_analytics():
    """Get trainer analytics."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Query parameters
    trainer_id = request.args.get('trainer_id', type=int)
    
    if trainer_id:
        # Specific trainer analytics
        trainer = User.query.filter_by(id=trainer_id, role='trainer').first_or_404()
        
        analytics = {
            'trainer': {
                'id': trainer.id,
                'name': f"{trainer.first_name} {trainer.last_name}",
                'email': trainer.email
            },
            'beneficiaries': {
                'total': Beneficiary.query.filter_by(trainer_id=trainer_id).count(),
                'active': Beneficiary.query.filter_by(
                    trainer_id=trainer_id,
                    status='active'
                ).count()
            },
            'sessions': {
                'total': Appointment.query.filter_by(trainer_id=trainer_id).count(),
                'completed': Appointment.query.filter_by(
                    trainer_id=trainer_id,
                    status='completed'
                ).count(),
                'scheduled': Appointment.query.filter_by(
                    trainer_id=trainer_id,
                    status='scheduled'
                ).count()
            },
            'performance': {
                'average_beneficiary_score': db.session.query(func.avg(TestSession.score)).join(
                    Beneficiary
                ).filter(
                    Beneficiary.trainer_id == trainer_id,
                    TestSession.status == 'completed'
                ).scalar() or 0
            }
        }
        
        return jsonify(analytics), 200
    
    else:
        # All trainers analytics
        trainers = User.query.filter_by(
            tenant_id=user.tenant_id,
            role='trainer'
        ).all()
        
        result = []
        for trainer in trainers:
            beneficiary_count = Beneficiary.query.filter_by(trainer_id=trainer.id).count()
            session_count = Appointment.query.filter_by(trainer_id=trainer.id).count()
            
            result.append({
                'id': trainer.id,
                'name': f"{trainer.first_name} {trainer.last_name}",
                'email': trainer.email,
                'beneficiary_count': beneficiary_count,
                'session_count': session_count,
                'is_active': trainer.is_active
            })
        
        return jsonify({
            'trainers': result,
            'total': len(result)
        }), 200


@analytics_bp.route('/analytics/programs', methods=['GET'])
@jwt_required()
def get_program_analytics():
    """Get program analytics."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.models.program import Program, ProgramEnrollment, Session, SessionAttendance, Module
    
    # Query parameters
    program_id = request.args.get('program_id', type=int)
    
    if program_id:
        # Specific program analytics
        program = Program.query.get_or_404(program_id)
        
        # Get enrollment stats
        total_enrollments = ProgramEnrollment.query.filter_by(program_id=program_id).count()
        active_enrollments = ProgramEnrollment.query.filter_by(
            program_id=program_id,
            status='enrolled'
        ).count()
        completed_enrollments = ProgramEnrollment.query.filter_by(
            program_id=program_id,
            status='completed'
        ).count()
        
        # Get attendance stats
        total_sessions = Session.query.filter_by(program_id=program_id).count()
        completed_sessions = Session.query.filter_by(
            program_id=program_id,
            status='completed'
        ).count()
        
        # Calculate average attendance rate
        attendance_stats = db.session.query(
            func.avg(SessionAttendance.attendance_status == 'present')
        ).join(Session).filter(
            Session.program_id == program_id
        ).scalar() or 0
        
        # Get module progress
        modules = Module.query.filter_by(program_id=program_id).order_by(Module.order).all()
        module_progress = []
        
        for module in modules:
            module_sessions = Session.query.filter_by(module_id=module.id).count()
            completed_module_sessions = Session.query.filter_by(
                module_id=module.id,
                status='completed'
            ).count()
            
            module_progress.append({
                'module_id': module.id,
                'module_name': module.name,
                'total_sessions': module_sessions,
                'completed_sessions': completed_module_sessions,
                'completion_rate': (completed_module_sessions / module_sessions * 100) if module_sessions > 0 else 0
            })
        
        # Get test performance by program enrollees
        test_performance = db.session.query(
            func.avg(TestSession.score),
            func.count(TestSession.id)
        ).join(Beneficiary).join(ProgramEnrollment).filter(
            ProgramEnrollment.program_id == program_id,
            TestSession.status == 'completed'
        ).first()
        
        return jsonify({
            'program': {
                'id': program.id,
                'name': program.name,
                'description': program.description,
                'status': program.status
            },
            'enrollments': {
                'total': total_enrollments,
                'active': active_enrollments,
                'completed': completed_enrollments,
                'completion_rate': (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
            },
            'sessions': {
                'total': total_sessions,
                'completed': completed_sessions,
                'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            'attendance': {
                'average_rate': float(attendance_stats * 100)
            },
            'modules': module_progress,
            'test_performance': {
                'average_score': float(test_performance[0] or 0),
                'total_tests': test_performance[1] or 0
            }
        }), 200
    
    else:
        # All programs analytics
        programs = Program.query.filter_by(tenant_id=user.tenant_id).all()
        
        result = []
        for program in programs:
            # Basic stats for each program
            enrollment_count = ProgramEnrollment.query.filter_by(program_id=program.id).count()
            active_count = ProgramEnrollment.query.filter_by(
                program_id=program.id,
                status='enrolled'
            ).count()
            completed_count = ProgramEnrollment.query.filter_by(
                program_id=program.id,
                status='completed'
            ).count()
            
            # Average test score for program participants
            avg_score = db.session.query(func.avg(TestSession.score)).join(
                Beneficiary
            ).join(ProgramEnrollment).filter(
                ProgramEnrollment.program_id == program.id,
                TestSession.status == 'completed'
            ).scalar() or 0
            
            result.append({
                'id': program.id,
                'name': program.name,
                'code': program.code,
                'status': program.status,
                'enrollments': enrollment_count,
                'active_enrollments': active_count,
                'completed_enrollments': completed_count,
                'completion_rate': (completed_count / enrollment_count * 100) if enrollment_count > 0 else 0,
                'average_test_score': float(avg_score)
            })
        
        return jsonify({
            'programs': result,
            'total': len(result)
        }), 200