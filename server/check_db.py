#!/usr/bin/env python3
"""Check database contents."""

import sys
sys.path.insert(0, '.')

from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    print("Users in database:")
    print("-" * 50)
    
    users = User.query.all()
    for user in users:
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        print(f"Role: {user.role}")
        print(f"Active: {user.is_active}")
        print(f"Can login with Admin123!: {user.verify_password('Admin123!')}")
        print("-" * 50)
    
    print(f"Total users: {len(users)}")
    
    # Check admin specifically
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        print(f"\nAdmin user details:")
        print(f"ID: {admin.id}")
        print(f"Password hash: {admin.password_hash[:50]}...")
        print(f"Created at: {admin.created_at}")
        print(f"Last login: {admin.last_login}")
    else:
        print("\nNo admin user found!")