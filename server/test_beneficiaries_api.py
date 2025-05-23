#!/usr/bin/env python
"""Test beneficiaries API endpoints."""

from app import create_app
from config import DevelopmentConfig
import json

app = create_app(DevelopmentConfig)

def get_auth_token(client):
    """Get auth token."""
    response = client.post('/api/auth/login', 
                          json={'email': 'test.admin@bdc.com', 'password': 'Test123!'},
                          content_type='application/json')
    if response.status_code == 200:
        data = json.loads(response.data)
        return data.get('access_token')
    return None

def test_beneficiaries_list(client, token):
    """Test beneficiaries list."""
    print("\n1. Testing Beneficiaries List...")
    response = client.get('/api/beneficiaries',
                         headers={'Authorization': f'Bearer {token}'})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Items count: {len(data.get('items', []))}")
        print(f"Total: {data.get('total', 0)}")
    else:
        print(f"Error: {response.data.decode()}")

def test_beneficiary_create(client, token):
    """Test beneficiary creation."""
    print("\n2. Testing Beneficiary Creation...")
    
    beneficiary_data = {
        'first_name': 'Test',
        'last_name': 'Beneficiary',
        'email': 'test.beneficiary@example.com',
        'phone': '+33123456789',
        'gender': 'male',
        'birth_date': '1990-01-01',
        'address': '123 Test Street',
        'city': 'Paris',
        'state': 'IDF',
        'zip_code': '75001',
        'country': 'France',
        'nationality': 'French',
        'native_language': 'French',
        'education_level': 'Bachelor',
        'profession': 'Engineer',
        'organization': 'Test Company',
        'category': 'Professional',
        'status': 'active',
        'bio': 'Test bio',
        'goals': 'Test goals',
        'notes': 'Test notes',
        'referral_source': 'Website',
        'custom_fields': {'field1': 'value1'}
    }
    
    response = client.post('/api/beneficiaries',
                          json=beneficiary_data,
                          headers={'Authorization': f'Bearer {token}'},
                          content_type='application/json')
    
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = json.loads(response.data)
        print(f"Created beneficiary ID: {data.get('id')}")
        return data.get('id')
    else:
        print(f"Error: {response.data.decode()}")
        return None

def test_beneficiary_get(client, token, beneficiary_id):
    """Test get beneficiary."""
    print(f"\n3. Testing Get Beneficiary ID: {beneficiary_id}...")
    
    response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                         headers={'Authorization': f'Bearer {token}'})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Beneficiary: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
    else:
        print(f"Error: {response.data.decode()}")

def test_beneficiary_update(client, token, beneficiary_id):
    """Test update beneficiary."""
    print(f"\n4. Testing Update Beneficiary ID: {beneficiary_id}...")
    
    update_data = {
        'city': 'Lyon',
        'profession': 'Senior Engineer'
    }
    
    response = client.patch(f'/api/beneficiaries/{beneficiary_id}',
                           json=update_data,
                           headers={'Authorization': f'Bearer {token}'},
                           content_type='application/json')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print("Update successful")
    else:
        print(f"Error: {response.data.decode()}")

with app.app_context():
    client = app.test_client()
    
    # Get token
    token = get_auth_token(client)
    if not token:
        print("Failed to get auth token")
        exit(1)
    
    print(f"Got token: {token[:50]}...")
    
    # Run tests
    test_beneficiaries_list(client, token)
    beneficiary_id = test_beneficiary_create(client, token)
    
    if beneficiary_id:
        test_beneficiary_get(client, token, beneficiary_id)
        test_beneficiary_update(client, token, beneficiary_id)