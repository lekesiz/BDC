#!/usr/bin/env python3
"""Simple auth test to debug dependency injection issues"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.app_factory import ApplicationFactory
from app.core.improved_container import get_auth_service

def test_auth_service():
    """Test auth service creation"""
    try:
        print("🔍 Testing auth service creation...")
        
        # Create app
        app_factory = ApplicationFactory()
        app = app_factory.create_application()
        
        with app.app_context():
            print("✅ App context created")
            
            # Test auth service
            auth_service = get_auth_service()
            print(f"✅ Auth service created: {type(auth_service)}")
            
            # Test login
            result = auth_service.login(
                email='admin@bdc.com',
                password='Admin123!',
                remember=False
            )
            
            if result:
                print(f"✅ Login successful: {result.get('user', {}).get('email')}")
            else:
                print("❌ Login failed")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_service()