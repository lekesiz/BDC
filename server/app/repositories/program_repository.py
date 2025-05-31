"""Program repository implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.program_repository_interface import IProgramRepository
from app.models import Program
from app.extensions import db


class ProgramRepository(BaseRepository[Program], IProgramRepository):
    """Program repository implementation."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize program repository."""
        super().__init__(Program, db_session)
    
    def find_by_tenant_id(self, tenant_id: int) -> List[Program]:
        """Find programs by tenant ID."""
        return self.db_session.query(Program).filter_by(
            tenant_id=tenant_id
        ).order_by(Program.created_at.desc()).all()
    
    def find_by_trainer_id(self, trainer_id: int) -> List[Program]:
        """Find programs by trainer ID."""
        return self.db_session.query(Program).filter_by(
            trainer_id=trainer_id
        ).order_by(Program.created_at.desc()).all()
    
    def find_by_status(self, status: str) -> List[Program]:
        """Find programs by status."""
        return self.db_session.query(Program).filter_by(
            status=status
        ).order_by(Program.created_at.desc()).all()
    
    def find_active_programs(self) -> List[Program]:
        """Find all active programs."""
        return self.db_session.query(Program).filter(
            and_(
                Program.is_active == True,
                Program.status == 'active'
            )
        ).order_by(Program.created_at.desc()).all()
    
    def find_by_category(self, category: str) -> List[Program]:
        """Find programs by category."""
        return self.db_session.query(Program).filter_by(
            category=category
        ).order_by(Program.created_at.desc()).all()
    
    def find_with_enrollments(self, program_id: int) -> Optional[Program]:
        """Find program with enrollments."""
        # Check if Program model has enrollments relationship
        program = self.db_session.query(Program).filter_by(id=program_id).first()
        if program and hasattr(program, 'enrollments'):
            # Eager load enrollments if relationship exists
            from sqlalchemy.orm import joinedload
            return self.db_session.query(Program).options(
                joinedload(Program.enrollments)
            ).filter_by(id=program_id).first()
        return program
    
    def get_program_statistics(self, program_id: int) -> Dict[str, Any]:
        """Get program statistics."""
        program = self.find_by_id(program_id)
        if not program:
            return {}
        
        stats = {
            'id': program.id,
            'name': program.name,
            'total_enrollments': 0,
            'active_enrollments': 0,
            'completed_enrollments': 0,
            'total_sessions': 0,
            'completion_rate': 0.0
        }
        
        # Calculate statistics if enrollments relationship exists
        if hasattr(program, 'enrollments'):
            enrollments = program.enrollments
            stats['total_enrollments'] = len(enrollments)
            stats['active_enrollments'] = len([e for e in enrollments if getattr(e, 'status', '') == 'active'])
            stats['completed_enrollments'] = len([e for e in enrollments if getattr(e, 'status', '') == 'completed'])
            
            if stats['total_enrollments'] > 0:
                stats['completion_rate'] = (stats['completed_enrollments'] / stats['total_enrollments']) * 100
        
        # Calculate total sessions if sessions relationship exists
        if hasattr(program, 'sessions'):
            stats['total_sessions'] = len(program.sessions)
        
        return stats
    
    def enroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Enroll beneficiary in program."""
        try:
            program = self.find_by_id(program_id)
            if not program:
                return False
            
            # Check if enrollment already exists
            if hasattr(program, 'enrollments'):
                existing_enrollment = next(
                    (e for e in program.enrollments if getattr(e, 'beneficiary_id', None) == beneficiary_id),
                    None
                )
                if existing_enrollment:
                    return False  # Already enrolled
            
            # Create enrollment (this depends on your enrollment model structure)
            # For now, we'll assume a simple many-to-many relationship
            from app.models import Beneficiary
            beneficiary = self.db_session.query(Beneficiary).get(beneficiary_id)
            if beneficiary and hasattr(program, 'beneficiaries'):
                if beneficiary not in program.beneficiaries:
                    program.beneficiaries.append(beneficiary)
                    self.db_session.flush()
                    return True
            
            return False
        except Exception:
            return False
    
    def unenroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Unenroll beneficiary from program."""
        try:
            program = self.find_by_id(program_id)
            if not program:
                return False
            
            # Remove from many-to-many relationship
            from app.models import Beneficiary
            beneficiary = self.db_session.query(Beneficiary).get(beneficiary_id)
            if beneficiary and hasattr(program, 'beneficiaries'):
                if beneficiary in program.beneficiaries:
                    program.beneficiaries.remove(beneficiary)
                    self.db_session.flush()
                    return True
            
            return False
        except Exception:
            return False
    
    def create(self, **kwargs) -> Program:
        """Create a new program."""
        program = Program(**kwargs)
        self.db_session.add(program)
        self.db_session.flush()
        return program
    
    def update(self, program_id: int, **kwargs) -> Optional[Program]:
        """Update program by ID."""
        program = self.find_by_id(program_id)
        if not program:
            return None
        
        for key, value in kwargs.items():
            if hasattr(program, key):
                setattr(program, key, value)
        
        if hasattr(program, 'updated_at'):
            program.updated_at = datetime.utcnow()
        
        self.db_session.flush()
        return program
    
    def delete(self, program_id: int) -> bool:
        """Delete program by ID."""
        program = self.find_by_id(program_id)
        if not program:
            return False
        
        self.db_session.delete(program)
        self.db_session.flush()
        return True
    
    def save(self, program: Program) -> Program:
        """Save program instance."""
        self.db_session.add(program)
        self.db_session.flush()
        return program
    
    def find_all(self, limit: int = None, offset: int = None) -> List[Program]:
        """Find all programs with optional pagination."""
        query = self.db_session.query(Program).order_by(Program.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count(self) -> int:
        """Count total programs."""
        return self.db_session.query(Program).count()