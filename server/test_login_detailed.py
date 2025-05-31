#!/usr/bin/env python
"""Test login endpoint step by step."""

from app import create_app
from app.schemas.auth import LoginSchema
from marshmallow import ValidationError

app = create_app()

with app.app_context():
    # Test schema validation
    schema = LoginSchema()
    test_data = {
        'email': 'admin@bdc.com',
        'password': 'Admin123!',
        'remember': False
    }
    
    try:
        validated_data = schema.load(test_data)
        print(f"Schema validation successful: {validated_data}")
    except ValidationError as e:
        print(f"Schema validation error: {e.messages}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
    # Test AuthService
    try:
        from app.services import AuthService
        from app.models import User
        
        # Check user exists
        user = User.query.filter_by(email='admin@bdc.com').first()
        print(f"User found: {user is not None}")
        if user:
            print(f"User role: {user.role}")
            print(f"User active: {user.is_active}")
            print(f"Password valid: {user.verify_password('Admin123!')}")
            
        # Test login
        result = AuthService.login('admin@bdc.com', 'Admin123!', False)
        print(f"AuthService.login result: {result is not None}")
        
    except Exception as e:
        print(f"AuthService error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()