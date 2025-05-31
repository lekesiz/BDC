#\!/usr/bin/env python
"""Fix admin password for development."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def fix_admin_password():
    """Reset admin password to Admin123\!"""
    app = create_app()
    
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='admin@bdc.com').first()
        
        if not admin:
            print("❌ Admin user not found\!")
            return False
            
        # Update password
        admin.password_hash = generate_password_hash('Admin123\!')
        db.session.commit()
        
        # Verify it worked
        if admin.verify_password('Admin123\!'):
            print("✅ Admin password successfully reset to: Admin123\!")
            print("📧 Email: admin@bdc.com")
            return True
        else:
            print("❌ Password verification failed\!")
            return False

if __name__ == '__main__':
    fix_admin_password()
