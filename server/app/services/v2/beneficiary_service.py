"""Beneficiary service implementation."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.repositories.v2.interfaces.beneficiary_repository_interface import IBeneficiaryRepository
from app.services.v2.interfaces.beneficiary_service_interface import IBeneficiaryService
from app.extensions import db
from app.utils.logging import logger


class BeneficiaryServiceV2(IBeneficiaryService):
    """Beneficiary service with business logic."""
    
    def __init__(self, beneficiary_repository: IBeneficiaryRepository,
                 db_session: Optional[Session] = None):
        """Initialize service with dependencies."""
        self.beneficiary_repository = beneficiary_repository
        self.db_session = db_session or db.session
    
    def get_all_beneficiaries(self, tenant_id: Optional[int] = None) -> List[Beneficiary]:
        """Get all beneficiaries, optionally filtered by tenant."""
        try:
            if tenant_id:
                return self.beneficiary_repository.find_by_tenant(tenant_id)
            return self.beneficiary_repository.find_all()
        except Exception as e:
            logger.exception(f"Error getting beneficiaries: {str(e)}")
            return []
    
    def get_beneficiary_by_id(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """Get beneficiary by ID."""
        try:
            return self.beneficiary_repository.find_by_id(beneficiary_id)
        except Exception as e:
            logger.exception(f"Error getting beneficiary {beneficiary_id}: {str(e)}")
            return None
    
    def create_beneficiary(self, data: Dict[str, Any]) -> Optional[Beneficiary]:
        """Create a new beneficiary."""
        try:
            # Check if beneficiary with same email exists
            if 'email' in data:
                existing = self.beneficiary_repository.find_by_email(data['email'])
                if existing:
                    logger.warning(f"Beneficiary with email {data['email']} already exists")
                    return None
            
            # Create beneficiary
            beneficiary = Beneficiary(**data)
            self.db_session.add(beneficiary)
            self.db_session.commit()
            
            logger.info(f"Created beneficiary: {beneficiary.id}")
            return beneficiary
            
        except Exception as e:
            logger.exception(f"Error creating beneficiary: {str(e)}")
            self.db_session.rollback()
            return None
    
    def update_beneficiary(self, beneficiary_id: int, data: Dict[str, Any]) -> Optional[Beneficiary]:
        """Update beneficiary data."""
        try:
            beneficiary = self.beneficiary_repository.find_by_id(beneficiary_id)
            if not beneficiary:
                return None
            
            # Update fields
            for key, value in data.items():
                if hasattr(beneficiary, key):
                    setattr(beneficiary, key, value)
            
            self.db_session.commit()
            
            logger.info(f"Updated beneficiary: {beneficiary_id}")
            return beneficiary
            
        except Exception as e:
            logger.exception(f"Error updating beneficiary {beneficiary_id}: {str(e)}")
            self.db_session.rollback()
            return None
    
    def delete_beneficiary(self, beneficiary_id: int) -> bool:
        """Delete a beneficiary."""
        try:
            beneficiary = self.beneficiary_repository.find_by_id(beneficiary_id)
            if not beneficiary:
                return False
            
            self.db_session.delete(beneficiary)
            self.db_session.commit()
            
            logger.info(f"Deleted beneficiary: {beneficiary_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error deleting beneficiary {beneficiary_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def search_beneficiaries(self, query: str, tenant_id: Optional[int] = None) -> List[Beneficiary]:
        """Search beneficiaries by name or email."""
        try:
            return self.beneficiary_repository.search(query, tenant_id)
        except Exception as e:
            logger.exception(f"Error searching beneficiaries: {str(e)}")
            return []
    
    def get_beneficiary_programs(self, beneficiary_id: int) -> List[Any]:
        """Get programs enrolled by beneficiary."""
        try:
            beneficiary = self.beneficiary_repository.find_by_id(beneficiary_id)
            if not beneficiary:
                return []
            
            # Return enrolled programs
            return [enrollment.program for enrollment in beneficiary.program_enrollments]
            
        except Exception as e:
            logger.exception(f"Error getting beneficiary programs: {str(e)}")
            return []
    
    def get_beneficiary_evaluations(self, beneficiary_id: int) -> List[Any]:
        """Get evaluations for beneficiary."""
        try:
            beneficiary = self.beneficiary_repository.find_by_id(beneficiary_id)
            if not beneficiary:
                return []
            
            # Return evaluations
            return beneficiary.evaluations
            
        except Exception as e:
            logger.exception(f"Error getting beneficiary evaluations: {str(e)}")
            return []