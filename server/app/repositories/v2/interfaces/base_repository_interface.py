"""Base repository interface for all repositories."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.orm import Session

T = TypeVar('T')  # Generic type for models


class IBaseRepository(ABC, Generic[T]):
    """Base repository interface with common CRUD operations."""
    
    @abstractmethod
    def __init__(self, db_session: Session):
        """Initialize repository with database session."""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Find all entities with pagination."""
        pass
    
    @abstractmethod
    def find_by(self, **kwargs) -> List[T]:
        """Find entities by given criteria."""
        pass
    
    @abstractmethod
    def find_one_by(self, **kwargs) -> Optional[T]:
        """Find single entity by given criteria."""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, entity: T, data: Dict[str, Any]) -> T:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity: T) -> bool:
        """Delete entity."""
        pass
    
    @abstractmethod
    def count(self, **kwargs) -> int:
        """Count entities matching criteria."""
        pass
    
    @abstractmethod
    def exists(self, **kwargs) -> bool:
        """Check if entity exists matching criteria."""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity (create or update)."""
        pass
    
    @abstractmethod
    def refresh(self, entity: T) -> T:
        """Refresh entity from database."""
        pass