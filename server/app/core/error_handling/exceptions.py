"""
Custom exceptions for the error handling system.
"""

from typing import Any, Dict, Optional


class ErrorHandlingException(Exception):
    """Base exception for error handling system."""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        super().__init__(self.message)


class CircuitBreakerError(ErrorHandlingException):
    """Raised when circuit breaker is open."""
    
    def __init__(self, service_name: str, failure_count: int = None, context: Dict[str, Any] = None):
        self.service_name = service_name
        self.failure_count = failure_count
        message = f"Circuit breaker is open for service: {service_name}"
        if failure_count:
            message += f" (failures: {failure_count})"
        super().__init__(message, "CIRCUIT_BREAKER_OPEN", context)


class RetryExhaustedError(ErrorHandlingException):
    """Raised when all retry attempts are exhausted."""
    
    def __init__(self, operation: str, attempts: int, last_error: Exception = None, context: Dict[str, Any] = None):
        self.operation = operation
        self.attempts = attempts
        self.last_error = last_error
        message = f"Retry exhausted for operation '{operation}' after {attempts} attempts"
        if last_error:
            message += f". Last error: {str(last_error)}"
        super().__init__(message, "RETRY_EXHAUSTED", context)


class RecoveryError(ErrorHandlingException):
    """Raised when error recovery fails."""
    
    def __init__(self, recovery_strategy: str, original_error: Exception = None, context: Dict[str, Any] = None):
        self.recovery_strategy = recovery_strategy
        self.original_error = original_error
        message = f"Recovery strategy '{recovery_strategy}' failed"
        if original_error:
            message += f". Original error: {str(original_error)}"
        super().__init__(message, "RECOVERY_FAILED", context)


class MonitoringError(ErrorHandlingException):
    """Raised when error monitoring fails."""
    
    def __init__(self, monitor_type: str, details: str = None, context: Dict[str, Any] = None):
        self.monitor_type = monitor_type
        self.details = details
        message = f"Monitoring error in {monitor_type}"
        if details:
            message += f": {details}"
        super().__init__(message, "MONITORING_ERROR", context)


class ConfigurationError(ErrorHandlingException):
    """Raised when error handling configuration is invalid."""
    
    def __init__(self, config_key: str, reason: str = None, context: Dict[str, Any] = None):
        self.config_key = config_key
        self.reason = reason
        message = f"Invalid configuration for '{config_key}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, "CONFIG_ERROR", context)


class FallbackError(ErrorHandlingException):
    """Raised when fallback mechanism fails."""
    
    def __init__(self, fallback_name: str, original_error: Exception = None, context: Dict[str, Any] = None):
        self.fallback_name = fallback_name
        self.original_error = original_error
        message = f"Fallback '{fallback_name}' failed"
        if original_error:
            message += f". Original error: {str(original_error)}"
        super().__init__(message, "FALLBACK_FAILED", context)


class AlertingError(ErrorHandlingException):
    """Raised when alerting system fails."""
    
    def __init__(self, alert_type: str, destination: str = None, context: Dict[str, Any] = None):
        self.alert_type = alert_type
        self.destination = destination
        message = f"Failed to send {alert_type} alert"
        if destination:
            message += f" to {destination}"
        super().__init__(message, "ALERTING_FAILED", context)