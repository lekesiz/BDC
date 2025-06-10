"""Service configuration for the standardized service layer."""

from typing import Dict, Any
from flask import Flask

from app.services.core import ServiceContainer, get_service_container
from app.utils.logger import get_logger


logger = get_logger('ServiceConfig')


def configure_services(app: Flask, container: ServiceContainer = None) -> None:
    """
    Configure all services with dependency injection.
    
    Args:
        app: Flask application instance
        container: Service container (uses global if not provided)
    """
    container = container or get_service_container()
    
    # Configure repositories
    _configure_repositories(container)
    
    # Configure core services
    _configure_core_services(container)
    
    # Configure domain services
    _configure_domain_services(container)
    
    # Configure infrastructure services
    _configure_infrastructure_services(container)
    
    logger.info("Service configuration completed")


def _configure_repositories(container: ServiceContainer) -> None:
    """Configure repository services."""
    from app.repositories.user_repository import UserRepository
    from app.repositories.beneficiary_repository import BeneficiaryRepository
    from app.repositories.notification_repository import NotificationRepository
    from app.repositories.document_repository import DocumentRepository
    from app.repositories.appointment_repository import AppointmentRepository
    from app.repositories.program_repository import ProgramRepository
    from app.repositories.evaluation_repository import EvaluationRepository
    from app.repositories.calendar_repository import CalendarRepository
    from app.repositories.sms_repository import SMSRepository
    
    # Database session
    container.register('db_session', lambda: db.session, singleton=False)
    
    # User repository
    container.register(
        'user_repository',
        lambda db_session: UserRepository(db_session),
        dependencies=['db_session']
    )
    
    # Beneficiary repository
    container.register(
        'beneficiary_repository',
        lambda db_session: BeneficiaryRepository(db_session),
        dependencies=['db_session']
    )
    
    # Notification repository
    container.register(
        'notification_repository',
        lambda db_session: NotificationRepository(db_session),
        dependencies=['db_session']
    )
    
    # Document repository
    container.register(
        'document_repository',
        lambda db_session: DocumentRepository(db_session),
        dependencies=['db_session']
    )
    
    # Appointment repository
    container.register(
        'appointment_repository',
        lambda db_session: AppointmentRepository(db_session),
        dependencies=['db_session']
    )
    
    # Program repository
    container.register(
        'program_repository',
        lambda db_session: ProgramRepository(db_session),
        dependencies=['db_session']
    )
    
    # Evaluation repository
    container.register(
        'evaluation_repository',
        lambda db_session: EvaluationRepository(db_session),
        dependencies=['db_session']
    )
    
    # Calendar repository
    container.register(
        'calendar_repository',
        lambda db_session: CalendarRepository(db_session),
        dependencies=['db_session']
    )
    
    # SMS repository
    container.register(
        'sms_repository',
        lambda db_session: SMSRepository(db_session),
        dependencies=['db_session']
    )


def _configure_core_services(container: ServiceContainer) -> None:
    """Configure core services."""
    from app.core.security import SecurityManager
    from app.services.auth_service import AuthServiceV2
    from app.services.user_service import UserServiceV2
    
    # Security manager (singleton)
    container.register(
        'security_manager',
        SecurityManager,
        singleton=True
    )
    
    # Auth service
    container.register(
        'auth_service',
        lambda user_repository, security_manager: AuthServiceV2(
            user_repository=user_repository,
            security_manager=security_manager
        ),
        dependencies=['user_repository', 'security_manager']
    )
    
    # User service
    container.register(
        'user_service',
        lambda user_repository, security_manager: UserServiceV2(
            user_repository=user_repository,
            security_manager=security_manager
        ),
        dependencies=['user_repository', 'security_manager']
    )


def _configure_domain_services(container: ServiceContainer) -> None:
    """Configure domain-specific services."""
    from app.services.beneficiary_service import BeneficiaryService
    from app.services.notification_service import NotificationService
    from app.services.document_service import DocumentService
    from app.services.appointment_service import AppointmentService
    from app.services.program_service import ProgramService
    from app.services.evaluation_service import EvaluationService
    from app.services.calendar_service import CalendarService
    from app.services.analytics_service import AnalyticsService
    from app.services.gamification_service import GamificationService
    
    # Beneficiary service
    container.register(
        'beneficiary_service',
        lambda beneficiary_repository, user_repository: BeneficiaryService(
            beneficiary_repository=beneficiary_repository,
            user_repository=user_repository
        ),
        dependencies=['beneficiary_repository', 'user_repository']
    )
    
    # Notification service
    container.register(
        'notification_service',
        lambda notification_repository: NotificationService(
            notification_repository=notification_repository
        ),
        dependencies=['notification_repository']
    )
    
    # Document service
    container.register(
        'document_service',
        lambda document_repository, user_repository, beneficiary_repository, notification_service: DocumentService(
            document_repository=document_repository,
            user_repository=user_repository,
            beneficiary_repository=beneficiary_repository,
            notification_service=notification_service
        ),
        dependencies=['document_repository', 'user_repository', 
                     'beneficiary_repository', 'notification_service']
    )
    
    # Appointment service
    container.register(
        'appointment_service',
        lambda appointment_repository, notification_service, calendar_service: AppointmentService(
            appointment_repository=appointment_repository,
            notification_service=notification_service,
            calendar_service=calendar_service
        ),
        dependencies=['appointment_repository', 'notification_service', 'calendar_service']
    )
    
    # Program service
    container.register(
        'program_service',
        lambda program_repository, user_repository: ProgramService(
            program_repository=program_repository,
            user_repository=user_repository
        ),
        dependencies=['program_repository', 'user_repository']
    )
    
    # Evaluation service
    container.register(
        'evaluation_service',
        lambda evaluation_repository, beneficiary_repository, notification_service: EvaluationService(
            evaluation_repository=evaluation_repository,
            beneficiary_repository=beneficiary_repository,
            notification_service=notification_service
        ),
        dependencies=['evaluation_repository', 'beneficiary_repository', 
                     'notification_service']
    )
    
    # Calendar service
    container.register(
        'calendar_service',
        lambda calendar_repository, user_repository: CalendarService(
            calendar_repository=calendar_repository,
            user_repository=user_repository
        ),
        dependencies=['calendar_repository', 'user_repository']
    )
    
    # Analytics service
    container.register(
        'analytics_service',
        lambda user_repository, beneficiary_repository, program_repository: AnalyticsService(
            user_repository=user_repository,
            beneficiary_repository=beneficiary_repository,
            program_repository=program_repository
        ),
        dependencies=['user_repository', 'beneficiary_repository', 'program_repository']
    )
    
    # Gamification service
    container.register(
        'gamification_service',
        lambda user_repository, notification_service: GamificationService(
            user_repository=user_repository,
            notification_service=notification_service
        ),
        dependencies=['user_repository', 'notification_service']
    )


def _configure_infrastructure_services(container: ServiceContainer) -> None:
    """Configure infrastructure services."""
    from app.services.email_service import EmailService
    from app.services.sms_service import SMSService
    from app.services.storage_service import StorageService
    from app.services.search_service import SearchService
    from app.services.ai.ai_service import AIService
    
    # Email service
    container.register(
        'email_service',
        EmailService,
        singleton=True,
        metadata={'async': True}
    )
    
    # SMS service
    container.register(
        'sms_service',
        lambda sms_repository: SMSService(sms_repository),
        dependencies=['sms_repository'],
        metadata={'async': True}
    )
    
    # Storage service
    container.register(
        'storage_service',
        StorageService,
        singleton=True,
        metadata={'provider': 'local'}
    )
    
    # Search service
    container.register(
        'search_service',
        SearchService,
        singleton=True,
        metadata={'engine': 'elasticsearch'}
    )
    
    # AI service
    container.register(
        'ai_service',
        AIService,
        singleton=True,
        metadata={'provider': 'openai'}
    )


def create_service_aliases(container: ServiceContainer) -> None:
    """Create service aliases for convenience."""
    # Short aliases
    container.alias('auth', 'auth_service')
    container.alias('users', 'user_service')
    container.alias('notifications', 'notification_service')
    container.alias('docs', 'document_service')
    
    # Version aliases
    container.alias('auth_v2', 'auth_service')
    container.alias('user_service_v2', 'user_service')


def get_service_config() -> Dict[str, Any]:
    """Get service configuration for debugging/monitoring."""
    container = get_service_container()
    
    config = {
        'registered_services': container.list_services(),
        'service_count': len(container.list_services()),
        'services': {}
    }
    
    for service_name in container.list_services():
        metadata = container.get_metadata(service_name)
        config['services'][service_name] = {
            'metadata': metadata,
            'has_instance': service_name in container._singletons
        }
    
    return config


def validate_service_configuration() -> bool:
    """Validate that all required services are configured."""
    container = get_service_container()
    
    required_services = [
        'db_session',
        'security_manager',
        'auth_service',
        'user_service',
        'notification_service'
    ]
    
    missing = []
    for service in required_services:
        if not container.has(service):
            missing.append(service)
    
    if missing:
        logger.error(f"Missing required services: {', '.join(missing)}")
        return False
    
    logger.info("Service configuration validated successfully")
    return True


# Initialize services on import
from app.extensions import db

container = get_service_container()
configure_services(None, container)
create_service_aliases(container)