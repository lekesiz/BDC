#!/usr/bin/env python3
"""Create all test users."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant

app = create_app()

with app.app_context():
    # Get default tenant
    tenant = Tenant.query.first()
    if not tenant:
        tenant = Tenant(
            name='Default',
            slug='default',
            email='admin@default.com',
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
    
    # Define users
    users = [
        {
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'super_admin'
        },
        {
            'email': 'tenant@bdc.com',
            'password': 'Tenant123!',
            'first_name': 'Tenant',
            'last_name': 'Admin',
            'role': 'tenant_admin'
        },
        {
            'email': 'trainer@bdc.com',
            'password': 'Trainer123!',
            'first_name': 'Trainer',
            'last_name': 'User',
            'role': 'trainer'
        },
        {
            'email': 'student@bdc.com',
            'password': 'Student123!',
            'first_name': 'Student',
            'last_name': 'User',
            'role': 'student'
        }
    ]
    
    # Create or update users
    for user_data in users:
        user = User.query.filter_by(email=user_data['email']).first()
        if not user:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_active=True
            )
            db.session.add(user)
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")
        
        # Set password
        user.password = user_data['password']
        
        # Add tenant if not already assigned
        if hasattr(user, 'tenants') and tenant not in user.tenants:
            user.tenants.append(tenant)
    
    db.session.commit()
    
    # List all users
    users = User.query.all()
    print(f"\n✓ Total users: {len(users)}")
    for user in users:
        print(f"  - {user.email} ({user.role}) - Password verification: {user.verify_password(user.email.split('@')[0].capitalize() + '123!')}")