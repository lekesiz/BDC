"""Interface for beneficiary repository operations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.beneficiary import Beneficiary


class IBeneficiaryRepository(ABC):
    """Interface for beneficiary repository operations."""
    
    @abstractmethod
    def create(self, beneficiary: Beneficiary) -> Beneficiary:
        """Create a new beneficiary."""
        pass
    
    @abstractmethod
    def get_by_id(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """Get a beneficiary by ID."""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[Beneficiary]:
        """Get a beneficiary by user ID."""
        pass
    
    @abstractmethod
    def get_by_trainer_id(self, trainer_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get beneficiaries by trainer ID with pagination."""
        pass
    
    @abstractmethod
    def get_all(self, filters: dict = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all beneficiaries with optional filters and pagination."""
        pass
    
    @abstractmethod
    def update(self, beneficiary: Beneficiary, updates: dict) -> Beneficiary:
        """Update a beneficiary."""
        pass
    
    @abstractmethod
    def delete(self, beneficiary: Beneficiary) -> bool:
        """Delete a beneficiary."""
        pass
    
    @abstractmethod
    def count_by_user_id(self, user_id: int) -> int:
        """Count beneficiaries for a user."""
        pass
    
    @abstractmethod
    def get_by_phone_number(self, phone_number: str) -> Optional[Beneficiary]:
        """Get a beneficiary by phone number."""
        pass
    
    @abstractmethod
    def get_by_caregiver_id(self, caregiver_id: int) -> List[Beneficiary]:
        """Get beneficiaries by caregiver ID."""
        pass