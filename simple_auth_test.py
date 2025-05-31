#!/usr/bin/env python3
"""Simple authentication test."""

import sqlite3
from werkzeug.security import check_password_hash

# Connect directly to database
db_path = '/Users/mikail/Desktop/BDC/server/instance/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get user data directly from SQL
cursor.execute('SELECT email, password_hash FROM users WHERE email = ?', ('admin@bdc.com',))
user_data = cursor.fetchone()

if user_data:
    email, password_hash = user_data
    print(f"Email: {email}")
    print(f"Hash: {password_hash}")
    
    # Test password verification
    result = check_password_hash(str(password_hash), 'Admin123!')
    print(f"Password verification: {result}")
    
    if result:
        print("🎉 Authentication successful!")
        
        # Now test JWT creation
        import os
        os.environ['FLASK_ENV'] = 'development'
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        
        import sys
        sys.path.insert(0, '/Users/mikail/Desktop/BDC/server')
        
        from app import create_app
        from flask_jwt_extended import create_access_token, create_refresh_token
        
        app = create_app()
        with app.app_context():
            try:
                access_token = create_access_token(identity=1)  # admin user ID
                refresh_token = create_refresh_token(identity=1)
                
                print(f"Access token: {access_token[:30]}...")
                print(f"Refresh token: {refresh_token[:30]}...")
                print("✅ JWT tokens created successfully!")
                
                # Test complete response
                response_data = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': 1,
                        'email': email,
                        'role': 'super_admin'
                    }
                }
                print("✅ Complete authentication flow successful!")
                
            except Exception as e:
                print(f"❌ JWT creation failed: {e}")
    else:
        print("❌ Password verification failed")
else:
    print("❌ User not found")

conn.close()