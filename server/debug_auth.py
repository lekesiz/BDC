#!/usr/bin/env python3
"""Debug auth issue."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    
    if admin:
        print("Admin user found")
        print(f"Email: {admin.email}")
        print(f"Is active: {admin.is_active}")
        print(f"Role: {admin.role}")
        print(f"Password hash: {admin.password_hash[:20]}...")
        
        # Test password verification with different methods
        test_password = 'Admin123!'
        
        # Direct method
        print(f"\nDirect verify_password: {admin.verify_password(test_password)}")
        
        # Using werkzeug directly
        print(f"Werkzeug check_password_hash: {check_password_hash(admin.password_hash, test_password)}")
        
        # Reset password again just to be sure
        print("\nResetting password...")
        admin.password = test_password
        db.session.commit()
        
        # Test again
        print(f"After reset - verify_password: {admin.verify_password(test_password)}")
        
        # Now test the auth service
        from app.services.auth_service import AuthService
        print("\nTesting AuthService...")
        result = AuthService.login('admin@bdc.com', test_password)
        print(f"AuthService.login result: {'SUCCESS' if result else 'FAILED'}")
        
        if not result:
            # Debug the auth service
            print("\nDebugging AuthService...")
            user = User.query.filter_by(email='admin@bdc.com').first()
            print(f"User found: {user is not None}")
            if user:
                print(f"Password verification: {user.verify_password(test_password)}")
                print(f"Is active: {user.is_active}")
    else:
        print("Admin user not found!")
        
    # List all users
    print("\nAll users in database:")
    users = User.query.all()
    for user in users:
        print(f"- {user.email} (active: {user.is_active}, role: {user.role})")