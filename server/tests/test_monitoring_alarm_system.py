"""Comprehensive tests for monitoring alarm system."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone, timedelta
import json


class TestAlarmSystem:
    """Test cases for alarm system."""
    
    @pytest.fixture
    def alarm_config(self):
        """Create alarm configuration."""
        return {
            'cpu_threshold': 80,
            'memory_threshold': 90,
            'disk_threshold': 85,
            'response_time_threshold': 1000,
            'error_rate_threshold': 5,
            'notification_channels': ['email', 'slack']
        }
    
    @pytest.fixture
    def mock_metrics(self):
        """Create mock metrics."""
        return {
            'cpu_usage': 75,
            'memory_usage': 85,
            'disk_usage': 80,
            'response_time': 500,
            'error_rate': 2
        }
    
    def test_alarm_system_init(self, alarm_config):
        """Test alarm system initialization."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        assert alarm_system.config == alarm_config
        assert alarm_system.active_alarms == {}
        assert alarm_system.alarm_history == []
    
    def test_check_cpu_alarm(self, alarm_config):
        """Test CPU usage alarm."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Test normal CPU usage
        assert alarm_system.check_cpu_alarm(70) is False
        
        # Test high CPU usage
        assert alarm_system.check_cpu_alarm(85) is True
        
        # Verify alarm is created
        assert 'cpu_high' in alarm_system.active_alarms
    
    def test_check_memory_alarm(self, alarm_config):
        """Test memory usage alarm."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Test normal memory usage
        assert alarm_system.check_memory_alarm(80) is False
        
        # Test high memory usage
        assert alarm_system.check_memory_alarm(95) is True
        
        # Verify alarm is created
        assert 'memory_high' in alarm_system.active_alarms
    
    def test_check_disk_alarm(self, alarm_config):
        """Test disk usage alarm."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Test normal disk usage
        assert alarm_system.check_disk_alarm(80) is False
        
        # Test high disk usage
        assert alarm_system.check_disk_alarm(90) is True
        
        # Verify alarm is created
        assert 'disk_high' in alarm_system.active_alarms
    
    def test_check_response_time_alarm(self, alarm_config):
        """Test response time alarm."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Test normal response time
        assert alarm_system.check_response_time_alarm(800) is False
        
        # Test slow response time
        assert alarm_system.check_response_time_alarm(1500) is True
        
        # Verify alarm is created
        assert 'response_time_high' in alarm_system.active_alarms
    
    def test_check_error_rate_alarm(self, alarm_config):
        """Test error rate alarm."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Test normal error rate
        assert alarm_system.check_error_rate_alarm(3) is False
        
        # Test high error rate
        assert alarm_system.check_error_rate_alarm(10) is True
        
        # Verify alarm is created
        assert 'error_rate_high' in alarm_system.active_alarms
    
    def test_check_all_alarms(self, alarm_config, mock_metrics):
        """Test checking all alarms at once."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        alarms = alarm_system.check_all_alarms(mock_metrics)
        
        assert isinstance(alarms, list)
        assert len(alarms) >= 0
    
    @patch('app.utils.monitoring.alarm_system.send_notification')
    def test_trigger_alarm(self, mock_send_notification, alarm_config):
        """Test alarm triggering."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        alarm_data = {
            'type': 'cpu_high',
            'severity': 'critical',
            'value': 95,
            'threshold': 80,
            'message': 'CPU usage is critically high'
        }
        
        alarm_system.trigger_alarm(alarm_data)
        
        # Verify notification sent
        assert mock_send_notification.call_count == len(alarm_config['notification_channels'])
        
        # Verify alarm is active
        assert 'cpu_high' in alarm_system.active_alarms
        
        # Verify alarm in history
        assert len(alarm_system.alarm_history) == 1
    
    def test_resolve_alarm(self, alarm_config):
        """Test alarm resolution."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Create an active alarm
        alarm_system.active_alarms['cpu_high'] = {
            'type': 'cpu_high',
            'triggered_at': datetime.now(timezone.utc),
            'severity': 'critical'
        }
        
        # Resolve the alarm
        alarm_system.resolve_alarm('cpu_high')
        
        # Verify alarm is resolved
        assert 'cpu_high' not in alarm_system.active_alarms
    
    def test_get_active_alarms(self, alarm_config):
        """Test getting active alarms."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Add some active alarms
        alarm_system.active_alarms = {
            'cpu_high': {'type': 'cpu_high', 'severity': 'critical'},
            'memory_high': {'type': 'memory_high', 'severity': 'warning'}
        }
        
        active = alarm_system.get_active_alarms()
        
        assert len(active) == 2
        assert any(a['type'] == 'cpu_high' for a in active)
        assert any(a['type'] == 'memory_high' for a in active)
    
    def test_get_alarm_history(self, alarm_config):
        """Test getting alarm history."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Add alarm history
        alarm_system.alarm_history = [
            {
                'type': 'cpu_high',
                'triggered_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'type': 'memory_high',
                'triggered_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'resolved_at': None
            }
        ]
        
        history = alarm_system.get_alarm_history(hours=24)
        
        assert len(history) == 2
    
    def test_alarm_escalation(self, alarm_config):
        """Test alarm escalation."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Create alarm that needs escalation
        alarm_system.active_alarms['cpu_high'] = {
            'type': 'cpu_high',
            'triggered_at': datetime.now(timezone.utc) - timedelta(hours=2),
            'severity': 'warning',
            'escalated': False
        }
        
        # Check for escalation
        alarm_system.check_escalations()
        
        # Verify alarm was escalated
        assert alarm_system.active_alarms['cpu_high']['escalated'] is True
        assert alarm_system.active_alarms['cpu_high']['severity'] == 'critical'
    
    def test_alarm_suppression(self, alarm_config):
        """Test alarm suppression."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Suppress an alarm type
        alarm_system.suppress_alarm('cpu_high', minutes=30)
        
        # Try to trigger suppressed alarm
        result = alarm_system.check_cpu_alarm(95)
        
        # Should not trigger due to suppression
        assert result is False
        assert 'cpu_high' not in alarm_system.active_alarms
    
    def test_alarm_grouping(self, alarm_config):
        """Test alarm grouping."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Create multiple related alarms
        alarm_system.active_alarms = {
            'cpu_high_server1': {'type': 'cpu_high', 'server': 'server1'},
            'cpu_high_server2': {'type': 'cpu_high', 'server': 'server2'},
            'memory_high_server1': {'type': 'memory_high', 'server': 'server1'}
        }
        
        # Group alarms
        grouped = alarm_system.group_alarms()
        
        assert 'cpu_high' in grouped
        assert len(grouped['cpu_high']) == 2
        assert 'memory_high' in grouped
        assert len(grouped['memory_high']) == 1
    
    def test_alarm_correlation(self, alarm_config):
        """Test alarm correlation."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Create correlated alarms
        alarm_system.active_alarms = {
            'cpu_high': {'type': 'cpu_high', 'triggered_at': datetime.now(timezone.utc)},
            'memory_high': {'type': 'memory_high', 'triggered_at': datetime.now(timezone.utc)},
            'response_time_high': {'type': 'response_time_high', 'triggered_at': datetime.now(timezone.utc)}
        }
        
        # Find correlations
        correlations = alarm_system.find_correlations()
        
        assert len(correlations) > 0
        assert any(c['correlation_type'] == 'resource_exhaustion' for c in correlations)
    
    def test_alarm_rules_engine(self, alarm_config):
        """Test alarm rules engine."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Define custom rules
        rules = [
            {
                'name': 'high_load',
                'conditions': [
                    {'metric': 'cpu_usage', 'operator': '>', 'value': 80},
                    {'metric': 'memory_usage', 'operator': '>', 'value': 85}
                ],
                'action': 'trigger_high_load_alarm'
            }
        ]
        
        alarm_system.add_rules(rules)
        
        # Evaluate rules
        metrics = {'cpu_usage': 85, 'memory_usage': 90}
        triggered = alarm_system.evaluate_rules(metrics)
        
        assert len(triggered) == 1
        assert triggered[0]['name'] == 'high_load'
    
    @patch('app.utils.monitoring.alarm_system.db')
    def test_alarm_persistence(self, mock_db, alarm_config):
        """Test alarm persistence to database."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Save alarm to database
        alarm_data = {
            'type': 'cpu_high',
            'severity': 'critical',
            'value': 95,
            'threshold': 80
        }
        
        alarm_system.save_alarm(alarm_data)
        
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    def test_alarm_analytics(self, alarm_config):
        """Test alarm analytics."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Add historical data
        alarm_system.alarm_history = [
            {'type': 'cpu_high', 'triggered_at': datetime.now(timezone.utc) - timedelta(days=i)}
            for i in range(30)
        ]
        
        # Get analytics
        analytics = alarm_system.get_alarm_analytics()
        
        assert 'total_alarms' in analytics
        assert 'alarms_by_type' in analytics
        assert 'alarms_by_day' in analytics
        assert analytics['total_alarms'] == 30
    
    def test_alarm_webhooks(self, alarm_config):
        """Test alarm webhooks."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Configure webhooks
        webhooks = [
            {'url': 'https://example.com/webhook', 'events': ['cpu_high', 'memory_high']},
            {'url': 'https://slack.com/webhook', 'events': ['*']}
        ]
        
        alarm_system.configure_webhooks(webhooks)
        
        with patch('requests.post') as mock_post:
            alarm_system.send_webhook_notification('cpu_high', {'value': 95})
            
            # Should send to both webhooks
            assert mock_post.call_count == 2
    
    def test_alarm_dashboard_data(self, alarm_config):
        """Test alarm dashboard data generation."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        alarm_system = AlarmSystem(alarm_config)
        
        # Add various alarms
        alarm_system.active_alarms = {
            'cpu_high': {'severity': 'critical'},
            'memory_high': {'severity': 'warning'},
            'disk_high': {'severity': 'warning'}
        }
        
        dashboard_data = alarm_system.get_dashboard_data()
        
        assert dashboard_data['total_active'] == 3
        assert dashboard_data['critical_count'] == 1
        assert dashboard_data['warning_count'] == 2
    
    def test_alarm_integration(self, alarm_config):
        """Test alarm system integration."""
        from app.utils.monitoring.alarm_system import AlarmSystem
        
        with patch('app.utils.monitoring.alarm_system.get_system_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'cpu_usage': 95,
                'memory_usage': 92,
                'disk_usage': 88,
                'response_time': 1200,
                'error_rate': 8
            }
            
            alarm_system = AlarmSystem(alarm_config)
            
            # Run full monitoring cycle
            alarm_system.monitor()
            
            # Should have multiple active alarms
            assert len(alarm_system.active_alarms) >= 3
            
            # Check specific alarms
            assert 'cpu_high' in alarm_system.active_alarms
            assert 'memory_high' in alarm_system.active_alarms
            assert 'error_rate_high' in alarm_system.active_alarms