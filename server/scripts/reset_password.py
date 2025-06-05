#!/usr/bin/env python3
"""Reset admin password."""

import sys
sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')

from app import create_app
from app.extensions import db
from app.models.user import User

from app.utils.logging import logger

app = create_app()

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(email='admin@bdc.com').first()
    
    if admin:
        logger.info(f"Found admin user: {admin.email}")
        logger.info(f"Current role: {admin.role}")
        logger.info(f"Is active: {admin.is_active}")
        
        # Reset password
        admin.password = 'Admin123!'
        db.session.commit()
        
        logger.info("\nPassword reset successfully!")
        logger.info("New password: Admin123!")
        
        # Verify password
        if admin.verify_password('Admin123!'):
            logger.info("Password verification: SUCCESS")
        else:
            logger.info("Password verification: FAILED")
    else:
        logger.info("Admin user not found!")