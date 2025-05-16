#!/usr/bin/env python
"""Direct API test."""

from app import create_app
from app.extensions import db
from app.models import User
from config import DevelopmentConfig
from flask import Flask
import json

app = create_app(DevelopmentConfig)

with app.app_context():
    # Test directly with the Flask test client
    client = app.test_client()
    
    response = client.post('/api/auth/login', 
                          json={'email': 'test.admin@bdc.com', 'password': 'Test123!'},
                          content_type='application/json')
    
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data.decode()}")
    
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Token: {data.get('access_token', '')[:50]}...")
    
    # Also check user directly
    user = User.query.filter_by(email='test.admin@bdc.com').first()
    print(f"\nUser check:")
    print(f"Found: {user is not None}")
    if user:
        print(f"Active: {user.is_active}")
        print(f"Password OK: {user.verify_password('Test123!')}")