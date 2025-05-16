#!/usr/bin/env python3
"""Comprehensive test all beneficiaries endpoints."""

import requests
import json
import datetime

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

def create_test_beneficiary(token):
    """Create a test beneficiary."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First create a user for the beneficiary
    user_data = {
        "email": f"test.beneficiary.{datetime.datetime.now().timestamp()}@example.com",
        "password": "Pass123!",
        "confirm_password": "Pass123!",
        "first_name": "Test",
        "last_name": "Beneficiary",
        "role": "student"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=user_data, headers=headers)
    print(f"Register response: {response.status_code}")
    print(f"Register data: {response.text}")
    if response.status_code not in [200, 201]:
        print(f"Failed to create user: {response.status_code}")
        return None
    
    resp_json = response.json()
    user_id = resp_json.get('user', {}).get('id') or resp_json.get('id')
    
    # Create beneficiary profile
    beneficiary_data = {
        "email": user_data["email"],
        "first_name": user_data["first_name"],
        "last_name": user_data["last_name"],
        "phone": "+1234567890",
        "address": "123 Test St",
        "city": "Test City",
        "country": "USA",
        "birth_date": "1990-01-01",
        "gender": "male",
        "profession": "Developer",
        "company": "Test Company",
        "education_level": "Bachelor's Degree",
        "category": "Technology",
        "bio": "Test bio",
        "goals": "Test goals"
    }
    
    response = requests.post(f"{API_URL}/beneficiaries", json=beneficiary_data, headers=headers)
    print(f"Create beneficiary response: {response.status_code}")
    print(f"Create beneficiary data: {response.text}")
    if response.status_code == 201:
        resp_json = response.json()
        return resp_json.get('beneficiary', {}).get('id') or resp_json.get('id')
    else:
        print(f"Failed to create beneficiary")
        return None

def test_beneficiary_endpoints(token, beneficiary_id):
    """Test all beneficiary endpoints."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting with beneficiary ID: {beneficiary_id}")
    
    # Test individual endpoints
    endpoints = [
        (f"/beneficiaries/{beneficiary_id}", "GET"),
        (f"/beneficiaries/{beneficiary_id}/evaluations", "GET"),
        (f"/beneficiaries/{beneficiary_id}/sessions", "GET"),
        (f"/beneficiaries/{beneficiary_id}/progress", "GET"),
        (f"/beneficiaries/{beneficiary_id}/skills", "GET"),
        (f"/beneficiaries/{beneficiary_id}/documents", "GET"),
        (f"/beneficiaries/{beneficiary_id}/trainers", "GET"),
        (f"/beneficiaries/{beneficiary_id}/comparison", "GET"),
    ]
    
    for endpoint, method in endpoints:
        print(f"\nTesting {method} {endpoint}")
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print(f"Error: {response.text}")
    
    # Test trainer assignment
    print(f"\nTesting POST /beneficiaries/{beneficiary_id}/assign-trainer")
    trainer_data = {"trainer_id": 1}  # Assuming admin user is ID 1
    response = requests.post(f"{API_URL}/beneficiaries/{beneficiary_id}/assign-trainer", 
                           json=trainer_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
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
        
    # Test file upload (profile picture)
    print(f"\nTesting POST /beneficiaries/{beneficiary_id}/profile-picture")
    files = {
        'file': ('test.jpg', b'fake image content', 'image/jpeg')
    }
    # Remove Content-Type header for multipart/form-data
    upload_headers = headers.copy()
    del upload_headers["Content-Type"]
    response = requests.post(f"{API_URL}/beneficiaries/{beneficiary_id}/profile-picture", 
                           headers=upload_headers, files=files)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Test update
    print(f"\nTesting PUT /beneficiaries/{beneficiary_id}")
    update_data = {"goals": "Updated test goals"}
    response = requests.put(f"{API_URL}/beneficiaries/{beneficiary_id}", 
                          json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Test list with pagination
    print("\nTesting GET /beneficiaries with pagination")
    response = requests.get(f"{API_URL}/beneficiaries?page=1&per_page=10", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total beneficiaries: {data.get('total')}")
        print(f"Page count: {data.get('pages')}")
    else:
        print(f"Error: {response.text}")

def test_error_cases(token):
    """Test error cases."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n=== Testing Error Cases ===")
    
    # Test non-existent beneficiary
    print("\nTesting GET /beneficiaries/99999 (non-existent)")
    response = requests.get(f"{API_URL}/beneficiaries/99999", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test invalid data
    print("\nTesting POST /beneficiaries with invalid data")
    invalid_data = {"email": "invalid-email"}
    response = requests.post(f"{API_URL}/beneficiaries", json=invalid_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def main():
    """Main test function."""
    print("Starting comprehensive beneficiaries API test...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to authenticate")
        return
    
    print(f"Got auth token: {token[:20]}...")
    
    # Create test beneficiary
    beneficiary_id = create_test_beneficiary(token)
    if not beneficiary_id:
        print("Failed to create test beneficiary")
        return
    
    # Test all endpoints
    test_beneficiary_endpoints(token, beneficiary_id)
    
    # Test error cases
    test_error_cases(token)
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    main()