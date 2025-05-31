#!/usr/bin/env python3
"""WSGI entry point for production deployment."""

import os
import sys
from pathlib import Path

# Add the server directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app
from app.extensions import socketio

# Create application instance
application = create_app()

# For Gunicorn with SocketIO support
app = application

if __name__ == "__main__":
    # Development server with SocketIO support
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    socketio.run(application, host='0.0.0.0', port=port, debug=debug)