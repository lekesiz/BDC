"""Push notification API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.push_notification_service import PushNotificationService
from app.models.push_notification import PushNotificationDevice, PushNotificationLog
from app.models.user import User
from app.extensions import db
from app.middleware.i18n_middleware import i18n_response
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

push_notifications_bp = Blueprint('push_notifications', __name__, url_prefix='/api/push-notifications')


@push_notifications_bp.route('/register', methods=['POST'])
@jwt_required()
@i18n_response
def register_device():
    """Register a device for push notifications."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['device_token', 'device_type', 'provider']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': 'invalid_request',
                    'message': f'{field} is required'
                }), 400
        
        # Validate device type
        valid_device_types = ['ios', 'android', 'web']
        if data['device_type'] not in valid_device_types:
            return jsonify({
                'error': 'invalid_device_type',
                'message': f'Device type must be one of: {", ".join(valid_device_types)}'
            }), 400
        
        # Validate provider
        valid_providers = ['fcm', 'apns', 'webpush']
        if data['provider'] not in valid_providers:
            return jsonify({
                'error': 'invalid_provider',
                'message': f'Provider must be one of: {", ".join(valid_providers)}'
            }), 400
        
        # Register device
        push_service = PushNotificationService()
        device = push_service.register_device(
            user_id=user_id,
            token=data['device_token'],
            device_type=data['device_type'],
            provider=data['provider'],
            device_name=data.get('device_name'),
            device_model=data.get('device_model'),
            device_os=data.get('device_os'),
            app_version=data.get('app_version'),
            provider_data=data.get('provider_data')
        )
        
        return jsonify({
            'success': True,
            'device': device.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Device registration error: {str(e)}")
        return jsonify({
            'error': 'registration_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/unregister', methods=['POST'])
@jwt_required()
@i18n_response
def unregister_device():
    """Unregister a device from push notifications."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        device_token = data.get('device_token')
        if not device_token:
            return jsonify({
                'error': 'invalid_request',
                'message': 'device_token is required'
            }), 400
        
        push_service = PushNotificationService()
        success = push_service.unregister_device(user_id, device_token)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Device unregistered successfully'
            }), 200
        else:
            return jsonify({
                'error': 'device_not_found',
                'message': 'Device not found or already unregistered'
            }), 404
            
    except Exception as e:
        logger.error(f"Device unregistration error: {str(e)}")
        return jsonify({
            'error': 'unregistration_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/devices', methods=['GET'])
@jwt_required()
@i18n_response
def get_user_devices():
    """Get all registered devices for the current user."""
    try:
        user_id = get_jwt_identity()
        
        push_service = PushNotificationService()
        devices = push_service.get_user_devices(user_id)
        
        return jsonify({
            'success': True,
            'devices': devices
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching devices: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/send', methods=['POST'])
@jwt_required()
@i18n_response
def send_notification():
    """Send a notification (admin only)."""
    try:
        admin_id = get_jwt_identity()
        admin = User.query.get(admin_id)
        
        # Check if user is admin
        if not admin or admin.role not in ['super_admin', 'tenant_admin']:
            return jsonify({
                'error': 'unauthorized',
                'message': 'Admin access required'
            }), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('body'):
            return jsonify({
                'error': 'invalid_request',
                'message': 'title and body are required'
            }), 400
        
        push_service = PushNotificationService()
        
        # Send to specific user
        if data.get('user_id'):
            result = push_service.send_to_user(
                user_id=data['user_id'],
                title=data['title'],
                body=data['body'],
                data=data.get('data'),
                notification_type=data.get('notification_type'),
                priority=data.get('priority', 'normal')
            )
            
        # Send to multiple users
        elif data.get('user_ids'):
            result = push_service.send_to_users(
                user_ids=data['user_ids'],
                title=data['title'],
                body=data['body'],
                data=data.get('data'),
                notification_type=data.get('notification_type'),
                priority=data.get('priority', 'normal')
            )
            
        # Send to topic
        elif data.get('topic'):
            result = push_service.send_to_topic(
                topic=data['topic'],
                title=data['title'],
                body=data['body'],
                data=data.get('data'),
                notification_type=data.get('notification_type'),
                priority=data.get('priority', 'normal')
            )
            
        else:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Must specify user_id, user_ids, or topic'
            }), 400
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Notification send error: {str(e)}")
        return jsonify({
            'error': 'send_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/test', methods=['POST'])
@jwt_required()
@i18n_response
def test_notification():
    """Send a test notification to current user's devices."""
    try:
        user_id = get_jwt_identity()
        
        push_service = PushNotificationService()
        result = push_service.send_to_user(
            user_id=user_id,
            title='Test Notification',
            body='This is a test notification from BDC',
            data={'test': True, 'timestamp': datetime.utcnow().isoformat()},
            notification_type='test'
        )
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Test notification error: {str(e)}")
        return jsonify({
            'error': 'test_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/history', methods=['GET'])
@jwt_required()
@i18n_response
def get_notification_history():
    """Get notification history for current user."""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        
        push_service = PushNotificationService()
        notifications = push_service.get_notification_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'notifications': notifications
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching notification history: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/statistics', methods=['GET'])
@jwt_required()
@i18n_response
def get_notification_statistics():
    """Get notification statistics (admin only)."""
    try:
        admin_id = get_jwt_identity()
        admin = User.query.get(admin_id)
        
        # Check if user is admin
        if not admin or admin.role not in ['super_admin', 'tenant_admin']:
            return jsonify({
                'error': 'unauthorized',
                'message': 'Admin access required'
            }), 403
        
        # Get statistics
        from sqlalchemy import func
        from datetime import timedelta
        
        # Total devices
        total_devices = PushNotificationDevice.query.count()
        active_devices = PushNotificationDevice.query.filter_by(is_active=True).count()
        
        # Device breakdown
        device_stats = db.session.query(
            PushNotificationDevice.device_type,
            func.count(PushNotificationDevice.id).label('count')
        ).group_by(PushNotificationDevice.device_type).all()
        
        # Provider breakdown
        provider_stats = db.session.query(
            PushNotificationDevice.provider,
            func.count(PushNotificationDevice.id).label('count')
        ).group_by(PushNotificationDevice.provider).all()
        
        # Recent notifications
        days = request.args.get('days', 7, type=int)
        since = datetime.utcnow() - timedelta(days=days)
        
        notification_stats = db.session.query(
            func.count(PushNotificationLog.id).label('total'),
            func.sum(func.case([(PushNotificationLog.status == 'sent', 1)], else_=0)).label('sent'),
            func.sum(func.case([(PushNotificationLog.status == 'delivered', 1)], else_=0)).label('delivered'),
            func.sum(func.case([(PushNotificationLog.status == 'failed', 1)], else_=0)).label('failed')
        ).filter(PushNotificationLog.created_at >= since).first()
        
        return jsonify({
            'success': True,
            'statistics': {
                'devices': {
                    'total': total_devices,
                    'active': active_devices,
                    'inactive': total_devices - active_devices,
                    'by_type': {stat.device_type: stat.count for stat in device_stats},
                    'by_provider': {stat.provider: stat.count for stat in provider_stats}
                },
                'notifications': {
                    'period_days': days,
                    'total': notification_stats.total or 0,
                    'sent': notification_stats.sent or 0,
                    'delivered': notification_stats.delivered or 0,
                    'failed': notification_stats.failed or 0,
                    'delivery_rate': (notification_stats.delivered / notification_stats.sent * 100) if notification_stats.sent else 0
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching notification statistics: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/settings', methods=['GET'])
@jwt_required()
@i18n_response
def get_notification_settings():
    """Get notification settings for current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get user's notification preferences
        preferences = user.preferences
        notification_settings = preferences.get('notifications', {}) if preferences else {}
        
        # Get registered devices
        devices = PushNotificationDevice.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'settings': {
                'enabled': notification_settings.get('enabled', True),
                'types': notification_settings.get('types', {
                    'message': True,
                    'appointment': True,
                    'test_result': True,
                    'system': True
                }),
                'quiet_hours': notification_settings.get('quiet_hours', {
                    'enabled': False,
                    'start': '22:00',
                    'end': '08:00'
                }),
                'devices_count': len(devices)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching notification settings: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@push_notifications_bp.route('/settings', methods=['PUT'])
@jwt_required()
@i18n_response
def update_notification_settings():
    """Update notification settings for current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        # Update preferences
        if not user.preferences:
            user.preferences = {}
        
        if 'notifications' not in user.preferences:
            user.preferences['notifications'] = {}
        
        # Update settings
        if 'enabled' in data:
            user.preferences['notifications']['enabled'] = data['enabled']
        
        if 'types' in data:
            user.preferences['notifications']['types'] = data['types']
        
        if 'quiet_hours' in data:
            user.preferences['notifications']['quiet_hours'] = data['quiet_hours']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification settings updated'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        return jsonify({
            'error': 'update_failed',
            'message': str(e)
        }), 500