"""Lazy-loading dependency injection container."""

from typing import Dict, Any, Type, Callable, TypeVar, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import threading
import logging
from flask import g, current_app, has_app_context
from sqlalchemy.orm import Session

T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime enumeration."""
    SINGLETON = "singleton"
    SCOPED = "scoped"        # Per request
    TRANSIENT = "transient"  # New instance each time


@dataclass
class ServiceDescriptor:
    """Service registration descriptor."""
    interface: Type
    implementation: Optional[Type] = None
    factory: Optional[Callable] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    lazy: bool = True
    dependencies: List[Type] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ILazyContainer(ABC):
    """Interface for lazy-loading dependency injection container."""
    
    @abstractmethod
    def register(self, interface: Type[T], implementation: Type[T], 
                lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
                lazy: bool = True) -> None:
        """Register a service."""
        pass
    
    @abstractmethod
    def register_factory(self, interface: Type[T], factory: Callable[[], T],
                        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
                        lazy: bool = True) -> None:
        """Register a factory function."""
        pass
    
    @abstractmethod
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        pass
    
    @abstractmethod
    def is_registered(self, interface: Type) -> bool:
        """Check if a service is registered."""
        pass


class LazyServiceProxy:
    """Proxy that delays service creation until first access."""
    
    def __init__(self, container: 'LazyDIContainer', interface: Type):
        """Initialize proxy.
        
        Args:
            container: Container instance
            interface: Service interface
        """
        self._container = container
        self._interface = interface
        self._instance = None
        self._lock = threading.Lock()
    
    def _get_instance(self):
        """Get the actual service instance."""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._container._create_instance_direct(self._interface)
        return self._instance
    
    def __getattr__(self, name):
        """Delegate attribute access to the actual instance."""
        instance = self._get_instance()
        return getattr(instance, name)
    
    def __call__(self, *args, **kwargs):
        """Delegate calls to the actual instance."""
        instance = self._get_instance()
        return instance(*args, **kwargs)


class LazyDIContainer(ILazyContainer):
    """Lazy-loading dependency injection container with enhanced lifetime management."""
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._proxies: Dict[Type, LazyServiceProxy] = {}
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
        self._initialized = False
    
    def initialize(self, app) -> None:
        """Initialize the container with Flask app context.
        
        Args:
            app: Flask application instance
        """
        if self._initialized:
            return
        
        with app.app_context():
            self._configure_default_services()
            self._setup_request_teardown(app)
            self._initialized = True
            self._logger.info("Lazy DI container initialized")
    
    def _configure_default_services(self) -> None:
        """Configure default service bindings with lazy loading."""
        # Import services only when needed to avoid import-time dependencies
        
        # Register core services as singletons
        self.register_factory(
            self._get_security_manager_interface(),
            self._create_security_manager,
            ServiceLifetime.SINGLETON,
            lazy=True
        )
        
        # Register repositories as scoped
        self.register_factory(
            self._get_user_repository_interface(),
            self._create_user_repository,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_document_repository_interface(),
            self._create_document_repository,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_evaluation_repository_interface(),
            self._create_evaluation_repository,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_program_repository_interface(),
            self._create_program_repository,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_notification_repository_interface(),
            self._create_notification_repository,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_calendar_repository_interface(),
            self._create_calendar_repository,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        # Register services as scoped
        self.register_factory(
            self._get_auth_service_interface(),
            self._create_auth_service,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_document_service_interface(),
            self._create_document_service,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_evaluation_service_interface(),
            self._create_evaluation_service,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_program_service_interface(),
            self._create_program_service,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_notification_service_interface(),
            self._create_notification_service,
            ServiceLifetime.SCOPED,
            lazy=True
        )
        
        self.register_factory(
            self._get_calendar_service_interface(),
            self._create_calendar_service,
            ServiceLifetime.SCOPED,
            lazy=True
        )
    
    def register(self, interface: Type[T], implementation: Type[T], 
                lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
                lazy: bool = True) -> None:
        """Register a service with its implementation."""
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=lifetime,
            lazy=lazy
        )
        self._services[interface] = descriptor
        self._logger.debug(f"Registered service: {interface.__name__} -> {implementation.__name__}")
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T],
                        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
                        lazy: bool = True) -> None:
        """Register a factory function for a service."""
        descriptor = ServiceDescriptor(
            interface=interface,
            factory=factory,
            lifetime=lifetime,
            lazy=lazy
        )
        self._services[interface] = descriptor
        self._logger.debug(f"Registered factory for: {interface.__name__}")
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} is not registered")
        
        descriptor = self._services[interface]
        
        # Handle lazy loading
        if descriptor.lazy and descriptor.lifetime == ServiceLifetime.SINGLETON:
            # Return proxy for lazy singletons
            if interface not in self._proxies:
                self._proxies[interface] = LazyServiceProxy(self, interface)
            return self._proxies[interface]
        
        # Handle regular resolution
        return self._resolve_instance(interface, descriptor)
    
    def _resolve_instance(self, interface: Type, descriptor: ServiceDescriptor) -> Any:
        """Resolve an actual service instance."""
        # Handle singleton lifetime
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if interface not in self._singletons:
                with self._lock:
                    if interface not in self._singletons:
                        self._singletons[interface] = self._create_instance(descriptor)
            return self._singletons[interface]
        
        # Handle scoped (per-request) lifetime
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if not has_app_context():
                # Fallback to transient if no app context
                return self._create_instance(descriptor)
            
            instance_key = f'_di_scoped_{interface.__name__}'
            if hasattr(g, instance_key):
                return getattr(g, instance_key)
            
            instance = self._create_instance(descriptor)
            setattr(g, instance_key, instance)
            return instance
        
        # Handle transient lifetime
        else:
            return self._create_instance(descriptor)
    
    def _create_instance_direct(self, interface: Type) -> Any:
        """Create instance directly (used by proxy)."""
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} is not registered")
        
        descriptor = self._services[interface]
        return self._resolve_instance(interface, descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create an instance from a service descriptor."""
        try:
            if descriptor.factory:
                return descriptor.factory()
            elif descriptor.implementation:
                return descriptor.implementation()
            else:
                raise ValueError(f"No factory or implementation for {descriptor.interface}")
        except Exception as e:
            self._logger.error(f"Failed to create instance for {descriptor.interface.__name__}: {e}")
            raise
    
    def is_registered(self, interface: Type) -> bool:
        """Check if a service is registered."""
        return interface in self._services
    
    def clear_scoped_services(self) -> None:
        """Clear scoped (per-request) services."""
        if has_app_context():
            for key in list(g.__dict__.keys()):
                if key.startswith('_di_scoped_'):
                    delattr(g, key)
    
    def _setup_request_teardown(self, app) -> None:
        """Set up request teardown to clear scoped services."""
        @app.teardown_appcontext
        def clear_scoped_services(error=None):
            """Clear scoped services after each request."""
            self.clear_scoped_services()
    
    def _get_db_session(self) -> Session:
        """Get the current database session."""
        from app.extensions import db
        return db.session
    
    # Lazy import methods to avoid import-time dependencies
    def _get_security_manager_interface(self):
        """Get SecurityManager interface."""
        from app.core.security import SecurityManager
        return SecurityManager
    
    def _create_security_manager(self):
        """Create SecurityManager instance."""
        from app.core.security import SecurityManager
        return SecurityManager()
    
    def _get_user_repository_interface(self):
        """Get user repository interface."""
        from app.services.interfaces.user_repository_interface import IUserRepository
        return IUserRepository
    
    def _create_user_repository(self):
        """Create user repository instance."""
        from app.repositories.improved_user_repository import ImprovedUserRepository
        return ImprovedUserRepository(self._get_db_session())
    
    def _get_document_repository_interface(self):
        """Get document repository interface."""
        from app.repositories.interfaces.document_repository_interface import IDocumentRepository
        return IDocumentRepository
    
    def _create_document_repository(self):
        """Create document repository instance."""
        from app.repositories.document_repository import DocumentRepository
        return DocumentRepository(self._get_db_session())
    
    def _get_evaluation_repository_interface(self):
        """Get evaluation repository interface."""
        from app.repositories.interfaces.evaluation_repository_interface import IEvaluationRepository
        return IEvaluationRepository
    
    def _create_evaluation_repository(self):
        """Create evaluation repository instance."""
        from app.repositories.evaluation_repository import EvaluationRepository
        return EvaluationRepository(self._get_db_session())
    
    def _get_program_repository_interface(self):
        """Get program repository interface."""
        from app.repositories.interfaces.program_repository_interface import IProgramRepository
        return IProgramRepository
    
    def _create_program_repository(self):
        """Create program repository instance."""
        from app.repositories.program_repository import ProgramRepository
        return ProgramRepository(self._get_db_session())
    
    def _get_notification_repository_interface(self):
        """Get notification repository interface."""
        from app.repositories.interfaces.notification_repository_interface import INotificationRepository
        return INotificationRepository
    
    def _create_notification_repository(self):
        """Create notification repository instance."""
        from app.repositories.notification_repository import NotificationRepository
        return NotificationRepository(self._get_db_session())
    
    def _get_calendar_repository_interface(self):
        """Get calendar repository interface."""
        from app.repositories.interfaces.calendar_repository_interface import ICalendarRepository
        return ICalendarRepository
    
    def _create_calendar_repository(self):
        """Create calendar repository instance."""
        from app.repositories.calendar_repository import CalendarRepository
        return CalendarRepository(self._get_db_session())
    
    def _get_auth_service_interface(self):
        """Get auth service interface."""
        from app.services.interfaces.auth_service_interface import IAuthService
        return IAuthService
    
    def _create_auth_service(self):
        """Create auth service instance."""
        from app.services.improved_auth_service import ImprovedAuthService
        return ImprovedAuthService(
            user_repository=self.resolve(self._get_user_repository_interface()),
            db_session=self._get_db_session()
        )
    
    def _get_document_service_interface(self):
        """Get document service interface."""
        from app.services.interfaces.document_service_interface import IDocumentService
        return IDocumentService
    
    def _create_document_service(self):
        """Create document service instance."""
        from app.services.improved_document_service import ImprovedDocumentService
        return ImprovedDocumentService(
            document_repository=self.resolve(self._get_document_repository_interface()),
            db_session=self._get_db_session()
        )
    
    def _get_evaluation_service_interface(self):
        """Get evaluation service interface."""
        from app.services.interfaces.evaluation_service_interface import IEvaluationService
        return IEvaluationService
    
    def _create_evaluation_service(self):
        """Create evaluation service instance."""
        from app.services.improved_evaluation_service import ImprovedEvaluationService
        return ImprovedEvaluationService(
            evaluation_repository=self.resolve(self._get_evaluation_repository_interface()),
            db_session=self._get_db_session()
        )
    
    def _get_program_service_interface(self):
        """Get program service interface."""
        from app.services.interfaces.program_service_interface import IProgramService
        return IProgramService
    
    def _create_program_service(self):
        """Create program service instance."""
        from app.services.improved_program_service import ImprovedProgramService
        return ImprovedProgramService(
            program_repository=self.resolve(self._get_program_repository_interface()),
            db_session=self._get_db_session()
        )
    
    def _get_notification_service_interface(self):
        """Get notification service interface."""
        from app.services.interfaces.notification_service_interface import INotificationService
        return INotificationService
    
    def _create_notification_service(self):
        """Create notification service instance."""
        from app.services.improved_notification_service import ImprovedNotificationService
        return ImprovedNotificationService(
            notification_repository=self.resolve(self._get_notification_repository_interface()),
            db_session=self._get_db_session()
        )
    
    def _get_calendar_service_interface(self):
        """Get calendar service interface."""
        from app.services.interfaces.calendar_service_interface import ICalendarService
        return ICalendarService
    
    def _create_calendar_service(self):
        """Create calendar service instance."""
        from app.services.improved_calendar_service import ImprovedCalendarService
        return ImprovedCalendarService(
            calendar_repository=self.resolve(self._get_calendar_repository_interface()),
            db_session=self._get_db_session()
        )


# Global lazy container instance
lazy_container = LazyDIContainer()


# Helper functions for easy access
def get_service(service_type: Type[T]) -> T:
    """Get a service instance from the lazy container."""
    return lazy_container.resolve(service_type)


def get_auth_service():
    """Get the authentication service."""
    from app.services.interfaces.auth_service_interface import IAuthService
    return get_service(IAuthService)


def get_user_repository():
    """Get the user repository."""
    from app.services.interfaces.user_repository_interface import IUserRepository
    return get_service(IUserRepository)


def get_document_service():
    """Get the document service."""
    from app.services.interfaces.document_service_interface import IDocumentService
    return get_service(IDocumentService)