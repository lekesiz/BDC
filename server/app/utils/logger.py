"""Logging utility module."""

import logging
import os
import time
import json
from flask import request, g, has_request_context
import structlog


class RequestFormatter(logging.Formatter):
    """Custom formatter for Flask request logging."""
    
    def format(self, record):
        """Format the record with request-specific information."""
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
            record.request_id = getattr(g, 'request_id', 'no-request-id')
            record.user_id = getattr(g, 'user_id', None)
        else:
            record.url = None
            record.method = None
            record.remote_addr = None
            record.request_id = None
            record.user_id = None
            
        return super().format(record)


def configure_logger(app):
    """
    Configure application logger with structured logging.
    
    Args:
        app (Flask): Flask application
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(app.root_path, '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up log file handler
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = logging.FileHandler(log_file)
    
    # Configure formatter based on log format preference
    if app.config.get('LOG_FORMAT', 'json') == 'json':
        # JSON formatter for structured logging
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Add request information to all log records
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
                    'level': record.levelname,
                    'name': record.name,
                    'message': record.getMessage(),
                }
                
                # Add request context if available
                if has_request_context():
                    log_record.update({
                        'url': request.url,
                        'method': request.method,
                        'ip': request.remote_addr,
                        'request_id': getattr(g, 'request_id', 'no-request-id'),
                        'user_id': getattr(g, 'user_id', None)
                    })
                
                # Add exception info if available
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_record)
        
        formatter = JsonFormatter()
    else:
        # Standard formatter for human-readable logs
        formatter = RequestFormatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s [%(request_id)s] [%(user_id)s]'
        )
    
    # Configure handler
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    
    # Add the file handler to the logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    
    # Make Flask use the app logger for its own logs
    for handler in logging.getLogger('werkzeug').handlers:
        app.logger.addHandler(handler)


def get_logger(name):
    """
    Get a logger instance.
    
    Args:
        name (str): Logger name
        
    Returns:
        Logger: Logger instance
    """
    return structlog.get_logger(name)


# Default logger instance
logger = get_logger(__name__)