#!/usr/bin/env python3
"""Reset admin password."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    
    if admin:
        print(f"Found admin user: {admin.email}")
        print(f"Current role: {admin.role}")
        print(f"Is active: {admin.is_active}")
        
        # Reset password
        admin.password = 'Admin123!'
        db.session.commit()
        
        print("\nPassword reset successfully!")
        print("New password: Admin123!")
        
        # Verify password
        if admin.verify_password('Admin123!'):
            print("Password verification: SUCCESS")
        else:
            print("Password verification: FAILED")
    else:
        print("Admin user not found!")