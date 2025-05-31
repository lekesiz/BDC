"""Refactored authentication service with dependency injection."""

from datetime import datetime, timezone
from typing import Optional, Dict
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash

from app.models import User, TokenBlocklist
from app.services.interfaces.auth_service_interface import IAuthService
from app.services.interfaces.user_repository_interface import IUserRepository
from app.extensions import db


class AuthServiceRefactored(IAuthService):
    """Refactored authentication service implementation."""
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize auth service with dependencies.
        
        Args:
            user_repository: User repository for data access
        """
        self.user_repository = user_repository
    
    def login(self, email: str, password: str) -> Optional[Dict[str, any]]:
        """Authenticate user and return tokens."""
        user = self.user_repository.find_by_email(email)
        
        if not user or not user.verify_password(password):
            return None
        
        # Update last login
        self.update_last_login(user)
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600,  # 1 hour
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }
    
    def register(self, email: str, password: str, **kwargs) -> User:
        """Register a new user."""
        # Check if user already exists
        if self.user_repository.exists_by_email(email):
            raise ValueError("Email already registered")
        
        # Create user
        user_data = {
            'email': email,
            'password_hash': generate_password_hash(password),
            **kwargs
        }
        
        return self.user_repository.create(**user_data)
    
    def logout(self, user_id: int, token: str) -> bool:
        """Logout user and invalidate token."""
        try:
            # Add token to blocklist
            blocked_token = TokenBlocklist(
                jti=token,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(blocked_token)
            db.session.commit()
            return True
        except Exception:
            return False
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, any]]:
        """Refresh access token using refresh token."""
        # This would need JWT decoding logic
        # For now, return None as placeholder
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.user_repository.find_by_email(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repository.find_by_id(user_id)
    
    def update_last_login(self, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = datetime.utcnow()
        self.user_repository.save(user)
    
    def verify_password(self, user: User, password: str) -> bool:
        """Verify user's password."""
        return user.verify_password(password)
    
    @staticmethod
    def generate_tokens(user: User) -> Dict[str, any]:
        """Generate access and refresh tokens for user."""
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600
        }
    
    def request_password_reset(self, email: str) -> bool:
        """Request password reset for user."""
        user = self.user_repository.find_by_email(email)
        if not user:
            # Don't reveal if email exists
            return True
        
        # In a real implementation, we would:
        # 1. Generate a reset token
        # 2. Store it in the database
        # 3. Send email with reset link
        # For now, just return True
        return True
    
    def reset_password(self, token: str, password: str) -> bool:
        """Reset user password using reset token."""
        # In a real implementation, we would:
        # 1. Validate the reset token
        # 2. Find the user associated with the token
        # 3. Update their password
        # 4. Invalidate the token
        # For now, return False as we don't have token storage
        return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not user.verify_password(current_password):
            return False
        
        # Update password
        user.set_password(new_password)
        self.user_repository.save(user)
        
        return True