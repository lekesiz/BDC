#!/usr/bin/env python
"""Check passwords for test users."""

from app import create_app
from app.models import User
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    users = User.query.all()
    print("Existing users:")
    for user in users:
        print(f"Email: {user.email}, Role: {user.role}")
        # Try to verify password
        if user.check_password('password123'):
            print(f"  Password 'password123' works")
        elif user.check_password('admin123'):
            print(f"  Password 'admin123' works")
        else:
            print(f"  Password unknown")