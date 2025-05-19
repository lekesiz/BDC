#!/usr/bin/env python3
"""UI Test Helper - Browser automation script for BDC UI testing."""

import webbrowser
import time
import subprocess
import os

# Test URLs
BASE_URL = "http://localhost:5173"
URLS = {
    "login": f"{BASE_URL}/login",
    "dashboard": f"{BASE_URL}/dashboard",
    "portal": f"{BASE_URL}/portal",
    "test_auth": f"{BASE_URL}/test-auth.html",
    "users": f"{BASE_URL}/users",
    "beneficiaries": f"{BASE_URL}/beneficiaries",
    "evaluations": f"{BASE_URL}/evaluations",
    "documents": f"{BASE_URL}/documents",
    "settings": f"{BASE_URL}/settings"
}

# User credentials
USERS = {
    "super_admin": {
        "email": "admin@bdc.com",
        "password": "Admin123!",
        "expected_redirect": "/dashboard",
        "role": "super_admin"
    },
    "tenant_admin": {
        "email": "tenant@bdc.com",
        "password": "Tenant123!",
        "expected_redirect": "/dashboard",
        "role": "tenant_admin"
    },
    "trainer": {
        "email": "trainer@bdc.com",
        "password": "Trainer123!",
        "expected_redirect": "/dashboard",
        "role": "trainer"
    },
    "student": {
        "email": "student@bdc.com",
        "password": "Student123!",
        "expected_redirect": "/portal",
        "role": "student"
    }
}

def open_url(url):
    """Open URL in default browser."""
    print(f"Opening: {url}")
    webbrowser.open(url)
    time.sleep(2)  # Wait for page to load

def test_login_flow():
    """Test login flow for all users."""
    print("🧪 Starting UI Login Tests")
    print("=" * 50)
    
    for user_type, creds in USERS.items():
        print(f"\n📋 Testing {user_type.upper()}")
        print(f"URL: {URLS['login']}")
        print(f"Credentials: {creds['email']} / {creds['password']}")
        print(f"Expected redirect: {creds['expected_redirect']}")
        print("-" * 30)
        
        # Open login page
        open_url(URLS['login'])
        
        print("Steps to test manually:")
        print(f"1. Enter email: {creds['email']}")
        print(f"2. Enter password: {creds['password']}")
        print("3. Click Login button")
        print("4. Verify redirect to: " + BASE_URL + creds['expected_redirect'])
        print("5. Check visible menu items for role: " + creds['role'])
        print("6. Test logout functionality")
        
        input("\nPress Enter after completing this test...")
        print("✓ Test completed for " + user_type)

def test_protected_routes():
    """Test access to protected routes."""
    print("\n🔒 Testing Protected Routes")
    print("=" * 50)
    
    protected_routes = [
        ("/users", ["super_admin", "tenant_admin"]),
        ("/tenants", ["super_admin"]),
        ("/beneficiaries", ["super_admin", "tenant_admin", "trainer"]),
        ("/admin", ["super_admin"])
    ]
    
    for route, allowed_roles in protected_routes:
        print(f"\nRoute: {route}")
        print(f"Allowed roles: {', '.join(allowed_roles)}")
        print("Test by logging in with different roles and accessing this route")
        print("Expected: 403 or redirect for unauthorized roles")

def generate_test_report():
    """Generate a test report template."""
    report_content = """# UI Test Report

## Test Date: {date}

### Test Environment
- Frontend: http://localhost:5173
- Backend: http://localhost:5001
- Browser: {browser}

### Test Results

#### 1. Super Admin Login
- [ ] Login successful
- [ ] Redirected to /dashboard
- [ ] All menu items visible
- [ ] Can access all routes
- [ ] Logout works

#### 2. Tenant Admin Login
- [ ] Login successful
- [ ] Redirected to /dashboard
- [ ] Correct menu items visible
- [ ] Cannot access /tenants
- [ ] Logout works

#### 3. Trainer Login
- [ ] Login successful
- [ ] Redirected to /dashboard
- [ ] Limited menu items visible
- [ ] Cannot access /users or /tenants
- [ ] Logout works

#### 4. Student Login
- [ ] Login successful
- [ ] Redirected to /portal
- [ ] Student menu items visible
- [ ] Cannot access admin routes
- [ ] Logout works

### Issues Found
1. 
2. 
3. 

### Screenshots
- Login page: 
- Dashboard (Super Admin): 
- Dashboard (Student): 
- Error messages: 

### Notes
"""
    
    filename = "UI_TEST_REPORT_TEMPLATE.md"
    with open(filename, 'w') as f:
        f.write(report_content.format(
            date=time.strftime("%Y-%m-%d"),
            browser="Chrome/Firefox/Safari"
        ))
    
    print(f"\n📝 Test report template created: {filename}")

def main():
    """Main test runner."""
    print("🚀 BDC UI Test Helper")
    print("This script helps you test the BDC UI manually")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Test login flow for all users")
        print("2. Test protected routes")
        print("3. Open specific page")
        print("4. Generate test report template")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == "1":
            test_login_flow()
        elif choice == "2":
            test_protected_routes()
        elif choice == "3":
            print("\nAvailable pages:")
            for name, url in URLS.items():
                print(f"- {name}: {url}")
            page = input("\nEnter page name: ")
            if page in URLS:
                open_url(URLS[page])
            else:
                print("Invalid page name")
        elif choice == "4":
            generate_test_report()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()