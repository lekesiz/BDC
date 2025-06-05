"""Basic Socket.IO event handlers."""

from app.extensions import socketio
from flask_socketio import emit

from app.utils.logging import logger

# Commented out to allow socketio_events.py to handle authentication
# @socketio.on('connect')
# def handle_connect():
#     """Handle client connection."""
#     logger.info("Client connected")
#     emit('connected', {'message': 'Welcome to BDC'})
#     return True

# @socketio.on('disconnect')
# def handle_disconnect():
#     """Handle client disconnection."""
#     logger.info("Client disconnected")

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages."""
    logger.info(f"Received message: {data}")
    emit('response', {'echo': data})