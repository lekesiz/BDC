#!/usr/bin/env python3
"""Create test data for beneficiaries testing."""

from app import create_app, db
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.tenant import Tenant
from datetime import datetime

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email="admin@bdc.com").first()
    if admin:
        # Update password
        admin.password = "Admin123!"
        db.session.commit()
        print(f"Updated password for {admin.email}")
    else:
        # Create super admin
        admin = User(
            email="admin@bdc.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            role="super_admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.password = "Admin123!"
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user: {admin.email}")

    # Check if we have a beneficiary
    beneficiary = Beneficiary.query.first()
    if not beneficiary:
        # First create a user for the beneficiary
        ben_user = User(
            email="test.beneficiary@example.com",
            username="testbeneficiary",
            first_name="Test",
            last_name="Beneficiary",
            role="student",
            is_active=True,
            created_at=datetime.utcnow()
        )
        ben_user.password = "Pass123!"
        db.session.add(ben_user)
        db.session.commit()
        
        # Get default tenant
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(
                name="Default Tenant",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(tenant)
            db.session.commit()
        
        # Create beneficiary
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            phone="+1234567890",
            address="123 Test St",
            city="Test City",
            country="Test Country",
            date_of_birth=datetime(1990, 1, 1),
            created_at=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        print(f"Created test beneficiary for user: {ben_user.email}")
    
    print("Test data creation complete!")