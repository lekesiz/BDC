#!/usr/bin/env python3
"""Simple login test."""

import requests
import json

# Configuration
API_URL = "http://localhost:5001/api"

# Test credentials
TEST_EMAIL = "admin@bdc.com"
TEST_PASSWORD = "Admin123!"

print("Testing login...")

# Test login
login_data = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(f"{API_URL}/auth/login", json=login_data, headers=headers)

print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nSuccess! Token: {data.get('access_token', 'N/A')[:50]}...")
else:
    print(f"\nFailed!")