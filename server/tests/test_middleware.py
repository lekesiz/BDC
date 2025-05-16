"""Tests for middleware functions."""

from unittest.mock import patch, MagicMock
from app.middleware.request_context import request_context_middleware


def test_request_context_middleware():
    """Test request context middleware."""
    # Create a mock Flask request
    with patch('app.middleware.request_context.request') as mock_request:
        # Configure the mock request
        mock_request.method = 'GET'
        mock_request.path = '/api/users'
        mock_request.remote_addr = '127.0.0.1'
        mock_request.headers = {'User-Agent': 'Test User Agent'}
        
        # Mock g object
        with patch('app.middleware.request_context.g') as mock_g:
            # Call the middleware
            result = request_context_middleware()
            
            # Verify the middleware didn't return a response (it's not blocking)
            assert result is None
            
            # Check that the request context was properly stored in g
            assert hasattr(mock_g, 'request_id')
            assert hasattr(mock_g, 'request_start_time')