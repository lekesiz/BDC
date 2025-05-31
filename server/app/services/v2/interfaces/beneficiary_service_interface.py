"""Beneficiary service interface."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.models import Beneficiary, Note, Document, Appointment


class IBeneficiaryService(ABC):
    """Beneficiary service interface."""
    
    @abstractmethod
    def create_beneficiary(self, beneficiary_data: Dict[str, Any]) -> Beneficiary:
        """Create a new beneficiary."""
        pass
    
    @abstractmethod
    def get_beneficiary(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """Get beneficiary by ID."""
        pass
    
    @abstractmethod
    def update_beneficiary(self, beneficiary_id: int, update_data: Dict[str, Any]) -> Optional[Beneficiary]:
        """Update beneficiary information."""
        pass
    
    @abstractmethod
    def delete_beneficiary(self, beneficiary_id: int) -> bool:
        """Delete a beneficiary."""
        pass
    
    @abstractmethod
    def search_beneficiaries(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                           page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search beneficiaries with pagination."""
        pass
    
    @abstractmethod
    def get_beneficiary_by_email(self, email: str) -> Optional[Beneficiary]:
        """Get beneficiary by email."""
        pass
    
    @abstractmethod
    def get_beneficiary_by_national_id(self, national_id: str) -> Optional[Beneficiary]:
        """Get beneficiary by national ID."""
        pass
    
    @abstractmethod
    def get_beneficiaries_by_program(self, program_id: int) -> List[Beneficiary]:
        """Get all beneficiaries in a program."""
        pass
    
    @abstractmethod
    def enroll_in_program(self, beneficiary_id: int, program_id: int) -> bool:
        """Enroll beneficiary in a program."""
        pass
    
    @abstractmethod
    def unenroll_from_program(self, beneficiary_id: int, program_id: int) -> bool:
        """Unenroll beneficiary from a program."""
        pass
    
    @abstractmethod
    def get_beneficiary_statistics(self) -> Dict[str, Any]:
        """Get beneficiary statistics."""
        pass
    
    # Note management
    @abstractmethod
    def add_note(self, beneficiary_id: int, note_content: str, note_type: str = 'general',
                 is_private: bool = False, created_by_id: int = None) -> Note:
        """Add a note to beneficiary."""
        pass
    
    @abstractmethod
    def get_notes(self, beneficiary_id: int, include_private: bool = False) -> List[Note]:
        """Get beneficiary notes."""
        pass
    
    @abstractmethod
    def update_note(self, note_id: int, content: str) -> Optional[Note]:
        """Update a note."""
        pass
    
    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        pass
    
    # Document management
    @abstractmethod
    def upload_document(self, beneficiary_id: int, file_data: Dict[str, Any]) -> Document:
        """Upload a document for beneficiary."""
        pass
    
    @abstractmethod
    def get_documents(self, beneficiary_id: int, document_type: Optional[str] = None) -> List[Document]:
        """Get beneficiary documents."""
        pass
    
    @abstractmethod
    def download_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Download a document."""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: int) -> bool:
        """Delete a document."""
        pass
    
    # Appointment management
    @abstractmethod
    def schedule_appointment(self, beneficiary_id: int, appointment_data: Dict[str, Any]) -> Appointment:
        """Schedule an appointment."""
        pass
    
    @abstractmethod
    def get_appointments(self, beneficiary_id: int, include_past: bool = False) -> List[Appointment]:
        """Get beneficiary appointments."""
        pass
    
    @abstractmethod
    def update_appointment(self, appointment_id: int, update_data: Dict[str, Any]) -> Optional[Appointment]:
        """Update an appointment."""
        pass
    
    @abstractmethod
    def cancel_appointment(self, appointment_id: int, reason: Optional[str] = None) -> bool:
        """Cancel an appointment."""
        pass
    
    @abstractmethod
    def get_upcoming_appointments(self, days: int = 7) -> List[Appointment]:
        """Get upcoming appointments for all beneficiaries."""
        pass
    
    # Export functionality
    @abstractmethod
    def export_beneficiary_data(self, beneficiary_id: int, format: str = 'pdf') -> bytes:
        """Export beneficiary data in specified format."""
        pass
    
    @abstractmethod
    def export_beneficiaries_list(self, filters: Optional[Dict[str, Any]] = None, 
                                 format: str = 'csv') -> bytes:
        """Export list of beneficiaries."""
        pass