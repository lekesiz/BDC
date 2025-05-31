"""Repository implementation for Beneficiary entity."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.beneficiary import Beneficiary
from app.services.interfaces.beneficiary_repository_interface import IBeneficiaryRepository


class BeneficiaryRepository(IBeneficiaryRepository):
    """Repository implementation for Beneficiary entity."""
    
    def __init__(self, db_session: Session):
        """Initialize the repository with a database session."""
        self.db = db_session
    
    def create(self, beneficiary: Beneficiary) -> Beneficiary:
        """Create a new beneficiary."""
        self.db.add(beneficiary)
        self.db.commit()
        self.db.refresh(beneficiary)
        return beneficiary
    
    def get_by_id(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """Get a beneficiary by ID."""
        return self.db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    
    def get_by_user_id(self, user_id: int) -> Optional[Beneficiary]:
        """Get a beneficiary by user ID."""
        return self.db.query(Beneficiary).filter(Beneficiary.user_id == user_id).first()
    
    def get_by_trainer_id(self, trainer_id: int, page: int = 1, per_page: int = 10) -> List[Beneficiary]:
        """Get beneficiaries by trainer ID with pagination."""
        query = self.db.query(Beneficiary).filter(Beneficiary.trainer_id == trainer_id)
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': paginated.items,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }
    
    def get_all(self, filters: dict = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all beneficiaries with optional filters and pagination."""
        query = self.db.query(Beneficiary)
        
        if filters:
            if 'program_id' in filters:
                query = query.filter(Beneficiary.program_id == filters['program_id'])
            if 'search' in filters:
                search = f"%{filters['search']}%"
                query = query.filter(
                    (Beneficiary.first_name.ilike(search)) |
                    (Beneficiary.last_name.ilike(search)) |
                    (Beneficiary.email.ilike(search))
                )
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': paginated.items,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }
    
    def update(self, beneficiary: Beneficiary, updates: dict) -> Beneficiary:
        """Update a beneficiary."""
        if not beneficiary:
            return None
        
        for key, value in updates.items():
            setattr(beneficiary, key, value)
        
        self.db.commit()
        self.db.refresh(beneficiary)
        return beneficiary
    
    def delete(self, beneficiary: Beneficiary) -> bool:
        """Delete a beneficiary."""
        if not beneficiary:
            return False
        
        self.db.delete(beneficiary)
        self.db.commit()
        return True
    
    def count_by_user_id(self, user_id: int) -> int:
        """Count beneficiaries for a user."""
        return self.db.query(Beneficiary).filter(Beneficiary.user_id == user_id).count()
    
    def get_by_phone_number(self, phone_number: str) -> Optional[Beneficiary]:
        """Get a beneficiary by phone number."""
        return self.db.query(Beneficiary).filter(Beneficiary.phone == phone_number).first()
    
    def get_by_caregiver_id(self, caregiver_id: int) -> List[Beneficiary]:
        """Get beneficiaries by caregiver ID."""
        return self.db.query(Beneficiary).filter(Beneficiary.caregiver_id == caregiver_id).all()