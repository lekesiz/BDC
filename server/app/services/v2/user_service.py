"""User service implementation with dependency injection."""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from flask import current_app
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.models import User, UserProfile, UserActivity, Permission, Role
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.repositories.v2.user_repository import UserRepository
from app.services.v2.interfaces.user_service_interface import IUserService
from app.core.security import SecurityManager
from app.utils.cache import cache, generate_cache_key


class UserServiceV2(IUserService):
    """User service with dependency injection."""
    
    def __init__(self, user_repository: Optional[IUserRepository] = None,
                 security_manager: Optional[SecurityManager] = None,
                 db_session: Optional[Session] = None):
        """Initialize user service with dependencies."""
        self.user_repository = user_repository
        self.security_manager = security_manager or SecurityManager()
        self.db_session = db_session
    
    def _get_repository(self) -> IUserRepository:
        """Get user repository instance."""
        if self.user_repository:
            return self.user_repository
        
        from app.extensions import db
        session = self.db_session or db.session
        return UserRepository(session)
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        repo = self._get_repository()
        
        # Check if user exists
        if repo.find_by_email(user_data['email']):
            raise ValueError(f"User with email {user_data['email']} already exists")
        
        # Hash password if provided
        if 'password' in user_data:
            user_data['password_hash'] = self.security_manager.hash_password(user_data.pop('password'))
        
        # Create user
        user = User(**user_data)
        created_user = repo.create(user)
        
        # Create default profile
        self.create_user_profile(created_user.id, {})
        
        # Log activity
        self.log_user_activity(created_user.id, 'user_created', {'email': user_data['email']})
        
        # Clear cache
        self._clear_cache()
        
        return created_user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        cache_key = generate_cache_key('user', user_id)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        repo = self._get_repository()
        user = repo.find_by_id(user_id)
        
        if user:
            cache.set(cache_key, user, timeout=300)
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        repo = self._get_repository()
        return repo.find_by_email(email)
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        repo = self._get_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return None
        
        # Hash password if being updated
        if 'password' in update_data:
            update_data['password_hash'] = self.security_manager.hash_password(update_data.pop('password'))
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(user, key) and key not in ['id', 'created_at']:
                setattr(user, key, value)
        
        updated_user = repo.update(user)
        
        # Log activity
        self.log_user_activity(user_id, 'user_updated', {'fields': list(update_data.keys())})
        
        # Clear cache
        cache_key = generate_cache_key('user', user_id)
        cache.delete(cache_key)
        self._clear_cache()
        
        return updated_user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        repo = self._get_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return False
        
        # Log activity before deletion
        self.log_user_activity(user_id, 'user_deleted', {'email': user.email})
        
        result = repo.delete(user_id)
        
        if result:
            # Clear cache
            cache_key = generate_cache_key('user', user_id)
            cache.delete(cache_key)
            self._clear_cache()
        
        return result
    
    def search_users(self, query: str, filters: Optional[Dict[str, Any]] = None,
                    page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search users with pagination."""
        repo = self._get_repository()
        
        # Build search query
        users_query = repo.db.query(User)
        
        # Apply text search
        if query:
            users_query = users_query.filter(
                User.name.ilike(f'%{query}%') |
                User.surname.ilike(f'%{query}%') |
                User.email.ilike(f'%{query}%')
            )
        
        # Apply filters
        if filters:
            if 'role' in filters:
                users_query = users_query.filter(User.role == filters['role'])
            if 'is_active' in filters:
                users_query = users_query.filter(User.is_active == filters['is_active'])
            if 'tenant_id' in filters:
                users_query = users_query.filter(User.tenant_id == filters['tenant_id'])
        
        # Paginate
        total = users_query.count()
        users = users_query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
        repo = self._get_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return False
        
        user.is_active = True
        user.activated_at = datetime.utcnow()
        repo.update(user)
        
        self.log_user_activity(user_id, 'user_activated', {})
        self._clear_cache()
        
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        repo = self._get_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return False
        
        user.is_active = False
        user.deactivated_at = datetime.utcnow()
        repo.update(user)
        
        self.log_user_activity(user_id, 'user_deactivated', {})
        self._clear_cache()
        
        return True
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update user role."""
        repo = self._get_repository()
        user = repo.find_by_id(user_id)
        
        if not user:
            return False
        
        old_role = user.role
        user.role = new_role
        repo.update(user)
        
        self.log_user_activity(user_id, 'role_changed', {
            'old_role': old_role,
            'new_role': new_role
        })
        self._clear_cache()
        
        return True
    
    def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        repo = self._get_repository()
        return repo.find_all_by(role=role)
    
    def get_users_by_tenant(self, tenant_id: int) -> List[User]:
        """Get all users for a tenant."""
        repo = self._get_repository()
        return repo.find_all_by(tenant_id=tenant_id)
    
    # User Profile Management
    def create_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        """Create user profile."""
        from app.extensions import db
        
        # Check if profile exists
        existing = db.session.query(UserProfile).filter_by(user_id=user_id).first()
        if existing:
            return existing
        
        profile = UserProfile(user_id=user_id, **profile_data)
        db.session.add(profile)
        db.session.commit()
        
        return profile
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile."""
        from app.extensions import db
        return db.session.query(UserProfile).filter_by(user_id=user_id).first()
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile."""
        profile = self.get_user_profile(user_id)
        
        if not profile:
            return self.create_user_profile(user_id, profile_data)
        
        from app.extensions import db
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return profile
    
    def upload_profile_picture(self, user_id: int, file_data: Dict[str, Any]) -> str:
        """Upload user profile picture."""
        file = file_data['file']
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_id}_{timestamp}_{filename}"
        
        # Create upload directory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pictures')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Update profile
        profile_url = f"/uploads/profile_pictures/{filename}"
        self.update_user_profile(user_id, {'profile_picture': profile_url})
        
        return profile_url
    
    # Activity Tracking
    def get_user_activities(self, user_id: int, limit: int = 50) -> List[UserActivity]:
        """Get user activity history."""
        from app.extensions import db
        return db.session.query(UserActivity).filter_by(
            user_id=user_id
        ).order_by(UserActivity.created_at.desc()).limit(limit).all()
    
    def log_user_activity(self, user_id: int, activity_type: str,
                         details: Dict[str, Any]) -> UserActivity:
        """Log user activity."""
        from app.extensions import db
        
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            details=details,
            ip_address=details.get('ip_address'),
            user_agent=details.get('user_agent')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return activity
    
    # Statistics and Analytics
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        from app.extensions import db
        
        user = self.get_user(user_id)
        if not user:
            return {}
        
        # Activity count
        activity_count = db.session.query(UserActivity).filter_by(
            user_id=user_id
        ).count()
        
        # Last activity
        last_activity = db.session.query(UserActivity).filter_by(
            user_id=user_id
        ).order_by(UserActivity.created_at.desc()).first()
        
        # Login count
        login_count = db.session.query(UserActivity).filter_by(
            user_id=user_id,
            activity_type='login'
        ).count()
        
        return {
            'user_id': user_id,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'last_login': user.last_login,
            'activity_count': activity_count,
            'login_count': login_count,
            'last_activity': last_activity.created_at if last_activity else None
        }
    
    def get_users_statistics(self) -> Dict[str, Any]:
        """Get overall users statistics."""
        cache_key = generate_cache_key('users_stats')
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        repo = self._get_repository()
        
        # Count by role
        role_counts = repo.db.query(
            User.role,
            repo.db.func.count(User.id)
        ).group_by(User.role).all()
        
        # Count active/inactive
        active_count = repo.count_by(is_active=True)
        inactive_count = repo.count_by(is_active=False)
        
        stats = {
            'total': repo.count(),
            'active': active_count,
            'inactive': inactive_count,
            'by_role': dict(role_counts),
            'recent_registrations': repo.db.query(User).filter(
                User.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
        }
        
        cache.set(cache_key, stats, timeout=600)
        
        return stats
    
    # Permissions and Access
    def check_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has a specific permission."""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # Super admin has all permissions
        if user.role == 'super_admin':
            return True
        
        # Check role-based permissions
        from app.extensions import db
        role = db.session.query(Role).filter_by(name=user.role).first()
        if role:
            return any(p.name == permission for p in role.permissions)
        
        return False
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get all permissions for a user."""
        user = self.get_user(user_id)
        if not user:
            return []
        
        # Super admin has all permissions
        if user.role == 'super_admin':
            from app.extensions import db
            all_permissions = db.session.query(Permission).all()
            return [p.name for p in all_permissions]
        
        # Get role-based permissions
        from app.extensions import db
        role = db.session.query(Role).filter_by(name=user.role).first()
        if role:
            return [p.name for p in role.permissions]
        
        return []
    
    def update_user_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """Update user permissions."""
        # This would typically update custom user permissions
        # For now, permissions are role-based
        self.log_user_activity(user_id, 'permissions_updated', {
            'permissions': permissions
        })
        return True
    
    def _clear_cache(self):
        """Clear relevant cache entries."""
        cache.delete(generate_cache_key('users_stats'))
        cache.delete_many(*[
            generate_cache_key('users_list', page)
            for page in range(1, 10)
        ])