"""Fixed Notification API endpoints with proper dependency injection."""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.container import get_container

from app.utils.logging import logger

notifications_bp = Blueprint('notifications', __name__)


def get_notification_service():
    """Get notification service instance from DI container."""
    if not hasattr(g, '_notification_service'):
        container = get_container()
        g._notification_service = container.resolve('notification_service')
    return g._notification_service


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get all notifications for the current user."""
    user_id = get_jwt_identity()
    
    # Parse query parameters
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    notification_type = request.args.get('type')
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Get notifications
    notifications = notification_service.get_user_notifications(
        user_id=user_id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
        type=notification_type
    )
    
    # Get unread count
    unread_count = notification_service.get_unread_count(user_id)
    
    return jsonify({
        'notifications': notifications,
        'unread_count': unread_count,
        'limit': limit,
        'offset': offset,
        'total': len(notifications)  # This is not accurate for total count, just current batch
    }), 200


@notifications_bp.route('/notifications/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get the count of unread notifications for the current user."""
    user_id = get_jwt_identity()
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Get unread count
    unread_count = notification_service.get_unread_count(user_id)
    
    return jsonify({
        'unread_count': unread_count
    }), 200


@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """Mark a notification as read."""
    user_id = get_jwt_identity()
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Mark notification as read
    success = notification_service.mark_as_read(notification_id, user_id)
    
    if not success:
        return jsonify({
            'error': 'notification_not_found',
            'message': 'Notification not found'
        }), 404
    
    return jsonify({
        'message': 'Notification marked as read'
    }), 200


@notifications_bp.route('/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_as_read():
    """Mark all notifications as read for the current user."""
    user_id = get_jwt_identity()
    
    # Get notification type from request
    notification_type = request.json.get('type') if request.json else None
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Mark all notifications as read
    count = notification_service.mark_all_as_read(user_id, notification_type)
    
    return jsonify({
        'message': f'{count} notifications marked as read'
    }), 200


@notifications_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification."""
    user_id = get_jwt_identity()
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Delete notification
    success = notification_service.delete_notification(notification_id, user_id)
    
    if not success:
        return jsonify({
            'error': 'notification_not_found',
            'message': 'Notification not found'
        }), 404
    
    return jsonify({
        'message': 'Notification deleted'
    }), 200


@notifications_bp.route('/notifications/test', methods=['POST'])
@jwt_required()
def create_test_notification():
    """Create a test notification for the current user (development only)."""
    # Only allow in development
    if current_app.config.get('FLASK_ENV') != 'development':
        return jsonify({
            'error': 'not_allowed',
            'message': 'This endpoint is only available in development mode'
        }), 403
    
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Create notification
    notification = notification_service.create_notification(
        user_id=user_id,
        type='test',
        title='Test Notification',
        message='This is a test notification',
        data={'test_key': 'test_value'},
        related_id=None,
        related_type=None,
        sender_id=None,
        priority='normal',
        send_email=request.json.get('send_email', False) if request.json else False
    )
    
    if not notification:
        return jsonify({
            'error': 'notification_creation_failed',
            'message': 'Failed to create notification'
        }), 500
    
    return jsonify({
        'message': 'Test notification created',
        'notification': notification.to_dict()
    }), 201


@notifications_bp.route('/notifications/send', methods=['POST'])
@jwt_required()
def send_notification():
    """Send a notification to a user or current user."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'invalid_request',
            'message': 'Invalid request data'
        }), 400
    
    # Determine recipient
    recipient_id = data.get('recipient_id', current_user_id)
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Create notification
    notification = notification_service.create_notification(
        user_id=recipient_id,
        type=data.get('type', 'info'),
        title=data.get('title', 'Notification'),
        message=data.get('message', ''),
        data=data.get('data'),
        sender_id=current_user_id,
        priority=data.get('priority', 'normal'),
        send_email=data.get('send_email', False)
    )
    
    if notification:
        return jsonify({
            'message': 'Notification sent successfully',
            'notification': notification.to_dict()
        }), 201
    else:
        return jsonify({
            'error': 'notification_creation_failed',
            'message': 'Failed to create notification'
        }), 500


@notifications_bp.route('/notifications/broadcast', methods=['POST'])
@jwt_required()
def broadcast_notification():
    """Broadcast a notification to all users."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user is an admin
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({
            'error': 'not_authorized',
            'message': 'Not authorized to broadcast notifications'
        }), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'invalid_request',
            'message': 'Invalid request data'
        }), 400
    
    # Get all active users
    users = User.query.filter_by(is_active=True).all()
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Create notifications for all users
    created_count = 0
    for user in users:
        notification = notification_service.create_notification(
            user_id=user.id,
            type=data.get('type', 'info'),
            title=data.get('title', 'Broadcast'),
            message=data.get('message', ''),
            data=data.get('data'),
            sender_id=current_user_id,
            priority=data.get('priority', 'normal'),
            send_email=data.get('send_email', False)
        )
        if notification:
            created_count += 1
    
    return jsonify({
        'message': f'Broadcast sent to {created_count} users',
        'count': created_count
    }), 201


# Admin-only endpoints
@notifications_bp.route('/admin/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a notification for a user (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user is an admin
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({
            'error': 'not_authorized',
            'message': 'Not authorized to create notifications for other users'
        }), 403
    
    # Validate request data
    if not request.json:
        return jsonify({
            'error': 'invalid_request',
            'message': 'Invalid request data'
        }), 400
    
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({
            'error': 'user_id_required',
            'message': 'User ID is required'
        }), 400
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Create notification
    notification = notification_service.create_notification(
        user_id=user_id,
        type=request.json.get('type', 'system'),
        title=request.json.get('title', 'System Notification'),
        message=request.json.get('message', ''),
        data=request.json.get('data'),
        related_id=request.json.get('related_id'),
        related_type=request.json.get('related_type'),
        sender_id=current_user_id,
        priority=request.json.get('priority', 'normal'),
        send_email=request.json.get('send_email', False),
        tenant_id=request.json.get('tenant_id')
    )
    
    if not notification:
        return jsonify({
            'error': 'notification_creation_failed',
            'message': 'Failed to create notification'
        }), 500
    
    return jsonify({
        'message': 'Notification created',
        'notification': notification.to_dict()
    }), 201


@notifications_bp.route('/admin/notifications/bulk', methods=['POST'])
@jwt_required()
def create_bulk_notifications():
    """Create notifications for multiple users (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user is an admin
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({
            'error': 'not_authorized',
            'message': 'Not authorized to create notifications for other users'
        }), 403
    
    # Validate request data
    if not request.json:
        return jsonify({
            'error': 'invalid_request',
            'message': 'Invalid request data'
        }), 400
    
    user_ids = request.json.get('user_ids')
    if not user_ids or not isinstance(user_ids, list):
        return jsonify({
            'error': 'user_ids_required',
            'message': 'User IDs are required as a list'
        }), 400
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Create notifications
    notifications = notification_service.create_bulk_notifications(
        user_ids=user_ids,
        type=request.json.get('type', 'system'),
        title=request.json.get('title', 'System Notification'),
        message=request.json.get('message', ''),
        data=request.json.get('data'),
        related_id=request.json.get('related_id'),
        related_type=request.json.get('related_type'),
        sender_id=current_user_id,
        priority=request.json.get('priority', 'normal'),
        send_email=request.json.get('send_email', False),
        tenant_id=request.json.get('tenant_id')
    )
    
    return jsonify({
        'message': f'{len(notifications)} notifications created'
    }), 201


@notifications_bp.route('/admin/notifications/role', methods=['POST'])
@jwt_required()
def create_role_notification():
    """Create a notification for all users with a specific role (admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user is an admin
    if current_user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({
            'error': 'not_authorized',
            'message': 'Not authorized to create notifications for roles'
        }), 403
    
    # Validate request data
    if not request.json:
        return jsonify({
            'error': 'invalid_request',
            'message': 'Invalid request data'
        }), 400
    
    role = request.json.get('role')
    if not role:
        return jsonify({
            'error': 'role_required',
            'message': 'Role is required'
        }), 400
    
    # Get notification service
    notification_service = get_notification_service()
    
    # Create notifications
    notifications = notification_service.create_role_notification(
        role=role,
        type=request.json.get('type', 'system'),
        title=request.json.get('title', 'System Notification'),
        message=request.json.get('message', ''),
        data=request.json.get('data'),
        related_id=request.json.get('related_id'),
        related_type=request.json.get('related_type'),
        sender_id=current_user_id,
        priority=request.json.get('priority', 'normal'),
        send_email=request.json.get('send_email', False),
        tenant_id=request.json.get('tenant_id')
    )
    
    return jsonify({
        'message': f'{len(notifications)} notifications created for {role}s'
    }), 201