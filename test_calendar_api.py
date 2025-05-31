import requests

# First login
login_response = requests.post(
    'http://localhost:5001/api/auth/login',
    json={
        'email': 'admin@bdc.com',
        'password': 'Admin123!',
        'remember': False
    }
)

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"Login successful. Token: {token[:50]}...")
    
    # Test calendar endpoint
    calendar_response = requests.get(
        'http://localhost:5001/api/calendar/events',
        params={
            'start': '2025-05-28',
            'end': '2025-06-04'
        },
        headers={
            'Authorization': f'Bearer {token}'
        }
    )
    
    print(f"\nCalendar API Response:")
    print(f"Status: {calendar_response.status_code}")
    print(f"Response: {calendar_response.text[:500]}")
else:
    print(f"Login failed: {login_response.text}")