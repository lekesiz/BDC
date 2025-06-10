"""Evaluation service with dependency injection."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.test import Test
from app.models.beneficiary import Beneficiary
from app.models.user import User
from app.extensions import db
from app.utils.logging import logger


class EvaluationService:
    """Service for managing evaluations."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize evaluation service."""
        self.db_session = db_session or db.session
    
    def create_evaluation(self, data: Dict[str, Any]) -> Optional[Evaluation]:
        """Create a new evaluation."""
        try:
            # Validate beneficiary exists
            beneficiary = Beneficiary.query.get(data['beneficiary_id'])
            if not beneficiary:
                raise ValueError("Beneficiary not found")
            
            # Validate test exists
            test = Test.query.get(data['test_id'])
            if not test:
                raise ValueError("Test not found")
            
            # Create evaluation
            evaluation = Evaluation(
                beneficiary_id=data['beneficiary_id'],
                test_id=data['test_id'],
                trainer_id=data['trainer_id'],
                tenant_id=data.get('tenant_id'),
                creator_id=data.get('creator_id'),
                randomization_enabled=data.get('randomization_enabled', True),
                randomization_strategy=data.get('randomization_strategy', 'simple_random'),
                randomization_config=data.get('randomization_config', {}),
                answer_randomization=data.get('answer_randomization', True),
                status='in_progress'
            )
            
            self.db_session.add(evaluation)
            self.db_session.commit()
            
            logger.info(f"Created evaluation {evaluation.id}")
            return evaluation
            
        except Exception as e:
            logger.exception(f"Error creating evaluation: {str(e)}")
            self.db_session.rollback()
            return None
    
    def get_evaluation(self, evaluation_id: int) -> Optional[Evaluation]:
        """Get evaluation by ID."""
        try:
            return Evaluation.query.get(evaluation_id)
        except Exception as e:
            logger.exception(f"Error getting evaluation {evaluation_id}: {str(e)}")
            return None
    
    def get_evaluations(self, filters: Dict[str, Any] = None, 
                       page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get evaluations with filters and pagination."""
        try:
            query = Evaluation.query
            
            if filters:
                if 'beneficiary_id' in filters:
                    query = query.filter_by(beneficiary_id=filters['beneficiary_id'])
                if 'trainer_id' in filters:
                    query = query.filter_by(trainer_id=filters['trainer_id'])
                if 'tenant_id' in filters:
                    query = query.filter_by(tenant_id=filters['tenant_id'])
                if 'status' in filters:
                    query = query.filter_by(status=filters['status'])
                if 'is_adaptive' in filters:
                    query = query.filter_by(is_adaptive=filters['is_adaptive'])
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'items': pagination.items,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
            
        except Exception as e:
            logger.exception(f"Error getting evaluations: {str(e)}")
            return {
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0
            }
    
    def update_evaluation(self, evaluation_id: int, data: Dict[str, Any]) -> Optional[Evaluation]:
        """Update evaluation."""
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            if not evaluation:
                return None
            
            # Update allowed fields
            updatable_fields = ['feedback', 'strengths', 'weaknesses', 
                              'recommendations', 'score', 'status']
            
            for field in updatable_fields:
                if field in data:
                    setattr(evaluation, field, data[field])
            
            # Update timestamps
            if data.get('status') == 'completed' and not evaluation.completed_at:
                evaluation.completed_at = datetime.utcnow()
            elif data.get('status') == 'reviewed' and not evaluation.reviewed_at:
                evaluation.reviewed_at = datetime.utcnow()
            
            self.db_session.commit()
            
            logger.info(f"Updated evaluation {evaluation_id}")
            return evaluation
            
        except Exception as e:
            logger.exception(f"Error updating evaluation {evaluation_id}: {str(e)}")
            self.db_session.rollback()
            return None
    
    def submit_response(self, evaluation_id: int, responses: List[Dict[str, Any]]) -> bool:
        """Submit evaluation responses."""
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            if not evaluation:
                return False
            
            # Store responses
            evaluation.responses = responses
            
            # Calculate score
            evaluation.calculate_score()
            
            # Update status
            evaluation.status = 'completed'
            evaluation.completed_at = datetime.utcnow()
            
            self.db_session.commit()
            
            logger.info(f"Submitted responses for evaluation {evaluation_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error submitting responses: {str(e)}")
            self.db_session.rollback()
            return False
    
    def delete_evaluation(self, evaluation_id: int) -> bool:
        """Delete evaluation."""
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            if not evaluation:
                return False
            
            self.db_session.delete(evaluation)
            self.db_session.commit()
            
            logger.info(f"Deleted evaluation {evaluation_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Error deleting evaluation {evaluation_id}: {str(e)}")
            self.db_session.rollback()
            return False
    
    def get_beneficiary_evaluations(self, beneficiary_id: int) -> List[Evaluation]:
        """Get all evaluations for a beneficiary."""
        try:
            return Evaluation.query.filter_by(beneficiary_id=beneficiary_id)\
                                 .order_by(Evaluation.created_at.desc())\
                                 .all()
        except Exception as e:
            logger.exception(f"Error getting beneficiary evaluations: {str(e)}")
            return []
    
    def get_evaluation_statistics(self, evaluation_id: int) -> Dict[str, Any]:
        """Get statistics for an evaluation."""
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            if not evaluation:
                return {}
            
            stats = {
                'score': evaluation.score,
                'status': evaluation.status,
                'total_questions': len(evaluation.responses) if evaluation.responses else 0,
                'correct_answers': sum(1 for r in (evaluation.responses or []) if r.get('is_correct')),
                'completion_time': None,
                'average_response_time': None
            }
            
            # Calculate completion time
            if evaluation.completed_at and evaluation.created_at:
                stats['completion_time'] = (evaluation.completed_at - evaluation.created_at).total_seconds()
            
            return stats
            
        except Exception as e:
            logger.exception(f"Error getting evaluation statistics: {str(e)}")
            return {}