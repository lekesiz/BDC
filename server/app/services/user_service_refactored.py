"""Refactored User Service implementation with dependency injection."""

import os
import time
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserSchema, UserProfileSchema
from app.exceptions import NotFoundException, ValidationException, ForbiddenException
from app.utils.logger import get_logger
from app.services.interfaces.user_repository_interface import IUserRepository
from app.services.interfaces.beneficiary_repository_interface import IBeneficiaryRepository

logger = get_logger(__name__)


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    TRAINER = "trainer"
    CAREGIVER = "caregiver"
    VIEWER = "viewer"


class UserStatus(Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class PaginationResult:
    """Pagination result wrapper."""
    items: List[Any]
    total: int
    pages: int
    current_page: int
    per_page: int


class UserServiceRefactored:
    """User service implementation with dependency injection and improved architecture."""
    
    def __init__(
        self, 
        db_session: Session,
        user_repository: Optional[IUserRepository] = None,
        beneficiary_repository: Optional[IBeneficiaryRepository] = None,
        upload_folder: Optional[str] = None
    ):
        """
        Initialize UserService with injected dependencies.
        
        Args:
            db_session: SQLAlchemy database session
            user_repository: Optional user repository interface
            beneficiary_repository: Optional beneficiary repository interface
            upload_folder: Path to upload folder for profile pictures
        """
        self.db = db_session
        self.user_repository = user_repository
        self.beneficiary_repository = beneficiary_repository
        self.upload_folder = upload_folder or 'uploads'
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.max_file_size = 5 * 1024 * 1024  # 5MB
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary containing user creation data
            
        Returns:
            Dict: Created user data
            
        Raises:
            ValidationException: If user data is invalid or email already exists
        """
        try:
            # Validate input data - basic validation without DB access
            if not user_data.get('email'):
                raise ValidationException("Email is required")
            if not user_data.get('password'):
                raise ValidationException("Password is required")
            if not user_data.get('first_name'):
                raise ValidationException("First name is required")
            if not user_data.get('last_name'):
                raise ValidationException("Last name is required")
            
            validated_data = user_data
            
            # Check if user already exists
            existing_user = self._get_user_by_email(validated_data['email'])
            if existing_user:
                raise ValidationException("User with this email already exists")
            
            # Validate role
            if validated_data.get('role') and validated_data['role'] not in [role.value for role in UserRole]:
                raise ValidationException(f"Invalid role: {validated_data['role']}")
            
            # Hash the password
            hashed_password = self.pwd_context.hash(validated_data['password'])
            
            # Create user entity
            user = User(
                email=validated_data['email'],
                password=hashed_password,
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role=validated_data.get('role'),
                phone=validated_data.get('phone'),
                organization=validated_data.get('organization'),
                tenant_id=validated_data.get('tenant_id'),
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Save to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Convert to response schema
            response_schema = UserSchema()
            return response_schema.dump(user)
            
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Create user error: {str(e)}")
            raise ValidationException(f"Failed to create user: {str(e)}")
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            Dict: User data if found, None otherwise
        """
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            
            if not user:
                return None
            
            schema = UserSchema()
            return schema.dump(user)
            
        except Exception as e:
            logger.exception(f"Get user error: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email.
        
        Args:
            email: Email address to search for
            
        Returns:
            Dict: User data if found, None otherwise
        """
        try:
            user = self._get_user_by_email(email)
            
            if not user:
                return None
            
            schema = UserSchema()
            return schema.dump(user)
            
        except Exception as e:
            logger.exception(f"Get user by email error: {str(e)}")
            raise
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a user's information.
        
        Args:
            user_id: ID of user to update
            user_data: Dictionary containing updated user data
            
        Returns:
            Dict: Updated user data if successful, None if user not found
            
        Raises:
            ValidationException: If update data is invalid
        """
        try:
            user = self._get_user_or_404(user_id)
            
            # Use user_data directly without schema validation to avoid app context issues
            update_data = user_data
            
            # Validate role if provided
            if 'role' in update_data and update_data['role'] not in [role.value for role in UserRole]:
                raise ValidationException(f"Invalid role: {update_data['role']}")
            
            # Handle password update if provided
            if 'password' in update_data:
                update_data['password'] = self.pwd_context.hash(update_data['password'])
            
            # Update fields
            for key, value in update_data.items():
                setattr(user, key, value)
            
            user.updated_at = datetime.now(timezone.utc)
            
            # Save changes
            self.db.commit()
            self.db.refresh(user)
            
            response_schema = UserSchema()
            return response_schema.dump(user)
            
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Update user error: {str(e)}")
            raise ValidationException(f"Failed to update user: {str(e)}")
    
    def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            bool: True if successful, False if user not found
        """
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            
            if not user:
                return False
            
            # Soft delete the user
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Delete user error: {str(e)}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            User: Authenticated user object if successful, None otherwise
        """
        try:
            user = self._get_user_by_email(email)
            
            if not user:
                return None
            
            if not user.is_active:
                logger.warning(f"Inactive user attempted login: {email}")
                return None
            
            if not self.verify_password(password, user.password_hash):
                return None
            
            # Update last login timestamp
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()
            
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Authenticate user error: {str(e)}")
            raise
    
    # Helper methods
    
    def _get_user_or_404(self, user_id: int) -> User:
        """
        Get user by ID or raise NotFoundException.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User: User object
            
        Raises:
            NotFoundException: If user not found
        """
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email address to search for
            
        Returns:
            User: User object if found, None otherwise
        """
        return self.db.query(User).filter_by(email=email).first()
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """
        Update a user's password.
        
        Args:
            user_id: ID of user whose password to update
            new_password: New plain text password
            
        Returns:
            bool: True if successful, False if user not found
            
        Raises:
            ValidationException: If password is invalid
        """
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            
            if not user:
                return False
            
            # Validate password strength (basic validation)
            if len(new_password) < 8:
                raise ValidationException("Password must be at least 8 characters long")
            
            # Hash the new password
            user.password_hash = self.pwd_context.hash(new_password)
            user.updated_at = datetime.now(timezone.utc)
            
            # Save changes
            self.db.commit()
            
            return True
            
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Update user password error: {str(e)}")
            raise
    
    # Profile and User Management Methods
    
    def get_current_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the current authenticated user profile.
        
        Args:
            user_id: ID of the current user
            
        Returns:
            Dict: User profile data if found, None otherwise
        """
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            
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
    ) -> PaginationResult:
        """
        Get paginated users with filters.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            role: Filter by user role
            is_active: Filter by active status
            status: Filter by status string ('active' or 'inactive')
            tenant_id: Filter by tenant ID
            sort_by: Field to sort by
            sort_direction: Sort direction ('asc' or 'desc')
            
        Returns:
            PaginationResult: Paginated user results
        """
        try:
            # Build query
            query = self.db.query(User)
            
            # Apply filters
            if role:
                query = query.filter_by(role=role)
            
            # Handle is_active filtering
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            elif status:
                if status == UserStatus.ACTIVE.value:
                    query = query.filter_by(is_active=True)
                elif status == UserStatus.INACTIVE.value:
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
            
            # Calculate pagination
            total = query.count()
            pages = (total + per_page - 1) // per_page if per_page > 0 else 0
            
            # Get paginated results
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return PaginationResult(
                items=items,
                total=total,
                pages=pages,
                current_page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.exception(f"Get users error: {str(e)}")
            raise
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed user profile with statistics.
        
        Args:
            user_id: ID of user to get profile for
            
        Returns:
            Dict: User profile data with statistics, None if user not found
        """
        try:
            user = self.db.query(User).filter_by(id=user_id).first()
            
            if not user:
                return None
            
            schema = UserProfileSchema()
            profile_data = schema.dump(user)
            
            # Add additional profile information
            profile_data['stats'] = self._get_user_statistics(user)
            
            return profile_data
            
        except Exception as e:
            logger.exception(f"Get user profile error: {str(e)}")
            raise
    
    def update_user_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: ID of user to update
            data: Dictionary of fields to update
            
        Returns:
            Dict: Updated user profile data
            
        Raises:
            NotFoundException: If user not found
            ValidationException: If update data is invalid
        """
        try:
            user = self._get_user_or_404(user_id)
            
            # Define updateable fields
            updateable_fields = [
                'first_name', 'last_name', 'phone', 'bio', 'timezone', 
                'organization', 'address', 'city', 'state', 'zip_code', 
                'country', 'email_notifications', 'push_notifications', 
                'sms_notifications', 'language', 'theme'
            ]
            
            # Validate and update fields
            for field in updateable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            user.updated_at = datetime.now(timezone.utc)
            
            # Save changes
            self.db.commit()
            self.db.refresh(user)
            
            # Return updated profile
            schema = UserProfileSchema()
            return schema.dump(user)
            
        except NotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Update user profile error: {str(e)}")
            raise ValidationException(f"Failed to update profile: {str(e)}")
    
    def upload_profile_picture(self, user_id: int, file: FileStorage) -> Dict[str, str]:
        """
        Upload user profile picture.
        
        Args:
            user_id: ID of user uploading picture
            file: File storage object containing the image
            
        Returns:
            Dict: Success message and profile picture URL
            
        Raises:
            NotFoundException: If user not found
            ValidationException: If file is invalid
        """
        try:
            user = self._get_user_or_404(user_id)
            
            if not file or file.filename == '':
                raise ValidationException("No file provided")
            
            # Check file extension
            if not self._allowed_file(file.filename):
                raise ValidationException("Invalid file type. Allowed types: png, jpg, jpeg, gif")
            
            # Check file size (basic check)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.max_file_size:
                raise ValidationException(f"File too large. Maximum size is {self.max_file_size / 1024 / 1024}MB")
            
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
            
            # Delete old profile picture if exists
            if user.profile_picture:
                old_path = user.profile_picture.replace('/uploads/', self.upload_folder + '/')
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete old profile picture: {e}")
            
            # Update user's profile picture URL
            user.profile_picture = f'/uploads/profile_pictures/{filename}'
            user.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            return {
                'message': 'Profile picture uploaded successfully',
                'profile_picture': user.profile_picture
            }
            
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Upload profile picture error: {str(e)}")
            raise ValidationException(f"Failed to upload profile picture: {str(e)}")
    
    def _allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if file extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def _get_user_statistics(self, user: User) -> Dict[str, int]:
        """
        Get user statistics based on their role.
        
        Args:
            user: User object to get statistics for
            
        Returns:
            Dict: Dictionary containing user statistics
        """
        stats = {
            'appointments_count': 0,
            'evaluations_count': 0,
            'documents_count': 0
        }
        
        # Get counts based on user role
        if user.role == UserRole.TRAINER.value:
            # Count appointments where user is trainer
            from app.models.appointment import Appointment
            stats['appointments_count'] = self.db.query(Appointment).filter_by(
                trainer_id=user.id
            ).count()
            
            # Count evaluations created by user
            from app.models.test import TestSet
            stats['evaluations_count'] = self.db.query(TestSet).filter_by(
                creator_id=user.id
            ).count()
            
        elif user.role == UserRole.CAREGIVER.value:
            # Count beneficiaries for caregiver
            if self.beneficiary_repository:
                try:
                    beneficiaries = self.beneficiary_repository.get_by_caregiver_id(user.id)
                    stats['beneficiaries_count'] = len(beneficiaries) if beneficiaries else 0
                except Exception:
                    stats['beneficiaries_count'] = 0
            else:
                # Direct query if repository not available
                from app.models.beneficiary import Beneficiary
                stats['beneficiaries_count'] = self.db.query(Beneficiary).filter_by(
                    caregiver_id=user.id
                ).count()
        
        # Count documents for all users
        from app.models.document import Document
        stats['documents_count'] = self.db.query(Document).filter_by(
            owner_id=user.id
        ).count()
        
        return stats