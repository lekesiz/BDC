"""Models package with improved import patterns."""

# Import db first to avoid circular dependencies
from app.extensions import db


def _import_models():
    """Import all models using a controlled approach to avoid circular dependencies."""
    # Import models in dependency order (base models first, then dependent models)
    
    # Base models (no foreign keys to other models)
    from app.models.tenant import Tenant
    from app.models.permission import Permission, Role
    
    # User model (depends on tenant)
    from app.models.user import User, TokenBlocklist, UserRole
    
    # Core entity models (depend on user and tenant)
    from app.models.beneficiary import Beneficiary, Note, BeneficiaryAppointment, BeneficiaryDocument
    from app.models.folder import Folder
    from app.models.profile import UserProfile
    
    # Activity and preference models
    from app.models.user_activity import UserActivity
    from app.models.user_preference import UserPreference
    
    # Test and assessment models
    from app.models.test import Test, TestSet, Question, TestSession, Response, AIFeedback
    from app.models.evaluation import Evaluation
    from app.models.adaptive_test import (
        AdaptiveTestPool, AdaptiveQuestion, AdaptiveTestSession,
        AdaptiveResponse, AdaptiveTestReport
    )
    
    # Document and appointment models
    from app.models.document import Document
    from app.models.document_version import DocumentVersion, DocumentComparison
    from app.models.appointment import Appointment
    from app.models.recurring_appointment import RecurringPattern, AppointmentSeries
    
    # Program and training models
    from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession, SessionAttendance
    
    # Communication models
    from app.models.notification import Notification, MessageThread, ThreadParticipant, Message, ReadReceipt
    
    # Reporting models
    from app.models.report import Report, ReportSchedule
    
    # Availability and scheduling models
    from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException
    
    # Additional models
    from app.models.monitoring import Monitoring
    from app.models.activity import Activity
    from app.models.assessment import Assessment
    from app.models.settings import Settings
    from app.models.integration import UserIntegration
    from app.models.document_permission import DocumentPermission
    from app.models.two_factor_auth import TwoFactorAuth, TwoFactorSession
    
    # Chat conversation models
    from app.models.chat_conversation import (
        ChatConversation, ChatMessage, ChatRateLimit, 
        ConversationTemplate, ConversationStatus, MessageRole
    )
    
    # Performance prediction models
    from app.models.performance_prediction import (
        PredictionModel, PerformancePrediction, PredictionRecommendation,
        ModelTrainingHistory
    )
    
    # AI Question Generation models
    from app.models.ai_question_generation import (
        ContentType, QuestionType, BloomsTaxonomy,
        LearningObjective, QuestionGenerationRequest, GeneratedQuestion,
        QuestionDuplicate, QuestionBank, QuestionBankQuestion,
        GenerationAnalytics
    )
    
    # Internationalization models
    from app.models.i18n import (
        Language, MultilingualContent, TranslationProject,
        TranslationWorkflow, UserLanguagePreference
    )
    
    # Gamification models
    from app.models.gamification import (
        Badge, UserBadge, UserXP, PointTransaction,
        Leaderboard, LeaderboardEntry, Challenge, ChallengeParticipant,
        GamificationTeam, Reward, RewardRedemption, UserGoal,
        GamificationEvent, UserProgress,
        AchievementCategory, AchievementType, PointActivityType,
        LeaderboardType, ChallengeType, RewardType
    )
    
    # Return all models as a dictionary for easier access
    return {
        # Database instance
        'db': db,
        
        # Base models
        'Tenant': Tenant,
        'Permission': Permission,
        'Role': Role,
        
        # User models
        'User': User,
        'TokenBlocklist': TokenBlocklist,
        'UserRole': UserRole,
        'UserProfile': UserProfile,
        'UserActivity': UserActivity,
        'UserPreference': UserPreference,
        
        # Beneficiary models
        'Beneficiary': Beneficiary,
        'Note': Note,
        'BeneficiaryAppointment': BeneficiaryAppointment,
        'BeneficiaryDocument': BeneficiaryDocument,
        
        # Test and evaluation models
        'Test': Test,
        'TestSet': TestSet,
        'Question': Question,
        'TestSession': TestSession,
        'Response': Response,
        'AIFeedback': AIFeedback,
        'Evaluation': Evaluation,
        'Assessment': Assessment,
        
        # Adaptive test models
        'AdaptiveTestPool': AdaptiveTestPool,
        'AdaptiveQuestion': AdaptiveQuestion,
        'AdaptiveTestSession': AdaptiveTestSession,
        'AdaptiveResponse': AdaptiveResponse,
        'AdaptiveTestReport': AdaptiveTestReport,
        
        # Document models
        'Document': Document,
        'DocumentPermission': DocumentPermission,
        'Folder': Folder,
        
        # Appointment and scheduling models
        'Appointment': Appointment,
        'RecurringPattern': RecurringPattern,
        'AppointmentSeries': AppointmentSeries,
        'AvailabilitySchedule': AvailabilitySchedule,
        'AvailabilitySlot': AvailabilitySlot,
        'AvailabilityException': AvailabilityException,
        
        # Program models
        'Program': Program,
        'ProgramModule': ProgramModule,
        'ProgramEnrollment': ProgramEnrollment,
        'TrainingSession': TrainingSession,
        'SessionAttendance': SessionAttendance,
        
        # Communication models
        'Notification': Notification,
        'MessageThread': MessageThread,
        'ThreadParticipant': ThreadParticipant,
        'Message': Message,
        'ReadReceipt': ReadReceipt,
        
        # Reporting models
        'Report': Report,
        'ReportSchedule': ReportSchedule,
        
        # Other models
        'Activity': Activity,
        'Monitoring': Monitoring,
        'Settings': Settings,
        'Integration': UserIntegration,
        
        # Two-Factor Authentication
        'TwoFactorAuth': TwoFactorAuth,
        'TwoFactorSession': TwoFactorSession,
        
        # Chat conversation models
        'ChatConversation': ChatConversation,
        'ChatMessage': ChatMessage,
        'ChatRateLimit': ChatRateLimit,
        'ConversationTemplate': ConversationTemplate,
        'ConversationStatus': ConversationStatus,
        'MessageRole': MessageRole,
        
        # Performance prediction models
        'PredictionModel': PredictionModel,
        'PerformancePrediction': PerformancePrediction,
        'PredictionRecommendation': PredictionRecommendation,
        'ModelTrainingHistory': ModelTrainingHistory,
        
        # AI Question Generation models
        'ContentType': ContentType,
        'QuestionType': QuestionType,
        'BloomsTaxonomy': BloomsTaxonomy,
        'LearningObjective': LearningObjective,
        'QuestionGenerationRequest': QuestionGenerationRequest,
        'GeneratedQuestion': GeneratedQuestion,
        'QuestionDuplicate': QuestionDuplicate,
        'QuestionBank': QuestionBank,
        'QuestionBankQuestion': QuestionBankQuestion,
        'GenerationAnalytics': GenerationAnalytics,
        
        # Internationalization models
        'Language': Language,
        'MultilingualContent': MultilingualContent,
        'TranslationProject': TranslationProject,
        'TranslationWorkflow': TranslationWorkflow,
        'UserLanguagePreference': UserLanguagePreference,
        
        # Gamification models
        'Badge': Badge,
        'UserBadge': UserBadge,
        'UserXP': UserXP,
        'PointTransaction': PointTransaction,
        'Leaderboard': Leaderboard,
        'LeaderboardEntry': LeaderboardEntry,
        'Challenge': Challenge,
        'ChallengeParticipant': ChallengeParticipant,
        'GamificationTeam': GamificationTeam,
        'Reward': Reward,
        'RewardRedemption': RewardRedemption,
        'UserGoal': UserGoal,
        'GamificationEvent': GamificationEvent,
        'UserProgress': UserProgress,
        'AchievementCategory': AchievementCategory,
        'AchievementType': AchievementType,
        'PointActivityType': PointActivityType,
        'LeaderboardType': LeaderboardType,
        'ChallengeType': ChallengeType,
        'RewardType': RewardType,
    }


# Use lazy loading to avoid import-time side effects
_models_cache = None


def get_models():
    """Get all models using lazy loading."""
    global _models_cache
    if _models_cache is None:
        _models_cache = _import_models()
    return _models_cache


def get_model(name):
    """Get a specific model by name."""
    models = get_models()
    return models.get(name)


# Export commonly used items directly for backward compatibility
# These will be imported only when explicitly accessed
def __getattr__(name):
    """Dynamic import for backward compatibility."""
    models = get_models()
    if name in models:
        return models[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Export db for immediate use
db = db

# Export all model names for __all__
__all__ = [
    'db',
    'get_models',
    'get_model',
    # Base models
    'Tenant',
    'Permission',
    'Role',
    # User models
    'User',
    'TokenBlocklist',
    'UserRole',
    'UserProfile',
    'UserActivity',
    'UserPreference',
    # Beneficiary models
    'Beneficiary',
    'Note',
    'BeneficiaryAppointment',
    'BeneficiaryDocument',
    # Test and evaluation models
    'Test',
    'TestSet',
    'Question',
    'TestSession',
    'Response',
    'AIFeedback',
    'Evaluation',
    'Assessment',
    # Adaptive test models
    'AdaptiveTestPool',
    'AdaptiveQuestion',
    'AdaptiveTestSession',
    'AdaptiveResponse',
    'AdaptiveTestReport',
    # Document models
    'Document',
    'DocumentPermission',
    'Folder',
    # Appointment and scheduling models
    'Appointment',
    'RecurringPattern',
    'AppointmentSeries',
    'AvailabilitySchedule',
    'AvailabilitySlot',
    'AvailabilityException',
    # Program models
    'Program',
    'ProgramModule',
    'ProgramEnrollment',
    'TrainingSession',
    'SessionAttendance',
    # Communication models
    'Notification',
    'MessageThread',
    'ThreadParticipant',
    'Message',
    'ReadReceipt',
    # Reporting models
    'Report',
    'ReportSchedule',
    # Other models
    'Activity',
    'Monitoring',
    'Settings',
    'Integration',
    # Two-Factor Authentication
    'TwoFactorAuth',
    'TwoFactorSession',
    # Chat conversation models
    'ChatConversation',
    'ChatMessage',
    'ChatRateLimit',
    'ConversationTemplate',
    'ConversationStatus',
    'MessageRole',
    # Performance prediction models
    'PredictionModel',
    'PerformancePrediction',
    'PredictionRecommendation',
    'ModelTrainingHistory',
    # AI Question Generation models
    'ContentType',
    'SourceContent',
    'QuestionType',
    'BloomsTaxonomy',
    'LearningObjective',
    'QuestionGenerationRequest',
    'GeneratedQuestion',
    'QuestionDuplicate',
    'QuestionBank',
    'QuestionBankQuestion',
    'GenerationAnalytics',
    # Internationalization models
    'Language',
    'MultilingualContent',
    'TranslationProject',
    'TranslationWorkflow',
    'UserLanguagePreference',
    # Gamification models
    'Badge',
    'UserBadge',
    'UserXP',
    'PointTransaction',
    'Leaderboard',
    'LeaderboardEntry',
    'Challenge',
    'ChallengeParticipant',
    'GamificationTeam',
    'Reward',
    'RewardRedemption',
    'UserGoal',
    'GamificationEvent',
    'UserProgress',
    'AchievementCategory',
    'AchievementType',
    'PointActivityType',
    'LeaderboardType',
    'ChallengeType',
    'RewardType',
]