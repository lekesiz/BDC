"""
Error Recovery Strategies and Fallback Mechanisms.

Provides automatic error recovery capabilities and fallback strategies for resilient applications.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
import functools
import threading

from .exceptions import RecoveryError, FallbackError
from .error_manager import ErrorContext


class RecoveryStrategy(Enum):
    """Types of recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    CACHE_FALLBACK = "cache_fallback"
    DEFAULT_VALUE = "default_value"
    ALTERNATIVE_SERVICE = "alternative_service"


class RecoveryPriority(Enum):
    """Priority levels for recovery strategies."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RecoveryAction:
    """Represents a recovery action to be executed."""
    name: str
    strategy: RecoveryStrategy
    priority: RecoveryPriority
    handler: Callable
    conditions: List[Callable[[Exception], bool]] = field(default_factory=list)
    max_attempts: int = 3
    enabled: bool = True
    timeout: Optional[float] = None
    
    def matches_exception(self, exception: Exception) -> bool:
        """Check if this recovery action matches the given exception."""
        if not self.conditions:
            return True
        
        return any(condition(exception) for condition in self.conditions)


class BaseRecoveryHandler(ABC):
    """Base class for recovery handlers."""
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def can_handle(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Check if this handler can handle the given exception."""
        pass
    
    @abstractmethod
    def recover(self, exception: Exception, context: Dict[str, Any]) -> Any:
        """Attempt to recover from the exception."""
        pass


class RetryRecoveryHandler(BaseRecoveryHandler):
    """Recovery handler that implements retry logic."""
    
    def __init__(self, name: str = "retry", max_attempts: int = 3, delay: float = 1.0):
        super().__init__(name)
        self.max_attempts = max_attempts
        self.delay = delay
    
    def can_handle(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Check if retry is appropriate for this exception."""
        # Retry for transient errors
        transient_exceptions = (ConnectionError, TimeoutError, OSError)
        return isinstance(exception, transient_exceptions)
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> Any:
        """Attempt recovery through retry."""
        original_function = context.get('original_function')
        args = context.get('args', ())
        kwargs = context.get('kwargs', {})
        
        if not original_function:
            raise RecoveryError(self.name, exception, {'reason': 'No original function provided'})
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                self.logger.info(f"Retry attempt {attempt}/{self.max_attempts} for {self.name}")
                
                if attempt > 1:
                    import time
                    time.sleep(self.delay * attempt)  # Exponential backoff
                
                return original_function(*args, **kwargs)
                
            except Exception as e:
                if attempt == self.max_attempts:
                    raise RecoveryError(self.name, e, {'attempts': attempt})
                self.logger.warning(f"Retry attempt {attempt} failed: {e}")
        
        raise RecoveryError(self.name, exception)


class FallbackRecoveryHandler(BaseRecoveryHandler):
    """Recovery handler that provides fallback values or functions."""
    
    def __init__(self, name: str = "fallback", fallback_value: Any = None, fallback_function: Callable = None):
        super().__init__(name)
        self.fallback_value = fallback_value
        self.fallback_function = fallback_function
    
    def can_handle(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Fallback can handle any exception."""
        return True
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> Any:
        """Attempt recovery through fallback."""
        try:
            if self.fallback_function:
                args = context.get('args', ())
                kwargs = context.get('kwargs', {})
                self.logger.info(f"Using fallback function for {self.name}")
                return self.fallback_function(*args, **kwargs)
            else:
                self.logger.info(f"Using fallback value for {self.name}")
                return self.fallback_value
        except Exception as e:
            raise RecoveryError(self.name, e)


class CacheFallbackHandler(BaseRecoveryHandler):
    """Recovery handler that falls back to cached values."""
    
    def __init__(self, name: str = "cache_fallback", cache_ttl: int = 3600):
        super().__init__(name)
        self.cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self.cache_ttl = cache_ttl
        self._lock = threading.RLock()
    
    def can_handle(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Check if we have cached data available."""
        cache_key = context.get('cache_key')
        return cache_key is not None and self._has_valid_cache(cache_key)
    
    def _has_valid_cache(self, cache_key: str) -> bool:
        """Check if cache entry is valid."""
        with self._lock:
            if cache_key not in self.cache:
                return False
            
            value, timestamp = self.cache[cache_key]
            return datetime.utcnow().timestamp() - timestamp < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Any:
        """Get value from cache."""
        with self._lock:
            if cache_key in self.cache:
                value, timestamp = self.cache[cache_key]
                return value
            return None
    
    def _store_in_cache(self, cache_key: str, value: Any):
        """Store value in cache."""
        with self._lock:
            self.cache[cache_key] = (value, datetime.utcnow().timestamp())
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> Any:
        """Attempt recovery through cached value."""
        cache_key = context.get('cache_key')
        if not cache_key:
            raise RecoveryError(self.name, exception, {'reason': 'No cache key provided'})
        
        cached_value = self._get_from_cache(cache_key)
        if cached_value is not None:
            self.logger.info(f"Using cached value for {self.name}")
            return cached_value
        
        raise RecoveryError(self.name, exception, {'reason': 'No valid cache entry found'})


class GracefulDegradationHandler(BaseRecoveryHandler):
    """Recovery handler that provides graceful degradation."""
    
    def __init__(self, name: str = "graceful_degradation", degraded_function: Callable = None):
        super().__init__(name)
        self.degraded_function = degraded_function
    
    def can_handle(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Check if graceful degradation is available."""
        return self.degraded_function is not None
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> Any:
        """Attempt recovery through degraded functionality."""
        try:
            args = context.get('args', ())
            kwargs = context.get('kwargs', {})
            self.logger.warning(f"Using degraded functionality for {self.name}")
            return self.degraded_function(*args, **kwargs)
        except Exception as e:
            raise RecoveryError(self.name, e)


class AlternativeServiceHandler(BaseRecoveryHandler):
    """Recovery handler that switches to alternative services."""
    
    def __init__(self, name: str = "alternative_service", alternative_services: List[Callable] = None):
        super().__init__(name)
        self.alternative_services = alternative_services or []
        self.current_service_index = 0
    
    def can_handle(self, exception: Exception, context: Dict[str, Any]) -> bool:
        """Check if alternative services are available."""
        return len(self.alternative_services) > 0
    
    def recover(self, exception: Exception, context: Dict[str, Any]) -> Any:
        """Attempt recovery through alternative service."""
        args = context.get('args', ())
        kwargs = context.get('kwargs', {})
        
        for i, service in enumerate(self.alternative_services):
            try:
                self.logger.info(f"Trying alternative service {i+1}/{len(self.alternative_services)}")
                return service(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Alternative service {i+1} failed: {e}")
                if i == len(self.alternative_services) - 1:
                    raise RecoveryError(self.name, e, {'tried_services': len(self.alternative_services)})
        
        raise RecoveryError(self.name, exception)


class ErrorRecovery:
    """Main error recovery system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._recovery_handlers: List[BaseRecoveryHandler] = []
        self._recovery_stats: Dict[str, Dict[str, int]] = {}
        self._lock = threading.RLock()
        
        # Setup default recovery handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default recovery handlers."""
        # Add basic retry handler
        retry_handler = RetryRecoveryHandler("default_retry", max_attempts=3, delay=1.0)
        self.register_handler(retry_handler)
        
        # Add fallback handler with None fallback
        fallback_handler = FallbackRecoveryHandler("default_fallback", fallback_value=None)
        self.register_handler(fallback_handler)
    
    def register_handler(self, handler: BaseRecoveryHandler):
        """Register a recovery handler."""
        with self._lock:
            self._recovery_handlers.append(handler)
            self._recovery_stats[handler.name] = {
                'attempts': 0,
                'successes': 0,
                'failures': 0
            }
            self.logger.info(f"Registered recovery handler: {handler.name}")
    
    def unregister_handler(self, handler_name: str):
        """Unregister a recovery handler."""
        with self._lock:
            self._recovery_handlers = [h for h in self._recovery_handlers if h.name != handler_name]
            if handler_name in self._recovery_stats:
                del self._recovery_stats[handler_name]
            self.logger.info(f"Unregistered recovery handler: {handler_name}")
    
    def attempt_recovery(
        self,
        exception: Exception,
        original_function: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Attempt to recover from an exception using registered handlers."""
        context = {
            'original_function': original_function,
            'args': args,
            'kwargs': kwargs,
            'exception': exception,
            'timestamp': datetime.utcnow()
        }
        
        # Try each recovery handler in order
        for handler in self._recovery_handlers:
            if not handler.can_handle(exception, context):
                continue
            
            handler_name = handler.name
            self._increment_stat(handler_name, 'attempts')
            
            try:
                self.logger.info(f"Attempting recovery with handler: {handler_name}")
                result = handler.recover(exception, context)
                self._increment_stat(handler_name, 'successes')
                self.logger.info(f"Recovery successful with handler: {handler_name}")
                return result
                
            except RecoveryError as e:
                self._increment_stat(handler_name, 'failures')
                self.logger.warning(f"Recovery failed with handler {handler_name}: {e}")
                continue
            except Exception as e:
                self._increment_stat(handler_name, 'failures')
                self.logger.error(f"Recovery handler {handler_name} raised unexpected exception: {e}")
                continue
        
        # No recovery handler succeeded
        self.logger.error(f"All recovery attempts failed for exception: {exception}")
        raise RecoveryError("all_handlers", exception, {'handlers_tried': len(self._recovery_handlers)})
    
    def _increment_stat(self, handler_name: str, stat_type: str):
        """Increment a statistic for a handler."""
        with self._lock:
            if handler_name in self._recovery_stats:
                self._recovery_stats[handler_name][stat_type] += 1
    
    def get_recovery_stats(self) -> Dict[str, Dict[str, int]]:
        """Get recovery statistics."""
        with self._lock:
            return self._recovery_stats.copy()
    
    def reset_stats(self):
        """Reset recovery statistics."""
        with self._lock:
            for handler_name in self._recovery_stats:
                self._recovery_stats[handler_name] = {
                    'attempts': 0,
                    'successes': 0,
                    'failures': 0
                }
    
    def get_handler_names(self) -> List[str]:
        """Get names of all registered handlers."""
        with self._lock:
            return [handler.name for handler in self._recovery_handlers]


def with_recovery(
    recovery_handlers: Optional[List[BaseRecoveryHandler]] = None,
    cache_key: Optional[str] = None,
    fallback_value: Any = None,
    fallback_function: Optional[Callable] = None
):
    """Decorator to add error recovery to a function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Cache successful result if cache_key provided
                if cache_key and hasattr(error_recovery, '_cache_handler'):
                    context = {'cache_key': cache_key}
                    for handler in error_recovery._recovery_handlers:
                        if isinstance(handler, CacheFallbackHandler):
                            handler._store_in_cache(cache_key, result)
                            break
                
                return result
                
            except Exception as e:
                # Add cache key to context if provided
                context_kwargs = kwargs.copy()
                if cache_key:
                    context_kwargs['cache_key'] = cache_key
                
                # Try to recover
                return error_recovery.attempt_recovery(e, func, *args, **context_kwargs)
        
        return wrapper
    
    return decorator


def with_fallback(fallback_value: Any = None, fallback_function: Optional[Callable] = None):
    """Decorator to add fallback behavior to a function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if fallback_function:
                    try:
                        return fallback_function(*args, **kwargs)
                    except Exception as fallback_error:
                        raise FallbackError(func.__name__, fallback_error)
                else:
                    return fallback_value
        
        return wrapper
    
    return decorator


# Global error recovery instance
error_recovery = ErrorRecovery()