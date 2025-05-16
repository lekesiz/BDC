#!/usr/bin/env python3
"""Test full authentication flow from client to server."""

import requests
import json
import time

def test_direct_api():
    """Test direct API connection."""
    print("1. Testing direct API connection...")
    
    url = "http://localhost:5001/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:5173"
    }
    data = {
        "email": "admin@bdc.com",
        "password": "Admin123!"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"   API Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ API is accessible")
            return True
        else:
            print(f"   ✗ API error: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ API connection error: {e}")
        return False

def test_client_page():
    """Test client page is accessible."""
    print("\n2. Testing client page...")
    
    try:
        response = requests.get("http://localhost:5173/test-auth")
        print(f"   Client Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Client page is accessible")
            return True
        else:
            print(f"   ✗ Client error: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Client connection error: {e}")
        return False

def test_cors_preflight():
    """Test CORS preflight request."""
    print("\n3. Testing CORS preflight...")
    
    url = "http://localhost:5001/api/auth/login"
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization"
    }
    
    try:
        response = requests.options(url, headers=headers)
        print(f"   Preflight Status: {response.status_code}")
        
        cors_headers = {
            k: v for k, v in response.headers.items() 
            if k.lower().startswith('access-control')
        }
        
        if cors_headers:
            print("   CORS Headers:")
            for k, v in cors_headers.items():
                print(f"     {k}: {v}")
            return True
        else:
            print("   ✗ No CORS headers found")
            return False
            
    except Exception as e:
        print(f"   ✗ Preflight error: {e}")
        return False

def test_browser_flow():
    """Test login flow in browser."""
    print("\n4. Testing browser login flow...")
    
    # Create a simple HTML file to test
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BDC Login Test</title>
    </head>
    <body>
        <h1>BDC Login Test</h1>
        <div id="status">Not logged in</div>
        <button id="login">Login</button>
        <div id="error"></div>
        
        <script>
            document.getElementById('login').addEventListener('click', async () => {
                try {
                    const response = await fetch('http://localhost:5001/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Origin': 'http://localhost:5173'
                        },
                        credentials: 'include',
                        body: JSON.stringify({
                            email: 'admin@bdc.com',
                            password: 'Admin123!'
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        document.getElementById('status').textContent = 'Logged in as: ' + data.user.email;
                        document.getElementById('error').textContent = '';
                    } else {
                        const error = await response.text();
                        document.getElementById('error').textContent = 'Error: ' + error;
                    }
                } catch (err) {
                    document.getElementById('error').textContent = 'Network error: ' + err.message;
                }
            });
        </script>
    </body>
    </html>
    '''
    
    with open('/tmp/bdc_test.html', 'w') as f:
        f.write(html_content)
    
    print("   ✓ Test page created at /tmp/bdc_test.html")
    print("   Open file:///tmp/bdc_test.html in your browser to test")
    
    return True

if __name__ == "__main__":
    print("BDC Full Flow Test")
    print("==================")
    
    # Run all tests
    api_ok = test_direct_api()
    client_ok = test_client_page()
    cors_ok = test_cors_preflight()
    browser_ok = test_browser_flow()
    
    print("\nSummary")
    print("=======")
    print(f"API Direct Access: {'✓' if api_ok else '✗'}")
    print(f"Client Page Access: {'✓' if client_ok else '✗'}")
    print(f"CORS Configuration: {'✓' if cors_ok else '✗'}")
    print(f"Browser Test Page: {'✓' if browser_ok else '✗'}")
    
    if all([api_ok, client_ok, cors_ok, browser_ok]):
        print("\n✓ All tests passed! The system is ready for use.")
        print("\nYou can now:")
        print("1. Go to http://localhost:5173/test-auth to test authentication")
        print("2. Or open file:///tmp/bdc_test.html for manual testing")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")