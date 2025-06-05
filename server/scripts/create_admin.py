#!/usr/bin/env python3
"""Create admin user for testing."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.tenant import Tenant

app = create_app()

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if admin already exists
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        print("Admin user already exists")
    else:
        # Create default tenant if it doesn't exist
        tenant = Tenant.query.filter_by(name='Default').first()
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
            role=UserRole.SUPER_ADMIN,
            tenant_id=tenant.id,
            is_active=True
        )
        admin.set_password('Admin123!')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Created admin user:")
        print(f"Email: admin@bdc.com")
        print(f"Password: Admin123!")
        print(f"Role: {admin.role}")
        
    # List all users
    users = User.query.all()
    print(f"\nTotal users in database: {len(users)}")
    for user in users:
        print(f"- {user.email} ({user.role})")