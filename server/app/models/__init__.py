"""Models package."""

from app.models.user import User, TokenBlocklist, UserRole
from app.models.beneficiary import Beneficiary, Note, BeneficiaryAppointment, BeneficiaryDocument
from app.models.appointment import Appointment
from app.models.document import Document
from app.models.test import Test, TestSet, Question, TestSession, Response, AIFeedback
from app.models.notification import Notification, MessageThread, ThreadParticipant, Message, ReadReceipt
from app.models.evaluation import Evaluation
from app.models.tenant import Tenant
from app.models.folder import Folder
from app.models.report import Report, ReportSchedule
from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession, SessionAttendance
from app.models.profile import UserProfile
from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException

# Export all models
__all__ = [
    'User',
    'Tenant',
    'TokenBlocklist',
    'UserRole',
    'Beneficiary',
    'Note',
    'BeneficiaryAppointment',
    'BeneficiaryDocument',
    'Appointment',
    'Document',
    'Evaluation',
    'Test',
    'TestSet',
    'Question',
    'TestSession',
    'Response',
    'AIFeedback',
    'Notification',
    'MessageThread',
    'ThreadParticipant',
    'Message',
    'ReadReceipt',
    'Folder',
    'Report',
    'ReportSchedule',
    'Program',
    'ProgramModule',
    'ProgramEnrollment',
    'TrainingSession',
    'SessionAttendance',
    'UserProfile',
    'AvailabilitySchedule',
    'AvailabilitySlot',
    'AvailabilityException'
]