#!/usr/bin/env python
"""Debug auth issue."""

from app import create_app
from app.models import User
from app.services.auth_service import AuthService
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    # Direct DB query and password test
    email = 'test.admin@bdc.com'
    password = 'Test123!'
    
    print(f"Testing login with: {email} / {password}")
    
    # Direct user check
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"User found: {user.email}")
        print(f"Is active: {user.is_active}")
        print(f"Password verification: {user.verify_password(password)}")
        print(f"Password hash: {user.password_hash[:50]}...")
    else:
        print("User not found")
    
    # AuthService test
    result = AuthService.login(email, password)
    print(f"AuthService result: {result is not None}")
    
    # Test API directly
    import requests
    response = requests.post('http://localhost:5001/api/auth/login', 
                           json={'email': email, 'password': password})
    print(f"API response: {response.status_code}")
    print(f"API data: {response.text}")