"""
Configuration management for integrations.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import asdict
import logging

from .base import IntegrationConfig, IntegrationError

logger = logging.getLogger(__name__)


class IntegrationManager:
    """Manages integration configurations and lifecycle."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv('INTEGRATIONS_CONFIG_FILE', 'integrations.json')
        self._configs: Dict[str, IntegrationConfig] = {}
        self._active_integrations: Dict[str, Any] = {}
        self.load_configs()
    
    def load_configs(self) -> None:
        """Load integration configurations from file or environment."""
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for name, config_data in data.items():
                        self._configs[name] = IntegrationConfig(**config_data)
                logger.info(f"Loaded {len(self._configs)} integration configs from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file {self.config_file}: {e}")
        
        # Load from environment variables
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load integration configs from environment variables."""
        # Calendar integrations
        if os.getenv('GOOGLE_CALENDAR_CLIENT_ID'):
            self.add_config('google_calendar', IntegrationConfig(
                name='google_calendar',
                enabled=True,
                credentials={
                    'client_id': os.getenv('GOOGLE_CALENDAR_CLIENT_ID'),
                    'client_secret': os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET'),
                    'redirect_uri': os.getenv('GOOGLE_CALENDAR_REDIRECT_URI')
                }
            ))
        
        if os.getenv('OUTLOOK_CLIENT_ID'):
            self.add_config('outlook_calendar', IntegrationConfig(
                name='outlook_calendar',
                enabled=True,
                credentials={
                    'client_id': os.getenv('OUTLOOK_CLIENT_ID'),
                    'client_secret': os.getenv('OUTLOOK_CLIENT_SECRET'),
                    'redirect_uri': os.getenv('OUTLOOK_REDIRECT_URI')
                }
            ))
        
        # Payment processors
        if os.getenv('STRIPE_SECRET_KEY'):
            self.add_config('stripe', IntegrationConfig(
                name='stripe',
                enabled=True,
                credentials={
                    'secret_key': os.getenv('STRIPE_SECRET_KEY'),
                    'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
                    'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET')
                }
            ))
        
        if os.getenv('PAYPAL_CLIENT_ID'):
            self.add_config('paypal', IntegrationConfig(
                name='paypal',
                enabled=True,
                credentials={
                    'client_id': os.getenv('PAYPAL_CLIENT_ID'),
                    'client_secret': os.getenv('PAYPAL_CLIENT_SECRET'),
                    'environment': os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')
                }
            ))
        
        # Video conferencing
        if os.getenv('ZOOM_CLIENT_ID'):
            self.add_config('zoom', IntegrationConfig(
                name='zoom',
                enabled=True,
                credentials={
                    'client_id': os.getenv('ZOOM_CLIENT_ID'),
                    'client_secret': os.getenv('ZOOM_CLIENT_SECRET'),
                    'redirect_uri': os.getenv('ZOOM_REDIRECT_URI')
                }
            ))
        
        if os.getenv('TEAMS_CLIENT_ID'):
            self.add_config('microsoft_teams', IntegrationConfig(
                name='microsoft_teams',
                enabled=True,
                credentials={
                    'client_id': os.getenv('TEAMS_CLIENT_ID'),
                    'client_secret': os.getenv('TEAMS_CLIENT_SECRET'),
                    'redirect_uri': os.getenv('TEAMS_REDIRECT_URI')
                }
            ))
        
        # Email services
        if os.getenv('SENDGRID_API_KEY'):
            self.add_config('sendgrid', IntegrationConfig(
                name='sendgrid',
                enabled=True,
                credentials={
                    'api_key': os.getenv('SENDGRID_API_KEY')
                }
            ))
        
        if os.getenv('MAILGUN_API_KEY'):
            self.add_config('mailgun', IntegrationConfig(
                name='mailgun',
                enabled=True,
                credentials={
                    'api_key': os.getenv('MAILGUN_API_KEY'),
                    'domain': os.getenv('MAILGUN_DOMAIN')
                }
            ))
        
        # Storage providers
        if os.getenv('AWS_ACCESS_KEY_ID'):
            self.add_config('aws_s3', IntegrationConfig(
                name='aws_s3',
                enabled=True,
                credentials={
                    'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                    'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                    'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                    'bucket_name': os.getenv('AWS_S3_BUCKET')
                }
            ))
        
        if os.getenv('AZURE_STORAGE_ACCOUNT_NAME'):
            self.add_config('azure_storage', IntegrationConfig(
                name='azure_storage',
                enabled=True,
                credentials={
                    'account_name': os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
                    'account_key': os.getenv('AZURE_STORAGE_ACCOUNT_KEY'),
                    'container_name': os.getenv('AZURE_STORAGE_CONTAINER')
                }
            ))
        
        if os.getenv('GOOGLE_CLOUD_PROJECT_ID'):
            self.add_config('google_cloud_storage', IntegrationConfig(
                name='google_cloud_storage',
                enabled=True,
                credentials={
                    'project_id': os.getenv('GOOGLE_CLOUD_PROJECT_ID'),
                    'bucket_name': os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET'),
                    'credentials_file': os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                }
            ))
        
        # Authentication providers
        if os.getenv('GOOGLE_OAUTH_CLIENT_ID'):
            self.add_config('google_auth', IntegrationConfig(
                name='google_auth',
                enabled=True,
                credentials={
                    'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
                    'client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
                }
            ))
        
        if os.getenv('MICROSOFT_AUTH_CLIENT_ID'):
            self.add_config('microsoft_auth', IntegrationConfig(
                name='microsoft_auth',
                enabled=True,
                credentials={
                    'client_id': os.getenv('MICROSOFT_AUTH_CLIENT_ID'),
                    'client_secret': os.getenv('MICROSOFT_AUTH_CLIENT_SECRET')
                }
            ))
        
        if os.getenv('GITHUB_CLIENT_ID'):
            self.add_config('github_auth', IntegrationConfig(
                name='github_auth',
                enabled=True,
                credentials={
                    'client_id': os.getenv('GITHUB_CLIENT_ID'),
                    'client_secret': os.getenv('GITHUB_CLIENT_SECRET')
                }
            ))
    
    def add_config(self, name: str, config: IntegrationConfig) -> None:
        """Add or update an integration configuration."""
        self._configs[name] = config
        logger.info(f"Added config for integration: {name}")
    
    def get_config(self, name: str) -> Optional[IntegrationConfig]:
        """Get configuration for a specific integration."""
        return self._configs.get(name)
    
    def list_configs(self) -> List[str]:
        """List all available integration configurations."""
        return list(self._configs.keys())
    
    def list_enabled_configs(self) -> List[str]:
        """List enabled integration configurations."""
        return [name for name, config in self._configs.items() if config.enabled]
    
    def enable_integration(self, name: str) -> bool:
        """Enable an integration."""
        if name in self._configs:
            self._configs[name].enabled = True
            return True
        return False
    
    def disable_integration(self, name: str) -> bool:
        """Disable an integration."""
        if name in self._configs:
            self._configs[name].enabled = False
            return True
        return False
    
    def save_configs(self) -> None:
        """Save configurations to file."""
        try:
            data = {}
            for name, config in self._configs.items():
                # Don't save sensitive credentials to file
                config_dict = asdict(config)
                config_dict['credentials'] = {}  # Remove credentials for security
                data[name] = config_dict
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self._configs)} configs to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configs: {e}")
            raise IntegrationError(f"Failed to save configs: {e}")
    
    def register_integration(self, name: str, integration_instance: Any) -> None:
        """Register an active integration instance."""
        self._active_integrations[name] = integration_instance
        logger.info(f"Registered integration instance: {name}")
    
    def get_integration(self, name: str) -> Optional[Any]:
        """Get an active integration instance."""
        return self._active_integrations.get(name)
    
    def list_active_integrations(self) -> List[str]:
        """List active integration instances."""
        return list(self._active_integrations.keys())
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        status = {}
        for name, integration in self._active_integrations.items():
            if hasattr(integration, 'get_status'):
                status[name] = integration.get_status()
            else:
                status[name] = {'name': name, 'status': 'unknown'}
        return status