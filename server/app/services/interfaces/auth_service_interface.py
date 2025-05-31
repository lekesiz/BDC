"""Authentication service interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from app.models import User


class IAuthService(ABC):
    """Interface for authentication service."""
    
    @abstractmethod
    def login(self, email: str, password: str) -> Optional[Dict[str, any]]:
        """
        Authenticate user and return tokens.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dictionary with access_token, refresh_token, and expires_in
            or None if authentication fails
        """
        pass
    
    @abstractmethod
    def register(self, email: str, password: str, **kwargs) -> User:
        """
        Register a new user.
        
        Args:
            email: User's email
            password: User's password
            **kwargs: Additional user attributes
            
        Returns:
            Newly created User instance
            
        Raises:
            ValueError: If email already exists
        """
        pass
    
    @abstractmethod
    def logout(self, user_id: int, token: str) -> bool:
        """
        Logout user and invalidate token.
        
        Args:
            user_id: ID of the user
            token: JWT token to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, any]]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dictionary with new access_token and expires_in
            or None if refresh token is invalid
        """
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email
            
        Returns:
            User instance or None if not found
        """
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User instance or None if not found
        """
        pass
    
    @abstractmethod
    def update_last_login(self, user: User) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user: User instance to update
        """
        pass
    
    @abstractmethod
    def verify_password(self, user: User, password: str) -> bool:
        """
        Verify user's password.
        
        Args:
            user: User instance
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        pass
    
    @abstractmethod
    def request_password_reset(self, email: str) -> bool:
        """
        Request password reset for user.
        
        Args:
            email: User's email
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def reset_password(self, token: str, password: str) -> bool:
        """
        Reset user password using reset token.
        
        Args:
            token: Password reset token
            password: New password
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User's ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        pass