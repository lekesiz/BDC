"""Tests for middleware and core modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request
import os
import json


class TestCorsMiddleware:
    """Test CORS middleware."""
    
    @patch('app.middleware.cors_middleware.Response')
    def test_cors_after_request(self, mock_response, test_app):
        """Test CORS headers are added after request."""
        with test_app.app_context():
            from app.middleware.cors_middleware import add_cors_headers
            
            # Mock response
            response = Mock()
            response.headers = {}
            
            # Test adding CORS headers
            result = add_cors_headers(response)
            
            assert 'Access-Control-Allow-Origin' in result.headers
            assert 'Access-Control-Allow-Methods' in result.headers
            assert 'Access-Control-Allow-Headers' in result.headers
    
    def test_cors_preflight_request(self, test_app):
        """Test CORS preflight request handling."""
        with test_app.app_context():
            from app.middleware.cors_middleware import handle_preflight
            
            # Mock preflight request
            with test_app.test_request_context(method='OPTIONS'):
                response = handle_preflight()
                
                assert response.status_code == 200
                assert response.headers.get('Access-Control-Allow-Methods') is not None


class TestAppFactory:
    """Test app factory configuration."""
    
    def test_create_app_with_config_class(self):
        """Test creating app with config class."""
        from app import create_app
        from config import TestingConfig
        
        app = create_app(TestingConfig)
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_create_app_with_config_dict(self):
        """Test creating app with config dictionary."""
        from app import create_app
        
        config = {
            'SECRET_KEY': 'test-secret',
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        }
        
        app = create_app(config)
        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['SECRET_KEY'] == 'test-secret'
    
    @patch.dict(os.environ, {'FLASK_ENV': 'production'})
    def test_create_app_production_env(self):
        """Test creating app in production environment."""
        from app import create_app
        
        app = create_app()
        assert app is not None
        assert app.config['DEBUG'] is False


class TestExtensions:
    """Test Flask extensions initialization."""
    
    def test_extensions_import(self, test_app):
        """Test that all extensions can be imported."""
        from app.extensions import (
            db, jwt, migrate, cors, mail, socketio,
            cache, logger, login_manager, admin, ma
        )
        
        assert db is not None
        assert jwt is not None
        assert migrate is not None
        assert cors is not None
        assert mail is not None
        assert socketio is not None
        assert cache is not None
        assert logger is not None
    
    def test_extensions_initialization(self, test_app):
        """Test extensions are properly initialized."""
        from app.extensions import db
        
        # Test db is bound to app
        assert db.engine is not None
        assert db.session is not None


class TestConfig:
    """Test configuration classes."""
    
    def test_base_config(self):
        """Test base configuration."""
        from config import Config
        
        assert Config.SECRET_KEY is not None
        assert hasattr(Config, 'SQLALCHEMY_TRACK_MODIFICATIONS')
        assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    
    def test_development_config(self):
        """Test development configuration."""
        from config import DevelopmentConfig
        
        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.ENV == 'development'
    
    def test_testing_config(self):
        """Test testing configuration."""
        from config import TestingConfig
        
        assert TestingConfig.TESTING is True
        assert TestingConfig.WTF_CSRF_ENABLED is False
        assert 'memory' in TestingConfig.SQLALCHEMY_DATABASE_URI
    
    def test_production_config(self):
        """Test production configuration."""
        from config import ProductionConfig
        
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.ENV == 'production'
    
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test'})
    def test_config_from_env(self):
        """Test loading configuration from environment."""
        from config import Config
        
        # Reload config to pick up env var
        import importlib
        import config
        importlib.reload(config)
        
        assert 'postgresql' in config.Config.SQLALCHEMY_DATABASE_URI


class TestMiddlewareIntegration:
    """Test middleware integration."""
    
    def test_error_handler_middleware(self, test_app):
        """Test error handler middleware."""
        @test_app.errorhandler(404)
        def not_found(error):
            return {'error': 'Not found'}, 404
        
        with test_app.test_client() as client:
            response = client.get('/nonexistent-endpoint')
            assert response.status_code == 404
            data = response.get_json()
            assert data is not None
            assert 'error' in data
    
    def test_request_logging_middleware(self, test_app):
        """Test request logging middleware."""
        with patch('app.utils.logger.logger') as mock_logger:
            @test_app.before_request
            def log_request():
                mock_logger.info(f'Request: {request.method} {request.path}')
            
            with test_app.test_client() as client:
                client.get('/api/health')
                mock_logger.info.assert_called()
    
    def test_response_timing_middleware(self, test_app):
        """Test response timing middleware."""
        import time
        
        @test_app.before_request
        def start_timer():
            request.start_time = time.time()
        
        @test_app.after_request
        def log_response_time(response):
            if hasattr(request, 'start_time'):
                elapsed = time.time() - request.start_time
                response.headers['X-Response-Time'] = str(elapsed)
            return response
        
        with test_app.test_client() as client:
            response = client.get('/health')
            assert 'X-Response-Time' in response.headers


class TestDatabaseOperations:
    """Test database operations."""
    
    def test_db_session_lifecycle(self, test_app):
        """Test database session lifecycle."""
        with test_app.app_context():
            from app.extensions import db
            from app.models import User
            
            # Test session creation
            user = User(email='lifecycle@test.com', username='lifecycle')
            db.session.add(user)
            
            # Test rollback
            db.session.rollback()
            assert User.query.filter_by(email='lifecycle@test.com').first() is None
            
            # Test commit
            user = User(email='lifecycle2@test.com', username='lifecycle2')
            db.session.add(user)
            db.session.commit()
            
            fetched_user = User.query.filter_by(email='lifecycle2@test.com').first()
            assert fetched_user is not None
    
    def test_db_model_relationships(self, test_app):
        """Test database model relationships."""
        with test_app.app_context():
            from app.models import User, Notification, Document
            from app.extensions import db
            
            # Create user
            user = User(email='relationship@test.com', username='relationship')
            db.session.add(user)
            db.session.commit()
            
            # Create related notification
            notification = Notification(
                user_id=user.id,
                title='Test',
                message='Test notification',
                type='info'
            )
            db.session.add(notification)
            db.session.commit()
            
            # Test relationship
            assert user.notifications.count() == 1
            assert notification.user == user


if __name__ == '__main__':
    pytest.main([__file__, '-v'])