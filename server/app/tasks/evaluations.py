"""Evaluation-related Celery tasks."""

from celery import shared_task
from datetime import datetime, timedelta
from app.models import Evaluation, TestSession, Beneficiary
from app.services import NotificationService, EmailService
from app.extensions import db
from flask import current_app


@shared_task(bind=True)
def check_overdue_evaluations(self):
    """Check for overdue evaluations and send notifications."""
    try:
        # Get evaluations that are past their due date
        overdue_evaluations = Evaluation.query.filter(
            Evaluation.due_date < datetime.utcnow(),
            Evaluation.status.in_(['pending', 'in_progress']),
            Evaluation.is_active == True
        ).all()
        
        count = 0
        for evaluation in overdue_evaluations:
            try:
                # Update status to overdue
                evaluation.status = 'overdue'
                
                # Notify beneficiary if assigned
                if evaluation.beneficiary and evaluation.beneficiary.user:
                    NotificationService.create_notification(
                        user_id=evaluation.beneficiary.user.id,
                        title='Overdue Evaluation',
                        message=f'Your evaluation "{evaluation.title}" is overdue. Please complete it as soon as possible.',
                        type='evaluation',
                        related_id=evaluation.id,
                        related_type='evaluation',
                        priority='high'
                    )
                
                # Notify trainer/creator
                if evaluation.creator:
                    NotificationService.create_notification(
                        user_id=evaluation.creator_id,
                        title='Evaluation Overdue',
                        message=f'The evaluation "{evaluation.title}" for {evaluation.beneficiary.user.first_name} {evaluation.beneficiary.user.last_name} is overdue.',
                        type='evaluation',
                        related_id=evaluation.id,
                        related_type='evaluation',
                        priority='normal'
                    )
                
                count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error processing overdue evaluation {evaluation.id}: {str(e)}")
                continue
        
        db.session.commit()
        return f"Processed {count} overdue evaluations"
        
    except Exception as e:
        current_app.logger.error(f"Error in check_overdue_evaluations task: {str(e)}")
        raise


@shared_task(bind=True)
def process_ai_analysis(self, session_id):
    """Process AI analysis for a completed evaluation session."""
    try:
        from app.services.ai import AIService
        from app.services import ResponseService, AIFeedbackService
        
        # Get the test session
        session = TestSession.query.get(session_id)
        if not session:
            raise ValueError(f"Test session {session_id} not found")
        
        # Get evaluation
        evaluation = session.evaluation
        if not evaluation:
            raise ValueError(f"Evaluation not found for session {session_id}")
        
        # Get responses
        responses = ResponseService.get_session_responses(session_id)
        
        # Prepare data for AI analysis
        response_data = []
        for response in responses:
            question = response.question
            response_data.append({
                'question': question.text,
                'question_type': question.question_type,
                'response': response.answer_text or response.answer_choice,
                'correct_answer': question.correct_answer
            })
        
        # Get AI analysis
        analysis = AIService.analyze_evaluation_responses(
            evaluation_title=evaluation.title,
            responses=response_data
        )
        
        # Save AI feedback
        feedback = AIFeedbackService.create_feedback({
            'session_id': session_id,
            'feedback_type': 'evaluation_analysis',
            'content': analysis.get('summary', ''),
            'recommendations': analysis.get('recommendations', []),
            'strengths': analysis.get('strengths', []),
            'areas_for_improvement': analysis.get('areas_for_improvement', []),
            'confidence_score': analysis.get('confidence_score', 0.0),
            'is_automated': True
        })
        
        # Notify beneficiary
        if session.beneficiary and session.beneficiary.user:
            NotificationService.create_notification(
                user_id=session.beneficiary.user.id,
                title='AI Analysis Complete',
                message=f'AI analysis for your evaluation "{evaluation.title}" is ready.',
                type='evaluation',
                related_id=evaluation.id,
                related_type='evaluation'
            )
        
        return f"AI analysis completed for session {session_id}"
        
    except Exception as e:
        current_app.logger.error(f"Error in process_ai_analysis task: {str(e)}")
        raise


@shared_task(bind=True)
def send_evaluation_reminder(self, evaluation_id):
    """Send reminder for an upcoming evaluation deadline."""
    try:
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        if evaluation.beneficiary and evaluation.beneficiary.user:
            # Calculate days until due
            days_until = (evaluation.due_date - datetime.utcnow()).days
            
            NotificationService.create_notification(
                user_id=evaluation.beneficiary.user.id,
                title='Evaluation Reminder',
                message=f'Your evaluation "{evaluation.title}" is due in {days_until} days.',
                type='evaluation',
                related_id=evaluation.id,
                related_type='evaluation',
                priority='high' if days_until <= 1 else 'normal'
            )
            
            # Send email reminder
            EmailService.send_evaluation_reminder(
                to_email=evaluation.beneficiary.user.email,
                evaluation=evaluation
            )
        
        return f"Sent reminder for evaluation {evaluation_id}"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_evaluation_reminder task: {str(e)}")
        raise