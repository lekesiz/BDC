"""Service factory for creating service instances with proper dependency injection."""

from typing import Any, Dict, Optional, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.extensions import db
from app.utils.logger import get_logger
from .service_container import get_service_container, get_request_container


T = TypeVar('T')  # Service type


class IServiceFactory(ABC, Generic[T]):
    """Interface for service factories."""
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create a service instance."""
        pass
    
    @abstractmethod
    def create_with_dependencies(self, dependencies: Dict[str, Any]) -> T:
        """Create a service instance with explicit dependencies."""
        pass


class ServiceFactory(IServiceFactory[T]):
    """
    Factory for creating service instances with dependency injection.
    
    This factory provides:
    - Automatic dependency resolution
    - Service configuration
    - Instance caching
    - Lifecycle management
    """
    
    def __init__(self, 
                 service_class: Type[T],
                 service_name: Optional[str] = None,
                 use_request_scope: bool = True):
        """
        Initialize service factory.
        
        Args:
            service_class: Service class to instantiate
            service_name: Service name for container registration
            use_request_scope: Whether to use request-scoped container
        """
        self.service_class = service_class
        self.service_name = service_name or service_class.__name__
        self.use_request_scope = use_request_scope
        self.logger = get_logger(f'ServiceFactory[{self.service_name}]')
    
    @property
    def container(self):
        """Get appropriate container based on scope."""
        if self.use_request_scope:
            try:
                return get_request_container()
            except RuntimeError:
                # Outside request context
                return get_service_container()
        return get_service_container()
    
    def create(self, **kwargs) -> T:
        """
        Create a service instance.
        
        Args:
            **kwargs: Additional arguments for service construction
            
        Returns:
            Service instance
        """
        # Check if service is registered in container
        if self.container.has(self.service_name):
            self.logger.debug(f"Creating {self.service_name} from container")
            return self.container.resolve(self.service_name)
        
        # Create with automatic dependency resolution
        dependencies = self._resolve_dependencies()
        return self.create_with_dependencies(dependencies, **kwargs)
    
    def create_with_dependencies(self, 
                                dependencies: Dict[str, Any],
                                **kwargs) -> T:
        """
        Create a service instance with explicit dependencies.
        
        Args:
            dependencies: Dependency instances
            **kwargs: Additional arguments
            
        Returns:
            Service instance
        """
        all_args = {**dependencies, **kwargs}
        self.logger.debug(f"Creating {self.service_name} with dependencies: {list(all_args.keys())}")
        
        try:
            instance = self.service_class(**all_args)
            self.logger.info(f"Created {self.service_name} instance")
            return instance
        except Exception as e:
            self.logger.error(f"Failed to create {self.service_name}: {str(e)}")
            raise
    
    def _resolve_dependencies(self) -> Dict[str, Any]:
        """
        Resolve dependencies for the service.
        
        Returns:
            Dictionary of dependency instances
        """
        dependencies = {}
        
        # Get constructor parameters
        import inspect
        sig = inspect.signature(self.service_class.__init__)
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Skip if has default value
            if param.default != inspect.Parameter.empty:
                continue
            
            # Try to resolve from container
            if self.container.has(param_name):
                dependencies[param_name] = self.container.resolve(param_name)
                self.logger.debug(f"Resolved dependency '{param_name}' from container")
            
            # Special handling for common dependencies
            elif param_name == 'db_session':
                dependencies['db_session'] = db.session
                self.logger.debug("Resolved db_session from default")
            
            # Try to resolve by type annotation
            elif param.annotation != inspect.Parameter.empty:
                type_name = self._get_type_name(param.annotation)
                if self.container.has(type_name):
                    dependencies[param_name] = self.container.resolve(type_name)
                    self.logger.debug(f"Resolved dependency '{param_name}' by type '{type_name}'")
        
        return dependencies
    
    def _get_type_name(self, annotation) -> str:
        """Get type name from annotation."""
        if hasattr(annotation, '__name__'):
            return annotation.__name__
        return str(annotation)
    
    def register(self, singleton: bool = False, **metadata) -> None:
        """
        Register this factory's service in the container.
        
        Args:
            singleton: Whether service should be singleton
            **metadata: Additional metadata
        """
        self.container.register(
            self.service_name,
            lambda: self.create(),
            singleton=singleton,
            metadata=metadata,
            interface=getattr(self.service_class, '__interface__', None)
        )
        self.logger.info(f"Registered {self.service_name} in container")


class ServiceFactoryRegistry:
    """Registry for managing service factories."""
    
    def __init__(self):
        """Initialize factory registry."""
        self._factories: Dict[str, ServiceFactory] = {}
        self.logger = get_logger('ServiceFactoryRegistry')
    
    def register_factory(self, name: str, factory: ServiceFactory) -> None:
        """Register a service factory."""
        self._factories[name] = factory
        self.logger.debug(f"Registered factory: {name}")
    
    def get_factory(self, name: str) -> Optional[ServiceFactory]:
        """Get a service factory by name."""
        return self._factories.get(name)
    
    def create_service(self, name: str, **kwargs) -> Any:
        """Create a service using its factory."""
        factory = self.get_factory(name)
        if not factory:
            raise ValueError(f"No factory registered for service: {name}")
        return factory.create(**kwargs)
    
    def list_factories(self) -> List[str]:
        """List all registered factory names."""
        return list(self._factories.keys())


# Global factory registry
_factory_registry = ServiceFactoryRegistry()


def get_factory_registry() -> ServiceFactoryRegistry:
    """Get the global factory registry."""
    return _factory_registry


# Convenience functions
def create_service_factory(service_class: Type[T], 
                          service_name: Optional[str] = None,
                          **kwargs) -> ServiceFactory[T]:
    """
    Create and optionally register a service factory.
    
    Args:
        service_class: Service class
        service_name: Optional service name
        **kwargs: Additional factory configuration
        
    Returns:
        ServiceFactory instance
    """
    factory = ServiceFactory(service_class, service_name, **kwargs)
    
    # Auto-register if name provided
    if service_name:
        _factory_registry.register_factory(service_name, factory)
    
    return factory


def get_service(service_name: str, **kwargs) -> Any:
    """
    Get a service instance by name.
    
    First tries container resolution, then factory creation.
    
    Args:
        service_name: Service name
        **kwargs: Additional arguments
        
    Returns:
        Service instance
    """
    # Try container first
    container = get_request_container()
    if container.has(service_name):
        return container.resolve(service_name)
    
    # Try factory
    return _factory_registry.create_service(service_name, **kwargs)