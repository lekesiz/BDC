"""Program service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IProgramService(ABC):
    """Interface for program service operations."""
    
    @abstractmethod
    def create_program(self, name: str, description: str, trainer_id: int,
                      tenant_id: Optional[int] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new program.
        
        Args:
            name: Program name
            description: Program description
            trainer_id: Trainer ID
            tenant_id: Tenant ID
            **kwargs: Additional program data
            
        Returns:
            Created program data or None if failed
        """
        pass
    
    @abstractmethod
    def get_program(self, program_id: int) -> Optional[Dict[str, Any]]:
        """Get program by ID.
        
        Args:
            program_id: Program ID
            
        Returns:
            Program data or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_programs(self, limit: Optional[int] = None, 
                        offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all programs.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of program data
        """
        pass
    
    @abstractmethod
    def get_programs_by_trainer(self, trainer_id: int) -> List[Dict[str, Any]]:
        """Get programs by trainer.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            List of program data
        """
        pass
    
    @abstractmethod
    def get_programs_by_tenant(self, tenant_id: int) -> List[Dict[str, Any]]:
        """Get programs by tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of program data
        """
        pass
    
    @abstractmethod
    def get_active_programs(self) -> List[Dict[str, Any]]:
        """Get all active programs.
        
        Returns:
            List of active program data
        """
        pass
    
    @abstractmethod
    def get_programs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get programs by category.
        
        Args:
            category: Program category
            
        Returns:
            List of program data
        """
        pass
    
    @abstractmethod
    def update_program(self, program_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update program.
        
        Args:
            program_id: Program ID
            **kwargs: Update data
            
        Returns:
            Updated program data or None if failed
        """
        pass
    
    @abstractmethod
    def delete_program(self, program_id: int) -> bool:
        """Delete program.
        
        Args:
            program_id: Program ID
            
        Returns:
            True if successful, False otherwise
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
    
    @abstractmethod
    def get_program_enrollments(self, program_id: int) -> List[Dict[str, Any]]:
        """Get program enrollments.
        
        Args:
            program_id: Program ID
            
        Returns:
            List of enrollment data
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
    def activate_program(self, program_id: int) -> bool:
        """Activate program.
        
        Args:
            program_id: Program ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def deactivate_program(self, program_id: int) -> bool:
        """Deactivate program.
        
        Args:
            program_id: Program ID
            
        Returns:
            True if successful, False otherwise
        """
        pass