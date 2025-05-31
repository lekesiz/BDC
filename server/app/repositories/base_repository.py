"""Base repository implementation."""

from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from app.repositories.interfaces.base_repository_interface import IBaseRepository
from app.extensions import db

T = TypeVar('T')


class BaseRepository(IBaseRepository[T]):
    """Base repository implementation."""
    
    def __init__(self, model_class: Type[T], db_session: Optional[Session] = None):
        """Initialize repository.
        
        Args:
            model_class: The SQLAlchemy model class
            db_session: Database session (optional, defaults to db.session)
        """
        self.model_class = model_class
        self.db_session = db_session or db.session
    
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        return self.db_session.query(self.model_class).get(entity_id)
    
    def find_all(self, filters: Optional[Dict[str, Any]] = None, 
                page: int = 1, per_page: int = 10) -> tuple[List[T], int]:
        """Find all entities with optional filtering and pagination."""
        query = self.db_session.query(self.model_class)
        
        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if filters and 'sort_by' in filters:
            query = self._apply_sorting(query, filters)
        
        # Apply pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        return query.all(), total
    
    def create(self, entity_data: Dict[str, Any]) -> T:
        """Create a new entity."""
        entity = self.model_class(**entity_data)
        self.db_session.add(entity)
        self.db_session.flush()  # Get ID without committing
        return entity
    
    def update(self, entity_id: int, entity_data: Dict[str, Any]) -> Optional[T]:
        """Update an existing entity."""
        entity = self.find_by_id(entity_id)
        if not entity:
            return None
        
        for key, value in entity_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        self.db_session.flush()
        return entity
    
    def delete(self, entity_id: int) -> bool:
        """Delete an entity."""
        entity = self.find_by_id(entity_id)
        if not entity:
            return False
        
        self.db_session.delete(entity)
        self.db_session.flush()
        return True
    
    def save(self, entity: T) -> T:
        """Save entity changes."""
        self.db_session.add(entity)
        self.db_session.flush()
        return entity
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        query = self.db_session.query(self.model_class)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        return query.count()
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query."""
        conditions = []
        
        for key, value in filters.items():
            if key in ['sort_by', 'sort_dir', 'page', 'per_page']:
                continue  # Skip pagination and sorting parameters
            
            if hasattr(self.model_class, key):
                if isinstance(value, list):
                    conditions.append(getattr(self.model_class, key).in_(value))
                elif isinstance(value, str) and value.startswith('%') and value.endswith('%'):
                    conditions.append(getattr(self.model_class, key).like(value))
                else:
                    conditions.append(getattr(self.model_class, key) == value)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query
    
    def _apply_sorting(self, query, filters: Dict[str, Any]):
        """Apply sorting to query."""
        sort_by = filters.get('sort_by')
        sort_dir = filters.get('sort_dir', 'asc')
        
        if sort_by and hasattr(self.model_class, sort_by):
            column = getattr(self.model_class, sort_by)
            if sort_dir.lower() == 'desc':
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        
        return query