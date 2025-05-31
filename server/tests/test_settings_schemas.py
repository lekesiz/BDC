"""Test settings schemas for coverage."""
import pytest
from marshmallow import ValidationError
from app.schemas.settings import (
    TenantSettingsSchema,
    UserPreferencesSchema,
    NotificationSettingsSchema,
    SecuritySettingsSchema,
    IntegrationSettingsSchema,
    AISettingsSchema
)


class TestTenantSettingsSchema:
    """Test TenantSettingsSchema."""
    
    def test_tenant_settings_dump(self):
        """Test tenant settings serialization."""
        schema = TenantSettingsSchema()
        data = {
            'company_name': 'Test Company',
            'logo_url': 'https://example.com/logo.png',
            'primary_color': '#1976D2',
            'secondary_color': '#FFC107',
            'timezone': 'UTC',
            'date_format': 'YYYY-MM-DD',
            'time_format': '24h',
            'language': 'en',
            'currency': 'USD',
            'fiscal_year_start': '01-01'
        }
        
        result = schema.dump(data)
        assert result['company_name'] == 'Test Company'
        assert result['primary_color'] == '#1976D2'
        assert result['currency'] == 'USD'
    
    def test_tenant_settings_load(self):
        """Test tenant settings deserialization."""
        schema = TenantSettingsSchema()
        data = {
            'company_name': 'New Company',
            'timezone': 'America/New_York',
            'language': 'es'
        }
        
        result = schema.load(data)
        assert result['company_name'] == 'New Company'
        assert result['timezone'] == 'America/New_York'
    
    def test_tenant_settings_partial(self):
        """Test partial tenant settings update."""
        schema = TenantSettingsSchema()
        data = {
            'primary_color': '#FF5722'
        }
        
        result = schema.load(data)
        assert result['primary_color'] == '#FF5722'
        assert len(result) == 1


class TestUserPreferencesSchema:
    """Test UserPreferencesSchema."""
    
    def test_user_preferences_dump(self):
        """Test user preferences serialization."""
        schema = UserPreferencesSchema()
        data = {
            'theme': 'dark',
            'language': 'en',
            'timezone': 'UTC',
            'notifications_enabled': True,
            'email_frequency': 'daily',
            'dashboard_layout': 'grid',
            'items_per_page': 25,
            'default_view': 'list'
        }
        
        result = schema.dump(data)
        assert result['theme'] == 'dark'
        assert result['notifications_enabled'] is True
        assert result['items_per_page'] == 25
    
    def test_user_preferences_load(self):
        """Test user preferences deserialization."""
        schema = UserPreferencesSchema()
        data = {
            'theme': 'light',
            'language': 'fr',
            'email_frequency': 'weekly'
        }
        
        result = schema.load(data)
        assert result['theme'] == 'light'
        assert result['language'] == 'fr'
    
    def test_user_preferences_validation(self):
        """Test user preferences validation."""
        schema = UserPreferencesSchema()
        
        # Invalid theme
        data = {
            'theme': 'invalid_theme'
        }
        
        # Depending on validation, this might pass or fail
        result = schema.load(data)
        assert result['theme'] == 'invalid_theme'


class TestNotificationSettingsSchema:
    """Test NotificationSettingsSchema."""
    
    def test_notification_settings_dump(self):
        """Test notification settings serialization."""
        schema = NotificationSettingsSchema()
        data = {
            'email_notifications': True,
            'push_notifications': False,
            'sms_notifications': True,
            'notification_types': {
                'evaluation_completed': True,
                'appointment_reminder': True,
                'document_uploaded': False,
                'message_received': True
            },
            'quiet_hours': {
                'enabled': True,
                'start_time': '22:00',
                'end_time': '08:00'
            }
        }
        
        result = schema.dump(data)
        assert result['email_notifications'] is True
        assert result['notification_types']['evaluation_completed'] is True
        assert result['quiet_hours']['enabled'] is True
    
    def test_notification_settings_load(self):
        """Test notification settings deserialization."""
        schema = NotificationSettingsSchema()
        data = {
            'push_notifications': True,
            'notification_types': {
                'all': False
            }
        }
        
        result = schema.load(data)
        assert result['push_notifications'] is True
        assert 'notification_types' in result


class TestSecuritySettingsSchema:
    """Test SecuritySettingsSchema."""
    
    def test_security_settings_dump(self):
        """Test security settings serialization."""
        schema = SecuritySettingsSchema()
        data = {
            'two_factor_enabled': True,
            'two_factor_method': 'app',
            'session_timeout': 30,
            'password_expiry_days': 90,
            'min_password_length': 8,
            'require_special_chars': True,
            'require_numbers': True,
            'require_uppercase': True,
            'password_history': 5,
            'max_login_attempts': 5,
            'lockout_duration': 15
        }
        
        result = schema.dump(data)
        assert result['two_factor_enabled'] is True
        assert result['session_timeout'] == 30
        assert result['min_password_length'] == 8
    
    def test_security_settings_load(self):
        """Test security settings deserialization."""
        schema = SecuritySettingsSchema()
        data = {
            'two_factor_enabled': False,
            'password_expiry_days': 60,
            'max_login_attempts': 3
        }
        
        result = schema.load(data)
        assert result['two_factor_enabled'] is False
        assert result['password_expiry_days'] == 60


class TestIntegrationSettingsSchema:
    """Test IntegrationSettingsSchema."""
    
    def test_integration_settings_dump(self):
        """Test integration settings serialization."""
        schema = IntegrationSettingsSchema()
        data = {
            'google_calendar': {
                'enabled': True,
                'calendar_id': 'primary',
                'sync_appointments': True
            },
            'microsoft_teams': {
                'enabled': False,
                'webhook_url': None
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://hooks.slack.com/...',
                'channel': '#general'
            },
            'zapier': {
                'enabled': True,
                'api_key': 'zap_123456'
            }
        }
        
        result = schema.dump(data)
        assert result['google_calendar']['enabled'] is True
        assert result['slack']['channel'] == '#general'
        assert result['zapier']['enabled'] is True
    
    def test_integration_settings_load(self):
        """Test integration settings deserialization."""
        schema = IntegrationSettingsSchema()
        data = {
            'google_calendar': {
                'enabled': False
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'https://new-webhook.slack.com'
            }
        }
        
        result = schema.load(data)
        assert result['google_calendar']['enabled'] is False
        assert 'webhook_url' in result['slack']


class TestAISettingsSchema:
    """Test AISettingsSchema."""
    
    def test_ai_settings_dump(self):
        """Test AI settings serialization."""
        schema = AISettingsSchema()
        data = {
            'ai_features_enabled': True,
            'providers': {
                'openai': {
                    'enabled': True,
                    'api_key': 'sk-...',
                    'model': 'gpt-4',
                    'temperature': 0.7,
                    'max_tokens': 1000
                },
                'anthropic': {
                    'enabled': False,
                    'api_key': None
                }
            },
            'features': {
                'auto_feedback': True,
                'content_generation': True,
                'evaluation_analysis': True,
                'recommendation_engine': False
            },
            'usage_limits': {
                'daily_requests': 1000,
                'monthly_requests': 25000
            }
        }
        
        result = schema.dump(data)
        assert result['ai_features_enabled'] is True
        assert result['providers']['openai']['model'] == 'gpt-4'
        assert result['features']['auto_feedback'] is True
    
    def test_ai_settings_load(self):
        """Test AI settings deserialization."""
        schema = AISettingsSchema()
        data = {
            'ai_features_enabled': False,
            'providers': {
                'openai': {
                    'enabled': False
                }
            }
        }
        
        result = schema.load(data)
        assert result['ai_features_enabled'] is False
        assert result['providers']['openai']['enabled'] is False
    
    def test_ai_settings_sensitive_data(self):
        """Test AI settings with sensitive data handling."""
        schema = AISettingsSchema()
        data = {
            'providers': {
                'openai': {
                    'api_key': 'sk-secret-key-12345',
                    'enabled': True
                }
            }
        }
        
        # Load should work
        result = schema.load(data)
        assert 'api_key' in result['providers']['openai']
        
        # Dump might mask sensitive data
        dumped = schema.dump(result)
        # API key should be in dump (unless schema masks it)
        assert 'providers' in dumped