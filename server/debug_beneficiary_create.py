#!/usr/bin/env python
"""Debug beneficiary creation with detailed logging."""

from app import create_app
from app.models import User, Tenant, Beneficiary
from app.services.beneficiary_service import BeneficiaryService
from app.extensions import db
from config import DevelopmentConfig
import json

app = create_app(DevelopmentConfig)

with app.app_context():
    # Simple test data
    user_data = {
        'email': 'test.beneficiary2@example.com',
        'password': 'Test123!',
        'first_name': 'Test',
        'last_name': 'Beneficiary'
    }
    
    beneficiary_data = {
        'tenant_id': 1,  # Using the default tenant
        'phone': '+33123456789'
    }
    
    print("Testing direct service call...")
    
    try:
        beneficiary = BeneficiaryService.create_beneficiary(user_data, beneficiary_data)
        if beneficiary:
            print(f"Success! Created beneficiary ID: {beneficiary.id}")
        else:
            print("Service returned None")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check for existing user
    existing_user = User.query.filter_by(email=user_data['email']).first()
    if existing_user:
        print(f"\nExisting user found: {existing_user.email}")
        print(f"User tenants count: {len(existing_user.tenants) if existing_user.tenants else 0}")
        
    # Check tenants
    print("\nAvailable tenants:")
    tenants = Tenant.query.all()
    for tenant in tenants:
        print(f"ID: {tenant.id}, Name: {tenant.name}")