"""Evaluation service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IEvaluationService(ABC):
    """Interface for evaluation service operations."""
    
    @abstractmethod
    def create_evaluation(self, beneficiary_id: int, test_id: int, trainer_id: int,
                         creator_id: Optional[int] = None, tenant_id: Optional[int] = None,
                         **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new evaluation.
        
        Args:
            beneficiary_id: Beneficiary ID
            test_id: Test ID
            trainer_id: Trainer ID
            creator_id: Creator ID
            tenant_id: Tenant ID
            **kwargs: Additional evaluation data
            
        Returns:
            Created evaluation data or None if failed
        """
        pass
    
    @abstractmethod
    def get_evaluation(self, evaluation_id: int) -> Optional[Dict[str, Any]]:
        """Get evaluation by ID.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Evaluation data or None if not found
        """
        pass
    
    @abstractmethod
    def get_evaluations_by_beneficiary(self, beneficiary_id: int) -> List[Dict[str, Any]]:
        """Get evaluations for a beneficiary.
        
        Args:
            beneficiary_id: Beneficiary ID
            
        Returns:
            List of evaluation data
        """
        pass
    
    @abstractmethod
    def get_evaluations_by_trainer(self, trainer_id: int) -> List[Dict[str, Any]]:
        """Get evaluations by trainer.
        
        Args:
            trainer_id: Trainer ID
            
        Returns:
            List of evaluation data
        """
        pass
    
    @abstractmethod
    def get_evaluations_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get evaluations by status.
        
        Args:
            status: Evaluation status
            
        Returns:
            List of evaluation data
        """
        pass
    
    @abstractmethod
    def update_evaluation(self, evaluation_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update evaluation.
        
        Args:
            evaluation_id: Evaluation ID
            **kwargs: Update data
            
        Returns:
            Updated evaluation data or None if failed
        """
        pass
    
    @abstractmethod
    def submit_responses(self, evaluation_id: int, responses: List[Dict[str, Any]]) -> bool:
        """Submit evaluation responses.
        
        Args:
            evaluation_id: Evaluation ID
            responses: List of responses
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_score(self, evaluation_id: int) -> Optional[float]:
        """Calculate evaluation score.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Calculated score or None if failed
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
    
    @abstractmethod
    def complete_evaluation(self, evaluation_id: int) -> bool:
        """Mark evaluation as completed.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def review_evaluation(self, evaluation_id: int) -> bool:
        """Mark evaluation as reviewed.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_evaluation(self, evaluation_id: int) -> bool:
        """Delete evaluation.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_evaluation_statistics(self, evaluation_id: int) -> Dict[str, Any]:
        """Get evaluation statistics.
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Dictionary with evaluation statistics
        """
        pass