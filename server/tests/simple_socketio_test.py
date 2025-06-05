#!/usr/bin/env python3
"""Simple Socket.IO test server."""

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from app.utils.logging import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    emit('connected', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

@app.route('/')
def index():
    return 'Socket.IO Server Running'

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)