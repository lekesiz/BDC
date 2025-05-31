"""User Service implementation."""

import os
import time
from typing import Dict, Any, Optional, List
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from marshmallow import ValidationError
from passlib.context import CryptContext

from app.extensions import db, logger
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas import UserSchema, UserCreateSchema, UserUpdateSchema, UserProfileSchema
from app.services.interfaces.user_service_interface import IUserService
from app.repositories.user_repository import UserRepository


class UserService(IUserService):
    """User service implementation."""
    
    def __init__(self, user_repository: UserRepository, upload_folder: str = None):
        """
        Initialize UserService.
        
        Args:
            user_repository: The user repository instance
            upload_folder: Path to upload folder for profile pictures
        """
        self.user_repository = user_repository
        self.upload_folder = upload_folder or 'uploads'
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Hash the password
            hashed_password = self.pwd_context.hash(user_data.password)
            
            # Create user entity
            user = User(
                email=user_data.email,
                password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role,
                phone=user_data.phone,
                organization=user_data.organization,
                tenant_id=user_data.tenant_id,
                is_active=True
            )
            
            # Save to database
            saved_user = await self.user_repository.create(user)
            
            # Convert to response schema
            return UserResponse.from_orm(saved_user)
            
        except Exception as e:
            logger.exception(f"Create user error: {str(e)}")
            raise
    
    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get a user by ID."""
        try:
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                return None
            
            return UserResponse.from_orm(user)
            
        except Exception as e:
            logger.exception(f"Get user error: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by email."""
        try:
            user = await self.user_repository.get_by_email(email)
            
            if not user:
                return None
            
            return UserResponse.from_orm(user)
            
        except Exception as e:
            logger.exception(f"Get user by email error: {str(e)}")
            raise
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update a user's information."""
        try:
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                return None
            
            # Update user fields
            update_data = user_data.dict(exclude_unset=True)
            
            # Handle password update if provided
            if 'password' in update_data:
                update_data['password'] = self.pwd_context.hash(update_data['password'])
            
            # Update fields
            for key, value in update_data.items():
                setattr(user, key, value)
            
            # Save changes
            updated_user = await self.user_repository.update(user)
            
            return UserResponse.from_orm(updated_user)
            
        except Exception as e:
            logger.exception(f"Update user error: {str(e)}")
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                return False
            
            # Soft delete the user
            user.is_active = False
            await self.user_repository.update(user)
            
            return True
            
        except Exception as e:
            logger.exception(f"Delete user error: {str(e)}")
            raise
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        try:
            user = await self.user_repository.get_by_email(email)
            
            if not user:
                return None
            
            if not await self.verify_password(password, user.password):
                return None
            
            return user
            
        except Exception as e:
            logger.exception(f"Authenticate user error: {str(e)}")
            raise
    
    async def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update a user's password."""
        try:
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                return False
            
            # Hash the new password
            user.password = self.pwd_context.hash(new_password)
            
            # Save changes
            await self.user_repository.update(user)
            
            return True
            
        except Exception as e:
            logger.exception(f"Update user password error: {str(e)}")
            raise
    
    # Additional methods that were in the original service
    def get_current_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user."""
        try:
            user = self.user_repository.get_by_id(user_id)
            
            if not user:
                return None
            
            schema = UserProfileSchema()
            return schema.dump(user)
            
        except Exception as e:
            logger.exception(f"Get current user error: {str(e)}")
            raise
    
    def get_users(
        self,
        page: int = 1,
        per_page: int = 10,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        tenant_id: Optional[int] = None,
        sort_by: str = 'created_at',
        sort_direction: str = 'desc'
    ) -> Dict[str, Any]:
        """Get paginated users with filters."""
        try:
            # Build query
            query = User.query
            
            if role:
                query = query.filter_by(role=role)
            
            # Handle is_active filtering
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            elif status:
                if status == 'active':
                    query = query.filter_by(is_active=True)
                elif status == 'inactive':
                    query = query.filter_by(is_active=False)
            else:
                # Default to active users only
                query = query.filter_by(is_active=True)
            
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            
            # Apply sorting
            sort_attr = getattr(User, sort_by, None)
            if sort_attr:
                if sort_direction.lower() == 'desc':
                    query = query.order_by(sort_attr.desc())
                else:
                    query = query.order_by(sort_attr.asc())
            
            # Paginate query
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Serialize data
            schema = UserSchema(many=True)
            users = schema.dump(pagination.items)
            
            return {
                'items': users,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'filters': {
                    'is_active': is_active,
                    'status': status,
                    'role': role,
                    'show_inactive': is_active is False or status == 'inactive'
                }
            }
            
        except Exception as e:
            logger.exception(f"Get users error: {str(e)}")
            raise
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed user profile."""
        try:
            user = self.user_repository.get_by_id(user_id)
            
            if not user:
                return None
            
            schema = UserProfileSchema()
            profile_data = schema.dump(user)
            
            # Add additional profile information
            profile_data['stats'] = {
                'appointments_count': 0,  # To be implemented
                'evaluations_count': 0,   # To be implemented
                'documents_count': 0      # To be implemented
            }
            
            return profile_data
            
        except Exception as e:
            logger.exception(f"Get user profile error: {str(e)}")
            raise
    
    def update_user_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile."""
        try:
            user = self.user_repository.get_by_id(user_id)
            
            if not user:
                raise ValueError("User not found")
            
            # Update user fields
            updateable_fields = [
                'first_name', 'last_name', 'phone', 'bio', 'timezone', 
                'organization', 'address', 'city', 'state', 'zip_code', 
                'country', 'email_notifications', 'push_notifications', 
                'sms_notifications', 'language', 'theme'
            ]
            
            for field in updateable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            db.session.commit()
            
            # Return updated profile
            schema = UserProfileSchema()
            return schema.dump(user)
            
        except Exception as e:
            logger.exception(f"Update user profile error: {str(e)}")
            db.session.rollback()
            raise
    
    def upload_profile_picture(self, user_id: int, file: FileStorage) -> Dict[str, str]:
        """Upload user profile picture."""
        try:
            user = self.user_repository.get_by_id(user_id)
            
            if not user:
                raise ValueError("User not found")
            
            if not file or file.filename == '':
                raise ValueError("No file provided")
            
            # Check file extension
            if not self._allowed_file(file.filename):
                raise ValueError("Invalid file type. Allowed types: png, jpg, jpeg, gif")
            
            # Create secure filename
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{user_id}_{timestamp}_{filename}"
            
            # Save file
            profile_pictures_folder = os.path.join(self.upload_folder, 'profile_pictures')
            
            # Create directory if it doesn't exist
            if not os.path.exists(profile_pictures_folder):
                os.makedirs(profile_pictures_folder)
            
            file_path = os.path.join(profile_pictures_folder, filename)
            file.save(file_path)
            
            # Update user's profile picture URL
            user.profile_picture = f'/uploads/profile_pictures/{filename}'
            db.session.commit()
            
            return {
                'message': 'Profile picture uploaded successfully',
                'profile_picture': user.profile_picture
            }
            
        except Exception as e:
            logger.exception(f"Upload profile picture error: {str(e)}")
            db.session.rollback()
            raise
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions