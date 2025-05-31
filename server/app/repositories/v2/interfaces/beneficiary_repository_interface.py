"""Beneficiary repository interface."""

from abc import abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime
from app.repositories.v2.interfaces.base_repository_interface import IBaseRepository
from app.models import Beneficiary, Note, Document, Appointment


class IBeneficiaryRepository(IBaseRepository[Beneficiary]):
    """Beneficiary repository interface with beneficiary-specific operations."""
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> Optional[Beneficiary]:
        """Find beneficiary by user ID."""
        pass
    
    @abstractmethod
    def find_by_tenant(self, tenant_id: int, limit: int = 100, offset: int = 0) -> List[Beneficiary]:
        """Find all beneficiaries for a tenant."""
        pass
    
    @abstractmethod
    def find_by_trainer(self, trainer_id: int, limit: int = 100, offset: int = 0) -> List[Beneficiary]:
        """Find all beneficiaries assigned to a trainer."""
        pass
    
    @abstractmethod
    def search(self, filters: Dict[str, Any], tenant_id: int, 
               limit: int = 100, offset: int = 0) -> Tuple[List[Beneficiary], int]:
        """Search beneficiaries with filters. Returns (results, total_count)."""
        pass
    
    @abstractmethod
    def find_by_status(self, status: str, tenant_id: int) -> List[Beneficiary]:
        """Find beneficiaries by status."""
        pass
    
    @abstractmethod
    def add_note(self, beneficiary: Beneficiary, note_data: Dict[str, Any]) -> Note:
        """Add note to beneficiary."""
        pass
    
    @abstractmethod
    def get_notes(self, beneficiary_id: int, limit: int = 100, offset: int = 0) -> List[Note]:
        """Get beneficiary notes."""
        pass
    
    @abstractmethod
    def add_document(self, beneficiary: Beneficiary, document_data: Dict[str, Any]) -> Document:
        """Add document to beneficiary."""
        pass
    
    @abstractmethod
    def get_documents(self, beneficiary_id: int) -> List[Document]:
        """Get beneficiary documents."""
        pass
    
    @abstractmethod
    def remove_document(self, beneficiary: Beneficiary, document_id: int) -> bool:
        """Remove document from beneficiary."""
        pass
    
    @abstractmethod
    def schedule_appointment(self, beneficiary: Beneficiary, 
                           appointment_data: Dict[str, Any]) -> Appointment:
        """Schedule appointment for beneficiary."""
        pass
    
    @abstractmethod
    def get_appointments(self, beneficiary_id: int, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Appointment]:
        """Get beneficiary appointments."""
        pass
    
    @abstractmethod
    def cancel_appointment(self, beneficiary: Beneficiary, appointment_id: int) -> bool:
        """Cancel beneficiary appointment."""
        pass
    
    @abstractmethod
    def update_trainer(self, beneficiary: Beneficiary, trainer_id: Optional[int]) -> Beneficiary:
        """Update beneficiary's assigned trainer."""
        pass
    
    @abstractmethod
    def get_statistics(self, tenant_id: int) -> Dict[str, Any]:
        """Get beneficiary statistics for tenant."""
        pass
    
    @abstractmethod
    def bulk_update_status(self, beneficiaries: List[Beneficiary], status: str) -> int:
        """Bulk update beneficiary status. Returns count updated."""
        pass