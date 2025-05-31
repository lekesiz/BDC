"""Application initialization utilities."""

from typing import Optional
from flask import Flask, current_app
from app.extensions import db


class DatabaseInitializer:
    """Handles database initialization logic."""
    
    @staticmethod
    def initialize_database(app: Flask, create_test_data: bool = False) -> None:
        """Initialize database with optional test data creation.
        
        Args:
            app: Flask application instance
            create_test_data: Whether to create test users and data
        """
        with app.app_context():
            db.create_all()
            
            if create_test_data:
                DatabaseInitializer._create_default_data()
    
    @staticmethod
    def _create_default_data() -> None:
        """Create default tenant and test users."""
        from app.models.user import User
        from app.models.tenant import Tenant
        
        # Create default tenant if needed
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(
                name='Default',
                slug='default', 
                email='admin@default.com',
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            current_app.logger.info("Created default tenant")
        
        # Define test users
        test_users = [
            {
                'email': 'admin@bdc.com',
                'username': 'admin',
                'password': 'Admin123!',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'super_admin'
            },
            {
                'email': 'tenant@bdc.com',
                'username': 'tenant',
                'password': 'Tenant123!',
                'first_name': 'Tenant',
                'last_name': 'Admin',
                'role': 'tenant_admin'
            },
            {
                'email': 'trainer@bdc.com',
                'username': 'trainer',
                'password': 'Trainer123!',
                'first_name': 'Trainer',
                'last_name': 'User',
                'role': 'trainer'
            },
            {
                'email': 'student@bdc.com',
                'username': 'student',
                'password': 'Student123!',
                'first_name': 'Student',
                'last_name': 'User',
                'role': 'student'
            }
        ]
        
        # Create or update test users
        for user_data in test_users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=True,
                    tenant_id=tenant.id
                )
                db.session.add(user)
                current_app.logger.info(f"Created user: {user_data['email']}")
            
            # Reset password for testing
            user.password = user_data['password']
            
            # Add tenant relationship if needed
            if hasattr(user, 'tenants') and tenant not in user.tenants:
                user.tenants.append(tenant)
            
            db.session.commit()
        
        current_app.logger.info(f"Total users in database: {User.query.count()}")


class AppConfigurationManager:
    """Manages application configuration and initialization."""
    
    @staticmethod
    def load_config(app: Flask, config_object: Optional[object] = None) -> None:
        """Load application configuration.
        
        Args:
            app: Flask application instance
            config_object: Configuration object to use
        """
        if config_object is None:
            import os
            config_name = os.getenv('FLASK_ENV', 'default')
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from config import config
            app.config.from_object(config[config_name])
        else:
            app.config.from_object(config_object)