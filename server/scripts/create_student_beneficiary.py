#!/usr/bin/env python
"""Create beneficiary profile for student user."""

from app import create_app
from app.models import User, Beneficiary
from app.extensions import db
from config import DevelopmentConfig
from datetime import datetime

app = create_app(DevelopmentConfig)

with app.app_context():
    # Find student user
    student = User.query.filter_by(email='student@bdc.com').first()
    
    if student:
        print(f"Found student user: {student.email}")
        
        # Check if beneficiary profile already exists
        existing_beneficiary = Beneficiary.query.filter_by(user_id=student.id).first()
        
        if existing_beneficiary:
            print(f"Beneficiary profile already exists with ID: {existing_beneficiary.id}")
        else:
            # Create beneficiary profile
            beneficiary = Beneficiary(
                user_id=student.id,
                tenant_id=1,  # Default tenant
                birth_date=datetime(1995, 1, 1),
                nationality="US",
                notes="Demo student beneficiary profile"
            )
            
            db.session.add(beneficiary)
            db.session.commit()
            
            print(f"Created beneficiary profile for {student.email}")
            print(f"Beneficiary ID: {beneficiary.id}")
            print(f"Identifier: {beneficiary.identifier}")
    else:
        print("Student user not found!")
    
    # List all beneficiaries
    print("\nAll beneficiaries:")
    beneficiaries = Beneficiary.query.all()
    for b in beneficiaries:
        user = User.query.get(b.user_id) if b.user_id else None
        user_email = user.email if user else "No user linked"
        print(f"- {b.first_name} {b.last_name} (ID: {b.id}, Identifier: {b.identifier}, User: {user_email})")