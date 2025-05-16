#!/usr/bin/env python3
"""Test login endpoint."""

import requests
import json

url = "http://localhost:5001/api/auth/login"
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173"
}

data = {
    "email": "admin@bdc.com",
    "password": "Admin123!"
}

print(f"Testing login to {url}")
print(f"Payload: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Check CORS headers
    cors_headers = {
        k: v for k, v in response.headers.items() 
        if k.lower().startswith('access-control')
    }
    if cors_headers:
        print("\nCORS Headers:")
        for k, v in cors_headers.items():
            print(f"  {k}: {v}")
            
except Exception as e:
    print(f"Error: {str(e)}")