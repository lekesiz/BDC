"""Example of UserService using the new standardized service layer architecture."""

from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models import User, UserProfile, UserActivity
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.repositories.v2.user_repository import UserRepository
from app.services.v2.interfaces.user_service_interface import IUserService
from app.core.security import SecurityManager

from .base_service import BaseService
from .decorators import service, transactional, cached, inject


@service(name='user_service_v3', dependencies=['user_repository', 'security_manager'])
class UserServiceV3(BaseService[User, IUserRepository], IUserService):
    """
    User service implementation using standardized architecture.
    
    This service demonstrates:
    - Extending BaseService for common functionality
    - Using @service decorator for auto-registration
    - Leveraging dependency injection
    - Using decorators for cross-cutting concerns
    """
    
    def __init__(self, 
                 user_repository: Optional[IUserRepository] = None,
                 security_manager: Optional[SecurityManager] = None,
                 **kwargs):
        """Initialize user service with dependencies."""
        super().__init__(repository=user_repository, **kwargs)
        self.security_manager = security_manager or SecurityManager()
    
    def _create_repository(self) -> IUserRepository:
        """Create repository instance."""
        return UserRepository(self.db_session)
    
    def validate(self, data: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """Validate user data."""
        errors = {}
        
        if context == 'create':
            # Email is required for creation
            if not data.get('email'):
                errors['email'] = 'Email is required'
            elif self.get_user_by_email(data['email']):
                errors['email'] = 'Email already exists'
            
            # Password is required for creation
            if not data.get('password'):
                errors['password'] = 'Password is required'
            elif len(data.get('password', '')) < 8:
                errors['password'] = 'Password must be at least 8 characters'
        
        # Validate email format
        if 'email' in data:
            import re
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
                errors['email'] = 'Invalid email format'
        
        # Validate role
        if 'role' in data:
            valid_roles = ['admin', 'trainer', 'beneficiary', 'user']
            if data['role'] not in valid_roles:
                errors['role'] = f'Invalid role. Must be one of: {", ".join(valid_roles)}'
        
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        
        return data
    
    def before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data before creating user."""
        # Hash password
        if 'password' in data:
            data['password_hash'] = self.security_manager.hash_password(data.pop('password'))
        
        # Set defaults
        data.setdefault('is_active', True)
        data.setdefault('role', 'user')
        data.setdefault('created_at', datetime.utcnow())
        
        return data
    
    def after_create(self, user: User) -> User:
        """Process after creating user."""
        # Create default profile
        self._create_default_profile(user)
        
        # Log activity
        self._log_activity(user.id, 'user_created', {'email': user.email})
        
        # Clear caches
        super().after_create(user)
        
        return user
    
    @transactional()
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user with profile.
        
        This method demonstrates using the base create() with additional logic.
        """
        # Use base create method
        user = self.create(user_data)
        
        # Send welcome email (async)
        self._send_welcome_email(user)
        
        return user
    
    @cached(timeout=300)
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with caching."""
        return self.repository.find_by_email(email)
    
    @transactional()
    def update_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Update user password with validation."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not self.security_manager.verify_password(current_password, user.password_hash):
            self.logger.warning(f"Invalid password attempt for user {user_id}")
            return False
        
        # Update password
        update_data = {
            'password_hash': self.security_manager.hash_password(new_password),
            'password_changed_at': datetime.utcnow()
        }
        
        self.update(user_id, update_data)
        
        # Log activity
        self._log_activity(user_id, 'password_changed', {})
        
        return True
    
    @cached(timeout=600)
    def get_users_by_role(self, role: str, 
                         include_inactive: bool = False) -> List[User]:
        """Get users by role with caching."""
        filters = {'role': role}
        if not include_inactive:
            filters['is_active'] = True
        
        return self.repository.find_all(filters=filters)
    
    def get_user_with_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user with profile information."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # Get profile
        profile = self.repository.get_user_profile(user_id)
        
        return {
            'user': user,
            'profile': profile,
            'permissions': self._get_user_permissions(user),
            'stats': self._get_user_stats(user_id)
        }
    
    @transactional()
    def deactivate_user(self, user_id: int, reason: str) -> bool:
        """Deactivate a user account."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        # Update user
        self.update(user_id, {
            'is_active': False,
            'deactivated_at': datetime.utcnow(),
            'deactivation_reason': reason
        })
        
        # Log activity
        self._log_activity(user_id, 'user_deactivated', {'reason': reason})
        
        # Revoke active sessions
        self._revoke_user_sessions(user_id)
        
        return True
    
    @inject('notification_service')
    def notify_user(self, user_id: int, message: str, notification_service=None):
        """
        Send notification to user.
        
        Demonstrates using @inject decorator for optional dependencies.
        """
        if notification_service:
            notification_service.send_notification(user_id, message)
        else:
            self.logger.warning("Notification service not available")
    
    # Private helper methods
    
    def _create_default_profile(self, user: User):
        """Create default user profile."""
        try:
            profile = UserProfile(
                user_id=user.id,
                display_name=f"{user.name} {user.surname}".strip() or user.email.split('@')[0]
            )
            self.db_session.add(profile)
            self.db_session.flush()
        except Exception as e:
            self.logger.error(f"Failed to create profile for user {user.id}: {str(e)}")
    
    def _log_activity(self, user_id: int, activity_type: str, details: Dict[str, Any]):
        """Log user activity."""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                details=details,
                created_at=datetime.utcnow()
            )
            self.db_session.add(activity)
            self.db_session.flush()
        except Exception as e:
            self.logger.error(f"Failed to log activity: {str(e)}")
    
    def _send_welcome_email(self, user: User):
        """Send welcome email to new user."""
        # This would typically use an email service
        self.logger.info(f"Would send welcome email to {user.email}")
    
    def _get_user_permissions(self, user: User) -> List[str]:
        """Get user permissions based on role."""
        # Simplified permission logic
        role_permissions = {
            'admin': ['users.*', 'settings.*', 'reports.*'],
            'trainer': ['users.read', 'users.update', 'reports.read'],
            'beneficiary': ['profile.*', 'documents.read'],
            'user': ['profile.read', 'profile.update']
        }
        return role_permissions.get(user.role, [])
    
    def _get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        # This would aggregate various user metrics
        return {
            'login_count': 0,
            'last_login': None,
            'documents_count': 0,
            'activities_count': 0
        }
    
    def _revoke_user_sessions(self, user_id: int):
        """Revoke all active sessions for user."""
        # This would invalidate all user tokens/sessions
        self.logger.info(f"Revoking sessions for user {user_id}")


# Example of using the service with factory
def example_usage():
    """Example of how to use the new service architecture."""
    from .service_factory import create_service_factory, get_service
    from .service_container import get_request_container
    
    # Method 1: Using factory
    factory = create_service_factory(UserServiceV3, 'user_service_v3')
    user_service = factory.create()
    
    # Method 2: Using container (after registration)
    container = get_request_container()
    user_service = container.resolve('user_service_v3')
    
    # Method 3: Using helper function
    user_service = get_service('user_service_v3')
    
    # Use the service
    user = user_service.create_user({
        'email': 'test@example.com',
        'password': 'secure_password',
        'name': 'Test',
        'surname': 'User'
    })
    
    return user