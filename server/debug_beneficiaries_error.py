#!/usr/bin/env python
"""Debug beneficiaries error with logging."""

from app import create_app
from app.models import User
from app.services.beneficiary_service import BeneficiaryService
from config import DevelopmentConfig
from flask_jwt_extended import get_jwt_identity
from flask import Flask
import json
import traceback

app = create_app(DevelopmentConfig)

with app.app_context():
    client = app.test_client()
    
    # Login with super_admin user
    login_response = client.post('/api/auth/login', 
                               json={'email': 'admin@bdc.com', 'password': 'Admin123!'},
                               content_type='application/json')
    
    if login_response.status_code == 200:
        token = json.loads(login_response.data)['access_token']
        
        # Mock a beneficiaries request
        try:
            print("Direct service call test:")
            # Test direct service call
            beneficiaries, total, pages = BeneficiaryService.get_beneficiaries(
                tenant_id=None,
                trainer_id=None,
                status=None,
                query=None,
                page=1,
                per_page=10,
                sort_by='created_at',
                sort_dir='desc'
            )
            print(f"Direct call success: {len(beneficiaries)} items")
        except Exception as e:
            print(f"Direct call error: {e}")
            traceback.print_exc()
        
        # Test API endpoint
        params = {
            "page": 1,
            "per_page": 10,
            "sort_by": "created_at",
            "sort_dir": "desc"
        }
        
        try:
            response = client.get('/api/beneficiaries',
                                query_string=params,
                                headers={'Authorization': f'Bearer {token}'})
            
            print(f"\nAPI Status: {response.status_code}")
            if response.status_code != 200:
                print(f"API Response: {response.data.decode()}")
        except Exception as e:
            print(f"API call error: {e}")
            traceback.print_exc()
    else:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.data.decode())