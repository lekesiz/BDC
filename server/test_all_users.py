#!/usr/bin/env python3
"""Test all users login."""

import requests
import json

users = [
    ('admin@bdc.com', 'Admin123!'),
    ('tenant@bdc.com', 'Tenant123!'),
    ('trainer@bdc.com', 'Trainer123!'),
    ('student@bdc.com', 'Student123!')
]

for email, password in users:
    print(f"\nTesting {email}...")
    
    try:
        response = requests.post('http://localhost:5001/api/auth/login', 
                               json={'email': email, 'password': password, 'remember_me': False},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print(f"✓ Success: {email}")
            data = response.json()
            if 'access_token' in data:
                print(f"  Token: {data['access_token'][:50]}...")
        else:
            print(f"✗ Failed: {email}")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")