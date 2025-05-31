#!/usr/bin/env python3
import requests
import json

# Test 1: Direct Login with requests
print("=== Test 1: Direct Login ===")
try:
    response = requests.post(
        'http://localhost:5001/api/auth/login',
        json={
            'email': 'admin@bdc.com',
            'password': 'Admin123!',
            'remember': False
        },
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("✓ Login successful!")
        if 'access_token' in response.json():
            print("✓ Access token received")
    else:
        print("✗ Login failed")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== Test 2: Check CORS headers ===")
try:
    response = requests.options(
        'http://localhost:5001/api/auth/login',
        headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        }
    )
    print(f"Status Code: {response.status_code}")
    print("CORS Headers:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"  {header}: {value}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== Test 3: Check server health ===")
try:
    response = requests.get('http://localhost:5001/api/health')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"✗ Error: {e}")