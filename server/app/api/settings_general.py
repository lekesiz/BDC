"""General settings API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.settings import GeneralSettings
from app.schemas.settings import GeneralSettingsSchema, GeneralSettingsUpdateSchema

from app.utils.logging import logger

settings_general_bp = Blueprint('settings_general', __name__)
general_settings_schema = GeneralSettingsSchema()
general_settings_update_schema = GeneralSettingsUpdateSchema()


@settings_general_bp.route('/settings/general', methods=['GET'])
@jwt_required()
def get_general_settings():
    """Get general settings for current user's tenant."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get tenant ID based on user role
    tenant_id = None
    if hasattr(current_user, 'tenant_id'):
        tenant_id = current_user.tenant_id
    elif hasattr(current_user, 'tenants') and current_user.tenants:
        tenant_id = current_user.tenants[0].id
    
    if not tenant_id:
        return jsonify({'error': 'No tenant associated with user'}), 400
    
    # Get or create general settings for tenant
    settings = GeneralSettings.query.filter_by(tenant_id=tenant_id).first()
    if not settings:
        # Create default settings
        settings = GeneralSettings(
            tenant_id=tenant_id,
            site_name='Beneficiary Development Center',
            site_logo=None,
            primary_color='#3B82F6',
            secondary_color='#1E40AF',
            enable_notifications=True,
            enable_email_notifications=True,
            enable_sms_notifications=False,
            default_language='en',
            timezone='UTC',
            date_format='MM/DD/YYYY',
            time_format='12h',
            week_starts_on='sunday',
            working_hours_start='09:00',
            working_hours_end='17:00',
            max_file_upload_size=10485760,  # 10MB in bytes
            allowed_file_types=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg']
        )
        db.session.add(settings)
        db.session.commit()
    
    return jsonify(general_settings_schema.dump(settings)), 200


@settings_general_bp.route('/settings/general', methods=['PUT', 'PATCH'])
@jwt_required()
def update_general_settings():
    """Update general settings for current user's tenant."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions - only admins can update settings
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized to update settings'}), 403
    
    # Get tenant ID
    tenant_id = None
    if hasattr(current_user, 'tenant_id'):
        tenant_id = current_user.tenant_id
    elif hasattr(current_user, 'tenants') and current_user.tenants:
        tenant_id = current_user.tenants[0].id
    
    if not tenant_id:
        return jsonify({'error': 'No tenant associated with user'}), 400
    
    # Validate request data
    errors = general_settings_update_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Get existing settings
    settings = GeneralSettings.query.filter_by(tenant_id=tenant_id).first()
    if not settings:
        return jsonify({'error': 'Settings not found'}), 404
    
    # Update settings
    for key, value in request.json.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    try:
        db.session.commit()
        return jsonify(general_settings_schema.dump(settings)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update settings'}), 500


@settings_general_bp.route('/settings/general/languages', methods=['GET'])
@jwt_required()
def get_available_languages():
    """Get list of available languages."""
    languages = [
        {'code': 'en', 'name': 'English', 'native_name': 'English'},
        {'code': 'fr', 'name': 'French', 'native_name': 'Français'},
        {'code': 'es', 'name': 'Spanish', 'native_name': 'Español'},
        {'code': 'de', 'name': 'German', 'native_name': 'Deutsch'},
        {'code': 'it', 'name': 'Italian', 'native_name': 'Italiano'},
        {'code': 'pt', 'name': 'Portuguese', 'native_name': 'Português'},
        {'code': 'tr', 'name': 'Turkish', 'native_name': 'Türkçe'},
        {'code': 'ar', 'name': 'Arabic', 'native_name': 'العربية'},
        {'code': 'zh', 'name': 'Chinese', 'native_name': '中文'},
        {'code': 'ja', 'name': 'Japanese', 'native_name': '日本語'}
    ]
    return jsonify(languages), 200


@settings_general_bp.route('/settings/general/timezones', methods=['GET'])
@jwt_required()
def get_available_timezones():
    """Get list of available timezones."""
    timezones = [
        {'value': 'UTC', 'label': 'UTC (Coordinated Universal Time)'},
        {'value': 'America/New_York', 'label': 'Eastern Time (US & Canada)'},
        {'value': 'America/Chicago', 'label': 'Central Time (US & Canada)'},
        {'value': 'America/Denver', 'label': 'Mountain Time (US & Canada)'},
        {'value': 'America/Los_Angeles', 'label': 'Pacific Time (US & Canada)'},
        {'value': 'Europe/London', 'label': 'London'},
        {'value': 'Europe/Paris', 'label': 'Paris'},
        {'value': 'Europe/Berlin', 'label': 'Berlin'},
        {'value': 'Europe/Istanbul', 'label': 'Istanbul'},
        {'value': 'Asia/Dubai', 'label': 'Dubai'},
        {'value': 'Asia/Shanghai', 'label': 'Shanghai'},
        {'value': 'Asia/Tokyo', 'label': 'Tokyo'},
        {'value': 'Australia/Sydney', 'label': 'Sydney'}
    ]
    return jsonify(timezones), 200


@settings_general_bp.route('/settings/general/date-formats', methods=['GET'])
@jwt_required()
def get_date_formats():
    """Get list of available date formats."""
    formats = [
        {'value': 'MM/DD/YYYY', 'example': '03/14/2024'},
        {'value': 'DD/MM/YYYY', 'example': '14/03/2024'},
        {'value': 'YYYY-MM-DD', 'example': '2024-03-14'},
        {'value': 'DD.MM.YYYY', 'example': '14.03.2024'},
        {'value': 'MMM DD, YYYY', 'example': 'Mar 14, 2024'},
        {'value': 'DD MMM YYYY', 'example': '14 Mar 2024'}
    ]
    return jsonify(formats), 200


@settings_general_bp.route('/settings/general/logo', methods=['POST'])
@jwt_required()
def upload_logo():
    """Upload site logo."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized to upload logo'}), 403
    
    if 'logo' not in request.files:
        return jsonify({'error': 'No logo file provided'}), 400
    
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    if not file.filename.lower().split('.')[-1] in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, svg'}), 400
    
    # TODO: Implement actual file upload logic
    # For now, just return a placeholder response
    return jsonify({
        'logo_url': f'/uploads/logos/{file.filename}',
        'message': 'Logo uploaded successfully'
    }), 200


@settings_general_bp.route('/settings/general/reset', methods=['POST'])
@jwt_required()
def reset_to_defaults():
    """Reset general settings to defaults."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'error': 'Unauthorized to reset settings'}), 403
    
    # Get tenant ID
    tenant_id = None
    if hasattr(current_user, 'tenant_id'):
        tenant_id = current_user.tenant_id
    elif hasattr(current_user, 'tenants') and current_user.tenants:
        tenant_id = current_user.tenants[0].id
    
    if not tenant_id:
        return jsonify({'error': 'No tenant associated with user'}), 400
    
    # Get existing settings
    settings = GeneralSettings.query.filter_by(tenant_id=tenant_id).first()
    if not settings:
        return jsonify({'error': 'Settings not found'}), 404
    
    # Reset to defaults
    settings.site_name = 'Beneficiary Development Center'
    settings.site_logo = None
    settings.primary_color = '#3B82F6'
    settings.secondary_color = '#1E40AF'
    settings.enable_notifications = True
    settings.enable_email_notifications = True
    settings.enable_sms_notifications = False
    settings.default_language = 'en'
    settings.timezone = 'UTC'
    settings.date_format = 'MM/DD/YYYY'
    settings.time_format = '12h'
    settings.week_starts_on = 'sunday'
    settings.working_hours_start = '09:00'
    settings.working_hours_end = '17:00'
    settings.max_file_upload_size = 10485760
    settings.allowed_file_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Settings reset to defaults',
            'settings': general_settings_schema.dump(settings)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset settings'}), 500