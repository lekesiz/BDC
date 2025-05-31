"""Evaluation repository interface."""
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models import Evaluation, EvaluationResult, EvaluationTemplate
from app.repositories.v2.interfaces.base_repository_interface import IBaseRepository


class IEvaluationRepository(IBaseRepository[Evaluation]):
    """Evaluation repository interface with evaluation-specific operations."""
    
    @abstractmethod
    def find_by_beneficiary(self, beneficiary_id: int) -> List[Evaluation]:
        """Find all evaluations for a beneficiary."""
        pass
    
    @abstractmethod
    def find_by_evaluator(self, evaluator_id: int) -> List[Evaluation]:
        """Find all evaluations by an evaluator."""
        pass
    
    @abstractmethod
    def find_by_program(self, program_id: int) -> List[Evaluation]:
        """Find all evaluations for a program."""
        pass
    
    @abstractmethod
    def find_pending_evaluations(self, beneficiary_id: Optional[int] = None) -> List[Evaluation]:
        """Find pending evaluations, optionally filtered by beneficiary."""
        pass
    
    @abstractmethod
    def find_completed_evaluations(self, beneficiary_id: Optional[int] = None) -> List[Evaluation]:
        """Find completed evaluations, optionally filtered by beneficiary."""
        pass
    
    @abstractmethod
    def create_evaluation_result(self, evaluation_id: int, result_data: Dict[str, Any]) -> EvaluationResult:
        """Create evaluation result."""
        pass
    
    @abstractmethod
    def get_evaluation_results(self, evaluation_id: int) -> List[EvaluationResult]:
        """Get results for an evaluation."""
        pass
    
    @abstractmethod
    def update_evaluation_status(self, evaluation_id: int, status: str) -> Optional[Evaluation]:
        """Update evaluation status."""
        pass
    
    @abstractmethod
    def get_evaluation_statistics(self, beneficiary_id: Optional[int] = None) -> Dict[str, Any]:
        """Get evaluation statistics."""
        pass
    
    @abstractmethod
    def get_evaluation_templates(self, active_only: bool = True) -> List[EvaluationTemplate]:
        """Get evaluation templates."""
        pass
    
    @abstractmethod
    def create_evaluation_from_template(self, template_id: int, 
                                      beneficiary_id: int,
                                      evaluator_id: int) -> Evaluation:
        """Create evaluation from template."""
        pass
    
    @abstractmethod
    def get_overdue_evaluations(self) -> List[Evaluation]:
        """Get overdue evaluations."""
        pass
    
    @abstractmethod
    def calculate_evaluation_score(self, evaluation_id: int) -> float:
        """Calculate total score for an evaluation."""
        pass