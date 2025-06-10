"""Service container for dependency injection management."""

from typing import Any, Callable, Dict, List, Optional, Type, Union
from threading import Lock
from flask import Flask, g, current_app
from sqlalchemy.orm import Session

from app.extensions import db
from app.utils.logger import get_logger


class ServiceContainer:
    """
    Dependency injection container for managing service instances.
    
    Features:
    - Service registration with factory functions
    - Singleton and transient lifecycle management
    - Dependency resolution with circular dependency detection
    - Request-scoped services
    - Service aliases
    - Service metadata
    - Thread-safe operations
    """
    
    def __init__(self):
        """Initialize the service container."""
        self._services: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._aliases: Dict[str, str] = {}
        self._lock = Lock()
        self._resolving: List[str] = []
        self._logger = get_logger('ServiceContainer')
    
    def register(self, 
                 name: str, 
                 factory: Union[Callable, Type],
                 singleton: bool = False,
                 dependencies: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 interface: Optional[Type] = None) -> None:
        """
        Register a service with the container.
        
        Args:
            name: Service name
            factory: Factory function or class to create the service
            singleton: Whether to create only one instance
            dependencies: List of dependency service names
            metadata: Additional metadata for the service
            interface: Interface that the service implements
        """
        with self._lock:
            self._services[name] = {
                'factory': factory,
                'singleton': singleton,
                'dependencies': dependencies or [],
                'metadata': metadata or {},
                'interface': interface
            }
            self._logger.debug(f"Registered service: {name} (singleton={singleton})")
    
    def register_factory(self, name: str, factory: Callable, **kwargs) -> None:
        """Register a service with a factory function."""
        self.register(name, factory, **kwargs)
    
    def register_class(self, name: str, cls: Type, **kwargs) -> None:
        """Register a service with a class."""
        def factory():
            dependencies = kwargs.get('dependencies', [])
            dep_instances = {dep: self.resolve(dep) for dep in dependencies}
            return cls(**dep_instances)
        
        self.register(name, factory, **kwargs)
    
    def register_instance(self, name: str, instance: Any, **kwargs) -> None:
        """Register a pre-created instance as a singleton."""
        self.register(name, lambda: instance, singleton=True, **kwargs)
    
    def alias(self, alias: str, service_name: str) -> None:
        """Create an alias for a service."""
        with self._lock:
            self._aliases[alias] = service_name
            self._logger.debug(f"Created alias: {alias} -> {service_name}")
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Args:
            name: Service name or alias
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
            RuntimeError: If circular dependency detected
        """
        # Resolve alias if exists
        actual_name = self._aliases.get(name, name)
        
        # Check if service is registered
        if actual_name not in self._services:
            raise ValueError(f"Service '{name}' is not registered")
        
        # Check for circular dependencies
        if actual_name in self._resolving:
            circular_path = ' -> '.join(self._resolving + [actual_name])
            raise RuntimeError(f"Circular dependency detected: {circular_path}")
        
        try:
            self._resolving.append(actual_name)
            
            service_config = self._services[actual_name]
            
            # Return singleton if exists
            if service_config['singleton'] and actual_name in self._singletons:
                return self._singletons[actual_name]
            
            # Resolve dependencies
            dependencies = {}
            for dep_name in service_config['dependencies']:
                dependencies[dep_name] = self.resolve(dep_name)
            
            # Create instance
            factory = service_config['factory']
            
            if dependencies:
                instance = factory(**dependencies)
            else:
                instance = factory()
            
            # Store singleton
            if service_config['singleton']:
                with self._lock:
                    self._singletons[actual_name] = instance
            
            self._logger.debug(f"Resolved service: {actual_name}")
            
            return instance
            
        finally:
            self._resolving.remove(actual_name)
    
    def resolve_many(self, interface: Type) -> List[Any]:
        """
        Resolve all services implementing an interface.
        
        Args:
            interface: Interface type
            
        Returns:
            List of service instances
        """
        services = []
        
        for name, config in self._services.items():
            if config.get('interface') == interface:
                services.append(self.resolve(name))
        
        return services
    
    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        actual_name = self._aliases.get(name, name)
        return actual_name in self._services
    
    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a service."""
        actual_name = self._aliases.get(name, name)
        if actual_name in self._services:
            return self._services[actual_name]['metadata']
        return None
    
    def list_services(self) -> List[str]:
        """List all registered service names."""
        return list(self._services.keys())
    
    def clear_singletons(self) -> None:
        """Clear all singleton instances."""
        with self._lock:
            self._singletons.clear()
            self._logger.debug("Cleared all singleton instances")
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a service.
        
        Args:
            name: Service name
            
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if name in self._services:
                del self._services[name]
                if name in self._singletons:
                    del self._singletons[name]
                # Remove aliases
                self._aliases = {k: v for k, v in self._aliases.items() if v != name}
                self._logger.debug(f"Unregistered service: {name}")
                return True
            return False
    
    def configure_defaults(self) -> None:
        """Configure default services."""
        # Database session
        self.register('db_session', lambda: db.session, singleton=False)
        
        # Repositories
        self._register_repositories()
        
        # Services
        self._register_services()
        
        self._logger.info("Configured default services")
    
    def _register_repositories(self) -> None:
        """Register default repository services."""
        from app.repositories.user_repository import UserRepository
        from app.repositories.beneficiary_repository import BeneficiaryRepository
        from app.repositories.notification_repository import NotificationRepository
        from app.repositories.document_repository import DocumentRepository
        from app.repositories.appointment_repository import AppointmentRepository
        from app.repositories.program_repository import ProgramRepository
        from app.repositories.evaluation_repository import EvaluationRepository
        
        # User repository
        self.register('user_repository', 
                     lambda db_session: UserRepository(db_session),
                     dependencies=['db_session'])
        
        # Beneficiary repository
        self.register('beneficiary_repository',
                     lambda db_session: BeneficiaryRepository(db_session),
                     dependencies=['db_session'])
        
        # Notification repository
        self.register('notification_repository',
                     lambda db_session: NotificationRepository(db_session),
                     dependencies=['db_session'])
        
        # Document repository
        self.register('document_repository',
                     lambda db_session: DocumentRepository(db_session),
                     dependencies=['db_session'])
        
        # Appointment repository
        self.register('appointment_repository',
                     lambda db_session: AppointmentRepository(db_session),
                     dependencies=['db_session'])
        
        # Program repository
        self.register('program_repository',
                     lambda db_session: ProgramRepository(db_session),
                     dependencies=['db_session'])
        
        # Evaluation repository
        self.register('evaluation_repository',
                     lambda db_session: EvaluationRepository(db_session),
                     dependencies=['db_session'])
    
    def _register_services(self) -> None:
        """Register default services."""
        from app.services.auth_service import AuthServiceV2
        from app.services.user_service import UserServiceV2
        from app.services.beneficiary_service import BeneficiaryService
        from app.services.notification_service import NotificationService
        from app.services.document_service import DocumentService
        from app.services.appointment_service import AppointmentService
        from app.services.program_service import ProgramService
        from app.services.evaluation_service import EvaluationService
        from app.core.security import SecurityManager
        
        # Security manager
        self.register('security_manager', SecurityManager, singleton=True)
        
        # Auth service
        self.register('auth_service',
                     lambda user_repository, security_manager: AuthServiceV2(
                         user_repository=user_repository,
                         security_manager=security_manager
                     ),
                     dependencies=['user_repository', 'security_manager'])
        
        # User service
        self.register('user_service',
                     lambda user_repository, security_manager: UserServiceV2(
                         user_repository=user_repository,
                         security_manager=security_manager
                     ),
                     dependencies=['user_repository', 'security_manager'])
        
        # Beneficiary service
        self.register('beneficiary_service',
                     lambda beneficiary_repository, user_repository: BeneficiaryService(
                         beneficiary_repository=beneficiary_repository,
                         user_repository=user_repository
                     ),
                     dependencies=['beneficiary_repository', 'user_repository'])
        
        # Notification service
        self.register('notification_service',
                     lambda notification_repository: NotificationService(
                         notification_repository=notification_repository
                     ),
                     dependencies=['notification_repository'])
        
        # Document service
        self.register('document_service',
                     lambda document_repository, user_repository, beneficiary_repository, notification_service: DocumentService(
                         document_repository=document_repository,
                         user_repository=user_repository,
                         beneficiary_repository=beneficiary_repository,
                         notification_service=notification_service
                     ),
                     dependencies=['document_repository', 'user_repository', 
                                 'beneficiary_repository', 'notification_service'])
        
        # Appointment service
        self.register('appointment_service',
                     lambda appointment_repository: AppointmentService(
                         appointment_repository=appointment_repository
                     ),
                     dependencies=['appointment_repository'])
        
        # Program service
        self.register('program_service',
                     lambda program_repository: ProgramService(
                         program_repository=program_repository
                     ),
                     dependencies=['program_repository'])
        
        # Evaluation service
        self.register('evaluation_service',
                     lambda evaluation_repository, beneficiary_repository, notification_service: EvaluationService(
                         evaluation_repository=evaluation_repository,
                         beneficiary_repository=beneficiary_repository,
                         notification_service=notification_service
                     ),
                     dependencies=['evaluation_repository', 'beneficiary_repository', 
                                 'notification_service'])


# Global container instance
_container = ServiceContainer()


def get_service_container() -> ServiceContainer:
    """Get the global service container instance."""
    return _container


def setup_request_container(app: Flask) -> None:
    """
    Set up per-request container handling.
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        """Create request-scoped container."""
        if not hasattr(g, 'container'):
            g.container = ServiceContainer()
            g.container.configure_defaults()
    
    @app.teardown_request
    def teardown_request(exception=None):
        """Clean up request-scoped container."""
        if hasattr(g, 'container'):
            g.container.clear_singletons()


def get_request_container() -> ServiceContainer:
    """Get request-scoped container or global container."""
    if hasattr(g, 'container'):
        return g.container
    return _container


# Configure global container on import
_container.configure_defaults()