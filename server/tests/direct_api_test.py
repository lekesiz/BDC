#!/usr/bin/env python
"""Direct API test."""

from app import create_app
from app.extensions import db
from app.models import User
from config import DevelopmentConfig
from flask import Flask
import json

from app.utils.logging import logger

app = create_app(DevelopmentConfig)

with app.app_context():
    # Test directly with the Flask test client
    client = app.test_client()
    
    response = client.post('/api/auth/login', 
                          json={'email': 'test.admin@bdc.com', 'password': 'Test123!'},
                          content_type='application/json')
    
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Data: {response.data.decode()}")
    
    if response.status_code == 200:
        data = json.loads(response.data)
        logger.info(f"Token: {data.get('access_token', '')[:50]}...")
    
    # Also check user directly
    user = User.query.filter_by(email='test.admin@bdc.com').first()
    logger.info(f"\nUser check:")
    logger.info(f"Found: {user is not None}")
    if user:
        logger.info(f"Active: {user.is_active}")
        logger.info(f"Password OK: {user.verify_password('Test123!')}")