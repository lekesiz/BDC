"""
Base integration classes and utilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntegrationStatus(Enum):
    """Integration connection status."""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"


class IntegrationError(Exception):
    """Base exception for integration-related errors."""
    
    def __init__(self, message: str, integration_type: str = None, error_code: str = None):
        super().__init__(message)
        self.integration_type = integration_type
        self.error_code = error_code
        

class AuthenticationError(IntegrationError):
    """Raised when authentication with a service fails."""
    pass


class RateLimitError(IntegrationError):
    """Raised when rate limits are exceeded."""
    pass


class ServiceUnavailableError(IntegrationError):
    """Raised when the external service is unavailable."""
    pass


@dataclass
class IntegrationConfig:
    """Configuration for an integration."""
    name: str
    enabled: bool = True
    credentials: Dict[str, Any] = None
    settings: Dict[str, Any] = None
    webhook_url: Optional[str] = None
    rate_limit: Optional[int] = None
    timeout: int = 30
    
    def __post_init__(self):
        if self.credentials is None:
            self.credentials = {}
        if self.settings is None:
            self.settings = {}


class BaseIntegration(ABC):
    """Base class for all third-party integrations."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.status = IntegrationStatus.DISCONNECTED
        self._client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @property
    @abstractmethod
    def integration_type(self) -> str:
        """Return the type of integration (e.g., 'calendar', 'payment')."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the service provider (e.g., 'google', 'stripe')."""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the service."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the connection is working."""
        pass
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the service."""
        self.status = IntegrationStatus.AUTHENTICATING
        try:
            self.config.credentials.update(credentials)
            success = await self._authenticate()
            if success:
                self.status = IntegrationStatus.CONNECTED
            else:
                self.status = IntegrationStatus.ERROR
            return success
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {e}", self.integration_type)
    
    @abstractmethod
    async def _authenticate(self) -> bool:
        """Implementation-specific authentication logic."""
        pass
    
    def is_connected(self) -> bool:
        """Check if the integration is connected."""
        return self.status == IntegrationStatus.CONNECTED
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status information."""
        return {
            'name': self.config.name,
            'type': self.integration_type,
            'provider': self.provider_name,
            'status': self.status.value,
            'enabled': self.config.enabled,
            'last_error': getattr(self, '_last_error', None)
        }
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhook from the service."""
        self.logger.info(f"Received webhook for {self.provider_name}: {payload}")
        return await self._handle_webhook(payload)
    
    async def _handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation-specific webhook handling."""
        return {'status': 'received'}


class OAuth2Integration(BaseIntegration):
    """Base class for OAuth2-based integrations."""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    @abstractmethod
    async def get_authorization_url(self, state: str = None) -> str:
        """Get the OAuth2 authorization URL."""
        pass
    
    @abstractmethod
    async def exchange_code_for_tokens(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access tokens."""
        pass
    
    @abstractmethod
    async def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        pass
    
    async def _authenticate(self) -> bool:
        """OAuth2 authentication flow."""
        # This would be called after tokens are obtained
        if 'access_token' in self.config.credentials:
            self.access_token = self.config.credentials['access_token']
            self.refresh_token = self.config.credentials.get('refresh_token')
            return True
        return False


class APIKeyIntegration(BaseIntegration):
    """Base class for API key-based integrations."""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.api_key = config.credentials.get('api_key')
    
    async def _authenticate(self) -> bool:
        """API key authentication."""
        return self.api_key is not None and len(self.api_key) > 0