#!/usr/bin/env python3
"""Comprehensive authentication and CORS test."""

import requests
import json
import sys

base_url = "http://localhost:5001"
headers = {
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:5173'
}

def test_step(description, func):
    """Run a test step and handle errors."""
    print(f"\n{description}...")
    print("-" * 50)
    try:
        result = func()
        if result:
            print("✓ Success")
        return result
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_cors_preflight():
    """Test CORS preflight request."""
    headers = {
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type,Authorization'
    }
    response = requests.options(f"{base_url}/api/auth/login", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"CORS Headers: {dict(response.headers)}")
    return response.status_code == 200

def test_login():
    """Test login endpoint."""
    data = {
        'email': 'admin@bdc.com',
        'password': 'Admin123!'
    }
    response = requests.post(f"{base_url}/api/auth/login", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        tokens = response.json()
        return tokens
    return None

def test_protected_endpoint(token):
    """Test a protected endpoint."""
    auth_headers = headers.copy()
    auth_headers['Authorization'] = f"Bearer {token}"
    
    response = requests.get(f"{base_url}/api/users/me", headers=auth_headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_refresh_token(refresh_token, access_token):
    """Test token refresh."""
    auth_headers = headers.copy()
    auth_headers['Authorization'] = f"Bearer {refresh_token}"
    
    response = requests.post(f"{base_url}/api/auth/refresh", headers=auth_headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_invalid_credentials():
    """Test login with invalid credentials."""
    data = {
        'email': 'admin@bdc.com',
        'password': 'wrongpassword'
    }
    response = requests.post(f"{base_url}/api/auth/login", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 401

def main():
    """Run all tests."""
    print("CORS and Authentication Test Suite")
    print("=" * 50)
    
    # Test 1: CORS preflight
    test_step("Test 1: CORS Preflight", test_cors_preflight)
    
    # Test 2: Login
    tokens = test_step("Test 2: Login", test_login)
    
    if tokens:
        # Test 3: Protected endpoint
        test_step("Test 3: Protected Endpoint", 
                 lambda: test_protected_endpoint(tokens['access_token']))
        
        # Test 4: Refresh token
        test_step("Test 4: Refresh Token", 
                 lambda: test_refresh_token(tokens['refresh_token'], tokens['access_token']))
    
    # Test 5: Invalid credentials
    test_step("Test 5: Invalid Credentials", test_invalid_credentials)
    
    print("\n" + "=" * 50)
    print("Test suite complete.")

if __name__ == "__main__":
    main()