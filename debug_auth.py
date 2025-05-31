#!/usr/bin/env python3
"""Debug authentication directly."""

import os
import sys
import traceback

# Set environment
os.environ['FLASK_ENV'] = 'development'
# Force the same database path as the server
os.environ['DATABASE_URL'] = 'sqlite:////Users/mikail/Desktop/BDC/server/instance/app.db'

# Add current directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

try:
    from app import create_app
    from app.models import User
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    print("Creating app...")
    app = create_app()
    
    print("Testing authentication logic...")
    with app.app_context():
        # Simulate the authentication request
        email = "admin@bdc.com"
        password = "Admin123!"
        
        print(f"1. Looking up user: {email}")
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print("❌ User not found")
            sys.exit(1)
        
        print(f"2. User found: {user.email}, active: {user.is_active}")
        
        print("3. Verifying password...")
        # Force refresh user from database 
        from app.extensions import db
        db.session.refresh(user)
        
        password_result = user.verify_password(password)
        print(f"   Password verification result: {password_result}")
        
        if not password_result:
            print("❌ Password verification failed")
            print(f"   Tried password: '{password}'")
            print(f"   Hash: {user.password_hash[:50]}...")
            
            # Test direct werkzeug verification
            from werkzeug.security import check_password_hash
            direct_test = check_password_hash(user.password_hash, password)
            print(f"   Direct werkzeug test: {direct_test}")
            
            if not direct_test:
                sys.exit(1)
        
        print("4. Password verified successfully")
        
        print("5. Creating JWT tokens...")
        try:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            print(f"6. ✅ Tokens created successfully!")
            print(f"   Access token: {access_token[:30]}...")
            print(f"   Refresh token: {refresh_token[:30]}...")
            
            # Test the response format
            response_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'tenant_id': user.tenant_id,
                    'is_active': user.is_active
                }
            }
            
            print("7. ✅ Response data prepared successfully!")
            print(f"   User data: {response_data['user']}")
            
        except Exception as jwt_error:
            print(f"❌ JWT creation failed: {jwt_error}")
            traceback.print_exc()
            sys.exit(1)
        
        print("\n🎉 Authentication test completed successfully!")
        
except Exception as e:
    print(f"❌ Authentication test failed: {e}")
    traceback.print_exc()
    sys.exit(1)