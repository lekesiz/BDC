"""User settings API."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.user_preference import UserPreference

user_settings_bp = Blueprint('user_settings', __name__)

@user_settings_bp.route('/api/users/settings/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user preferences."""
    user_id = get_jwt_identity()
    
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        # Create default preferences
        preferences = UserPreference(
            user_id=user_id,
            theme='light',
            language='en',
            notifications_enabled=True,
            email_notifications=True
        )
        db.session.add(preferences)
        db.session.commit()
    
    return jsonify({
        'theme': preferences.theme,
        'language': preferences.language,
        'notifications_enabled': preferences.notifications_enabled,
        'email_notifications': preferences.email_notifications
    })

@user_settings_bp.route('/api/users/settings/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreference(user_id=user_id)
        db.session.add(preferences)
    
    # Update preferences
    if 'theme' in data:
        preferences.theme = data['theme']
    if 'language' in data:
        preferences.language = data['language']
    if 'notifications_enabled' in data:
        preferences.notifications_enabled = data['notifications_enabled']
    if 'email_notifications' in data:
        preferences.email_notifications = data['email_notifications']
    
    db.session.commit()
    
    return jsonify({'message': 'Preferences updated successfully'})
