"""Authentication service interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.models import User


class IAuthService(ABC):
    """Authentication service interface."""
    
    @abstractmethod
    def authenticate(self, email: str, password: str, remember: bool = False) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password.
        Returns dict with user and tokens if successful, None otherwise.
        """
        pass
    
    @abstractmethod
    def register(self, user_data: Dict[str, Any]) -> User:
        """Register new user."""
        pass
    
    @abstractmethod
    def logout(self, user_id: int, access_token: str) -> bool:
        """Logout user and invalidate token."""
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token."""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[User]:
        """Verify token and return user if valid."""
        pass
    
    @abstractmethod
    def request_password_reset(self, email: str) -> bool:
        """Request password reset for user."""
        pass
    
    @abstractmethod
    def reset_password(self, email: str) -> Optional[str]:
        """Generate password reset token."""
        pass
    
    @abstractmethod
    def confirm_reset_password(self, token: str, new_password: str) -> Optional[User]:
        """Confirm password reset with token."""
        pass
    
    @abstractmethod
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password."""
        pass
    
    @abstractmethod
    def verify_email(self, token: str) -> bool:
        """Verify user email with token."""
        pass
    
    @abstractmethod
    def resend_verification_email(self, email: str) -> bool:
        """Resend email verification."""
        pass