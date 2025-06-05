#!/usr/bin/env python3
"""Initialize database with admin user."""

import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant

from app.utils.logging import logger

# Create the app
app = create_app()

# Initialize database within app context
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check for admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    
    if not admin:
        logger.info("Creating admin user...")
        
        # Create default tenant
        tenant = Tenant.query.filter_by(name='Default').first()
        if not tenant:
            tenant = Tenant(
                name='Default',
                code='DEFAULT',  # This might fail if the column doesn't exist
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            logger.info("Created default tenant")
        
        # Create admin user
        admin = User(
            email='admin@bdc.com',
            first_name='Admin',
            last_name='User',
            role='super_admin',
            is_active=True
        )
        admin.password = 'Admin123!'
        
        # Add tenant relationship
        if hasattr(admin, 'tenants'):
            admin.tenants.append(tenant)
        
        db.session.add(admin)
        db.session.commit()
        logger.info("Created admin user successfully")
    else:
        logger.info("Admin user already exists")
    
    # Always reset the password to ensure it's correct
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        admin.password = 'Admin123!'
        db.session.commit()
        logger.info(f"Password reset for admin user")
        
        # Verify it works
        if admin.verify_password('Admin123!'):
            logger.info("Password verification successful")
        else:
            logger.info("WARNING: Password verification failed!")
    
    # List all users
    users = User.query.all()
    logger.info(f"\nTotal users in database: {len(users)}")
    for user in users:
        logger.info(f"- {user.email} ({user.role}, active: {user.is_active})")