"""
Custom Exceptions for Synchronization System

Defines specific exceptions for different synchronization scenarios:
- Connection and network related errors
- Conflict resolution failures
- Version management issues
- Event sourcing problems
- Device synchronization errors
"""

class SyncException(Exception):
    """Base exception for all synchronization errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "SYNC_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ConnectionException(SyncException):
    """Exceptions related to WebSocket connections"""
    
    def __init__(self, message: str, connection_id: str = None, **kwargs):
        self.connection_id = connection_id
        super().__init__(message, error_code="CONNECTION_ERROR", **kwargs)


class AuthenticationException(SyncException):
    """Authentication and authorization failures"""
    
    def __init__(self, message: str, user_id: str = None, **kwargs):
        self.user_id = user_id
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)


class ConflictResolutionException(SyncException):
    """Conflict resolution failures"""
    
    def __init__(self, message: str, conflict_id: str = None, strategy: str = None, **kwargs):
        self.conflict_id = conflict_id
        self.strategy = strategy
        super().__init__(message, error_code="CONFLICT_ERROR", **kwargs)


class VersionException(SyncException):
    """Version management errors"""
    
    def __init__(self, message: str, version_id: str = None, entity_type: str = None, 
                 entity_id: str = None, **kwargs):
        self.version_id = version_id
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(message, error_code="VERSION_ERROR", **kwargs)


class EventException(SyncException):
    """Event sourcing related errors"""
    
    def __init__(self, message: str, event_id: str = None, aggregate_type: str = None,
                 aggregate_id: str = None, **kwargs):
        self.event_id = event_id
        self.aggregate_type = aggregate_type
        self.aggregate_id = aggregate_id
        super().__init__(message, error_code="EVENT_ERROR", **kwargs)


class DeviceSyncException(SyncException):
    """Device synchronization errors"""
    
    def __init__(self, message: str, device_id: str = None, user_id: str = None, **kwargs):
        self.device_id = device_id
        self.user_id = user_id
        super().__init__(message, error_code="DEVICE_SYNC_ERROR", **kwargs)


class OfflineException(SyncException):
    """Offline operation errors"""
    
    def __init__(self, message: str, operation_id: str = None, **kwargs):
        self.operation_id = operation_id
        super().__init__(message, error_code="OFFLINE_ERROR", **kwargs)


class ConfigurationException(SyncException):
    """Configuration related errors"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        self.config_key = config_key
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)


class StorageException(SyncException):
    """Storage backend errors"""
    
    def __init__(self, message: str, backend_type: str = None, **kwargs):
        self.backend_type = backend_type
        super().__init__(message, error_code="STORAGE_ERROR", **kwargs)


class ValidationException(SyncException):
    """Data validation errors"""
    
    def __init__(self, message: str, field_name: str = None, field_value: str = None, **kwargs):
        self.field_name = field_name
        self.field_value = field_value
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)


class RateLimitException(SyncException):
    """Rate limiting errors"""
    
    def __init__(self, message: str, limit: int = None, window: int = None, **kwargs):
        self.limit = limit
        self.window = window
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)


class TimeoutException(SyncException):
    """Timeout related errors"""
    
    def __init__(self, message: str, timeout_duration: float = None, **kwargs):
        self.timeout_duration = timeout_duration
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)