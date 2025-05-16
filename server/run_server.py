#!/usr/bin/env python3
"""Run the Flask application with proper initialization and CORS support."""

import sys
import os

# IMPORTANT: Apply eventlet monkey-patch first
import eventlet
eventlet.monkey_patch()

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, socketio
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
import redis

# Create the app
app = create_app()

# Initialize database within app context
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check for admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if not admin:
        print("Creating admin user...")
        
        # Create default tenant if it doesn't exist
        tenant = Tenant.query.filter_by(slug='default').first()
        if not tenant:
            tenant = Tenant(
                name='Default',
                slug='default',
                email='admin@default.com',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            print("Created default tenant")
        
        # Create admin user
        admin = User(
            email='admin@bdc.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_active=True,
            tenant_id=tenant.id
        )
        admin.password = 'Admin123!'
        
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")
    else:
        print("Admin user already exists")
    
    # Verify admin can login
    if admin.verify_password('Admin123!'):
        print("Admin password verified successfully")
    else:
        print("Resetting admin password...")
        admin.password = 'Admin123!'
        db.session.commit()
        print("Admin password reset")
    
    # Ensure admin has username
    if not admin.username:
        admin.username = 'admin'
        db.session.commit()
        print("Added username to admin")
    
    # List all users
    users = User.query.all()
    print(f"\nUsers in database: {len(users)}")
    for user in users:
        print(f"- {user.email} ({user.role})")
    
    # Test Redis connection
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        print("\nRedis connection successful")
    except Exception as e:
        print(f"\nRedis connection failed: {e}")
        print("WARNING: Running without Redis. Some features may not work.")

# Run the app with SocketIO
if __name__ == '__main__':
    print("\nStarting Flask server on http://localhost:5001")
    print("CORS enabled for: http://localhost:5173, http://localhost:3000")
    print("Press CTRL+C to quit\n")
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)