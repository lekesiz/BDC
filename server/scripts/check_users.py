#!/usr/bin/env python
"""Check all users."""

from app import create_app
from app.models import User, Tenant
from config import DevelopmentConfig
from flask_jwt_extended import decode_token

from app.utils.logging import logger

app = create_app(DevelopmentConfig)

with app.app_context():
    logger.info("=== ALL USERS ===")
    users = User.query.all()
    for user in users:
        logger.info(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}")
        logger.info(f"  Tenant ID: {user.tenant_id}")
        logger.info(f"  Has tenants: {len(user.tenants) if user.tenants else 0}")
        if user.tenants:
            for tenant in user.tenants:
                logger.info(f"    - {tenant.name}")
    
    logger.info("\n=== TOKEN DECODE ===")
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NzM1ODYwMSwianRpIjoiMGMwMmI5OTktNTJiMS00Y2JlLTkwNWItOTNlZDMyZjAwNDM3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzQ3MzU4NjAxLCJjc3JmIjoiYzRmOTc0NzktYWIyYi00ZGJhLTg5OGEtNzczYTg2YmFhMjkxIiwiZXhwIjoxNzQ3MzYyMjAxfQ.8aCASGHV3I67EAirbcc-2T6lXtTAWJlic6Gye8TkTl8"
    
    try:
        decoded = decode_token(token)
        user_id = decoded.get('sub')
        logger.info(f"Token User ID: {user_id}")
        
        # Get this user
        token_user = User.query.get(user_id)
        if token_user:
            logger.info(f"Token User: {token_user.email}, Role: {token_user.role}")
            logger.info(f"Tenant ID: {token_user.tenant_id}")
            logger.info(f"Has tenants: {len(token_user.tenants) if token_user.tenants else 0}")
    except Exception as e:
        logger.info(f"Token decode error: {e}")
    
    logger.info("\n=== TENANTS ===")
    tenants = Tenant.query.all()
    for tenant in tenants:
        logger.info(f"ID: {tenant.id}, Name: {tenant.name}")
        logger.info(f"  Users: {len(tenant.users)}")