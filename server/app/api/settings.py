"""Settings API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.tenant import Tenant

from app.utils.logging import logger

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings/general', methods=['GET'])
@jwt_required()
def get_general_settings():
    """Get general settings for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's tenant settings if applicable
    tenant_settings = {}
    if hasattr(user, 'tenants') and user.tenants:
        tenant = user.tenants[0]  # Assuming user belongs to first tenant
        tenant_settings = {
            'tenant_name': tenant.name,
            'tenant_id': tenant.id,
            'tenant_logo': getattr(tenant, 'logo_url', None),
            'tenant_email': tenant.email
        }
    
    # User preferences
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    settings = {
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'phone': getattr(user, 'phone', None),
            'timezone': getattr(preferences, 'timezone', 'UTC') if preferences else 'UTC'
        },
        'tenant': tenant_settings,
        'system': {
            'version': '1.0.0',
            'features': {
                'evaluations': True,
                'appointments': True,
                'documents': True,
                'analytics': True,
                'reports': True,
                'notifications': True
            }
        }
    }
    
    return jsonify(settings), 200


@settings_bp.route('/settings/general', methods=['PUT'])
@jwt_required()
def update_general_settings():
    """Update general settings for the current user."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update user information
    if 'user' in data:
        user_data = data['user']
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'phone' in user_data and hasattr(user, 'phone'):
            user.phone = user_data['phone']
    
    # Update preferences
    if 'preferences' in data:
        preferences = UserPreference.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = UserPreference(user_id=user_id)
            db.session.add(preferences)
        
        pref_data = data['preferences']
        if 'timezone' in pref_data:
            preferences.timezone = pref_data['timezone']
    
    db.session.commit()
    
    return jsonify({'message': 'Settings updated successfully'}), 200


@settings_bp.route('/settings/appearance', methods=['GET'])
@jwt_required()
def get_appearance_settings():
    """Get appearance settings for the current user."""
    user_id = get_jwt_identity()
    
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        # Create default preferences
        preferences = UserPreference(
            user_id=user_id,
            theme='light',
            language='en',
            sidebar_collapsed=False,
            density='normal'
        )
        db.session.add(preferences)
        db.session.commit()
    
    settings = {
        'theme': preferences.theme,
        'language': preferences.language,
        'sidebar_collapsed': getattr(preferences, 'sidebar_collapsed', False),
        'density': getattr(preferences, 'density', 'normal'),
        'accent_color': getattr(preferences, 'accent_color', 'blue'),
        'font_size': getattr(preferences, 'font_size', 'medium')
    }
    
    return jsonify(settings), 200


@settings_bp.route('/settings/appearance', methods=['PUT'])
@jwt_required()
def update_appearance_settings():
    """Update appearance settings for the current user."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreference(user_id=user_id)
        db.session.add(preferences)
    
    # Update appearance settings
    if 'theme' in data:
        preferences.theme = data['theme']
    if 'language' in data:
        preferences.language = data['language']
    if 'sidebar_collapsed' in data:
        preferences.sidebar_collapsed = data['sidebar_collapsed']
    if 'density' in data:
        preferences.density = data['density']
    if 'accent_color' in data:
        preferences.accent_color = data['accent_color']
    if 'font_size' in data:
        preferences.font_size = data['font_size']
    
    db.session.commit()
    
    return jsonify({'message': 'Appearance settings updated successfully'}), 200


@settings_bp.route('/settings/notifications', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Get notification settings for the current user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    settings = {
        'email_notifications': getattr(user, 'email_notifications', True),
        'push_notifications': getattr(user, 'push_notifications', False),
        'sms_notifications': getattr(user, 'sms_notifications', False),
        'notification_preferences': {
            'new_evaluations': True,
            'appointment_reminders': True,
            'messages': True,
            'system_alerts': True,
            'status_updates': True
        }
    }
    
    return jsonify(settings), 200


@settings_bp.route('/settings/notifications', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Update notification settings for the current user."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update notification settings
    if 'email_notifications' in data:
        user.email_notifications = data['email_notifications']
    if 'push_notifications' in data:
        user.push_notifications = data['push_notifications']
    if 'sms_notifications' in data:
        user.sms_notifications = data['sms_notifications']
    
    db.session.commit()
    
    return jsonify({'message': 'Notification settings updated successfully'}), 200


@settings_bp.route('/settings/privacy', methods=['GET'])
@jwt_required()
def get_privacy_settings():
    """Get privacy settings for the current user."""
    user_id = get_jwt_identity()
    
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        # Create default preferences
        preferences = UserPreference(
            user_id=user_id,
            profile_visibility='all',
            show_online_status=True,
            share_activity=True,
            allow_data_collection=True
        )
        db.session.add(preferences)
        db.session.commit()
    
    settings = {
        'profile_visibility': getattr(preferences, 'profile_visibility', 'all'),
        'show_online_status': getattr(preferences, 'show_online_status', True),
        'share_activity': getattr(preferences, 'share_activity', True),
        'allow_data_collection': getattr(preferences, 'allow_data_collection', True),
        'blocked_users': getattr(preferences, 'blocked_users', []) if hasattr(preferences, 'blocked_users') else []
    }
    
    return jsonify(settings), 200


@settings_bp.route('/settings/privacy', methods=['PUT'])
@jwt_required()
def update_privacy_settings():
    """Update privacy settings for the current user."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreference(user_id=user_id)
        db.session.add(preferences)
    
    # Update privacy settings
    if 'profile_visibility' in data:
        preferences.profile_visibility = data['profile_visibility']
    if 'show_online_status' in data:
        preferences.show_online_status = data['show_online_status']
    if 'share_activity' in data:
        preferences.share_activity = data['share_activity']  
    if 'allow_data_collection' in data:
        preferences.allow_data_collection = data['allow_data_collection']
    
    db.session.commit()
    
    return jsonify({'message': 'Privacy settings updated successfully'}), 200