"""Evaluation repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.repositories.interfaces.base_repository_interface import IBaseRepository


class IEvaluationRepository(IBaseRepository, ABC):
    """Interface for evaluation repository operations."""
    
    @abstractmethod
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Any]:
        """Find evaluations by beneficiary ID.
        
        Args:
            beneficiary_id: Beneficiary ID
            
        Returns:
            List of evaluation instances
        """
        pass
    
    @abstractmethod
    def find_by_trainer_id(self, trainer_id: int) -> List[Any]:
        """Find evaluations by trainer ID.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            List of evaluation instances
        """
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[Any]:
        """Find evaluations by status.
        
        Args:
            status: Evaluation status
            
        Returns:
            List of evaluation instances
        """
        pass
    
    @abstractmethod
    def find_by_test_id(self, test_id: int) -> List[Any]:
        """Find evaluations by test ID.
        
        Args:
            test_id: Test ID
            
        Returns:
            List of evaluation instances
        """
        pass
    
    @abstractmethod
    def find_by_tenant_id(self, tenant_id: int) -> List[Any]:
        """Find evaluations by tenant ID.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of evaluation instances
        """
        pass
    
    @abstractmethod
    def update_score(self, evaluation_id: int, score: float) -> bool:
        """Update evaluation score.
        
        Args:
            evaluation_id: Evaluation ID
            score: New score
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update_status(self, evaluation_id: int, status: str) -> bool:
        """Update evaluation status.
        
        Args:
            evaluation_id: Evaluation ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def add_feedback(self, evaluation_id: int, feedback: str, 
                    strengths: Optional[str] = None, 
                    weaknesses: Optional[str] = None,
                    recommendations: Optional[str] = None) -> bool:
        """Add feedback to evaluation.
        
        Args:
            evaluation_id: Evaluation ID
            feedback: Feedback text
            strengths: Strengths text
            weaknesses: Weaknesses text
            recommendations: Recommendations text
            
        Returns:
            True if successful, False otherwise
        """
        pass