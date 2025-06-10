"""User service implementation."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.services.v2.interfaces.user_service_interface import IUserService
from app.core.security import SecurityManager
from app.extensions import db
from app.utils.logging import logger


class UserServiceV2(IUserService):
    """User service with business logic."""
    
    def __init__(self, user_repository: IUserRepository,
                 security_manager: SecurityManager,
                 db_session: Optional[Session] = None):
        """Initialize service with dependencies."""
        self.user_repository = user_repository
        self.security_manager = security_manager
        self.db_session = db_session or db.session
    
    def get_all_users(self, tenant_id: Optional[int] = None) -> List[User]:
        """Get all users, optionally filtered by tenant."""
        try:
            if tenant_id:
                return self.user_repository.find_by_tenant(tenant_id)
            return self.user_repository.find_all()
        except Exception as e:
            logger.exception(f"Error getting users: {str(e)}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return self.user_repository.find_by_id(user_id)
        except Exception as e:
            logger.exception(f"Error getting user {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return self.user_repository.find_by_email(email)
        except Exception as e:
            logger.exception(f"Error getting user by email {email}: {str(e)}")
            return None
    
    def create_user(self, data: Dict[str, Any]) -> Optional[User]:
        """Create a new user."""
        try:
            # Check if user exists
            if self.user_repository.find_by_email(data['email']):
                logger.warning(f"User with email {data['email']} already exists")
                return None
            
            # Extract password before creating user
            password = data.pop('password', None)
            
            # Create user
            user = User(**data)
            
            # Set password if provided
            if password:
                user.password = password
            
            self.db_session.add(user)
            self.db_session.commit()
            
            logger.info(f"Created user: {user.id}")
            return user
            
        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")
            self.db_session.rollback()
            return None
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Optional[User]:
        """Update user data."""
        try:
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return None
            
            # Handle password separately
            if 'password' in data:
                password = data.pop('password')
                user.password = password
            
            # Update other fields
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db_session.commit()
            
            logger.info(f"Updated user: {user_id}")
            return user
            
        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {str(e)}")
            self.db_session.rollback()
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False
            
            # Soft delete - just deactivate
            user.is_active = False
            self.db_session.commit()
            
            logger.info(f"Deactivated user: {user_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error deleting user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user."""
        try:
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False
            
            user.is_active = True
            self.db_session.commit()
            
            logger.info(f"Activated user: {user_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error activating user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user."""
        try:
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            self.db_session.commit()
            
            logger.info(f"Deactivated user: {user_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error deactivating user {user_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def change_user_role(self, user_id: int, new_role: str) -> bool:
        """Change user role."""
        try:
            user = self.user_repository.find_by_id(user_id)
            if not user:
                return False
            
            # Validate role
            valid_roles = ['super_admin', 'tenant_admin', 'trainer', 'trainee']
            if new_role not in valid_roles:
                logger.warning(f"Invalid role: {new_role}")
                return False
            
            user.role = new_role
            self.db_session.commit()
            
            logger.info(f"Changed user {user_id} role to {new_role}")
            return True
            
        except Exception as e:
            logger.exception(f"Error changing user role: {str(e)}")
            self.db_session.rollback()
            return False
    
    def get_users_by_role(self, role: str, tenant_id: Optional[int] = None) -> List[User]:
        """Get users by role."""
        try:
            return self.user_repository.find_by_role(role, tenant_id)
        except Exception as e:
            logger.exception(f"Error getting users by role {role}: {str(e)}")
            return []