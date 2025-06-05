#!/usr/bin/env python
"""Check passwords for test users."""

from app import create_app
from app.models import User
from config import DevelopmentConfig

from app.utils.logging import logger

app = create_app(DevelopmentConfig)

with app.app_context():
    users = User.query.all()
    logger.info("Existing users:")
    for user in users:
        logger.info(f"Email: {user.email}, Role: {user.role}")
        # Try to verify password
        if user.check_password('password123'):
            logger.info(f"  Password 'password123' works")
        elif user.check_password('admin123'):
            logger.info(f"  Password 'admin123' works")
        else:
            logger.info(f"  Password unknown")