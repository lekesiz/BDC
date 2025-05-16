#!/usr/bin/env python
"""Create admin user."""

from app import create_app
from app.models import User, Tenant
from app.extensions import db
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    # Get first tenant
    tenant = Tenant.query.first()
    if not tenant:
        print("No tenant found, creating one...")
        tenant = Tenant(
            name='BDC',
            slug='bdc',
            email='info@bdc.com',
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
    
    # Create new admin user
    new_admin = User(
        email='test.admin@bdc.com',
        username='testadmin',
        first_name='Test',
        last_name='Admin',
        role='super_admin',
        is_active=True,
        tenant_id=tenant.id
    )
    new_admin.password = 'Test123!'
    
    db.session.add(new_admin)
    db.session.commit()
    
    print(f"Created admin user: {new_admin.email} with password: Test123!")
    
    # Test password
    test_admin = User.query.filter_by(email='test.admin@bdc.com').first()
    if test_admin.verify_password('Test123!'):
        print("Password verification successful!")
    else:
        print("Password verification failed!")