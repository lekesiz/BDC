#!/usr/bin/env python
"""Check all users."""

from app import create_app
from app.models import User, Tenant
from config import DevelopmentConfig
from flask_jwt_extended import decode_token

app = create_app(DevelopmentConfig)

with app.app_context():
    print("=== ALL USERS ===")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}")
        print(f"  Tenant ID: {user.tenant_id}")
        print(f"  Has tenants: {len(user.tenants) if user.tenants else 0}")
        if user.tenants:
            for tenant in user.tenants:
                print(f"    - {tenant.name}")
    
    print("\n=== TOKEN DECODE ===")
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NzM1ODYwMSwianRpIjoiMGMwMmI5OTktNTJiMS00Y2JlLTkwNWItOTNlZDMyZjAwNDM3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzQ3MzU4NjAxLCJjc3JmIjoiYzRmOTc0NzktYWIyYi00ZGJhLTg5OGEtNzczYTg2YmFhMjkxIiwiZXhwIjoxNzQ3MzYyMjAxfQ.8aCASGHV3I67EAirbcc-2T6lXtTAWJlic6Gye8TkTl8"
    
    try:
        decoded = decode_token(token)
        user_id = decoded.get('sub')
        print(f"Token User ID: {user_id}")
        
        # Get this user
        token_user = User.query.get(user_id)
        if token_user:
            print(f"Token User: {token_user.email}, Role: {token_user.role}")
            print(f"Tenant ID: {token_user.tenant_id}")
            print(f"Has tenants: {len(token_user.tenants) if token_user.tenants else 0}")
    except Exception as e:
        print(f"Token decode error: {e}")
    
    print("\n=== TENANTS ===")
    tenants = Tenant.query.all()
    for tenant in tenants:
        print(f"ID: {tenant.id}, Name: {tenant.name}")
        print(f"  Users: {len(tenant.users)}")