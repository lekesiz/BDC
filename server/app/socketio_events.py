"""WebSocket events for real-time features."""

from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from flask import request, current_app
from app.extensions import socketio, db
from app.models.user import User
from app.models.notification import Notification, MessageThread, Message
import json
import logging
from datetime import datetime

# Configure websocket logging
socketio_logger = logging.getLogger('socketio')

# Store connected users: {user_id: sid}
connected_users = {}

@socketio.on('connect')
def handle_connect(auth=None):
    """
    Handle client connection.
    
    Authentication can be provided in two ways:
    1. Via auth parameter (preferred for Socket.IO clients)
    2. Via query parameter token in the connection URL
    
    Returns True to allow the connection, or False to reject it.
    """
    # Extract token from auth parameter or query parameters
    token = None
    if auth and 'token' in auth:
        token = auth['token']
    elif request.args and 'token' in request.args:
        token = request.args.get('token')
    
    socketio_logger.info(f"Connection attempt from {request.remote_addr}")
    
    # If no token, still allow connection but don't register the user
    if not token:
        socketio_logger.info("No auth token provided, allowing anonymous connection")
        emit('connected', {'status': 'Connected anonymously'})
        return True
    
    try:
        # Decode JWT token
        decoded = decode_token(token, allow_expired=False)
        user_id = decoded['sub']
        
        # Store socket ID
        connected_users[user_id] = request.sid
        
        # Join user's personal room
        join_room(f'user_{user_id}')
        
        # Get user's tenant and role
        user = User.query.get(user_id)
        if user:
            # Join tenant room
            if user.tenant_id:
                join_room(f'tenant_{user.tenant_id}')
            
            # Join role room
            if user.role:
                join_room(f'role_{user.role}')
                
            socketio_logger.info(f"User {user_id} ({user.role}) connected successfully")
            
            # Return success with user info
            emit('connected', {
                'status': 'Connected successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role
                }
            })
        else:
            socketio_logger.warning(f"Valid token but user {user_id} not found")
            emit('connected', {'status': 'Connected with limited access'})
            
        return True
        
    except Exception as e:
        socketio_logger.error(f"Connection authentication error: {str(e)}")
        # Still allow connection, but with a warning
        emit('connected', {'status': 'Connected anonymously', 'warning': 'Invalid authentication'})
        return True


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    # Find and remove user from connected users
    user_id = next((uid for uid, sid in connected_users.items() if sid == request.sid), None)
    
    if user_id:
        # Remove from connected users dict
        socketio_logger.info(f"User {user_id} disconnected")
        del connected_users[user_id]
        
        # Leave user room
        leave_room(f'user_{user_id}')
        
        # Get user to leave tenant and role rooms
        try:
            user = User.query.get(user_id)
            if user:
                # Leave tenant room
                if user.tenant_id:
                    leave_room(f'tenant_{user.tenant_id}')
                
                # Leave role room
                if user.role:
                    leave_room(f'role_{user.role}')
        except Exception as e:
            socketio_logger.error(f"Error during disconnect cleanup: {str(e)}")
    else:
        socketio_logger.info(f"Anonymous client {request.sid} disconnected")


@socketio.on('join_room')
def handle_join_room(data):
    """Join a specific room."""
    room = data.get('room')
    if room:
        join_room(room)
        emit('joined_room', {'room': room})


@socketio.on('leave_room')
def handle_leave_room(data):
    """Leave a specific room."""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('left_room', {'room': room})


@socketio.on('send_message')
def handle_send_message(data):
    """
    Handle sending a message in a thread.
    
    Required data keys:
    - thread_id: ID of the message thread
    - content: Message content
    - token: JWT token for authentication
    
    Optional data keys:
    - attachments: List of attachment IDs or URLs
    """
    try:
        # Get sender ID from token
        token = data.get('token')
        if not token:
            socketio_logger.warning("Message send attempt without token")
            emit('error', {'message': 'Authentication required'})
            return
        
        # Validate thread_id and content
        if 'thread_id' not in data:
            emit('error', {'message': 'Thread ID is required'})
            return
            
        if 'content' not in data or not data['content'].strip():
            emit('error', {'message': 'Message content is required'})
            return
        
        # Decode token to get user ID
        try:
            decoded = decode_token(token)
            sender_id = decoded['sub']
        except Exception as auth_error:
            socketio_logger.warning(f"Invalid token in message: {auth_error}")
            emit('error', {'message': 'Invalid authentication'})
            return
        
        # Get the thread and verify participant
        thread = MessageThread.query.get(data['thread_id'])
        if not thread:
            emit('error', {'message': 'Thread not found'})
            return
            
        # Check if user is participant in thread
        is_participant = any(p.user_id == sender_id for p in thread.participants)
        if not is_participant:
            socketio_logger.warning(f"User {sender_id} tried to send message to thread they're not in: {thread.id}")
            emit('error', {'message': 'You are not a participant in this thread'})
            return
        
        # Create message
        message = Message(
            thread_id=data['thread_id'],
            sender_id=sender_id,
            content=data['content'],
            attachments=data.get('attachments', [])
        )
        
        db.session.add(message)
        
        # Mark thread as unread for other participants
        for participant in thread.participants:
            if participant.user_id != sender_id:
                participant.last_read_at = None
        
        # Update thread last activity
        thread.last_activity = message.created_at
        db.session.commit()
        
        # Prepare message data for sending
        message_data = {
            'id': message.id,
            'thread_id': message.thread_id,
            'sender_id': message.sender_id,
            'content': message.content,
            'attachments': message.attachments if hasattr(message, 'attachments') else [],
            'created_at': message.created_at.isoformat()
        }
        
        # Get sender information to include in the message
        sender = User.query.get(sender_id)
        if sender:
            message_data['sender'] = {
                'id': sender.id,
                'name': f"{sender.first_name} {sender.last_name}",
                'avatar': sender.profile_image if hasattr(sender, 'profile_image') else None
            }
        
        # Emit to thread participants
        socketio_logger.info(f"Sending message in thread {thread.id} from user {sender_id}")
        for participant in thread.participants:
            if participant.user_id in connected_users:
                emit('new_message', message_data, room=f'user_{participant.user_id}')
                
        # Create notifications for other participants who are not connected
        for participant in thread.participants:
            if participant.user_id != sender_id and participant.user_id not in connected_users:
                # Create notification for offline participants
                try:
                    from app.services.notification_service import NotificationService
                    NotificationService.create_notification(
                        recipient_id=participant.user_id,
                        sender_id=sender_id,
                        notification_type='message',
                        content=f"New message from {sender.first_name} {sender.last_name}" if sender else "New message",
                        data={
                            'thread_id': thread.id,
                            'message_id': message.id
                        }
                    )
                except Exception as notify_error:
                    socketio_logger.error(f"Failed to create notification: {notify_error}")
                
    except Exception as e:
        socketio_logger.error(f"Error sending message: {str(e)}")
        emit('error', {'message': 'An error occurred while sending your message'})


@socketio.on('typing')
def handle_typing(data):
    """
    Handle typing indicator in a message thread.
    
    Required data keys:
    - thread_id: ID of the message thread
    - token: JWT token for authentication
    
    Optional data keys:
    - is_typing: Boolean indicating whether user is typing (default: True)
    """
    try:
        # Get sender ID from token
        token = data.get('token')
        if not token:
            return
        
        # Validate thread_id
        if 'thread_id' not in data:
            return
            
        # Decode token to get user ID
        try:
            decoded = decode_token(token)
            sender_id = decoded['sub']
        except Exception:
            return
        
        # Get thread and validate user is a participant
        thread = MessageThread.query.get(data['thread_id'])
        if not thread:
            return
            
        # Check if user is participant in thread
        is_participant = any(p.user_id == sender_id for p in thread.participants)
        if not is_participant:
            return
        
        # Get user info for richer typing indicator
        sender = User.query.get(sender_id)
        sender_name = f"{sender.first_name} {sender.last_name}" if sender else f"User {sender_id}"
        
        # Emit typing indicator to other participants
        for participant in thread.participants:
            if participant.user_id != sender_id and participant.user_id in connected_users:
                emit('user_typing', {
                    'thread_id': data['thread_id'],
                    'user_id': sender_id,
                    'user_name': sender_name,
                    'is_typing': data.get('is_typing', True),
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f'user_{participant.user_id}')
                
    except Exception as e:
        socketio_logger.error(f"Error in typing indicator: {str(e)}")


@socketio.on('mark_read')
def handle_mark_read(data):
    """
    Mark notifications or messages as read.
    
    Required data keys:
    - token: JWT token for authentication
    
    Optional data keys (at least one required):
    - notification_ids: List of notification IDs to mark as read
    - thread_id: Thread ID to mark as read
    - message_ids: List of message IDs to mark as read
    """
    try:
        # Get user ID from token
        token = data.get('token')
        if not token:
            emit('error', {'message': 'Authentication required'})
            return
        
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
        except Exception:
            emit('error', {'message': 'Invalid authentication'})
            return
        
        # Check if any valid data is provided
        has_valid_data = any(key in data for key in ['notification_ids', 'thread_id', 'message_ids'])
        if not has_valid_data:
            emit('error', {'message': 'No valid items to mark as read'})
            return
        
        # Mark notifications as read
        if 'notification_ids' in data and isinstance(data['notification_ids'], list):
            notification_count = Notification.query.filter(
                Notification.id.in_(data['notification_ids']),
                Notification.recipient_id == user_id,
                Notification.is_read == False
            ).update({'is_read': True}, synchronize_session=False)
            
            socketio_logger.info(f"Marked {notification_count} notifications as read for user {user_id}")
            
            # Get updated unread count
            unread_count = Notification.query.filter_by(
                recipient_id=user_id,
                is_read=False
            ).count()
            
            # Emit events
            emit('notifications_read', {
                'notification_ids': data['notification_ids'],
                'unread_count': unread_count
            }, room=f'user_{user_id}')
            
            # Emit unread count update event
            emit('notification_count_updated', {
                'count': unread_count
            }, room=f'user_{user_id}')
            
        # Mark message thread as read
        if 'thread_id' in data:
            thread_id = data['thread_id']
            
            # Get the thread
            thread = MessageThread.query.get(thread_id)
            if thread:
                # Find participant record
                from sqlalchemy import and_
                from app.models.notification import ThreadParticipant
                
                participant = ThreadParticipant.query.filter(
                    and_(
                        ThreadParticipant.thread_id == thread_id,
                        ThreadParticipant.user_id == user_id
                    )
                ).first()
                
                if participant:
                    # Update last_read_at to current time
                    participant.last_read_at = datetime.utcnow()
                    db.session.commit()
                    
                    socketio_logger.info(f"Marked thread {thread_id} as read for user {user_id}")
                    
                    # Emit event
                    emit('thread_read', {
                        'thread_id': thread_id,
                        'last_read_at': participant.last_read_at.isoformat()
                    }, room=f'user_{user_id}')
            
        # Mark specific messages as read
        if 'message_ids' in data and isinstance(data['message_ids'], list):
            # This would require additional implementation based on your data model
            pass
            
        # Commit any pending changes
        db.session.commit()
            
    except Exception as e:
        socketio_logger.error(f"Error marking items as read: {str(e)}")
        emit('error', {'message': 'Failed to mark items as read'})


def send_notification(user_id, notification_data):
    """
    Send a real-time notification to a specific user.
    
    Args:
        user_id (int): The user's ID
        notification_data (dict): The notification data to send
        
    Returns:
        bool: True if the notification was sent, False otherwise
    """
    if user_id in connected_users:
        try:
            socketio.emit('notification', notification_data, room=f'user_{user_id}')
            socketio_logger.debug(f"Sent notification to user {user_id}")
            return True
        except Exception as e:
            socketio_logger.error(f"Failed to send notification to user {user_id}: {e}")
            return False
    else:
        # User not connected
        socketio_logger.debug(f"User {user_id} not connected, notification not sent")
        return False


def broadcast_to_tenant(tenant_id, event_name, data):
    """
    Broadcast an event to all users in a tenant.
    
    Args:
        tenant_id (int): The tenant's ID
        event_name (str): The name of the event
        data (dict): The data to send with the event
        
    Returns:
        bool: True if the event was broadcast, False otherwise
    """
    try:
        socketio.emit(event_name, data, room=f'tenant_{tenant_id}')
        socketio_logger.debug(f"Broadcast {event_name} to tenant {tenant_id}")
        return True
    except Exception as e:
        socketio_logger.error(f"Failed to broadcast {event_name} to tenant {tenant_id}: {e}")
        return False


def broadcast_to_role(role, event_name, data):
    """
    Broadcast an event to all users with a specific role.
    
    Args:
        role (str): The role name (e.g. 'super_admin', 'tenant_admin', 'trainer', 'student')
        event_name (str): The name of the event
        data (dict): The data to send with the event
        
    Returns:
        int: The number of users the event was sent to
    """
    sent_count = 0
    try:
        # First try broadcasting to role room directly
        socketio.emit(event_name, data, room=f'role_{role}')
        socketio_logger.debug(f"Broadcast {event_name} to role {role}")
        
        # For precise counting, we need to check individual users
        users = User.query.filter_by(role=role).all()
        for user in users:
            if user.id in connected_users:
                sent_count += 1
                
        return sent_count
    except Exception as e:
        socketio_logger.error(f"Failed to broadcast {event_name} to role {role}: {e}")
        
        # Fallback to manual broadcasting to each user
        users = User.query.filter_by(role=role).all()
        for user in users:
            if user.id in connected_users:
                try:
                    socketio.emit(event_name, data, room=f'user_{user.id}')
                    sent_count += 1
                except Exception:
                    pass
                    
        return sent_count


def broadcast_system_notification(message, level='info', roles=None):
    """
    Broadcast a system notification to all users or specific roles.
    
    Args:
        message (str): The notification message
        level (str): The notification level (info, warning, error)
        roles (list): Optional list of roles to send to (None = all users)
        
    Returns:
        int: The number of users the notification was sent to
    """
    notification = {
        'type': 'system',
        'message': message,
        'level': level,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    sent_count = 0
    
    try:
        if roles:
            # Send to specific roles
            for role in roles:
                sent_count += broadcast_to_role(role, 'system_notification', notification)
        else:
            # Broadcast to all connected users
            socketio.emit('system_notification', notification, broadcast=True)
            sent_count = len(connected_users)
            
        return sent_count
    except Exception as e:
        socketio_logger.error(f"Failed to broadcast system notification: {e}")
        return 0