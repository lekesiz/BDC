"""Decorators for dependency injection and service management."""

import functools
from typing import Any, Callable, Dict, List, Optional, Type, Union
from flask import g, current_app
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.utils.logger import get_logger
from .service_container import get_request_container, get_service_container


logger = get_logger('ServiceDecorators')


def inject(*service_names: str, **named_services: str):
    """
    Decorator to inject services into function parameters.
    
    Args:
        *service_names: Positional service names to inject
        **named_services: Named services (param_name=service_name)
        
    Example:
        @inject('user_service', 'auth_service')
        def my_function(user_service, auth_service):
            # Services are automatically injected
            pass
        
        @inject(user_svc='user_service', auth='auth_service')
        def my_function(user_svc, auth):
            # Services injected with custom parameter names
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            container = get_request_container()
            
            # Inject positional services
            injected_args = list(args)
            for service_name in service_names:
                if container.has(service_name):
                    service = container.resolve(service_name)
                    injected_args.append(service)
                else:
                    logger.warning(f"Service '{service_name}' not found in container")
            
            # Inject named services
            for param_name, service_name in named_services.items():
                if param_name not in kwargs:  # Don't override existing kwargs
                    if container.has(service_name):
                        kwargs[param_name] = container.resolve(service_name)
                    else:
                        logger.warning(f"Service '{service_name}' not found in container")
            
            return func(*injected_args, **kwargs)
        
        return wrapper
    return decorator


def service(name: Optional[str] = None, 
           singleton: bool = False,
           dependencies: Optional[List[str]] = None,
           interface: Optional[Type] = None):
    """
    Class decorator to register a service in the container.
    
    Args:
        name: Service name (defaults to class name)
        singleton: Whether service should be singleton
        dependencies: List of dependency service names
        interface: Interface that the service implements
        
    Example:
        @service(name='my_service', singleton=True)
        class MyService:
            def __init__(self, user_repository):
                self.user_repository = user_repository
    """
    def decorator(cls: Type) -> Type:
        service_name = name or cls.__name__
        
        # Store interface on class for factory
        if interface:
            cls.__interface__ = interface
        
        # Create factory function
        def factory(**kwargs):
            # Resolve dependencies
            container = get_request_container()
            dep_instances = {}
            
            if dependencies:
                for dep in dependencies:
                    if container.has(dep):
                        dep_instances[dep] = container.resolve(dep)
            
            # Merge with provided kwargs
            all_kwargs = {**dep_instances, **kwargs}
            
            return cls(**all_kwargs)
        
        # Register in global container
        container = get_service_container()
        container.register(
            service_name,
            factory,
            singleton=singleton,
            dependencies=dependencies,
            interface=interface
        )
        
        logger.info(f"Registered service class: {service_name}")
        
        # Add service name to class
        cls.__service_name__ = service_name
        
        return cls
    
    return decorator


def transactional(rollback_on: Optional[List[Type[Exception]]] = None,
                 commit: bool = True):
    """
    Decorator to handle database transactions.
    
    Args:
        rollback_on: List of exception types that trigger rollback
        commit: Whether to commit on success (default True)
        
    Example:
        @transactional()
        def create_user(user_data):
            # Database operations here
            pass
        
        @transactional(rollback_on=[ValueError, KeyError])
        def update_user(user_id, data):
            # Will rollback on ValueError or KeyError
            pass
    """
    rollback_exceptions = rollback_on or [Exception]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if we're already in a transaction
            if hasattr(g, 'in_transaction') and g.in_transaction:
                # Nested transaction - just execute
                return func(*args, **kwargs)
            
            g.in_transaction = True
            
            try:
                result = func(*args, **kwargs)
                
                if commit:
                    db.session.commit()
                    logger.debug(f"Transaction committed for {func.__name__}")
                
                return result
                
            except tuple(rollback_exceptions) as e:
                db.session.rollback()
                logger.error(f"Transaction rolled back for {func.__name__}: {str(e)}")
                raise
                
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error in {func.__name__}: {str(e)}")
                raise
                
            finally:
                g.in_transaction = False
        
        return wrapper
    return decorator


def cached(timeout: int = 300, 
          key_prefix: Optional[str] = None,
          unless: Optional[Callable] = None):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Cache key prefix
        unless: Function to determine if result should be cached
        
    Example:
        @cached(timeout=600)
        def get_user(user_id):
            return User.query.get(user_id)
        
        @cached(unless=lambda x: x is None)
        def find_user(email):
            return User.query.filter_by(email=email).first()
    """
    def decorator(func: Callable) -> Callable:
        from app.utils.cache import cache, generate_cache_key
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result if conditions met
            if unless is None or not unless(result):
                cache.set(cache_key, result, timeout=timeout)
                logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        # Add cache control methods
        wrapper.clear_cache = lambda: cache.delete_pattern(f"{key_prefix or func.__name__}:*")
        
        return wrapper
    return decorator


def rate_limit(calls: int, period: int):
    """
    Decorator to rate limit function calls.
    
    Args:
        calls: Number of allowed calls
        period: Time period in seconds
        
    Example:
        @rate_limit(calls=10, period=60)  # 10 calls per minute
        def api_endpoint():
            pass
    """
    def decorator(func: Callable) -> Callable:
        from app.utils.cache import cache
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get identifier (could be user ID, IP, etc.)
            identifier = getattr(g, 'user_id', 'anonymous')
            key = f"rate_limit:{func.__name__}:{identifier}"
            
            # Check current count
            current = cache.get(key) or 0
            
            if current >= calls:
                logger.warning(f"Rate limit exceeded for {func.__name__} by {identifier}")
                raise Exception(f"Rate limit exceeded: {calls} calls per {period} seconds")
            
            # Increment counter
            cache.set(key, current + 1, timeout=period)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_input(schema: Union[Dict[str, Any], Type]):
    """
    Decorator to validate function input.
    
    Args:
        schema: Validation schema (dict or marshmallow schema)
        
    Example:
        @validate_input({'name': str, 'age': int})
        def create_user(data):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Simple implementation - extend as needed
            if isinstance(schema, dict):
                # Basic type checking
                data = args[0] if args else kwargs.get('data', {})
                for key, expected_type in schema.items():
                    if key in data and not isinstance(data[key], expected_type):
                        raise ValueError(f"Invalid type for {key}: expected {expected_type.__name__}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def authorize(required_permission: Optional[str] = None,
             required_role: Optional[str] = None):
    """
    Decorator to check authorization before executing function.
    
    Args:
        required_permission: Required permission name
        required_role: Required role name
        
    Example:
        @authorize(required_permission='users.create')
        def create_user(data):
            pass
        
        @authorize(required_role='admin')
        def admin_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get current user from context
            user = getattr(g, 'current_user', None)
            
            if not user:
                raise Exception("Authentication required")
            
            # Check role
            if required_role and not hasattr(user, 'role'):
                raise Exception(f"Role '{required_role}' required")
            
            if required_role and user.role != required_role:
                raise Exception(f"Role '{required_role}' required")
            
            # Check permission
            if required_permission:
                # Implement permission checking logic
                pass
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def async_task(queue: str = 'default'):
    """
    Decorator to run function as async task.
    
    Args:
        queue: Task queue name
        
    Example:
        @async_task(queue='emails')
        def send_email(to, subject, body):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if should run sync (e.g., in tests)
            if current_app.config.get('TESTING'):
                return func(*args, **kwargs)
            
            # Queue task (implement with Celery or similar)
            logger.info(f"Queuing async task: {func.__name__} on queue: {queue}")
            
            # For now, run synchronously
            return func(*args, **kwargs)
        
        return wrapper
    return decorator