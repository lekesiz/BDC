"""Improved evaluation service with dependency injection."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from app.services.interfaces.evaluation_service_interface import IEvaluationService
from app.repositories.interfaces.evaluation_repository_interface import IEvaluationRepository
from app.extensions import db

logger = logging.getLogger(__name__)


class ImprovedEvaluationService(IEvaluationService):
    """Improved evaluation service with dependency injection."""
    
    def __init__(self, evaluation_repository: IEvaluationRepository, db_session: Optional[Session] = None):
        """Initialize service with dependencies.
        
        Args:
            evaluation_repository: Evaluation repository implementation
            db_session: Database session (optional)
        """
        self.evaluation_repository = evaluation_repository
        self.db_session = db_session or db.session
    
    def create_evaluation(self, beneficiary_id: int, test_id: int, trainer_id: int,
                         creator_id: Optional[int] = None, tenant_id: Optional[int] = None,
                         **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new evaluation."""
        try:
            evaluation_data = {
                'beneficiary_id': beneficiary_id,
                'test_id': test_id,
                'trainer_id': trainer_id,
                'status': 'in_progress',
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            if creator_id:
                evaluation_data['creator_id'] = creator_id
            if tenant_id:
                evaluation_data['tenant_id'] = tenant_id
            
            # Add any additional kwargs
            evaluation_data.update(kwargs)
            
            evaluation = self.evaluation_repository.create(**evaluation_data)
            self.db_session.commit()
            
            logger.info(f"Created evaluation {evaluation.id} for beneficiary {beneficiary_id}")
            return evaluation.to_dict()
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create evaluation: {str(e)}")
            return None
    
    def get_evaluation(self, evaluation_id: int) -> Optional[Dict[str, Any]]:
        """Get evaluation by ID."""
        try:
            evaluation = self.evaluation_repository.find_by_id(evaluation_id)
            if evaluation:
                return evaluation.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get evaluation {evaluation_id}: {str(e)}")
            return None
    
    def get_evaluations_by_beneficiary(self, beneficiary_id: int) -> List[Dict[str, Any]]:
        """Get evaluations for a beneficiary."""
        try:
            evaluations = self.evaluation_repository.find_by_beneficiary_id(beneficiary_id)
            return [evaluation.to_dict() for evaluation in evaluations]
        except Exception as e:
            logger.error(f"Failed to get evaluations for beneficiary {beneficiary_id}: {str(e)}")
            return []
    
    def get_evaluations_by_trainer(self, trainer_id: int) -> List[Dict[str, Any]]:
        """Get evaluations by trainer."""
        try:
            evaluations = self.evaluation_repository.find_by_trainer_id(trainer_id)
            return [evaluation.to_dict() for evaluation in evaluations]
        except Exception as e:
            logger.error(f"Failed to get evaluations for trainer {trainer_id}: {str(e)}")
            return []
    
    def get_evaluations_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get evaluations by status."""
        try:
            evaluations = self.evaluation_repository.find_by_status(status)
            return [evaluation.to_dict() for evaluation in evaluations]
        except Exception as e:
            logger.error(f"Failed to get evaluations by status {status}: {str(e)}")
            return []
    
    def update_evaluation(self, evaluation_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update evaluation."""
        try:
            evaluation = self.evaluation_repository.update(evaluation_id, **kwargs)
            if evaluation:
                self.db_session.commit()
                logger.info(f"Updated evaluation {evaluation_id}")
                return evaluation.to_dict()
            return None
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update evaluation {evaluation_id}: {str(e)}")
            return None
    
    def submit_responses(self, evaluation_id: int, responses: List[Dict[str, Any]]) -> bool:
        """Submit evaluation responses."""
        try:
            evaluation = self.evaluation_repository.find_by_id(evaluation_id)
            if not evaluation:
                return False
            
            evaluation.responses = responses
            evaluation.updated_at = datetime.now(timezone.utc)
            
            # Calculate score if responses include correctness
            if all('is_correct' in response for response in responses):
                score = self._calculate_score_from_responses(responses)
                evaluation.score = score
            
            self.evaluation_repository.save(evaluation)
            self.db_session.commit()
            
            logger.info(f"Submitted responses for evaluation {evaluation_id}")
            return True
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to submit responses for evaluation {evaluation_id}: {str(e)}")
            return False
    
    def calculate_score(self, evaluation_id: int) -> Optional[float]:
        """Calculate evaluation score."""
        try:
            evaluation = self.evaluation_repository.find_by_id(evaluation_id)
            if not evaluation:
                return None
            
            if not evaluation.responses:
                return 0.0
            
            score = self._calculate_score_from_responses(evaluation.responses)
            
            # Update the evaluation with the calculated score
            self.evaluation_repository.update_score(evaluation_id, score)
            self.db_session.commit()
            
            logger.info(f"Calculated score {score} for evaluation {evaluation_id}")
            return score
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to calculate score for evaluation {evaluation_id}: {str(e)}")
            return None
    
    def add_feedback(self, evaluation_id: int, feedback: str,
                    strengths: Optional[str] = None,
                    weaknesses: Optional[str] = None,
                    recommendations: Optional[str] = None) -> bool:
        """Add feedback to evaluation."""
        try:
            success = self.evaluation_repository.add_feedback(
                evaluation_id, feedback, strengths, weaknesses, recommendations
            )
            if success:
                self.db_session.commit()
                logger.info(f"Added feedback to evaluation {evaluation_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to add feedback to evaluation {evaluation_id}: {str(e)}")
            return False
    
    def complete_evaluation(self, evaluation_id: int) -> bool:
        """Mark evaluation as completed."""
        try:
            success = self.evaluation_repository.update_status(evaluation_id, 'completed')
            if success:
                self.db_session.commit()
                logger.info(f"Completed evaluation {evaluation_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to complete evaluation {evaluation_id}: {str(e)}")
            return False
    
    def review_evaluation(self, evaluation_id: int) -> bool:
        """Mark evaluation as reviewed."""
        try:
            success = self.evaluation_repository.update_status(evaluation_id, 'reviewed')
            if success:
                self.db_session.commit()
                logger.info(f"Reviewed evaluation {evaluation_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to review evaluation {evaluation_id}: {str(e)}")
            return False
    
    def delete_evaluation(self, evaluation_id: int) -> bool:
        """Delete evaluation."""
        try:
            success = self.evaluation_repository.delete(evaluation_id)
            if success:
                self.db_session.commit()
                logger.info(f"Deleted evaluation {evaluation_id}")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete evaluation {evaluation_id}: {str(e)}")
            return False
    
    def get_evaluation_statistics(self, evaluation_id: int) -> Dict[str, Any]:
        """Get evaluation statistics."""
        try:
            evaluation = self.evaluation_repository.find_by_id(evaluation_id)
            if not evaluation:
                return {}
            
            stats = {
                'id': evaluation.id,
                'status': evaluation.status,
                'score': evaluation.score,
                'total_responses': len(evaluation.responses) if evaluation.responses else 0,
                'has_feedback': bool(evaluation.feedback),
                'has_strengths': bool(evaluation.strengths),
                'has_weaknesses': bool(evaluation.weaknesses),
                'has_recommendations': bool(evaluation.recommendations),
                'created_at': evaluation.created_at.isoformat(),
                'updated_at': evaluation.updated_at.isoformat()
            }
            
            if evaluation.completed_at:
                stats['completed_at'] = evaluation.completed_at.isoformat()
            if evaluation.reviewed_at:
                stats['reviewed_at'] = evaluation.reviewed_at.isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics for evaluation {evaluation_id}: {str(e)}")
            return {}
    
    def _calculate_score_from_responses(self, responses: List[Dict[str, Any]]) -> float:
        """Calculate score from responses."""
        if not responses:
            return 0.0
        
        correct_count = sum(1 for response in responses if response.get('is_correct', False))
        total_questions = len(responses)
        
        return (correct_count / total_questions) * 100 if total_questions > 0 else 0.0