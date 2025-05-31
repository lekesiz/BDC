"""Refactored Beneficiary Service with dependency injection and improved architecture."""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session, aliased
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.models import User, Beneficiary, Note, Appointment, Document
from app.exceptions import NotFoundException, ValidationException, ForbiddenException

if TYPE_CHECKING:
    from app.services.interfaces.user_repository_interface import IUserRepository
    from app.services.interfaces.beneficiary_repository_interface import IBeneficiaryRepository


class BeneficiaryStatus(Enum):
    """Beneficiary status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class NoteType(Enum):
    """Note type enumeration."""
    GENERAL = "general"
    PROGRESS = "progress"
    CONCERN = "concern"
    GOAL = "goal"


class AppointmentStatus(Enum):
    """Appointment status enumeration."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


@dataclass
class PaginationResult:
    """Pagination result wrapper."""
    items: List[Any]
    total: int
    pages: int
    current_page: int
    per_page: int


@dataclass
class BeneficiaryData:
    """Data class for beneficiary information."""
    id: int
    user_id: int
    trainer_id: Optional[int]
    tenant_id: int
    first_name: str
    last_name: str
    email: str
    gender: Optional[str]
    birth_date: Optional[datetime]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    state: Optional[str]
    country: Optional[str]
    nationality: Optional[str]
    native_language: Optional[str]
    profession: Optional[str]
    company: Optional[str]
    company_size: Optional[str]
    years_of_experience: Optional[int]
    education_level: Optional[str]
    category: Optional[str]
    bio: Optional[str]
    goals: Optional[str]
    notes: Optional[str]
    referral_source: Optional[str]
    custom_fields: Optional[Dict[str, Any]]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BeneficiaryServiceRefactored:
    """Refactored beneficiary service with dependency injection."""
    
    def __init__(
        self, 
        db_session: Session,
        upload_folder: Optional[str] = None,
        user_repository: Optional['IUserRepository'] = None,
        beneficiary_repository: Optional['IBeneficiaryRepository'] = None
    ):
        """
        Initialize BeneficiaryService with injected dependencies.
        
        Args:
            db_session: SQLAlchemy database session
            upload_folder: Path to upload folder for documents
            user_repository: Optional user repository interface
            beneficiary_repository: Optional beneficiary repository interface
        """
        self.db = db_session
        self.upload_folder = upload_folder or 'uploads'
        self.user_repository = user_repository
        self.beneficiary_repository = beneficiary_repository
    
    def get_beneficiaries(
        self,
        tenant_id: Optional[int] = None,
        trainer_id: Optional[int] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by: Optional[str] = None,
        sort_dir: Optional[str] = None
    ) -> PaginationResult:
        """
        Get beneficiaries with optional filtering and pagination.
        
        Args:
            tenant_id: Filter by tenant ID
            trainer_id: Filter by trainer ID
            status: Filter by status
            query: Search query for name or email
            page: Page number (default: 1)
            per_page: Results per page (default: 10)
            sort_by: Field to sort by
            sort_dir: Sort direction ('asc' or 'desc')
        
        Returns:
            PaginationResult: Paginated beneficiaries with metadata
            
        Raises:
            ValidationException: If parameters are invalid
        """
        # Validate pagination parameters
        if page < 1:
            raise ValidationException("Page number must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValidationException("Per page must be between 1 and 100")
        
        # Build query
        beneficiary_query = self.db.query(Beneficiary)
        
        # Apply filters
        if tenant_id:
            beneficiary_query = beneficiary_query.filter_by(tenant_id=tenant_id)
        
        if trainer_id:
            beneficiary_query = beneficiary_query.filter_by(trainer_id=trainer_id)
        
        if status:
            if status not in [s.value for s in BeneficiaryStatus]:
                raise ValidationException(f"Invalid status: {status}")
            beneficiary_query = beneficiary_query.filter_by(status=status)
        
        if query:
            # Join with User table to search in first_name, last_name and email
            beneficiary_user = aliased(User)
            beneficiary_query = beneficiary_query.join(
                beneficiary_user, 
                Beneficiary.user_id == beneficiary_user.id
            ).filter(
                or_(
                    beneficiary_user.first_name.ilike(f'%{query}%'),
                    beneficiary_user.last_name.ilike(f'%{query}%'),
                    beneficiary_user.email.ilike(f'%{query}%')
                )
            )
        
        # Apply sorting
        if sort_by:
            valid_sort_fields = ['created_at', 'updated_at', 'first_name', 'last_name', 'email']
            if sort_by not in valid_sort_fields:
                raise ValidationException(f"Invalid sort field: {sort_by}")
            
            # Handle user fields separately
            if sort_by in ['first_name', 'last_name', 'email']:
                if 'beneficiary_user' not in locals():
                    beneficiary_user = aliased(User)
                    beneficiary_query = beneficiary_query.join(
                        beneficiary_user,
                        Beneficiary.user_id == beneficiary_user.id
                    )
                sort_column = getattr(beneficiary_user, sort_by)
            else:
                sort_column = getattr(Beneficiary, sort_by)
            
            if sort_dir == 'desc':
                beneficiary_query = beneficiary_query.order_by(sort_column.desc())
            else:
                beneficiary_query = beneficiary_query.order_by(sort_column.asc())
        else:
            # Default sorting
            beneficiary_query = beneficiary_query.order_by(Beneficiary.created_at.desc())
        
        # Calculate pagination
        total = beneficiary_query.count()
        pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated results
        items = beneficiary_query.offset(offset).limit(per_page).all()
        
        # Convert to data objects
        beneficiary_data = [self._serialize_beneficiary(b) for b in items]
        
        return PaginationResult(
            items=beneficiary_data,
            total=total,
            pages=pages,
            current_page=page,
            per_page=per_page
        )
    
    def get_beneficiary(self, beneficiary_id: int) -> Dict[str, Any]:
        """
        Get a beneficiary by ID.
        
        Args:
            beneficiary_id: Beneficiary ID
        
        Returns:
            Dict: Beneficiary data
            
        Raises:
            NotFoundException: If beneficiary not found
        """
        beneficiary = self.db.query(Beneficiary).filter_by(id=beneficiary_id).first()
        if not beneficiary:
            raise NotFoundException(f"Beneficiary {beneficiary_id} not found")
        
        return self._serialize_beneficiary(beneficiary)
    
    def create_beneficiary(
        self,
        user_data: Dict[str, Any],
        beneficiary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new beneficiary with a user account.
        
        Args:
            user_data: User account data
            beneficiary_data: Beneficiary profile data
        
        Returns:
            Dict: Created beneficiary data
            
        Raises:
            ValidationException: If data is invalid or user already exists
        """
        try:
            # Validate required user data
            if not user_data.get('email'):
                raise ValidationException("Email is required")
            if not user_data.get('first_name'):
                raise ValidationException("First name is required")
            if not user_data.get('last_name'):
                raise ValidationException("Last name is required")
            
            # Validate required beneficiary data
            if not beneficiary_data.get('tenant_id'):
                raise ValidationException("Tenant ID is required")
            
            # Check if user already exists
            existing_user = self.db.query(User).filter_by(email=user_data['email']).first()
            
            if existing_user:
                # Check if user already has a beneficiary profile
                existing_beneficiary = self.db.query(Beneficiary).filter_by(
                    user_id=existing_user.id
                ).first()
                if existing_beneficiary:
                    raise ValidationException(
                        f"User {user_data['email']} already has a beneficiary profile"
                    )
                
                # Use existing user
                user = existing_user
                # Update user info if provided
                if user_data.get('first_name'):
                    user.first_name = user_data['first_name']
                if user_data.get('last_name'):
                    user.last_name = user_data['last_name']
            else:
                # Create new user
                user = User(
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role='student',
                    is_active=True,
                    tenant_id=beneficiary_data['tenant_id']
                )
                
                # Set password if provided
                if user_data.get('password'):
                    user.set_password(user_data['password'])
                
                self.db.add(user)
                self.db.flush()  # Get user ID without committing
            
            # Create beneficiary
            beneficiary = Beneficiary(
                user_id=user.id,
                trainer_id=beneficiary_data.get('trainer_id'),
                tenant_id=beneficiary_data['tenant_id'],
                gender=beneficiary_data.get('gender'),
                birth_date=self._parse_date(beneficiary_data.get('birth_date')),
                phone=beneficiary_data.get('phone'),
                address=beneficiary_data.get('address'),
                city=beneficiary_data.get('city'),
                postal_code=beneficiary_data.get('postal_code'),
                state=beneficiary_data.get('state'),
                country=beneficiary_data.get('country'),
                nationality=beneficiary_data.get('nationality'),
                native_language=beneficiary_data.get('native_language'),
                profession=beneficiary_data.get('profession'),
                company=beneficiary_data.get('company'),
                company_size=beneficiary_data.get('company_size'),
                years_of_experience=beneficiary_data.get('years_of_experience'),
                education_level=beneficiary_data.get('education_level'),
                category=beneficiary_data.get('category'),
                bio=beneficiary_data.get('bio'),
                goals=beneficiary_data.get('goals'),
                notes=beneficiary_data.get('notes'),
                referral_source=beneficiary_data.get('referral_source'),
                custom_fields=beneficiary_data.get('custom_fields'),
                status=beneficiary_data.get('status', BeneficiaryStatus.ACTIVE.value),
                is_active=True
            )
            
            self.db.add(beneficiary)
            self.db.commit()
            self.db.refresh(beneficiary)
            
            return self._serialize_beneficiary(beneficiary)
        
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error creating beneficiary: {str(e)}")
    
    def update_beneficiary(
        self,
        beneficiary_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a beneficiary.
        
        Args:
            beneficiary_id: Beneficiary ID
            data: Data to update
        
        Returns:
            Dict: Updated beneficiary data
            
        Raises:
            NotFoundException: If beneficiary not found
            ValidationException: If data is invalid
        """
        try:
            beneficiary = self.db.query(Beneficiary).filter_by(id=beneficiary_id).first()
            if not beneficiary:
                raise NotFoundException(f"Beneficiary {beneficiary_id} not found")
            
            # Separate user fields from beneficiary fields
            user_fields = ['first_name', 'last_name', 'email']
            user_data = {}
            beneficiary_data = {}
            
            for key, value in data.items():
                if key in user_fields:
                    user_data[key] = value
                else:
                    beneficiary_data[key] = value
            
            # Update user if needed
            if user_data and beneficiary.user:
                for key, value in user_data.items():
                    if hasattr(beneficiary.user, key):
                        setattr(beneficiary.user, key, value)
                beneficiary.user.updated_at = datetime.now(timezone.utc)
            
            # Update beneficiary attributes
            for key, value in beneficiary_data.items():
                if hasattr(beneficiary, key):
                    # Handle special cases
                    if key == 'birth_date':
                        value = self._parse_date(value)
                    elif key == 'status' and value not in [s.value for s in BeneficiaryStatus]:
                        raise ValidationException(f"Invalid status: {value}")
                    
                    setattr(beneficiary, key, value)
            
            beneficiary.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(beneficiary)
            
            return self._serialize_beneficiary(beneficiary)
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error updating beneficiary: {str(e)}")
    
    def delete_beneficiary(self, beneficiary_id: int) -> Dict[str, str]:
        """
        Delete a beneficiary and associated data.
        
        Args:
            beneficiary_id: Beneficiary ID
        
        Returns:
            Dict: Success message
            
        Raises:
            NotFoundException: If beneficiary not found
        """
        try:
            beneficiary = self.db.query(Beneficiary).filter_by(id=beneficiary_id).first()
            if not beneficiary:
                raise NotFoundException(f"Beneficiary {beneficiary_id} not found")
            
            # Delete associated data
            self.db.query(Note).filter_by(beneficiary_id=beneficiary_id).delete()
            self.db.query(Appointment).filter_by(beneficiary_id=beneficiary_id).delete()
            
            # Delete documents with files
            documents = self.db.query(Document).filter_by(beneficiary_id=beneficiary_id).all()
            for document in documents:
                file_path = os.path.join(self.upload_folder, document.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            self.db.query(Document).filter_by(beneficiary_id=beneficiary_id).delete()
            
            # Delete beneficiary
            self.db.delete(beneficiary)
            
            # Deactivate associated user
            if beneficiary.user:
                beneficiary.user.is_active = False
                beneficiary.user.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            return {"message": "Beneficiary deleted successfully"}
        
        except NotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error deleting beneficiary: {str(e)}")
    
    def assign_trainer(
        self,
        beneficiary_id: int,
        trainer_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Assign or unassign a trainer to a beneficiary.
        
        Args:
            beneficiary_id: Beneficiary ID
            trainer_id: Trainer ID (None to unassign)
        
        Returns:
            Dict: Updated beneficiary data
            
        Raises:
            NotFoundException: If beneficiary or trainer not found
            ValidationException: If trainer doesn't have appropriate role
        """
        try:
            beneficiary = self.db.query(Beneficiary).filter_by(id=beneficiary_id).first()
            if not beneficiary:
                raise NotFoundException(f"Beneficiary {beneficiary_id} not found")
            
            # Verify trainer exists and has appropriate role
            if trainer_id:
                trainer = self.db.query(User).filter_by(id=trainer_id).first()
                if not trainer:
                    raise NotFoundException(f"Trainer {trainer_id} not found")
                if trainer.role not in ['trainer', 'super_admin', 'tenant_admin']:
                    raise ValidationException("User does not have trainer permissions")
            
            beneficiary.trainer_id = trainer_id
            beneficiary.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(beneficiary)
            
            return self._serialize_beneficiary(beneficiary)
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error assigning trainer: {str(e)}")
    
    # Private helper methods
    
    def _serialize_beneficiary(self, beneficiary: Beneficiary) -> Dict[str, Any]:
        """Convert beneficiary model to dictionary."""
        data = {
            'id': beneficiary.id,
            'user_id': beneficiary.user_id,
            'trainer_id': beneficiary.trainer_id,
            'tenant_id': beneficiary.tenant_id,
            'gender': beneficiary.gender,
            'birth_date': beneficiary.birth_date.isoformat() if beneficiary.birth_date else None,
            'phone': beneficiary.phone,
            'address': beneficiary.address,
            'city': beneficiary.city,
            'postal_code': beneficiary.postal_code,
            'state': beneficiary.state,
            'country': beneficiary.country,
            'nationality': beneficiary.nationality,
            'native_language': beneficiary.native_language,
            'profession': beneficiary.profession,
            'company': beneficiary.company,
            'company_size': beneficiary.company_size,
            'years_of_experience': beneficiary.years_of_experience,
            'education_level': beneficiary.education_level,
            'category': beneficiary.category,
            'bio': beneficiary.bio,
            'goals': beneficiary.goals,
            'notes': beneficiary.notes,
            'referral_source': beneficiary.referral_source,
            'custom_fields': beneficiary.custom_fields,
            'status': beneficiary.status,
            'is_active': beneficiary.is_active,
            'created_at': beneficiary.created_at.isoformat(),
            'updated_at': beneficiary.updated_at.isoformat()
        }
        
        # Add user information
        if beneficiary.user:
            data['user'] = {
                'id': beneficiary.user.id,
                'email': beneficiary.user.email,
                'first_name': beneficiary.user.first_name,
                'last_name': beneficiary.user.last_name,
                'role': beneficiary.user.role,
                'is_active': beneficiary.user.is_active
            }
        
        # Add trainer information
        if beneficiary.trainer:
            data['trainer'] = {
                'id': beneficiary.trainer.id,
                'email': beneficiary.trainer.email,
                'first_name': beneficiary.trainer.first_name,
                'last_name': beneficiary.trainer.last_name
            }
        
        return data
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats."""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try date only format
                    return datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    raise ValidationException(f"Invalid date format: {date_value}")
        
        raise ValidationException(f"Invalid date type: {type(date_value)}")


class NoteServiceRefactored:
    """Refactored note service with dependency injection."""
    
    def __init__(self, db_session: Session):
        """
        Initialize NoteService with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_notes(
        self,
        beneficiary_id: int,
        user_id: Optional[int] = None,
        note_type: Optional[str] = None,
        is_private: Optional[bool] = None,
        page: int = 1,
        per_page: int = 10
    ) -> PaginationResult:
        """
        Get notes for a beneficiary with pagination.
        
        Args:
            beneficiary_id: Beneficiary ID
            user_id: Filter by user ID
            note_type: Filter by note type
            is_private: Filter by privacy status
            page: Page number
            per_page: Results per page
        
        Returns:
            PaginationResult: Paginated notes
        """
        # Validate pagination
        if page < 1:
            raise ValidationException("Page number must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValidationException("Per page must be between 1 and 100")
        
        # Build query
        note_query = self.db.query(Note).filter_by(beneficiary_id=beneficiary_id)
        
        # Apply filters
        if user_id:
            note_query = note_query.filter_by(user_id=user_id)
        
        if note_type:
            if note_type not in [t.value for t in NoteType]:
                raise ValidationException(f"Invalid note type: {note_type}")
            note_query = note_query.filter_by(type=note_type)
        
        if is_private is not None:
            note_query = note_query.filter_by(is_private=is_private)
        
        # Order by created_at descending
        note_query = note_query.order_by(Note.created_at.desc())
        
        # Calculate pagination
        total = note_query.count()
        pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated results
        items = note_query.offset(offset).limit(per_page).all()
        
        # Convert to dictionaries
        notes_data = [self._serialize_note(note) for note in items]
        
        return PaginationResult(
            items=notes_data,
            total=total,
            pages=pages,
            current_page=page,
            per_page=per_page
        )
    
    def get_note(self, note_id: int) -> Dict[str, Any]:
        """
        Get a note by ID.
        
        Args:
            note_id: Note ID
        
        Returns:
            Dict: Note data
            
        Raises:
            NotFoundException: If note not found
        """
        note = self.db.query(Note).filter_by(id=note_id).first()
        if not note:
            raise NotFoundException(f"Note {note_id} not found")
        
        return self._serialize_note(note)
    
    def create_note(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new note.
        
        Args:
            user_id: User ID creating the note
            data: Note data
        
        Returns:
            Dict: Created note data
            
        Raises:
            ValidationException: If data is invalid
        """
        try:
            # Validate required fields
            if not data.get('beneficiary_id'):
                raise ValidationException("Beneficiary ID is required")
            if not data.get('content'):
                raise ValidationException("Note content is required")
            
            # Validate note type
            note_type = data.get('type', NoteType.GENERAL.value)
            if note_type not in [t.value for t in NoteType]:
                raise ValidationException(f"Invalid note type: {note_type}")
            
            note = Note(
                beneficiary_id=data['beneficiary_id'],
                user_id=user_id,
                content=data['content'],
                type=note_type,
                is_private=data.get('is_private', False)
            )
            
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)
            
            return self._serialize_note(note)
        
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error creating note: {str(e)}")
    
    def update_note(self, note_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a note.
        
        Args:
            note_id: Note ID
            data: Data to update
        
        Returns:
            Dict: Updated note data
            
        Raises:
            NotFoundException: If note not found
            ValidationException: If data is invalid
        """
        try:
            note = self.db.query(Note).filter_by(id=note_id).first()
            if not note:
                raise NotFoundException(f"Note {note_id} not found")
            
            # Update allowed fields
            if 'content' in data:
                note.content = data['content']
            if 'type' in data:
                if data['type'] not in [t.value for t in NoteType]:
                    raise ValidationException(f"Invalid note type: {data['type']}")
                note.type = data['type']
            if 'is_private' in data:
                note.is_private = bool(data['is_private'])
            
            note.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(note)
            
            return self._serialize_note(note)
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error updating note: {str(e)}")
    
    def delete_note(self, note_id: int) -> Dict[str, str]:
        """
        Delete a note.
        
        Args:
            note_id: Note ID
        
        Returns:
            Dict: Success message
            
        Raises:
            NotFoundException: If note not found
        """
        try:
            note = self.db.query(Note).filter_by(id=note_id).first()
            if not note:
                raise NotFoundException(f"Note {note_id} not found")
            
            self.db.delete(note)
            self.db.commit()
            
            return {"message": "Note deleted successfully"}
        
        except NotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error deleting note: {str(e)}")
    
    def _serialize_note(self, note: Note) -> Dict[str, Any]:
        """Convert note model to dictionary."""
        return {
            'id': note.id,
            'beneficiary_id': note.beneficiary_id,
            'user_id': note.user_id,
            'content': note.content,
            'type': note.type,
            'is_private': note.is_private,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'user': {
                'id': note.user.id,
                'first_name': note.user.first_name,
                'last_name': note.user.last_name,
                'email': note.user.email
            } if note.user else None
        }


class AppointmentServiceRefactored:
    """Refactored appointment service with dependency injection."""
    
    def __init__(self, db_session: Session):
        """
        Initialize AppointmentService with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_appointments(
        self,
        user_id: Optional[int] = None,
        beneficiary_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 10
    ) -> PaginationResult:
        """
        Get appointments with optional filtering and pagination.
        
        Args:
            user_id: Filter by user ID
            beneficiary_id: Filter by beneficiary ID
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number
            per_page: Results per page
        
        Returns:
            PaginationResult: Paginated appointments
        """
        # Validate pagination
        if page < 1:
            raise ValidationException("Page number must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValidationException("Per page must be between 1 and 100")
        
        # Build query
        appointment_query = self.db.query(Appointment)
        
        # Apply filters
        if user_id:
            appointment_query = appointment_query.filter_by(user_id=user_id)
        
        if beneficiary_id:
            appointment_query = appointment_query.filter_by(beneficiary_id=beneficiary_id)
        
        if status:
            if status not in [s.value for s in AppointmentStatus]:
                raise ValidationException(f"Invalid status: {status}")
            appointment_query = appointment_query.filter_by(status=status)
        
        if start_date:
            appointment_query = appointment_query.filter(Appointment.start_time >= start_date)
        
        if end_date:
            appointment_query = appointment_query.filter(Appointment.start_time <= end_date)
        
        # Order by start_time ascending
        appointment_query = appointment_query.order_by(Appointment.start_time.asc())
        
        # Calculate pagination
        total = appointment_query.count()
        pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated results
        items = appointment_query.offset(offset).limit(per_page).all()
        
        # Convert to dictionaries
        appointments_data = [self._serialize_appointment(apt) for apt in items]
        
        return PaginationResult(
            items=appointments_data,
            total=total,
            pages=pages,
            current_page=page,
            per_page=per_page
        )
    
    def get_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """
        Get an appointment by ID.
        
        Args:
            appointment_id: Appointment ID
        
        Returns:
            Dict: Appointment data
            
        Raises:
            NotFoundException: If appointment not found
        """
        appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            raise NotFoundException(f"Appointment {appointment_id} not found")
        
        return self._serialize_appointment(appointment)
    
    def create_appointment(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new appointment.
        
        Args:
            user_id: User ID creating the appointment
            data: Appointment data
        
        Returns:
            Dict: Created appointment data
            
        Raises:
            ValidationException: If data is invalid
        """
        try:
            # Validate required fields
            required_fields = ['beneficiary_id', 'title', 'start_time', 'end_time']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationException(f"{field} is required")
            
            # Parse dates
            start_time = self._parse_datetime(data['start_time'])
            end_time = self._parse_datetime(data['end_time'])
            
            # Validate dates
            if start_time >= end_time:
                raise ValidationException("Start time must be before end time")
            
            appointment = Appointment(
                beneficiary_id=data['beneficiary_id'],
                user_id=user_id,
                title=data['title'],
                description=data.get('description'),
                start_time=start_time,
                end_time=end_time,
                location=data.get('location', 'Online'),
                status=AppointmentStatus.SCHEDULED.value
            )
            
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            return self._serialize_appointment(appointment)
        
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error creating appointment: {str(e)}")
    
    def update_appointment(self, appointment_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an appointment.
        
        Args:
            appointment_id: Appointment ID
            data: Data to update
        
        Returns:
            Dict: Updated appointment data
            
        Raises:
            NotFoundException: If appointment not found
            ValidationException: If data is invalid
        """
        try:
            appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
            if not appointment:
                raise NotFoundException(f"Appointment {appointment_id} not found")
            
            # Update allowed fields
            if 'title' in data:
                appointment.title = data['title']
            if 'description' in data:
                appointment.description = data['description']
            if 'location' in data:
                appointment.location = data['location']
            if 'status' in data:
                if data['status'] not in [s.value for s in AppointmentStatus]:
                    raise ValidationException(f"Invalid status: {data['status']}")
                appointment.status = data['status']
            
            # Update dates if provided
            if 'start_time' in data:
                appointment.start_time = self._parse_datetime(data['start_time'])
            if 'end_time' in data:
                appointment.end_time = self._parse_datetime(data['end_time'])
            
            # Validate dates
            if appointment.start_time >= appointment.end_time:
                raise ValidationException("Start time must be before end time")
            
            appointment.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(appointment)
            
            return self._serialize_appointment(appointment)
        
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error updating appointment: {str(e)}")
    
    def delete_appointment(self, appointment_id: int) -> Dict[str, str]:
        """
        Delete an appointment.
        
        Args:
            appointment_id: Appointment ID
        
        Returns:
            Dict: Success message
            
        Raises:
            NotFoundException: If appointment not found
        """
        try:
            appointment = self.db.query(Appointment).filter_by(id=appointment_id).first()
            if not appointment:
                raise NotFoundException(f"Appointment {appointment_id} not found")
            
            self.db.delete(appointment)
            self.db.commit()
            
            return {"message": "Appointment deleted successfully"}
        
        except NotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error deleting appointment: {str(e)}")
    
    def _serialize_appointment(self, appointment: Appointment) -> Dict[str, Any]:
        """Convert appointment model to dictionary."""
        return {
            'id': appointment.id,
            'beneficiary_id': appointment.beneficiary_id,
            'user_id': appointment.user_id,
            'title': appointment.title,
            'description': appointment.description,
            'start_time': appointment.start_time.isoformat(),
            'end_time': appointment.end_time.isoformat(),
            'location': appointment.location,
            'status': appointment.status,
            'created_at': appointment.created_at.isoformat(),
            'updated_at': appointment.updated_at.isoformat(),
            'user': {
                'id': appointment.user.id,
                'first_name': appointment.user.first_name,
                'last_name': appointment.user.last_name,
                'email': appointment.user.email
            } if appointment.user else None,
            'beneficiary': {
                'id': appointment.beneficiary.id,
                'user': {
                    'first_name': appointment.beneficiary.user.first_name,
                    'last_name': appointment.beneficiary.user.last_name,
                    'email': appointment.beneficiary.user.email
                } if appointment.beneficiary.user else None
            } if appointment.beneficiary else None
        }
    
    def _parse_datetime(self, datetime_value: Any) -> datetime:
        """Parse datetime from various formats."""
        if isinstance(datetime_value, datetime):
            return datetime_value
        
        if isinstance(datetime_value, str):
            try:
                # Try ISO format with timezone
                return datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try without timezone
                    return datetime.fromisoformat(datetime_value)
                except ValueError:
                    raise ValidationException(f"Invalid datetime format: {datetime_value}")
        
        raise ValidationException(f"Invalid datetime type: {type(datetime_value)}")


class DocumentServiceRefactored:
    """Refactored document service with dependency injection."""
    
    def __init__(self, db_session: Session, upload_folder: Optional[str] = None):
        """
        Initialize DocumentService with database session.
        
        Args:
            db_session: SQLAlchemy database session
            upload_folder: Path to upload folder
        """
        self.db = db_session
        self.upload_folder = upload_folder or 'uploads'
        self.allowed_extensions = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def get_documents(
        self,
        beneficiary_id: Optional[int] = None,
        user_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10
    ) -> PaginationResult:
        """
        Get documents with optional filtering and pagination.
        
        Args:
            beneficiary_id: Filter by beneficiary ID
            user_id: Filter by user ID
            page: Page number
            per_page: Results per page
        
        Returns:
            PaginationResult: Paginated documents
        """
        # Validate pagination
        if page < 1:
            raise ValidationException("Page number must be at least 1")
        if per_page < 1 or per_page > 100:
            raise ValidationException("Per page must be between 1 and 100")
        
        # Build query
        document_query = self.db.query(Document)
        
        # Apply filters
        if beneficiary_id:
            document_query = document_query.filter_by(beneficiary_id=beneficiary_id)
        
        if user_id:
            document_query = document_query.filter_by(user_id=user_id)
        
        # Order by created_at descending
        document_query = document_query.order_by(Document.created_at.desc())
        
        # Calculate pagination
        total = document_query.count()
        pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated results
        items = document_query.offset(offset).limit(per_page).all()
        
        # Convert to dictionaries
        documents_data = [self._serialize_document(doc) for doc in items]
        
        return PaginationResult(
            items=documents_data,
            total=total,
            pages=pages,
            current_page=page,
            per_page=per_page
        )
    
    def get_document(self, document_id: int) -> Dict[str, Any]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Dict: Document data
            
        Raises:
            NotFoundException: If document not found
        """
        document = self.db.query(Document).filter_by(id=document_id).first()
        if not document:
            raise NotFoundException(f"Document {document_id} not found")
        
        return self._serialize_document(document)
    
    def create_document(
        self,
        user_id: int,
        file: FileStorage,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new document.
        
        Args:
            user_id: User ID uploading the document
            file: Uploaded file
            data: Document metadata
        
        Returns:
            Dict: Created document data
            
        Raises:
            ValidationException: If data is invalid or file upload fails
        """
        try:
            # Validate required fields
            if not data.get('beneficiary_id'):
                raise ValidationException("Beneficiary ID is required")
            if not data.get('title'):
                raise ValidationException("Document title is required")
            
            # Validate file
            if not file or file.filename == '':
                raise ValidationException("No file provided")
            
            # Check file extension
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if file_extension not in self.allowed_extensions:
                raise ValidationException(f"File type '{file_extension}' not allowed")
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join('documents', unique_filename)
            full_path = os.path.join(self.upload_folder, 'documents')
            
            # Ensure directory exists
            os.makedirs(full_path, exist_ok=True)
            
            # Save file
            file_full_path = os.path.join(full_path, unique_filename)
            file.save(file_full_path)
            
            # Check file size
            file_size = os.path.getsize(file_full_path)
            if file_size > self.max_file_size:
                os.remove(file_full_path)
                raise ValidationException(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
            
            # Create document record
            document = Document(
                beneficiary_id=data['beneficiary_id'],
                user_id=user_id,
                title=data['title'],
                description=data.get('description'),
                file_path=file_path,
                file_type=file_extension,
                file_size=file_size,
                is_private=data.get('is_private', False)
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            return self._serialize_document(document)
        
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            # Clean up file if database operation failed
            if 'file_full_path' in locals() and os.path.exists(file_full_path):
                os.remove(file_full_path)
            raise ValidationException(f"Error creating document: {str(e)}")
    
    def update_document(self, document_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a document's metadata.
        
        Args:
            document_id: Document ID
            data: Data to update
        
        Returns:
            Dict: Updated document data
            
        Raises:
            NotFoundException: If document not found
            ValidationException: If data is invalid
        """
        try:
            document = self.db.query(Document).filter_by(id=document_id).first()
            if not document:
                raise NotFoundException(f"Document {document_id} not found")
            
            # Update allowed fields
            if 'title' in data:
                document.title = data['title']
            if 'description' in data:
                document.description = data['description']
            if 'is_private' in data:
                document.is_private = bool(data['is_private'])
            
            document.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(document)
            
            return self._serialize_document(document)
        
        except NotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error updating document: {str(e)}")
    
    def delete_document(self, document_id: int) -> Dict[str, str]:
        """
        Delete a document and its file.
        
        Args:
            document_id: Document ID
        
        Returns:
            Dict: Success message
            
        Raises:
            NotFoundException: If document not found
        """
        try:
            document = self.db.query(Document).filter_by(id=document_id).first()
            if not document:
                raise NotFoundException(f"Document {document_id} not found")
            
            # Delete file
            file_path = os.path.join(self.upload_folder, document.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete document record
            self.db.delete(document)
            self.db.commit()
            
            return {"message": "Document deleted successfully"}
        
        except NotFoundException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise ValidationException(f"Error deleting document: {str(e)}")
    
    def _serialize_document(self, document: Document) -> Dict[str, Any]:
        """Convert document model to dictionary."""
        return {
            'id': document.id,
            'beneficiary_id': document.beneficiary_id,
            'user_id': document.user_id,
            'title': document.title,
            'description': document.description,
            'file_path': document.file_path,
            'file_type': document.file_type,
            'file_size': document.file_size,
            'is_private': document.is_private,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'user': {
                'id': document.user.id,
                'first_name': document.user.first_name,
                'last_name': document.user.last_name,
                'email': document.user.email
            } if document.user else None
        }