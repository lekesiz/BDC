"""Program repository interface."""
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models import Program, ProgramEnrollment
from app.repositories.v2.interfaces.base_repository_interface import IBaseRepository


class IProgramRepository(IBaseRepository[Program]):
    """Program repository interface with program-specific operations."""
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Program]:
        """Find program by name."""
        pass
    
    @abstractmethod
    def find_active_programs(self) -> List[Program]:
        """Find all active programs."""
        pass
    
    @abstractmethod
    def find_by_category(self, category: str) -> List[Program]:
        """Find programs by category."""
        pass
    
    @abstractmethod
    def search_programs(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Program]:
        """Search programs with filters."""
        pass
    
    @abstractmethod
    def get_program_statistics(self, program_id: int) -> Dict[str, Any]:
        """Get statistics for a program."""
        pass
    
    @abstractmethod
    def enroll_beneficiary(self, program_id: int, beneficiary_id: int, 
                          enrolled_by_id: int) -> ProgramEnrollment:
        """Enroll a beneficiary in a program."""
        pass
    
    @abstractmethod
    def unenroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Unenroll a beneficiary from a program."""
        pass
    
    @abstractmethod
    def get_enrollments(self, program_id: int) -> List[ProgramEnrollment]:
        """Get all enrollments for a program."""
        pass
    
    @abstractmethod
    def get_beneficiary_enrollments(self, beneficiary_id: int) -> List[ProgramEnrollment]:
        """Get all program enrollments for a beneficiary."""
        pass
    
    @abstractmethod
    def update_enrollment_status(self, enrollment_id: int, status: str) -> Optional[ProgramEnrollment]:
        """Update enrollment status."""
        pass
    
    @abstractmethod
    def get_upcoming_programs(self, days: int = 30) -> List[Program]:
        """Get programs starting in the next N days."""
        pass
    
    @abstractmethod
    def archive_program(self, program_id: int) -> bool:
        """Archive a program."""
        pass