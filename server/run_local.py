#!/usr/bin/env python3
"""Run the Flask application locally."""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    try:
        app = create_app()
        print("Starting Flask server on http://127.0.0.1:9001")
        app.run(host='127.0.0.1', port=9001, debug=True)
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        import traceback
        traceback.print_exc()