#!/usr/bin/env python
"""Direct test of auth service."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.services.auth_service import AuthService

def test_auth():
    """Test authentication directly."""
    app = create_app()
    
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='admin@bdc.com').first()
        
        print(f"Admin user found: {admin is not None}")
        if admin:
            print(f"Email: {admin.email}")
            print(f"Active: {admin.is_active}")
            print(f"Role: {admin.role}")
            
            # Test password directly
            password_ok = admin.verify_password('Admin123!')
            print(f"Password verification: {password_ok}")
            
            # Test auth service
            result = AuthService.login('admin@bdc.com', 'Admin123!', False)
            print(f"AuthService.login result: {result is not None}")
            
            if result:
                print("Login successful!")
                print(f"Access token: {result['access_token'][:50]}...")
            else:
                print("Login failed in AuthService")

if __name__ == '__main__':
    test_auth()