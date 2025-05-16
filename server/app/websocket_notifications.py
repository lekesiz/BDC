"""WebSocket notifications handler."""

from flask import request
from flask_jwt_extended import decode_token
from app.extensions import socketio
from app.models.notification import Notification
from app.models.user import User
from app import db
import json

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
            print(f"Token decode error: {e}")
            return False
            
        # Store client connection
        connected_clients[request.sid] = user_id
        print(f"User {user_id} connected to notifications")
        
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
        print(f"Connection error: {e}")
        return False

@socketio.on('disconnect', namespace='/ws/notifications')
def handle_notifications_disconnect():
    """Handle client disconnection from notifications namespace."""
    if request.sid in connected_clients:
        user_id = connected_clients[request.sid]
        del connected_clients[request.sid]
        print(f"User {user_id} disconnected from notifications")

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
        print(f"Mark read error: {e}")

def send_notification_to_user(user_id, notification_data):
    """Send notification to all connected devices of a user."""
    for sid, uid in connected_clients.items():
        if uid == user_id:
            socketio.emit('new_notification', {
                'type': 'new_notification',
                'notification': notification_data
            }, namespace='/ws/notifications', room=sid)