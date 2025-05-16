#!/usr/bin/env python3
"""Debug user and test login."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant

app = create_app()

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    
    if admin:
        print(f"Admin user details:")
        print(f"- Email: {admin.email}")
        print(f"- Role: {admin.role}")
        print(f"- Is active: {admin.is_active}")
        print(f"- Password hash exists: {bool(admin.password_hash)}")
        print(f"- Tenant count: {len(admin.tenants) if admin.tenants else 0}")
        
        # Check tenant
        if hasattr(admin, 'tenant_id'):
            print(f"- Direct tenant_id: {getattr(admin, 'tenant_id', None)}")
        
        # Test password directly
        test_password = 'Admin123!'
        result = admin.verify_password(test_password)
        print(f"\nPassword verification for '{test_password}': {result}")
        
        # Check related models
        print("\nTenants:")
        for tenant in Tenant.query.all():
            print(f"- {tenant.name} (ID: {tenant.id}, Active: {tenant.is_active})")
            
        # Add tenant if missing
        if not admin.tenants:
            print("\nAdding default tenant to admin...")
            default_tenant = Tenant.query.filter_by(name='Default').first()
            if default_tenant:
                admin.tenants.append(default_tenant)
                db.session.commit()
                print(f"Added tenant: {default_tenant.name}")
        
        # Test auth service directly
        from app.services.auth_service import AuthService
        
        result = AuthService.login('admin@bdc.com', 'Admin123!')
        print(f"\nAuthService login result: {result}")
    else:
        print("Admin user not found!")