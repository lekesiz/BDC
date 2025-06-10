"""Base service interface and implementation for standardized service layer."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic, List
from datetime import datetime
from flask import current_app
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.utils.logger import get_logger
from app.utils.cache import cache, generate_cache_key


T = TypeVar('T')  # Generic type for entity
R = TypeVar('R')  # Generic type for repository


class IService(ABC, Generic[T]):
    """Base interface for all services."""
    
    @abstractmethod
    def get_repository(self) -> Any:
        """Get the repository instance for this service."""
        pass
    
    @abstractmethod
    def get_logger(self) -> Any:
        """Get logger instance for this service."""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate data before processing.
        
        Args:
            data: Data to validate
            context: Validation context (create, update, etc.)
            
        Returns:
            Validated data
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    @abstractmethod
    def before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before entity creation."""
        pass
    
    @abstractmethod
    def after_create(self, entity: T) -> T:
        """Hook called after entity creation."""
        pass
    
    @abstractmethod
    def before_update(self, entity: T, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before entity update."""
        pass
    
    @abstractmethod
    def after_update(self, entity: T) -> T:
        """Hook called after entity update."""
        pass
    
    @abstractmethod
    def before_delete(self, entity: T) -> None:
        """Hook called before entity deletion."""
        pass
    
    @abstractmethod
    def after_delete(self, entity_id: Any) -> None:
        """Hook called after entity deletion."""
        pass


class BaseService(IService[T], Generic[T, R]):
    """
    Base implementation for all services with common functionality.
    
    This class provides:
    - Dependency injection support
    - Repository pattern integration
    - Caching capabilities
    - Logging
    - Transaction management
    - Lifecycle hooks
    - Error handling
    """
    
    def __init__(self, 
                 repository: Optional[R] = None,
                 db_session: Optional[Session] = None,
                 cache_enabled: bool = True,
                 cache_timeout: int = 300):
        """
        Initialize base service.
        
        Args:
            repository: Repository instance
            db_session: Database session
            cache_enabled: Whether to enable caching
            cache_timeout: Cache timeout in seconds
        """
        self._repository = repository
        self._db_session = db_session
        self._cache_enabled = cache_enabled
        self._cache_timeout = cache_timeout
        self._logger = None
        self._service_name = self.__class__.__name__
    
    @property
    def repository(self) -> R:
        """Get repository instance, creating if necessary."""
        if not self._repository:
            self._repository = self._create_repository()
        return self._repository
    
    @property
    def db_session(self) -> Session:
        """Get database session."""
        if self._db_session:
            return self._db_session
        return db.session
    
    @property
    def logger(self):
        """Get logger instance."""
        if not self._logger:
            self._logger = get_logger(self._service_name)
        return self._logger
    
    def get_repository(self) -> R:
        """Get the repository instance for this service."""
        return self.repository
    
    def get_logger(self):
        """Get logger instance for this service."""
        return self.logger
    
    def _create_repository(self) -> R:
        """
        Create repository instance. Override in subclasses.
        
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _create_repository")
    
    def validate(self, data: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate data before processing.
        
        Default implementation - override in subclasses for specific validation.
        
        Args:
            data: Data to validate
            context: Validation context
            
        Returns:
            Validated data
        """
        return data
    
    def before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before entity creation."""
        return data
    
    def after_create(self, entity: T) -> T:
        """Hook called after entity creation."""
        self._clear_cache()
        return entity
    
    def before_update(self, entity: T, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before entity update."""
        return data
    
    def after_update(self, entity: T) -> T:
        """Hook called after entity update."""
        self._clear_cache()
        self._clear_entity_cache(entity)
        return entity
    
    def before_delete(self, entity: T) -> None:
        """Hook called before entity deletion."""
        pass
    
    def after_delete(self, entity_id: Any) -> None:
        """Hook called after entity deletion."""
        self._clear_cache()
        self._clear_entity_cache_by_id(entity_id)
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.
        
        Args:
            data: Entity data
            
        Returns:
            Created entity
            
        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Validate data
            validated_data = self.validate(data, context='create')
            
            # Before create hook
            processed_data = self.before_create(validated_data)
            
            # Create entity
            entity = self.repository.create(processed_data)
            
            # After create hook
            entity = self.after_create(entity)
            
            self.logger.info(f"Created {self._service_name} entity: {entity.id if hasattr(entity, 'id') else entity}")
            
            return entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in {self._service_name}.create: {str(e)}")
            self.db_session.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Error in {self._service_name}.create: {str(e)}")
            raise
    
    def get_by_id(self, entity_id: Any, use_cache: bool = True) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            use_cache: Whether to use cache
            
        Returns:
            Entity or None if not found
        """
        if self._cache_enabled and use_cache:
            cache_key = self._get_cache_key('id', entity_id)
            cached = cache.get(cache_key)
            if cached:
                self.logger.debug(f"Cache hit for {self._service_name} ID: {entity_id}")
                return cached
        
        entity = self.repository.find_by_id(entity_id)
        
        if entity and self._cache_enabled and use_cache:
            cache.set(cache_key, entity, timeout=self._cache_timeout)
        
        return entity
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None, 
                pagination: Optional[Dict[str, int]] = None) -> List[T]:
        """
        Get all entities with optional filtering and pagination.
        
        Args:
            filters: Filter criteria
            pagination: Pagination params (page, per_page)
            
        Returns:
            List of entities
        """
        return self.repository.find_all(filters=filters, pagination=pagination)
    
    def update(self, entity_id: Any, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            entity_id: Entity ID
            data: Update data
            
        Returns:
            Updated entity or None if not found
            
        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            entity = self.get_by_id(entity_id, use_cache=False)
            if not entity:
                return None
            
            # Validate data
            validated_data = self.validate(data, context='update')
            
            # Before update hook
            processed_data = self.before_update(entity, validated_data)
            
            # Update entity
            updated_entity = self.repository.update(entity, processed_data)
            
            # After update hook
            updated_entity = self.after_update(updated_entity)
            
            self.logger.info(f"Updated {self._service_name} entity: {entity_id}")
            
            return updated_entity
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in {self._service_name}.update: {str(e)}")
            self.db_session.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Error in {self._service_name}.update: {str(e)}")
            raise
    
    def delete(self, entity_id: Any) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            entity = self.get_by_id(entity_id, use_cache=False)
            if not entity:
                return False
            
            # Before delete hook
            self.before_delete(entity)
            
            # Delete entity
            self.repository.delete(entity)
            
            # After delete hook
            self.after_delete(entity_id)
            
            self.logger.info(f"Deleted {self._service_name} entity: {entity_id}")
            
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in {self._service_name}.delete: {str(e)}")
            self.db_session.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Error in {self._service_name}.delete: {str(e)}")
            raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.
        
        Args:
            filters: Filter criteria
            
        Returns:
            Entity count
        """
        return self.repository.count(filters=filters)
    
    def exists(self, entity_id: Any) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists(entity_id)
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key for this service."""
        return generate_cache_key(self._service_name, *args)
    
    def _clear_cache(self):
        """Clear all cache for this service."""
        if self._cache_enabled:
            # Implementation depends on cache backend
            # This is a simplified version
            pattern = f"{self._service_name}:*"
            self.logger.debug(f"Clearing cache for pattern: {pattern}")
    
    def _clear_entity_cache(self, entity: T):
        """Clear cache for specific entity."""
        if self._cache_enabled and hasattr(entity, 'id'):
            cache_key = self._get_cache_key('id', entity.id)
            cache.delete(cache_key)
    
    def _clear_entity_cache_by_id(self, entity_id: Any):
        """Clear cache for specific entity by ID."""
        if self._cache_enabled:
            cache_key = self._get_cache_key('id', entity_id)
            cache.delete(cache_key)
    
    def begin_transaction(self):
        """Begin a new transaction."""
        return self.db_session.begin()
    
    def commit(self):
        """Commit current transaction."""
        self.db_session.commit()
    
    def rollback(self):
        """Rollback current transaction."""
        self.db_session.rollback()
    
    def flush(self):
        """Flush pending changes without committing."""
        self.db_session.flush()