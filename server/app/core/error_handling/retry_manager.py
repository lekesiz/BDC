"""
Retry Manager with Exponential Backoff and Jitter.

Provides configurable retry mechanisms for handling transient failures.
"""

import time
import random
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass
import functools
import asyncio

from .exceptions import RetryExhaustedError


class BackoffStrategy(Enum):
    """Backoff strategy types."""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"


class JitterType(Enum):
    """Jitter types for randomizing retry delays."""
    NONE = "none"
    FULL = "full"          # Random delay between 0 and computed delay
    EQUAL = "equal"        # Half computed delay + random half
    DECORRELATED = "decorrelated"  # Uses previous delay for calculation


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0              # Base delay in seconds
    max_delay: float = 60.0              # Maximum delay in seconds
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0      # Multiplier for exponential backoff
    jitter_type: JitterType = JitterType.EQUAL
    retryable_exceptions: tuple = (Exception,)  # Exceptions that trigger retry
    non_retryable_exceptions: tuple = ()  # Exceptions that don't trigger retry
    timeout: Optional[float] = None       # Overall timeout for all attempts
    on_retry: Optional[Callable] = None   # Callback called on each retry


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    attempt_number: int
    delay: float
    exception: Optional[Exception]
    timestamp: datetime
    execution_time: Optional[float] = None


@dataclass
class RetryStats:
    """Statistics for retry operations."""
    operation_name: str
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    average_attempts_per_operation: float
    total_retry_time: float
    last_attempt: Optional[datetime]


class RetryManager:
    """Manager for retry operations with various strategies."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._operation_stats: Dict[str, List[RetryAttempt]] = {}
        self._fibonacci_cache = {0: 0, 1: 1}
    
    def _calculate_delay(self, config: RetryConfig, attempt: int, previous_delay: float = 0) -> float:
        """Calculate delay for the given attempt number."""
        if config.backoff_strategy == BackoffStrategy.FIXED:
            delay = config.base_delay
        
        elif config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = config.base_delay * attempt
        
        elif config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        
        elif config.backoff_strategy == BackoffStrategy.FIBONACCI:
            fib_value = self._fibonacci(attempt)
            delay = config.base_delay * fib_value
        
        else:
            delay = config.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, config.max_delay)
        
        # Apply jitter
        delay = self._apply_jitter(delay, config.jitter_type, previous_delay)
        
        return max(0, delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number with memoization."""
        if n not in self._fibonacci_cache:
            self._fibonacci_cache[n] = self._fibonacci(n-1) + self._fibonacci(n-2)
        return self._fibonacci_cache[n]
    
    def _apply_jitter(self, delay: float, jitter_type: JitterType, previous_delay: float) -> float:
        """Apply jitter to the calculated delay."""
        if jitter_type == JitterType.NONE:
            return delay
        
        elif jitter_type == JitterType.FULL:
            return random.uniform(0, delay)
        
        elif jitter_type == JitterType.EQUAL:
            return delay * 0.5 + random.uniform(0, delay * 0.5)
        
        elif jitter_type == JitterType.DECORRELATED:
            if previous_delay > 0:
                return random.uniform(0, min(delay * 3, previous_delay * 3))
            else:
                return random.uniform(0, delay)
        
        return delay
    
    def _is_retryable_exception(self, exception: Exception, config: RetryConfig) -> bool:
        """Check if an exception should trigger a retry."""
        # Check non-retryable exceptions first
        if config.non_retryable_exceptions and isinstance(exception, config.non_retryable_exceptions):
            return False
        
        # Check retryable exceptions
        return isinstance(exception, config.retryable_exceptions)
    
    def _record_attempt(self, operation_name: str, attempt: RetryAttempt):
        """Record a retry attempt for statistics."""
        if operation_name not in self._operation_stats:
            self._operation_stats[operation_name] = []
        
        self._operation_stats[operation_name].append(attempt)
        
        # Keep only recent attempts (last 1000 per operation)
        if len(self._operation_stats[operation_name]) > 1000:
            self._operation_stats[operation_name] = self._operation_stats[operation_name][-1000:]
    
    def retry(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        operation_name: Optional[str] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic."""
        config = config or RetryConfig()
        operation_name = operation_name or func.__name__
        
        start_time = datetime.utcnow()
        timeout_time = None
        if config.timeout:
            timeout_time = start_time + timedelta(seconds=config.timeout)
        
        last_exception = None
        previous_delay = 0
        
        for attempt in range(1, config.max_attempts + 1):
            # Check timeout
            if timeout_time and datetime.utcnow() > timeout_time:
                raise RetryExhaustedError(
                    operation_name,
                    attempt - 1,
                    last_exception,
                    {'reason': 'timeout', 'timeout_seconds': config.timeout}
                )
            
            attempt_start = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - attempt_start
                
                # Record successful attempt
                self._record_attempt(operation_name, RetryAttempt(
                    attempt_number=attempt,
                    delay=0,
                    exception=None,
                    timestamp=datetime.utcnow(),
                    execution_time=execution_time
                ))
                
                if attempt > 1:
                    self.logger.info(
                        f"Operation '{operation_name}' succeeded on attempt {attempt} "
                        f"after {execution_time:.3f}s"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - attempt_start
                last_exception = e
                
                # Check if this exception is retryable
                if not self._is_retryable_exception(e, config):
                    self.logger.info(
                        f"Operation '{operation_name}' failed with non-retryable exception: {e}"
                    )
                    raise
                
                # Calculate delay for next attempt (if not the last attempt)
                delay = 0
                if attempt < config.max_attempts:
                    delay = self._calculate_delay(config, attempt, previous_delay)
                    previous_delay = delay
                
                # Record failed attempt
                self._record_attempt(operation_name, RetryAttempt(
                    attempt_number=attempt,
                    delay=delay,
                    exception=e,
                    timestamp=datetime.utcnow(),
                    execution_time=execution_time
                ))
                
                self.logger.warning(
                    f"Operation '{operation_name}' failed on attempt {attempt}/{config.max_attempts}: {e}"
                )
                
                # If this was the last attempt, raise RetryExhaustedError
                if attempt == config.max_attempts:
                    raise RetryExhaustedError(operation_name, attempt, e)
                
                # Call retry callback if provided
                if config.on_retry:
                    try:
                        config.on_retry(attempt, delay, e)
                    except Exception as callback_error:
                        self.logger.warning(f"Retry callback failed: {callback_error}")
                
                # Wait before next attempt
                if delay > 0:
                    self.logger.debug(f"Waiting {delay:.3f}s before attempt {attempt + 1}")
                    time.sleep(delay)
        
        # This should never be reached, but just in case
        raise RetryExhaustedError(operation_name, config.max_attempts, last_exception)
    
    async def async_retry(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        operation_name: Optional[str] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute an async function with retry logic."""
        config = config or RetryConfig()
        operation_name = operation_name or func.__name__
        
        start_time = datetime.utcnow()
        timeout_time = None
        if config.timeout:
            timeout_time = start_time + timedelta(seconds=config.timeout)
        
        last_exception = None
        previous_delay = 0
        
        for attempt in range(1, config.max_attempts + 1):
            # Check timeout
            if timeout_time and datetime.utcnow() > timeout_time:
                raise RetryExhaustedError(
                    operation_name,
                    attempt - 1,
                    last_exception,
                    {'reason': 'timeout', 'timeout_seconds': config.timeout}
                )
            
            attempt_start = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - attempt_start
                
                # Record successful attempt
                self._record_attempt(operation_name, RetryAttempt(
                    attempt_number=attempt,
                    delay=0,
                    exception=None,
                    timestamp=datetime.utcnow(),
                    execution_time=execution_time
                ))
                
                if attempt > 1:
                    self.logger.info(
                        f"Async operation '{operation_name}' succeeded on attempt {attempt} "
                        f"after {execution_time:.3f}s"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - attempt_start
                last_exception = e
                
                # Check if this exception is retryable
                if not self._is_retryable_exception(e, config):
                    self.logger.info(
                        f"Async operation '{operation_name}' failed with non-retryable exception: {e}"
                    )
                    raise
                
                # Calculate delay for next attempt (if not the last attempt)
                delay = 0
                if attempt < config.max_attempts:
                    delay = self._calculate_delay(config, attempt, previous_delay)
                    previous_delay = delay
                
                # Record failed attempt
                self._record_attempt(operation_name, RetryAttempt(
                    attempt_number=attempt,
                    delay=delay,
                    exception=e,
                    timestamp=datetime.utcnow(),
                    execution_time=execution_time
                ))
                
                self.logger.warning(
                    f"Async operation '{operation_name}' failed on attempt {attempt}/{config.max_attempts}: {e}"
                )
                
                # If this was the last attempt, raise RetryExhaustedError
                if attempt == config.max_attempts:
                    raise RetryExhaustedError(operation_name, attempt, e)
                
                # Call retry callback if provided
                if config.on_retry:
                    try:
                        if asyncio.iscoroutinefunction(config.on_retry):
                            await config.on_retry(attempt, delay, e)
                        else:
                            config.on_retry(attempt, delay, e)
                    except Exception as callback_error:
                        self.logger.warning(f"Retry callback failed: {callback_error}")
                
                # Wait before next attempt
                if delay > 0:
                    self.logger.debug(f"Waiting {delay:.3f}s before attempt {attempt + 1}")
                    await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        raise RetryExhaustedError(operation_name, config.max_attempts, last_exception)
    
    def get_operation_stats(self, operation_name: str) -> Optional[RetryStats]:
        """Get statistics for a specific operation."""
        if operation_name not in self._operation_stats:
            return None
        
        attempts = self._operation_stats[operation_name]
        if not attempts:
            return None
        
        successful_attempts = len([a for a in attempts if a.exception is None])
        failed_attempts = len([a for a in attempts if a.exception is not None])
        
        # Group attempts by operation (consecutive attempts with same timestamp group)
        operations = []
        current_operation = []
        
        for attempt in attempts:
            if current_operation and attempt.attempt_number == 1:
                operations.append(current_operation)
                current_operation = [attempt]
            else:
                current_operation.append(attempt)
        
        if current_operation:
            operations.append(current_operation)
        
        total_operations = len(operations)
        if total_operations > 0:
            total_attempts_across_operations = sum(len(op) for op in operations)
            avg_attempts = total_attempts_across_operations / total_operations
        else:
            avg_attempts = 0
        
        total_retry_time = sum(a.delay for a in attempts if a.delay > 0)
        last_attempt = max(a.timestamp for a in attempts) if attempts else None
        
        return RetryStats(
            operation_name=operation_name,
            total_attempts=len(attempts),
            successful_attempts=successful_attempts,
            failed_attempts=failed_attempts,
            average_attempts_per_operation=avg_attempts,
            total_retry_time=total_retry_time,
            last_attempt=last_attempt
        )
    
    def get_all_stats(self) -> Dict[str, RetryStats]:
        """Get statistics for all operations."""
        stats = {}
        for operation_name in self._operation_stats:
            operation_stats = self.get_operation_stats(operation_name)
            if operation_stats:
                stats[operation_name] = operation_stats
        return stats
    
    def clear_stats(self, operation_name: Optional[str] = None):
        """Clear statistics for an operation or all operations."""
        if operation_name:
            if operation_name in self._operation_stats:
                del self._operation_stats[operation_name]
        else:
            self._operation_stats.clear()


# Global retry manager instance
retry_manager = RetryManager()


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
    backoff_multiplier: float = 2.0,
    jitter_type: JitterType = JitterType.EQUAL,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (),
    timeout: Optional[float] = None,
    on_retry: Optional[Callable] = None,
    operation_name: Optional[str] = None
):
    """Decorator to add retry behavior to a function."""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_strategy=backoff_strategy,
        backoff_multiplier=backoff_multiplier,
        jitter_type=jitter_type,
        retryable_exceptions=retryable_exceptions,
        non_retryable_exceptions=non_retryable_exceptions,
        timeout=timeout,
        on_retry=on_retry
    )
    
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_manager.async_retry(func, config, op_name, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_manager.retry(func, config, op_name, *args, **kwargs)
            return sync_wrapper
    
    return decorator