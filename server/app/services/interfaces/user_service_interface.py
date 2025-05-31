"""Interface for User service operations."""

from abc import ABC, abstractmethod
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class IUserService(ABC):
    """Interface defining operations for User service."""
    
    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get a user by ID."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by email."""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update a user's information."""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        pass
    
    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        pass
    
    @abstractmethod
    async def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update a user's password."""
        pass