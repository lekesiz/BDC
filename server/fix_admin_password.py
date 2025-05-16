#!/usr/bin/env python
"""Fix admin password."""

from app import create_app
from app.models import User
from app.extensions import db
from config import DevelopmentConfig
from werkzeug.security import generate_password_hash

app = create_app(DevelopmentConfig)

with app.app_context():
    # Reset admin password
    admin = User.query.filter_by(email='admin@bdc.com').first()
    if admin:
        # Directly set the password hash
        admin.password_hash = generate_password_hash('admin123')
        db.session.commit()
        print(f"Fixed password for {admin.email}")
        
        # Test it
        if admin.verify_password('admin123'):
            print("Password verification successful!")
        else:
            print("Password verification failed!")
    else:
        print("Admin user not found")