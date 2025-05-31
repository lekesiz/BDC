"""User repository implementation."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import User
from app.services.interfaces.user_repository_interface import IUserRepository


class UserRepository(IUserRepository):
    """Repository for user data access."""
    
    def __init__(self, db_session: Session):
        """
        Initialize user repository.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def find_all(self, limit: int = None, offset: int = None) -> List[User]:
        """Find all users with optional pagination."""
        query = self.db.query(User)
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def find_by_role(self, role: str) -> List[User]:
        """Find users by role."""
        return self.db.query(User).filter(User.role == role).all()
    
    def create(self, **kwargs) -> User:
        """Create a new user."""
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user by ID."""
        user = self.find_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.find_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.db.query(User).filter(User.email == email).count() > 0
    
    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        return self.db.query(User).filter(User.username == username).count() > 0
    
    def count(self) -> int:
        """Count total users."""
        return self.db.query(User).count()
    
    def save(self, user: User) -> User:
        """Save user instance."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user