"""
Tests for core infrastructure components (app_factory, config_manager, improved_container).
These tests target 70%+ coverage for core infrastructure.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g

from app.core.app_factory import ApplicationFactory, create_app
from app.core.config_manager import ConfigManager, ConfigValidationResult
from app.core.improved_container import ImprovedDIContainer, ServiceLifetime, ServiceDescriptor
from app.core.extension_manager import ExtensionManager
from app.core.lazy_container import LazyContainer
from app.core.database_manager import DatabaseManager
from app.core.cache_manager import CacheManager
from app.core.security import SecurityManager

# Import interfaces for DI testing
from app.services.interfaces.auth_service_interface import IAuthService
from app.services.interfaces.user_repository_interface import IUserRepository


class TestApplicationFactory:
    """Test cases for ApplicationFactory."""
    
    @pytest.fixture
    def app_factory(self):
        """Create application factory instance."""
        return ApplicationFactory()
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration object."""
        config = Mock()
        config.TESTING = True
        config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        config.JWT_SECRET_KEY = 'test-secret'
        config.SECRET_KEY = 'test-secret'
        return config
    
    def test_create_application_success(self, app_factory):
        """Test successful application creation."""
        # Use a simple test configuration
        app = app_factory.create_application()
        
        assert isinstance(app, Flask)
        assert app.config.get('TESTING') is not None
    
    @patch('app.core.app_factory.config_manager')
    @patch('app.core.app_factory.extension_manager')
    @patch('app.core.app_factory.lazy_container')
    def test_create_application_with_config(self, mock_container, mock_ext_manager, 
                                          mock_config_manager, app_factory, mock_config):
        """Test application creation with custom config."""
        # Setup mocks
        mock_config_manager.load_configuration.return_value = ConfigValidationResult(True, [])
        mock_ext_manager.initialize_extensions.return_value = True
        
        # Create app
        app = app_factory.create_application(mock_config)
        
        assert isinstance(app, Flask)
        mock_config_manager.load_configuration.assert_called_once()
        mock_ext_manager.initialize_extensions.assert_called_once()
        mock_container.initialize.assert_called_once()
    
    @patch('app.core.app_factory.config_manager')
    def test_create_application_config_validation_failure(self, mock_config_manager, app_factory):
        """Test application creation with config validation failure."""
        # Setup mock to return invalid config
        mock_config_manager.load_configuration.return_value = ConfigValidationResult(
            False, ['Invalid configuration']
        )
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Configuration validation failed"):
            app_factory.create_application()
    
    @patch('app.core.app_factory.extension_manager')
    @patch('app.core.app_factory.config_manager')
    def test_create_application_extension_failure(self, mock_config_manager, 
                                                 mock_ext_manager, app_factory):
        """Test application creation with extension initialization failure."""
        # Setup mocks
        mock_config_manager.load_configuration.return_value = ConfigValidationResult(True, [])
        mock_ext_manager.initialize_extensions.return_value = False
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Extension initialization failed"):
            app_factory.create_application()
    
    def test_configure_logging_success(self, app_factory):
        """Test successful logging configuration."""
        app = Flask(__name__)
        
        # Should not raise exception
        app_factory._configure_logging(app)
        
        # Check that logger was configured
        assert app.logger is not None
    
    @patch('app.core.app_factory.configure_logger')
    def test_configure_logging_fallback(self, mock_configure_logger, app_factory):
        """Test logging configuration fallback."""
        app = Flask(__name__)
        mock_configure_logger.side_effect = Exception("Logger error")
        
        # Should not raise exception, should fallback
        app_factory._configure_logging(app)
        
        # Should have attempted to configure custom logger
        mock_configure_logger.assert_called_once()
    
    def test_register_error_handlers(self, app_factory):
        """Test error handler registration."""
        app = Flask(__name__)
        
        app_factory._register_error_handlers(app)
        
        # Check that error handlers are registered
        assert len(app.error_handler_spec[None]) > 0
    
    @patch('app.core.app_factory.os.getenv')
    def test_register_optional_middleware_with_ip_whitelist(self, mock_getenv, app_factory):
        """Test optional middleware registration with IP whitelist enabled."""
        app = Flask(__name__)
        mock_getenv.return_value = 'true'
        
        # Should not raise exception
        app_factory._register_optional_middleware(app)
    
    def test_register_health_endpoints(self, app_factory):
        """Test health endpoint registration."""
        app = Flask(__name__)
        
        app_factory._register_health_endpoints(app)
        
        # Create test client and check endpoints
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            
            response = client.get('/api/test-cors')
            assert response.status_code == 200
    
    def test_setup_production_features(self, app_factory):
        """Test production feature setup."""
        app = Flask(__name__)
        app.config['ENV'] = 'production'
        
        # Should not raise exception
        app_factory._setup_production_features(app)
    
    def test_setup_development_features(self, app_factory):
        """Test development feature setup."""
        app = Flask(__name__)
        app.config['ENV'] = 'development'
        
        # Should not raise exception
        app_factory._setup_development_features(app)


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    @pytest.fixture
    def config_manager(self):
        """Create config manager instance."""
        return ConfigManager()
    
    def test_load_configuration_success(self, config_manager):
        """Test successful configuration loading."""
        app = Flask(__name__)
        
        result = config_manager.load_configuration(app)
        
        assert isinstance(result, ConfigValidationResult)
        assert result.is_valid is True
    
    def test_load_configuration_with_custom_config(self, config_manager):
        """Test configuration loading with custom config object."""
        app = Flask(__name__)
        
        class TestConfig:
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SECRET_KEY = 'test-secret'
        
        result = config_manager.load_configuration(app, TestConfig)
        
        assert result.is_valid is True
        assert app.config['TESTING'] is True
    
    def test_validate_required_settings_success(self, config_manager):
        """Test successful required settings validation."""
        app = Flask(__name__)
        app.config.update({
            'SECRET_KEY': 'test-secret',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        
        result = config_manager._validate_required_settings(app)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_required_settings_missing(self, config_manager):
        """Test required settings validation with missing settings."""
        app = Flask(__name__)
        # Don't set required settings
        
        result = config_manager._validate_required_settings(app)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_apply_environment_overrides(self, config_manager):
        """Test environment variable overrides."""
        app = Flask(__name__)
        
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'}):
            config_manager._apply_environment_overrides(app)
            
            assert app.config.get('SQLALCHEMY_DATABASE_URI') == 'postgresql://test'
    
    def test_setup_logging_configuration(self, config_manager):
        """Test logging configuration setup."""
        app = Flask(__name__)
        
        # Should not raise exception
        config_manager._setup_logging_configuration(app)
        
        # Check that logging config is set
        assert 'LOG_LEVEL' in app.config


class TestImprovedDIContainer:
    """Test cases for ImprovedDIContainer."""
    
    @pytest.fixture
    def container(self):
        """Create DI container instance."""
        return ImprovedDIContainer()
    
    @pytest.fixture
    def mock_service_interface(self):
        """Mock service interface."""
        from abc import ABC, abstractmethod
        
        class IMockService(ABC):
            @abstractmethod
            def do_something(self):
                pass
        
        return IMockService
    
    @pytest.fixture
    def mock_service_implementation(self, mock_service_interface):
        """Mock service implementation."""
        class MockService(mock_service_interface):
            def do_something(self):
                return "done"
        
        return MockService
    
    def test_service_descriptor_creation(self):
        """Test ServiceDescriptor creation."""
        descriptor = ServiceDescriptor(
            interface=IAuthService,
            implementation=Mock,
            lifetime=ServiceLifetime.SINGLETON
        )
        
        assert descriptor.interface == IAuthService
        assert descriptor.implementation == Mock
        assert descriptor.lifetime == ServiceLifetime.SINGLETON
    
    def test_register_service(self, container, mock_service_interface, mock_service_implementation):
        """Test service registration."""
        container.register(mock_service_interface, mock_service_implementation)
        
        assert mock_service_interface in container._services
        descriptor = container._services[mock_service_interface]
        assert descriptor.implementation == mock_service_implementation
    
    def test_register_singleton(self, container, mock_service_interface, mock_service_implementation):
        """Test singleton service registration."""
        container.register_singleton(mock_service_interface, mock_service_implementation)
        
        descriptor = container._services[mock_service_interface]
        assert descriptor.lifetime == ServiceLifetime.SINGLETON
    
    def test_register_factory(self, container, mock_service_interface):
        """Test factory service registration."""
        def factory():
            return Mock()
        
        container.register_factory(mock_service_interface, factory)
        
        descriptor = container._services[mock_service_interface]
        assert descriptor.factory == factory
    
    def test_resolve_transient_service(self, container, mock_service_interface, mock_service_implementation):
        """Test resolving transient service."""
        container.register(mock_service_interface, mock_service_implementation, 
                         ServiceLifetime.TRANSIENT)
        
        service1 = container.resolve(mock_service_interface)
        service2 = container.resolve(mock_service_interface)
        
        # Should be different instances
        assert service1 != service2
        assert isinstance(service1, mock_service_implementation)
    
    def test_resolve_singleton_service(self, container, mock_service_interface, mock_service_implementation):
        """Test resolving singleton service."""
        container.register_singleton(mock_service_interface, mock_service_implementation)
        
        service1 = container.resolve(mock_service_interface)
        service2 = container.resolve(mock_service_interface)
        
        # Should be same instance
        assert service1 is service2
        assert isinstance(service1, mock_service_implementation)
    
    def test_resolve_scoped_service(self, container, mock_service_interface):
        """Test resolving scoped service."""
        def factory():
            return Mock()
        
        container.register_factory(mock_service_interface, factory, ServiceLifetime.SCOPED)
        
        # Mock Flask's g object
        with patch('app.core.improved_container.g', spec=['__dict__']) as mock_g:
            mock_g.__dict__ = {}
            
            service1 = container.resolve(mock_service_interface)
            service2 = container.resolve(mock_service_interface)
            
            # Should be same instance within scope
            assert service1 is service2
    
    def test_resolve_unregistered_service(self, container):
        """Test resolving unregistered service."""
        class UnregisteredService:
            pass
        
        with pytest.raises(ValueError, match="Service .* is not registered"):
            container.resolve(UnregisteredService)
    
    def test_clear_scoped_services(self, container):
        """Test clearing scoped services."""
        with patch('app.core.improved_container.g', spec=['__dict__']) as mock_g:
            mock_g.__dict__ = {'_di_scoped_test': Mock()}
            
            container.clear_scoped_services()
            
            # Should be cleared
            assert '_di_scoped_test' not in mock_g.__dict__
    
    @patch('app.core.improved_container.db')
    def test_get_db_session(self, mock_db, container):
        """Test getting database session."""
        mock_session = Mock()
        mock_db.session = mock_session
        
        result = container._get_db_session()
        
        assert result == mock_session


class TestExtensionManager:
    """Test cases for ExtensionManager."""
    
    @pytest.fixture
    def extension_manager(self):
        """Create extension manager instance."""
        return ExtensionManager()
    
    def test_initialize_extensions_success(self, extension_manager):
        """Test successful extension initialization."""
        app = Flask(__name__)
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'JWT_SECRET_KEY': 'test-secret',
            'SECRET_KEY': 'test-secret'
        })
        
        result = extension_manager.initialize_extensions(app)
        
        assert result is True
    
    @patch('app.core.extension_manager.db')
    def test_initialize_database_extension(self, mock_db, extension_manager):
        """Test database extension initialization."""
        app = Flask(__name__)
        
        extension_manager._initialize_database(app)
        
        mock_db.init_app.assert_called_once_with(app)
    
    @patch('app.core.extension_manager.jwt')
    def test_initialize_jwt_extension(self, mock_jwt, extension_manager):
        """Test JWT extension initialization."""
        app = Flask(__name__)
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        
        extension_manager._initialize_jwt(app)
        
        mock_jwt.init_app.assert_called_once_with(app)


class TestLazyContainer:
    """Test cases for LazyContainer."""
    
    @pytest.fixture
    def lazy_container(self):
        """Create lazy container instance."""
        return LazyContainer()
    
    def test_initialize_container(self, lazy_container):
        """Test container initialization."""
        app = Flask(__name__)
        
        lazy_container.initialize(app)
        
        assert lazy_container._initialized is True
    
    def test_container_not_initialized_error(self, lazy_container):
        """Test error when container not initialized."""
        with pytest.raises(RuntimeError, match="Container not initialized"):
            lazy_container.get_service(IAuthService)
    
    def test_get_service_after_initialization(self, lazy_container):
        """Test getting service after initialization."""
        app = Flask(__name__)
        
        with app.app_context():
            lazy_container.initialize(app)
            
            # This should not raise an error even if service isn't found
            # because it will delegate to the container
            try:
                lazy_container.get_service(IAuthService)
            except ValueError:
                # Expected if service not registered
                pass


class TestSecurityManager:
    """Test cases for SecurityManager."""
    
    @pytest.fixture
    def security_manager(self):
        """Create security manager instance."""
        return SecurityManager()
    
    def test_hash_password(self, security_manager):
        """Test password hashing."""
        password = "test_password"
        hashed = security_manager.hash_password(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password(self, security_manager):
        """Test password verification."""
        password = "test_password"
        hashed = security_manager.hash_password(password)
        
        assert security_manager.verify_password(password, hashed) is True
        assert security_manager.verify_password("wrong_password", hashed) is False
    
    def test_generate_token(self, security_manager):
        """Test token generation."""
        token = security_manager.generate_token()
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_validate_email(self, security_manager):
        """Test email validation."""
        assert security_manager.validate_email("test@example.com") is True
        assert security_manager.validate_email("invalid_email") is False
        assert security_manager.validate_email("") is False
    
    def test_sanitize_input(self, security_manager):
        """Test input sanitization."""
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = security_manager.sanitize_input(dangerous_input)
        
        assert "<script>" not in sanitized
        assert "alert" not in sanitized


class TestDatabaseManager:
    """Test cases for DatabaseManager."""
    
    @pytest.fixture
    def database_manager(self):
        """Create database manager instance."""
        return DatabaseManager()
    
    def test_create_tables(self, database_manager):
        """Test table creation."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            # Should not raise exception
            database_manager.create_tables()
    
    def test_drop_tables(self, database_manager):
        """Test table dropping."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            # Should not raise exception
            database_manager.drop_tables()
    
    def test_get_connection_info(self, database_manager):
        """Test getting connection info."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            info = database_manager.get_connection_info()
            
            assert isinstance(info, dict)
            assert 'driver' in info or 'url' in info


class TestCacheManager:
    """Test cases for CacheManager."""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance."""
        return CacheManager()
    
    def test_initialize_cache(self, cache_manager):
        """Test cache initialization."""
        app = Flask(__name__)
        app.config['CACHE_TYPE'] = 'simple'
        
        # Should not raise exception
        cache_manager.initialize(app)
    
    def test_get_set_cache(self, cache_manager):
        """Test cache get/set operations."""
        app = Flask(__name__)
        app.config['CACHE_TYPE'] = 'simple'
        
        with app.app_context():
            cache_manager.initialize(app)
            
            # Test cache operations
            cache_manager.set('test_key', 'test_value')
            value = cache_manager.get('test_key')
            
            assert value == 'test_value'
    
    def test_cache_delete(self, cache_manager):
        """Test cache deletion."""
        app = Flask(__name__)
        app.config['CACHE_TYPE'] = 'simple'
        
        with app.app_context():
            cache_manager.initialize(app)
            
            cache_manager.set('test_key', 'test_value')
            cache_manager.delete('test_key')
            value = cache_manager.get('test_key')
            
            assert value is None