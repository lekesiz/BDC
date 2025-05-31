"""Program repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.repositories.interfaces.base_repository_interface import IBaseRepository


class IProgramRepository(IBaseRepository, ABC):
    """Interface for program repository operations."""
    
    @abstractmethod
    def find_by_tenant_id(self, tenant_id: int) -> List[Any]:
        """Find programs by tenant ID.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of program instances
        """
        pass
    
    @abstractmethod
    def find_by_trainer_id(self, trainer_id: int) -> List[Any]:
        """Find programs by trainer ID.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            List of program instances
        """
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[Any]:
        """Find programs by status.
        
        Args:
            status: Program status
            
        Returns:
            List of program instances
        """
        pass
    
    @abstractmethod
    def find_active_programs(self) -> List[Any]:
        """Find all active programs.
        
        Returns:
            List of active program instances
        """
        pass
    
    @abstractmethod
    def find_by_category(self, category: str) -> List[Any]:
        """Find programs by category.
        
        Args:
            category: Program category
            
        Returns:
            List of program instances
        """
        pass
    
    @abstractmethod
    def find_with_enrollments(self, program_id: int) -> Optional[Any]:
        """Find program with enrollments.
        
        Args:
            program_id: Program ID
            
        Returns:
            Program instance with enrollments or None
        """
        pass
    
    @abstractmethod
    def get_program_statistics(self, program_id: int) -> Dict[str, Any]:
        """Get program statistics.
        
        Args:
            program_id: Program ID
            
        Returns:
            Dictionary with program statistics
        """
        pass
    
    @abstractmethod
    def enroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Enroll beneficiary in program.
        
        Args:
            program_id: Program ID
            beneficiary_id: Beneficiary ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def unenroll_beneficiary(self, program_id: int, beneficiary_id: int) -> bool:
        """Unenroll beneficiary from program.
        
        Args:
            program_id: Program ID
            beneficiary_id: Beneficiary ID
            
        Returns:
            True if successful, False otherwise
        """
        pass