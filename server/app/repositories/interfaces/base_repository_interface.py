"""Base repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar('T')


class IBaseRepository(ABC, Generic[T]):
    """Base repository interface."""
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self, filters: Optional[Dict[str, Any]] = None, 
                page: int = 1, per_page: int = 10) -> tuple[List[T], int]:
        """Find all entities with optional filtering and pagination."""
        pass
    
    @abstractmethod
    def create(self, entity_data: Dict[str, Any]) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def update(self, entity_id: int, entity_data: Dict[str, Any]) -> Optional[T]:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete an entity."""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity changes."""
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        pass