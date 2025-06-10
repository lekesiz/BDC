"""Authentication service implementation with proper JWT handling."""
from typing import Optional, Dict, Any
from datetime import datetime
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_activity import UserActivity
from app.models.tenant import Tenant
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.services.v2.interfaces.auth_service_interface import IAuthService
from app.core.security import SecurityManager
from app.extensions import db
from app.utils.cache import cache, generate_cache_key
from app.utils.logging import logger


class AuthServiceV2(IAuthService):
    """Authentication service with proper JWT and security handling."""
    
    def __init__(self, user_repository: IUserRepository, 
                 security_manager: SecurityManager,
                 db_session: Optional[Session] = None):
        """Initialize auth service with dependencies."""
        self.user_repository = user_repository
        self.security_manager = security_manager
        self.db_session = db_session or db.session
    
    def login(self, email: str, password: str, remember: bool = False) -> Optional[Dict[str, Any]]:
        """Authenticate user and return JWT tokens."""
        try:
            # Find user by email
            user = self.user_repository.find_by_email(email)
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {email}")
                return None
            
            # Verify password
            if not user.verify_password(password):
                # Update failed login attempts
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                user.last_failed_login = datetime.utcnow()
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.is_active = False
                    user.locked_at = datetime.utcnow()
                    logger.warning(f"Account locked due to failed attempts: {email}")
                
                self.db_session.commit()
                return None
            
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            user.last_failed_login = None
            self.db_session.commit()
            
            # Generate JWT tokens
            access_token = create_access_token(
                identity=user.id,
                fresh=True,
                additional_claims={
                    'role': user.role,
                    'tenant_id': user.tenant_id,
                    'email': user.email
                }
            )
            
            refresh_token = create_refresh_token(
                identity=user.id,
                additional_claims={
                    'role': user.role,
                    'tenant_id': user.tenant_id
                }
            )
            
            # Log activity
            self._log_activity(user.id, 'login', {'remember': remember})
            
            # Return user data and tokens
            return {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'tenant_id': user.tenant_id,
                    'is_active': user.is_active
                },
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer'
            }
            
        except Exception as e:
            logger.exception(f"Login error for {email}: {str(e)}")
            return None
    
    def register(self, email: str, password: str, first_name: str, last_name: str,
                 role: str = 'trainee', tenant_id: Optional[int] = None) -> Optional[User]:
        """Register a new user and return tokens."""
        try:
            # Check if user already exists
            if self.user_repository.find_by_email(email):
                logger.warning(f"Registration attempt with existing email: {email}")
                return None
            
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True,
                tenant_id=tenant_id
            )
            
            # Set password (this will hash it)
            user.password = password
            
            # Save user
            self.db_session.add(user)
            self.db_session.commit()
            
            # Generate JWT tokens for auto-login
            access_token = create_access_token(
                identity=user.id,
                fresh=True,
                additional_claims={
                    'role': user.role,
                    'tenant_id': user.tenant_id,
                    'email': user.email
                }
            )
            
            refresh_token = create_refresh_token(
                identity=user.id,
                additional_claims={
                    'role': user.role,
                    'tenant_id': user.tenant_id
                }
            )
            
            # Log activity
            self._log_activity(user.id, 'register', {'email': email})
            
            # Add tokens to user object for response
            user._access_token = access_token
            user._refresh_token = refresh_token
            
            return user
            
        except Exception as e:
            logger.exception(f"Registration error for {email}: {str(e)}")
            self.db_session.rollback()
            return None
    
    def refresh_token(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Refresh access token for user."""
        try:
            # Get user
            user = self.user_repository.find_by_id(user_id)
            
            if not user or not user.is_active:
                return None
            
            # Generate new access token
            access_token = create_access_token(
                identity=user.id,
                fresh=False,
                additional_claims={
                    'role': user.role,
                    'tenant_id': user.tenant_id,
                    'email': user.email
                }
            )
            
            return {
                'access_token': access_token,
                'token_type': 'Bearer'
            }
            
        except Exception as e:
            logger.exception(f"Token refresh error for user {user_id}: {str(e)}")
            return None
    
    def logout(self, jti: str) -> bool:
        """Logout user by blacklisting the JWT token."""
        try:
            # Add token to blacklist
            cache_key = generate_cache_key('token_blacklist', jti)
            cache.set(cache_key, True, timeout=86400)  # 24 hours
            
            return True
            
        except Exception as e:
            logger.exception(f"Logout error: {str(e)}")
            return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            user = self.user_repository.find_by_id(user_id)
            
            if not user:
                return False
            
            # Verify current password
            if not user.verify_password(current_password):
                return False
            
            # Update password
            user.password = new_password
            self.db_session.commit()
            
            # Log activity
            self._log_activity(user_id, 'password_changed', {})
            
            return True
            
        except Exception as e:
            logger.exception(f"Change password error for user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def reset_password(self, email: str, new_password: str) -> bool:
        """Reset user password (admin function)."""
        try:
            user = self.user_repository.find_by_email(email)
            
            if not user:
                return False
            
            # Update password
            user.password = new_password
            self.db_session.commit()
            
            # Log activity
            self._log_activity(user.id, 'password_reset', {'by': 'admin'})
            
            return True
            
        except Exception as e:
            logger.exception(f"Password reset error for {email}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def _log_activity(self, user_id: int, activity_type: str, details: Dict[str, Any]):
        """Log user activity."""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                details=details,
                ip_address=details.get('ip_address'),
                user_agent=details.get('user_agent')
            )
            self.db_session.add(activity)
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")