#!/usr/bin/env python3
"""Test notification endpoint."""

import requests
import json

# First login to get token
login_url = "http://localhost:5001/api/auth/login"
notification_url = "http://localhost:5001/api/notifications/unread-count"

login_data = {
    "email": "admin@bdc.com",
    "password": "Admin123!"
}

print("1. Logging in...")
login_response = requests.post(login_url, json=login_data)

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"   ✓ Login successful, got token: {token[:20]}...")
    
    print("\n2. Testing notification endpoint...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(notification_url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Error: {response.text}")
else:
    print(f"   ✗ Login failed: {login_response.text}")