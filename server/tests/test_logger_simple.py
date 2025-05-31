"""Simple tests for logger utility."""

import pytest
import logging
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from app.utils.logger import RequestFormatter, configure_logger, get_logger


class TestRequestFormatter:
    """Test the RequestFormatter class."""
    
    @patch('app.utils.logger.has_request_context')
    def test_format_without_request_context(self, mock_has_context):
        """Test formatting without request context."""
        mock_has_context.return_value = False
        
        formatter = RequestFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatter.format(record)
        
        assert record.url is None
        assert record.method is None
        assert record.remote_addr is None
        assert record.request_id is None
        assert record.user_id is None
    
    @patch('app.utils.logger.has_request_context')
    @patch('app.utils.logger.request')
    @patch('app.utils.logger.g')
    def test_format_with_request_context(self, mock_g, mock_request, mock_has_context):
        """Test formatting with request context."""
        mock_has_context.return_value = True
        mock_request.url = "http://example.com/test"
        mock_request.method = "GET"
        mock_request.remote_addr = "127.0.0.1"
        mock_g.request_id = "test-req-123"
        mock_g.user_id = 42
        
        formatter = RequestFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatter.format(record)
        
        assert record.url == "http://example.com/test"
        assert record.method == "GET"
        assert record.remote_addr == "127.0.0.1"
        assert record.request_id == "test-req-123"
        assert record.user_id == 42


class TestConfigureLogger:
    """Test the configure_logger function."""
    
    @patch('app.utils.logger.os.makedirs')
    @patch('app.utils.logger.os.path.exists')
    def test_configure_logger_creates_log_dir(self, mock_exists, mock_makedirs):
        """Test that logger configuration creates log directory."""
        mock_exists.return_value = False
        
        app = Mock()
        app.root_path = "/app"
        app.config = {"LOG_LEVEL": "INFO", "LOG_FORMAT": "text"}
        app.logger = Mock()
        
        configure_logger(app)
        
        mock_makedirs.assert_called_once()
    
    @patch('app.utils.logger.os.path.exists')
    @patch('app.utils.logger.logging.FileHandler')
    def test_configure_logger_with_text_format(self, mock_file_handler, mock_exists):
        """Test logger configuration with text format."""
        mock_exists.return_value = True
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        app = Mock()
        app.root_path = "/app"
        app.config = {"LOG_LEVEL": "INFO", "LOG_FORMAT": "text"}
        app.logger = Mock()
        
        configure_logger(app)
        
        mock_file_handler.assert_called_once()
        mock_handler.setFormatter.assert_called_once()
        app.logger.addHandler.assert_called()
    
    @patch('app.utils.logger.os.path.exists')
    @patch('app.utils.logger.logging.FileHandler')
    @patch('app.utils.logger.structlog.configure')
    def test_configure_logger_with_json_format(self, mock_structlog, mock_file_handler, mock_exists):
        """Test logger configuration with JSON format."""
        mock_exists.return_value = True
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        app = Mock()
        app.root_path = "/app"
        app.config = {"LOG_LEVEL": "DEBUG", "LOG_FORMAT": "json"}
        app.logger = Mock()
        
        configure_logger(app)
        
        mock_structlog.assert_called_once()
        mock_file_handler.assert_called_once()
        mock_handler.setFormatter.assert_called_once()


class TestGetLogger:
    """Test the get_logger function."""
    
    @patch('app.utils.logger.structlog.get_logger')
    def test_get_logger(self, mock_structlog_get_logger):
        """Test getting a logger instance."""
        mock_logger = Mock()
        mock_structlog_get_logger.return_value = mock_logger
        
        logger = get_logger("test_logger")
        
        mock_structlog_get_logger.assert_called_once_with("test_logger")
        assert logger == mock_logger


class TestJsonFormatter:
    """Test the JsonFormatter nested class."""
    
    @patch('app.utils.logger.os.path.exists')
    @patch('app.utils.logger.logging.FileHandler')
    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.has_request_context')
    def test_json_formatter_without_request(self, mock_has_context, mock_structlog, mock_file_handler, mock_exists):
        """Test JSON formatter without request context."""
        mock_exists.return_value = True
        mock_has_context.return_value = False
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        app = Mock()
        app.root_path = "/app"
        app.config = {"LOG_FORMAT": "json"}
        app.logger = Mock()
        
        # Configure logger to create the JsonFormatter
        configure_logger(app)
        
        # Get the formatter that was set
        formatter = mock_handler.setFormatter.call_args[0][0]
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test JSON message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data['level'] == 'INFO'
        assert log_data['message'] == 'Test JSON message'
        assert 'url' not in log_data
        assert 'method' not in log_data