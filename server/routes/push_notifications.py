"""
Push Notification API Routes for BDC PWA
Handles subscription management and notification sending
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

from services.push_notification_service import (
    PushNotificationService, 
    NotificationTemplates,
    create_push_service
)
from models.user import User
from models.notification import Notification
from app.extensions import db
from utils.decorators import roles_required
from utils.validation import validate_json

logger = logging.getLogger(__name__)

# Create blueprint
push_bp = Blueprint('push_notifications', __name__, url_prefix='/api/push')

# Initialize push service (this would be done in app factory)
push_service = None

def init_push_service(app):
    """Initialize push notification service with app config"""
    global push_service
    push_service = create_push_service(app.config)


@push_bp.route('/vapid-public-key', methods=['GET'])
def get_vapid_public_key():
    """Get VAPID public key for client-side subscription"""
    try:
        public_key = current_app.config.get('VAPID_PUBLIC_KEY')
        if not public_key:
            return jsonify({
                'error': 'VAPID public key not configured'
            }), 500
        
        return jsonify({
            'public_key': public_key
        })
        
    except Exception as e:
        logger.error(f"Failed to get VAPID public key: {str(e)}")
        return jsonify({
            'error': 'Failed to get public key'
        }), 500


@push_bp.route('/subscribe', methods=['POST'])
@jwt_required()
@validate_json(['endpoint', 'keys'])
def subscribe_to_push():
    """Subscribe user to push notifications"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate subscription data
        subscription_data = {
            'endpoint': data['endpoint'],
            'keys': data['keys']
        }
        
        # Validate keys format
        if not isinstance(subscription_data['keys'], dict):
            return jsonify({
                'error': 'Invalid keys format'
            }), 400
        
        required_keys = ['p256dh', 'auth']
        if not all(key in subscription_data['keys'] for key in required_keys):
            return jsonify({
                'error': 'Missing required keys'
            }), 400
        
        # Subscribe user
        success = push_service.subscribe_user(user_id, subscription_data)
        
        if success:
            return jsonify({
                'message': 'Successfully subscribed to push notifications',
                'subscribed': True
            })
        else:
            return jsonify({
                'error': 'Failed to subscribe to push notifications'
            }), 500
            
    except Exception as e:
        logger.error(f"Push subscription failed: {str(e)}")
        return jsonify({
            'error': 'Subscription failed'
        }), 500


@push_bp.route('/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribe_from_push():
    """Unsubscribe user from push notifications"""
    try:
        user_id = get_jwt_identity()
        
        success = push_service.unsubscribe_user(user_id)
        
        if success:
            return jsonify({
                'message': 'Successfully unsubscribed from push notifications',
                'subscribed': False
            })
        else:
            return jsonify({
                'error': 'Failed to unsubscribe from push notifications'
            }), 500
            
    except Exception as e:
        logger.error(f"Push unsubscription failed: {str(e)}")
        return jsonify({
            'error': 'Unsubscription failed'
        }), 500


@push_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Get user's push notification subscription status"""
    try:
        user_id = get_jwt_identity()
        subscription = push_service.get_user_subscription(user_id)
        
        if subscription:
            return jsonify({
                'subscribed': subscription.get('active', False),
                'subscription_date': subscription.get('subscribed_at'),
                'endpoint': subscription.get('endpoint', '').split('/')[-1][:20] + '...'  # Partial endpoint for privacy
            })
        else:
            return jsonify({
                'subscribed': False
            })
            
    except Exception as e:
        logger.error(f"Failed to get subscription status: {str(e)}")
        return jsonify({
            'error': 'Failed to get subscription status'
        }), 500


@push_bp.route('/test', methods=['POST'])
@jwt_required()
def send_test_notification():
    """Send a test push notification to the current user"""
    try:
        user_id = get_jwt_identity()
        
        success = push_service.send_notification(
            user_id=user_id,
            title='Test Notification',
            body='This is a test notification from BDC',
            data={
                'type': 'test',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        if success:
            return jsonify({
                'message': 'Test notification sent successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to send test notification'
            }), 500
            
    except Exception as e:
        logger.error(f"Test notification failed: {str(e)}")
        return jsonify({
            'error': 'Test notification failed'
        }), 500


@push_bp.route('/send', methods=['POST'])
@jwt_required()
@roles_required(['admin', 'trainer'])
@validate_json(['title', 'body'])
def send_notification():
    """Send push notification to specific users or roles"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        title = data['title']
        body = data['body']
        notification_data = data.get('data', {})
        options = data.get('options', {})
        
        # Determine recipients
        if 'user_ids' in data:
            # Send to specific users
            user_ids = data['user_ids']
            if not isinstance(user_ids, list):
                return jsonify({'error': 'user_ids must be a list'}), 400
            
            results = push_service.send_bulk_notification(
                user_ids, title, body, notification_data, options
            )
            
        elif 'role' in data:
            # Send to users with specific role
            role = data['role']
            results = push_service.send_notification_by_role(
                role, title, body, notification_data, options
            )
            
        else:
            return jsonify({
                'error': 'Must specify either user_ids or role'
            }), 400
        
        return jsonify({
            'message': 'Notifications sent',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Failed to send notifications: {str(e)}")
        return jsonify({
            'error': 'Failed to send notifications'
        }), 500


@push_bp.route('/templates', methods=['GET'])
@jwt_required()
@roles_required(['admin', 'trainer'])
def get_notification_templates():
    """Get available notification templates"""
    try:
        templates = {
            'evaluation_available': {
                'name': 'Evaluation Available',
                'description': 'Notify when a new evaluation is available',
                'parameters': ['beneficiary_name', 'evaluation_title']
            },
            'appointment_reminder': {
                'name': 'Appointment Reminder',
                'description': 'Remind about upcoming appointments',
                'parameters': ['appointment_time', 'participant_name']
            },
            'message_received': {
                'name': 'Message Received',
                'description': 'Notify about new messages',
                'parameters': ['sender_name', 'message_preview']
            },
            'system_update': {
                'name': 'System Update',
                'description': 'Notify about app updates',
                'parameters': ['version', 'features']
            },
            'document_shared': {
                'name': 'Document Shared',
                'description': 'Notify when documents are shared',
                'parameters': ['document_name', 'shared_by']
            }
        }
        
        return jsonify({
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Failed to get templates: {str(e)}")
        return jsonify({
            'error': 'Failed to get templates'
        }), 500


@push_bp.route('/send-template', methods=['POST'])
@jwt_required()
@roles_required(['admin', 'trainer'])
@validate_json(['template', 'parameters'])
def send_template_notification():
    """Send notification using a predefined template"""
    try:
        data = request.get_json()
        template_name = data['template']
        parameters = data['parameters']
        recipients = data.get('recipients', {})
        
        # Get template function
        template_func = getattr(NotificationTemplates, template_name, None)
        if not template_func:
            return jsonify({
                'error': f'Template {template_name} not found'
            }), 400
        
        # Generate notification content
        notification_content = template_func(**parameters)
        
        # Send notification
        if 'user_ids' in recipients:
            results = push_service.send_bulk_notification(
                recipients['user_ids'],
                notification_content['title'],
                notification_content['body'],
                notification_content['data']
            )
        elif 'role' in recipients:
            results = push_service.send_notification_by_role(
                recipients['role'],
                notification_content['title'],
                notification_content['body'],
                notification_content['data']
            )
        else:
            return jsonify({
                'error': 'Must specify recipients'
            }), 400
        
        return jsonify({
            'message': 'Template notification sent',
            'template': template_name,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Template notification failed: {str(e)}")
        return jsonify({
            'error': 'Template notification failed'
        }), 500


@push_bp.route('/stats', methods=['GET'])
@jwt_required()
@roles_required(['admin'])
def get_notification_stats():
    """Get push notification statistics"""
    try:
        stats = push_service.get_subscription_stats()
        
        # Additional stats from database
        recent_notifications = Notification.query.filter(
            Notification.type == 'push',
            Notification.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        stats['notifications_today'] = recent_notifications
        
        return jsonify({
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        return jsonify({
            'error': 'Failed to get statistics'
        }), 500


@push_bp.route('/preferences', methods=['GET', 'POST'])
@jwt_required()
def notification_preferences():
    """Get or update user's notification preferences"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            # Get current preferences
            preferences = getattr(user, 'notification_preferences', {})
            default_preferences = {
                'evaluations': True,
                'appointments': True,
                'messages': True,
                'updates': False,
                'reminders': True
            }
            
            # Merge with defaults
            merged_preferences = {**default_preferences, **preferences}
            
            return jsonify({
                'preferences': merged_preferences
            })
        
        elif request.method == 'POST':
            # Update preferences
            data = request.get_json()
            
            if not isinstance(data.get('preferences'), dict):
                return jsonify({'error': 'Invalid preferences format'}), 400
            
            # Update user preferences
            setattr(user, 'notification_preferences', data['preferences'])
            db.session.commit()
            
            return jsonify({
                'message': 'Preferences updated successfully',
                'preferences': data['preferences']
            })
            
    except Exception as e:
        logger.error(f"Notification preferences failed: {str(e)}")
        return jsonify({
            'error': 'Failed to handle preferences'
        }), 500


# Error handlers
@push_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': str(error)
    }), 400


@push_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@push_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden',
        'message': 'Insufficient permissions'
    }), 403


@push_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in push notifications: {str(error)}")
    return jsonify({
        'error': 'Internal server error'
    }), 500