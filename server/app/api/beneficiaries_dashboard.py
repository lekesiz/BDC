from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from sqlalchemy.sql.expression import case
from app.models import Beneficiary, User, Evaluation, Appointment, Document
from app.extensions import db

class BeneficiaryDashboardResource(Resource):
    @jwt_required()
    def get(self, beneficiary_id=None):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # If no beneficiary_id provided, get dashboard for current user if they are a beneficiary
        if not beneficiary_id:
            if current_user.role in ['student', 'beneficiary']:
                beneficiary = Beneficiary.query.filter_by(user_id=current_user_id).first()
                if not beneficiary:
                    return {'message': 'Beneficiary profile not found'}, 404
                beneficiary_id = beneficiary.id
            else:
                return {'message': 'Unauthorized'}, 403
        else:
            # Check permissions
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if not beneficiary:
                return {'message': 'Beneficiary not found'}, 404
                
            if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
                # Check if this is the beneficiary themselves
                if current_user.id != beneficiary.user_id:
                    return {'message': 'Unauthorized'}, 403
        
        # Get dashboard data
        dashboard_data = self._get_dashboard_data(beneficiary)
        
        return jsonify(dashboard_data)
    
    def _get_dashboard_data(self, beneficiary):
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        week_ago = now - timedelta(days=7)
        
        # Basic info
        data = {
            'beneficiary': {
                'id': beneficiary.id,
                'name': beneficiary.user.full_name,
                'email': beneficiary.user.email,
                'phone': beneficiary.phone,
                'enrollment_date': beneficiary.enrollment_date.isoformat() if beneficiary.enrollment_date else None,
                'status': beneficiary.status,
                'progress': beneficiary.progress or 0
            }
        }
        
        # Trainer info
        if beneficiary.trainer:
            data['trainer'] = {
                'id': beneficiary.trainer.id,
                'name': beneficiary.trainer.full_name,
                'email': beneficiary.trainer.email
            }
        
        # Progress statistics
        progress_records = BeneficiaryProgress.query.filter_by(
            beneficiary_id=beneficiary.id
        ).order_by(BeneficiaryProgress.created_at.desc()).limit(30).all()
        
        data['progress_history'] = [
            {
                'date': record.created_at.isoformat(),
                'progress': record.progress_value,
                'notes': record.notes
            }
            for record in progress_records
        ]
        
        # Evaluations/Tests
        evaluations = Evaluation.query.filter_by(
            beneficiary_id=beneficiary.id
        ).order_by(Evaluation.created_at.desc()).limit(10).all()
        
        data['recent_evaluations'] = [
            {
                'id': eval.id,
                'title': eval.test.title if eval.test else 'Unknown Test',
                'score': eval.score,
                'completed_at': eval.completed_at.isoformat() if eval.completed_at else None,
                'status': eval.status
            }
            for eval in evaluations
        ]
        
        # Evaluation statistics
        eval_stats = db.session.query(
            func.count(Evaluation.id).label('total'),
            func.avg(Evaluation.score).label('average_score'),
            func.sum(case((Evaluation.status == 'completed', 1), else_=0)).label('completed'),
            func.sum(case((Evaluation.status == 'in_progress', 1), else_=0)).label('in_progress')
        ).filter_by(beneficiary_id=beneficiary.id).first()
        
        data['evaluation_stats'] = {
            'total': eval_stats.total or 0,
            'average_score': float(eval_stats.average_score or 0),
            'completed': eval_stats.completed or 0,
            'in_progress': eval_stats.in_progress or 0
        }
        
        # Appointments
        upcoming_appointments = Appointment.query.filter(
            and_(
                Appointment.beneficiary_id == beneficiary.id,
                Appointment.start_time > now,
                Appointment.status != 'cancelled'
            )
        ).order_by(Appointment.start_time).limit(5).all()
        
        data['upcoming_appointments'] = [
            {
                'id': apt.id,
                'title': apt.title,
                'start_time': apt.start_time.isoformat(),
                'end_time': apt.end_time.isoformat(),
                'location': apt.location,
                'status': apt.status,
                'trainer': {
                    'id': apt.trainer.id,
                    'name': apt.trainer.full_name
                } if apt.trainer else None
            }
            for apt in upcoming_appointments
        ]
        
        # Recent documents
        recent_documents = Document.query.filter_by(
            beneficiary_id=beneficiary.id
        ).order_by(Document.created_at.desc()).limit(5).all()
        
        data['recent_documents'] = [
            {
                'id': doc.id,
                'title': doc.title,
                'type': doc.type,
                'created_at': doc.created_at.isoformat(),
                'url': doc.url
            }
            for doc in recent_documents
        ]
        
        # Activity summary
        activity_data = self._get_activity_summary(beneficiary, week_ago, month_ago)
        data['activity_summary'] = activity_data
        
        # Goals and milestones
        goals_data = self._get_goals_and_milestones(beneficiary)
        data['goals_and_milestones'] = goals_data
        
        return data
    
    def _get_activity_summary(self, beneficiary, week_ago, month_ago):
        # Weekly activity
        weekly_evaluations = Evaluation.query.filter(
            and_(
                Evaluation.beneficiary_id == beneficiary.id,
                Evaluation.created_at >= week_ago
            )
        ).count()
        
        weekly_appointments = Appointment.query.filter(
            and_(
                Appointment.beneficiary_id == beneficiary.id,
                Appointment.start_time >= week_ago
            )
        ).count()
        
        # Monthly activity
        monthly_evaluations = Evaluation.query.filter(
            and_(
                Evaluation.beneficiary_id == beneficiary.id,
                Evaluation.created_at >= month_ago
            )
        ).count()
        
        monthly_appointments = Appointment.query.filter(
            and_(
                Appointment.beneficiary_id == beneficiary.id,
                Appointment.start_time >= month_ago
            )
        ).count()
        
        return {
            'weekly': {
                'evaluations': weekly_evaluations,
                'appointments': weekly_appointments
            },
            'monthly': {
                'evaluations': monthly_evaluations,
                'appointments': monthly_appointments
            }
        }
    
    def _get_goals_and_milestones(self, beneficiary):
        # This would typically come from a Goals or Milestones model
        # For now, returning sample data
        return {
            'current_goals': [
                {
                    'id': 1,
                    'title': 'Complete JavaScript Course',
                    'progress': 75,
                    'target_date': (datetime.utcnow() + timedelta(days=30)).isoformat()
                },
                {
                    'id': 2,
                    'title': 'Build Portfolio Website',
                    'progress': 40,
                    'target_date': (datetime.utcnow() + timedelta(days=45)).isoformat()
                }
            ],
            'milestones': [
                {
                    'id': 1,
                    'title': 'Completed HTML/CSS Module',
                    'achieved_date': (datetime.utcnow() - timedelta(days=15)).isoformat()
                },
                {
                    'id': 2,
                    'title': 'First Project Submitted',
                    'achieved_date': (datetime.utcnow() - timedelta(days=7)).isoformat()
                }
            ]
        }

class BeneficiaryProgressResource(Resource):
    @jwt_required()
    def post(self, beneficiary_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check permissions
        if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
            return {'message': 'Unauthorized'}, 403
        
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            return {'message': 'Beneficiary not found'}, 404
        
        # Create progress entry
        data = request.get_json()
        progress = BeneficiaryProgress(
            beneficiary_id=beneficiary_id,
            progress_value=data.get('progress_value', beneficiary.progress),
            notes=data.get('notes'),
            recorded_by=current_user_id
        )
        
        # Update beneficiary's current progress
        beneficiary.progress = data.get('progress_value', beneficiary.progress)
        
        db.session.add(progress)
        db.session.commit()
        
        return {'message': 'Progress updated successfully'}, 200 