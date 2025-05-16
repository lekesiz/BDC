"""Services package."""

from app.services.auth_service import AuthService
from app.services.beneficiary_service import (
    BeneficiaryService, NoteService, AppointmentService, DocumentService
)
from app.services.evaluation_service import (
    EvaluationService, QuestionService, TestSessionService,
    ResponseService, AIFeedbackService
)
from app.services.email_service import (
    send_email, send_password_reset_email, send_welcome_email,
    send_notification_email, generate_email_token, verify_email_token
)

# Export all services
__all__ = [
    'AuthService',
    'BeneficiaryService',
    'NoteService',
    'AppointmentService',
    'DocumentService',
    'EvaluationService',
    'QuestionService',
    'TestSessionService',
    'ResponseService',
    'AIFeedbackService',
    'send_email',
    'send_password_reset_email',
    'send_welcome_email',
    'send_notification_email',
    'generate_email_token',
    'verify_email_token'
]