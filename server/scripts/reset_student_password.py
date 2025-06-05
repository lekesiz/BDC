#!/usr/bin/env python
"""Reset student user password."""

from app import create_app
from app.models import User
from app.extensions import db
from config import DevelopmentConfig

from app.utils.logging import logger

app = create_app(DevelopmentConfig)

with app.app_context():
    # Reset student password
    student = User.query.filter_by(email='student@bdc.com').first()
    if student:
        student.password = 'password123'
        db.session.commit()
        logger.info(f"Reset password for {student.email} to: password123")
        
        # Verify password
        if student.verify_password('password123'):
            logger.info("Password verification: SUCCESS")
        else:
            logger.info("Password verification: FAILED")
    else:
        logger.info("Student user not found!")
    
    # List all users
    logger.info("\nAll users:")
    users = User.query.all()
    for user in users:
        logger.info(f"- {user.email} ({user.role})")