#!/usr/bin/env python
"""Test GET beneficiaries directly."""

from app import create_app
from app.models import User
from config import DevelopmentConfig
import json

app = create_app(DevelopmentConfig)

with app.app_context():
    client = app.test_client()
    
    # Login with admin@bdc.com 
    login_response = client.post('/api/auth/login', 
                               json={'email': 'admin@bdc.com', 'password': 'Admin123!'},
                               content_type='application/json')
    
    if login_response.status_code == 200:
        token = json.loads(login_response.data)['access_token']
        
        # Test same parameters as frontend
        params = {
            "page": 1,
            "per_page": 10,
            "sort_by": "created_at",
            "sort_dir": "desc"
        }
        
        response = client.get('/api/beneficiaries',
                            query_string=params,
                            headers={'Authorization': f'Bearer {token}'})
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.data.decode()}")
        else:
            data = json.loads(response.data)
            print(f"Items: {len(data.get('items', []))}")
    else:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.data.decode())
    
    # Also test user ID 1 directly
    user = User.query.get(1)
    if user:
        print(f"\nUser ID 1: {user.email}, Role: {user.role}")
        print(f"Has tenants: {len(user.tenants) if user.tenants else 0}")
        if user.tenants:
            for tenant in user.tenants:
                print(f"  Tenant: {tenant.name}")