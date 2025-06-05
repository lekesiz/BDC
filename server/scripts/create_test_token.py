#!/usr/bin/env python
"""Create a test token for development."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask_jwt_extended import create_access_token
from app.models.user import User

def create_test_token():
    """Create a test token for admin user."""
    app = create_app()
    
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='admin@bdc.com').first()
        
        if admin:
            # Create token
            access_token = create_access_token(identity=admin.id)
            
            print("Test token created successfully!")
            print(f"Token: {access_token}")
            print("\nTo use in browser console:")
            print(f"localStorage.setItem('access_token', '{access_token}');")
            print("window.location.reload();")
            
            return access_token
        else:
            print("Admin user not found!")
            return None

if __name__ == '__main__':
    create_test_token()