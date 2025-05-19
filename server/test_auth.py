"""Test authentication endpoint."""

import requests
import json

# Test URL
url = "http://localhost:5001/api/auth/login"

# Test data
data = {
    "email": "admin@bdc.com",
    "password": "Admin123!"
}

# Headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Make request
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Content: {response.text}")
    
    if response.status_code == 200:
        print("\nLogin successful!")
        print(f"Response JSON: {response.json()}")
    else:
        print(f"\nLogin failed with status: {response.status_code}")
        print(f"Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to server. Make sure the server is running on port 5001.")
except Exception as e:
    print(f"Error: {e}")