"""Evaluation repository implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.evaluation_repository_interface import IEvaluationRepository
from app.models import Evaluation
from app.extensions import db


class EvaluationRepository(BaseRepository[Evaluation], IEvaluationRepository):
    """Evaluation repository implementation."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize evaluation repository."""
        super().__init__(Evaluation, db_session)
    
    def find_by_beneficiary_id(self, beneficiary_id: int) -> List[Evaluation]:
        """Find evaluations by beneficiary ID."""
        return self.db_session.query(Evaluation).filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(Evaluation.created_at.desc()).all()
    
    def find_by_trainer_id(self, trainer_id: int) -> List[Evaluation]:
        """Find evaluations by trainer ID."""
        return self.db_session.query(Evaluation).filter_by(
            trainer_id=trainer_id
        ).order_by(Evaluation.created_at.desc()).all()
    
    def find_by_status(self, status: str) -> List[Evaluation]:
        """Find evaluations by status."""
        return self.db_session.query(Evaluation).filter_by(
            status=status
        ).order_by(Evaluation.created_at.desc()).all()
    
    def find_by_test_id(self, test_id: int) -> List[Evaluation]:
        """Find evaluations by test ID."""
        return self.db_session.query(Evaluation).filter_by(
            test_id=test_id
        ).order_by(Evaluation.created_at.desc()).all()
    
    def find_by_tenant_id(self, tenant_id: int) -> List[Evaluation]:
        """Find evaluations by tenant ID."""
        return self.db_session.query(Evaluation).filter_by(
            tenant_id=tenant_id
        ).order_by(Evaluation.created_at.desc()).all()
    
    def update_score(self, evaluation_id: int, score: float) -> bool:
        """Update evaluation score."""
        try:
            evaluation = self.find_by_id(evaluation_id)
            if not evaluation:
                return False
            
            evaluation.score = score
            evaluation.updated_at = datetime.utcnow()
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def update_status(self, evaluation_id: int, status: str) -> bool:
        """Update evaluation status."""
        try:
            evaluation = self.find_by_id(evaluation_id)
            if not evaluation:
                return False
            
            evaluation.status = status
            evaluation.updated_at = datetime.utcnow()
            
            if status == 'completed':
                evaluation.completed_at = datetime.utcnow()
            elif status == 'reviewed':
                evaluation.reviewed_at = datetime.utcnow()
            
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def add_feedback(self, evaluation_id: int, feedback: str, 
                    strengths: Optional[str] = None, 
                    weaknesses: Optional[str] = None,
                    recommendations: Optional[str] = None) -> bool:
        """Add feedback to evaluation."""
        try:
            evaluation = self.find_by_id(evaluation_id)
            if not evaluation:
                return False
            
            evaluation.feedback = feedback
            if strengths:
                evaluation.strengths = strengths
            if weaknesses:
                evaluation.weaknesses = weaknesses
            if recommendations:
                evaluation.recommendations = recommendations
            
            evaluation.updated_at = datetime.utcnow()
            self.db_session.flush()
            return True
        except Exception:
            return False
    
    def create(self, **kwargs) -> Evaluation:
        """Create a new evaluation."""
        evaluation = Evaluation(**kwargs)
        self.db_session.add(evaluation)
        self.db_session.flush()
        return evaluation
    
    def update(self, evaluation_id: int, **kwargs) -> Optional[Evaluation]:
        """Update evaluation by ID."""
        evaluation = self.find_by_id(evaluation_id)
        if not evaluation:
            return None
        
        for key, value in kwargs.items():
            if hasattr(evaluation, key):
                setattr(evaluation, key, value)
        
        evaluation.updated_at = datetime.utcnow()
        self.db_session.flush()
        return evaluation
    
    def delete(self, evaluation_id: int) -> bool:
        """Delete evaluation by ID."""
        evaluation = self.find_by_id(evaluation_id)
        if not evaluation:
            return False
        
        self.db_session.delete(evaluation)
        self.db_session.flush()
        return True
    
    def save(self, evaluation: Evaluation) -> Evaluation:
        """Save evaluation instance."""
        self.db_session.add(evaluation)
        self.db_session.flush()
        return evaluation
    
    def find_all(self, limit: int = None, offset: int = None) -> List[Evaluation]:
        """Find all evaluations with optional pagination."""
        query = self.db_session.query(Evaluation).order_by(Evaluation.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count(self) -> int:
        """Count total evaluations."""
        return self.db_session.query(Evaluation).count()