"""Refactored Program Service implementation with dependency injection."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.program import Program
from app.exceptions import NotFoundException, ValidationException
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProgramStatus(Enum):
    """Program status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProgramLevel(Enum):
    """Program level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class PaginationResult:
    """Pagination result wrapper."""
    items: List[Any]
    total: int
    pages: int
    current_page: int
    per_page: int


class ProgramServiceRefactored:
    """Program service implementation with dependency injection and improved architecture."""
    
    def __init__(
        self, 
        db_session: Session,
        realtime_emitter: Optional[Callable] = None
    ):
        """
        Initialize ProgramService with injected dependencies.
        
        Args:
            db_session: SQLAlchemy database session
            realtime_emitter: Optional function to emit real-time events
        """
        self.db = db_session
        self.realtime_emitter = realtime_emitter
    
    def create_program(self, program_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new program.
        
        Args:
            program_data: Dictionary containing program creation data
            
        Returns:
            Dict: Created program data
            
        Raises:
            ValidationException: If program data is invalid
        """
        try:
            # Validate required fields
            if not program_data.get('name'):
                raise ValidationException("Program name is required")
            if not program_data.get('tenant_id'):
                raise ValidationException("Tenant ID is required")
            
            # Validate optional fields
            if program_data.get('status') and program_data['status'] not in [s.value for s in ProgramStatus]:
                raise ValidationException(f"Invalid status: {program_data['status']}")
            
            if program_data.get('level') and program_data['level'] not in [l.value for l in ProgramLevel]:
                raise ValidationException(f"Invalid level: {program_data['level']}")
            
            # Validate numeric fields
            if program_data.get('minimum_attendance') is not None:
                if not 0 <= program_data['minimum_attendance'] <= 100:
                    raise ValidationException("Minimum attendance must be between 0 and 100")
            
            if program_data.get('passing_score') is not None:
                if not 0 <= program_data['passing_score'] <= 100:
                    raise ValidationException("Passing score must be between 0 and 100")
            
            # Create program entity
            program = Program(
                name=program_data['name'],
                tenant_id=program_data['tenant_id'],
                description=program_data.get('description'),
                code=program_data.get('code'),
                duration=program_data.get('duration'),
                level=program_data.get('level'),
                category=program_data.get('category'),
                prerequisites=program_data.get('prerequisites'),
                minimum_attendance=program_data.get('minimum_attendance', 80.0),
                passing_score=program_data.get('passing_score', 70.0),
                status=program_data.get('status', 'draft'),
                is_active=program_data.get('is_active', True),
                start_date=program_data.get('start_date'),
                end_date=program_data.get('end_date'),
                max_participants=program_data.get('max_participants'),
                created_by_id=program_data.get('created_by_id'),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Save to database
            self.db.add(program)
            self.db.commit()
            self.db.refresh(program)
            
            # Emit real-time event if emitter is available
            if self.realtime_emitter:
                try:
                    self.realtime_emitter(
                        program.tenant_id,
                        'program_created',
                        {'program': program.to_dict()}
                    )
                except Exception as e:
                    logger.warning(f"Failed to emit program_created event: {e}")
            
            return program.to_dict()
            
        except ValidationException:
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            if 'unique constraint' in str(e).lower():
                raise ValidationException("Program with this code already exists")
            raise ValidationException(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Create program error: {str(e)}")
            raise ValidationException(f"Failed to create program: {str(e)}")
    
    def get_program(self, program_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a program by ID.
        
        Args:
            program_id: Program ID to retrieve
            
        Returns:
            Dict: Program data if found, None otherwise
        """
        try:
            program = self.db.query(Program).filter_by(id=program_id).first()
            
            if not program:
                return None
            
            return program.to_dict()
            
        except Exception as e:
            logger.exception(f"Get program error: {str(e)}")
            raise
    
    def update_program(self, program_id: int, program_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a program's information.
        
        Args:
            program_id: ID of program to update
            program_data: Dictionary containing updated program data
            
        Returns:
            Dict: Updated program data if successful, None if program not found
            
        Raises:
            ValidationException: If update data is invalid
            NotFoundException: If program not found
        """
        try:
            program = self._get_program_or_404(program_id)
            
            # Validate optional fields
            if 'status' in program_data and program_data['status'] not in [s.value for s in ProgramStatus]:
                raise ValidationException(f"Invalid status: {program_data['status']}")
            
            if 'level' in program_data and program_data['level'] not in [l.value for l in ProgramLevel]:
                raise ValidationException(f"Invalid level: {program_data['level']}")
            
            # Validate numeric fields
            if 'minimum_attendance' in program_data:
                if not 0 <= program_data['minimum_attendance'] <= 100:
                    raise ValidationException("Minimum attendance must be between 0 and 100")
            
            if 'passing_score' in program_data:
                if not 0 <= program_data['passing_score'] <= 100:
                    raise ValidationException("Passing score must be between 0 and 100")
            
            # Update fields
            updateable_fields = [
                'name', 'description', 'code', 'duration', 'level', 'category',
                'prerequisites', 'minimum_attendance', 'passing_score', 'status',
                'is_active', 'start_date', 'end_date', 'max_participants'
            ]
            
            for field in updateable_fields:
                if field in program_data:
                    setattr(program, field, program_data[field])
            
            program.updated_at = datetime.now(timezone.utc)
            
            # Save changes
            self.db.commit()
            self.db.refresh(program)
            
            # Emit real-time event if emitter is available
            if self.realtime_emitter:
                try:
                    self.realtime_emitter(
                        program.tenant_id,
                        'program_updated',
                        {'program': program.to_dict()}
                    )
                except Exception as e:
                    logger.warning(f"Failed to emit program_updated event: {e}")
            
            return program.to_dict()
            
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            if 'unique constraint' in str(e).lower():
                raise ValidationException("Program with this code already exists")
            raise ValidationException(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Update program error: {str(e)}")
            raise ValidationException(f"Failed to update program: {str(e)}")
    
    def delete_program(self, program_id: int) -> bool:
        """
        Delete a program.
        
        Args:
            program_id: ID of program to delete
            
        Returns:
            bool: True if successful, False if program not found
            
        Raises:
            ValidationException: If program cannot be deleted due to dependencies
        """
        try:
            program = self.db.query(Program).filter_by(id=program_id).first()
            
            if not program:
                return False
            
            # Store tenant_id before deletion for event emission
            tenant_id = program.tenant_id
            
            # Check for dependencies
            if program.enrollments:
                raise ValidationException("Cannot delete program with active enrollments")
            
            # Delete the program
            self.db.delete(program)
            self.db.commit()
            
            # Emit real-time event if emitter is available
            if self.realtime_emitter:
                try:
                    self.realtime_emitter(
                        tenant_id,
                        'program_deleted',
                        {'program_id': program_id}
                    )
                except Exception as e:
                    logger.warning(f"Failed to emit program_deleted event: {e}")
            
            return True
            
        except ValidationException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Delete program error: {str(e)}")
            raise
    
    def list_programs(
        self,
        tenant_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        level: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = 'created_at',
        sort_direction: str = 'desc'
    ) -> PaginationResult:
        """
        Get paginated programs with filters.
        
        Args:
            tenant_id: Filter by tenant ID
            is_active: Filter by active status
            status: Filter by program status
            level: Filter by program level
            category: Filter by program category
            page: Page number (1-based)
            per_page: Items per page
            sort_by: Field to sort by
            sort_direction: Sort direction ('asc' or 'desc')
            
        Returns:
            PaginationResult: Paginated program results
        """
        try:
            # Build query
            query = self.db.query(Program)
            
            # Apply filters
            if tenant_id is not None:
                query = query.filter_by(tenant_id=tenant_id)
            
            if is_active is not None:
                query = query.filter_by(is_active=is_active)
            elif is_active is None:
                # Default to active programs only
                query = query.filter_by(is_active=True)
            
            if status:
                query = query.filter_by(status=status)
            
            if level:
                query = query.filter_by(level=level)
            
            if category:
                query = query.filter_by(category=category)
            
            # Apply sorting
            sort_attr = getattr(Program, sort_by, None)
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
            
            # Convert to dictionaries
            items_dict = [item.to_dict() for item in items]
            
            return PaginationResult(
                items=items_dict,
                total=total,
                pages=pages,
                current_page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.exception(f"List programs error: {str(e)}")
            raise
    
    def get_program_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get a program by its unique code.
        
        Args:
            code: Program code to search for
            
        Returns:
            Dict: Program data if found, None otherwise
        """
        try:
            program = self.db.query(Program).filter_by(code=code).first()
            
            if not program:
                return None
            
            return program.to_dict()
            
        except Exception as e:
            logger.exception(f"Get program by code error: {str(e)}")
            raise
    
    def get_program_statistics(self, program_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific program.
        
        Args:
            program_id: ID of program to get statistics for
            
        Returns:
            Dict: Program statistics including enrollment counts, completion rates, etc.
            
        Raises:
            NotFoundException: If program not found
        """
        try:
            program = self._get_program_or_404(program_id)
            
            # Calculate statistics
            total_enrollments = len(program.enrollments)
            active_enrollments = sum(1 for e in program.enrollments if e.status == 'active')
            completed_enrollments = sum(1 for e in program.enrollments if e.status == 'completed')
            
            completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
            
            # Calculate average scores and attendance
            avg_score = 0
            avg_attendance = 0
            if completed_enrollments > 0:
                completed = [e for e in program.enrollments if e.status == 'completed']
                avg_score = sum(e.overall_score for e in completed) / len(completed)
                avg_attendance = sum(e.attendance_rate for e in completed) / len(completed)
            
            return {
                'program_id': program.id,
                'program_name': program.name,
                'total_enrollments': total_enrollments,
                'active_enrollments': active_enrollments,
                'completed_enrollments': completed_enrollments,
                'completion_rate': round(completion_rate, 2),
                'average_score': round(avg_score, 2),
                'average_attendance': round(avg_attendance, 2),
                'module_count': len(program.modules),
                'session_count': len(program.sessions),
                'status': program.status,
                'duration_days': program.duration,
                'duration_weeks': round(program.duration / 7.0, 2) if program.duration else None
            }
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Get program statistics error: {str(e)}")
            raise
    
    def archive_program(self, program_id: int) -> Dict[str, Any]:
        """
        Archive a program by setting its status to archived.
        
        Args:
            program_id: ID of program to archive
            
        Returns:
            Dict: Updated program data
            
        Raises:
            NotFoundException: If program not found
            ValidationException: If program cannot be archived
        """
        try:
            program = self._get_program_or_404(program_id)
            
            # Check if program can be archived
            if program.status == ProgramStatus.ARCHIVED.value:
                raise ValidationException("Program is already archived")
            
            # Check for active enrollments
            active_enrollments = sum(1 for e in program.enrollments if e.status == 'active')
            if active_enrollments > 0:
                raise ValidationException(f"Cannot archive program with {active_enrollments} active enrollments")
            
            # Archive the program
            program.status = ProgramStatus.ARCHIVED.value
            program.is_active = False
            program.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(program)
            
            # Emit real-time event if emitter is available
            if self.realtime_emitter:
                try:
                    self.realtime_emitter(
                        program.tenant_id,
                        'program_archived',
                        {'program': program.to_dict()}
                    )
                except Exception as e:
                    logger.warning(f"Failed to emit program_archived event: {e}")
            
            return program.to_dict()
            
        except (NotFoundException, ValidationException):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Archive program error: {str(e)}")
            raise ValidationException(f"Failed to archive program: {str(e)}")
    
    def search_programs(
        self,
        search_term: str,
        tenant_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search programs by name, code, or description.
        
        Args:
            search_term: Term to search for
            tenant_id: Optional tenant ID filter
            limit: Maximum number of results to return
            
        Returns:
            List[Dict]: List of matching programs
        """
        try:
            query = self.db.query(Program).filter_by(is_active=True)
            
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            
            # Search in name, code, and description
            search_pattern = f"%{search_term}%"
            query = query.filter(
                (Program.name.ilike(search_pattern)) |
                (Program.code.ilike(search_pattern)) |
                (Program.description.ilike(search_pattern))
            )
            
            # Order by relevance (name matches first, then code, then description)
            query = query.order_by(
                Program.name.ilike(search_pattern).desc(),
                Program.code.ilike(search_pattern).desc(),
                Program.created_at.desc()
            )
            
            programs = query.limit(limit).all()
            
            return [program.to_dict() for program in programs]
            
        except Exception as e:
            logger.exception(f"Search programs error: {str(e)}")
            raise
    
    # Helper methods
    
    def _get_program_or_404(self, program_id: int) -> Program:
        """
        Get program by ID or raise NotFoundException.
        
        Args:
            program_id: Program ID to retrieve
            
        Returns:
            Program: Program object
            
        Raises:
            NotFoundException: If program not found
        """
        program = self.db.query(Program).filter_by(id=program_id).first()
        if not program:
            raise NotFoundException(f"Program with ID {program_id} not found")
        return program