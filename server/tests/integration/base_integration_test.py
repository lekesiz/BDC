"""Base class for integration tests."""
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.extensions import db as _db
from app.models import User, Tenant
from app.core.container import container
from app.core.security import SecurityManager


class BaseIntegrationTest:
    """Base class for integration tests with database setup."""
    
    @pytest.fixture(scope='function')
    def app(self):
        """Create application for testing."""
        app = create_app('config.TestingConfig')
        
        # Override database URI to use in-memory SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            yield app
    
    @pytest.fixture(scope='function')
    def db(self, app):
        """Create database for testing."""
        with app.app_context():
            _db.create_all()
            yield _db
            if hasattr(_db.session, 'remove'):
                _db.session.remove()
            else:
                _db.session.close()
            _db.drop_all()
    
    @pytest.fixture(scope='function')
    def session(self, db):
        """Create a database session for testing."""
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session
        Session = sessionmaker(bind=connection)
        session = Session()
        
        # Make session available to app
        db.session = session
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()
    
    @pytest.fixture(scope='function')
    def client(self, app):
        """Create a test client."""
        return app.test_client()
    
    @pytest.fixture(scope='function')
    def runner(self, app):
        """Create a test CLI runner."""
        return app.test_cli_runner()
    
    @pytest.fixture(scope='function')
    def security_manager(self):
        """Get security manager instance."""
        return SecurityManager()
    
    @pytest.fixture(scope='function')
    def test_tenant(self, db, session):
        """Create a test tenant."""
        tenant = Tenant(
            name='Test Tenant',
            slug='test',
            email='test@tenant.com',
            is_active=True
        )
        session.add(tenant)
        session.commit()
        return tenant
    
    @pytest.fixture(scope='function')
    def test_user(self, db, session, test_tenant, security_manager):
        """Create a test user."""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password_hash=security_manager.hash_password('Test123!'),
            role='user',
            is_active=True
        )
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture(scope='function')
    def admin_user(self, db, session, test_tenant, security_manager):
        """Create an admin user."""
        user = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            password_hash=security_manager.hash_password('Admin123!'),
            role='super_admin',
            is_active=True
        )
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture(scope='function')
    def auth_headers(self, client, test_user, security_manager):
        """Get authentication headers for test user."""
        token = security_manager.generate_access_token(test_user.id)
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    @pytest.fixture(scope='function')
    def admin_auth_headers(self, client, admin_user, security_manager):
        """Get authentication headers for admin user."""
        token = security_manager.generate_access_token(admin_user.id)
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def create_user(self, session, **kwargs):
        """Helper to create a user."""
        security_manager = SecurityManager()
        user_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password_hash': security_manager.hash_password('Password123!'),
            'role': 'user',
            'is_active': True
        }
        user_data.update(kwargs)
        
        user = User(**user_data)
        session.add(user)
        session.commit()
        return user
    
    def assert_response_ok(self, response, status_code=200):
        """Assert response is successful."""
        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.data}"
    
    def assert_response_error(self, response, status_code=400):
        """Assert response is an error."""
        assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.data}"