#!/usr/bin/env python3
"""Test backend connection and API endpoints."""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:5001"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_endpoint(method, path, data=None, headers=None, description=""):
    """Test an API endpoint."""
    url = f"{BASE_URL}{path}"
    print(f"\n{BLUE}Testing: {description or path}{RESET}")
    print(f"Method: {method} URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "OPTIONS":
            response = requests.options(url, headers=headers)
        else:
            print(f"{RED}Unsupported method: {method}{RESET}")
            return None
            
        print(f"Status: {response.status_code}")
        
        # Print headers for debugging CORS
        if "Access-Control-Allow-Origin" in response.headers:
            print(f"CORS Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        
        # Try to parse JSON response
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)[:200]}...")
        except:
            print(f"Response: {response.text[:200]}...")
            
        if response.status_code < 400:
            print(f"{GREEN}✓ Success{RESET}")
        else:
            print(f"{RED}✗ Failed{RESET}")
            
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ Connection Error - Backend not running?{RESET}")
        return None
    except Exception as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        return None

def main():
    """Run all tests."""
    print(f"{YELLOW}=== BDC Backend Connection Test ==={RESET}")
    print(f"Testing backend at: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    
    # Test 1: Basic connectivity
    test_endpoint("GET", "/", description="Root endpoint")
    
    # Test 2: Health check
    test_endpoint("GET", "/api/health", description="Health check")
    
    # Test 3: Auth debug endpoint
    test_endpoint("GET", "/api/auth/debug", description="Auth debug info")
    
    # Test 4: CORS preflight
    cors_headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization"
    }
    test_endpoint("OPTIONS", "/api/auth/login", headers=cors_headers, description="CORS preflight test")
    
    # Test 5: Login attempt
    login_data = {
        "email": "admin@bdc.com",
        "password": "Admin123!",
        "remember": True
    }
    login_headers = {
        "Origin": "http://localhost:5173",
        "Content-Type": "application/json"
    }
    response = test_endpoint("POST", "/api/auth/login", data=login_data, headers=login_headers, description="Admin login")
    
    # If login successful, test authenticated endpoint
    if response and response.status_code == 200:
        try:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                # Test authenticated endpoint
                auth_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Origin": "http://localhost:5173"
                }
                test_endpoint("GET", "/api/users/me", headers=auth_headers, description="Get current user")
                test_endpoint("GET", "/api/beneficiaries", headers=auth_headers, description="Get beneficiaries")
        except:
            pass
    
    print(f"\n{YELLOW}=== Test Complete ==={RESET}")

if __name__ == "__main__":
    main()