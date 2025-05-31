"""Factory for creating evaluation service instances."""

from app.services.evaluation_service_refactored import EvaluationServiceRefactored
from app import db


class EvaluationServiceFactory:
    """Factory for creating evaluation service instances."""
    
    @staticmethod
    def create():
        """Create an evaluation service instance with all dependencies."""
        return EvaluationServiceRefactored(db.session)