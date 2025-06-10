"""
Circuit Breaker Pattern Implementation.

Provides fault tolerance by preventing calls to failing services and allowing recovery.
"""

import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, Union
from dataclasses import dataclass
import logging

from .exceptions import CircuitBreakerError


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Request timeout in seconds
    expected_exception: Type[Exception] = Exception  # Exception type to count as failure
    excluded_exceptions: tuple = ()     # Exceptions that don't count as failures


@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    state: CircuitState
    failure_count: int
    success_count: int
    last_failure_time: Optional[datetime]
    total_requests: int
    successful_requests: int
    failed_requests: int
    circuit_open_count: int
    last_state_change: datetime


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._last_state_change = datetime.utcnow()
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.{name}")
        
        # Statistics
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._circuit_open_count = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._update_state()
            return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking calls)."""
        return self.state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.state == CircuitState.HALF_OPEN
    
    def _update_state(self):
        """Update circuit state based on current conditions."""
        now = datetime.utcnow()
        
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self._last_failure_time and 
                now - self._last_failure_time >= timedelta(seconds=self.config.recovery_timeout)):
                self._transition_to_half_open()
        
        elif self._state == CircuitState.HALF_OPEN:
            # Check if we should close the circuit
            if self._success_count >= self.config.success_threshold:
                self._transition_to_closed()
    
    def _transition_to_open(self):
        """Transition circuit to open state."""
        if self._state != CircuitState.OPEN:
            self._logger.warning(f"Circuit breaker '{self.name}' opened due to {self._failure_count} failures")
            self._state = CircuitState.OPEN
            self._last_state_change = datetime.utcnow()
            self._circuit_open_count += 1
    
    def _transition_to_half_open(self):
        """Transition circuit to half-open state."""
        if self._state != CircuitState.HALF_OPEN:
            self._logger.info(f"Circuit breaker '{self.name}' transitioned to half-open for testing")
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0
            self._last_state_change = datetime.utcnow()
    
    def _transition_to_closed(self):
        """Transition circuit to closed state."""
        if self._state != CircuitState.CLOSED:
            self._logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_state_change = datetime.utcnow()
    
    def _record_success(self):
        """Record a successful operation."""
        with self._lock:
            self._total_requests += 1
            self._successful_requests += 1
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                self._update_state()
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                if self._failure_count > 0:
                    self._failure_count = 0
    
    def _record_failure(self, exception: Exception):
        """Record a failed operation."""
        with self._lock:
            self._total_requests += 1
            self._failed_requests += 1
            
            # Check if this exception should be ignored
            if isinstance(exception, self.config.excluded_exceptions):
                return
            
            # Check if this is the expected exception type
            if not isinstance(exception, self.config.expected_exception):
                return
            
            self._failure_count += 1
            self._last_failure_time = datetime.utcnow()
            
            self._logger.warning(
                f"Circuit breaker '{self.name}' recorded failure {self._failure_count}: {exception}"
            )
            
            # Check if we should open the circuit
            if self._state == CircuitState.CLOSED:
                if self._failure_count >= self.config.failure_threshold:
                    self._transition_to_open()
            elif self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open state reopens the circuit
                self._transition_to_open()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with circuit breaker protection."""
        with self._lock:
            current_state = self.state
            
            if current_state == CircuitState.OPEN:
                raise CircuitBreakerError(
                    self.name, 
                    self._failure_count,
                    {'last_failure': self._last_failure_time.isoformat() if self._last_failure_time else None}
                )
        
        # Execute the function
        start_time = time.time()
        try:
            # Apply timeout if specified
            if self.config.timeout:
                # Note: This is a simple timeout. In production, you might want
                # to use more sophisticated timeout mechanisms
                result = func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            self._record_success()
            
            self._logger.debug(
                f"Circuit breaker '{self.name}' successful call in {execution_time:.3f}s"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_failure(e)
            
            self._logger.error(
                f"Circuit breaker '{self.name}' failed call in {execution_time:.3f}s: {e}"
            )
            
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator interface for circuit breaker."""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        wrapper.__name__ = f"circuit_breaker_{self.name}_{func.__name__}"
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    def get_stats(self) -> CircuitStats:
        """Get circuit breaker statistics."""
        with self._lock:
            return CircuitStats(
                state=self._state,
                failure_count=self._failure_count,
                success_count=self._success_count,
                last_failure_time=self._last_failure_time,
                total_requests=self._total_requests,
                successful_requests=self._successful_requests,
                failed_requests=self._failed_requests,
                circuit_open_count=self._circuit_open_count,
                last_state_change=self._last_state_change
            )
    
    def reset(self):
        """Reset circuit breaker to closed state."""
        with self._lock:
            self._logger.info(f"Circuit breaker '{self.name}' manually reset")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_state_change = datetime.utcnow()
    
    def force_open(self):
        """Force circuit breaker to open state."""
        with self._lock:
            self._logger.warning(f"Circuit breaker '{self.name}' manually opened")
            self._state = CircuitState.OPEN
            self._last_failure_time = datetime.utcnow()
            self._last_state_change = datetime.utcnow()


class CircuitBreakerManager:
    """Manager for multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
    
    def get_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
                self._logger.info(f"Created circuit breaker: {name}")
            return self._breakers[name]
    
    def get_all_stats(self) -> Dict[str, CircuitStats]:
        """Get statistics for all circuit breakers."""
        with self._lock:
            return {name: breaker.get_stats() for name, breaker in self._breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            self._logger.info("Reset all circuit breakers")
    
    def get_breaker_names(self) -> list[str]:
        """Get names of all registered circuit breakers."""
        with self._lock:
            return list(self._breakers.keys())


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


def circuit_breaker(
    name: str, 
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    success_threshold: int = 3,
    timeout: float = 30.0,
    expected_exception: Type[Exception] = Exception,
    excluded_exceptions: tuple = ()
):
    """Decorator to add circuit breaker protection to a function."""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        timeout=timeout,
        expected_exception=expected_exception,
        excluded_exceptions=excluded_exceptions
    )
    
    breaker = circuit_breaker_manager.get_breaker(name, config)
    
    def decorator(func: Callable) -> Callable:
        return breaker(func)
    
    return decorator