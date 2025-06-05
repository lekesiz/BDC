"""WebSocket notifications handler."""

from flask import request
from flask_jwt_extended import decode_token
from app.extensions import socketio
from app.models.notification import Notification
from app.models.user import User
from app import db
import json

from app.utils.logging import logger

# Track connected clients
connected_clients = {}

@socketio.on('connect', namespace='/ws/notifications')
def handle_notifications_connect():
    """Handle client connection to notifications namespace."""
    try:
        # Get token from query params or headers
        token = request.args.get('token')
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return False
            
        # Decode token to get user ID
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
        except Exception as e:
            logger.info(f"Token decode error: {e}")
            return False
            
        # Store client connection
        connected_clients[request.sid] = user_id
        logger.info(f"User {user_id} connected to notifications")
        
        # Send current unread count
        unread_count = Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).count()
        
        socketio.emit('unread_count', {
            'count': unread_count
        }, namespace='/ws/notifications', room=request.sid)
        
        return True
        
    except Exception as e:
        logger.info(f"Connection error: {e}")
        return False

@socketio.on('disconnect', namespace='/ws/notifications')
def handle_notifications_disconnect():
    """Handle client disconnection from notifications namespace."""
    if request.sid in connected_clients:
        user_id = connected_clients[request.sid]
        del connected_clients[request.sid]
        logger.info(f"User {user_id} disconnected from notifications")

@socketio.on('mark_read', namespace='/ws/notifications')
def handle_mark_read(data):
    """Mark notification as read."""
    try:
        notification_id = data.get('notification_id')
        if not notification_id:
            return
            
        # Get user ID from connection
        user_id = connected_clients.get(request.sid)
        if not user_id:
            return
            
        # Update notification
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification and not notification.read:
            notification.read = True
            db.session.commit()
            
            # Broadcast to all user's connected devices
            for sid, uid in connected_clients.items():
                if uid == user_id:
                    socketio.emit('notification_read', {
                        'notification_id': notification_id
                    }, namespace='/ws/notifications', room=sid)
                    
    except Exception as e:
        logger.info(f"Mark read error: {e}")

def send_notification_to_user(user_id, notification_data):
    """Send notification to all connected devices of a user."""
    for sid, uid in connected_clients.items():
        if uid == user_id:
            socketio.emit('new_notification', {
                'type': 'new_notification',
                'notification': notification_data
            }, namespace='/ws/notifications', room=sid)


# Messaging WebSocket Events
@socketio.on('connect', namespace='/ws/messages')
def handle_messages_connect():
    """Handle client connection to messages namespace."""
    try:
        # Get token from query params or headers
        token = request.args.get('token')
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return False
            
        # Decode token to get user ID
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
        except Exception as e:
            logger.info(f"Token decode error: {e}")
            return False
            
        # Store client connection
        connected_clients[f"msg_{request.sid}"] = user_id
        logger.info(f"User {user_id} connected to messages")
        
        # Join user to their personal room for direct messages
        socketio.server.enter_room(request.sid, f"user_{user_id}", namespace='/ws/messages')
        
        # Get and join all thread rooms the user is part of
        from app.models.notification import ThreadParticipant
        participant_threads = ThreadParticipant.query.filter_by(user_id=user_id).all()
        for participant in participant_threads:
            socketio.server.enter_room(request.sid, f"thread_{participant.thread_id}", namespace='/ws/messages')
        
        return True
        
    except Exception as e:
        logger.info(f"Connection error: {e}")
        return False


@socketio.on('disconnect', namespace='/ws/messages')
def handle_messages_disconnect():
    """Handle client disconnection from messages namespace."""
    msg_sid = f"msg_{request.sid}"
    if msg_sid in connected_clients:
        user_id = connected_clients[msg_sid]
        del connected_clients[msg_sid]
        logger.info(f"User {user_id} disconnected from messages")


@socketio.on('join_thread', namespace='/ws/messages')
def handle_join_thread(data):
    """Join a message thread room."""
    try:
        thread_id = data.get('thread_id')
        if not thread_id:
            return
            
        # Get user ID from connection
        msg_sid = f"msg_{request.sid}"
        user_id = connected_clients.get(msg_sid)
        if not user_id:
            return
            
        # Verify user is participant
        from app.models.notification import ThreadParticipant
        participant = ThreadParticipant.query.filter_by(
            thread_id=thread_id,
            user_id=user_id
        ).first()
        
        if participant:
            socketio.server.enter_room(request.sid, f"thread_{thread_id}", namespace='/ws/messages')
            socketio.emit('joined_thread', {
                'thread_id': thread_id
            }, namespace='/ws/messages', room=request.sid)
                    
    except Exception as e:
        logger.info(f"Join thread error: {e}")


@socketio.on('leave_thread', namespace='/ws/messages')
def handle_leave_thread(data):
    """Leave a message thread room."""
    try:
        thread_id = data.get('thread_id')
        if not thread_id:
            return
            
        socketio.server.leave_room(request.sid, f"thread_{thread_id}", namespace='/ws/messages')
        socketio.emit('left_thread', {
            'thread_id': thread_id
        }, namespace='/ws/messages', room=request.sid)
                    
    except Exception as e:
        logger.info(f"Leave thread error: {e}")


@socketio.on('message_sent', namespace='/ws/messages')
def handle_message_sent(data):
    """Handle when a message is sent."""
    try:
        thread_id = data.get('thread_id')
        message_data = data.get('message')
        
        if not thread_id or not message_data:
            return
            
        # Get user ID from connection
        msg_sid = f"msg_{request.sid}"
        user_id = connected_clients.get(msg_sid)
        if not user_id:
            return
            
        # Verify user is participant
        from app.models.notification import ThreadParticipant
        participant = ThreadParticipant.query.filter_by(
            thread_id=thread_id,
            user_id=user_id
        ).first()
        
        if not participant:
            return
            
        # Broadcast to all participants in the thread
        socketio.emit('new_message', {
            'thread_id': thread_id,
            'message': message_data
        }, namespace='/ws/messages', room=f"thread_{thread_id}")
        
        # Send notification to other participants
        other_participants = ThreadParticipant.query.filter(
            ThreadParticipant.thread_id == thread_id,
            ThreadParticipant.user_id != user_id
        ).all()
        
        sender = User.query.get(user_id)
        for participant in other_participants:
            # Send push notification
            send_notification_to_user(participant.user_id, {
                'id': None,
                'title': 'New Message',
                'message': f'{sender.first_name} {sender.last_name} sent you a message',
                'type': 'message',
                'related_id': thread_id,
                'related_type': 'thread'
            })
                    
    except Exception as e:
        logger.info(f"Message sent error: {e}")


@socketio.on('typing', namespace='/ws/messages')
def handle_typing(data):
    """Handle typing indicator."""
    try:
        thread_id = data.get('thread_id')
        is_typing = data.get('is_typing', False)
        
        if not thread_id:
            return
            
        # Get user ID from connection
        msg_sid = f"msg_{request.sid}"
        user_id = connected_clients.get(msg_sid)
        if not user_id:
            return
            
        # Get user info
        user = User.query.get(user_id)
        if not user:
            return
            
        # Broadcast to other participants in the thread
        socketio.emit('user_typing', {
            'thread_id': thread_id,
            'user_id': user_id,
            'user_name': f"{user.first_name} {user.last_name}",
            'is_typing': is_typing
        }, namespace='/ws/messages', room=f"thread_{thread_id}", include_self=False)
                    
    except Exception as e:
        logger.info(f"Typing indicator error: {e}")


@socketio.on('mark_read', namespace='/ws/messages')
def handle_mark_message_read(data):
    """Mark message as read."""
    try:
        message_id = data.get('message_id')
        if not message_id:
            return
            
        # Get user ID from connection
        msg_sid = f"msg_{request.sid}"
        user_id = connected_clients.get(msg_sid)
        if not user_id:
            return
            
        # Create read receipt
        from app.models.notification import ReadReceipt, Message
        from datetime import datetime
        
        message = Message.query.get(message_id)
        if not message:
            return
            
        # Check if user is participant in the thread
        from app.models.notification import ThreadParticipant
        participant = ThreadParticipant.query.filter_by(
            thread_id=message.thread_id,
            user_id=user_id
        ).first()
        
        if not participant:
            return
            
        # Check if read receipt already exists
        existing = ReadReceipt.query.filter_by(
            message_id=message_id,
            user_id=user_id
        ).first()
        
        if not existing:
            read_receipt = ReadReceipt(
                message_id=message_id,
                user_id=user_id,
                read_at=datetime.utcnow()
            )
            db.session.add(read_receipt)
            db.session.commit()
            
            # Broadcast read receipt to thread participants
            socketio.emit('message_read', {
                'message_id': message_id,
                'user_id': user_id,
                'read_at': read_receipt.read_at.isoformat()
            }, namespace='/ws/messages', room=f"thread_{message.thread_id}")
                    
    except Exception as e:
        logger.info(f"Mark message read error: {e}")


def emit_to_thread(thread_id, event, data):
    """Emit an event to all participants in a thread."""
    socketio.emit(event, data, namespace='/ws/messages', room=f"thread_{thread_id}")


def emit_to_user(user_id, event, data):
    """Emit an event to a specific user."""
    socketio.emit(event, data, namespace='/ws/messages', room=f"user_{user_id}")