import requests
import json

# Test login endpoint
url = "http://localhost:5001/api/auth/login"
headers = {"Content-Type": "application/json"}
data = {
    "email": "admin@bdc.com",
    "password": "Admin123!",
    "remember": False
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")