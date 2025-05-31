"""Comprehensive tests for the refactored evaluation service."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock

from app.services.evaluation_service_refactored import (
    EvaluationServiceRefactored,
    EvaluationStatus,
    EvaluationType,
    SessionStatus,
    PaginationResult
)
from app.exceptions import NotFoundException, ForbiddenException, ValidationException


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.delete = Mock()
    session.refresh = Mock()
    session.flush = Mock()
    return session


@pytest.fixture
def evaluation_service(mock_db_session):
    """Create evaluation service instance with mocked dependencies."""
    return EvaluationServiceRefactored(mock_db_session)


@pytest.fixture
def sample_trainer():
    """Create a sample trainer user."""
    trainer = Mock()
    trainer.id = 1
    trainer.role = 'trainer'
    trainer.first_name = 'John'
    trainer.last_name = 'Doe'
    trainer.email = 'trainer@example.com'
    return trainer


@pytest.fixture
def sample_student():
    """Create a sample student user."""
    student = Mock()
    student.id = 2
    student.role = 'student'
    student.first_name = 'Jane'
    student.last_name = 'Smith'
    student.email = 'student@example.com'
    return student


@pytest.fixture
def sample_evaluation():
    """Create a sample evaluation/test set."""
    evaluation = Mock()
    evaluation.id = 100
    evaluation.title = 'Test Evaluation'
    evaluation.description = 'Test description'
    evaluation.type = EvaluationType.ASSESSMENT.value
    evaluation.status = EvaluationStatus.PUBLISHED.value
    evaluation.creator_id = 1
    evaluation.tenant_id = 1
    evaluation.is_template = False
    evaluation.passing_score = 70
    evaluation.created_at = datetime.now(timezone.utc)
    evaluation.updated_at = datetime.now(timezone.utc)
    return evaluation


@pytest.fixture
def sample_question():
    """Create a sample question."""
    question = Mock()
    question.id = 10
    question.test_set_id = 100
    question.text = 'What is 2 + 2?'
    question.type = 'multiple_choice'
    question.points = 5
    question.order = 1
    question.options = ['3', '4', '5', '6']
    question.correct_answer = '4'
    return question


@pytest.fixture
def sample_session(sample_evaluation, sample_student):
    """Create a sample test session."""
    session = Mock()
    session.id = 1000
    session.test_set_id = sample_evaluation.id
    session.user_id = sample_student.id
    session.beneficiary_id = sample_student.id
    session.status = SessionStatus.IN_PROGRESS.value
    session.score = 0
    session.total_score = 0
    session.started_at = datetime.now(timezone.utc)
    return session


class TestEvaluationManagement:
    """Test cases for evaluation management."""
    
    def test_get_evaluations_with_filters(
        self,
        evaluation_service,
        mock_db_session,
        sample_evaluation
    ):
        """Test getting evaluations with various filters."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Mock pagination
        mock_pagination = Mock()
        mock_pagination.items = [sample_evaluation]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.page = 1
        mock_query.paginate.return_value = mock_pagination
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = evaluation_service.get_evaluations(
            tenant_id=1,
            creator_id=1,
            status=EvaluationStatus.PUBLISHED.value,
            page=1,
            per_page=10
        )
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0] == sample_evaluation
    
    def test_get_evaluation_by_id_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_evaluation
    ):
        """Test getting evaluation by ID successfully."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_evaluation
        
        # Execute
        result = evaluation_service.get_evaluation_by_id(sample_evaluation.id)
        
        # Assert
        assert result == sample_evaluation
    
    def test_get_evaluation_by_id_not_found(
        self,
        evaluation_service,
        mock_db_session
    ):
        """Test getting non-existent evaluation."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = None
        
        # Execute and assert
        with pytest.raises(NotFoundException) as exc_info:
            evaluation_service.get_evaluation_by_id(999)
        
        assert "Evaluation 999 not found" in str(exc_info.value)
    
    def test_create_evaluation_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer
    ):
        """Test successful evaluation creation."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Evaluation data
        data = {
            'title': 'New Evaluation',
            'type': EvaluationType.QUIZ.value,
            'tenant_id': 1,
            'description': 'A new quiz',
            'questions': [
                {
                    'text': 'Question 1',
                    'type': 'multiple_choice',
                    'options': ['A', 'B', 'C'],
                    'correct_answer': 'A'
                }
            ]
        }
        
        # Execute
        result = evaluation_service.create_evaluation(
            creator_id=sample_trainer.id,
            data=data
        )
        
        # Assert
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called_once()
    
    def test_create_evaluation_student_forbidden(
        self,
        evaluation_service,
        mock_db_session,
        sample_student
    ):
        """Test that students cannot create evaluations."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_student
        
        # Execute and assert
        with pytest.raises(ForbiddenException) as exc_info:
            evaluation_service.create_evaluation(
                creator_id=sample_student.id,
                data={'title': 'Test'}
            )
        
        assert "You do not have permission to create evaluations" in str(exc_info.value)
    
    def test_create_evaluation_missing_required_fields(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer
    ):
        """Test evaluation creation with missing fields."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_trainer
        
        # Missing required fields
        data = {
            'title': 'New Evaluation'
            # Missing type and tenant_id
        }
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            evaluation_service.create_evaluation(
                creator_id=sample_trainer.id,
                data=data
            )
        
        assert "Missing required field" in str(exc_info.value)
    
    def test_update_evaluation_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer,
        sample_evaluation
    ):
        """Test successful evaluation update."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_evaluation
        ]
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        # Execute
        result = evaluation_service.update_evaluation(
            evaluation_id=sample_evaluation.id,
            user_id=sample_trainer.id,
            data=update_data
        )
        
        # Assert
        assert sample_evaluation.title == 'Updated Title'
        assert sample_evaluation.description == 'Updated description'
        mock_db_session.commit.assert_called_once()
    
    def test_delete_evaluation_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer,
        sample_evaluation
    ):
        """Test successful evaluation deletion."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_evaluation
        ]
        
        # No active sessions
        mock_db_session.query().filter_by().count.return_value = 0
        
        # Mock cascade delete
        mock_db_session.query().filter_by().all.return_value = []  # No sessions
        mock_db_session.query().filter().delete.return_value = None
        mock_db_session.query().filter_by().delete.return_value = None
        
        # Execute
        result = evaluation_service.delete_evaluation(
            evaluation_id=sample_evaluation.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        assert result['message'] == 'Evaluation deleted successfully'
        mock_db_session.commit.assert_called_once()
    
    def test_delete_evaluation_with_active_sessions(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer,
        sample_evaluation
    ):
        """Test deletion fails with active sessions."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_evaluation
        ]
        
        # Has active sessions
        mock_db_session.query().filter_by().count.return_value = 2
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            evaluation_service.delete_evaluation(
                evaluation_id=sample_evaluation.id,
                user_id=sample_trainer.id
            )
        
        assert "Cannot delete evaluation with active sessions" in str(exc_info.value)


class TestQuestionManagement:
    """Test cases for question management."""
    
    def test_get_questions_for_evaluation(
        self,
        evaluation_service,
        mock_db_session,
        sample_evaluation,
        sample_question
    ):
        """Test getting questions for an evaluation."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_evaluation
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Mock pagination
        mock_pagination = Mock()
        mock_pagination.items = [sample_question]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.page = 1
        mock_query.paginate.return_value = mock_pagination
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = evaluation_service.get_questions_for_evaluation(
            evaluation_id=sample_evaluation.id
        )
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 1
        assert len(result.items) == 1
    
    def test_create_question_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer,
        sample_evaluation
    ):
        """Test successful question creation."""
        # Setup mocks
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_evaluation
        ]
        
        # Mock max order query
        mock_db_session.query().filter_by().with_entities().scalar.return_value = 3
        
        question_data = {
            'text': 'New Question',
            'type': 'multiple_choice',
            'options': ['A', 'B', 'C'],
            'correct_answer': 'B',
            'points': 10
        }
        
        # Execute
        result = evaluation_service.create_question(
            evaluation_id=sample_evaluation.id,
            user_id=sample_trainer.id,
            data=question_data
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestSessionManagement:
    """Test cases for test session management."""
    
    def test_create_test_session_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_student,
        sample_evaluation
    ):
        """Test successful test session creation."""
        # Setup mocks
        sample_beneficiary = Mock()
        sample_beneficiary.id = 10
        sample_beneficiary.user_id = sample_student.id
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_student,
            sample_evaluation,
            sample_beneficiary  # For beneficiary lookup
        ]
        
        # Execute
        result = evaluation_service.create_test_session(
            user_id=sample_student.id,
            evaluation_id=sample_evaluation.id
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_submit_response_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_student,
        sample_session,
        sample_question
    ):
        """Test successful response submission."""
        # Setup mocks
        sample_beneficiary = Mock()
        sample_beneficiary.id = sample_session.beneficiary_id
        sample_beneficiary.user_id = sample_student.id
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_student,
            sample_session,
            sample_beneficiary,  # For access check
            sample_question,
            None  # No existing response
        ]
        
        response_data = {'answer': '4'}
        
        # Execute
        result = evaluation_service.submit_response(
            session_id=sample_session.id,
            question_id=sample_question.id,
            user_id=sample_student.id,
            response_data=response_data
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_submit_response_to_completed_session(
        self,
        evaluation_service,
        mock_db_session,
        sample_student,
        sample_session,
        sample_question
    ):
        """Test response submission to completed session fails."""
        # Setup mocks
        sample_session.status = SessionStatus.COMPLETED.value
        
        sample_beneficiary = Mock()
        sample_beneficiary.id = sample_session.beneficiary_id
        sample_beneficiary.user_id = sample_student.id
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_student,
            sample_session,
            sample_beneficiary,  # For access check
            sample_question
        ]
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            evaluation_service.submit_response(
                session_id=sample_session.id,
                question_id=sample_question.id,
                user_id=sample_student.id,
                response_data={'answer': 'test'}
            )
        
        assert "Cannot submit response to completed session" in str(exc_info.value)
    
    def test_complete_session_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_student,
        sample_session
    ):
        """Test successful session completion."""
        # Setup mocks
        sample_beneficiary = Mock()
        sample_beneficiary.id = sample_session.beneficiary_id
        sample_beneficiary.user_id = sample_student.id
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_student,
            sample_session,
            sample_beneficiary,  # For access check
            None  # No existing AI feedback
        ]
        
        # Mock score calculations
        mock_db_session.query().filter_by().scalar.side_effect = [
            85.0,  # Session score
            100.0  # Total possible score
        ]
        
        # Execute
        result = evaluation_service.complete_session(
            session_id=sample_session.id,
            user_id=sample_student.id
        )
        
        # Assert
        assert sample_session.status == SessionStatus.COMPLETED.value
        assert sample_session.score == 85.0
        assert sample_session.total_score == 100.0
        mock_db_session.commit.assert_called_once()
    
    def test_abandon_session_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_student,
        sample_session
    ):
        """Test successful session abandonment."""
        # Setup mocks
        sample_beneficiary = Mock()
        sample_beneficiary.id = sample_session.beneficiary_id
        sample_beneficiary.user_id = sample_student.id
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_student,
            sample_session,
            sample_beneficiary  # For access check
        ]
        
        # Execute
        result = evaluation_service.abandon_session(
            session_id=sample_session.id,
            user_id=sample_student.id
        )
        
        # Assert
        assert sample_session.status == SessionStatus.ABANDONED.value
        mock_db_session.commit.assert_called_once()


class TestAIFeedback:
    """Test cases for AI feedback functionality."""
    
    def test_generate_feedback_for_session_success(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer,
        sample_session
    ):
        """Test successful AI feedback generation."""
        # Setup mocks
        sample_session.status = SessionStatus.COMPLETED.value
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_session,
            None  # No existing feedback
        ]
        
        # Mock AI feedback generation
        mock_db_session.query().filter_by().all.return_value = []  # Mock responses and questions
        
        # Execute
        result = evaluation_service.generate_feedback_for_session(
            session_id=sample_session.id,
            user_id=sample_trainer.id
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_generate_feedback_session_not_completed(
        self,
        evaluation_service,
        mock_db_session,
        sample_trainer,
        sample_session
    ):
        """Test feedback generation fails for incomplete session."""
        # Setup mocks
        sample_session.status = SessionStatus.IN_PROGRESS.value
        
        mock_db_session.query().filter_by().first.side_effect = [
            sample_trainer,
            sample_session
        ]
        
        # Execute and assert
        with pytest.raises(ValidationException) as exc_info:
            evaluation_service.generate_feedback_for_session(
                session_id=sample_session.id,
                user_id=sample_trainer.id
            )
        
        assert "Session must be completed to generate feedback" in str(exc_info.value)