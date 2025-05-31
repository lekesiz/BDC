"""Test evaluation schemas for coverage."""
import pytest
from datetime import datetime
from marshmallow import ValidationError
from app.schemas.evaluation import (
    QuestionSchema,
    QuestionCreateSchema, 
    QuestionUpdateSchema,
    EvaluationSchema,
    EvaluationCreateSchema,
    EvaluationUpdateSchema,
    TestSessionSchema,
    TestSessionCreateSchema,
    ResponseSchema,
    ResponseCreateSchema,
    AIFeedbackSchema,
    AIFeedbackUpdateSchema
)


class TestQuestionSchemas:
    """Test Question schemas."""
    
    def test_question_schema_dump(self):
        """Test question schema serialization."""
        schema = QuestionSchema()
        data = {
            'id': 1,
            'evaluation_id': 2,
            'text': 'What is Python?',
            'type': 'multiple_choice',
            'options': {'a': 'Language', 'b': 'Snake', 'c': 'Both'},
            'correct_answer': 'c',
            'explanation': 'Python is both',
            'category': 'basics',
            'difficulty': 'easy',
            'points': 1.0,
            'order': 1
        }
        
        result = schema.dump(data)
        assert result['text'] == 'What is Python?'
        assert result['type'] == 'multiple_choice'
    
    def test_question_create_schema(self):
        """Test question creation schema."""
        schema = QuestionCreateSchema()
        data = {
            'text': 'What is Django?',
            'type': 'text',
            'category': 'frameworks',
            'difficulty': 'medium',
            'points': 2.0
        }
        
        result = schema.load(data)
        assert result['text'] == 'What is Django?'
        assert result['type'] == 'text'
    
    def test_question_update_schema(self):
        """Test question update schema."""
        schema = QuestionUpdateSchema()
        data = {
            'text': 'Updated question text',
            'points': 3.0
        }
        
        result = schema.load(data)
        assert result['text'] == 'Updated question text'
        assert result['points'] == 3.0


class TestEvaluationSchemas:
    """Test Evaluation schemas."""
    
    def test_evaluation_schema_dump(self):
        """Test evaluation schema dump."""
        schema = EvaluationSchema()
        data = {
            'id': 1,
            'beneficiary_id': 2,
            'trainer_id': 3,
            'tenant_id': 4,
            'score': 85.5,
            'feedback': 'Good progress',
            'status': 'completed',
            'created_at': datetime.utcnow()
        }
        
        result = schema.dump(data)
        assert result['id'] == 1
        assert result['score'] == 85.5
    
    def test_evaluation_create_schema(self):
        """Test evaluation creation."""
        schema = EvaluationCreateSchema()
        data = {
            'beneficiary_id': 1,
            'trainer_id': 2,
            'test_id': 3,
            'score': 90.0,
            'feedback': 'Excellent work'
        }
        
        result = schema.load(data)
        assert result['beneficiary_id'] == 1
        assert result['score'] == 90.0
    
    def test_evaluation_update_schema(self):
        """Test evaluation update."""
        schema = EvaluationUpdateSchema()
        data = {
            'score': 95.0,
            'feedback': 'Updated feedback',
            'status': 'completed'
        }
        
        result = schema.load(data)
        assert result['score'] == 95.0
        assert result['status'] == 'completed'


class TestTestSessionSchemas:
    """Test TestSession schemas."""
    
    def test_test_session_schema_dump(self):
        """Test session schema dump."""
        schema = TestSessionSchema()
        data = {
            'id': 1,
            'evaluation_id': 2,
            'beneficiary_id': 3,
            'started_at': datetime.utcnow(),
            'completed_at': datetime.utcnow(),
            'duration_minutes': 60,
            'status': 'completed'
        }
        
        result = schema.dump(data)
        assert result['id'] == 1
        assert result['duration_minutes'] == 60
    
    def test_test_session_create_schema(self):
        """Test session creation."""
        schema = TestSessionCreateSchema()
        data = {
            'evaluation_id': 1,
            'beneficiary_id': 2
        }
        
        result = schema.load(data)
        assert result['evaluation_id'] == 1
        assert result['beneficiary_id'] == 2


class TestResponseSchemas:
    """Test Response schemas."""
    
    def test_response_schema_dump(self):
        """Test response schema dump."""
        schema = ResponseSchema()
        data = {
            'id': 1,
            'session_id': 2,
            'question_id': 3,
            'answer': 'My answer',
            'is_correct': True,
            'points_earned': 2.0,
            'time_taken_seconds': 45
        }
        
        result = schema.dump(data)
        assert result['answer'] == 'My answer'
        assert result['is_correct'] is True
    
    def test_response_create_schema(self):
        """Test response creation."""
        schema = ResponseCreateSchema()
        data = {
            'session_id': 1,
            'question_id': 2,
            'answer': 'User response'
        }
        
        result = schema.load(data)
        assert result['session_id'] == 1
        assert result['answer'] == 'User response'


class TestAIFeedbackSchemas:
    """Test AI Feedback schemas."""
    
    def test_ai_feedback_schema_dump(self):
        """Test AI feedback schema dump."""
        schema = AIFeedbackSchema()
        data = {
            'id': 1,
            'evaluation_id': 2,
            'strengths': 'Good understanding',
            'weaknesses': 'Needs practice',
            'recommendations': 'Study more',
            'overall_assessment': 'Satisfactory',
            'confidence_score': 0.85,
            'generated_at': datetime.utcnow()
        }
        
        result = schema.dump(data)
        assert result['strengths'] == 'Good understanding'
        assert result['confidence_score'] == 0.85
    
    def test_ai_feedback_update_schema(self):
        """Test AI feedback update."""
        schema = AIFeedbackUpdateSchema()
        data = {
            'recommendations': 'Updated recommendations',
            'confidence_score': 0.90
        }
        
        result = schema.load(data)
        assert result['recommendations'] == 'Updated recommendations'
        assert result['confidence_score'] == 0.90


class TestSchemaValidations:
    """Test schema validations."""
    
    def test_question_type_validation(self):
        """Test question type validation."""
        schema = QuestionCreateSchema()
        
        # Invalid type
        data = {
            'text': 'Question?',
            'type': 'invalid_type'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'type' in exc_info.value.messages
    
    def test_difficulty_validation(self):
        """Test difficulty validation."""
        schema = QuestionCreateSchema()
        
        # Valid difficulties
        for difficulty in ['easy', 'medium', 'hard']:
            data = {
                'text': 'Question?',
                'type': 'text',
                'difficulty': difficulty
            }
            result = schema.load(data)
            assert result['difficulty'] == difficulty
    
    def test_evaluation_score_range(self):
        """Test evaluation score validation."""
        schema = EvaluationCreateSchema()
        
        # Test various scores
        for score in [0, 50.5, 100]:
            data = {
                'beneficiary_id': 1,
                'trainer_id': 2,
                'score': score
            }
            result = schema.load(data)
            assert result['score'] == score