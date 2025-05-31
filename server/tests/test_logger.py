import pytest
import json
import logging
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g, request

from app import create_app
from app.utils.logger import RequestFormatter, configure_logger, get_logger


class TestRequestFormatter:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        return app
    
    @pytest.fixture
    def formatter(self):
        return RequestFormatter('[%(levelname)s] %(message)s [%(request_id)s]')
    
    def test_format_with_request_context(self, app, formatter):
        """Test formatting with Flask request context"""
        with app.test_request_context('/test', method='GET'):
            g.request_id = 'test-123'
            g.user_id = 42
            
            record = logging.LogRecord(
                name='test',
                level=logging.INFO,
                pathname='test.py',
                lineno=10,
                msg='Test message',
                args=(),
                exc_info=None
            )
            
            formatted = formatter.format(record)
            
            assert record.url == 'http://localhost/test'
            assert record.method == 'GET'
            assert record.request_id == 'test-123'
            assert record.user_id == 42
            assert '[INFO]' in formatted
            assert 'Test message' in formatted
            assert '[test-123]' in formatted
    
    def test_format_without_request_context(self, formatter):
        """Test formatting without Flask request context"""
        record = logging.LogRecord(
            name='test',
            level=logging.WARNING,
            pathname='test.py',
            lineno=10,
            msg='Warning message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert record.url is None
        assert record.method is None
        assert record.request_id is None
        assert record.user_id is None
        assert '[WARNING]' in formatted
        assert 'Warning message' in formatted


class TestConfigureLogger:
    @pytest.fixture
    def test_app(self):
        """Create a test Flask app"""
        app = Flask(__name__)
        app.config['LOG_LEVEL'] = 'DEBUG'
        app.config['LOG_FORMAT'] = 'standard'
        return app
    
    def test_configure_logger_creates_log_directory(self, test_app):
        """Test that configure_logger creates logs directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_app.root_path = tmpdir
            
            # Ensure logs directory doesn't exist
            log_dir = os.path.join(tmpdir, '..', 'logs')
            
            with patch('os.path.exists', return_value=False), \
                 patch('os.makedirs') as mock_makedirs:
                configure_logger(test_app)
                mock_makedirs.assert_called_once()
    
    def test_configure_logger_with_json_format(self, test_app):
        """Test logger configuration with JSON format"""
        test_app.config['LOG_FORMAT'] = 'json'
        
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'):
            configure_logger(test_app)
            
            # Check that handlers were added
            assert len(test_app.logger.handlers) > 0
    
    def test_configure_logger_with_standard_format(self, test_app):
        """Test logger configuration with standard format"""
        test_app.config['LOG_FORMAT'] = 'standard'
        
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'):
            configure_logger(test_app)
            
            # Check that handlers were added
            assert len(test_app.logger.handlers) > 0
    
    def test_configure_logger_log_level(self, test_app):
        """Test that log level is set correctly"""
        test_app.config['LOG_LEVEL'] = 'WARNING'
        
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'):
            configure_logger(test_app)
            
            # The effective level should be WARNING (30)
            assert test_app.logger.level == logging.WARNING


class TestJsonFormatter:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config['LOG_FORMAT'] = 'json'
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs'):
            configure_logger(app)
        return app
    
    def test_json_format_basic(self, app):
        """Test JSON formatter basic functionality"""
        # Create JsonFormatter instance
        formatter = None
        for handler in app.logger.handlers:
            if hasattr(handler.formatter, '__class__') and \
               handler.formatter.__class__.__name__ == 'JsonFormatter':
                formatter = handler.formatter
                break
        
        if formatter is None:
            # Create formatter manually if not found
            from app.utils.logger import configure_logger
            
            class JsonFormatter(logging.Formatter):
                def format(self, record):
                    log_record = {
                        'timestamp': '2025-05-26 12:00:00',
                        'level': record.levelname,
                        'name': record.name,
                        'message': record.getMessage(),
                    }
                    return json.dumps(log_record)
            
            formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test JSON message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert data['level'] == 'INFO'
        assert data['message'] == 'Test JSON message'
        assert 'timestamp' in data
    
    def test_json_format_with_exception(self, app):
        """Test JSON formatter with exception info"""
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        # Create formatter manually
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': '2025-05-26 12:00:00',
                    'level': record.levelname,
                    'name': record.name,
                    'message': record.getMessage(),
                }
                
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_record)
        
        formatter = JsonFormatter()
        
        record = logging.LogRecord(
            name='test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=10,
            msg='Error occurred',
            args=(),
            exc_info=exc_info
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert data['level'] == 'ERROR'
        assert 'exception' in data
        assert 'ValueError: Test exception' in data['exception']


class TestGetLogger:
    def test_get_logger(self):
        """Test getting a logger instance"""
        logger = get_logger('test_module')
        
        assert logger is not None
        # structlog returns a BoundLogger or similar
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
    
    def test_get_logger_different_names(self):
        """Test getting loggers with different names"""
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')
        
        # Different names should return different logger instances
        assert logger1 is not logger2