"""Tests for Evaluation model."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.models.evaluation import Evaluation


class TestEvaluationModel:
    """Test the Evaluation model."""
    
    @pytest.fixture
    def evaluation(self):
        """Create a test evaluation."""
        eval = Evaluation(
            beneficiary_id=1,
            test_id=1,
            trainer_id=2,
            tenant_id=1,
            creator_id=2
        )
        # Set created_at and updated_at for testing
        eval.created_at = datetime(2024, 1, 1, 10, 0, 0)
        eval.updated_at = datetime(2024, 1, 1, 10, 0, 0)
        return eval
    
    def test_evaluation_creation(self, evaluation):
        """Test evaluation creation with basic fields."""
        assert evaluation.beneficiary_id == 1
        assert evaluation.test_id == 1
        assert evaluation.trainer_id == 2
        assert evaluation.tenant_id == 1
        assert evaluation.creator_id == 2
        assert evaluation.status == 'in_progress'
    
    def test_evaluation_defaults(self):
        """Test evaluation default values."""
        eval = Evaluation(beneficiary_id=1, test_id=1, trainer_id=1)
        assert eval.status == 'in_progress'
        assert eval.score is None
        assert eval.completed_at is None
        assert eval.reviewed_at is None
    
    def test_evaluation_to_dict(self, evaluation):
        """Test evaluation to_dict method."""
        evaluation.score = 85.5
        evaluation.feedback = 'Good job'
        evaluation.strengths = 'Strong analytical skills'
        evaluation.weaknesses = 'Time management'
        evaluation.recommendations = 'Practice more'
        evaluation.responses = [{'question_id': 1, 'answer': 'A', 'is_correct': True}]
        evaluation.evaluation_metadata = {'duration': 3600}
        
        result = evaluation.to_dict()
        
        assert result['id'] == evaluation.id
        assert result['beneficiary_id'] == 1
        assert result['test_id'] == 1
        assert result['trainer_id'] == 2
        assert result['score'] == 85.5
        assert result['feedback'] == 'Good job'
        assert result['strengths'] == 'Strong analytical skills'
        assert result['weaknesses'] == 'Time management'
        assert result['recommendations'] == 'Practice more'
        assert result['responses'] == [{'question_id': 1, 'answer': 'A', 'is_correct': True}]
        assert result['metadata'] == {'duration': 3600}
        assert result['status'] == 'in_progress'
        assert result['completed_at'] is None
        assert result['reviewed_at'] is None
        assert result['created_at'] == '2024-01-01T10:00:00'
        assert result['updated_at'] == '2024-01-01T10:00:00'
    
    def test_evaluation_to_dict_with_dates(self, evaluation):
        """Test evaluation to_dict with completion and review dates."""
        evaluation.completed_at = datetime(2024, 1, 1, 11, 0, 0)
        evaluation.reviewed_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = evaluation.to_dict()
        
        assert result['completed_at'] == '2024-01-01T11:00:00'
        assert result['reviewed_at'] == '2024-01-01T12:00:00'
    
    def test_calculate_score_no_responses(self, evaluation):
        """Test score calculation with no responses."""
        evaluation.responses = None
        score = evaluation.calculate_score()
        assert score == 0
        
        evaluation.responses = []
        score = evaluation.calculate_score()
        assert score == 0
    
    def test_calculate_score_all_correct(self, evaluation):
        """Test score calculation with all correct answers."""
        evaluation.responses = [
            {'question_id': 1, 'answer': 'A', 'is_correct': True},
            {'question_id': 2, 'answer': 'B', 'is_correct': True},
            {'question_id': 3, 'answer': 'C', 'is_correct': True}
        ]
        
        score = evaluation.calculate_score()
        
        assert score == 100.0
        assert evaluation.score == 100.0
    
    def test_calculate_score_partial(self, evaluation):
        """Test score calculation with partial correct answers."""
        evaluation.responses = [
            {'question_id': 1, 'answer': 'A', 'is_correct': True},
            {'question_id': 2, 'answer': 'B', 'is_correct': False},
            {'question_id': 3, 'answer': 'C', 'is_correct': True},
            {'question_id': 4, 'answer': 'D', 'is_correct': False}
        ]
        
        score = evaluation.calculate_score()
        
        assert score == 50.0
        assert evaluation.score == 50.0
    
    def test_calculate_score_no_correct_field(self, evaluation):
        """Test score calculation when is_correct field is missing."""
        evaluation.responses = [
            {'question_id': 1, 'answer': 'A'},
            {'question_id': 2, 'answer': 'B', 'is_correct': True},
            {'question_id': 3, 'answer': 'C'}
        ]
        
        score = evaluation.calculate_score()
        
        # Only 1 out of 3 has is_correct=True, others default to False
        assert score == pytest.approx(33.33, rel=0.1)
    
    def test_complete(self, evaluation):
        """Test marking evaluation as completed."""
        assert evaluation.status == 'in_progress'
        assert evaluation.completed_at is None
        
        evaluation.complete()
        
        assert evaluation.status == 'completed'
        assert evaluation.completed_at is not None
        assert isinstance(evaluation.completed_at, datetime)
    
    def test_review(self, evaluation):
        """Test marking evaluation as reviewed."""
        evaluation.status = 'completed'
        assert evaluation.reviewed_at is None
        
        evaluation.review()
        
        assert evaluation.status == 'reviewed'
        assert evaluation.reviewed_at is not None
        assert isinstance(evaluation.reviewed_at, datetime)
    
    def test_relationships(self, evaluation):
        """Test evaluation relationships."""
        assert hasattr(evaluation, 'beneficiary')
        assert hasattr(evaluation, 'test')
        assert hasattr(evaluation, 'trainer')
        assert hasattr(evaluation, 'creator')
        assert hasattr(evaluation, 'tenant')