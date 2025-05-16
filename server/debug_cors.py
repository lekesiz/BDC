#!/usr/bin/env python3
"""Debug CORS and authentication issues."""

import requests
import sys

# Test different endpoints
base_url = "http://localhost:5001"

print("Testing CORS and Authentication...")
print("=" * 50)

# Test health check
print("\n1. Testing health check...")
try:
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test CORS endpoint
print("\n2. Testing CORS...")
try:
    headers = {
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    response = requests.options(f"{base_url}/api/auth/login", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
except Exception as e:
    print(f"Error: {e}")

# Test login
print("\n3. Testing login...")
try:
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5173'
    }
    data = {
        'email': 'admin@bdc.com',
        'password': 'Admin123!'
    }
    response = requests.post(f"{base_url}/api/auth/login", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"CORS Headers: {response.headers.get('Access-Control-Allow-Origin')}")
    
    if response.status_code == 200:
        tokens = response.json()
        print(f"\nAccess Token: {tokens.get('access_token')[:50]}...")
        
        # Test protected route
        print("\n4. Testing protected route...")
        auth_headers = {
            'Authorization': f"Bearer {tokens.get('access_token')}",
            'Origin': 'http://localhost:5173'
        }
        response = requests.get(f"{base_url}/api/users/me", headers=auth_headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Debug complete.")