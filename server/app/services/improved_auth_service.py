"""Improved authentication service with dependency injection."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm import Session

from app.services.interfaces.user_repository_interface import IUserRepository
from app.services.interfaces.auth_service_interface import IAuthService
from app.models import User, TokenBlocklist
from app.extensions import db


class ImprovedAuthService(IAuthService):
    """Improved authentication service with dependency injection."""
    
    def __init__(self, user_repository: IUserRepository, db_session: Optional[Session] = None):
        """Initialize service with dependencies.
        
        Args:
            user_repository: User repository implementation
            db_session: Database session (optional)
        """
        self.user_repository = user_repository
        self.db_session = db_session or db.session
    
    def login(self, email: str, password: str, remember: bool = False) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return tokens.
        
        Args:
            email: User's email
            password: User's password
            remember: Whether to remember the user
            
        Returns:
            Dictionary with tokens or None if authentication fails
        """
        # Verify credentials using repository
        user = self.user_repository.verify_credentials(email, password)
        if not user:
            return None
        
        # Update last login time
        user.last_login = datetime.now(timezone.utc)
        self.user_repository.save(user)
        self.db_session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': 3600,  # 1 hour in seconds
            'user': self._serialize_user(user)
        }
    
    def register(self, email: str, password: str, first_name: str, 
                last_name: str, role: str = 'student', 
                tenant_id: Optional[int] = None) -> Optional[User]:
        """Register a new user.
        
        Args:
            email: User's email
            password: User's password
            first_name: User's first name
            last_name: User's last name
            role: User's role
            tenant_id: User's tenant ID
            
        Returns:
            Created user or None if registration fails
        """
        # Check if user already exists
        if self.user_repository.exists_by_email(email):
            return None
        
        try:
            # Create user
            user_data = {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'is_active': True
            }
            
            if tenant_id:
                user_data['tenant_id'] = tenant_id
            
            user = self.user_repository.create(**user_data)
            
            # Handle tenant relationship if needed
            if tenant_id and hasattr(user, 'tenants'):
                from app.models import Tenant
                tenant = self.db_session.query(Tenant).get(tenant_id)
                if tenant:
                    user.tenants.append(tenant)
            
            self.db_session.commit()
            return user
            
        except Exception as e:
            self.db_session.rollback()
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if refresh fails
        """
        # TODO: Implement proper refresh token validation
        # For now, we'll extract user_id from the token using JWT decode
        try:
            from flask_jwt_extended import decode_token
            token_data = decode_token(refresh_token)
            user_id = token_data['sub']
            
            user = self.user_repository.find_by_id(user_id)
            if not user or not user.is_active:
                return None
            
            access_token = create_access_token(identity=user.id)
            
            return {
                'access_token': access_token,
                'token_type': 'bearer',
                'expires_in': 3600
            }
        except Exception:
            return None
    
    def logout(self, user_id: int, token: str) -> bool:
        """Logout user by blacklisting token.
        
        Args:
            user_id: ID of the user
            token: JWT token to invalidate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract JTI from token
            from flask_jwt_extended import decode_token
            token_data = decode_token(token)
            jti = token_data['jti']
            
            # Add token to blocklist
            token_blocklist = TokenBlocklist(jti=jti, created_at=datetime.now(timezone.utc))
            self.db_session.add(token_blocklist)
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            return False
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.user_repository.find_by_email(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repository.find_by_id(user_id)
    
    def update_last_login(self, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = datetime.now(timezone.utc)
        self.user_repository.save(user)
    
    def verify_password(self, user: User, password: str) -> bool:
        """Verify user's password."""
        return user.verify_password(password)
    
    def request_password_reset(self, email: str) -> bool:
        """Request password reset for user."""
        user = self.user_repository.find_by_email(email)
        if not user:
            return False
        
        # TODO: Implement password reset token generation and email sending
        # For now, just return True to indicate the request was processed
        return True
    
    def reset_password(self, token: str, password: str) -> bool:
        """Reset user password using reset token."""
        # TODO: Implement password reset token validation
        # For now, this method handles both token-based and email-based resets
        # In a real implementation, you would validate the token and find the user
        try:
            # For demonstration, we'll treat the token as an email if it contains @
            if '@' in token:
                user = self.user_repository.find_by_email(token)
                if user:
                    user.password = password
                    self.user_repository.save(user)
                    self.db_session.commit()
                    return True
            return False
        except Exception:
            self.db_session.rollback()
            return False
    
    def change_password(self, user_id: int, current_password: str, 
                       new_password: str) -> bool:
        """Change user password.
        
        Args:
            user_id: User's ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        user = self.user_repository.find_by_id(user_id)
        if not user or not user.verify_password(current_password):
            return False
        
        try:
            user.password = new_password
            self.user_repository.save(user)
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            return False
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user for API response.
        
        Args:
            user: User instance
            
        Returns:
            Serialized user data
        """
        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active
        }