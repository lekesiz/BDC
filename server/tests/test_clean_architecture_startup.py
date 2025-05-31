"""Comprehensive test for the clean architecture application startup."""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from flask import Flask

from app.core.config_manager import ConfigurationManager, ConfigValidationResult
from app.core.extension_manager import ExtensionManager
from app.core.lazy_container import LazyDIContainer
from app.core.database_manager import DatabaseInitializer, DatabaseMigrationManager
from app.core.app_factory import ApplicationFactory
from app import create_app


class TestConfigurationManager:
    """Test configuration management system."""
    
    def test_configuration_validation_success(self):
        """Test successful configuration validation."""
        config_manager = ConfigurationManager()
        
        # Valid configuration
        config = {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret',
            'REDIS_URL': 'redis://localhost:6379/0',
            'ENV': 'testing'
        }
        
        result = config_manager._validate_configuration(config)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_configuration_validation_missing_database(self):
        """Test configuration validation with missing database URI."""
        config_manager = ConfigurationManager()
        
        # Missing database URI
        config = {
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret'
        }
        
        result = config_manager._validate_configuration(config)
        
        assert not result.is_valid
        assert any('SQLALCHEMY_DATABASE_URI' in error for error in result.errors)
    
    def test_configuration_validation_production_secrets(self):
        """Test configuration validation for production secrets."""
        config_manager = ConfigurationManager()
        
        # Production config with default secrets
        config = {
            'SQLALCHEMY_DATABASE_URI': 'postgresql://user:pass@localhost/db',
            'SECRET_KEY': 'dev-secret-key-change-in-production',
            'JWT_SECRET_KEY': 'jwt-secret-key-change-in-production',
            'ENV': 'production'
        }
        
        result = config_manager._validate_configuration(config)
        
        assert not result.is_valid
        assert any('Production SECRET_KEY' in error for error in result.errors)
        assert any('Production JWT_SECRET_KEY' in error for error in result.errors)


class TestExtensionManager:
    """Test extension initialization system."""
    
    def test_extension_manager_initialization(self):
        """Test extension manager initialization."""
        extension_manager = ExtensionManager()
        
        # Check that default initializers are registered
        assert 'database' in extension_manager._initializers
        assert 'authentication' in extension_manager._initializers
        assert 'cors' in extension_manager._initializers
        assert 'caching' in extension_manager._initializers
        assert 'mail' in extension_manager._initializers
        assert 'rate_limiting' in extension_manager._initializers
        assert 'socketio' in extension_manager._initializers
    
    def test_initialization_order_dependencies(self):
        """Test that initialization order respects dependencies."""
        extension_manager = ExtensionManager()
        
        init_order = extension_manager._get_initialization_order()
        
        # Database should come before authentication
        db_index = init_order.index('database')
        auth_index = init_order.index('authentication')
        
        assert db_index < auth_index
    
    @patch('app.extensions.db')
    @patch('app.extensions.migrate')
    def test_database_extension_initialization(self, mock_migrate, mock_db):
        """Test database extension initialization."""
        from app.core.extension_manager import DatabaseExtensionInitializer
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        initializer = DatabaseExtensionInitializer()
        
        with app.app_context():
            result = initializer.initialize(app)
        
        assert result is True
        mock_db.init_app.assert_called_once_with(app)
        mock_migrate.init_app.assert_called_once_with(app, mock_db)


class TestLazyContainer:
    """Test lazy-loading dependency injection container."""
    
    def test_container_initialization(self):
        """Test container initialization."""
        container = LazyDIContainer()
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        container.initialize(app)
        
        assert container._initialized
    
    def test_service_registration(self):
        """Test service registration."""
        container = LazyDIContainer()
        
        class ITestService:
            pass
        
        class TestService:
            pass
        
        container.register(ITestService, TestService)
        
        assert container.is_registered(ITestService)
    
    def test_factory_registration(self):
        """Test factory registration."""
        container = LazyDIContainer()
        
        class ITestService:
            pass
        
        def test_factory():
            return "test_instance"
        
        container.register_factory(ITestService, test_factory)
        
        assert container.is_registered(ITestService)
    
    def test_service_resolution_unregistered(self):
        """Test service resolution for unregistered service."""
        container = LazyDIContainer()
        
        class IUnregisteredService:
            pass
        
        with pytest.raises(ValueError, match="Service .* is not registered"):
            container.resolve(IUnregisteredService)


class TestDatabaseManager:
    """Test database management system."""
    
    def test_database_initializer(self):
        """Test database initializer."""
        initializer = DatabaseInitializer()
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with patch('app.extensions.db') as mock_db:
            result = initializer.initialize_database(app, create_tables=True, create_test_data=False)
            
            assert result is True
            mock_db.create_all.assert_called_once()
    
    def test_migration_manager(self):
        """Test migration manager."""
        manager = DatabaseMigrationManager()
        
        # Check that default migrations are registered
        migrations = manager.get_available_migrations()
        
        assert 'create_default_tenant' in migrations
        assert 'create_admin_user' in migrations


class TestApplicationFactory:
    """Test application factory."""
    
    def test_application_creation_basic(self):
        """Test basic application creation."""
        # Use temporary directory for test database
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration
            class TestConfig:
                TESTING = True
                SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_dir}/test.db'
                SECRET_KEY = 'test-secret-key'
                JWT_SECRET_KEY = 'test-jwt-secret'
                REDIS_URL = 'redis://localhost:6379/0'
                CORS_ORIGINS = ['*']
                UPLOAD_FOLDER = temp_dir
                ENV = 'testing'
            
            factory = ApplicationFactory()
            
            # Mock some components to avoid external dependencies
            with patch('app.core.extension_manager.extension_manager') as mock_ext_mgr, \
                 patch('app.core.lazy_container.lazy_container') as mock_container:
                
                mock_ext_mgr.initialize_extensions.return_value = True
                
                app = factory.create_application(TestConfig)
                
                assert isinstance(app, Flask)
                assert app.config['TESTING'] is True
                mock_ext_mgr.initialize_extensions.assert_called_once()
                mock_container.initialize.assert_called_once()
    
    def test_application_creation_with_config_validation_failure(self):
        """Test application creation with configuration validation failure."""
        # Invalid configuration (missing required fields)
        class InvalidConfig:
            TESTING = True
            # Missing SQLALCHEMY_DATABASE_URI
        
        factory = ApplicationFactory()
        
        with pytest.raises(RuntimeError, match="Configuration validation failed"):
            factory.create_application(InvalidConfig)
    
    def test_application_creation_with_extension_failure(self):
        """Test application creation with extension initialization failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            class TestConfig:
                TESTING = True
                SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_dir}/test.db'
                SECRET_KEY = 'test-secret-key'
                JWT_SECRET_KEY = 'test-jwt-secret'
                REDIS_URL = 'redis://localhost:6379/0'
                CORS_ORIGINS = ['*']
                UPLOAD_FOLDER = temp_dir
                ENV = 'testing'
            
            factory = ApplicationFactory()
            
            # Mock extension manager to return failure
            with patch('app.core.extension_manager.extension_manager') as mock_ext_mgr:
                mock_ext_mgr.initialize_extensions.return_value = False
                
                with pytest.raises(RuntimeError, match="Extension initialization failed"):
                    factory.create_application(TestConfig)


class TestIntegrationStartup:
    """Integration tests for complete application startup."""
    
    def test_complete_application_startup_testing_config(self):
        """Test complete application startup with testing configuration."""
        # Use temporary directory for test database
        with tempfile.TemporaryDirectory() as temp_dir:
            class TestConfig:
                TESTING = True
                SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_dir}/test.db'
                SECRET_KEY = 'test-secret-key'
                JWT_SECRET_KEY = 'test-jwt-secret'
                REDIS_URL = 'redis://localhost:6379/0'
                CORS_ORIGINS = ['*']
                UPLOAD_FOLDER = temp_dir
                ENV = 'testing'
                # Disable features that might cause issues in testing
                RATELIMIT_ENABLED = False
                CACHE_TYPE = 'null'
                CACHE_NO_NULL_WARNING = True
            
            # Mock external dependencies
            with patch('app.extensions.cache') as mock_cache, \
                 patch('app.extensions.mail') as mock_mail, \
                 patch('app.extensions.limiter') as mock_limiter, \
                 patch('app.extensions.socketio') as mock_socketio:
                
                app = create_app(TestConfig)
                
                assert isinstance(app, Flask)
                assert app.config['TESTING'] is True
                
                # Test that the app can start and basic routes work
                with app.test_client() as client:
                    response = client.get('/health')
                    assert response.status_code == 200
                    
                    response = client.get('/api/test-cors')
                    assert response.status_code == 200
    
    def test_application_startup_no_import_time_dependencies(self):
        """Test that application startup has no import-time dependencies."""
        # This test ensures that simply importing the app module doesn't
        # cause any side effects or dependencies to be initialized
        
        # Before importing, check that no Flask app context exists
        from flask import has_app_context
        assert not has_app_context()
        
        # Import the main app module - this should not create any side effects
        from app import create_app
        
        # Still no app context should exist
        assert not has_app_context()
        
        # Only when we explicitly create an app should initialization happen
        with tempfile.TemporaryDirectory() as temp_dir:
            class TestConfig:
                TESTING = True
                SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_dir}/test.db'
                SECRET_KEY = 'test-secret-key'
                JWT_SECRET_KEY = 'test-jwt-secret'
                REDIS_URL = 'redis://localhost:6379/0'
                CORS_ORIGINS = ['*']
                UPLOAD_FOLDER = temp_dir
                ENV = 'testing'
                RATELIMIT_ENABLED = False
                CACHE_TYPE = 'null'
                CACHE_NO_NULL_WARNING = True
            
            # Mock external dependencies
            with patch('app.extensions.cache'), \
                 patch('app.extensions.mail'), \
                 patch('app.extensions.limiter'), \
                 patch('app.extensions.socketio'):
                
                app = create_app(TestConfig)
                assert isinstance(app, Flask)
    
    def test_cli_commands_registration(self):
        """Test that CLI commands are properly registered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            class TestConfig:
                TESTING = True
                SQLALCHEMY_DATABASE_URI = f'sqlite:///{temp_dir}/test.db'
                SECRET_KEY = 'test-secret-key'
                JWT_SECRET_KEY = 'test-jwt-secret'
                REDIS_URL = 'redis://localhost:6379/0'
                CORS_ORIGINS = ['*']
                UPLOAD_FOLDER = temp_dir
                ENV = 'testing'
                RATELIMIT_ENABLED = False
                CACHE_TYPE = 'null'
                CACHE_NO_NULL_WARNING = True
            
            with patch('app.extensions.cache'), \
                 patch('app.extensions.mail'), \
                 patch('app.extensions.limiter'), \
                 patch('app.extensions.socketio'):
                
                app = create_app(TestConfig)
                
                # Check that CLI commands are registered
                cli_commands = list(app.cli.commands.keys())
                
                expected_commands = [
                    'init-db',
                    'create-test-data',
                    'run-migration',
                    'list-migrations',
                    'validate-config',
                    'check-extensions',
                    'check-services'
                ]
                
                for cmd in expected_commands:
                    assert cmd in cli_commands or cmd.replace('-', '_') in cli_commands


if __name__ == '__main__':
    pytest.main([__file__, '-v'])