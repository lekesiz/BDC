"""User repository interface."""

from abc import abstractmethod
from typing import Optional, List
from datetime import datetime
from app.repositories.v2.interfaces.base_repository_interface import IBaseRepository
from app.models import User


class IUserRepository(IBaseRepository[User]):
    """User repository interface with user-specific operations."""
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        pass
    
    @abstractmethod
    def find_by_tenant(self, tenant_id: int, limit: int = 100, offset: int = 0) -> List[User]:
        """Find all users for a specific tenant."""
        pass
    
    @abstractmethod
    def find_by_role(self, role: str, tenant_id: Optional[int] = None) -> List[User]:
        """Find users by role, optionally filtered by tenant."""
        pass
    
    @abstractmethod
    def find_active_users(self, tenant_id: Optional[int] = None) -> List[User]:
        """Find all active users."""
        pass
    
    @abstractmethod
    def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp."""
        pass
    
    @abstractmethod
    def update_password(self, user: User, password_hash: str) -> User:
        """Update user's password hash."""
        pass
    
    @abstractmethod
    def deactivate(self, user: User) -> User:
        """Deactivate user account."""
        pass
    
    @abstractmethod
    def activate(self, user: User) -> User:
        """Activate user account."""
        pass
    
    @abstractmethod
    def find_by_reset_token(self, token: str) -> Optional[User]:
        """Find user by password reset token."""
        pass
    
    @abstractmethod
    def search(self, query: str, tenant_id: Optional[int] = None, 
               limit: int = 100, offset: int = 0) -> List[User]:
        """Search users by name or email."""
        pass