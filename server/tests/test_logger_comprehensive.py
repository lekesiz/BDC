"""Comprehensive tests for logger utility module."""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import logging
import os
from app.utils.logger import (
    RequestFormatter,
    configure_logger,
    get_request_id,
    set_request_id
)


class TestRequestFormatter:
    """Test RequestFormatter class."""
    
    def test_request_formatter_basic(self):
        """Test basic formatter functionality."""
        formatter = RequestFormatter('%(message)s')
        
        # Create a log record
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=10,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        assert 'Test message' in formatted
    
    @patch('app.utils.logger.g')
    @patch('app.utils.logger.has_request_context')
    def test_request_formatter_with_request_context(self, mock_has_context, mock_g):
        """Test formatter with request context."""
        # Mock request context
        mock_has_context.return_value = True
        mock_g.request_id = 'test-req-123'
        
        formatter = RequestFormatter('%(request_id)s - %(message)s')
        
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
        assert 'test-req-123' in formatted
        assert 'Test message' in formatted
    
    @patch('app.utils.logger.has_request_context')
    def test_request_formatter_without_request_context(self, mock_has_context):
        """Test formatter without request context."""
        # No request context
        mock_has_context.return_value = False
        
        formatter = RequestFormatter('%(request_id)s - %(message)s')
        
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
        # Should use default 'no-request-id'
        assert 'no-request-id' in formatted
        assert 'Test message' in formatted


class TestConfigureLogger:
    """Test configure_logger function."""
    
    @patch('app.utils.logger.structlog')
    @patch('app.utils.logger.logging.FileHandler')
    @patch('app.utils.logger.os.makedirs')
    @patch('app.utils.logger.os.path.exists')
    def test_configure_logger_json_format(self, mock_exists, mock_makedirs, mock_file_handler, mock_structlog):
        """Test logger configuration with JSON format."""
        # Mock app
        app = Mock()
        app.root_path = '/app'
        app.config = {
            'LOG_FORMAT': 'json',
            'LOG_LEVEL': 'INFO'
        }
        app.logger = Mock(spec=logging.Logger)
        
        # Mock os.path.exists to return False (directory doesn't exist)
        mock_exists.return_value = False
        
        # Mock file handler
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        # Configure logger
        configure_logger(app)
        
        # Should create logs directory
        mock_makedirs.assert_called_once()
        # Should create file handler
        mock_file_handler.assert_called_once()
        # Should configure structlog for JSON
        mock_structlog.configure.assert_called_once()
        # Should add handler to logger
        app.logger.addHandler.assert_called_with(mock_handler)
        # Should set log level
        app.logger.setLevel.assert_called_with(logging.INFO)
    
    @patch('app.utils.logger.logging.FileHandler')
    @patch('app.utils.logger.os.makedirs')
    @patch('app.utils.logger.os.path.exists')
    def test_configure_logger_text_format(self, mock_exists, mock_makedirs, mock_file_handler):
        """Test logger configuration with text format."""
        # Mock app
        app = Mock()
        app.root_path = '/app'
        app.config = {
            'LOG_FORMAT': 'text',
            'LOG_LEVEL': 'DEBUG'
        }
        app.logger = Mock(spec=logging.Logger)
        
        # Mock os.path.exists to return True (directory exists)
        mock_exists.return_value = True
        
        # Mock file handler
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        # Configure logger
        configure_logger(app)
        
        # Should not create logs directory (already exists)
        mock_makedirs.assert_not_called()
        # Should create file handler
        mock_file_handler.assert_called_once()
        # Should set formatter on handler
        mock_handler.setFormatter.assert_called_once()
        # Formatter should be RequestFormatter
        formatter = mock_handler.setFormatter.call_args[0][0]
        assert isinstance(formatter, RequestFormatter)
        # Should set log level to DEBUG
        app.logger.setLevel.assert_called_with(logging.DEBUG)
    
    @patch('app.utils.logger.logging.StreamHandler')
    @patch('app.utils.logger.logging.FileHandler')
    @patch('app.utils.logger.os.path.exists')
    def test_configure_logger_with_stream_handler(self, mock_exists, mock_file_handler, mock_stream_handler):
        """Test logger configuration adds stream handler."""
        # Mock app
        app = Mock()
        app.root_path = '/app'
        app.config = {
            'LOG_FORMAT': 'text',
            'LOG_LEVEL': 'WARNING'
        }
        app.logger = Mock(spec=logging.Logger)
        mock_exists.return_value = True
        
        # Mock handlers
        mock_file = Mock()
        mock_stream = Mock()
        mock_file_handler.return_value = mock_file
        mock_stream_handler.return_value = mock_stream
        
        # Configure logger
        configure_logger(app)
        
        # Should create both handlers
        mock_file_handler.assert_called_once()
        mock_stream_handler.assert_called_once()
        # Should add both handlers
        assert app.logger.addHandler.call_count == 2
        # Should set level to WARNING
        app.logger.setLevel.assert_called_with(logging.WARNING)


class TestRequestIdFunctions:
    """Test get_request_id and set_request_id functions."""
    
    @patch('app.utils.logger.g')
    @patch('app.utils.logger.has_request_context')
    def test_get_request_id_with_context(self, mock_has_context, mock_g):
        """Test getting request ID with request context."""
        mock_has_context.return_value = True
        mock_g.request_id = 'req-123'
        
        result = get_request_id()
        assert result == 'req-123'
    
    @patch('app.utils.logger.g')
    @patch('app.utils.logger.has_request_context')
    def test_get_request_id_without_context(self, mock_has_context, mock_g):
        """Test getting request ID without request context."""
        mock_has_context.return_value = False
        
        result = get_request_id()
        assert result is None
    
    @patch('app.utils.logger.g')
    @patch('app.utils.logger.has_request_context')
    def test_get_request_id_no_attribute(self, mock_has_context, mock_g):
        """Test getting request ID when attribute doesn't exist."""
        mock_has_context.return_value = True
        # Simulate AttributeError
        del mock_g.request_id
        
        result = get_request_id()
        assert result is None
    
    @patch('app.utils.logger.g')
    @patch('app.utils.logger.has_request_context')
    def test_set_request_id_with_context(self, mock_has_context, mock_g):
        """Test setting request ID with request context."""
        mock_has_context.return_value = True
        
        set_request_id('new-req-456')
        assert mock_g.request_id == 'new-req-456'
    
    @patch('app.utils.logger.has_request_context')
    def test_set_request_id_without_context(self, mock_has_context):
        """Test setting request ID without request context."""
        mock_has_context.return_value = False
        
        # Should not raise error
        set_request_id('new-req-789')
        # Nothing to assert, just ensure no exception


class TestLoggerEdgeCases:
    """Test edge cases and error scenarios."""
    
    @patch('app.utils.logger.logging.FileHandler')
    @patch('app.utils.logger.os.makedirs')
    def test_configure_logger_makedirs_error(self, mock_makedirs, mock_file_handler):
        """Test logger configuration when makedirs fails."""
        # Mock app
        app = Mock()
        app.root_path = '/app'
        app.config = {'LOG_LEVEL': 'INFO'}
        app.logger = Mock(spec=logging.Logger)
        
        # Make makedirs fail
        mock_makedirs.side_effect = OSError('Permission denied')
        
        # Should not raise exception
        configure_logger(app)
        
        # Should still try to create file handler
        mock_file_handler.assert_called_once()
    
    def test_request_formatter_custom_format(self):
        """Test RequestFormatter with custom format string."""
        formatter = RequestFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s'
        )
        
        record = logging.LogRecord(
            name='app.test',
            level=logging.ERROR,
            pathname='test.py',
            lineno=10,
            msg='Error occurred',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert 'app.test' in formatted
        assert 'ERROR' in formatted
        assert 'Error occurred' in formatted
        assert 'no-request-id' in formatted  # No request context