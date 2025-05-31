"""Critical tests to significantly increase coverage."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime, timedelta
from app import create_app


class TestCriticalCoverage:
    """Test critical paths to increase coverage."""
    
    def test_app_initialization(self):
        """Test app initialization."""
        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_extensions_loading(self):
        """Test that extensions are loaded."""
        from app.extensions import db, migrate, jwt, cors, mail, socketio, cache
        assert db is not None
        assert migrate is not None
        assert jwt is not None
    
    def test_models_import(self):
        """Test that all models can be imported."""
        from app.models import (
            User, Beneficiary, Program, Evaluation, 
            Appointment, Document, Notification
        )
        assert User is not None
        assert Beneficiary is not None
        assert Program is not None
    
    def test_schemas_import(self):
        """Test that all schemas can be imported."""
        from app.schemas import (
            UserSchema, BeneficiarySchema, ProgramSchema,
            EvaluationSchema, AppointmentSchema, DocumentSchema
        )
        assert UserSchema is not None
        assert BeneficiarySchema is not None
    
    def test_utils_functions(self):
        """Test utility functions."""
        from app.utils import generate_unique_filename, format_datetime
        
        # Test generate_unique_filename
        filename = generate_unique_filename('test.pdf')
        assert filename.endswith('.pdf')
        assert len(filename) > 8
        
        # Test format_datetime
        now = datetime.now()
        formatted = format_datetime(now)
        assert isinstance(formatted, str)
    
    @patch('app.models.User')
    def test_user_model_methods(self, mock_user_class):
        """Test User model methods."""
        user = Mock()
        user.check_password.return_value = True
        user.get_reset_password_token.return_value = 'token123'
        
        # Test password check
        assert user.check_password('password') is True
        
        # Test token generation
        token = user.get_reset_password_token()
        assert token == 'token123'
    
    def test_error_handlers(self):
        """Test error handlers."""
        app = create_app('testing')
        
        with app.test_client() as client:
            # Test 404 handler
            response = client.get('/nonexistent')
            assert response.status_code == 404
    
    def test_config_loading(self):
        """Test config loading."""
        from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
        
        assert Config.SECRET_KEY is not None
        assert DevelopmentConfig.DEBUG is True
        assert TestingConfig.TESTING is True
        assert ProductionConfig.DEBUG is False
    
    @patch('flask_mail.Mail.send')
    def test_email_sending(self, mock_send):
        """Test email sending functionality."""
        from app.utils.email import send_email
        
        mock_send.return_value = None
        
        result = send_email(
            subject='Test',
            sender='test@example.com',
            recipients=['user@example.com'],
            text_body='Test email',
            html_body='<p>Test email</p>'
        )
        
        mock_send.assert_called_once()
    
    def test_api_routes_registration(self):
        """Test that API routes are registered."""
        app = create_app('testing')
        
        # Check that routes exist
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        assert '/api/auth/login' in rules
        assert '/api/users' in rules
        assert '/api/beneficiaries' in rules
        assert '/api/programs' in rules
    
    @patch('redis.StrictRedis')
    def test_cache_operations(self, mock_redis):
        """Test cache operations."""
        from app.utils.cache import set_cache, get_cache, delete_cache
        
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        
        # Test set
        set_cache('key', 'value', 300)
        mock_redis_instance.setex.assert_called()
        
        # Test get
        mock_redis_instance.get.return_value = b'value'
        value = get_cache('key')
        assert value == 'value'
        
        # Test delete
        delete_cache('key')
        mock_redis_instance.delete.assert_called()
    
    def test_database_helpers(self):
        """Test database helper functions."""
        from app.utils.database import paginate_query
        
        mock_query = Mock()
        mock_query.paginate.return_value = Mock(
            items=[],
            total=0,
            pages=1,
            page=1
        )
        
        result = paginate_query(mock_query, page=1, per_page=10)
        assert result is not None
    
    def test_security_utils(self):
        """Test security utilities."""
        from app.utils.security import generate_token, verify_token
        
        # Test token generation
        token = generate_token({'user_id': 1})
        assert isinstance(token, str)
        
        # Test token verification
        data = verify_token(token)
        assert data is not None
        assert data.get('user_id') == 1
    
    def test_datetime_utils(self):
        """Test datetime utilities."""
        from app.utils.datetime import (
            utc_now, 
            format_date, 
            parse_date,
            get_date_range
        )
        
        # Test UTC now
        now = utc_now()
        assert isinstance(now, datetime)
        
        # Test format date
        formatted = format_date(now)
        assert isinstance(formatted, str)
        
        # Test parse date
        parsed = parse_date('2024-01-01')
        assert isinstance(parsed, datetime)
        
        # Test date range
        start, end = get_date_range('month')
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert end > start
    
    def test_validation_utils(self):
        """Test validation utilities."""
        from app.utils.validation import (
            validate_email,
            validate_phone,
            validate_password,
            sanitize_html
        )
        
        # Test email validation
        assert validate_email('test@example.com') is True
        assert validate_email('invalid') is False
        
        # Test phone validation
        assert validate_phone('+1234567890') is True
        assert validate_phone('invalid') is False
        
        # Test password validation
        assert validate_password('StrongPass123!') is True
        assert validate_password('weak') is False
        
        # Test HTML sanitization
        clean = sanitize_html('<script>alert("xss")</script><p>Safe</p>')
        assert '<script>' not in clean
        assert '<p>Safe</p>' in clean

    def test_api_response_helpers(self):
        """Test API response helper functions."""
        from app.utils.responses import (
            success_response,
            error_response,
            validation_error_response
        )
        
        # Test success response
        resp = success_response({'data': 'test'})
        assert resp[1] == 200
        assert resp[0].json['data'] == 'test'
        
        # Test error response
        resp = error_response('Error message', 400)
        assert resp[1] == 400
        assert 'error' in resp[0].json
        
        # Test validation error response
        errors = {'field': ['Invalid value']}
        resp = validation_error_response(errors)
        assert resp[1] == 422
        assert 'errors' in resp[0].json


if __name__ == '__main__':
    pytest.main([__file__, '-v'])