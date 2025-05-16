"""Fixtures for integration tests."""
import pytest
import uuid
from datetime import datetime
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import User, Tenant


@pytest.fixture
def client(app):
    """Create a test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture  
def auth_headers(app):
    """Generate auth headers for tests."""
    with app.app_context():
        # Create a test tenant if not exists
        tenant = db.session.query(Tenant).first()
        if not tenant:
            tenant = Tenant(name='Test Tenant', status='active')
            db.session.add(tenant)
            db.session.commit()
        
        # Create a test user if not exists
        user = db.session.query(User).filter_by(username='test_auth_user').first()
        if not user:
            user = User(
                username='test_auth_user',
                email='test_auth@test.com',
                user_type='Admin',
                tenant_id=tenant.id
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Generate access token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'user_type': user.user_type,
                'tenant_id': user.tenant_id
            }
        )
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    from app import create_app
    from app.config import TestConfig
    
    app = create_app(TestConfig)
    
    # Create application context
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()