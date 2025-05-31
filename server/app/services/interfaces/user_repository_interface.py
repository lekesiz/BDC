"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.models import User


class IUserRepository(ABC):
    """Interface for user repository."""
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = None, offset: int = None) -> List[User]:
        """Find all users with optional pagination."""
        pass
    
    @abstractmethod
    def find_by_role(self, role: str) -> List[User]:
        """Find users by role."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user by ID."""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Count total users."""
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Save user instance."""
        pass