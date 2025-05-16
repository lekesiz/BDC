#!/usr/bin/env python
"""Test admin password with auth service."""

from app import create_app
from app.models import User
from app.services.auth_service import AuthService
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        print(f"Admin found: {admin.email}")
        print(f"Active: {admin.is_active}")
        print(f"Role: {admin.role}")
        
        # Direct password check
        print(f"Direct password check (admin123): {admin.verify_password('admin123')}")
        
        # Service check
        tokens = AuthService.login('admin@bdc.com', 'admin123')
        if tokens:
            print("AuthService login successful!")
            print(f"Access token: {tokens['access_token'][:50]}...")
        else:
            print("AuthService login failed!")
    else:
        print("Admin user not found")