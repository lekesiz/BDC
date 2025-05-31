"""Comprehensive tests for error tracking system."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone, timedelta
import json
import traceback


class TestErrorTracking:
    """Test cases for error tracking system."""
    
    @pytest.fixture
    def error_config(self):
        """Create error tracking configuration."""
        return {
            'enabled': True,
            'capture_locals': True,
            'capture_request': True,
            'sanitize_data': True,
            'error_rate_limit': 100,
            'grouping_enabled': True,
            'notification_threshold': 10,
            'storage_backend': 'database',
            'retention_days': 30
        }
    
    @pytest.fixture
    def sample_error(self):
        """Create sample error data."""
        return {
            'type': 'ValueError',
            'message': 'Invalid input provided',
            'traceback': 'Traceback (most recent call last):\n  File "app.py", line 10',
            'timestamp': datetime.now(timezone.utc),
            'user_id': 123,
            'request_url': '/api/users/123',
            'request_method': 'POST',
            'request_data': {'name': 'test'},
            'environment': 'production',
            'server_name': 'web-01',
            'additional_data': {'version': '1.0.0'}
        }
    
    def test_error_tracker_init(self, error_config):
        """Test error tracker initialization."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        assert tracker.config == error_config
        assert tracker.enabled is True
        assert tracker.error_count == 0
        assert tracker.error_groups == {}
    
    def test_capture_error(self, error_config, sample_error):
        """Test capturing an error."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        error_id = tracker.capture_error(
            exception=ValueError("Test error"),
            context=sample_error
        )
        
        assert error_id is not None
        assert tracker.error_count == 1
        assert len(tracker.get_recent_errors()) == 1
    
    def test_capture_error_with_locals(self, error_config):
        """Test capturing error with local variables."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        def failing_function():
            local_var = "test_value"
            secret_key = "secret123"
            raise ValueError("Test error")
        
        try:
            failing_function()
        except ValueError as e:
            error_id = tracker.capture_exception(e)
            
            error_data = tracker.get_error(error_id)
            assert 'locals' in error_data
            assert 'local_var' in error_data['locals']
            # Secret should be sanitized
            assert error_data['locals'].get('secret_key') != 'secret123'
    
    def test_error_grouping(self, error_config):
        """Test error grouping functionality."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture similar errors
        for i in range(5):
            tracker.capture_error(
                exception=ValueError("Same error"),
                context={'iteration': i}
            )
        
        groups = tracker.get_error_groups()
        
        assert len(groups) == 1
        assert groups[0]['count'] == 5
        assert groups[0]['type'] == 'ValueError'
    
    def test_error_rate_limiting(self, error_config):
        """Test error rate limiting."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        error_config['error_rate_limit'] = 5
        tracker = ErrorTracker(error_config)
        
        # Capture errors up to limit
        for i in range(10):
            result = tracker.capture_error(
                exception=ValueError(f"Error {i}"),
                context={}
            )
            
            if i < 5:
                assert result is not None
            else:
                # Should be rate limited
                assert result is None or result == 'rate_limited'
    
    def test_error_notification(self, error_config):
        """Test error notification triggering."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        with patch.object(tracker, 'send_notification') as mock_notify:
            # Capture errors up to threshold
            for i in range(11):
                tracker.capture_error(
                    exception=ValueError("Critical error"),
                    context={'severity': 'high'}
                )
            
            # Should trigger notification
            mock_notify.assert_called()
    
    def test_error_sanitization(self, error_config):
        """Test sensitive data sanitization."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        sensitive_context = {
            'password': 'secret123',
            'api_key': 'key-12345',
            'credit_card': '1234-5678-9012-3456',
            'ssn': '123-45-6789',
            'normal_data': 'this is safe'
        }
        
        error_id = tracker.capture_error(
            exception=ValueError("Test"),
            context=sensitive_context
        )
        
        error_data = tracker.get_error(error_id)
        
        assert error_data['context']['password'] == '[REDACTED]'
        assert error_data['context']['api_key'] == '[REDACTED]'
        assert error_data['context']['credit_card'] == '[REDACTED]'
        assert error_data['context']['ssn'] == '[REDACTED]'
        assert error_data['context']['normal_data'] == 'this is safe'
    
    def test_error_storage_database(self, error_config):
        """Test storing errors in database."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        with patch('app.utils.monitoring.error_tracking.db') as mock_db:
            error_id = tracker.capture_error(
                exception=ValueError("Test"),
                context={}
            )
            
            tracker.save_to_database(error_id)
            
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    def test_error_storage_file(self, error_config):
        """Test storing errors in file system."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        error_config['storage_backend'] = 'file'
        tracker = ErrorTracker(error_config)
        
        with patch('builtins.open', create=True) as mock_open:
            error_id = tracker.capture_error(
                exception=ValueError("Test"),
                context={}
            )
            
            tracker.save_to_file(error_id)
            
            mock_open.assert_called()
    
    def test_error_retrieval(self, error_config):
        """Test error retrieval and filtering."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture various errors
        tracker.capture_error(ValueError("Error 1"), {'severity': 'low'})
        tracker.capture_error(TypeError("Error 2"), {'severity': 'high'})
        tracker.capture_error(ValueError("Error 3"), {'severity': 'high'})
        
        # Test filtering
        high_severity = tracker.get_errors_by_filter(severity='high')
        assert len(high_severity) == 2
        
        value_errors = tracker.get_errors_by_filter(error_type='ValueError')
        assert len(value_errors) == 2
    
    def test_error_statistics(self, error_config):
        """Test error statistics generation."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture various errors
        for i in range(10):
            tracker.capture_error(ValueError("Error"), {})
        for i in range(5):
            tracker.capture_error(TypeError("Error"), {})
        
        stats = tracker.get_error_statistics()
        
        assert stats['total_errors'] == 15
        assert stats['error_types']['ValueError'] == 10
        assert stats['error_types']['TypeError'] == 5
        assert 'errors_per_hour' in stats
        assert 'top_errors' in stats
    
    def test_error_cleanup(self, error_config):
        """Test old error cleanup."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Add old errors
        old_date = datetime.now(timezone.utc) - timedelta(days=40)
        tracker.errors = {
            'old_error': {'timestamp': old_date},
            'recent_error': {'timestamp': datetime.now(timezone.utc)}
        }
        
        tracker.cleanup_old_errors()
        
        assert 'old_error' not in tracker.errors
        assert 'recent_error' in tracker.errors
    
    def test_error_context_enrichment(self, error_config):
        """Test automatic context enrichment."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        with patch('app.utils.monitoring.error_tracking.request') as mock_request:
            mock_request.url = 'http://example.com/test'
            mock_request.method = 'GET'
            mock_request.headers = {'User-Agent': 'TestAgent'}
            mock_request.remote_addr = '192.168.1.1'
            
            error_id = tracker.capture_error(ValueError("Test"), {})
            error_data = tracker.get_error(error_id)
            
            assert error_data['request_url'] == 'http://example.com/test'
            assert error_data['request_method'] == 'GET'
            assert error_data['user_agent'] == 'TestAgent'
            assert error_data['ip_address'] == '192.168.1.1'
    
    def test_error_fingerprinting(self, error_config):
        """Test error fingerprinting for deduplication."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Same errors should have same fingerprint
        fp1 = tracker.generate_fingerprint(ValueError("Test error"), "traceback1")
        fp2 = tracker.generate_fingerprint(ValueError("Test error"), "traceback1")
        
        assert fp1 == fp2
        
        # Different errors should have different fingerprints
        fp3 = tracker.generate_fingerprint(TypeError("Different error"), "traceback2")
        
        assert fp1 != fp3
    
    def test_error_webhook_integration(self, error_config):
        """Test webhook integration for errors."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        tracker.configure_webhook('https://example.com/webhook')
        
        with patch('requests.post') as mock_post:
            tracker.capture_error(ValueError("Critical error"), {'severity': 'critical'})
            tracker.send_webhook_notification()
            
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert 'ValueError' in str(call_args)
    
    def test_error_dashboard_data(self, error_config):
        """Test error dashboard data generation."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture various errors
        for i in range(20):
            error_type = ValueError if i % 2 == 0 else TypeError
            tracker.capture_error(error_type("Error"), {'user_id': i % 5})
        
        dashboard = tracker.get_dashboard_data()
        
        assert dashboard['total_errors'] == 20
        assert dashboard['unique_errors'] == 2
        assert dashboard['affected_users'] == 5
        assert 'error_trend' in dashboard
        assert 'top_errors' in dashboard
    
    def test_error_correlation(self, error_config):
        """Test error correlation analysis."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture correlated errors
        base_time = datetime.now(timezone.utc)
        for i in range(5):
            tracker.capture_error(
                ValueError("Database connection failed"),
                {'timestamp': base_time + timedelta(seconds=i), 'component': 'database'}
            )
            tracker.capture_error(
                RuntimeError("Service unavailable"),
                {'timestamp': base_time + timedelta(seconds=i), 'component': 'api'}
            )
        
        correlations = tracker.find_error_correlations()
        
        assert len(correlations) > 0
        assert any(c['correlation_score'] > 0.8 for c in correlations)
    
    def test_error_export(self, error_config):
        """Test error data export."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture some errors
        for i in range(5):
            tracker.capture_error(ValueError(f"Error {i}"), {})
        
        # Test CSV export
        csv_data = tracker.export_errors('csv')
        assert 'ValueError' in csv_data
        
        # Test JSON export
        json_data = tracker.export_errors('json')
        data = json.loads(json_data)
        assert len(data['errors']) == 5
    
    def test_error_recovery_suggestions(self, error_config):
        """Test automatic recovery suggestions."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Known error patterns
        error_id = tracker.capture_error(
            ConnectionError("Database connection failed"),
            {'component': 'database'}
        )
        
        suggestions = tracker.get_recovery_suggestions(error_id)
        
        assert len(suggestions) > 0
        assert any('restart' in s.lower() for s in suggestions)
        assert any('connection pool' in s.lower() for s in suggestions)
    
    def test_error_impact_analysis(self, error_config):
        """Test error impact analysis."""
        from app.utils.monitoring.error_tracking import ErrorTracker
        
        tracker = ErrorTracker(error_config)
        
        # Capture errors with user impact
        for user_id in range(100):
            if user_id < 20:  # 20% of users affected
                tracker.capture_error(
                    ValueError("Feature broken"),
                    {'user_id': user_id, 'feature': 'payment'}
                )
        
        impact = tracker.analyze_error_impact('payment')
        
        assert impact['affected_users'] == 20
        assert impact['impact_percentage'] == 20.0
        assert impact['severity'] == 'high'  # Payment errors are high severity