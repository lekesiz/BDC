#!/usr/bin/env python
"""Reset student user password."""

from app import create_app
from app.models import User
from app.extensions import db
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    # Reset student password
    student = User.query.filter_by(email='student@bdc.com').first()
    if student:
        student.password = 'password123'
        db.session.commit()
        print(f"Reset password for {student.email} to: password123")
        
        # Verify password
        if student.verify_password('password123'):
            print("Password verification: SUCCESS")
        else:
            print("Password verification: FAILED")
    else:
        print("Student user not found!")
    
    # List all users
    print("\nAll users:")
    users = User.query.all()
    for user in users:
        print(f"- {user.email} ({user.role})")