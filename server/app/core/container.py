"""Dependency injection container configuration."""
from typing import Dict, Any, Type, Callable
from flask import g, current_app
from sqlalchemy.orm import Session

from app.extensions import db
from app.core.security import SecurityManager

# Repository imports
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.repositories.v2.interfaces.beneficiary_repository_interface import IBeneficiaryRepository
from app.repositories.v2.user_repository import UserRepository
from app.repositories.v2.beneficiary_repository import BeneficiaryRepository

# Service imports
from app.services.v2.interfaces.auth_service_interface import IAuthService
from app.services.v2.interfaces.beneficiary_service_interface import IBeneficiaryService
from app.services.v2.interfaces.user_service_interface import IUserService
from app.services.v2.auth_service import AuthServiceV2
from app.services.v2.beneficiary_service import BeneficiaryServiceV2
from app.services.v2.user_service import UserServiceV2


class DIContainer:
    """Dependency injection container."""
    
    def __init__(self):
        """Initialize the container."""
        self._services: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._configure()
    
    def _configure(self):
        """Configure service bindings."""
        # Security
        self.bind_singleton(SecurityManager, lambda: SecurityManager())
        
        # Repositories (per-request scope)
        self.bind(IUserRepository, lambda: UserRepository(self.get_db_session()))
        self.bind(IBeneficiaryRepository, lambda: BeneficiaryRepository(self.get_db_session()))
        
        # Services (per-request scope)
        self.bind(IAuthService, lambda: AuthServiceV2(
            user_repository=self.get(IUserRepository),
            security_manager=self.get(SecurityManager),
            db_session=self.get_db_session()
        ))
        
        self.bind(IBeneficiaryService, lambda: BeneficiaryServiceV2(
            beneficiary_repository=self.get(IBeneficiaryRepository),
            db_session=self.get_db_session()
        ))
        
        self.bind(IUserService, lambda: UserServiceV2(
            user_repository=self.get(IUserRepository),
            security_manager=self.get(SecurityManager),
            db_session=self.get_db_session()
        ))
    
    def bind(self, interface: Type, factory: Callable):
        """Bind an interface to a factory function."""
        self._services[interface] = factory
    
    def bind_singleton(self, interface: Type, factory: Callable):
        """Bind an interface to a singleton factory."""
        def singleton_factory():
            if interface not in self._singletons:
                self._singletons[interface] = factory()
            return self._singletons[interface]
        
        self._services[interface] = singleton_factory
    
    def get(self, interface: Type) -> Any:
        """Get an instance of the requested interface."""
        if interface not in self._services:
            raise ValueError(f"No binding found for {interface}")
        
        # Check if instance exists in Flask g object (request scope)
        instance_key = f'_di_{interface.__name__}'
        if hasattr(g, instance_key):
            return getattr(g, instance_key)
        
        # Create new instance
        instance = self._services[interface]()
        
        # Store in Flask g for request scope
        setattr(g, instance_key, instance)
        
        return instance
    
    def get_db_session(self) -> Session:
        """Get the current database session."""
        return db.session
    
    def clear_request_scope(self):
        """Clear request-scoped instances."""
        # This is called at the end of each request
        for key in list(g.__dict__.keys()):
            if key.startswith('_di_'):
                delattr(g, key)


# Global container instance
container = DIContainer()


def init_app(app):
    """Initialize the DI container with the Flask app."""
    @app.teardown_appcontext
    def clear_request_scope(error=None):
        """Clear request-scoped instances after each request."""
        container.clear_request_scope()


# Helper functions for easy access
def get_service(service_type: Type) -> Any:
    """Get a service instance from the container."""
    return container.get(service_type)


def get_auth_service() -> IAuthService:
    """Get the authentication service."""
    return get_service(IAuthService)


def get_beneficiary_service() -> IBeneficiaryService:
    """Get the beneficiary service."""
    return get_service(IBeneficiaryService)


def get_user_service() -> IUserService:
    """Get the user service."""
    return get_service(IUserService)