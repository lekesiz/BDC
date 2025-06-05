"""Appearance settings API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.settings import AppearanceSettings
from app.schemas.settings import AppearanceSettingsSchema, AppearanceSettingsUpdateSchema

settings_appearance_bp = Blueprint('settings_appearance', __name__)
appearance_settings_schema = AppearanceSettingsSchema()
appearance_settings_update_schema = AppearanceSettingsUpdateSchema()


@settings_appearance_bp.route('/settings/appearance', methods=['GET'])
@jwt_required()
def get_appearance_settings():
    """Get appearance settings for current user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Try to get user-specific settings first
    settings = AppearanceSettings.query.filter_by(user_id=current_user_id).first()
    
    # If no user-specific settings, get tenant settings
    if not settings:
        tenant_id = None
        if hasattr(current_user, 'tenant_id'):
            tenant_id = current_user.tenant_id
        elif hasattr(current_user, 'tenants') and current_user.tenants:
            tenant_id = current_user.tenants[0].id
        
        if tenant_id:
            settings = AppearanceSettings.query.filter_by(
                tenant_id=tenant_id,
                user_id=None
            ).first()
    
    # If still no settings, create default tenant settings
    if not settings:
        tenant_id = None
        if hasattr(current_user, 'tenant_id'):
            tenant_id = current_user.tenant_id
        elif hasattr(current_user, 'tenants') and current_user.tenants:
            tenant_id = current_user.tenants[0].id
        
        if tenant_id:
            settings = AppearanceSettings(
                tenant_id=tenant_id,
                theme='light',
                font_family='Inter',
                font_size='medium',
                sidebar_position='left',
                sidebar_collapsed=False,
                compact_mode=False,
                rounded_corners=True,
                show_animations=True,
                animation_speed='normal'
            )
            db.session.add(settings)
            db.session.commit()
    
    if not settings:
        return jsonify({'error': 'Unable to load appearance settings'}), 500
    
    return jsonify(appearance_settings_schema.dump(settings)), 200


@settings_appearance_bp.route('/settings/appearance', methods=['PUT', 'PATCH'])
@jwt_required()
def update_appearance_settings():
    """Update appearance settings for current user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Validate request data
    errors = appearance_settings_update_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Determine if we're updating user or tenant settings
    create_user_settings = request.args.get('user_specific', 'false').lower() == 'true'
    
    if create_user_settings:
        # Update or create user-specific settings
        settings = AppearanceSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            # Create new user-specific settings
            tenant_id = None
            if hasattr(current_user, 'tenant_id'):
                tenant_id = current_user.tenant_id
            elif hasattr(current_user, 'tenants') and current_user.tenants:
                tenant_id = current_user.tenants[0].id
            
            settings = AppearanceSettings(
                tenant_id=tenant_id,
                user_id=current_user_id
            )
            db.session.add(settings)
    else:
        # Update tenant settings (admin only)
        if current_user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({'error': 'Unauthorized to update tenant appearance settings'}), 403
        
        tenant_id = None
        if hasattr(current_user, 'tenant_id'):
            tenant_id = current_user.tenant_id
        elif hasattr(current_user, 'tenants') and current_user.tenants:
            tenant_id = current_user.tenants[0].id
        
        if not tenant_id:
            return jsonify({'error': 'No tenant associated with user'}), 400
        
        settings = AppearanceSettings.query.filter_by(
            tenant_id=tenant_id,
            user_id=None
        ).first()
        
        if not settings:
            return jsonify({'error': 'Tenant appearance settings not found'}), 404
    
    # Update settings
    for key, value in request.json.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    try:
        db.session.commit()
        return jsonify(appearance_settings_schema.dump(settings)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update appearance settings'}), 500


@settings_appearance_bp.route('/settings/appearance/themes', methods=['GET'])
@jwt_required()
def get_available_themes():
    """Get list of available themes."""
    themes = [
        {
            'id': 'light',
            'name': 'Light',
            'description': 'Default light theme',
            'preview': {
                'primary': '#3B82F6',
                'secondary': '#1E40AF',
                'background': '#FFFFFF',
                'surface': '#F9FAFB',
                'text': '#111827'
            }
        },
        {
            'id': 'dark',
            'name': 'Dark',
            'description': 'Dark theme for low-light environments',
            'preview': {
                'primary': '#3B82F6',
                'secondary': '#1E40AF',
                'background': '#111827',
                'surface': '#1F2937',
                'text': '#F9FAFB'
            }
        },
        {
            'id': 'auto',
            'name': 'Auto',
            'description': 'Automatically switch based on system preference',
            'preview': None
        }
    ]
    return jsonify(themes), 200


@settings_appearance_bp.route('/settings/appearance/fonts', methods=['GET'])
@jwt_required()
def get_available_fonts():
    """Get list of available fonts."""
    fonts = [
        {'id': 'Inter', 'name': 'Inter', 'category': 'Sans-serif'},
        {'id': 'Roboto', 'name': 'Roboto', 'category': 'Sans-serif'},
        {'id': 'Open Sans', 'name': 'Open Sans', 'category': 'Sans-serif'},
        {'id': 'Lato', 'name': 'Lato', 'category': 'Sans-serif'},
        {'id': 'Montserrat', 'name': 'Montserrat', 'category': 'Sans-serif'},
        {'id': 'Poppins', 'name': 'Poppins', 'category': 'Sans-serif'},
        {'id': 'Source Sans Pro', 'name': 'Source Sans Pro', 'category': 'Sans-serif'},
        {'id': 'Playfair Display', 'name': 'Playfair Display', 'category': 'Serif'},
        {'id': 'Merriweather', 'name': 'Merriweather', 'category': 'Serif'},
        {'id': 'Georgia', 'name': 'Georgia', 'category': 'Serif'}
    ]
    return jsonify(fonts), 200


@settings_appearance_bp.route('/settings/appearance/preview', methods=['POST'])
@jwt_required()
def preview_appearance_settings():
    """Preview appearance settings without saving."""
    if not request.json:
        return jsonify({'error': 'Request body is required'}), 400
    
    # Validate the preview data
    errors = appearance_settings_update_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Return the preview data with a preview flag
    preview_data = request.json.copy()
    preview_data['is_preview'] = True
    preview_data['preview_timestamp'] = datetime.utcnow().isoformat()
    
    return jsonify(preview_data), 200


@settings_appearance_bp.route('/settings/appearance/reset', methods=['POST'])
@jwt_required()
def reset_appearance_settings():
    """Reset appearance settings to defaults."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Determine if resetting user or tenant settings
    reset_user_settings = request.args.get('user_specific', 'false').lower() == 'true'
    
    if reset_user_settings:
        # Delete user-specific settings
        AppearanceSettings.query.filter_by(user_id=current_user_id).delete()
        db.session.commit()
        
        # Return tenant defaults
        return get_appearance_settings()
    else:
        # Reset tenant settings (admin only)
        if current_user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({'error': 'Unauthorized to reset tenant appearance settings'}), 403
        
        tenant_id = None
        if hasattr(current_user, 'tenant_id'):
            tenant_id = current_user.tenant_id
        elif hasattr(current_user, 'tenants') and current_user.tenants:
            tenant_id = current_user.tenants[0].id
        
        if not tenant_id:
            return jsonify({'error': 'No tenant associated with user'}), 400
        
        settings = AppearanceSettings.query.filter_by(
            tenant_id=tenant_id,
            user_id=None
        ).first()
        
        if not settings:
            return jsonify({'error': 'Tenant appearance settings not found'}), 404
        
        # Reset to defaults
        settings.theme = 'light'
        settings.font_family = 'Inter'
        settings.font_size = 'medium'
        settings.sidebar_position = 'left'
        settings.sidebar_collapsed = False
        settings.compact_mode = False
        settings.accent_color = None
        settings.background_color = None
        settings.text_color = None
        settings.rounded_corners = True
        settings.show_animations = True
        settings.animation_speed = 'normal'
        
        try:
            db.session.commit()
            return jsonify({
                'message': 'Appearance settings reset to defaults',
                'settings': appearance_settings_schema.dump(settings)
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to reset appearance settings'}), 500


@settings_appearance_bp.route('/settings/appearance/export', methods=['GET'])
@jwt_required()
def export_appearance_settings():
    """Export appearance settings as JSON."""
    current_user_id = get_jwt_identity()
    
    # Get user settings
    user_settings = AppearanceSettings.query.filter_by(user_id=current_user_id).first()
    
    # Get tenant settings
    current_user = User.query.get(current_user_id)
    tenant_settings = None
    
    if current_user:
        tenant_id = None
        if hasattr(current_user, 'tenant_id'):
            tenant_id = current_user.tenant_id
        elif hasattr(current_user, 'tenants') and current_user.tenants:
            tenant_id = current_user.tenants[0].id
        
        if tenant_id:
            tenant_settings = AppearanceSettings.query.filter_by(
                tenant_id=tenant_id,
                user_id=None
            ).first()
    
    export_data = {
        'exported_at': datetime.utcnow().isoformat(),
        'user_settings': appearance_settings_schema.dump(user_settings) if user_settings else None,
        'tenant_settings': appearance_settings_schema.dump(tenant_settings) if tenant_settings else None,
        'active_settings': appearance_settings_schema.dump(user_settings or tenant_settings)
    }
    
    return jsonify(export_data), 200


from datetime import datetime  # Add this import at the top

from app.utils.logging import logger