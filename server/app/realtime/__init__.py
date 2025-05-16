"""Real-time communication module using Socket.IO."""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, current_app
from flask_jwt_extended import decode_token
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import json
import functools

# Initialize SocketIO with message queue (Redis)
socketio = SocketIO()

# Store active connections
active_users = {}  # Maps user_id to session_id
user_rooms = {}    # Maps user_id to list of rooms


def configure_socketio(app):
    """Configure SocketIO with the Flask app."""
    # Configure SocketIO
    socketio.init_app(
        app,
        message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE', 'redis://'),
        cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'),
        async_mode='eventlet'
    )
    
    # Register event handlers
    register_event_handlers()
    
    return socketio


def register_event_handlers():
    """Register Socket.IO event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        # Authenticate user
        token = request.args.get('token')
        if not token:
            return False  # Reject connection
        
        try:
            # Decode and validate token
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
            
            # Store session ID for this user
            active_users[user_id] = request.sid
            user_rooms[user_id] = []
            
            # Join user's personal room
            join_room(f'user_{user_id}')
            user_rooms[user_id].append(f'user_{user_id}')
            
            # Get user's roles and tenants
            from app.models.user import User
            user = User.query.get(user_id)
            
            if user:
                # Join role-based room
                join_room(f'role_{user.role}')
                user_rooms[user_id].append(f'role_{user.role}')
                
                # Join tenant-based rooms if applicable
                for tenant in user.tenants:
                    join_room(f'tenant_{tenant.id}')
                    user_rooms[user_id].append(f'tenant_{tenant.id}')
            
            current_app.logger.info(f"User {user_id} connected")
            return True
            
        except (InvalidTokenError, ExpiredSignatureError) as e:
            current_app.logger.warning(f"Authentication failed: {str(e)}")
            return False  # Reject connection
        
        except Exception as e:
            current_app.logger.error(f"Connection error: {str(e)}")
            return False  # Reject connection
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        # Find user ID from session ID
        user_id = None
        for uid, sid in active_users.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if user_id:
            # Remove user from active users
            active_users.pop(user_id, None)
            
            # Remove user from rooms
            for room in user_rooms.get(user_id, []):
                leave_room(room)
            
            user_rooms.pop(user_id, None)
            
            current_app.logger.info(f"User {user_id} disconnected")
    
    @socketio.on('join')
    def handle_join(data):
        """Handle client joining a room."""
        # Ensure user is authenticated
        user_id = get_user_id_from_session()
        if not user_id:
            return
        
        # Join room
        room = data.get('room')
        if room:
            join_room(room)
            
            # Track room for user
            if room not in user_rooms.get(user_id, []):
                user_rooms.setdefault(user_id, []).append(room)
                
            current_app.logger.info(f"User {user_id} joined room {room}")
    
    @socketio.on('leave')
    def handle_leave(data):
        """Handle client leaving a room."""
        # Ensure user is authenticated
        user_id = get_user_id_from_session()
        if not user_id:
            return
        
        # Leave room
        room = data.get('room')
        if room:
            leave_room(room)
            
            # Remove room from user's list
            if room in user_rooms.get(user_id, []):
                user_rooms[user_id].remove(room)
                
            current_app.logger.info(f"User {user_id} left room {room}")


def get_user_id_from_session():
    """Get the user ID from the current session."""
    for user_id, sid in active_users.items():
        if sid == request.sid:
            return user_id
    return None


def user_is_online(user_id):
    """Check if a user is currently online."""
    return user_id in active_users


def emit_to_user(user_id, event, data):
    """Emit an event to a specific user."""
    room = f'user_{user_id}'
    socketio.emit(event, data, room=room, namespace='/')


def emit_to_role(role, event, data):
    """Emit an event to all users with a specific role."""
    room = f'role_{role}'
    socketio.emit(event, data, room=room, namespace='/')


def emit_to_tenant(tenant_id, event, data):
    """Emit an event to all users in a specific tenant."""
    room = f'tenant_{tenant_id}'
    socketio.emit(event, data, room=room, namespace='/')


def emit_to_room(room, event, data):
    """Emit an event to all users in a specific room."""
    socketio.emit(event, data, room=room, namespace='/')


def broadcast(event, data):
    """Broadcast an event to all connected users."""
    socketio.emit(event, data, namespace='/')