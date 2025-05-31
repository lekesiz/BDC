"""Basic Socket.IO event handlers."""

from app.extensions import socketio
from flask_socketio import emit

# Commented out to allow socketio_events.py to handle authentication
# @socketio.on('connect')
# def handle_connect():
#     """Handle client connection."""
#     print('Client connected')
#     emit('connected', {'message': 'Welcome to BDC'})
#     return True

# @socketio.on('disconnect')
# def handle_disconnect():
#     """Handle client disconnection."""
#     print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages."""
    print(f'Received message: {data}')
    emit('response', {'echo': data})