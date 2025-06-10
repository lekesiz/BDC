"""
Integration registry for managing and discovering integrations.
"""

from typing import Dict, Type, List, Any, Optional
import logging

from .base import BaseIntegration, IntegrationConfig

logger = logging.getLogger(__name__)


class IntegrationRegistry:
    """Registry for managing integration classes and instances."""
    
    def __init__(self):
        self._integration_classes: Dict[str, Type[BaseIntegration]] = {}
        self._instances: Dict[str, BaseIntegration] = {}
    
    def register_integration_class(self, name: str, integration_class: Type[BaseIntegration]) -> None:
        """Register an integration class."""
        if not issubclass(integration_class, BaseIntegration):
            raise ValueError(f"Integration class must inherit from BaseIntegration")
        
        self._integration_classes[name] = integration_class
        logger.info(f"Registered integration class: {name}")
    
    def get_integration_class(self, name: str) -> Optional[Type[BaseIntegration]]:
        """Get an integration class by name."""
        return self._integration_classes.get(name)
    
    def list_integration_classes(self) -> List[str]:
        """List all registered integration classes."""
        return list(self._integration_classes.keys())
    
    def create_integration(self, name: str, config: IntegrationConfig) -> BaseIntegration:
        """Create an integration instance."""
        integration_class = self.get_integration_class(name)
        if not integration_class:
            raise ValueError(f"No integration class registered for: {name}")
        
        instance = integration_class(config)
        self._instances[name] = instance
        logger.info(f"Created integration instance: {name}")
        return instance
    
    def get_integration_instance(self, name: str) -> Optional[BaseIntegration]:
        """Get an integration instance by name."""
        return self._instances.get(name)
    
    def list_integration_instances(self) -> List[str]:
        """List all created integration instances."""
        return list(self._instances.keys())
    
    def remove_integration_instance(self, name: str) -> bool:
        """Remove an integration instance."""
        if name in self._instances:
            del self._instances[name]
            logger.info(f"Removed integration instance: {name}")
            return True
        return False
    
    def get_integrations_by_type(self, integration_type: str) -> List[BaseIntegration]:
        """Get all integration instances of a specific type."""
        return [
            instance for instance in self._instances.values()
            if instance.integration_type == integration_type
        ]
    
    def get_integration_info(self) -> Dict[str, Any]:
        """Get information about all registrations."""
        return {
            'registered_classes': list(self._integration_classes.keys()),
            'active_instances': list(self._instances.keys()),
            'instance_details': {
                name: {
                    'type': instance.integration_type,
                    'provider': instance.provider_name,
                    'status': instance.status.value if hasattr(instance, 'status') else 'unknown'
                }
                for name, instance in self._instances.items()
            }
        }


# Global registry instance
integration_registry = IntegrationRegistry()


def register_integration(name: str):
    """Decorator to register an integration class."""
    def decorator(cls: Type[BaseIntegration]):
        integration_registry.register_integration_class(name, cls)
        return cls
    return decorator