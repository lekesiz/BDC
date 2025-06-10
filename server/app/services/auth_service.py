"""Authentication service implementation with dependency injection."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy.orm import Session

from app.models import User, UserActivity
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.repositories.v2.user_repository import UserRepository
from app.services.v2.interfaces.auth_service_interface import IAuthService
from app.core.security import SecurityManager
from app.utils.cache import cache, generate_cache_key


class AuthServiceV2(IAuthService):
    """Authentication service with dependency injection."""
    
    def __init__(self, user_repository: Optional[IUserRepository] = None, 
                 security_manager: Optional[SecurityManager] = None,
                 db_session: Optional[Session] = None):
        """Initialize auth service with dependencies."""
        self.user_repository = user_repository
        self.security_manager = security_manager or SecurityManager()
        self.db_session = db_session
    
    def _get_user_repository(self) -> IUserRepository:
        """Get user repository instance."""
        if self.user_repository:
            return self.user_repository
        
        # Fallback to creating repository with current session
        from app.extensions import db
        session = self.db_session or db.session
        return UserRepository(session)
    
    def authenticate(self, email: str, password: str, remember: bool = False) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password."""
        repo = self._get_user_repository()
        user = repo.find_by_email(email)
        
        if not user or not user.is_active:
            return None
        
        if not self.security_manager.verify_password(password, user.password_hash):
            # Update failed login attempts
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            user.last_failed_login = datetime.utcnow()
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.is_active = False
                user.locked_at = datetime.utcnow()
            
            repo.update(user)
            return None
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        user.last_failed_login = None
        repo.update(user)
        
        # Generate tokens
        access_token = self.security_manager.generate_access_token(user.id, remember)
        refresh_token = self.security_manager.generate_refresh_token(user.id)
        
        # Log activity
        self._log_activity(user.id, 'login', {'remember': remember})
        
        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 86400 if remember else 3600  # 24h if remember, else 1h
        }
    
    def register(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Register a new user."""
        repo = self._get_user_repository()
        
        # Check if user already exists
        if repo.find_by_email(user_data['email']):
            return None
        
        # Hash password
        password_hash = self.security_manager.hash_password(user_data['password'])
        
        # Create user
        user = User(
            email=user_data['email'],
            name=user_data.get('name'),
            surname=user_data.get('surname'),
            password_hash=password_hash,
            role=user_data.get('role', 'user'),
            is_active=user_data.get('is_active', True),
            tenant_id=user_data.get('tenant_id')
        )
        
        created_user = repo.create(user)
        
        # Log activity
        self._log_activity(created_user.id, 'register', {'email': user_data['email']})
        
        return created_user
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        payload = self.security_manager.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        repo = self._get_user_repository()
        user = repo.find_by_id(user_id)
        
        if not user or not user.is_active:
            return None
        
        # Generate new access token
        access_token = self.security_manager.generate_access_token(user.id)
        
        return {
            'user': user,
            'access_token': access_token,
            'expires_in': 3600  # 1 hour
        }
    
    def reset_password(self, email: str) -> Optional[str]:
        """Generate password reset token."""
        repo = self._get_user_repository()
        user = repo.find_by_email(email)
        
        if not user:
            return None
        
        # Generate reset token
        reset_token = self.security_manager.generate_password_reset_token(user.id)
        
        # Store token with expiration
        cache_key = generate_cache_key('password_reset', user.id)
        cache.set(cache_key, reset_token, timeout=3600)  # 1 hour expiration
        
        # Log activity
        self._log_activity(user.id, 'password_reset_requested', {'email': email})
        
        return reset_token
    
    def confirm_reset_password(self, token: str, new_password: str) -> Optional[User]:
        """Confirm password reset with token."""
        payload = self.security_manager.verify_password_reset_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        # Verify token in cache
        cache_key = generate_cache_key('password_reset', user_id)
        cached_token = cache.get(cache_key)
        
        if cached_token != token:
            return None
        
        repo = self._get_user_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return None
        
        # Update password
        user.password_hash = self.security_manager.hash_password(new_password)
        updated_user = repo.update(user)
        
        # Clear reset token from cache
        cache.delete(cache_key)
        
        # Log activity
        self._log_activity(user.id, 'password_reset_completed', {})
        
        return updated_user
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        repo = self._get_user_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return False
        
        # Verify current password
        if not self.security_manager.verify_password(current_password, user.password_hash):
            return False
        
        # Update password
        user.password_hash = self.security_manager.hash_password(new_password)
        repo.update(user)
        
        # Log activity
        self._log_activity(user_id, 'password_changed', {})
        
        return True
    
    def logout(self, user_id: int, access_token: str) -> bool:
        """Logout user and invalidate token."""
        # Add token to blacklist
        cache_key = generate_cache_key('token_blacklist', access_token)
        cache.set(cache_key, True, timeout=86400)  # 24 hours
        
        # Log activity
        self._log_activity(user_id, 'logout', {})
        
        return True
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify access token and return user."""
        # Check if token is blacklisted
        cache_key = generate_cache_key('token_blacklist', token)
        if cache.get(cache_key):
            return None
        
        payload = self.security_manager.verify_access_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        repo = self._get_user_repository()
        user = repo.find_by_id(user_id)
        
        if not user or not user.is_active:
            return None
        
        return user
    
    def unlock_account(self, email: str) -> bool:
        """Unlock a locked user account."""
        repo = self._get_user_repository()
        user = repo.find_by_email(email)
        
        if not user:
            return False
        
        user.is_active = True
        user.failed_login_attempts = 0
        user.locked_at = None
        repo.update(user)
        
        # Log activity
        self._log_activity(user.id, 'account_unlocked', {'email': email})
        
        return True
    
    def verify_email(self, token: str) -> bool:
        """Verify email address."""
        # TODO: Implement email verification
        return True
    
    def resend_verification_email(self, email: str) -> bool:
        """Resend verification email."""
        # TODO: Implement resend verification
        return True
    
    def request_password_reset(self, email: str) -> bool:
        """Request password reset."""
        # This is same as reset_password method
        return self.reset_password(email) is not None
    
    def _log_activity(self, user_id: int, activity_type: str, details: Dict[str, Any]):
        """Log user activity."""
        try:
            from app.extensions import db
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                details=details,
                ip_address=None,  # Should be passed from request context
                user_agent=None   # Should be passed from request context
            )
            db.session.add(activity)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log activity: {str(e)}")


# Backward compatibility alias
AuthService = AuthServiceV2