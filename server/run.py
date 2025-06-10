#!/usr/bin/env python3
"""
BDC Platform - Development Server Runner
"""
import os
import sys
from app import create_app

# Set environment to development if not specified
os.environ.setdefault('FLASK_ENV', 'development')

# Create Flask app
app = create_app('development')

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    
    # Get host from environment or use default
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║                BDC Platform                      ║
    ║            Development Server                    ║
    ╠══════════════════════════════════════════════════╣
    ║  Server running at: http://localhost:{port}       ║
    ║  API Docs: http://localhost:{port}/api/docs       ║
    ║  Health Check: http://localhost:{port}/health     ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # Run the development server
    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=True,
        use_debugger=True
    )