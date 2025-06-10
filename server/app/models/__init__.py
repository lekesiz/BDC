_('models___init__.message.models_package_with_improved_i')
from app.extensions import db
from flask_babel import _, lazy_gettext as _l


def _import_models():
    _('models___init__.message.import_all_models_using_a_cont')
    from app.models.tenant import Tenant
    from app.models.permission import Permission, Role
    from app.models.user import User, TokenBlocklist, UserRole
    from app.models.beneficiary import Beneficiary, Note, BeneficiaryAppointment, BeneficiaryDocument
    from app.models.folder import Folder
    from app.models.profile import UserProfile
    from app.models.user_activity import UserActivity
    from app.models.user_preference import UserPreference
    from app.models.test import Test, TestSet, Question, TestSession, Response, AIFeedback
    from app.models.evaluation import Evaluation
    from app.models.adaptive_test import AdaptiveTestPool, AdaptiveQuestion, AdaptiveTestSession, AdaptiveResponse, AdaptiveTestReport
    from app.models.document import Document
    from app.models.document_version import DocumentVersion, DocumentComparison
    from app.models.appointment import Appointment
    from app.models.recurring_appointment import RecurringPattern, AppointmentSeries
    from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession, SessionAttendance
    from app.models.notification import Notification, MessageThread, ThreadParticipant, Message, ReadReceipt
    from app.models.report import Report, ReportSchedule
    from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException
    from app.models.monitoring import Monitoring
    from app.models.activity import Activity
    from app.models.assessment import Assessment
    from app.models.settings import Settings
    from app.models.integration import UserIntegration
    from app.models.document_permission import DocumentPermission
    from app.models.two_factor_auth import TwoFactorAuth, TwoFactorSession
    from app.models.chat_conversation import ChatConversation, ChatMessage, ChatRateLimit, ConversationTemplate, ConversationStatus, MessageRole
    from app.models.performance_prediction import PredictionModel, PerformancePrediction, PredictionRecommendation, ModelTrainingHistory
    from app.models.ai_question_generation import ContentType, QuestionType, BloomsTaxonomy, LearningObjective, QuestionGenerationRequest, GeneratedQuestion, QuestionDuplicate, QuestionBank, QuestionBankQuestion, GenerationAnalytics
    from app.models.i18n import Language, MultilingualContent, TranslationProject, TranslationWorkflow, UserLanguagePreference
    from app.models.gamification import Badge, UserBadge, UserXP, PointTransaction, Leaderboard, LeaderboardEntry, Challenge, ChallengeParticipant, GamificationTeam, Reward, RewardRedemption, UserGoal, GamificationEvent, UserProgress, AchievementCategory, AchievementType, PointActivityType, LeaderboardType, ChallengeType, RewardType
    return {'db': db, _('models_chat_conversation.label.tenant_1'): Tenant,
        _('models___init__.label.permission_1'): Permission, _(
        'models___init__.label.role_1'): Role, _(
        'i18n_content_translation_service.label.user_2'): User, _(
        'models___init__.label.tokenblocklist_1'): TokenBlocklist, _(
        'models___init__.label.userrole_1'): UserRole, _(
        'models___init__.label.userprofile_1'): UserProfile, _(
        'models___init__.label.useractivity_1'): UserActivity, _(
        'models___init__.label.userpreference_1'): UserPreference, _(
        'api_reports.label.beneficiary'): Beneficiary, _(
        'models___init__.label.note_1'): Note, _(
        'models___init__.label.beneficiaryappointment_1'):
        BeneficiaryAppointment, _(
        'models___init__.label.beneficiarydocument_1'): BeneficiaryDocument,
        _('core_user_service_example.label.test'): Test, _(
        'models___init__.label.testset_1'): TestSet, _(
        'models_test.label.question'): Question, _(
        'models_test.label.testsession_1'): TestSession, _(
        'models_test.label.response_1'): Response, _(
        'models___init__.label.aifeedback_1'): AIFeedback, _(
        'api_tests.label.evaluation'): Evaluation, _(
        'ai_content_recommendations.label.assessment'): Assessment, _(
        'models_adaptive_test.label.adaptivetestpool_1'): AdaptiveTestPool,
        _('models_adaptive_test.label.adaptivequestion_1'):
        AdaptiveQuestion, _(
        'models_adaptive_test.label.adaptivetestsession_2'):
        AdaptiveTestSession, _(
        'models_adaptive_test.label.adaptiveresponse_1'): AdaptiveResponse,
        _('models___init__.label.adaptivetestreport_1'): AdaptiveTestReport,
        _('sync_sync_service.label.document'): Document, _(
        'models___init__.label.documentpermission_1'): DocumentPermission,
        _('models___init__.label.folder_1'): Folder, _(
        'models_recurring_appointment.label.appointment'): Appointment, _(
        'models_recurring_appointment.label.recurringpattern'):
        RecurringPattern, _('models_appointment.label.appointmentseries'):
        AppointmentSeries, _('models___init__.label.availabilityschedule_1'
        ): AvailabilitySchedule, _(
        'models_availability.label.availabilityslot'): AvailabilitySlot, _(
        'models___init__.label.availabilityexception_1'):
        AvailabilityException, _('api_reports.label.program'): Program, _(
        'models_program.label.programmodule_1'): ProgramModule, _(
        'models_program.label.programenrollment'): ProgramEnrollment, _(
        'models_program.label.trainingsession_2'): TrainingSession, _(
        'models_program.label.sessionattendance'): SessionAttendance, _(
        'api_notifications.label.notification'): Notification, _(
        'models___init__.label.messagethread_1'): MessageThread, _(
        'models___init__.label.threadparticipant_1'): ThreadParticipant, _(
        'sync___init__.label.message'): Message, _(
        'models___init__.label.readreceipt_1'): ReadReceipt, _(
        'reporting_export_service.label.report_5'): Report, _(
        'models_report.label.reportschedule'): ReportSchedule, _(
        'models___init__.label.activity_1'): Activity, _(
        'models___init__.label.monitoring_1'): Monitoring, _(
        'i18n_translation_service.label.settings'): Settings, _(
        'models___init__.label.integration_1'): UserIntegration, _(
        'models___init__.label.twofactorauth_1'): TwoFactorAuth, _(
        'models___init__.label.twofactorsession_1'): TwoFactorSession, _(
        'models___init__.label.chatconversation_1'): ChatConversation, _(
        'models_chat_conversation.label.chatmessage'): ChatMessage, _(
        'models___init__.label.chatratelimit_1'): ChatRateLimit, _(
        'models___init__.label.conversationtemplate_1'):
        ConversationTemplate, _(
        'models___init__.label.conversationstatus_1'): ConversationStatus,
        _('models___init__.label.messagerole_1'): MessageRole, _(
        'models_performance_prediction.label.predictionmodel_1'):
        PredictionModel, _(
        'models_performance_prediction.label.performanceprediction_1'):
        PerformancePrediction, _(
        'models_performance_prediction.label.predictionrecommendation'):
        PredictionRecommendation, _(
        'models___init__.label.modeltraininghistory_1'):
        ModelTrainingHistory, _('models___init__.label.contenttype_1'):
        ContentType, _('models_ai_question_generation.label.questiontype'):
        QuestionType, _(
        'models_ai_question_generation.label.bloomstaxonomy_1'):
        BloomsTaxonomy, _(
        'models_ai_question_generation.label.learningobjective'):
        LearningObjective, _(
        'models_ai_question_generation.label.questiongenerationrequest'):
        QuestionGenerationRequest, _(
        'models_ai_question_generation.label.generatedquestion_2'):
        GeneratedQuestion, _('models___init__.label.questionduplicate_1'):
        QuestionDuplicate, _(
        'models_ai_question_generation.label.questionbank'): QuestionBank,
        _('models___init__.label.questionbankquestion_1'):
        QuestionBankQuestion, _(
        'models___init__.label.generationanalytics_1'): GenerationAnalytics,
        _('programs_v2_util_routes.label.language'): Language, _(
        'models_i18n.label.multilingualcontent_1'): MultilingualContent, _(
        'models_i18n.label.translationproject'): TranslationProject, _(
        'models_i18n.label.translationworkflow'): TranslationWorkflow, _(
        'models___init__.label.userlanguagepreference_1'):
        UserLanguagePreference, _('models_gamification.label.badge'): Badge,
        _('models_gamification.label.userbadge'): UserBadge, _(
        'models_gamification.label.userxp'): UserXP, _(
        'models_gamification.label.pointtransaction'): PointTransaction, _(
        'models_gamification.label.leaderboard'): Leaderboard, _(
        'models_gamification.label.leaderboardentry'): LeaderboardEntry, _(
        'models_gamification.label.challenge'): Challenge, _(
        'models_gamification.label.challengeparticipant'):
        ChallengeParticipant, _(
        'models_gamification.label.gamificationteam'): GamificationTeam, _(
        'models_gamification.label.reward'): Reward, _(
        'models_gamification.label.rewardredemption'): RewardRedemption, _(
        'models___init__.label.usergoal_1'): UserGoal, _(
        'models___init__.label.gamificationevent_1'): GamificationEvent, _(
        'models___init__.label.userprogress_1'): UserProgress, _(
        'models___init__.label.achievementcategory_1'): AchievementCategory,
        _('models___init__.label.achievementtype_1'): AchievementType, _(
        'models___init__.label.pointactivitytype_1'): PointActivityType, _(
        'models___init__.label.leaderboardtype_1'): LeaderboardType, _(
        'models___init__.label.challengetype_1'): ChallengeType, _(
        'models___init__.label.rewardtype_1'): RewardType}


_models_cache = None


def get_models():
    _('models___init__.message.get_all_models_using_lazy_load')
    global _models_cache
    if _models_cache is None:
        _models_cache = _import_models()
    return _models_cache


def get_model(name):
    _('models___init__.message.get_a_specific_model_by_name')
    models = get_models()
    return models.get(name)


def __getattr__(name):
    _('models___init__.message.dynamic_import_for_backward_co')
    models = get_models()
    if name in models:
        return models[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


db = db
__all__ = ['db', 'get_models', 'get_model', _(
    'models_chat_conversation.label.tenant_1'), _(
    'models___init__.label.permission_1'), _('models___init__.label.role_1'
    ), _('i18n_content_translation_service.label.user_2'), _(
    'models___init__.label.tokenblocklist_1'), _(
    'models___init__.label.userrole_1'), _(
    'models___init__.label.userprofile_1'), _(
    'models___init__.label.useractivity_1'), _(
    'models___init__.label.userpreference_1'), _(
    'api_reports.label.beneficiary'), _('models___init__.label.note_1'), _(
    'models___init__.label.beneficiaryappointment_1'), _(
    'models___init__.label.beneficiarydocument_1'), _(
    'core_user_service_example.label.test'), _(
    'models___init__.label.testset_1'), _('models_test.label.question'), _(
    'models_test.label.testsession_1'), _('models_test.label.response_1'),
    _('models___init__.label.aifeedback_1'), _('api_tests.label.evaluation'
    ), _('ai_content_recommendations.label.assessment'), _(
    'models_adaptive_test.label.adaptivetestpool_1'), _(
    'models_adaptive_test.label.adaptivequestion_1'), _(
    'models_adaptive_test.label.adaptivetestsession_2'), _(
    'models_adaptive_test.label.adaptiveresponse_1'), _(
    'models___init__.label.adaptivetestreport_1'), _(
    'sync_sync_service.label.document'), _(
    'models___init__.label.documentpermission_1'), _(
    'models___init__.label.folder_1'), _(
    'models_recurring_appointment.label.appointment'), _(
    'models_recurring_appointment.label.recurringpattern'), _(
    'models_appointment.label.appointmentseries'), _(
    'models___init__.label.availabilityschedule_1'), _(
    'models_availability.label.availabilityslot'), _(
    'models___init__.label.availabilityexception_1'), _(
    'api_reports.label.program'), _('models_program.label.programmodule_1'),
    _('models_program.label.programenrollment'), _(
    'models_program.label.trainingsession_2'), _(
    'models_program.label.sessionattendance'), _(
    'api_notifications.label.notification'), _(
    'models___init__.label.messagethread_1'), _(
    'models___init__.label.threadparticipant_1'), _(
    'sync___init__.label.message'), _('models___init__.label.readreceipt_1'
    ), _('reporting_export_service.label.report_5'), _(
    'models_report.label.reportschedule'), _(
    'models___init__.label.activity_1'), _(
    'models___init__.label.monitoring_1'), _(
    'i18n_translation_service.label.settings'), _(
    'models___init__.label.integration_1'), _(
    'models___init__.label.twofactorauth_1'), _(
    'models___init__.label.twofactorsession_1'), _(
    'models___init__.label.chatconversation_1'), _(
    'models_chat_conversation.label.chatmessage'), _(
    'models___init__.label.chatratelimit_1'), _(
    'models___init__.label.conversationtemplate_1'), _(
    'models___init__.label.conversationstatus_1'), _(
    'models___init__.label.messagerole_1'), _(
    'models_performance_prediction.label.predictionmodel_1'), _(
    'models_performance_prediction.label.performanceprediction_1'), _(
    'models_performance_prediction.label.predictionrecommendation'), _(
    'models___init__.label.modeltraininghistory_1'), _(
    'models___init__.label.contenttype_1'), _(
    'models_ai_question_generation.label.sourcecontent'), _(
    'models_ai_question_generation.label.questiontype'), _(
    'models_ai_question_generation.label.bloomstaxonomy_1'), _(
    'models_ai_question_generation.label.learningobjective'), _(
    'models_ai_question_generation.label.questiongenerationrequest'), _(
    'models_ai_question_generation.label.generatedquestion_2'), _(
    'models___init__.label.questionduplicate_1'), _(
    'models_ai_question_generation.label.questionbank'), _(
    'models___init__.label.questionbankquestion_1'), _(
    'models___init__.label.generationanalytics_1'), _(
    'programs_v2_util_routes.label.language'), _(
    'models_i18n.label.multilingualcontent_1'), _(
    'models_i18n.label.translationproject'), _(
    'models_i18n.label.translationworkflow'), _(
    'models___init__.label.userlanguagepreference_1'), _(
    'models_gamification.label.badge'), _(
    'models_gamification.label.userbadge'), _(
    'models_gamification.label.userxp'), _(
    'models_gamification.label.pointtransaction'), _(
    'models_gamification.label.leaderboard'), _(
    'models_gamification.label.leaderboardentry'), _(
    'models_gamification.label.challenge'), _(
    'models_gamification.label.challengeparticipant'), _(
    'models_gamification.label.gamificationteam'), _(
    'models_gamification.label.reward'), _(
    'models_gamification.label.rewardredemption'), _(
    'models___init__.label.usergoal_1'), _(
    'models___init__.label.gamificationevent_1'), _(
    'models___init__.label.userprogress_1'), _(
    'models___init__.label.achievementcategory_1'), _(
    'models___init__.label.achievementtype_1'), _(
    'models___init__.label.pointactivitytype_1'), _(
    'models___init__.label.leaderboardtype_1'), _(
    'models___init__.label.challengetype_1'), _(
    'models___init__.label.rewardtype_1')]
