#!/usr/bin/env python
"""Check student beneficiary profile."""

from app import create_app
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.extensions import db

from app.utils.logging import logger

app = create_app()

with app.app_context():
    # Find student user
    student = User.query.filter_by(email='student@bdc.com').first()
    
    if student:
        logger.info(f"Found student user:")
        logger.info(f"  ID: {student.id}")
        logger.info(f"  Email: {student.email}")
        logger.info(f"  Role: {student.role}")
        
        # Check beneficiary profile
        beneficiary = Beneficiary.query.filter_by(user_id=student.id).first()
        
        if beneficiary:
            logger.info(f"\nFound beneficiary profile:")
            logger.info(f"  Beneficiary ID: {beneficiary.id}")
            logger.info(f"  User ID: {beneficiary.user_id}")
            logger.info(f"  Tenant ID: {beneficiary.tenant_id}")
            logger.info(f"  Status: {beneficiary.status}")
            logger.info(f"  First Name: {beneficiary.first_name}")
            logger.info(f"  Last Name: {beneficiary.last_name}")
        else:
            logger.info("\nNo beneficiary profile found!")
    else:
        logger.info("Student user not found!")
    
    # List all beneficiaries
    logger.info("\nAll beneficiaries:")
    beneficiaries = Beneficiary.query.all()
    for b in beneficiaries:
        user = User.query.get(b.user_id) if b.user_id else None
        logger.info(f"- ID: {b.id}, User ID: {b.user_id}, Email: {user.email if user else 'N/A'}")