"""Utility script to manually inspect the admin user.

This module is NOT intended to run under the automated pytest suite because it
relies on a running PostgreSQL instance defined in the development Docker
compose stack. Skipping at collection time prevents CI failures.
"""

import pytest

# Skip during pytest collection
pytest.skip("Utility script – skip in automated test runs", allow_module_level=True)

# The original diagnostic code is kept below for manual execution when needed.

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