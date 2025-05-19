#!/usr/bin/env python3
"""Test API endpoints with different user roles."""

import requests
import json
from urllib.parse import urljoin

API_BASE = "http://localhost:5001"

# User credentials
USERS = {
    "super_admin": {"email": "admin@bdc.com", "password": "Admin123!"},
    "tenant_admin": {"email": "tenant@bdc.com", "password": "Tenant123!"},
    "trainer": {"email": "trainer@bdc.com", "password": "Trainer123!"},
    "student": {"email": "student@bdc.com", "password": "Student123!"}
}

# API endpoints to test
ENDPOINTS = {
    "GET": [
        "/api/users/me",
        "/api/users?page=1&limit=10",
        "/api/tenants",
        "/api/beneficiaries?page=1&per_page=10",
        "/api/evaluations",
        "/api/appointments",
        "/api/documents",
        "/api/programs",
        "/api/calendars/availability",
        "/api/analytics/dashboard?range=7days",
        "/api/reports/recent",
        "/api/notifications",
        "/api/notifications/unread-count",
        "/api/settings/general",
        "/api/settings/appearance",
        "/api/assessment/templates",
        "/api/tests/sessions"
    ],
    "POST": [
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/refresh"
    ]
}

def login(email, password):
    """Login and get access token."""
    response = requests.post(
        urljoin(API_BASE, "/api/auth/login"),
        json={"email": email, "password": password, "remember_me": False}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed for {email}: {response.status_code} - {response.text}")
        return None

def test_endpoint(method, endpoint, token=None):
    """Test a single endpoint."""
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = urljoin(API_BASE, endpoint)
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json={})
    else:
        response = None
    
    return response

def main():
    print("🧪 BDC API Endpoint Testing")
    print("=" * 50)
    
    # Test each user role
    for role, creds in USERS.items():
        print(f"\n\n📋 Testing with {role.upper()} role")
        print("-" * 50)
        
        # Login
        token = login(creds["email"], creds["password"])
        if not token:
            print(f"❌ Failed to login as {role}")
            continue
        
        print(f"✅ Logged in as {role}")
        
        # Test GET endpoints
        print("\n📥 Testing GET endpoints:")
        for endpoint in ENDPOINTS["GET"]:
            response = test_endpoint("GET", endpoint, token)
            if response:
                status = "✅" if response.status_code in [200, 201] else "❌"
                print(f"  {status} {endpoint} - {response.status_code}")
                if response.status_code not in [200, 201]:
                    print(f"     Error: {response.text[:100]}...")
        
        # Test logout
        print("\n📤 Testing logout:")
        response = test_endpoint("POST", "/api/auth/logout", token)
        if response:
            status = "✅" if response.status_code == 200 else "❌"
            print(f"  {status} /auth/logout - {response.status_code}")
        
        print("\n" + "=" * 50)

def test_single_user(role="super_admin"):
    """Test with a single user role."""
    print(f"\n🧪 Quick test with {role}")
    creds = USERS[role]
    
    # Login
    token = login(creds["email"], creds["password"])
    if not token:
        print(f"❌ Failed to login as {role}")
        return
    
    print(f"✅ Logged in successfully")
    
    # Test a few critical endpoints
    critical_endpoints = [
        "/api/users/me",
        "/api/beneficiaries?page=1&per_page=10",
        "/api/evaluations",
        "/api/analytics/dashboard"
    ]
    
    for endpoint in critical_endpoints:
        response = test_endpoint("GET", endpoint, token)
        if response:
            status = "✅" if response.status_code in [200, 201] else "❌"
            print(f"{status} {endpoint} - {response.status_code}")

if __name__ == "__main__":
    # Run full test
    main()
    
    # Or run a quick test with one user
    # test_single_user("super_admin")