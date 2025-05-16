"""Notifications unread count API."""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.notification import Notification

notifications_unread_bp = Blueprint('notifications_unread', __name__)

@notifications_unread_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread notifications count for the current user."""
    user_id = get_jwt_identity()
    
    unread_count = Notification.query.filter_by(
        user_id=user_id,
        read=False
    ).count()
    
    return {
        'count': unread_count
    }, 200