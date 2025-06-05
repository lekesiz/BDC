#!/usr/bin/env python3
"""Fix user roles in database"""

from run_local import app, db, User

from app.utils.logging import logger

with app.app_context():
    # Delete existing database
    db.drop_all()
    
    # Create new database
    db.create_all()
    
    # Create users with correct roles
    users = [
        {
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'role': 'super_admin',  # Changed from 'admin' to 'super_admin'
            'first_name': 'Admin',
            'last_name': 'User'
        },
        {
            'email': 'student@bdc.com',
            'password': 'Student123!',
            'role': 'student',
            'first_name': 'Student',  
            'last_name': 'User'
        },
        {
            'email': 'trainer@bdc.com',
            'password': 'Trainer123!',
            'role': 'trainer',
            'first_name': 'Trainer',
            'last_name': 'User'
        }
    ]
    
    for user_data in users:
        user = User(
            email=user_data['email'],
            role=user_data['role'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
    
    db.session.commit()
    logger.info("✅ Users created with correct roles:")
    
    # Verify
    all_users = User.query.all()
    for u in all_users:
        logger.info(f"   {u.email} - Role: {u.role}")