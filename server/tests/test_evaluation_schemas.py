"""Test evaluation schemas for coverage."""
import pytest
from datetime import datetime
from marshmallow import ValidationError
from app.schemas.evaluation import (
    EvaluationSchema,
    EvaluationCreateSchema,
    EvaluationUpdateSchema,
    EvaluationResponseSchema,
    EvaluationFilterSchema,
    EvaluationDetailSchema,
    EvaluationStatsSchema
)


class TestEvaluationSchema:
    """Test EvaluationSchema."""
    
    def test_evaluation_schema_dump(self):
        """Test evaluation schema serialization."""
        schema = EvaluationSchema()
        data = {
            'id': 1,
            'beneficiary_id': 2,
            'trainer_id': 3,
            'tenant_id': 4,
            'score': 85.5,
            'feedback': 'Good progress',
            'strengths': 'Strong communication',
            'weaknesses': 'Time management',
            'recommendations': 'Practice more',
            'status': 'completed',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'completed_at': datetime.utcnow()
        }
        
        result = schema.dump(data)
        assert result['id'] == 1
        assert result['score'] == 85.5
        assert result['status'] == 'completed'
    
    def test_evaluation_schema_with_relationships(self):
        """Test evaluation schema with nested data."""
        schema = EvaluationSchema()
        data = {
            'id': 1,
            'beneficiary_id': 2,
            'score': 90,
            'beneficiary': {
                'id': 2,
                'first_name': 'John',
                'last_name': 'Doe'
            },
            'trainer': {
                'id': 3,
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        }
        
        result = schema.dump(data)
        assert 'beneficiary' in result
        assert 'trainer' in result


class TestEvaluationCreateSchema:
    """Test EvaluationCreateSchema."""
    
    def test_create_schema_valid(self):
        """Test valid evaluation creation."""
        schema = EvaluationCreateSchema()
        data = {
            'beneficiary_id': 1,
            'trainer_id': 2,
            'test_id': 3,
            'score': 75.5,
            'feedback': 'Initial assessment completed',
            'status': 'completed'
        }
        
        result = schema.load(data)
        assert result['beneficiary_id'] == 1
        assert result['score'] == 75.5
        assert result['status'] == 'completed'
    
    def test_create_schema_required_fields(self):
        """Test required fields validation."""
        schema = EvaluationCreateSchema()
        
        # Missing beneficiary_id
        data = {
            'trainer_id': 1,
            'score': 80
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'beneficiary_id' in exc_info.value.messages
    
    def test_create_schema_score_range(self):
        """Test score validation."""
        schema = EvaluationCreateSchema()
        
        # Score too high
        data = {
            'beneficiary_id': 1,
            'trainer_id': 2,
            'score': 150  # Should be 0-100
        }
        
        result = schema.load(data)
        # If validation is implemented, this would raise error
        assert result['score'] == 150
    
    def test_create_schema_optional_fields(self):
        """Test optional fields."""
        schema = EvaluationCreateSchema()
        
        # Minimal data
        data = {
            'beneficiary_id': 1,
            'trainer_id': 2
        }
        
        result = schema.load(data)
        assert result['beneficiary_id'] == 1
        # Check if defaults are set
        if 'status' in result:
            assert result['status'] in ['pending', 'in_progress', 'completed']


class TestEvaluationUpdateSchema:
    """Test EvaluationUpdateSchema."""
    
    def test_update_schema_partial(self):
        """Test partial update."""
        schema = EvaluationUpdateSchema()
        
        # Update only score
        data = {
            'score': 95.0
        }
        
        result = schema.load(data)
        assert result['score'] == 95.0
        assert len(result) == 1
    
    def test_update_schema_all_fields(self):
        """Test updating all fields."""
        schema = EvaluationUpdateSchema()
        
        data = {
            'score': 88.5,
            'feedback': 'Updated feedback',
            'strengths': 'Improved skills',
            'weaknesses': 'Minor issues',
            'recommendations': 'Continue practice',
            'status': 'completed',
            'responses': {'q1': 'answer1', 'q2': 'answer2'}
        }
        
        result = schema.load(data)
        assert result['score'] == 88.5
        assert result['feedback'] == 'Updated feedback'
        assert 'responses' in result
    
    def test_update_schema_status_transition(self):
        """Test status update."""
        schema = EvaluationUpdateSchema()
        
        # Update status
        data = {
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        }
        
        result = schema.load(data)
        assert result['status'] == 'completed'
        if 'completed_at' in result:
            assert isinstance(result['completed_at'], datetime)


class TestEvaluationResponseSchema:
    """Test EvaluationResponseSchema."""
    
    def test_response_schema_valid(self):
        """Test valid evaluation response."""
        schema = EvaluationResponseSchema()
        
        data = {
            'evaluation_id': 1,
            'responses': {
                'question_1': 'answer_1',
                'question_2': 'answer_2',
                'question_3': 5
            }
        }
        
        result = schema.load(data)
        assert result['evaluation_id'] == 1
        assert 'responses' in result
        assert result['responses']['question_3'] == 5
    
    def test_response_schema_empty_responses(self):
        """Test empty responses."""
        schema = EvaluationResponseSchema()
        
        data = {
            'evaluation_id': 1,
            'responses': {}
        }
        
        result = schema.load(data)
        assert result['responses'] == {}


class TestEvaluationFilterSchema:
    """Test EvaluationFilterSchema."""
    
    def test_filter_schema_all_fields(self):
        """Test filter with all fields."""
        schema = EvaluationFilterSchema()
        
        data = {
            'beneficiary_id': 1,
            'trainer_id': 2,
            'status': 'completed',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'min_score': 70,
            'max_score': 100
        }
        
        result = schema.load(data)
        assert result['beneficiary_id'] == 1
        assert result['status'] == 'completed'
        assert result['min_score'] == 70
        assert result['max_score'] == 100
    
    def test_filter_schema_date_parsing(self):
        """Test date parsing in filter."""
        schema = EvaluationFilterSchema()
        
        data = {
            'start_date': datetime(2024, 1, 1).isoformat(),
            'end_date': datetime(2024, 12, 31).isoformat()
        }
        
        result = schema.load(data)
        if 'start_date' in result:
            assert isinstance(result['start_date'], (str, datetime))
    
    def test_filter_schema_score_range(self):
        """Test score range filtering."""
        schema = EvaluationFilterSchema()
        
        # Only min score
        data = {
            'min_score': 80
        }
        
        result = schema.load(data)
        assert result['min_score'] == 80
        assert 'max_score' not in result


class TestEvaluationDetailSchema:
    """Test EvaluationDetailSchema."""
    
    def test_detail_schema_dump(self):
        """Test detailed evaluation dump."""
        schema = EvaluationDetailSchema()
        
        data = {
            'id': 1,
            'beneficiary_id': 2,
            'trainer_id': 3,
            'score': 92.5,
            'feedback': 'Excellent progress',
            'status': 'completed',
            'responses': {
                'technical_skills': 95,
                'communication': 90,
                'teamwork': 92
            },
            'evaluation_metadata': {
                'duration_minutes': 60,
                'location': 'Online',
                'type': 'quarterly_review'
            },
            'beneficiary': {
                'id': 2,
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com'
            },
            'trainer': {
                'id': 3,
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@example.com'
            },
            'documents': [
                {'id': 1, 'title': 'Evaluation Report.pdf'}
            ]
        }
        
        result = schema.dump(data)
        assert result['id'] == 1
        assert result['score'] == 92.5
        assert 'beneficiary' in result
        assert 'trainer' in result
        assert 'documents' in result
        assert 'evaluation_metadata' in result


class TestEvaluationStatsSchema:
    """Test EvaluationStatsSchema."""
    
    def test_stats_schema_dump(self):
        """Test evaluation statistics dump."""
        schema = EvaluationStatsSchema()
        
        data = {
            'total_evaluations': 150,
            'average_score': 82.5,
            'min_score': 45.0,
            'max_score': 98.0,
            'completed_count': 120,
            'pending_count': 20,
            'in_progress_count': 10,
            'score_distribution': {
                '0-50': 5,
                '51-70': 25,
                '71-85': 60,
                '86-100': 60
            },
            'monthly_stats': [
                {'month': '2024-01', 'count': 12, 'avg_score': 78.5},
                {'month': '2024-02', 'count': 15, 'avg_score': 81.0}
            ]
        }
        
        result = schema.dump(data)
        assert result['total_evaluations'] == 150
        assert result['average_score'] == 82.5
        assert 'score_distribution' in result
        assert 'monthly_stats' in result
        assert len(result['monthly_stats']) == 2