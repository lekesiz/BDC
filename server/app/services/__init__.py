"""Services package."""

from app.services.auth_service import AuthService
from app.services.beneficiary_service import (
    BeneficiaryService, NoteService, AppointmentService
)
from app.services.document_service import DocumentService
from app.services.document_version_service import DocumentVersionService
from app.services.evaluation_service import (
    EvaluationService, QuestionService, TestSessionService,
    ResponseService, AIFeedbackService
)
from app.services.email_service import (
    send_email, send_password_reset_email, send_welcome_email,
    send_notification_email, generate_email_token, verify_email_token
)
from app.services.two_factor_service import TwoFactorService
from app.services.recurring_appointment_service import RecurringAppointmentService
from app.services.performance_prediction_service import PerformancePredictionService
from app.services.ai_question_generator_service import AIQuestionGeneratorService

# Export all services
__all__ = [
    'AuthService',
    'BeneficiaryService',
    'NoteService',
    'AppointmentService',
    'DocumentService',
    'DocumentVersionService',
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
    'verify_email_token',
    'TwoFactorService',
    'RecurringAppointmentService',
    'PerformancePredictionService',
    'AIQuestionGeneratorService'
]