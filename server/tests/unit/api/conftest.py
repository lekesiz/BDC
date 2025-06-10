"""Test configuration for API tests."""

import pytest
import tempfile
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token

from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    from config import TestingConfig
    
    app = create_app(TestingConfig)
    
    # Ensure we're in testing mode
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Create tables
        db.create_all()
        yield app
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        email='admin@bdc.com',
        username='admin',
        first_name='Admin',
        last_name='User',
        role='super_admin',
        is_active=True
    )
    user.set_password('Admin123!')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers(admin_user):
    """Generate authorization headers."""
    access_token = create_access_token(
        identity=admin_user.id,
        additional_claims={
            'role': admin_user.role
        }
    )
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def valid_jwt_token(admin_user):
    """Create a valid JWT token."""
    return create_access_token(
        identity=admin_user.id,
        additional_claims={
            'user_id': admin_user.id,
            'role': admin_user.role
        }
    )


@pytest.fixture
def expired_jwt_token(admin_user):
    """Create an expired JWT token."""
    from datetime import timedelta
    return create_access_token(
        identity=admin_user.id,
        additional_claims={
            'user_id': admin_user.id,
            'role': admin_user.role
        },
        expires_delta=timedelta(seconds=-1)
    )


@pytest.fixture
def refresh_token(admin_user):
    """Create a refresh token."""
    return create_refresh_token(
        identity=admin_user.id,
        additional_claims={
            'role': admin_user.role
        }
    )