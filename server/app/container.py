"""Dependency injection container."""

from typing import Any, Callable, Dict, Optional
from flask import Flask, g
from sqlalchemy.orm import Session

from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.document_repository import DocumentRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.services.document_service import DocumentService
from app.services.beneficiary_service import BeneficiaryService
from app.services.interfaces.auth_service_interface import IAuthService
from app.services.interfaces.user_repository_interface import IUserRepository
from app.services.interfaces.beneficiary_repository_interface import IBeneficiaryRepository
from app.services.interfaces.user_service_interface import IUserService
from app.services.interfaces.notification_service_interface import INotificationService
from app.services.interfaces.document_service_interface import IDocumentService
from app.services.interfaces.document_repository_interface import IDocumentRepository
from app.repositories.interfaces.notification_repository_interface import INotificationRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.services.appointment_service import AppointmentService
from app.services.interfaces.appointment_service_interface import IAppointmentService
from app.services.interfaces.appointment_repository_interface import IAppointmentRepository


class DIContainer:
    """Dependency injection container for managing service instances."""
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[str, tuple[Callable, bool]] = {}
        self._singletons: Dict[str, Any] = {}
        self._setup_services()
    
    def _setup_services(self):
        """Set up service registrations."""
        # Register repositories
        self.register('db_session', lambda: db.session, singleton=False)
        self.register('user_repository', self._create_user_repository, singleton=False)
        self.register('beneficiary_repository', self._create_beneficiary_repository, singleton=False)
        self.register('notification_repository', self._create_notification_repository, singleton=False)
        self.register('document_repository', self._create_document_repository, singleton=False)
        self.register('appointment_repository', self._create_appointment_repository, singleton=False)
        
        # Register services
        self.register('auth_service', self._create_auth_service, singleton=False)
        self.register('user_service', self._create_user_service, singleton=False)
        self.register('beneficiary_service', self._create_beneficiary_service, singleton=False)
        self.register('notification_service', self._create_notification_service, singleton=False)
        self.register('document_service', self._create_document_service, singleton=False)
        self.register('appointment_service', self._create_appointment_service, singleton=False)
    
    def register(self, name: str, factory: Callable, singleton: bool = False):
        """
        Register a service with the container.
        
        Args:
            name: Service name
            factory: Factory function to create the service
            singleton: Whether to create only one instance
        """
        self._services[name] = (factory, singleton)
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' is not registered")
        
        factory, is_singleton = self._services[name]
        
        if is_singleton:
            if name not in self._singletons:
                self._singletons[name] = factory()
            return self._singletons[name]
        
        return factory()
    
    def _create_user_repository(self) -> IUserRepository:
        """Create user repository instance."""
        session = self.resolve('db_session')
        return UserRepository(session)
    
    def _create_beneficiary_repository(self) -> IBeneficiaryRepository:
        """Create beneficiary repository instance."""
        session = self.resolve('db_session')
        return BeneficiaryRepository(session)
    
    def _create_notification_repository(self) -> INotificationRepository:
        """Create notification repository instance."""
        session = self.resolve('db_session')
        return NotificationRepository(session)
    
    def _create_document_repository(self) -> IDocumentRepository:
        """Create document repository instance."""
        session = self.resolve('db_session')
        return DocumentRepository(session)
    
    def _create_appointment_repository(self) -> IAppointmentRepository:
        """Create appointment repository instance."""
        session = self.resolve('db_session')
        return AppointmentRepository(session)
    
    def _create_auth_service(self) -> IAuthService:
        """Create auth service instance."""
        user_repository = self.resolve('user_repository')
        return AuthService(user_repository)
    
    def _create_user_service(self) -> IUserService:
        """Create user service instance."""
        user_repository = self.resolve('user_repository')
        beneficiary_repository = self.resolve('beneficiary_repository')
        from flask import current_app
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        return UserService(user_repository, beneficiary_repository, upload_folder)
    
    def _create_notification_service(self) -> INotificationService:
        """Create notification service instance."""
        notification_repository = self.resolve('notification_repository')
        return NotificationService(notification_repository)
    
    def _create_document_service(self) -> IDocumentService:
        """Create document service instance."""
        document_repository = self.resolve('document_repository')
        user_repository = self.resolve('user_repository')
        beneficiary_repository = self.resolve('beneficiary_repository')
        notification_service = self.resolve('notification_service')
        return DocumentService(
            document_repository,
            user_repository,
            beneficiary_repository,
            notification_service
        )
    
    def _create_beneficiary_service(self):
        """Create beneficiary service instance."""
        beneficiary_repository = self.resolve('beneficiary_repository')
        user_repository = self.resolve('user_repository')
        return BeneficiaryService(beneficiary_repository, user_repository)
    
    def _create_appointment_service(self) -> IAppointmentService:
        """Create appointment service instance."""
        appointment_repository = self.resolve('appointment_repository')
        return AppointmentService(appointment_repository)
    
    def clear_singletons(self):
        """Clear all singleton instances."""
        self._singletons.clear()


# Global container instance
container = DIContainer()


def get_container() -> DIContainer:
    """Get the global container instance."""
    return container


def inject(service_name: str):
    """
    Decorator to inject dependencies into Flask route handlers.
    
    Args:
        service_name: Name of the service to inject
        
    Example:
        @app.route('/login')
        @inject('auth_service')
        def login(auth_service: IAuthService):
            return auth_service.login(email, password)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            service = container.resolve(service_name)
            return func(*args, service=service, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


def setup_request_container(app: Flask):
    """
    Set up per-request container handling.
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        """Create request-scoped services."""
        g.container = DIContainer()
    
    @app.teardown_request
    def teardown_request(exception=None):
        """Clean up request-scoped services."""
        if hasattr(g, 'container'):
            g.container.clear_singletons()