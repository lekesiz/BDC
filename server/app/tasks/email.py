"""Email-related Celery tasks."""

from celery import shared_task
from app.services import EmailService
from flask import current_app


@shared_task(bind=True, max_retries=3)
def send_email_async(self, to_email, subject, html_content, text_content=None):
    """Send email asynchronously."""
    try:
        EmailService.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        return f"Email sent to {to_email}"
        
    except Exception as e:
        current_app.logger.error(f"Error sending email to {to_email}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True)
def send_bulk_email(self, email_list, subject, html_template, template_data=None):
    """Send bulk emails to multiple recipients."""
    try:
        success_count = 0
        failed_count = 0
        
        for email in email_list:
            try:
                # Personalize template data if provided
                personal_data = template_data.copy() if template_data else {}
                if isinstance(email, dict):
                    personal_data.update(email.get('data', {}))
                    email_address = email.get('email')
                else:
                    email_address = email
                
                # Render template with personal data
                html_content = EmailService.render_template(html_template, personal_data)
                
                # Send email
                EmailService.send_email(
                    to_email=email_address,
                    subject=subject,
                    html_content=html_content
                )
                success_count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error sending bulk email to {email}: {str(e)}")
                failed_count += 1
                continue
        
        return f"Bulk email complete: {success_count} sent, {failed_count} failed"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_bulk_email task: {str(e)}")
        raise


@shared_task(bind=True)
def send_welcome_email(self, user_id):
    """Send welcome email to a new user."""
    try:
        from app.models import User
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        EmailService.send_welcome_email(
            to_email=user.email,
            user_name=f"{user.first_name} {user.last_name}",
            user_role=user.role
        )
        
        return f"Welcome email sent to user {user_id}"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_welcome_email task: {str(e)}")
        raise


@shared_task(bind=True)
def send_password_reset_email(self, user_id, reset_token):
    """Send password reset email."""
    try:
        from app.models import User
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        EmailService.send_password_reset(
            to_email=user.email,
            user_name=f"{user.first_name} {user.last_name}",
            reset_token=reset_token
        )
        
        return f"Password reset email sent to user {user_id}"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_password_reset_email task: {str(e)}")
        raise


@shared_task(bind=True)
def send_evaluation_complete_email(self, session_id):
    """Send email when evaluation is completed."""
    try:
        from app.models import TestSession
        
        session = TestSession.query.get(session_id)
        if not session:
            raise ValueError(f"Test session {session_id} not found")
        
        # Send to beneficiary
        if session.beneficiary and session.beneficiary.user:
            EmailService.send_evaluation_complete(
                to_email=session.beneficiary.user.email,
                evaluation_title=session.evaluation.title,
                score=session.score,
                session_id=session_id
            )
        
        # Send to trainer
        if session.evaluation.creator:
            EmailService.send_evaluation_complete_trainer(
                to_email=session.evaluation.creator.email,
                evaluation_title=session.evaluation.title,
                beneficiary_name=f"{session.beneficiary.user.first_name} {session.beneficiary.user.last_name}",
                score=session.score,
                session_id=session_id
            )
        
        return f"Evaluation complete emails sent for session {session_id}"
        
    except Exception as e:
        current_app.logger.error(f"Error in send_evaluation_complete_email task: {str(e)}")
        raise