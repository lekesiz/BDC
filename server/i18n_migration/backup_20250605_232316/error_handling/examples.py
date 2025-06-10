"""
Usage Examples for the Error Handling System.

This module provides comprehensive examples of how to use the error handling system
in various scenarios within the BDC project.
"""

import time
import random
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Example imports (adjust based on your actual project structure)
from .error_manager import error_manager, ErrorCategory, ErrorSeverity
from .circuit_breaker import circuit_breaker, CircuitBreaker, CircuitBreakerConfig
from .retry_manager import retry, RetryConfig, BackoffStrategy
from .error_monitor import error_monitor, AlertRule, AlertLevel, AlertChannel
from .user_messages import error_message_mapper, UserMessage, MessageType
from .error_recovery import with_recovery, with_fallback, error_recovery
from .middleware import ErrorHandlingMiddleware
from .config import config_manager
from .exceptions import *

# Setup logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Example 1: Basic Error Handling with Manual Error Management
# =============================================================================

def example_basic_error_handling():
    """Example of basic error handling with manual error management."""
    print("\n=== Basic Error Handling Example ===")
    
    def risky_operation(fail_probability=0.3):
        """Simulates an operation that might fail."""
        if random.random() < fail_probability:
            raise ValueError("Simulated failure in risky operation")
        return {"status": "success", "data": "operation completed"}
    
    try:
        result = risky_operation()
        print(f"Operation succeeded: {result}")
    except Exception as e:
        # Handle error through error manager
        error_context = error_manager.handle_error(
            e,
            context={
                "operation": "risky_operation",
                "parameters": {"fail_probability": 0.3}
            },
            user_id="user_123",
            request_id="req_456"
        )
        
        print(f"Error handled - ID: {error_context.error_id}")
        print(f"Category: {error_context.category.value}")
        print(f"Severity: {error_context.severity.value}")
        
        # Get user-friendly message
        user_message = error_message_mapper.map_exception_to_message(e, "en")
        print(f"User message: {user_message.message}")


# =============================================================================
# Example 2: Circuit Breaker Pattern for External Services
# =============================================================================

class ExternalPaymentService:
    """Mock external payment service that can fail."""
    
    def __init__(self, failure_rate=0.4):
        self.failure_rate = failure_rate
        self.call_count = 0
    
    def process_payment(self, amount: float, currency: str = "USD") -> Dict[str, Any]:
        """Simulates payment processing that might fail."""
        self.call_count += 1
        
        if random.random() < self.failure_rate:
            raise ConnectionError(f"Payment service unavailable (call #{self.call_count})")
        
        return {
            "transaction_id": f"txn_{self.call_count}",
            "amount": amount,
            "currency": currency,
            "status": "completed"
        }


def example_circuit_breaker():
    """Example of using circuit breaker pattern for external services."""
    print("\n=== Circuit Breaker Example ===")
    
    payment_service = ExternalPaymentService(failure_rate=0.6)  # High failure rate
    
    # Configure circuit breaker
    @circuit_breaker(
        name="payment_service",
        failure_threshold=3,
        recovery_timeout=5,  # Short timeout for demo
        success_threshold=2
    )
    def make_payment(amount, currency="USD"):
        return payment_service.process_payment(amount, currency)
    
    # Simulate multiple payment attempts
    for i in range(10):
        try:
            result = make_payment(100.0)
            print(f"Payment {i+1} succeeded: {result['transaction_id']}")
        except CircuitBreakerError as e:
            print(f"Payment {i+1} blocked by circuit breaker: {e.message}")
        except Exception as e:
            print(f"Payment {i+1} failed: {e}")
        
        time.sleep(0.5)  # Brief pause between attempts
    
    # Check circuit breaker stats
    from .circuit_breaker import circuit_breaker_manager
    stats = circuit_breaker_manager.get_breaker("payment_service").get_stats()
    print(f"\nCircuit Breaker Stats:")
    print(f"State: {stats.state.value}")
    print(f"Total requests: {stats.total_requests}")
    print(f"Failed requests: {stats.failed_requests}")
    print(f"Success rate: {stats.successful_requests/stats.total_requests*100:.1f}%")


# =============================================================================
# Example 3: Retry Mechanisms with Different Strategies
# =============================================================================

class UnstableDatabase:
    """Mock database service with intermittent failures."""
    
    def __init__(self):
        self.query_count = 0
        self.failure_pattern = [True, True, False, True, False, False]  # Predefined pattern
    
    def query_user(self, user_id: int) -> Dict[str, Any]:
        """Simulates database query that might fail."""
        self.query_count += 1
        
        # Use failure pattern to simulate realistic intermittent failures
        pattern_index = (self.query_count - 1) % len(self.failure_pattern)
        if self.failure_pattern[pattern_index]:
            raise ConnectionError(f"Database connection timeout (query #{self.query_count})")
        
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "query_count": self.query_count
        }


def example_retry_mechanisms():
    """Example of different retry strategies."""
    print("\n=== Retry Mechanisms Example ===")
    
    db = UnstableDatabase()
    
    # Example 1: Exponential backoff retry
    @retry(
        max_attempts=5,
        base_delay=0.5,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        retryable_exceptions=(ConnectionError,)
    )
    def get_user_with_exponential_backoff(user_id):
        print(f"  Attempting to query user {user_id}...")
        return db.query_user(user_id)
    
    # Example 2: Linear backoff retry
    @retry(
        max_attempts=4,
        base_delay=0.3,
        backoff_strategy=BackoffStrategy.LINEAR,
        retryable_exceptions=(ConnectionError,)
    )
    def get_user_with_linear_backoff(user_id):
        print(f"  Attempting to query user {user_id}...")
        return db.query_user(user_id)
    
    # Test exponential backoff
    print("\nTesting exponential backoff:")
    try:
        user = get_user_with_exponential_backoff(123)
        print(f"Success: {user}")
    except RetryExhaustedError as e:
        print(f"All retries failed: {e}")
    
    # Reset database state
    db.query_count = 0
    
    # Test linear backoff
    print("\nTesting linear backoff:")
    try:
        user = get_user_with_linear_backoff(456)
        print(f"Success: {user}")
    except RetryExhaustedError as e:
        print(f"All retries failed: {e}")


# =============================================================================
# Example 4: Error Monitoring and Alerting
# =============================================================================

def example_error_monitoring():
    """Example of error monitoring and custom alerts."""
    print("\n=== Error Monitoring Example ===")
    
    # Create custom alert rule
    def critical_database_errors_condition(metrics: Dict[str, Any]) -> bool:
        """Alert when database errors exceed 3 in recent period."""
        db_errors = metrics.get('errors_by_category', {}).get('database', 0)
        return db_errors >= 3
    
    alert_rule = AlertRule(
        name="critical_database_errors",
        description="High number of database errors detected",
        condition=critical_database_errors_condition,
        level=AlertLevel.CRITICAL,
        channels=[AlertChannel.LOG],
        cooldown_minutes=1  # Short cooldown for demo
    )
    
    error_monitor.add_alert_rule(alert_rule)
    
    # Simulate database errors to trigger alert
    from ..exceptions import ExternalServiceException
    
    print("Simulating database errors...")
    for i in range(5):
        try:
            # Simulate different types of database errors
            if i % 2 == 0:
                raise ConnectionError(f"Database connection failed #{i+1}")
            else:
                raise TimeoutError(f"Database query timeout #{i+1}")
        except Exception as e:
            # Classify as database error and handle
            error_context = error_manager.handle_error(
                e,
                context={"operation": "database_query", "query_id": f"q_{i+1}"}
            )
            error_monitor.record_error(error_context)
    
    # Check metrics and alerts
    metrics = error_monitor.get_current_metrics()
    print(f"\nCurrent metrics:")
    print(f"Total errors: {metrics['total_errors']}")
    print(f"Error rate: {metrics['error_rate_per_minute']:.2f}/min")
    print(f"Errors by category: {metrics['errors_by_category']}")
    
    alert_history = error_monitor.get_alert_history(hours=1)
    print(f"\nAlerts triggered: {len(alert_history)}")
    for alert in alert_history:
        print(f"  - {alert['rule_name']}: {alert['message']}")


# =============================================================================
# Example 5: User-Friendly Error Messages with Localization
# =============================================================================

def example_user_friendly_messages():
    """Example of user-friendly error messages in different languages."""
    print("\n=== User-Friendly Messages Example ===")
    
    # Add custom error message
    custom_message_en = UserMessage(
        code="PAYMENT_DECLINED",
        message="Your payment was declined by your bank.",
        message_type=MessageType.ERROR,
        suggested_actions=[
            "Check that your card has sufficient funds",
            "Verify your card details are correct",
            "Try a different payment method",
            "Contact your bank if the problem persists"
        ],
        support_info="If you need help, contact our support team with reference code: PAYMENT_DECLINED"
    )
    
    custom_message_es = UserMessage(
        code="PAYMENT_DECLINED",
        message="Su pago fue rechazado por su banco.",
        message_type=MessageType.ERROR,
        suggested_actions=[
            "Verifique que su tarjeta tenga fondos suficientes",
            "Verifique que los detalles de su tarjeta sean correctos",
            "Intente con un método de pago diferente",
            "Contacte a su banco si el problema persiste"
        ],
        support_info="Si necesita ayuda, contacte a nuestro equipo de soporte con el código de referencia: PAYMENT_DECLINED"
    )
    
    error_message_mapper.add_message_mapping("en", "PAYMENT_DECLINED", custom_message_en)
    error_message_mapper.add_message_mapping("es", "PAYMENT_DECLINED", custom_message_es)
    
    # Simulate different error scenarios
    test_exceptions = [
        (ValueError("Invalid email format"), "INVALID_EMAIL"),
        (PermissionError("Access denied"), "ACCESS_DENIED"),
        (ConnectionError("Network error"), "NETWORK_ERROR"),
        (Exception("Payment declined"), "PAYMENT_DECLINED")  # Custom error
    ]
    
    for exception, expected_code in test_exceptions:
        print(f"\nTesting: {type(exception).__name__}")
        
        # English message
        en_message = error_message_mapper.map_exception_to_message(exception, "en")
        print(f"EN: {en_message.message}")
        if en_message.suggested_actions:
            print(f"    Actions: {', '.join(en_message.suggested_actions[:2])}...")
        
        # Spanish message
        es_message = error_message_mapper.map_exception_to_message(exception, "es")
        print(f"ES: {es_message.message}")
        if es_message.suggested_actions:
            print(f"    Acciones: {', '.join(es_message.suggested_actions[:2])}...")


# =============================================================================
# Example 6: Error Recovery and Fallback Strategies
# =============================================================================

class UserProfileService:
    """Mock user profile service that can fail."""
    
    def __init__(self):
        self.call_count = 0
        self.cache = {}
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile - might fail."""
        self.call_count += 1
        
        # Simulate service failures
        if self.call_count <= 2:
            raise ConnectionError("Profile service temporarily unavailable")
        
        # Return profile data
        profile = {
            "id": user_id,
            "name": f"User {user_id}",
            "avatar": f"https://example.com/avatars/{user_id}.jpg",
            "preferences": {"theme": "dark", "language": "en"}
        }
        
        # Cache the result
        self.cache[user_id] = profile
        return profile
    
    def get_cached_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached profile data."""
        return self.cache.get(user_id)


def example_error_recovery():
    """Example of error recovery strategies."""
    print("\n=== Error Recovery Example ===")
    
    profile_service = UserProfileService()
    
    # Example 1: Fallback to cached data
    @with_recovery(cache_key="user_profile_123")
    def get_user_profile_with_cache(user_id):
        print(f"  Attempting to get profile for user {user_id}")
        return profile_service.get_profile(user_id)
    
    # Example 2: Fallback to default values
    @with_fallback(fallback_value={"id": "unknown", "name": "Guest User"})
    def get_user_profile_with_default(user_id):
        print(f"  Attempting to get profile for user {user_id}")
        return profile_service.get_profile(user_id)
    
    # Example 3: Fallback to alternative function
    def get_basic_profile(user_id):
        print(f"  Using basic profile fallback for user {user_id}")
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "avatar": "/default-avatar.png",
            "preferences": {"theme": "light", "language": "en"}
        }
    
    @with_fallback(fallback_function=get_basic_profile)
    def get_user_profile_with_function_fallback(user_id):
        print(f"  Attempting to get profile for user {user_id}")
        return profile_service.get_profile(user_id)
    
    # Test different recovery strategies
    print("\nTesting fallback to default values:")
    try:
        profile = get_user_profile_with_default("123")
        print(f"Got profile: {profile}")
    except Exception as e:
        print(f"Recovery failed: {e}")
    
    print("\nTesting fallback to alternative function:")
    try:
        profile = get_user_profile_with_function_fallback("456")
        print(f"Got profile: {profile}")
    except Exception as e:
        print(f"Recovery failed: {e}")
    
    # Reset service state for cache test
    profile_service.call_count = 0
    
    print("\nTesting cache fallback (after initial success):")
    # First call succeeds and caches data
    try:
        profile = get_user_profile_with_cache("789")
        print(f"First call succeeded: {profile}")
    except Exception as e:
        print(f"First call failed: {e}")
    
    # Simulate service becoming unavailable
    profile_service.call_count = 1  # Will cause next call to fail
    
    try:
        profile = get_user_profile_with_cache("789")
        print(f"Second call with cache fallback: {profile}")
    except Exception as e:
        print(f"Cache fallback failed: {e}")


# =============================================================================
# Example 7: Async Error Handling
# =============================================================================

async def example_async_error_handling():
    """Example of async error handling with retry."""
    print("\n=== Async Error Handling Example ===")
    
    call_count = 0
    
    @retry(max_attempts=3, base_delay=0.5)
    async def async_api_call(endpoint: str):
        nonlocal call_count
        call_count += 1
        
        print(f"  Async API call #{call_count} to {endpoint}")
        
        # Simulate async operation that might fail
        await asyncio.sleep(0.1)  # Simulate network delay
        
        if call_count <= 2:
            raise ConnectionError(f"API call failed (attempt #{call_count})")
        
        return {"endpoint": endpoint, "data": "success", "attempt": call_count}
    
    try:
        result = await async_api_call("/api/data")
        print(f"Async call succeeded: {result}")
    except RetryExhaustedError as e:
        print(f"All async retries failed: {e}")


# =============================================================================
# Example 8: Integration with Flask Application
# =============================================================================

def example_flask_integration():
    """Example of integrating error handling with Flask."""
    print("\n=== Flask Integration Example ===")
    
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        # Configure error handling
        config_manager.load_from_dict({
            'enabled': True,
            'middleware': {
                'include_stack_trace': False,
                'log_request_data': True
            },
            'user_messages': {
                'default_locale': 'en'
            }
        })
        
        # Initialize error handling middleware
        error_middleware = ErrorHandlingMiddleware(
            app,
            enable_monitoring=True,
            include_stack_trace=False
        )
        
        @app.route('/api/test-error')
        def test_error():
            """Endpoint that demonstrates error handling."""
            error_type = request.args.get('type', 'validation')
            
            if error_type == 'validation':
                raise ValueError("Invalid input parameter")
            elif error_type == 'auth':
                from ..exceptions import UnauthorizedException
                raise UnauthorizedException("Authentication required")
            elif error_type == 'not_found':
                from ..exceptions import NotFoundException
                raise NotFoundException("Resource not found")
            else:
                raise Exception("Unknown error type")
        
        @app.route('/api/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "error_stats": error_monitor.get_current_metrics()
            })
        
        print("Flask app configured with error handling middleware")
        print("Example endpoints:")
        print("  GET /api/test-error?type=validation")
        print("  GET /api/test-error?type=auth") 
        print("  GET /api/test-error?type=not_found")
        print("  GET /api/health")
        
        return app
        
    except ImportError:
        print("Flask not available - skipping Flask integration example")
        return None


# =============================================================================
# Example 9: Configuration Management
# =============================================================================

def example_configuration_management():
    """Example of configuration management."""
    print("\n=== Configuration Management Example ===")
    
    # Load configuration from multiple sources
    config_manager.load_default_config()
    
    # Override with custom settings
    custom_config = {
        "circuit_breaker": {
            "failure_threshold": 10,
            "recovery_timeout": 120
        },
        "retry": {
            "max_attempts": 5,
            "base_delay": 2.0
        },
        "monitoring": {
            "error_rate_threshold": 20.0
        },
        "custom_settings": {
            "feature_flags": {
                "advanced_recovery": True,
                "detailed_logging": True
            }
        }
    }
    
    config_manager.load_from_dict(custom_config)
    
    # Validate configuration
    issues = config_manager.validate_config()
    if issues:
        print(f"Configuration issues found: {issues}")
    else:
        print("Configuration is valid")
    
    # Display current configuration
    current_config = config_manager.get_config()
    print(f"\nCurrent configuration:")
    print(f"Circuit Breaker failure threshold: {current_config.circuit_breaker.failure_threshold}")
    print(f"Retry max attempts: {current_config.retry.max_attempts}")
    print(f"Monitoring error rate threshold: {current_config.monitoring.error_rate_threshold}")
    
    # Export configuration
    config_json = config_manager.export_config('json')
    print(f"\nConfiguration exported (JSON): {len(config_json)} characters")


# =============================================================================
# Main Example Runner
# =============================================================================

def run_all_examples():
    """Run all examples in sequence."""
    print("🚀 Running Error Handling System Examples")
    print("=" * 60)
    
    try:
        # Run synchronous examples
        example_basic_error_handling()
        example_circuit_breaker()
        example_retry_mechanisms()
        example_error_monitoring()
        example_user_friendly_messages()
        example_error_recovery()
        example_configuration_management()
        
        # Run async example
        print("\nRunning async example...")
        asyncio.run(example_async_error_handling())
        
        # Run Flask integration example
        flask_app = example_flask_integration()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("\nKey takeaways:")
        print("1. Use decorators for common patterns (circuit breaker, retry, fallback)")
        print("2. Configure monitoring and alerting for production systems")
        print("3. Provide user-friendly, localized error messages")
        print("4. Implement appropriate recovery strategies for different failure modes")
        print("5. Use configuration management for flexible error handling behavior")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()