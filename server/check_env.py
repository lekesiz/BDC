#!/usr/bin/env python3
"""Check environment settings."""

import sys
import os
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"Flask Environment: {os.getenv('FLASK_ENV', 'default')}")
    print(f"Debug Mode: {app.config.get('DEBUG')}")
    
    # Check database file
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_uri.startswith('sqlite'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"SQLite database path: {db_path}")
        if os.path.exists(db_path):
            print(f"Database file exists: {os.path.getsize(db_path)} bytes")
        else:
            print("Database file does not exist")
    
    # Create fresh admin user
    from app.models.user import User
    from app.models.tenant import Tenant
    
    # Find existing admin
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        print(f"\nExisting admin password verification: {admin.verify_password('Admin123!')}")
        # Force update password
        admin.password = 'Admin123!'
        db.session.commit()
        print(f"Password updated. New verification: {admin.verify_password('Admin123!')}")
    else:
        print("\nAdmin user not found - creating new one")
        # Create tenant if needed
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(name='Default', code='DEFAULT', is_active=True)
            db.session.add(tenant)
            db.session.commit()
        
        # Create admin user
        admin = User(
            email='admin@bdc.com',
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_active=True
        )
        admin.password = 'Admin123!'
        admin.tenants.append(tenant)
        db.session.add(admin)
        db.session.commit()
        print("Created new admin user")
    
    # Test login again
    from app.services.auth_service import AuthService
    result = AuthService.login('admin@bdc.com', 'Admin123!')
    print(f"\nLogin test result: {'SUCCESS' if result else 'FAILED'}")