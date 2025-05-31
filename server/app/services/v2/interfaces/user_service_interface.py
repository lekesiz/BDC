"""User service interface."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.models import User, UserProfile, UserActivity


class IUserService(ABC):
    """User service interface."""
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        pass
    
    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    def search_users(self, query: str, filters: Optional[Dict[str, Any]] = None,
                    page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search users with pagination."""
        pass
    
    @abstractmethod
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
        pass
    
    @abstractmethod
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        pass
    
    @abstractmethod
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update user role."""
        pass
    
    @abstractmethod
    def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        pass
    
    @abstractmethod
    def get_users_by_tenant(self, tenant_id: int) -> List[User]:
        """Get all users for a tenant."""
        pass
    
    # User Profile Management
    @abstractmethod
    def create_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        """Create user profile."""
        pass
    
    @abstractmethod
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile."""
        pass
    
    @abstractmethod
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile."""
        pass
    
    @abstractmethod
    def upload_profile_picture(self, user_id: int, file_data: Dict[str, Any]) -> str:
        """Upload user profile picture."""
        pass
    
    # Activity Tracking
    @abstractmethod
    def get_user_activities(self, user_id: int, limit: int = 50) -> List[UserActivity]:
        """Get user activity history."""
        pass
    
    @abstractmethod
    def log_user_activity(self, user_id: int, activity_type: str, 
                         details: Dict[str, Any]) -> UserActivity:
        """Log user activity."""
        pass
    
    # Statistics and Analytics
    @abstractmethod
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        pass
    
    @abstractmethod
    def get_users_statistics(self) -> Dict[str, Any]:
        """Get overall users statistics."""
        pass
    
    # Permissions and Access
    @abstractmethod
    def check_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has a specific permission."""
        pass
    
    @abstractmethod
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get all permissions for a user."""
        pass
    
    @abstractmethod
    def update_user_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """Update user permissions."""
        pass