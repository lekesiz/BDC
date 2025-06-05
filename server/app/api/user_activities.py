"""User activities API."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.models.activity import Activity
from app.extensions import db

from app.utils.logging import logger

user_activities_bp = Blueprint('user_activities', __name__)

@user_activities_bp.route('/api/users/<int:user_id>/activities', methods=['GET'])
@jwt_required()
def get_user_activities(user_id):
    """Get user activities."""
    # Check if user exists
    user = User.query.get_or_404(user_id)
    
    activities = Activity.query.filter_by(user_id=user_id)\
                             .order_by(Activity.created_at.desc())\
                             .limit(50).all()
    
    return jsonify({
        'activities': [{
            'id': activity.id,
            'type': activity.type,
            'description': activity.description,
            'created_at': activity.created_at.isoformat() if activity.created_at else None,
            'metadata': activity.activity_data
        } for activity in activities]
    })

@user_activities_bp.route('/api/users/<int:user_id>/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions(user_id):
    """Get user test sessions."""
    from app.models.test import TestSession
    
    sessions = TestSession.query\
                        .filter_by(beneficiary_id=user_id)\
                        .order_by(TestSession.created_at.desc())\
                        .limit(20).all()
    
    return jsonify({
        'sessions': [{
            'id': session.id,
            'test_id': session.test_set_id,
            'status': session.status,
            'score': session.score,
            'max_score': session.max_score,
            'passed': session.passed,
            'start_time': session.start_time.isoformat() if session.start_time else None,
            'end_time': session.end_time.isoformat() if session.end_time else None,
        } for session in sessions]
    })

@user_activities_bp.route('/api/users/<int:user_id>/documents', methods=['GET'])
@jwt_required()
def get_user_documents(user_id):
    """Get user documents."""
    from app.models.document import Document
    
    documents = Document.query\
                       .filter_by(upload_by=user_id)\
                       .order_by(Document.created_at.desc())\
                       .limit(20).all()
    
    return jsonify({
        'documents': [{
            'id': doc.id,
            'title': doc.title,
            'type': doc.type,
            'size': doc.size,
            'created_at': doc.created_at.isoformat() if doc.created_at else None,
        } for doc in documents]
    })
