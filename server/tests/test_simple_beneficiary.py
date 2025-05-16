#!/usr/bin/env python
"""Test simple beneficiary creation."""

from app import create_app
from config import DevelopmentConfig
import json

app = create_app(DevelopmentConfig)

with app.app_context():
    client = app.test_client()
    
    # Get token
    response = client.post('/api/auth/login', 
                          json={'email': 'test.admin@bdc.com', 'password': 'Test123!'},
                          content_type='application/json')
    
    if response.status_code != 200:
        print("Failed to login")
        exit(1)
    
    token = json.loads(response.data)['access_token']
    
    # Simple beneficiary data
    beneficiary_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+33123456789'
    }
    
    # Create beneficiary
    response = client.post('/api/beneficiaries',
                          json=beneficiary_data,
                          headers={'Authorization': f'Bearer {token}'},
                          content_type='application/json')
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data.decode()}")