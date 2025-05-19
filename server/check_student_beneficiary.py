#!/usr/bin/env python
"""Check student beneficiary profile."""

from app import create_app
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.extensions import db

app = create_app()

with app.app_context():
    # Find student user
    student = User.query.filter_by(email='student@bdc.com').first()
    
    if student:
        print(f"Found student user:")
        print(f"  ID: {student.id}")
        print(f"  Email: {student.email}")
        print(f"  Role: {student.role}")
        
        # Check beneficiary profile
        beneficiary = Beneficiary.query.filter_by(user_id=student.id).first()
        
        if beneficiary:
            print(f"\nFound beneficiary profile:")
            print(f"  Beneficiary ID: {beneficiary.id}")
            print(f"  User ID: {beneficiary.user_id}")
            print(f"  Tenant ID: {beneficiary.tenant_id}")
            print(f"  Status: {beneficiary.status}")
            print(f"  First Name: {beneficiary.first_name}")
            print(f"  Last Name: {beneficiary.last_name}")
        else:
            print("\nNo beneficiary profile found!")
    else:
        print("Student user not found!")
    
    # List all beneficiaries
    print("\nAll beneficiaries:")
    beneficiaries = Beneficiary.query.all()
    for b in beneficiaries:
        user = User.query.get(b.user_id) if b.user_id else None
        print(f"- ID: {b.id}, User ID: {b.user_id}, Email: {user.email if user else 'N/A'}")