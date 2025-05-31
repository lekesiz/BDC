"""Improved program service with dependency injection."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from app.services.interfaces.program_service_interface import IProgramService
from app.repositories.interfaces.program_repository_interface import IProgramRepository
from app.extensions import db

logger = logging.getLogger(__name__)


class ImprovedProgramService(IProgramService):
    """Improved program service with dependency injection."""
    
    def __init__(self, program_repository: IProgramRepository, db_session: Optional[Session] = None):
        """Initialize service with dependencies.
        
        Args:
            program_repository: Program repository implementation
            db_session: Database session (optional)
        """
        self.program_repository = program_repository
        self.db_session = db_session or db.session
    
    def create_program(self, name: str, description: str, trainer_id: int,
                      tenant_id: Optional[int] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new program."""
        try:
            program_data = {
                'name': name,
                'description': description,
                'trainer_id': trainer_id,
                'status': 'active',
                'is_active': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            if tenant_id:
                program_data['tenant_id'] = tenant_id
            
            # Add any additional kwargs
            program_data.update(kwargs)
            
            program = self.program_repository.create(**program_data)
            self.db_session.commit()
            
            logger.info(f"Created program {program.id}: {name}")
            return program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program)
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create program: {str(e)}")
            return None
    
    def get_program(self, program_id: int) -> Optional[Dict[str, Any]]:
        """Get program by ID."""
        try:
            program = self.program_repository.find_by_id(program_id)
            if program:
                return program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program)
            return None
        except Exception as e:
            logger.error(f"Failed to get program {program_id}: {str(e)}")
            return None
    
    def get_all_programs(self, limit: Optional[int] = None, 
                        offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all programs."""
        try:
            programs = self.program_repository.find_all(limit=limit, offset=offset)
            return [program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program) 
                   for program in programs]
        except Exception as e:
            logger.error(f"Failed to get all programs: {str(e)}")
            return []
    
    def get_programs_by_trainer(self, trainer_id: int) -> List[Dict[str, Any]]:
        """Get programs by trainer."""
        try:
            programs = self.program_repository.find_by_trainer_id(trainer_id)
            return [program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program) 
                   for program in programs]
        except Exception as e:
            logger.error(f"Failed to get programs for trainer {trainer_id}: {str(e)}")
            return []
    
    def get_programs_by_tenant(self, tenant_id: int) -> List[Dict[str, Any]]:
        """Get programs by tenant."""
        try:
            programs = self.program_repository.find_by_tenant_id(tenant_id)
            return [program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program) 
                   for program in programs]
        except Exception as e:
            logger.error(f"Failed to get programs for tenant {tenant_id}: {str(e)}")
            return []
    
    def get_active_programs(self) -> List[Dict[str, Any]]:
        """Get all active programs."""
        try:
            programs = self.program_repository.find_active_programs()
            return [program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program) 
                   for program in programs]
        except Exception as e:
            logger.error(f"Failed to get active programs: {str(e)}")
            return []
    
    def get_programs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get programs by category."""
        try:
            programs = self.program_repository.find_by_category(category)
            return [program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program) 
                   for program in programs]
        except Exception as e:
            logger.error(f"Failed to get programs by category {category}: {str(e)}")
            return []
    
    def update_program(self, program_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update program."""
        try:
            program = self.program_repository.update(program_id, **kwargs)
            if program:
                self.db_session.commit()
                logger.info(f"Updated program {program_id}")
                return program.to_dict() if hasattr(program, 'to_dict') else self._serialize_program(program)
            return None
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update program {program_id}: {str(e)}")
            return None
    
    def delete_program(self, program_id: int) -> bool:
        """Delete program."""
        try:
            success = self.program_repository.delete(program_id)
            if success:
                self.db_session.commit()
                logger.info(f"Deleted program {program_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete program {program_id}: {str(e)}")
            return False
    
    def enroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Enroll beneficiary in program."""
        try:
            success = self.program_repository.enroll_beneficiary(program_id, beneficiary_id)
            if success:
                self.db_session.commit()
                logger.info(f"Enrolled beneficiary {beneficiary_id} in program {program_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to enroll beneficiary {beneficiary_id} in program {program_id}: {str(e)}")
            return False
    
    def unenroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Unenroll beneficiary from program."""
        try:
            success = self.program_repository.unenroll_beneficiary(program_id, beneficiary_id)
            if success:
                self.db_session.commit()
                logger.info(f"Unenrolled beneficiary {beneficiary_id} from program {program_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to unenroll beneficiary {beneficiary_id} from program {program_id}: {str(e)}")
            return False
    
    def get_program_enrollments(self, program_id: int) -> List[Dict[str, Any]]:
        """Get program enrollments."""
        try:
            program = self.program_repository.find_with_enrollments(program_id)
            if program and hasattr(program, 'enrollments'):
                return [enrollment.to_dict() if hasattr(enrollment, 'to_dict') else 
                       self._serialize_enrollment(enrollment) for enrollment in program.enrollments]
            elif program and hasattr(program, 'beneficiaries'):
                return [beneficiary.to_dict() if hasattr(beneficiary, 'to_dict') else 
                       self._serialize_beneficiary(beneficiary) for beneficiary in program.beneficiaries]
            return []
        except Exception as e:
            logger.error(f"Failed to get enrollments for program {program_id}: {str(e)}")
            return []
    
    def get_program_statistics(self, program_id: int) -> Dict[str, Any]:
        """Get program statistics."""
        try:
            return self.program_repository.get_program_statistics(program_id)
        except Exception as e:
            logger.error(f"Failed to get statistics for program {program_id}: {str(e)}")
            return {}
    
    def activate_program(self, program_id: int) -> bool:
        """Activate program."""
        try:
            program = self.program_repository.update(program_id, status='active', is_active=True)
            if program:
                self.db_session.commit()
                logger.info(f"Activated program {program_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to activate program {program_id}: {str(e)}")
            return False
    
    def deactivate_program(self, program_id: int) -> bool:
        """Deactivate program."""
        try:
            program = self.program_repository.update(program_id, status='inactive', is_active=False)
            if program:
                self.db_session.commit()
                logger.info(f"Deactivated program {program_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to deactivate program {program_id}: {str(e)}")
            return False
    
    def _serialize_program(self, program) -> Dict[str, Any]:
        """Serialize program for API response."""
        return {
            'id': program.id,
            'name': getattr(program, 'name', ''),
            'description': getattr(program, 'description', ''),
            'trainer_id': getattr(program, 'trainer_id', None),
            'tenant_id': getattr(program, 'tenant_id', None),
            'status': getattr(program, 'status', ''),
            'is_active': getattr(program, 'is_active', True),
            'category': getattr(program, 'category', ''),
            'created_at': getattr(program, 'created_at', datetime.now()).isoformat(),
            'updated_at': getattr(program, 'updated_at', datetime.now()).isoformat()
        }
    
    def _serialize_enrollment(self, enrollment) -> Dict[str, Any]:
        """Serialize enrollment for API response."""
        return {
            'id': getattr(enrollment, 'id', None),
            'program_id': getattr(enrollment, 'program_id', None),
            'beneficiary_id': getattr(enrollment, 'beneficiary_id', None),
            'status': getattr(enrollment, 'status', ''),
            'enrolled_at': getattr(enrollment, 'enrolled_at', datetime.now()).isoformat()
        }
    
    def _serialize_beneficiary(self, beneficiary) -> Dict[str, Any]:
        """Serialize beneficiary for API response."""
        return {
            'id': beneficiary.id,
            'first_name': getattr(beneficiary, 'first_name', ''),
            'last_name': getattr(beneficiary, 'last_name', ''),
            'email': getattr(beneficiary, 'email', ''),
            'is_active': getattr(beneficiary, 'is_active', True)
        }