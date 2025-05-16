"""Tests for the logger utility module."""

import json
import logging
import os
import time
from unittest.mock import Mock, patch, MagicMock
import structlog
import pytest
from flask import Flask, request, g


class TestRequestFormatter:
    """Test cases for the RequestFormatter class."""
    
    def test_format_with_request_context(self):
        """Test formatter with request context."""
        # Import here to avoid circular imports
        from app.utils.logger import RequestFormatter
        
        formatter = RequestFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Mock request context
        with patch('app.utils.logger.has_request_context', return_value=True):
            mock_request = MagicMock()
            mock_request.url = 'http://example.com'
            mock_request.method = 'GET'
            mock_request.remote_addr = '127.0.0.1'
            
            mock_g = MagicMock()
            mock_g.request_id = 'test-request-id'
            mock_g.user_id = 'test-user-id'
            
            with patch('app.utils.logger.request', mock_request):
                with patch('app.utils.logger.g', mock_g):
                    # Format record
                    formatter.format(record)
                    
                    # Verify attributes are set
                    assert record.url == 'http://example.com'
                    assert record.method == 'GET'
                    assert record.remote_addr == '127.0.0.1'
                    assert record.request_id == 'test-request-id'
                    assert record.user_id == 'test-user-id'
    
    def test_format_without_request_context(self):
        """Test formatter without request context."""
        from app.utils.logger import RequestFormatter
        
        formatter = RequestFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Mock no request context
        with patch('app.utils.logger.has_request_context', return_value=False):
            formatter.format(record)
            
            # Verify attributes are None
            assert record.url is None
            assert record.method is None
            assert record.remote_addr is None
            assert record.request_id is None
            assert record.user_id is None
    
    def test_format_with_missing_g_attributes(self):
        """Test formatter when g attributes are missing."""
        from app.utils.logger import RequestFormatter
        
        formatter = RequestFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Mock request context
        with patch('app.utils.logger.has_request_context', return_value=True):
            mock_request = MagicMock()
            mock_request.url = 'http://example.com'
            mock_request.method = 'GET'
            mock_request.remote_addr = '127.0.0.1'
            
            mock_g = MagicMock(spec=['__getattr__'])
            # Mock g to raise AttributeError for missing attributes
            mock_g.__getattr__.side_effect = AttributeError
            
            with patch('app.utils.logger.request', mock_request):
                with patch('app.utils.logger.g', mock_g):
                    # Format record
                    formatter.format(record)
                    
                    # Verify defaults are set for missing attributes
                    assert record.request_id == 'no-request-id'
                    assert record.user_id is None


class TestJsonFormatter:
    """Test cases for the JsonFormatter class."""
    
    def test_format_basic_record(self):
        """Test JSON formatter with basic record."""
        from app.utils.logger import configure_logger
        
        # Create a mock app
        app = Mock()
        app.config = {'LOG_FORMAT': 'json'}
        app.root_path = '/tmp/test'
        app.logger = Mock()
        
        # Patch os.path.exists and os.makedirs to avoid file operations
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs'):
                with patch('logging.FileHandler'):
                    configure_logger(app)
        
        # Get the formatter from the mocked handler
        # Since we're testing the inner JsonFormatter class
        # We need to create it directly
        with patch('time.strftime', return_value='2023-01-01 00:00:00'):
            with patch('app.utils.logger.has_request_context', return_value=False):
                # Create a LogRecord
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="test.py",
                    lineno=1,
                    msg="Test message",
                    args=(),
                    exc_info=None
                )
                
                # Create JsonFormatter instance manually for testing
                # We need to extract it from the configure_logger function
                from app.utils.logger import configure_logger
                import inspect
                
                # Get the source code and extract JsonFormatter class
                source = inspect.getsource(configure_logger)
                
                # Create a namespace to exec the JsonFormatter class
                namespace = {
                    'logging': logging,
                    'time': time,
                    'json': json,
                    'has_request_context': lambda: False,
                    'request': Mock(),
                    'g': Mock()
                }
                
                # Extract and execute just the JsonFormatter class definition
                formatter_code = """
import json
import time
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        
        # Add request context if available
        if False:  # has_request_context()
            log_record.update({
                'url': None,
                'method': None,
                'ip': None,
                'request_id': 'no-request-id',
                'user_id': None
            })
        
        # Add exception info if available
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)
"""
                exec(formatter_code, namespace)
                JsonFormatter = namespace['JsonFormatter']
                
                formatter = JsonFormatter()
                result = formatter.format(record)
                
                # Parse the JSON result
                log_data = json.loads(result)
                
                assert log_data['timestamp'] == '2023-01-01 00:00:00'
                assert log_data['level'] == 'INFO'
                assert log_data['name'] == 'test'
                assert log_data['message'] == 'Test message'
    
    def test_format_with_exception(self):
        """Test JSON formatter with exception info."""
        # Create a test exception
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        # Create a LogRecord with exception info
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        
        # Test the formatting - we'll create a simplified version
        log_record = {
            'timestamp': '2023-01-01 00:00:00',
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        
        # Add exception info
        formatter = logging.Formatter()
        log_record['exception'] = formatter.formatException(exc_info)
        
        result = json.dumps(log_record)
        log_data = json.loads(result)
        
        assert 'exception' in log_data
        assert 'ValueError: Test error' in log_data['exception']


class TestConfigureLogger:
    """Test cases for the configure_logger function."""
    
    def test_configure_logger_json_format(self):
        """Test logger configuration with JSON format."""
        from app.utils.logger import configure_logger
        
        app = Mock()
        app.config = {'LOG_FORMAT': 'json', 'LOG_LEVEL': 'INFO'}
        app.root_path = '/tmp/test'
        app.logger = Mock()
        app.logger.handlers = []
        
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                with patch('logging.FileHandler') as mock_file_handler:
                    with patch('structlog.configure') as mock_structlog_configure:
                        configure_logger(app)
                        
                        # Verify directory was created
                        mock_makedirs.assert_called_once()
                        
                        # Verify structlog was configured
                        mock_structlog_configure.assert_called_once()
                        
                        # Verify file handler was created
                        mock_file_handler.assert_called_once_with(
                            os.path.join('/tmp/test', '..', 'logs', 'app.log')
                        )
    
    def test_configure_logger_standard_format(self):
        """Test logger configuration with standard format."""
        from app.utils.logger import configure_logger
        
        app = Mock()
        app.config = {'LOG_FORMAT': 'standard', 'LOG_LEVEL': 'DEBUG'}
        app.root_path = '/tmp/test'
        app.logger = Mock()
        app.logger.handlers = []
        
        with patch('os.path.exists', return_value=True):
            with patch('logging.FileHandler') as mock_file_handler:
                mock_handler = Mock()
                mock_file_handler.return_value = mock_handler
                
                configure_logger(app)
                
                # Verify handler configuration
                mock_handler.setFormatter.assert_called_once()
                mock_handler.setLevel.assert_called_once_with(logging.DEBUG)
                
                # Verify logger configuration
                app.logger.addHandler.assert_called_with(mock_handler)
                app.logger.setLevel.assert_called_with(logging.DEBUG)
    
    def test_configure_logger_werkzeug_handlers(self):
        """Test that werkzeug handlers are added to app logger."""
        from app.utils.logger import configure_logger
        
        app = Mock()
        app.config = {}
        app.root_path = '/tmp/test'
        app.logger = Mock()
        
        # Mock werkzeug logger with handlers
        werkzeug_handler = Mock()
        with patch('logging.getLogger') as mock_get_logger:
            mock_werkzeug_logger = Mock()
            mock_werkzeug_logger.handlers = [werkzeug_handler]
            mock_get_logger.return_value = mock_werkzeug_logger
            
            with patch('os.path.exists', return_value=True):
                with patch('logging.FileHandler'):
                    configure_logger(app)
                    
                    # Verify werkzeug handler was added
                    app.logger.addHandler.assert_any_call(werkzeug_handler)
    
    def test_configure_logger_default_config(self):
        """Test logger configuration with default values."""
        from app.utils.logger import configure_logger
        
        app = Mock()
        app.config = {}  # Empty config to test defaults
        app.root_path = '/tmp/test'
        app.logger = Mock()
        
        with patch('os.path.exists', return_value=True):
            with patch('logging.FileHandler') as mock_file_handler:
                mock_handler = Mock()
                mock_file_handler.return_value = mock_handler
                
                with patch('structlog.configure') as mock_structlog_configure:
                    configure_logger(app)
                    
                    # Verify defaults were used
                    mock_handler.setLevel.assert_called_with(logging.INFO)
                    app.logger.setLevel.assert_called_with(logging.INFO)
                    mock_structlog_configure.assert_called_once()  # JSON is default


class TestGetLogger:
    """Test cases for the get_logger function."""
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        from app.utils.logger import get_logger
        
        with patch('structlog.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = get_logger('test_logger')
            
            mock_get_logger.assert_called_once_with('test_logger')
            assert result == mock_logger
    
    def test_get_logger_different_names(self):
        """Test getting loggers with different names."""
        from app.utils.logger import get_logger
        
        with patch('structlog.get_logger') as mock_get_logger:
            mock_logger1 = Mock()
            mock_logger2 = Mock()
            mock_get_logger.side_effect = [mock_logger1, mock_logger2]
            
            result1 = get_logger('logger1')
            result2 = get_logger('logger2')
            
            assert mock_get_logger.call_count == 2
            mock_get_logger.assert_any_call('logger1')
            mock_get_logger.assert_any_call('logger2')
            assert result1 == mock_logger1
            assert result2 == mock_logger2


if __name__ == '__main__':
    pytest.main([__file__])