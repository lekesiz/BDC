#!/usr/bin/env python3
"""Check database contents."""

import sys
sys.path.insert(0, '.')

from app import create_app
from app.models.user import User

from app.utils.logging import logger

app = create_app()

with app.app_context():
    logger.info("Users in database:")
    logger.info("-" * 50)
    
    users = User.query.all()
    for user in users:
        logger.info(f"Email: {user.email}")
        logger.info(f"Username: {user.username}")
        logger.info(f"Role: {user.role}")
        logger.info(f"Active: {user.is_active}")
        logger.info(f"Can login with Admin123!: {user.verify_password('Admin123!')}")
        logger.info("-" * 50)
    
    logger.info(f"Total users: {len(users)}")
    
    # Check admin specifically
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        logger.info(f"\nAdmin user details:")
        logger.info(f"ID: {admin.id}")
        logger.info(f"Password hash: {admin.password_hash[:50]}...")
        logger.info(f"Created at: {admin.created_at}")
        logger.info(f"Last login: {admin.last_login}")
    else:
        logger.info("\nNo admin user found!")