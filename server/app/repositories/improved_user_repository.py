"""Improved user repository implementation."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.services.interfaces.user_repository_interface import IUserRepository
from app.models import User
from app.extensions import db


class ImprovedUserRepository(BaseRepository[User], IUserRepository):
    """Improved user repository implementation."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize user repository."""
        super().__init__(User, db_session)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return self.db_session.query(User).filter_by(email=email).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        return self.db_session.query(User).filter_by(username=username).first()
    
    def find_all(self, limit: int = None, offset: int = None) -> List[User]:
        """Find all users with optional pagination."""
        query = self.db_session.query(User)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def find_by_role(self, role: str) -> List[User]:
        """Find users by role."""
        return self.db_session.query(User).filter_by(role=role).all()
    
    def find_by_tenant(self, tenant_id: int) -> List[User]:
        """Find users by tenant."""
        return self.db_session.query(User).filter_by(tenant_id=tenant_id).all()
    
    def find_all_active(self) -> List[User]:
        """Find all active users."""
        return self.db_session.query(User).filter_by(is_active=True).all()
    
    def verify_credentials(self, email: str, password: str) -> Optional[User]:
        """Verify user credentials."""
        user = self.find_by_email(email)
        if user and user.verify_password(password) and user.is_active:
            return user
        return None
    
    def create(self, **kwargs) -> User:
        """Create a new user."""
        user = User(**kwargs)
        self.db_session.add(user)
        self.db_session.flush()
        return user
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user by ID."""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db_session.flush()
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.find_by_id(user_id)
        if not user:
            return False
        
        self.db_session.delete(user)
        self.db_session.flush()
        return True
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.db_session.query(User).filter_by(email=email).first() is not None
    
    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        return self.db_session.query(User).filter_by(username=username).first() is not None
    
    def count(self) -> int:
        """Count total users."""
        return self.db_session.query(User).count()
    
    def save(self, user: User) -> User:
        """Save user instance."""
        self.db_session.add(user)
        self.db_session.flush()
        return user