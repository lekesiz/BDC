"""Schemas package."""

from app.schemas.auth import (
    LoginSchema, RegisterSchema, TokenSchema, RefreshTokenSchema,
    ResetPasswordRequestSchema, ResetPasswordSchema, ChangePasswordSchema
)
from app.schemas.user import (
    UserSchema, UserCreateSchema, UserUpdateSchema, UserProfileSchema,
    TenantSchema, TenantCreateSchema, TenantUpdateSchema
)
from app.schemas.beneficiary import (
    BeneficiarySchema, BeneficiaryCreateSchema, BeneficiaryUpdateSchema,
    NoteSchema, NoteCreateSchema, NoteUpdateSchema,
    AppointmentSchema, AppointmentCreateSchema, AppointmentUpdateSchema,
    DocumentSchema, DocumentCreateSchema, DocumentUpdateSchema
)
from app.schemas.evaluation import (
    EvaluationSchema, EvaluationCreateSchema, EvaluationUpdateSchema,
    QuestionSchema, QuestionCreateSchema, QuestionUpdateSchema,
    TestSessionSchema, TestSessionCreateSchema,
    ResponseSchema, ResponseCreateSchema,
    AIFeedbackSchema, AIFeedbackUpdateSchema
)

# Export all schemas
__all__ = [
    # Auth schemas
    'LoginSchema',
    'RegisterSchema',
    'TokenSchema',
    'RefreshTokenSchema',
    'ResetPasswordRequestSchema',
    'ResetPasswordSchema',
    'ChangePasswordSchema',
    
    # User schemas
    'UserSchema',
    'UserCreateSchema',
    'UserUpdateSchema',
    'UserProfileSchema',
    'TenantSchema',
    'TenantCreateSchema',
    'TenantUpdateSchema',
    
    # Beneficiary schemas
    'BeneficiarySchema',
    'BeneficiaryCreateSchema',
    'BeneficiaryUpdateSchema',
    'NoteSchema',
    'NoteCreateSchema',
    'NoteUpdateSchema',
    'AppointmentSchema',
    'AppointmentCreateSchema',
    'AppointmentUpdateSchema',
    'DocumentSchema',
    'DocumentCreateSchema',
    'DocumentUpdateSchema',
    
    # Evaluation schemas
    'EvaluationSchema',
    'EvaluationCreateSchema',
    'EvaluationUpdateSchema',
    'QuestionSchema',
    'QuestionCreateSchema',
    'QuestionUpdateSchema',
    'TestSessionSchema',
    'TestSessionCreateSchema',
    'ResponseSchema',
    'ResponseCreateSchema',
    'AIFeedbackSchema',
    'AIFeedbackUpdateSchema'
]