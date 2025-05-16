#!/usr/bin/env python
"""Test beneficiary creation with Flask test client."""

from app import create_app
from config import DevelopmentConfig
import json

app = create_app(DevelopmentConfig)

with app.app_context():
    client = app.test_client()
    
    # Same data structure from frontend
    data = {
        "first_name": "Mikail",
        "last_name": "Lekesiz",
        "email": "mikail.test@lekesiz.fr",  # Changed to avoid duplicate
        "phone": "",
        "birth_date": "",
        "address": "",
        "bio": "",
        "category": "",
        "city": "",
        "country": "",
        "custom_fields": {},
        "education_level": "",
        "gender": "",
        "goals": "",
        "nationality": "",
        "native_language": "",
        "notes": "",
        "occupation": "",
        "organization": "",
        "referral_source": "",
        "state": "",
        "status": "active",
        "zip_code": ""
    }
    
    # Login first with admin user
    login_response = client.post('/api/auth/login', 
                               json={'email': 'admin@bdc.com', 'password': 'Admin123!'},
                               content_type='application/json')
    
    if login_response.status_code == 200:
        token = json.loads(login_response.data)['access_token']
        
        # Create beneficiary
        response = client.post('/api/beneficiaries',
                             json=data,
                             headers={'Authorization': f'Bearer {token}'},
                             content_type='application/json')
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.data.decode()}")
    else:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.data.decode())