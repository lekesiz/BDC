#!/usr/bin/env python3
"""Run the Flask application with proper initialization."""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant

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
        tenant = Tenant.query.filter_by(code='DEFAULT').first()
        if not tenant:
            tenant = Tenant(
                name='Default',
                code='DEFAULT',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            print("Created default tenant")
        
        # Create admin user
        admin = User(
            email='admin@bdc.com',
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_active=True
        )
        admin.password = 'Admin123!'
        admin.tenants.append(tenant)
        
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
    
    # List all users
    users = User.query.all()
    print(f"\nUsers in database: {len(users)}")
    for user in users:
        print(f"- {user.email} ({user.role})")

# Run the app
if __name__ == '__main__':
    print("\nStarting Flask server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)