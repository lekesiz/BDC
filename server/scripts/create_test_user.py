#!/usr/bin/env python
"""Create test user for beneficiary testing."""

from app import create_app
from app.models import User, Tenant
from app.extensions import db
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    # Check if tenant exists
    tenant = Tenant.query.first()
    if not tenant:
        tenant = Tenant(
            name='Test Tenant',
            slug='test-tenant',
            email='test@tenant.com',
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
        print(f"Created tenant: {tenant.name}")
    
    # Create super admin user
    admin_email = 'admin@example.com'
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin = User(
            username='admin',
            email=admin_email,
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_active=True,
            tenant_id=tenant.id
        )
        admin.password = 'admin123'
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user: {admin_email} with password: admin123")
    else:
        print(f"Admin user already exists: {admin_email}")
    
    # Create tenant admin user
    tenant_admin_email = 'tenant.admin@example.com'
    existing_tenant_admin = User.query.filter_by(email=tenant_admin_email).first()
    
    if not existing_tenant_admin:
        tenant_admin = User(
            username='tenant_admin',
            email=tenant_admin_email,
            first_name='Tenant',
            last_name='Admin',
            role='tenant_admin',
            is_active=True,
            tenant_id=tenant.id
        )
        tenant_admin.password = 'admin123'
        db.session.add(tenant_admin)
        db.session.commit()
        print(f"Created tenant admin user: {tenant_admin_email} with password: admin123")
    else:
        print(f"Tenant admin user already exists: {tenant_admin_email}")