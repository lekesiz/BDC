"""Base repository implementation."""

from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.v2.interfaces.base_repository_interface import IBaseRepository

T = TypeVar('T')


class BaseRepository(IBaseRepository[T], Generic[T]):
    """Base repository with common CRUD implementations."""
    
    def __init__(self, db_session: Session, model_class: Type[T]):
        """Initialize repository with database session and model class."""
        self.db = db_session
        self.model_class = model_class
    
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        try:
            return self.db.query(self.model_class).filter_by(id=entity_id).first()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Find all entities with pagination."""
        try:
            return self.db.query(self.model_class).offset(offset).limit(limit).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def find_by(self, **kwargs) -> List[T]:
        """Find entities by given criteria."""
        try:
            query = self.db.query(self.model_class)
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
            return query.all()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def find_one_by(self, **kwargs) -> Optional[T]:
        """Find single entity by given criteria."""
        try:
            query = self.db.query(self.model_class)
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
            return query.first()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def create(self, data: Dict[str, Any]) -> T:
        """Create new entity."""
        try:
            entity = self.model_class(**data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def update(self, entity: T, data: Dict[str, Any]) -> T:
        """Update existing entity."""
        try:
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def delete(self, entity: T) -> bool:
        """Delete entity."""
        try:
            self.db.delete(entity)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def count(self, **kwargs) -> int:
        """Count entities matching criteria."""
        try:
            query = self.db.query(self.model_class)
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
            return query.count()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def exists(self, **kwargs) -> bool:
        """Check if entity exists matching criteria."""
        return self.count(**kwargs) > 0
    
    def save(self, entity: T) -> T:
        """Save entity (create or update)."""
        try:
            if not hasattr(entity, 'id') or entity.id is None:
                self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def refresh(self, entity: T) -> T:
        """Refresh entity from database."""
        try:
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e