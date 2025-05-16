"""Portal API for student/beneficiary dashboard."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    User, Beneficiary, Program, ProgramEnrollment, TrainingSession, 
    SessionAttendance, Document, TestSession, Appointment, Evaluation,
    TestSet, Question, Response, AIFeedback
)
from app.middleware.request_context import auth_required, role_required
from app.utils import cache_response


portal_bp = Blueprint('portal', __name__)


@portal_bp.route('/test', methods=['GET'])
def test_portal():
    """Test endpoint to verify portal API is working."""
    return jsonify({
        'status': 'success',
        'message': 'Portal API is working',
        'timestamp': datetime.utcnow().isoformat()
    })


@portal_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get student portal dashboard data."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is a student
        if user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        # Get the beneficiary profile for the current user
        beneficiary = Beneficiary.query.filter_by(user_id=user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found for this user'
            }), 404
        
        # Get enrolled programs
        enrollments = ProgramEnrollment.query.filter_by(
            beneficiary_id=beneficiary.id,
            status='enrolled'
        ).all()
        
        # Get upcoming sessions
        upcoming_sessions = db.session.query(TrainingSession).join(
            SessionAttendance
        ).filter(
            SessionAttendance.beneficiary_id == beneficiary.id,
            TrainingSession.session_date >= datetime.utcnow(),
            TrainingSession.status == 'scheduled'
        ).order_by(TrainingSession.session_date).limit(5).all()
        
        # Get recent test sessions
        recent_tests = TestSession.query.filter_by(
            beneficiary_id=beneficiary.id
        ).order_by(TestSession.created_at.desc()).limit(5).all()
        
        # Calculate overall progress
        total_progress = 0
        completed_programs = 0
        
        for enrollment in enrollments:
            if enrollment.progress:
                total_progress += enrollment.progress
            if enrollment.status == 'completed':
                completed_programs += 1
        
        average_progress = total_progress / len(enrollments) if enrollments else 0
        
        return jsonify({
            'user': {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'profile_picture': user.profile_picture
            },
            'beneficiary': beneficiary.to_dict(),
            'stats': {
                'enrolled_programs': len(enrollments),
                'completed_programs': completed_programs,
                'average_progress': round(average_progress, 2),
                'total_attendance_rate': beneficiary.attendance_rate if hasattr(beneficiary, 'attendance_rate') else 0
            },
            'upcoming_sessions': [session.to_dict() for session in upcoming_sessions],
            'recent_tests': [test.to_dict() for test in recent_tests]
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    """Get student's enrolled courses/programs."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        # Get query parameters
        status = request.args.get('status')  # enrolled, completed, all
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = ProgramEnrollment.query.filter_by(beneficiary_id=beneficiary.id)
        
        if status and status != 'all':
            query = query.filter_by(status=status)
        
        # Paginate results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Get detailed program info
        enrollments_data = []
        for enrollment in pagination.items:
            enrollment_dict = enrollment.to_dict()
            
            # Add additional program details
            if enrollment.program:
                enrollment_dict['program']['modules'] = [
                    module.to_dict() for module in enrollment.program.modules
                ]
                enrollment_dict['program']['sessions'] = [
                    session.to_dict() for session in enrollment.program.sessions
                ]
            
            enrollments_data.append(enrollment_dict)
        
        return jsonify({
            'enrollments': enrollments_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """Get student's progress tracking across all programs."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        # Get all enrollments
        enrollments = ProgramEnrollment.query.filter_by(
            beneficiary_id=beneficiary.id
        ).all()
        
        progress_data = []
        
        for enrollment in enrollments:
            # Get attendance for this program
            attended_sessions = db.session.query(SessionAttendance).join(
                TrainingSession
            ).filter(
                TrainingSession.program_id == enrollment.program_id,
                SessionAttendance.beneficiary_id == beneficiary.id,
                SessionAttendance.status == 'present'
            ).count()
            
            total_sessions = TrainingSession.query.filter_by(
                program_id=enrollment.program_id
            ).count()
            
            # Get test scores for this program
            test_scores = db.session.query(
                func.avg(TestSession.score)
            ).join(TestSet).filter(
                TestSet.tenant_id == enrollment.program.tenant_id,
                TestSession.beneficiary_id == beneficiary.id,
                TestSession.status == 'completed'
            ).scalar() or 0
            
            progress_data.append({
                'program': {
                    'id': enrollment.program.id,
                    'name': enrollment.program.name,
                    'code': enrollment.program.code,
                    'category': enrollment.program.category
                },
                'enrollment_date': enrollment.enrollment_date.isoformat(),
                'status': enrollment.status,
                'progress_percent': enrollment.progress,
                'attendance': {
                    'attended': attended_sessions,
                    'total': total_sessions,
                    'rate': enrollment.attendance_rate
                },
                'scores': {
                    'average': round(test_scores, 2),
                    'overall': enrollment.overall_score
                },
                'completion': {
                    'is_completed': enrollment.status == 'completed',
                    'date': enrollment.completion_date.isoformat() if enrollment.completion_date else None,
                    'certificate_issued': enrollment.certificate_issued,
                    'certificate_number': enrollment.certificate_number
                }
            })
        
        return jsonify({
            'progress': progress_data,
            'summary': {
                'total_programs': len(enrollments),
                'completed_programs': sum(1 for e in enrollments if e.status == 'completed'),
                'active_programs': sum(1 for e in enrollments if e.status == 'enrolled'),
                'average_progress': sum(e.progress for e in enrollments) / len(enrollments) if enrollments else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_achievements():
    """Get student's achievements and badges."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        # Get completed programs
        completed_enrollments = ProgramEnrollment.query.filter_by(
            beneficiary_id=beneficiary.id,
            status='completed'
        ).all()
        
        # Get all test sessions with high scores
        high_score_tests = TestSession.query.filter(
            TestSession.beneficiary_id == beneficiary.id,
            TestSession.score >= 90,
            TestSession.status == 'completed'
        ).all()
        
        # Create achievements list
        achievements = []
        
        # Program completion achievements
        for enrollment in completed_enrollments:
            achievements.append({
                'type': 'program_completion',
                'title': f'Completed {enrollment.program.name}',
                'description': f'Successfully completed the {enrollment.program.name} program',
                'date': enrollment.completion_date.isoformat() if enrollment.completion_date else None,
                'category': enrollment.program.category,
                'badge': {
                    'name': f'{enrollment.program.category}_completion',
                    'color': 'gold'
                },
                'certificate': {
                    'issued': enrollment.certificate_issued,
                    'number': enrollment.certificate_number
                }
            })
        
        # High score achievements
        for test_session in high_score_tests:
            test_set = TestSet.query.get(test_session.test_set_id)
            achievements.append({
                'type': 'high_score',
                'title': f'Excellence in {test_set.title}',
                'description': f'Scored {test_session.score}% in {test_set.title}',
                'date': test_session.end_time.isoformat() if test_session.end_time else None,
                'category': test_set.category,
                'badge': {
                    'name': 'high_achiever',
                    'color': 'silver'
                }
            })
        
        # Perfect attendance achievements
        programs_with_perfect_attendance = []
        enrollments = ProgramEnrollment.query.filter_by(
            beneficiary_id=beneficiary.id
        ).all()
        
        for enrollment in enrollments:
            if enrollment.attendance_rate >= 100:
                programs_with_perfect_attendance.append(enrollment)
                achievements.append({
                    'type': 'perfect_attendance',
                    'title': f'Perfect Attendance - {enrollment.program.name}',
                    'description': '100% attendance in program',
                    'date': datetime.utcnow().isoformat(),
                    'category': 'attendance',
                    'badge': {
                        'name': 'attendance_star',
                        'color': 'bronze'
                    }
                })
        
        # Sort achievements by date
        achievements.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
        
        return jsonify({
            'achievements': achievements,
            'stats': {
                'total_achievements': len(achievements),
                'completed_programs': len(completed_enrollments),
                'high_scores': len(high_score_tests),
                'perfect_attendance': len(programs_with_perfect_attendance)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments():
    """Get student's skill assessments and test results."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        # Get query parameters
        status = request.args.get('status')  # completed, in_progress, all
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = TestSession.query.filter_by(beneficiary_id=beneficiary.id)
        
        if status and status != 'all':
            query = query.filter_by(status=status)
        
        # Order by most recent first
        query = query.order_by(TestSession.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Get detailed assessment info
        assessments_data = []
        
        for session in pagination.items:
            session_dict = session.to_dict()
            
            # Get test set details
            test_set = TestSet.query.get(session.test_set_id)
            if test_set:
                session_dict['test'] = test_set.to_dict()
                
                # Get questions answered
                responses = Response.query.filter_by(
                    session_id=session.id
                ).all()
                
                session_dict['responses_count'] = len(responses)
                session_dict['correct_responses'] = sum(
                    1 for r in responses if r.is_correct
                )
            
            # Get AI feedback if available
            ai_feedback = AIFeedback.query.filter_by(
                session_id=session.id,
                status='approved'
            ).first()
            
            if ai_feedback:
                session_dict['feedback'] = ai_feedback.to_dict()
            
            assessments_data.append(session_dict)
        
        return jsonify({
            'assessments': assessments_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """Get student's calendar events including sessions and appointments."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.utcnow().replace(day=1)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        if not end_date:
            # Last day of current month
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        events = []
        
        # Get training sessions
        sessions = db.session.query(TrainingSession).join(
            SessionAttendance
        ).filter(
            SessionAttendance.beneficiary_id == beneficiary.id,
            TrainingSession.session_date >= start_date,
            TrainingSession.session_date <= end_date
        ).all()
        
        for session in sessions:
            events.append({
                'id': f'session_{session.id}',
                'type': 'training_session',
                'title': session.title,
                'description': session.description,
                'start': session.session_date.isoformat(),
                'end': (session.session_date + timedelta(minutes=session.duration)).isoformat() if session.duration else None,
                'location': session.location,
                'online_link': session.online_link,
                'status': session.status,
                'program': {
                    'id': session.program.id,
                    'name': session.program.name
                } if session.program else None
            })
        
        # Get appointments
        appointments = Appointment.query.filter(
            Appointment.beneficiary_id == beneficiary.id,
            Appointment.start_time >= start_date,
            Appointment.start_time <= end_date
        ).all()
        
        for appointment in appointments:
            events.append({
                'id': f'appointment_{appointment.id}',
                'type': 'appointment',
                'title': appointment.title,
                'description': appointment.description,
                'start': appointment.start_time.isoformat(),
                'end': appointment.end_time.isoformat(),
                'location': appointment.location,
                'status': appointment.status,
                'trainer': {
                    'id': appointment.trainer.id,
                    'name': appointment.trainer.full_name
                } if appointment.trainer else None
            })
        
        # Sort events by start time
        events.sort(key=lambda x: x['start'])
        
        return jsonify({
            'events': events,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/resources', methods=['GET'])
@jwt_required()
def get_resources():
    """Get student's resources and documents."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        # Get query parameters
        document_type = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query for documents
        query = Document.query.filter_by(
            beneficiary_id=beneficiary.id,
            is_active=True
        )
        
        if document_type:
            query = query.filter_by(document_type=document_type)
        
        # Order by most recent first
        query = query.order_by(Document.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Get program resources
        program_resources = []
        enrollments = ProgramEnrollment.query.filter_by(
            beneficiary_id=beneficiary.id,
            status='enrolled'
        ).all()
        
        for enrollment in enrollments:
            if enrollment.program:
                for module in enrollment.program.modules:
                    if module.resources:
                        for resource in module.resources:
                            program_resources.append({
                                'program': {
                                    'id': enrollment.program.id,
                                    'name': enrollment.program.name
                                },
                                'module': {
                                    'id': module.id,
                                    'name': module.name
                                },
                                'resource': resource
                            })
        
        return jsonify({
            'documents': [doc.to_dict() for doc in pagination.items],
            'program_resources': program_resources,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@portal_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get student's complete profile information."""
    try:
        # Check if user is a student
        if current_user.role != 'student':
            return jsonify({
                'error': 'unauthorized',
                'message': 'This endpoint is only accessible to students'
            }), 403
            
        beneficiary = Beneficiary.query.filter_by(user_id=current_user.id).first()
        
        if not beneficiary:
            return jsonify({
                'error': 'beneficiary_not_found',
                'message': 'Beneficiary profile not found'
            }), 404
        
        profile_data = {
            'user': current_user.to_dict(include_profile=True),
            'beneficiary': beneficiary.to_dict(),
            'trainer': beneficiary.trainer.to_dict() if beneficiary.trainer else None,
            'enrollments': [e.to_dict() for e in beneficiary.program_enrollments.all()],
            'recent_activity': {
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'recent_sessions': [],
                'recent_tests': []
            }
        }
        
        # Get recent session attendance
        recent_attendance = SessionAttendance.query.filter_by(
            beneficiary_id=beneficiary.id
        ).order_by(SessionAttendance.created_at.desc()).limit(5).all()
        
        for attendance in recent_attendance:
            if attendance.session:
                profile_data['recent_activity']['recent_sessions'].append({
                    'session': attendance.session.title,
                    'date': attendance.session.session_date.isoformat(),
                    'status': attendance.status
                })
        
        # Get recent test sessions
        recent_tests = TestSession.query.filter_by(
            beneficiary_id=beneficiary.id
        ).order_by(TestSession.created_at.desc()).limit(5).all()
        
        for test in recent_tests:
            test_set = TestSet.query.get(test.test_set_id)
            profile_data['recent_activity']['recent_tests'].append({
                'test': test_set.title if test_set else 'Unknown',
                'date': test.created_at.isoformat(),
                'score': test.score,
                'status': test.status
            })
        
        return jsonify(profile_data)
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': f'An error occurred: {str(e)}'
        }), 500