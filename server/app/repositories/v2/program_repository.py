"""Concrete implementation of program repository."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload

from app.models import Program, ProgramEnrollment, Beneficiary
from app.repositories.v2.base_repository import BaseRepository
from app.repositories.v2.interfaces.program_repository_interface import IProgramRepository


class ProgramRepository(BaseRepository[Program], IProgramRepository):
    """Program repository with concrete implementations."""
    
    def __init__(self, db_session):
        """Initialize program repository."""
        super().__init__(db_session, Program)
    
    def find_by_name(self, name: str) -> Optional[Program]:
        """Find program by name."""
        return self.find_one_by(name=name)
    
    def find_active_programs(self) -> List[Program]:
        """Find all active programs."""
        return self.db.query(self.model_class).filter(
            self.model_class.is_active == True,
            or_(
                self.model_class.end_date == None,
                self.model_class.end_date >= datetime.utcnow()
            )
        ).all()
    
    def find_by_category(self, category: str) -> List[Program]:
        """Find programs by category."""
        return self.find_all_by(category=category)
    
    def search_programs(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Program]:
        """Search programs with filters."""
        search_query = self.db.query(self.model_class)
        
        # Apply text search
        if query:
            search_filter = or_(
                self.model_class.name.ilike(f'%{query}%'),
                self.model_class.description.ilike(f'%{query}%'),
                self.model_class.category.ilike(f'%{query}%')
            )
            search_query = search_query.filter(search_filter)
        
        # Apply filters
        if filters:
            if 'is_active' in filters:
                search_query = search_query.filter(
                    self.model_class.is_active == filters['is_active']
                )
            if 'category' in filters:
                search_query = search_query.filter(
                    self.model_class.category == filters['category']
                )
            if 'start_after' in filters:
                search_query = search_query.filter(
                    self.model_class.start_date >= filters['start_after']
                )
            if 'start_before' in filters:
                search_query = search_query.filter(
                    self.model_class.start_date <= filters['start_before']
                )
        
        return search_query.all()
    
    def get_program_statistics(self, program_id: int) -> Dict[str, Any]:
        """Get statistics for a program."""
        program = self.find_by_id(program_id)
        if not program:
            return {}
        
        # Count enrollments by status
        enrollment_stats = self.db.query(
            ProgramEnrollment.status,
            func.count(ProgramEnrollment.id)
        ).filter(
            ProgramEnrollment.program_id == program_id
        ).group_by(ProgramEnrollment.status).all()
        
        stats = {
            'total_enrolled': 0,
            'active': 0,
            'completed': 0,
            'dropped': 0
        }
        
        for status, count in enrollment_stats:
            stats[status] = count
            stats['total_enrolled'] += count
        
        # Calculate completion rate
        if stats['total_enrolled'] > 0:
            stats['completion_rate'] = (stats['completed'] / stats['total_enrolled']) * 100
        else:
            stats['completion_rate'] = 0
        
        return stats
    
    def enroll_beneficiary(self, program_id: int, beneficiary_id: int,
                          enrolled_by_id: int) -> ProgramEnrollment:
        """Enroll a beneficiary in a program."""
        # Check if already enrolled
        existing = self.db.query(ProgramEnrollment).filter(
            ProgramEnrollment.program_id == program_id,
            ProgramEnrollment.beneficiary_id == beneficiary_id
        ).first()
        
        if existing:
            # Reactivate if dropped
            if existing.status == 'dropped':
                existing.status = 'active'
                existing.enrollment_date = datetime.utcnow()
                existing.enrolled_by_id = enrolled_by_id
                self.db.commit()
                self.db.refresh(existing)
            return existing
        
        # Create new enrollment
        enrollment = ProgramEnrollment(
            program_id=program_id,
            beneficiary_id=beneficiary_id,
            enrolled_by_id=enrolled_by_id,
            enrollment_date=datetime.utcnow(),
            status='active'
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        
        return enrollment
    
    def unenroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Unenroll a beneficiary from a program."""
        enrollment = self.db.query(ProgramEnrollment).filter(
            ProgramEnrollment.program_id == program_id,
            ProgramEnrollment.beneficiary_id == beneficiary_id,
            ProgramEnrollment.status == 'active'
        ).first()
        
        if enrollment:
            enrollment.status = 'dropped'
            enrollment.completion_date = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def get_enrollments(self, program_id: int) -> List[ProgramEnrollment]:
        """Get all enrollments for a program."""
        return self.db.query(ProgramEnrollment).filter(
            ProgramEnrollment.program_id == program_id
        ).options(
            joinedload(ProgramEnrollment.beneficiary)
        ).all()
    
    def get_beneficiary_enrollments(self, beneficiary_id: int) -> List[ProgramEnrollment]:
        """Get all program enrollments for a beneficiary."""
        return self.db.query(ProgramEnrollment).filter(
            ProgramEnrollment.beneficiary_id == beneficiary_id
        ).options(
            joinedload(ProgramEnrollment.program)
        ).all()
    
    def update_enrollment_status(self, enrollment_id: int, status: str) -> Optional[ProgramEnrollment]:
        """Update enrollment status."""
        enrollment = self.db.query(ProgramEnrollment).filter(
            ProgramEnrollment.id == enrollment_id
        ).first()
        
        if enrollment:
            enrollment.status = status
            if status == 'completed':
                enrollment.completion_date = datetime.utcnow()
            self.db.commit()
            self.db.refresh(enrollment)
        
        return enrollment
    
    def get_upcoming_programs(self, days: int = 30) -> List[Program]:
        """Get programs starting in the next N days."""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        return self.db.query(self.model_class).filter(
            self.model_class.start_date >= datetime.utcnow(),
            self.model_class.start_date <= cutoff_date,
            self.model_class.is_active == True
        ).order_by(self.model_class.start_date).all()
    
    def archive_program(self, program_id: int) -> bool:
        """Archive a program."""
        program = self.find_by_id(program_id)
        
        if program:
            program.is_active = False
            program.archived_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False