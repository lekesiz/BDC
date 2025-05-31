#!/usr/bin/env python
"""Test API endpoints directly with Flask test client."""

from app import create_app
import json

app = create_app()

with app.app_context():
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        print(f"Health endpoint: {response.status_code} - {response.data.decode()}")
        
        # Test auth debug
        response = client.get('/api/auth/debug')
        print(f"Auth debug: {response.status_code} - {response.data.decode()}")
        
        # Test login endpoint
        login_data = {
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'remember': False
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        print(f"\nLogin endpoint response:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Data: {response.data.decode()}")
        
        if response.status_code == 500:
            # Check Flask logs
            print("\nChecking for errors...")
            # The actual error should be logged to console