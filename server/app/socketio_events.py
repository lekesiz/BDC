"""WebSocket events for real-time features."""

from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from flask import request
from app.extensions import socketio
from app.models.user import User
from app.models.notification import Notification, MessageThread, Message
from app import db
import json

# Store connected users
connected_users = {}

@socketio.on('connect')
def handle_connect(auth=None):
    """Handle client connection."""
    print(f"Connection attempt with auth: {auth}")
    
    # For now, allow all connections
    if request.sid:
        print(f"Client {request.sid} connected successfully")
    
    emit('connected', {'status': 'Connected successfully'})
    return True
    
    if not auth or 'token' not in auth:
        print("No auth token provided")
        return True
    
    try:
        # Get the token from auth
        token = auth['token']
        
        # Decode JWT token from flask-jwt-extended
        from flask_jwt_extended import decode_token
        decoded = decode_token(token, allow_expired=False)
        user_id = decoded['sub']
        
        print(f"Successfully decoded token for user: {user_id}")
        
        # Store socket ID
        connected_users[user_id] = request.sid
        
        # Join user's personal room
        join_room(f'user_{user_id}')
        
        # Get user's tenant
        user = User.query.get(user_id)
        if user and user.tenant_id:
            join_room(f'tenant_{user.tenant_id}')
        
        emit('connected', {'status': 'Connected successfully'})
        print(f"User {user_id} connected successfully")
        return True
        
    except Exception as e:
        print(f"Connection error: {e}")
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    # Find and remove user from connected users
    for user_id, sid in connected_users.items():
        if sid == request.sid:
            del connected_users[user_id]
            
            # Leave rooms
            leave_room(f'user_{user_id}')
            
            user = User.query.get(user_id)
            if user and user.tenant_id:
                leave_room(f'tenant_{user.tenant_id}')
            break


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
    """Handle sending a message."""
    try:
        # Get sender ID from token
        token = data.get('token')
        if not token:
            return
        
        decoded = decode_token(token)
        sender_id = decoded['sub']
        
        # Create message
        message = Message(
            thread_id=data['thread_id'],
            sender_id=sender_id,
            content=data['content']
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Emit to thread participants
        thread = MessageThread.query.get(data['thread_id'])
        for participant in thread.participants:
            if participant.user_id in connected_users:
                emit('new_message', {
                    'id': message.id,
                    'thread_id': message.thread_id,
                    'sender_id': message.sender_id,
                    'content': message.content,
                    'created_at': message.created_at.isoformat()
                }, room=f'user_{participant.user_id}')
                
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator."""
    try:
        # Get sender ID from token
        token = data.get('token')
        if not token:
            return
        
        decoded = decode_token(token)
        sender_id = decoded['sub']
        
        # Emit to thread participants
        thread = MessageThread.query.get(data['thread_id'])
        for participant in thread.participants:
            if participant.user_id != sender_id and participant.user_id in connected_users:
                emit('user_typing', {
                    'thread_id': data['thread_id'],
                    'user_id': sender_id,
                    'is_typing': data.get('is_typing', True)
                }, room=f'user_{participant.user_id}')
                
    except Exception as e:
        pass


@socketio.on('mark_read')
def handle_mark_read(data):
    """Mark messages as read."""
    try:
        # Get user ID from token
        token = data.get('token')
        if not token:
            return
        
        decoded = decode_token(token)
        user_id = decoded['sub']
        
        # Mark notifications as read
        if 'notification_ids' in data:
            Notification.query.filter(
                Notification.id.in_(data['notification_ids']),
                Notification.recipient_id == user_id
            ).update({'is_read': True})
            db.session.commit()
            
            emit('notifications_read', {
                'notification_ids': data['notification_ids']
            })
            
    except Exception as e:
        emit('error', {'message': str(e)})


def send_notification(user_id, notification_data):
    """Send notification to specific user."""
    if user_id in connected_users:
        socketio.emit('notification', notification_data, room=f'user_{user_id}')


def broadcast_to_tenant(tenant_id, event_name, data):
    """Broadcast event to all users in a tenant."""
    socketio.emit(event_name, data, room=f'tenant_{tenant_id}')


def broadcast_to_role(role, event_name, data):
    """Broadcast event to all users with specific role."""
    # Get all users with role
    users = User.query.filter_by(role=role).all()
    
    for user in users:
        if user.id in connected_users:
            socketio.emit(event_name, data, room=f'user_{user.id}')