"""User repository implementation."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.repositories.v2.base_repository import BaseRepository
from app.repositories.v2.interfaces.user_repository_interface import IUserRepository
from app.models import User


class UserRepository(BaseRepository[User], IUserRepository):
    """User repository with concrete implementations."""
    
    def __init__(self, db_session: Session):
        """Initialize user repository."""
        super().__init__(db_session, User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address."""
        return self.find_one_by(email=email)
    
    def find_by_tenant(self, tenant_id: int, limit: int = 100, offset: int = 0) -> List[User]:
        """Find all users for a specific tenant."""
        try:
            return (self.db.query(User)
                    .filter_by(tenant_id=tenant_id)
                    .offset(offset)
                    .limit(limit)
                    .all())
        except Exception as e:
            self.db.rollback()
            raise e
    
    def find_by_role(self, role: str, tenant_id: Optional[int] = None) -> List[User]:
        """Find users by role, optionally filtered by tenant."""
        try:
            query = self.db.query(User).filter_by(role=role)
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            return query.all()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def find_active_users(self, tenant_id: Optional[int] = None) -> List[User]:
        """Find all active users."""
        try:
            query = self.db.query(User).filter_by(is_active=True)
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            return query.all()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp."""
        return self.update(user, {'last_login': datetime.utcnow()})
    
    def update_password(self, user: User, password_hash: str) -> User:
        """Update user's password hash."""
        return self.update(user, {'password_hash': password_hash})
    
    def deactivate(self, user: User) -> User:
        """Deactivate user account."""
        return self.update(user, {'is_active': False})
    
    def activate(self, user: User) -> User:
        """Activate user account."""
        return self.update(user, {'is_active': True})
    
    def find_by_reset_token(self, token: str) -> Optional[User]:
        """Find user by password reset token."""
        try:
            # This assumes we have a reset_token field or related table
            # Adjust based on actual implementation
            return self.db.query(User).filter_by(reset_token=token).first()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def search(self, query: str, tenant_id: Optional[int] = None, 
               limit: int = 100, offset: int = 0) -> List[User]:
        """Search users by name or email."""
        try:
            search_filter = or_(
                User.email.ilike(f'%{query}%'),
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%')
            )
            
            db_query = self.db.query(User).filter(search_filter)
            
            if tenant_id:
                db_query = db_query.filter_by(tenant_id=tenant_id)
            
            return db_query.offset(offset).limit(limit).all()
        except Exception as e:
            self.db.rollback()
            raise e