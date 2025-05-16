"""Evaluation service module."""

from datetime import datetime, timezone

from app.models import Evaluation, Question, TestSession, Response, AIFeedback
from app.extensions import db
from app.utils import clear_model_cache


class EvaluationService:
    """Evaluation service."""
    
    @staticmethod
    def get_evaluations(tenant_id=None, creator_id=None, beneficiary_id=None, status=None, 
                       type=None, is_template=None, page=1, per_page=10):
        """
        Get evaluations with optional filtering.
        
        Args:
            tenant_id (int, optional): Filter by tenant ID.
            creator_id (int, optional): Filter by creator ID.
            beneficiary_id (int, optional): Filter by beneficiary ID.
            status (str, optional): Filter by status.
            type (str, optional): Filter by type.
            is_template (bool, optional): Filter by is_template.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (evaluations, total, pages)
        """
        from app.models import TestSet
        
        # Build query - use TestSet instead of Evaluation
        evaluation_query = TestSet.query
        
        # Apply filters
        if tenant_id:
            evaluation_query = evaluation_query.filter_by(tenant_id=tenant_id)
        
        if creator_id:
            evaluation_query = evaluation_query.filter_by(creator_id=creator_id)
        
        if beneficiary_id:
            evaluation_query = evaluation_query.filter_by(beneficiary_id=beneficiary_id)
        
        if status:
            evaluation_query = evaluation_query.filter_by(status=status)
        
        if type:
            evaluation_query = evaluation_query.filter_by(type=type)
        
        if is_template is not None:
            evaluation_query = evaluation_query.filter_by(is_template=is_template)
        
        # Order by creation time descending
        evaluation_query = evaluation_query.order_by(TestSet.created_at.desc())
        
        # Paginate results
        pagination = evaluation_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_evaluation(evaluation_id):
        """
        Get an evaluation by ID.
        
        Args:
            evaluation_id (int): Evaluation ID.
        
        Returns:
            Evaluation: The evaluation or None if not found.
        """
        return Evaluation.query.get(evaluation_id)
    
    @staticmethod
    def create_evaluation(creator_id, data):
        """
        Create a new evaluation (test).
        
        Args:
            creator_id (int): Creator user ID.
            data (dict): Evaluation data.
        
        Returns:
            TestSet: The created test set or None if creation fails.
        """
        from app.models import TestSet
        
        try:
            # Extract questions data if provided
            questions_data = data.pop('questions', [])
            
            # Create TestSet directly since it's independent from Test
            test_set = TestSet(
                title=data['title'],
                type=data.get('type', 'assessment'),
                category=data.get('category'),
                tenant_id=data['tenant_id'],
                creator_id=creator_id,  # Changed from created_by to creator_id
                beneficiary_id=data.get('beneficiary_id'),
                time_limit=data.get('time_limit'),
                passing_score=data.get('passing_score'),
                is_randomized=data.get('is_randomized', False),
                allow_resume=data.get('allow_resume', True),
                max_attempts=data.get('max_attempts', 1),
                show_results=data.get('show_results', True),
                status=data.get('status', 'draft'),
                is_template=data.get('is_template', False)
            )
            
            db.session.add(test_set)
            db.session.flush()
            
            # Create questions if provided
            for idx, question_data in enumerate(questions_data):
                question = Question(
                    test_set_id=test_set.id,  # Questions belong to TestSet, not Test
                    text=question_data['text'],
                    type=question_data['type'],
                    options=question_data.get('options'),
                    correct_answer=question_data.get('correct_answer'),
                    explanation=question_data.get('explanation'),
                    category=question_data.get('category'),
                    difficulty=question_data.get('difficulty', 'medium'),
                    points=question_data.get('points', 1.0),
                    order=idx  # Use index for ordering
                )
                db.session.add(question)
            
            db.session.commit()
            
            # Clear cache
            clear_model_cache('test_sets')
            
            # Return test_set object directly - let schema handle serialization
            return test_set
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_evaluation(evaluation_id, data):
        """
        Update an evaluation.
        
        Args:
            evaluation_id (int): Evaluation ID.
            data (dict): Data to update.
        
        Returns:
            Evaluation: The updated evaluation or None if update fails.
        """
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            
            if not evaluation:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(evaluation, key):
                    setattr(evaluation, key, value)
            
            evaluation.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            # Clear cache
            clear_model_cache('evaluations')
            
            return evaluation
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_evaluation(evaluation_id):
        """
        Delete an evaluation.
        
        Args:
            evaluation_id (int): Evaluation ID.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            
            if not evaluation:
                return False
            
            # Delete associated data
            Question.query.filter_by(evaluation_id=evaluation_id).delete()
            
            # Delete test sessions and related data
            sessions = TestSession.query.filter_by(evaluation_id=evaluation_id).all()
            for session in sessions:
                Response.query.filter_by(session_id=session.id).delete()
                AIFeedback.query.filter_by(session_id=session.id).delete()
            
            TestSession.query.filter_by(evaluation_id=evaluation_id).delete()
            
            # Delete evaluation
            db.session.delete(evaluation)
            db.session.commit()
            
            # Clear cache
            clear_model_cache('evaluations')
            
            return True
        
        except Exception as e:
            db.session.rollback()
            raise e


class QuestionService:
    """Question service."""
    
    @staticmethod
    def get_questions(evaluation_id, category=None, difficulty=None, type=None, page=1, per_page=10):
        """
        Get questions for an evaluation.
        
        Args:
            evaluation_id (int): Evaluation ID.
            category (str, optional): Filter by category.
            difficulty (str, optional): Filter by difficulty.
            type (str, optional): Filter by type.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (questions, total, pages)
        """
        # Build query
        # Question model uses test_set_id, not evaluation_id
        # First get the evaluation to find the test_id
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return [], 0, 0
        
        # Then get questions for that test set
        question_query = Question.query.filter_by(test_set_id=evaluation.test_id)
        
        # Apply filters
        if category:
            question_query = question_query.filter_by(category=category)
        
        if difficulty:
            question_query = question_query.filter_by(difficulty=difficulty)
        
        if type:
            question_query = question_query.filter_by(type=type)
        
        # Order by order if available, otherwise by ID
        question_query = question_query.order_by(Question.order.asc(), Question.id.asc())
        
        # Paginate results
        pagination = question_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_question(question_id):
        """
        Get a question by ID.
        
        Args:
            question_id (int): Question ID.
        
        Returns:
            Question: The question or None if not found.
        """
        return Question.query.get(question_id)
    
    @staticmethod
    def create_question(data):
        """
        Create a new question.
        
        Args:
            data (dict): Question data.
        
        Returns:
            Question: The created question or None if creation fails.
        """
        try:
            question = Question(
                evaluation_id=data['evaluation_id'],
                text=data['text'],
                type=data['type'],
                options=data.get('options'),
                correct_answer=data.get('correct_answer'),
                explanation=data.get('explanation'),
                category=data.get('category'),
                difficulty=data.get('difficulty', 'medium'),
                points=data.get('points', 1.0),
                order=data.get('order')
            )
            
            db.session.add(question)
            db.session.commit()
            
            # Clear cache
            clear_model_cache('evaluations')
            
            return question
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_question(question_id, data):
        """
        Update a question.
        
        Args:
            question_id (int): Question ID.
            data (dict): Data to update.
        
        Returns:
            Question: The updated question or None if update fails.
        """
        try:
            question = Question.query.get(question_id)
            
            if not question:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(question, key):
                    setattr(question, key, value)
            
            question.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            # Clear cache
            clear_model_cache('evaluations')
            
            return question
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_question(question_id):
        """
        Delete a question.
        
        Args:
            question_id (int): Question ID.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            question = Question.query.get(question_id)
            
            if not question:
                return False
            
            # Delete associated data
            # Responses will remain but will be orphaned
            
            # Delete question
            db.session.delete(question)
            db.session.commit()
            
            # Clear cache
            clear_model_cache('evaluations')
            
            return True
        
        except Exception as e:
            db.session.rollback()
            raise e


class TestSessionService:
    """Test session service."""
    
    @staticmethod
    def get_sessions(evaluation_id=None, beneficiary_id=None, status=None, page=1, per_page=10):
        """
        Get test sessions with optional filtering.
        
        Args:
            evaluation_id (int, optional): Filter by evaluation ID.
            beneficiary_id (int, optional): Filter by beneficiary ID.
            status (str, optional): Filter by status.
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
        
        Returns:
            tuple: (sessions, total, pages)
        """
        # Build query
        session_query = TestSession.query
        
        # Apply filters
        if evaluation_id:
            session_query = session_query.filter_by(evaluation_id=evaluation_id)
        
        if beneficiary_id:
            session_query = session_query.filter_by(beneficiary_id=beneficiary_id)
        
        if status:
            session_query = session_query.filter_by(status=status)
        
        # Order by creation time descending
        session_query = session_query.order_by(TestSession.created_at.desc())
        
        # Paginate results
        pagination = session_query.paginate(page=page, per_page=per_page)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def get_session(session_id):
        """
        Get a test session by ID.
        
        Args:
            session_id (int): Test session ID.
        
        Returns:
            TestSession: The test session or None if not found.
        """
        return TestSession.query.get(session_id)
    
    @staticmethod
    def create_session(data):
        """
        Create a new test session.
        
        Args:
            data (dict): Test session data.
        
        Returns:
            TestSession: The created test session or None if creation fails.
        """
        try:
            # Check if there's an in-progress session for this beneficiary and evaluation
            existing_session = TestSession.query.filter_by(
                evaluation_id=data['evaluation_id'],
                beneficiary_id=data['beneficiary_id'],
                status='in_progress'
            ).first()
            
            if existing_session:
                return existing_session
            
            # Get evaluation
            evaluation = Evaluation.query.get(data['evaluation_id'])
            
            if not evaluation:
                return None
            
            # Check max attempts
            if evaluation.max_attempts > 0:
                attempt_count = TestSession.query.filter_by(
                    evaluation_id=data['evaluation_id'],
                    beneficiary_id=data['beneficiary_id'],
                    status='completed'
                ).count()
                
                if attempt_count >= evaluation.max_attempts:
                    return None
            
            # Create session
            session = TestSession(
                evaluation_id=data['evaluation_id'],
                beneficiary_id=data['beneficiary_id'],
                start_time=datetime.now(timezone.utc),
                status='in_progress'
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_session(session_id, data):
        """
        Update a test session.
        
        Args:
            session_id (int): Test session ID.
            data (dict): Data to update.
        
        Returns:
            TestSession: The updated test session or None if update fails.
        """
        try:
            session = TestSession.query.get(session_id)
            
            if not session:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            session.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return session
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def complete_session(session_id):
        """
        Complete a test session.
        
        Args:
            session_id (int): Test session ID.
        
        Returns:
            TestSession: The updated test session or None if completion fails.
        """
        try:
            session = TestSession.query.get(session_id)
            
            if not session or session.status != 'in_progress':
                return None
            
            # Calculate score
            evaluation = Evaluation.query.get(session.evaluation_id)
            responses = Response.query.filter_by(session_id=session_id).all()
            
            total_score = 0
            max_score = 0
            
            for response in responses:
                question = Question.query.get(response.question_id)
                if question:
                    max_score += question.points
                    total_score += response.score or 0
            
            # Update session
            session.end_time = datetime.now(timezone.utc)
            session.time_spent = int((session.end_time - session.start_time).total_seconds())
            session.status = 'completed'
            session.score = total_score
            session.max_score = max_score
            
            # Check if passed
            if evaluation.passing_score is not None and max_score > 0:
                percentage_score = (total_score / max_score) * 100
                session.passed = percentage_score >= evaluation.passing_score
            else:
                session.passed = None
            
            db.session.commit()
            
            return session
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def abandon_session(session_id):
        """
        Abandon a test session.
        
        Args:
            session_id (int): Test session ID.
        
        Returns:
            TestSession: The updated test session or None if abandonment fails.
        """
        try:
            session = TestSession.query.get(session_id)
            
            if not session or session.status != 'in_progress':
                return None
            
            # Update session
            session.end_time = datetime.now(timezone.utc)
            session.time_spent = int((session.end_time - session.start_time).total_seconds())
            session.status = 'abandoned'
            
            db.session.commit()
            
            return session
        
        except Exception as e:
            db.session.rollback()
            raise e


class ResponseService:
    """Response service."""
    
    @staticmethod
    def get_responses(session_id):
        """
        Get responses for a test session.
        
        Args:
            session_id (int): Test session ID.
        
        Returns:
            list: List of responses.
        """
        return Response.query.filter_by(session_id=session_id).all()
    
    @staticmethod
    def get_response(response_id):
        """
        Get a response by ID.
        
        Args:
            response_id (int): Response ID.
        
        Returns:
            Response: The response or None if not found.
        """
        return Response.query.get(response_id)
    
    @staticmethod
    def submit_response(data):
        """
        Submit a response.
        
        Args:
            data (dict): Response data.
        
        Returns:
            Response: The created/updated response or None if submission fails.
        """
        try:
            # Check if session exists and is in progress
            session = TestSession.query.get(data['session_id'])
            
            if not session or session.status != 'in_progress':
                return None
            
            # Check if question exists
            question = Question.query.get(data['question_id'])
            
            if not question:
                return None
            
            # Check if response already exists
            response = Response.query.filter_by(
                session_id=data['session_id'],
                question_id=data['question_id']
            ).first()
            
            # Create or update response
            now = datetime.now(timezone.utc)
            
            if response:
                # Update existing response
                response.answer = data['answer']
                response.end_time = now
                
                # Calculate time spent if not provided
                if data.get('time_spent') is not None:
                    response.time_spent = data['time_spent']
                elif response.start_time:
                    response.time_spent = int((now - response.start_time).total_seconds())
            else:
                # Create new response
                response = Response(
                    session_id=data['session_id'],
                    question_id=data['question_id'],
                    answer=data['answer'],
                    start_time=now,
                    end_time=now,
                    time_spent=data.get('time_spent')
                )
                
                db.session.add(response)
            
            # Check if answer is correct and calculate score
            if question.type in ['multiple_choice', 'true_false', 'matching', 'ordering']:
                # For question types with definitive correct answers
                response.is_correct = question.check_answer(data['answer'])
                response.score = question.points if response.is_correct else 0
            else:
                # For other question types (e.g., text), mark as correct but require human review
                response.is_correct = True
                response.score = question.points
            
            # Update session's current question if this is the latest question
            if not session.current_question or session.current_question < question.order or question.order is None:
                session.current_question = question.order or question.id
                session.updated_at = now
            
            db.session.commit()
            
            return response
        
        except Exception as e:
            db.session.rollback()
            raise e


class AIFeedbackService:
    """AI feedback service."""
    
    @staticmethod
    def get_feedback(session_id):
        """
        Get AI feedback for a test session.
        
        Args:
            session_id (int): Test session ID.
        
        Returns:
            AIFeedback: The AI feedback or None if not found.
        """
        return AIFeedback.query.filter_by(session_id=session_id).first()
    
    @staticmethod
    def generate_feedback(session_id):
        """
        Generate AI feedback for a test session.
        
        Args:
            session_id (int): Test session ID.
        
        Returns:
            AIFeedback: The generated AI feedback or None if generation fails.
        """
        try:
            # Check if session exists and is completed
            session = TestSession.query.get(session_id)
            
            if not session or session.status != 'completed':
                return None
            
            # Check if feedback already exists
            existing_feedback = AIFeedback.query.filter_by(session_id=session_id).first()
            
            if existing_feedback:
                return existing_feedback
            
            # Get evaluation and responses
            evaluation = Evaluation.query.get(session.evaluation_id)
            responses = Response.query.filter_by(session_id=session_id).all()
            
            # Prepare data for AI generation
            correct_count = 0
            total_count = len(responses)
            question_categories = {}
            
            for response in responses:
                question = Question.query.get(response.question_id)
                if question:
                    if response.is_correct:
                        correct_count += 1
                    
                    # Track performance by category
                    category = question.category or 'General'
                    if category not in question_categories:
                        question_categories[category] = {'correct': 0, 'total': 0}
                    
                    question_categories[category]['total'] += 1
                    if response.is_correct:
                        question_categories[category]['correct'] += 1
            
            # Calculate overall score percentage
            score_percentage = (correct_count / total_count * 100) if total_count > 0 else 0
            
            # Generate AI feedback based on performance
            strengths = []
            areas_to_improve = []
            recommendations = []
            next_steps = []
            
            # Analyze category performance
            for category, stats in question_categories.items():
                category_score = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                
                if category_score >= 80:
                    strengths.append(f"Excellent performance in {category} ({category_score:.0f}%)")
                elif category_score >= 60:
                    recommendations.append(f"Good foundation in {category}, consider advanced topics")
                else:
                    areas_to_improve.append(f"{category} needs more attention ({category_score:.0f}%)")
                    recommendations.append(f"Review fundamental concepts in {category}")
            
            # Overall performance feedback
            if score_percentage >= 90:
                summary = f"Outstanding performance! You scored {score_percentage:.0f}% demonstrating mastery of the material."
                strengths.append("Exceptional understanding of core concepts")
                next_steps.append("Consider mentoring others or teaching these concepts")
            elif score_percentage >= 75:
                summary = f"Great job! You scored {score_percentage:.0f}% showing strong competency."
                strengths.append("Solid grasp of most concepts")
                next_steps.append("Focus on mastering the remaining areas")
            elif score_percentage >= 60:
                summary = f"Good effort! You scored {score_percentage:.0f}% with room for improvement."
                next_steps.append("Review materials for weak areas")
                next_steps.append("Practice with more exercises")
            else:
                summary = f"You scored {score_percentage:.0f}%. More practice is needed to achieve mastery."
                areas_to_improve.append("Foundation concepts need strengthening")
                next_steps.append("Revisit basic concepts before advancing")
                next_steps.append("Seek additional help or tutoring")
            
            # Time analysis
            total_time = session.time_spent
            avg_time_per_question = (total_time / total_count / 60) if total_count > 0 else 0
            
            if avg_time_per_question < 0.5:
                areas_to_improve.append("Consider spending more time on each question")
            elif avg_time_per_question > 5:
                recommendations.append("Try to improve response time while maintaining accuracy")
            
            # Ensure we have at least some content in each section
            if not strengths:
                strengths.append("Completed the evaluation successfully")
            if not areas_to_improve:
                areas_to_improve.append("Maintain focus on continuous improvement")
            if not recommendations:
                recommendations.append("Continue practicing regularly")
            if not next_steps:
                next_steps.append("Review evaluation results with your trainer")
            
            feedback = AIFeedback(
                session_id=session_id,
                summary=summary,
                strengths=strengths[:5],  # Limit to 5 items
                areas_to_improve=areas_to_improve[:5],
                recommendations=recommendations[:5],
                next_steps=next_steps[:5],
                status="draft"
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            return feedback
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_feedback(feedback_id, data):
        """
        Update AI feedback.
        
        Args:
            feedback_id (int): AI feedback ID.
            data (dict): Data to update.
        
        Returns:
            AIFeedback: The updated AI feedback or None if update fails.
        """
        try:
            feedback = AIFeedback.query.get(feedback_id)
            
            if not feedback:
                return None
            
            # Update attributes
            for key, value in data.items():
                if hasattr(feedback, key):
                    setattr(feedback, key, value)
            
            feedback.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return feedback
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def approve_feedback(feedback_id, approver_id):
        """
        Approve AI feedback.
        
        Args:
            feedback_id (int): AI feedback ID.
            approver_id (int): Approver user ID.
        
        Returns:
            AIFeedback: The updated AI feedback or None if approval fails.
        """
        try:
            feedback = AIFeedback.query.get(feedback_id)
            
            if not feedback or feedback.status != 'draft':
                return None
            
            # Update feedback
            feedback.status = 'approved'
            feedback.approved_by = approver_id
            feedback.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return feedback
        
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def reject_feedback(feedback_id, reason):
        """
        Reject AI feedback.
        
        Args:
            feedback_id (int): AI feedback ID.
            reason (str): Rejection reason.
        
        Returns:
            AIFeedback: The updated AI feedback or None if rejection fails.
        """
        try:
            feedback = AIFeedback.query.get(feedback_id)
            
            if not feedback or feedback.status != 'draft':
                return None
            
            # Update feedback
            feedback.status = 'rejected'
            feedback.rejected_reason = reason
            feedback.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return feedback
        
        except Exception as e:
            db.session.rollback()
            raise e