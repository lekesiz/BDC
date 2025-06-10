"""
Configuration Management for Error Handling System.

Provides centralized configuration for all error handling components.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml

from .exceptions import ConfigurationError


class ConfigSource(Enum):
    """Configuration source types."""
    DEFAULT = "default"
    ENVIRONMENT = "environment"
    FILE = "file"
    DICT = "dict"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    timeout: float = 30.0
    enabled: bool = True


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_strategy: str = "exponential"
    backoff_multiplier: float = 2.0
    jitter_type: str = "equal"
    timeout: Optional[float] = None
    enabled: bool = True


@dataclass
class MonitoringConfig:
    """Error monitoring configuration."""
    enabled: bool = True
    metrics_retention_hours: int = 24
    alert_cooldown_minutes: int = 15
    error_rate_threshold: float = 10.0
    critical_error_threshold: int = 1
    database_error_threshold: float = 0.5
    external_service_error_threshold: int = 5


@dataclass
class AlertConfig:
    """Alert configuration."""
    enabled: bool = True
    channels: List[str] = field(default_factory=lambda: ["log"])
    email_enabled: bool = False
    email_recipients: List[str] = field(default_factory=list)
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    webhook_enabled: bool = False
    webhook_url: Optional[str] = None


@dataclass
class UserMessagesConfig:
    """User messages configuration."""
    default_locale: str = "en"
    supported_locales: List[str] = field(default_factory=lambda: ["en", "es"])
    include_technical_details: bool = False
    custom_message_file: Optional[str] = None


@dataclass
class RecoveryConfig:
    """Error recovery configuration."""
    enabled: bool = True
    max_recovery_attempts: int = 3
    cache_fallback_enabled: bool = True
    cache_ttl_seconds: int = 3600
    graceful_degradation_enabled: bool = True
    alternative_services_enabled: bool = True


@dataclass
class MiddlewareConfig:
    """Middleware configuration."""
    enabled: bool = True
    include_stack_trace: bool = False
    log_request_data: bool = True
    redact_sensitive_data: bool = True
    response_headers_enabled: bool = True


@dataclass
class ErrorHandlingConfig:
    """Main error handling configuration."""
    # Global settings
    enabled: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Component configurations
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    user_messages: UserMessagesConfig = field(default_factory=UserMessagesConfig)
    recovery: RecoveryConfig = field(default_factory=RecoveryConfig)
    middleware: MiddlewareConfig = field(default_factory=MiddlewareConfig)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Manages error handling configuration from multiple sources."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._config = ErrorHandlingConfig()
        self._config_sources: List[ConfigSource] = []
        self._watchers: List[callable] = []
    
    def load_default_config(self) -> 'ConfigManager':
        """Load default configuration."""
        self._config = ErrorHandlingConfig()
        self._config_sources.append(ConfigSource.DEFAULT)
        self.logger.info("Loaded default error handling configuration")
        return self
    
    def load_from_environment(self, prefix: str = "ERROR_HANDLING_") -> 'ConfigManager':
        """Load configuration from environment variables."""
        env_config = {}
        
        # General settings
        env_config.update(self._get_env_section(prefix, {
            'enabled': ('ENABLED', bool, True),
            'debug_mode': ('DEBUG_MODE', bool, False),
            'log_level': ('LOG_LEVEL', str, 'INFO')
        }))
        
        # Circuit breaker settings
        cb_config = self._get_env_section(prefix + "CB_", {
            'failure_threshold': ('FAILURE_THRESHOLD', int, 5),
            'recovery_timeout': ('RECOVERY_TIMEOUT', int, 60),
            'success_threshold': ('SUCCESS_THRESHOLD', int, 3),
            'timeout': ('TIMEOUT', float, 30.0),
            'enabled': ('ENABLED', bool, True)
        })
        if cb_config:
            env_config['circuit_breaker'] = cb_config
        
        # Retry settings
        retry_config = self._get_env_section(prefix + "RETRY_", {
            'max_attempts': ('MAX_ATTEMPTS', int, 3),
            'base_delay': ('BASE_DELAY', float, 1.0),
            'max_delay': ('MAX_DELAY', float, 60.0),
            'backoff_strategy': ('BACKOFF_STRATEGY', str, 'exponential'),
            'backoff_multiplier': ('BACKOFF_MULTIPLIER', float, 2.0),
            'jitter_type': ('JITTER_TYPE', str, 'equal'),
            'timeout': ('TIMEOUT', float, None),
            'enabled': ('ENABLED', bool, True)
        })
        if retry_config:
            env_config['retry'] = retry_config
        
        # Monitoring settings
        monitoring_config = self._get_env_section(prefix + "MONITORING_", {
            'enabled': ('ENABLED', bool, True),
            'metrics_retention_hours': ('METRICS_RETENTION_HOURS', int, 24),
            'alert_cooldown_minutes': ('ALERT_COOLDOWN_MINUTES', int, 15),
            'error_rate_threshold': ('ERROR_RATE_THRESHOLD', float, 10.0),
            'critical_error_threshold': ('CRITICAL_ERROR_THRESHOLD', int, 1),
            'database_error_threshold': ('DATABASE_ERROR_THRESHOLD', float, 0.5),
            'external_service_error_threshold': ('EXTERNAL_SERVICE_ERROR_THRESHOLD', int, 5)
        })
        if monitoring_config:
            env_config['monitoring'] = monitoring_config
        
        # Alert settings
        alert_config = self._get_env_section(prefix + "ALERT_", {
            'enabled': ('ENABLED', bool, True),
            'channels': ('CHANNELS', list, ['log']),
            'email_enabled': ('EMAIL_ENABLED', bool, False),
            'email_recipients': ('EMAIL_RECIPIENTS', list, []),
            'slack_enabled': ('SLACK_ENABLED', bool, False),
            'slack_webhook_url': ('SLACK_WEBHOOK_URL', str, None),
            'webhook_enabled': ('WEBHOOK_ENABLED', bool, False),
            'webhook_url': ('WEBHOOK_URL', str, None)
        })
        if alert_config:
            env_config['alerts'] = alert_config
        
        # User messages settings
        messages_config = self._get_env_section(prefix + "MESSAGES_", {
            'default_locale': ('DEFAULT_LOCALE', str, 'en'),
            'supported_locales': ('SUPPORTED_LOCALES', list, ['en', 'es']),
            'include_technical_details': ('INCLUDE_TECHNICAL_DETAILS', bool, False),
            'custom_message_file': ('CUSTOM_MESSAGE_FILE', str, None)
        })
        if messages_config:
            env_config['user_messages'] = messages_config
        
        # Recovery settings
        recovery_config = self._get_env_section(prefix + "RECOVERY_", {
            'enabled': ('ENABLED', bool, True),
            'max_recovery_attempts': ('MAX_RECOVERY_ATTEMPTS', int, 3),
            'cache_fallback_enabled': ('CACHE_FALLBACK_ENABLED', bool, True),
            'cache_ttl_seconds': ('CACHE_TTL_SECONDS', int, 3600),
            'graceful_degradation_enabled': ('GRACEFUL_DEGRADATION_ENABLED', bool, True),
            'alternative_services_enabled': ('ALTERNATIVE_SERVICES_ENABLED', bool, True)
        })
        if recovery_config:
            env_config['recovery'] = recovery_config
        
        # Middleware settings
        middleware_config = self._get_env_section(prefix + "MIDDLEWARE_", {
            'enabled': ('ENABLED', bool, True),
            'include_stack_trace': ('INCLUDE_STACK_TRACE', bool, False),
            'log_request_data': ('LOG_REQUEST_DATA', bool, True),
            'redact_sensitive_data': ('REDACT_SENSITIVE_DATA', bool, True),
            'response_headers_enabled': ('RESPONSE_HEADERS_ENABLED', bool, True)
        })
        if middleware_config:
            env_config['middleware'] = middleware_config
        
        # Update configuration
        if env_config:
            self._merge_config(env_config)
            self._config_sources.append(ConfigSource.ENVIRONMENT)
            self.logger.info("Loaded error handling configuration from environment")
        
        return self
    
    def load_from_file(self, file_path: str) -> 'ConfigManager':
        """Load configuration from a file (JSON or YAML)."""
        if not os.path.exists(file_path):
            raise ConfigurationError(f"config_file", f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    config_data = json.load(f)
                elif file_path.endswith(('.yml', '.yaml')):
                    config_data = yaml.safe_load(f)
                else:
                    raise ConfigurationError(f"config_file", f"Unsupported file format: {file_path}")
            
            self._merge_config(config_data)
            self._config_sources.append(ConfigSource.FILE)
            self.logger.info(f"Loaded error handling configuration from file: {file_path}")
            
        except Exception as e:
            raise ConfigurationError(f"config_file", f"Failed to load configuration from {file_path}: {e}")
        
        return self
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> 'ConfigManager':
        """Load configuration from a dictionary."""
        try:
            self._merge_config(config_dict)
            self._config_sources.append(ConfigSource.DICT)
            self.logger.info("Loaded error handling configuration from dictionary")
        except Exception as e:
            raise ConfigurationError("config_dict", f"Failed to load configuration from dictionary: {e}")
        
        return self
    
    def _get_env_section(self, prefix: str, schema: Dict[str, tuple]) -> Dict[str, Any]:
        """Get environment variables for a configuration section."""
        section_config = {}
        
        for key, (env_suffix, value_type, default) in schema.items():
            env_var = prefix + env_suffix
            env_value = os.getenv(env_var)
            
            if env_value is not None:
                try:
                    if value_type == bool:
                        section_config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        section_config[key] = int(env_value)
                    elif value_type == float:
                        section_config[key] = float(env_value)
                    elif value_type == list:
                        section_config[key] = [item.strip() for item in env_value.split(',')]
                    else:
                        section_config[key] = env_value
                except ValueError as e:
                    self.logger.warning(f"Invalid value for {env_var}: {env_value}. Using default: {default}")
        
        return section_config
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing configuration."""
        for key, value in new_config.items():
            if hasattr(self._config, key):
                current_value = getattr(self._config, key)
                
                if isinstance(current_value, dict):
                    # Merge dictionaries
                    if isinstance(value, dict):
                        current_value.update(value)
                    else:
                        setattr(self._config, key, value)
                elif hasattr(current_value, '__dict__'):
                    # Merge dataclass objects
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if hasattr(current_value, sub_key):
                                setattr(current_value, sub_key, sub_value)
                    else:
                        setattr(self._config, key, value)
                else:
                    # Replace scalar values
                    setattr(self._config, key, value)
            else:
                # Add new custom setting
                self._config.custom_settings[key] = value
    
    def get_config(self) -> ErrorHandlingConfig:
        """Get the current configuration."""
        return self._config
    
    def get_circuit_breaker_config(self) -> CircuitBreakerConfig:
        """Get circuit breaker configuration."""
        return self._config.circuit_breaker
    
    def get_retry_config(self) -> RetryConfig:
        """Get retry configuration."""
        return self._config.retry
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return self._config.monitoring
    
    def get_alert_config(self) -> AlertConfig:
        """Get alert configuration."""
        return self._config.alerts
    
    def get_user_messages_config(self) -> UserMessagesConfig:
        """Get user messages configuration."""
        return self._config.user_messages
    
    def get_recovery_config(self) -> RecoveryConfig:
        """Get recovery configuration."""
        return self._config.recovery
    
    def get_middleware_config(self) -> MiddlewareConfig:
        """Get middleware configuration."""
        return self._config.middleware
    
    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """Get a custom setting."""
        return self._config.custom_settings.get(key, default)
    
    def set_custom_setting(self, key: str, value: Any):
        """Set a custom setting."""
        self._config.custom_settings[key] = value
    
    def register_config_watcher(self, callback: callable):
        """Register a callback to be called when configuration changes."""
        self._watchers.append(callback)
    
    def notify_watchers(self):
        """Notify all registered watchers about configuration changes."""
        for watcher in self._watchers:
            try:
                watcher(self._config)
            except Exception as e:
                self.logger.error(f"Config watcher failed: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate the current configuration and return any issues."""
        issues = []
        
        # Validate circuit breaker config
        cb_config = self._config.circuit_breaker
        if cb_config.failure_threshold <= 0:
            issues.append("Circuit breaker failure_threshold must be positive")
        if cb_config.recovery_timeout <= 0:
            issues.append("Circuit breaker recovery_timeout must be positive")
        if cb_config.success_threshold <= 0:
            issues.append("Circuit breaker success_threshold must be positive")
        
        # Validate retry config
        retry_config = self._config.retry
        if retry_config.max_attempts <= 0:
            issues.append("Retry max_attempts must be positive")
        if retry_config.base_delay < 0:
            issues.append("Retry base_delay must be non-negative")
        if retry_config.max_delay < retry_config.base_delay:
            issues.append("Retry max_delay must be >= base_delay")
        
        # Validate monitoring config
        monitoring_config = self._config.monitoring
        if monitoring_config.metrics_retention_hours <= 0:
            issues.append("Monitoring metrics_retention_hours must be positive")
        if monitoring_config.error_rate_threshold < 0:
            issues.append("Monitoring error_rate_threshold must be non-negative")
        
        # Validate alert config
        alert_config = self._config.alerts
        if alert_config.email_enabled and not alert_config.email_recipients:
            issues.append("Email alerts enabled but no recipients configured")
        if alert_config.slack_enabled and not alert_config.slack_webhook_url:
            issues.append("Slack alerts enabled but no webhook URL configured")
        if alert_config.webhook_enabled and not alert_config.webhook_url:
            issues.append("Webhook alerts enabled but no webhook URL configured")
        
        return issues
    
    def export_config(self, format: str = 'json') -> str:
        """Export current configuration in specified format."""
        config_dict = self._config_to_dict()
        
        if format.lower() == 'json':
            return json.dumps(config_dict, indent=2, default=str)
        elif format.lower() in ['yaml', 'yml']:
            return yaml.dump(config_dict, indent=2, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dict__'):
                return {k: dataclass_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [dataclass_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            else:
                return obj
        
        return dataclass_to_dict(self._config)


# Global configuration manager instance
config_manager = ConfigManager()

# Load default configuration
config_manager.load_default_config()