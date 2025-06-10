"""Factory for creating evaluation service instances."""

from app.services.evaluation_service import EvaluationService
from app import db


class EvaluationServiceFactory:
    """Factory for creating evaluation service instances."""
    
    @staticmethod
    def create():
        """Create an evaluation service instance with all dependencies."""
        return EvaluationService(db.session)