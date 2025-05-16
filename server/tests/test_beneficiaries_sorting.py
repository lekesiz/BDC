#!/usr/bin/env python
"""Test beneficiaries endpoint with sorting."""

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
    
    # Test with sorting parameters
    params = {
        'page': 1,
        'per_page': 10,
        'sort_by': 'created_at',
        'sort_dir': 'desc'
    }
    
    response = client.get('/api/beneficiaries',
                         query_string=params,
                         headers={'Authorization': f'Bearer {token}'})
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data.decode()}")