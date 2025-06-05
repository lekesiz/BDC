#!/usr/bin/env python3
"""Create a test beneficiary linked to the student user."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.tenant import Tenant

app = create_app()

with app.app_context():
    # Get the student user
    student = User.query.filter_by(email='student@bdc.com').first()
    
    if not student:
        print("Student user not found!")
        exit(1)
    
    # Check if beneficiary already exists
    existing_beneficiary = Beneficiary.query.filter_by(user_id=student.id).first()
    
    if existing_beneficiary:
        print(f"✓ Beneficiary already exists for {student.email}")
        print(f"  ID: {existing_beneficiary.id}")
    else:
        # Get the default tenant
        tenant = Tenant.query.first()
        
        # Create new beneficiary
        beneficiary = Beneficiary(
            user_id=student.id,
            tenant_id=tenant.id,
            phone='+1234567890',
            status='active',
            notes='Test beneficiary for student user',
            category='student',
            city='Test City',
            country='Test Country'
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        print(f"✓ Created beneficiary for {student.email}")
        print(f"  ID: {beneficiary.id}")
    
    # List all beneficiaries
    beneficiaries = Beneficiary.query.all()
    print(f"\n✓ Total beneficiaries: {len(beneficiaries)}")
    for b in beneficiaries:
        user = User.query.get(b.user_id)
        if user:
            print(f"  - {user.email} (Status: {b.status}, User ID: {b.user_id})")