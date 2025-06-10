#!/usr/bin/env python3
"""
BDC Platform - Simple Development Server Runner
"""
import os
import sys
from flask import Flask
from flask_cors import CORS
from app.extensions import db, jwt, migrate, cache
from config import DevelopmentConfig

# Create Flask app
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Initialize extensions
db.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)
cache.init_app(app)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Import and register critical blueprints only
try:
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✓ Auth API registered")
except Exception as e:
    print(f"✗ Auth API failed: {e}")

try:
    from app.api.users import users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')
    print("✓ Users API registered")
except Exception as e:
    print(f"✗ Users API failed: {e}")

try:
    from app.api.beneficiaries_v2 import beneficiaries_bp
    app.register_blueprint(beneficiaries_bp, url_prefix='/api/beneficiaries')
    print("✓ Beneficiaries API registered")
except Exception as e:
    print(f"✗ Beneficiaries API failed: {e}")

try:
    from app.api.programs import programs_bp
    app.register_blueprint(programs_bp, url_prefix='/api/programs')
    print("✓ Programs API registered")
except Exception as e:
    print(f"✗ Programs API failed: {e}")

# Basic health check
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'mode': 'simple'
    }

# Simple root endpoint
@app.route('/')
def index():
    return {
        'message': 'BDC API Server',
        'status': 'running',
        'endpoints': [
            '/health',
            '/api/auth/login',
            '/api/users',
            '/api/beneficiaries',
            '/api/programs'
        ]
    }

if __name__ == '__main__':
    # Ensure database exists
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║           BDC Platform (Simple Mode)             ║
    ║            Development Server                    ║
    ╠══════════════════════════════════════════════════╣
    ║  Server running at: http://localhost:{port}       ║
    ║  Health Check: http://localhost:{port}/health     ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )