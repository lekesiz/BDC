#\!/usr/bin/env python3
"""Test all beneficiaries endpoints."""

import requests
import json

# Configuration
API_URL = "http://localhost:5001/api"

# Test credentials
TEST_EMAIL = "admin@bdc.com"
TEST_PASSWORD = "Admin123!"

def get_auth_token():
    """Login and get JWT token."""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_beneficiary_endpoints(token):
    """Test all beneficiary endpoints."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First, get a list of beneficiaries
    response = requests.get(f"{API_URL}/beneficiaries", headers=headers)
    if response.status_code == 200:
        beneficiaries = response.json().get('beneficiaries', [])
        if beneficiaries:
            beneficiary_id = beneficiaries[0]['id']
            print(f"Testing with beneficiary ID: {beneficiary_id}")
        else:
            print("No beneficiaries found")
            return
    else:
        print(f"Failed to get beneficiaries: {response.status_code}")
        return
    
    # Test endpoints
    endpoints = [
        f"/beneficiaries/{beneficiary_id}/evaluations",
        f"/beneficiaries/{beneficiary_id}/sessions", 
        f"/beneficiaries/{beneficiary_id}/progress",
        f"/beneficiaries/{beneficiary_id}/skills",
        f"/beneficiaries/{beneficiary_id}/documents",
        f"/beneficiaries/{beneficiary_id}/trainers",
        f"/beneficiaries/{beneficiary_id}/comparison",
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting GET {endpoint}")
        response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
    
    # Test report download
    print(f"\nTesting GET /beneficiaries/{beneficiary_id}/report")
    response = requests.get(f"{API_URL}/beneficiaries/{beneficiary_id}/report", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response type: {response.headers.get('Content-Type')}")
        print(f"Content length: {len(response.content)} bytes")
    else:
        print(f"Error: {response.text}")

def main():
    """Main test function."""
    print("Starting beneficiaries API test...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to authenticate")
        return
    
    print(f"Got auth token: {token[:20]}...")
    
    # Test endpoints
    test_beneficiary_endpoints(token)
    
    print("\nTest completed\!")

if __name__ == "__main__":
    main()