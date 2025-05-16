#!/usr/bin/env python3
"""Test /me endpoint with authentication."""

import requests
import json

# First login to get token
login_url = "http://localhost:5001/api/auth/login"
me_url = "http://localhost:5001/api/users/me"

headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173"
}

# Login first
login_data = {
    "email": "admin@bdc.com",
    "password": "Admin123!"
}

print("1. Testing login...")
login_response = requests.post(login_url, json=login_data, headers=headers)
print(f"Status: {login_response.status_code}")

if login_response.status_code == 200:
    tokens = login_response.json()
    access_token = tokens['access_token']
    print(f"Got access token: {access_token[:20]}...")
    
    # Test /me endpoint
    print("\n2. Testing /me endpoint...")
    auth_headers = headers.copy()
    auth_headers['Authorization'] = f"Bearer {access_token}"
    
    me_response = requests.get(me_url, headers=auth_headers)
    print(f"Status: {me_response.status_code}")
    print(f"Response: {json.dumps(me_response.json(), indent=2)}")
    
    # Check CORS headers
    cors_headers = {
        k: v for k, v in me_response.headers.items() 
        if k.lower().startswith('access-control')
    }
    if cors_headers:
        print("\nCORS Headers:")
        for k, v in cors_headers.items():
            print(f"  {k}: {v}")
else:
    print(f"Login failed: {login_response.text}")