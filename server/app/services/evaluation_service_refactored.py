"""Refactored evaluation service with improved architecture."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

from sqlalchemy.orm import Session
from flask import current_app

from app.models.test import TestSet, Question, TestSession, Response, AIFeedback
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.exceptions import NotFoundException, ForbiddenException, ValidationException
# from app.utils.ai import generate_ai_feedback  # Import when available


class EvaluationStatus(Enum):
    """Evaluation status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EvaluationType(Enum):
    """Evaluation type enumeration."""
    ASSESSMENT = "assessment"
    QUIZ = "quiz"
    SURVEY = "survey"
    EXAM = "exam"


class SessionStatus(Enum):
    """Test session status enumeration."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class PaginationResult:
    """Pagination result wrapper."""
    items: List[Any]
    total: int
    pages: int
    current_page: int


class EvaluationServiceRefactored:
    """Refactored evaluation service with improved testability."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session
    
    # Evaluation/TestSet Management
    
    def get_evaluations(
        self,
        tenant_id: Optional[int] = None,
        creator_id: Optional[int] = None,
        beneficiary_id: Optional[int] = None,
        status: Optional[str] = None,
        evaluation_type: Optional[str] = None,
        is_template: Optional[bool] = None,
        page: int = 1,
        per_page: int = 10
    ) -> PaginationResult:
        """Get evaluations with filtering and pagination."""
        query = self.db.query(TestSet)
        
        # Apply filters
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        if creator_id:
            query = query.filter_by(creator_id=creator_id)
        if beneficiary_id:
            query = query.filter_by(beneficiary_id=beneficiary_id)
        if status:
            query = query.filter_by(status=status)
        if evaluation_type:
            query = query.filter_by(type=evaluation_type)
        if is_template is not None:
            query = query.filter_by(is_template=is_template)
        
        # Order by creation time
        query = query.order_by(TestSet.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return PaginationResult(
            items=pagination.items,
            total=pagination.total,
            pages=pagination.pages,
            current_page=pagination.page
        )
    
    def get_evaluation_by_id(self, evaluation_id: int) -> TestSet:
        """Get evaluation by ID or raise NotFoundException."""
        evaluation = self.db.query(TestSet).filter_by(id=evaluation_id).first()
        if not evaluation:
            raise NotFoundException(f"Evaluation {evaluation_id} not found")
        return evaluation
    
    def create_evaluation(self, creator_id: int, data: Dict[str, Any]) -> TestSet:
        """Create a new evaluation with validation."""
        # Validate creator
        creator = self._get_user_or_404(creator_id)
        self._validate_creator_permissions(creator)
        
        # Validate and prepare data
        validated_data = self._validate_evaluation_data(data)
        questions_data = validated_data.pop('questions', [])
        
        # Create evaluation
        evaluation = TestSet(**validated_data)
        evaluation.creator_id = creator_id
        evaluation.created_at = datetime.now(timezone.utc)
        
        self.db.add(evaluation)
        self.db.flush()  # Get ID before adding questions
        
        # Add questions if provided
        if questions_data:
            self._add_questions_to_evaluation(evaluation, questions_data)
        
        self.db.commit()
        self.db.refresh(evaluation)
        
        return evaluation
    
    def update_evaluation(
        self,
        evaluation_id: int,
        user_id: int,
        data: Dict[str, Any]
    ) -> TestSet:
        """Update an existing evaluation."""
        user = self._get_user_or_404(user_id)
        evaluation = self._get_evaluation_with_access_check(evaluation_id, user)
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'type', 'category', 
                         'instructions', 'time_limit', 'passing_score']
        
        for field in allowed_fields:
            if field in data:
                setattr(evaluation, field, data[field])
        
        # Update questions if provided
        if 'questions' in data:
            self._update_evaluation_questions(evaluation, data['questions'])
        
        evaluation.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(evaluation)
        
        return evaluation
    
    def delete_evaluation(self, evaluation_id: int, user_id: int) -> Dict[str, str]:
        """Delete an evaluation and related data."""
        user = self._get_user_or_404(user_id)
        evaluation = self._get_evaluation_with_access_check(evaluation_id, user)
        
        # Check if evaluation can be deleted
        if self._has_active_sessions(evaluation):
            raise ValidationException("Cannot delete evaluation with active sessions")
        
        # Delete in order: responses -> sessions -> questions -> evaluation
        self._cascade_delete_evaluation(evaluation)
        
        self.db.commit()
        
        return {'message': 'Evaluation deleted successfully'}
    
    # Question Management
    
    def get_questions_for_evaluation(
        self,
        evaluation_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> PaginationResult:
        """Get questions for a specific evaluation."""
        evaluation = self._get_evaluation_or_404(evaluation_id)
        
        query = self.db.query(Question).filter_by(test_set_id=evaluation_id)
        query = query.order_by(Question.order.asc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return PaginationResult(
            items=pagination.items,
            total=pagination.total,
            pages=pagination.pages,
            current_page=pagination.page
        )
    
    def create_question(
        self,
        evaluation_id: int,
        user_id: int,
        data: Dict[str, Any]
    ) -> Question:
        """Create a new question for an evaluation."""
        user = self._get_user_or_404(user_id)
        evaluation = self._get_evaluation_with_access_check(evaluation_id, user)
        
        # Validate question data
        validated_data = self._validate_question_data(data)
        
        # Set order if not provided
        if 'order' not in validated_data:
            validated_data['order'] = self._get_next_question_order(evaluation_id)
        
        question = Question(
            test_set_id=evaluation_id,
            **validated_data
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    # Test Session Management
    
    def create_test_session(
        self,
        user_id: int,
        evaluation_id: int,
        beneficiary_id: Optional[int] = None
    ) -> TestSession:
        """Create a new test session."""
        user = self._get_user_or_404(user_id)
        evaluation = self._get_evaluation_or_404(evaluation_id)
        
        # Validate session creation
        self._validate_session_creation(user, evaluation, beneficiary_id)
        
        # Create session
        # Get beneficiary_id for the user if not provided
        if not beneficiary_id:
            beneficiary = self.db.query(Beneficiary).filter_by(user_id=user_id).first()
            if beneficiary:
                beneficiary_id = beneficiary.id
            else:
                raise ValidationException("User does not have a beneficiary profile")
        
        session = TestSession(
            test_set_id=evaluation_id,
            beneficiary_id=beneficiary_id,
            status=SessionStatus.IN_PROGRESS.value,
            start_time=datetime.now(timezone.utc)
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_session_by_id(self, session_id: int) -> TestSession:
        """Get test session by ID."""
        session = self.db.query(TestSession).filter_by(id=session_id).first()
        if not session:
            raise NotFoundException(f"Session {session_id} not found")
        return session
    
    def submit_response(
        self,
        session_id: int,
        question_id: int,
        user_id: int,
        response_data: Dict[str, Any]
    ) -> Response:
        """Submit or update a response for a question."""
        user = self._get_user_or_404(user_id)
        session = self._get_session_with_access_check(session_id, user)
        question = self._get_question_or_404(question_id)
        
        # Validate response
        if session.status != SessionStatus.IN_PROGRESS.value:
            raise ValidationException("Cannot submit response to completed session")
        
        if question.test_set_id != session.test_set_id:
            raise ValidationException("Question does not belong to this evaluation")
        
        # Check if response already exists
        existing_response = self.db.query(Response).filter_by(
            session_id=session_id,
            question_id=question_id
        ).first()
        
        if existing_response:
            # Update existing response
            existing_response.answer = response_data.get('answer')
            existing_response.updated_at = datetime.now(timezone.utc)
            response = existing_response
        else:
            # Create new response
            response = Response(
                session_id=session_id,
                question_id=question_id,
                answer=response_data.get('answer'),
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(response)
        
        # Calculate score if question has correct answer
        if question.correct_answer:
            response.is_correct = response.answer == question.correct_answer
            response.score = question.points if response.is_correct else 0
        
        self.db.commit()
        self.db.refresh(response)
        
        return response
    
    def complete_session(self, session_id: int, user_id: int) -> TestSession:
        """Complete a test session and calculate final score."""
        user = self._get_user_or_404(user_id)
        session = self._get_session_with_access_check(session_id, user)
        
        if session.status != SessionStatus.IN_PROGRESS.value:
            raise ValidationException("Session is not in progress")
        
        # Calculate total score
        session.score = self._calculate_session_score(session_id)
        session.total_score = self._calculate_total_possible_score(session.test_set_id)
        session.status = SessionStatus.COMPLETED.value
        session.completed_at = datetime.now(timezone.utc)
        
        # Generate AI feedback if enabled
        if self._should_generate_ai_feedback(session):
            self._generate_session_feedback(session)
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def abandon_session(self, session_id: int, user_id: int) -> TestSession:
        """Mark a session as abandoned."""
        user = self._get_user_or_404(user_id)
        session = self._get_session_with_access_check(session_id, user)
        
        if session.status != SessionStatus.IN_PROGRESS.value:
            raise ValidationException("Session is not in progress")
        
        session.status = SessionStatus.ABANDONED.value
        session.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    # AI Feedback Management
    
    def generate_feedback_for_session(
        self,
        session_id: int,
        user_id: int
    ) -> AIFeedback:
        """Generate AI feedback for a completed session."""
        user = self._get_user_or_404(user_id)
        session = self._get_session_with_access_check(session_id, user)
        
        if session.status != SessionStatus.COMPLETED.value:
            raise ValidationException("Session must be completed to generate feedback")
        
        # Check if feedback already exists
        existing_feedback = self.db.query(AIFeedback).filter_by(
            session_id=session_id
        ).first()
        
        if existing_feedback:
            return existing_feedback
        
        # Generate AI feedback
        feedback_content = self._generate_ai_feedback_content(session)
        
        feedback = AIFeedback(
            session_id=session_id,
            summary=feedback_content,
            status='draft'
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        return feedback
    
    # Private helper methods
    
    def _get_user_or_404(self, user_id: int) -> User:
        """Get user or raise NotFoundException."""
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return user
    
    def _get_evaluation_or_404(self, evaluation_id: int) -> TestSet:
        """Get evaluation or raise NotFoundException."""
        evaluation = self.db.query(TestSet).filter_by(id=evaluation_id).first()
        if not evaluation:
            raise NotFoundException(f"Evaluation {evaluation_id} not found")
        return evaluation
    
    def _get_question_or_404(self, question_id: int) -> Question:
        """Get question or raise NotFoundException."""
        question = self.db.query(Question).filter_by(id=question_id).first()
        if not question:
            raise NotFoundException(f"Question {question_id} not found")
        return question
    
    def _get_session_or_404(self, session_id: int) -> TestSession:
        """Get session or raise NotFoundException."""
        session = self.db.query(TestSession).filter_by(id=session_id).first()
        if not session:
            raise NotFoundException(f"Session {session_id} not found")
        return session
    
    def _validate_creator_permissions(self, user: User) -> None:
        """Validate that user can create evaluations."""
        allowed_roles = ['trainer', 'admin', 'super_admin']
        if user.role not in allowed_roles:
            raise ForbiddenException("You do not have permission to create evaluations")
    
    def _validate_evaluation_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare evaluation data."""
        required_fields = ['title', 'type', 'tenant_id']
        
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field: {field}")
        
        # Validate type
        if data['type'] not in [t.value for t in EvaluationType]:
            raise ValidationException(f"Invalid evaluation type: {data['type']}")
        
        # Set defaults
        validated_data = {
            'title': data['title'],
            'type': data['type'],
            'tenant_id': data['tenant_id'],
            'description': data.get('description', ''),
            'category': data.get('category'),
            'instructions': data.get('instructions'),
            'time_limit': data.get('time_limit'),
            'passing_score': data.get('passing_score', 70),
            'is_template': data.get('is_template', False),
            'status': data.get('status', EvaluationStatus.DRAFT.value)
        }
        
        # Include questions if provided
        if 'questions' in data:
            validated_data['questions'] = data['questions']
        
        return validated_data
    
    def _validate_question_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate question data."""
        required_fields = ['text', 'type']
        
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"Missing required field: {field}")
        
        validated_data = {
            'text': data['text'],
            'type': data['type'],
            'points': data.get('points', 1),
            'order': data.get('order'),
            'options': data.get('options'),
            'correct_answer': data.get('correct_answer'),
            'explanation': data.get('explanation'),
            'category': data.get('category'),
            'difficulty': data.get('difficulty', 'medium')
        }
        
        # Validate options for multiple choice questions
        if data['type'] in ['multiple_choice', 'checkbox']:
            if not validated_data.get('options'):
                raise ValidationException("Options required for multiple choice questions")
        
        return validated_data
    
    def _get_evaluation_with_access_check(
        self,
        evaluation_id: int,
        user: User
    ) -> TestSet:
        """Get evaluation and verify user has access."""
        evaluation = self._get_evaluation_or_404(evaluation_id)
        
        # Check permissions
        if user.role == 'trainer' and evaluation.creator_id != user.id:
            raise ForbiddenException("You do not have permission to modify this evaluation")
        
        return evaluation
    
    def _get_session_with_access_check(
        self,
        session_id: int,
        user: User
    ) -> TestSession:
        """Get session and verify user has access."""
        session = self._get_session_or_404(session_id)
        
        # Check permissions
        if user.role == 'student':
            # Check if user is the beneficiary
            beneficiary = self.db.query(Beneficiary).filter_by(
                id=session.beneficiary_id
            ).first()
            if not beneficiary or beneficiary.user_id != user.id:
                raise ForbiddenException("You do not have permission to access this session")
        
        return session
    
    def _add_questions_to_evaluation(
        self,
        evaluation: TestSet,
        questions_data: List[Dict[str, Any]]
    ) -> None:
        """Add questions to an evaluation."""
        for idx, q_data in enumerate(questions_data):
            q_data['order'] = q_data.get('order', idx + 1)
            validated_q_data = self._validate_question_data(q_data)
            
            question = Question(
                test_set_id=evaluation.id,
                **validated_q_data
            )
            self.db.add(question)
    
    def _update_evaluation_questions(
        self,
        evaluation: TestSet,
        questions_data: List[Dict[str, Any]]
    ) -> None:
        """Update questions for an evaluation."""
        # Delete existing questions
        self.db.query(Question).filter_by(test_set_id=evaluation.id).delete()
        
        # Add new questions
        self._add_questions_to_evaluation(evaluation, questions_data)
    
    def _get_next_question_order(self, evaluation_id: int) -> int:
        """Get the next order number for a question."""
        max_order = self.db.query(Question).filter_by(
            test_set_id=evaluation_id
        ).with_entities(
            self.db.func.max(Question.order)
        ).scalar()
        
        return (max_order or 0) + 1
    
    def _has_active_sessions(self, evaluation: TestSet) -> bool:
        """Check if evaluation has active sessions."""
        active_count = self.db.query(TestSession).filter_by(
            test_set_id=evaluation.id,
            status=SessionStatus.IN_PROGRESS.value
        ).count()
        
        return active_count > 0
    
    def _cascade_delete_evaluation(self, evaluation: TestSet) -> None:
        """Delete evaluation and all related data."""
        # Get all sessions for this evaluation
        session_ids = [s.id for s in self.db.query(TestSession).filter_by(test_set_id=evaluation.id).all()]
        
        if session_ids:
            # Delete responses for these sessions
            self.db.query(Response).filter(Response.session_id.in_(session_ids)).delete(synchronize_session=False)
            
            # Delete AI feedback for these sessions
            self.db.query(AIFeedback).filter(AIFeedback.session_id.in_(session_ids)).delete(synchronize_session=False)
        
        # Delete sessions
        self.db.query(TestSession).filter_by(test_set_id=evaluation.id).delete()
        
        # Delete questions
        self.db.query(Question).filter_by(test_set_id=evaluation.id).delete()
        
        # Delete evaluation
        self.db.delete(evaluation)
    
    def _validate_session_creation(
        self,
        user: User,
        evaluation: TestSet,
        beneficiary_id: Optional[int]
    ) -> None:
        """Validate session creation permissions."""
        # Check if evaluation is published
        if evaluation.status != EvaluationStatus.PUBLISHED.value:
            if user.id != evaluation.creator_id and user.role not in ['admin', 'super_admin']:
                raise ValidationException("Evaluation is not published")
        
        # Validate beneficiary if provided
        if beneficiary_id and beneficiary_id != user.id:
            if user.role not in ['trainer', 'admin', 'super_admin']:
                raise ForbiddenException("Cannot create session for another user")
            
            # Verify beneficiary exists
            beneficiary = self.db.query(User).filter_by(id=beneficiary_id).first()
            if not beneficiary:
                raise NotFoundException(f"Beneficiary {beneficiary_id} not found")
    
    def _calculate_session_score(self, session_id: int) -> float:
        """Calculate total score for a session."""
        total_score = self.db.query(
            self.db.func.sum(Response.score)
        ).filter_by(
            session_id=session_id
        ).scalar()
        
        return float(total_score or 0)
    
    def _calculate_total_possible_score(self, evaluation_id: int) -> float:
        """Calculate total possible score for an evaluation."""
        total_points = self.db.query(
            self.db.func.sum(Question.points)
        ).filter_by(
            test_set_id=evaluation_id
        ).scalar()
        
        return float(total_points or 0)
    
    def _should_generate_ai_feedback(self, session: TestSession) -> bool:
        """Check if AI feedback should be generated."""
        # Check if already has feedback
        existing = self.db.query(AIFeedback).filter_by(
            session_id=session.id
        ).first()
        
        return not existing
    
    def _generate_session_feedback(self, session: TestSession) -> None:
        """Generate AI feedback for session."""
        try:
            feedback_content = self._generate_ai_feedback_content(session)
            
            feedback = AIFeedback(
                session_id=session.id,
                summary=feedback_content,
                status='draft'
            )
            
            self.db.add(feedback)
        except Exception as e:
            # Log error if app context available
            try:
                current_app.logger.error(f"Failed to generate AI feedback: {str(e)}")
            except RuntimeError:
                pass  # No app context in tests
    
    def _generate_ai_feedback_content(self, session: TestSession) -> str:
        """Generate AI feedback content for a session."""
        # Get session data
        responses = self.db.query(Response).filter_by(session_id=session.id).all()
        questions = self.db.query(Question).filter_by(test_set_id=session.test_set_id).all()
        
        # Prepare data for AI
        session_data = {
            'score': session.score,
            'total_score': session.total_score,
            'percentage': (session.score / session.total_score * 100) if session.total_score > 0 else 0,
            'responses': len(responses),
            'total_questions': len(questions)
        }
        
        # Generate feedback
        try:
            # return generate_ai_feedback(session_data)  # Enable when AI is available
            raise Exception("AI not available")  # Temporary
        except Exception:
            # Fallback to simple feedback
            percentage = session_data['percentage']
            if percentage >= 90:
                return "Excellent performance! You demonstrated strong understanding of the material."
            elif percentage >= 70:
                return "Good job! You showed solid comprehension with room for improvement."
            elif percentage >= 50:
                return "Fair performance. Consider reviewing the material to strengthen your understanding."
            else:
                return "You may benefit from additional study. Focus on the areas where you struggled."