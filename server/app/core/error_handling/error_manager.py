"""
Centralized Error Manager for the BDC project.

Provides comprehensive error classification, logging, and management.
"""

import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, asdict
import uuid

from .exceptions import ErrorHandlingException


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error category classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Error context information."""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    stack_trace: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['severity'] = self.severity.value
        data['category'] = self.category.value
        return data


class ErrorManager:
    """Centralized error management system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._error_handlers: Dict[Type[Exception], callable] = {}
        self._error_classifiers: List[callable] = []
        self._error_callbacks: List[callable] = []
        self._error_history: List[ErrorContext] = []
        self._max_history_size = 1000
        
        # Setup default error classifications
        self._setup_default_classifiers()
    
    def _setup_default_classifiers(self):
        """Setup default error classification rules."""
        from ..exceptions import (
            ValidationException, NotFoundException, UnauthorizedException,
            ForbiddenException, ConflictException, ExternalServiceException
        )
        
        # Map exception types to categories and severities
        self._default_classifications = {
            ValidationException: (ErrorCategory.VALIDATION, ErrorSeverity.LOW),
            NotFoundException: (ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.LOW),
            UnauthorizedException: (ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM),
            ForbiddenException: (ErrorCategory.AUTHORIZATION, ErrorSeverity.MEDIUM),
            ConflictException: (ErrorCategory.BUSINESS_LOGIC, ErrorSeverity.MEDIUM),
            ExternalServiceException: (ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH),
            ConnectionError: (ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            TimeoutError: (ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            MemoryError: (ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL),
            OSError: (ErrorCategory.SYSTEM, ErrorSeverity.HIGH),
        }
    
    def register_error_handler(self, exception_type: Type[Exception], handler: callable):
        """Register a custom error handler for a specific exception type."""
        self._error_handlers[exception_type] = handler
    
    def register_error_classifier(self, classifier: callable):
        """Register a custom error classifier function."""
        self._error_classifiers.append(classifier)
    
    def register_error_callback(self, callback: callable):
        """Register a callback to be called when errors are processed."""
        self._error_callbacks.append(callback)
    
    def classify_error(self, exception: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify an error by category and severity."""
        # Try custom classifiers first
        for classifier in self._error_classifiers:
            try:
                result = classifier(exception)
                if result:
                    return result
            except Exception as e:
                self.logger.warning(f"Error classifier failed: {e}")
        
        # Use default classifications
        exception_type = type(exception)
        if exception_type in self._default_classifications:
            return self._default_classifications[exception_type]
        
        # Check parent classes
        for exc_type, (category, severity) in self._default_classifications.items():
            if isinstance(exception, exc_type):
                return category, severity
        
        # Default classification based on exception name patterns
        exception_name = exception_type.__name__.lower()
        
        if 'validation' in exception_name or 'invalid' in exception_name:
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        elif 'auth' in exception_name or 'permission' in exception_name:
            return ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM
        elif 'connection' in exception_name or 'network' in exception_name:
            return ErrorCategory.NETWORK, ErrorSeverity.HIGH
        elif 'database' in exception_name or 'sql' in exception_name:
            return ErrorCategory.DATABASE, ErrorSeverity.HIGH
        elif 'service' in exception_name or 'api' in exception_name:
            return ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def handle_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ErrorContext:
        """Handle an error with comprehensive logging and classification."""
        
        # Generate unique error ID
        error_id = str(uuid.uuid4())
        
        # Classify the error
        category, severity = self.classify_error(exception)
        
        # Create error context
        error_context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            message=str(exception),
            exception_type=type(exception).__name__,
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            tenant_id=tenant_id,
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data=context
        )
        
        # Add to error history
        self._add_to_history(error_context)
        
        # Log the error
        self._log_error(error_context)
        
        # Try custom error handler
        exception_type = type(exception)
        if exception_type in self._error_handlers:
            try:
                self._error_handlers[exception_type](exception, error_context)
            except Exception as e:
                self.logger.error(f"Custom error handler failed: {e}")
        
        # Execute callbacks
        for callback in self._error_callbacks:
            try:
                callback(error_context)
            except Exception as e:
                self.logger.warning(f"Error callback failed: {e}")
        
        return error_context
    
    def _add_to_history(self, error_context: ErrorContext):
        """Add error context to history with size management."""
        self._error_history.append(error_context)
        
        # Maintain history size
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level based on severity."""
        log_data = {
            'error_id': error_context.error_id,
            'category': error_context.category.value,
            'severity': error_context.severity.value,
            'exception_type': error_context.exception_type,
            'message': error_context.message,
            'user_id': error_context.user_id,
            'tenant_id': error_context.tenant_id,
            'request_id': error_context.request_id,
            'endpoint': error_context.endpoint,
            'method': error_context.method,
            'ip_address': error_context.ip_address
        }
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error_context.message}", extra=log_data)
        elif error_context.severity == ErrorSeverity.HIGH:
            self.logger.error(f"HIGH SEVERITY ERROR: {error_context.message}", extra=log_data)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"MEDIUM SEVERITY ERROR: {error_context.message}", extra=log_data)
        else:
            self.logger.info(f"LOW SEVERITY ERROR: {error_context.message}", extra=log_data)
        
        # Always log stack trace for high and critical errors
        if error_context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"Stack trace for error {error_context.error_id}:\n{error_context.stack_trace}")
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for the specified time period."""
        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
        recent_errors = [
            error for error in self._error_history
            if error.timestamp.timestamp() > cutoff_time
        ]
        
        # Count by category
        category_counts = {}
        for error in recent_errors:
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for error in recent_errors:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Most common errors
        error_type_counts = {}
        for error in recent_errors:
            error_type = error.exception_type
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        return {
            'total_errors': len(recent_errors),
            'time_period_hours': hours,
            'category_breakdown': category_counts,
            'severity_breakdown': severity_counts,
            'top_error_types': dict(sorted(error_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'critical_errors': len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
            'high_severity_errors': len([e for e in recent_errors if e.severity == ErrorSeverity.HIGH])
        }
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors in serializable format."""
        recent_errors = self._error_history[-limit:] if self._error_history else []
        return [error.to_dict() for error in reversed(recent_errors)]
    
    def clear_error_history(self):
        """Clear the error history."""
        self._error_history.clear()
        self.logger.info("Error history cleared")


# Global error manager instance
error_manager = ErrorManager()