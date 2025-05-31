"""Improved dependency injection container."""

from typing import Dict, Any, Type, Callable, TypeVar, Optional
from abc import ABC, abstractmethod
from flask import g, current_app
from sqlalchemy.orm import Session

from app.extensions import db
from app.core.security import SecurityManager

# Repository interfaces
from app.services.interfaces.user_repository_interface import IUserRepository
from app.services.interfaces.auth_service_interface import IAuthService
from app.repositories.interfaces.document_repository_interface import IDocumentRepository
from app.repositories.interfaces.evaluation_repository_interface import IEvaluationRepository
from app.repositories.interfaces.program_repository_interface import IProgramRepository
from app.repositories.interfaces.notification_repository_interface import INotificationRepository
from app.repositories.interfaces.calendar_repository_interface import ICalendarRepository

# Service interfaces
from app.services.interfaces.document_service_interface import IDocumentService
from app.services.interfaces.evaluation_service_interface import IEvaluationService
from app.services.interfaces.program_service_interface import IProgramService
from app.services.interfaces.notification_service_interface import INotificationService
from app.services.interfaces.calendar_service_interface import ICalendarService

# Repository implementations
from app.repositories.improved_user_repository import ImprovedUserRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.program_repository import ProgramRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.calendar_repository import CalendarRepository

# Service implementations
from app.services.improved_auth_service import ImprovedAuthService
from app.services.improved_document_service import ImprovedDocumentService
from app.services.improved_evaluation_service import ImprovedEvaluationService
from app.services.improved_program_service import ImprovedProgramService
from app.services.improved_notification_service import ImprovedNotificationService
from app.services.improved_calendar_service import ImprovedCalendarService

T = TypeVar('T')


class IContainer(ABC):
    """Container interface."""
    
    @abstractmethod
    def register(self, interface: Type[T], implementation: Type[T], 
                lifetime: str = 'transient') -> None:
        """Register a service."""
        pass
    
    @abstractmethod
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service."""
        pass
    
    @abstractmethod
    def register_factory(self, interface: Type[T], factory: Callable[[], T],
                        lifetime: str = 'transient') -> None:
        """Register a factory function."""
        pass
    
    @abstractmethod
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service."""
        pass


class ServiceLifetime:
    """Service lifetime constants."""
    SINGLETON = 'singleton'
    SCOPED = 'scoped'  # Per request
    TRANSIENT = 'transient'  # New instance each time


class ServiceDescriptor:
    """Service registration descriptor."""
    
    def __init__(self, interface: Type, implementation: Optional[Type] = None,
                 factory: Optional[Callable] = None, lifetime: str = ServiceLifetime.TRANSIENT):
        self.interface = interface
        self.implementation = implementation
        self.factory = factory
        self.lifetime = lifetime


class ImprovedDIContainer(IContainer):
    """Improved dependency injection container with proper lifetime management."""
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._configure_default_services()
    
    def _configure_default_services(self):
        """Configure default service bindings."""
        # Register core services
        self.register_singleton(SecurityManager, SecurityManager)
        
        # Register repositories (scoped to request)
        self.register_factory(IUserRepository, 
                            lambda: ImprovedUserRepository(self._get_db_session()),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(IDocumentRepository,
                            lambda: DocumentRepository(self._get_db_session()),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(IEvaluationRepository,
                            lambda: EvaluationRepository(self._get_db_session()),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(IProgramRepository,
                            lambda: ProgramRepository(self._get_db_session()),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(INotificationRepository,
                            lambda: NotificationRepository(self._get_db_session()),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(ICalendarRepository,
                            lambda: CalendarRepository(self._get_db_session()),
                            ServiceLifetime.SCOPED)
        
        # Register services (scoped to request)
        self.register_factory(IAuthService,
                            lambda: ImprovedAuthService(
                                user_repository=self.resolve(IUserRepository),
                                db_session=self._get_db_session()
                            ),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(IDocumentService,
                            lambda: ImprovedDocumentService(
                                document_repository=self.resolve(IDocumentRepository),
                                db_session=self._get_db_session()
                            ),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(IEvaluationService,
                            lambda: ImprovedEvaluationService(
                                evaluation_repository=self.resolve(IEvaluationRepository),
                                db_session=self._get_db_session()
                            ),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(IProgramService,
                            lambda: ImprovedProgramService(
                                program_repository=self.resolve(IProgramRepository),
                                db_session=self._get_db_session()
                            ),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(INotificationService,
                            lambda: ImprovedNotificationService(
                                notification_repository=self.resolve(INotificationRepository),
                                db_session=self._get_db_session()
                            ),
                            ServiceLifetime.SCOPED)
        
        self.register_factory(ICalendarService,
                            lambda: ImprovedCalendarService(
                                calendar_repository=self.resolve(ICalendarRepository),
                                db_session=self._get_db_session()
                            ),
                            ServiceLifetime.SCOPED)
    
    def register(self, interface: Type[T], implementation: Type[T], 
                lifetime: str = ServiceLifetime.TRANSIENT) -> None:
        """Register a service with its implementation.
        
        Args:
            interface: Service interface
            implementation: Service implementation
            lifetime: Service lifetime
        """
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            lifetime=lifetime
        )
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service.
        
        Args:
            interface: Service interface
            implementation: Service implementation
        """
        self.register(interface, implementation, ServiceLifetime.SINGLETON)
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T],
                        lifetime: str = ServiceLifetime.TRANSIENT) -> None:
        """Register a factory function for a service.
        
        Args:
            interface: Service interface
            factory: Factory function
            lifetime: Service lifetime
        """
        self._services[interface] = ServiceDescriptor(
            interface=interface,
            factory=factory,
            lifetime=lifetime
        )
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance.
        
        Args:
            interface: Service interface to resolve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        if interface not in self._services:
            raise ValueError(f"Service {interface} is not registered")
        
        descriptor = self._services[interface]
        
        # Handle singleton lifetime
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if interface not in self._singletons:
                self._singletons[interface] = self._create_instance(descriptor)
            return self._singletons[interface]
        
        # Handle scoped (per-request) lifetime
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            instance_key = f'_di_scoped_{interface.__name__}'
            if hasattr(g, instance_key):
                return getattr(g, instance_key)
            
            instance = self._create_instance(descriptor)
            setattr(g, instance_key, instance)
            return instance
        
        # Handle transient lifetime
        else:
            return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create an instance from a service descriptor.
        
        Args:
            descriptor: Service descriptor
            
        Returns:
            Service instance
        """
        if descriptor.factory:
            return descriptor.factory()
        elif descriptor.implementation:
            return descriptor.implementation()
        else:
            raise ValueError(f"No factory or implementation for {descriptor.interface}")
    
    def _get_db_session(self) -> Session:
        """Get the current database session."""
        return db.session
    
    def clear_scoped_services(self):
        """Clear scoped (per-request) services."""
        # Clear all scoped services from Flask g object
        for key in list(g.__dict__.keys()):
            if key.startswith('_di_scoped_'):
                delattr(g, key)


# Global container instance
container = ImprovedDIContainer()


def init_improved_container(app):
    """Initialize the improved DI container with the Flask app."""
    
    @app.teardown_appcontext
    def clear_scoped_services(error=None):
        """Clear scoped services after each request."""
        container.clear_scoped_services()


# Helper functions for easy access
def get_service(service_type: Type[T]) -> T:
    """Get a service instance from the container."""
    return container.resolve(service_type)


def get_auth_service() -> IAuthService:
    """Get the authentication service."""
    return get_service(IAuthService)


def get_user_repository() -> IUserRepository:
    """Get the user repository."""
    return get_service(IUserRepository)


def get_document_service() -> IDocumentService:
    """Get the document service."""
    return get_service(IDocumentService)


def get_document_repository() -> IDocumentRepository:
    """Get the document repository."""
    return get_service(IDocumentRepository)


def get_evaluation_service() -> IEvaluationService:
    """Get the evaluation service."""
    return get_service(IEvaluationService)


def get_evaluation_repository() -> IEvaluationRepository:
    """Get the evaluation repository."""
    return get_service(IEvaluationRepository)


def get_program_service() -> IProgramService:
    """Get the program service."""
    return get_service(IProgramService)


def get_program_repository() -> IProgramRepository:
    """Get the program repository."""
    return get_service(IProgramRepository)


def get_notification_service() -> INotificationService:
    """Get the notification service."""
    return get_service(INotificationService)


def get_notification_repository() -> INotificationRepository:
    """Get the notification repository."""
    return get_service(INotificationRepository)


def get_calendar_service() -> ICalendarService:
    """Get the calendar service."""
    return get_service(ICalendarService)


def get_calendar_repository() -> ICalendarRepository:
    """Get the calendar repository."""
    return get_service(ICalendarRepository)