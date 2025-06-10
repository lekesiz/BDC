"""Optimized relationship loading configurations for SQLAlchemy models."""

from sqlalchemy.orm import joinedload, selectinload, subqueryload, contains_eager, lazyload

# Relationship loading strategies:
# - 'select' (lazy loading) - Default, causes N+1 queries
# - 'joined' - Single JOIN query, good for one-to-one/many-to-one
# - 'selectin' - One additional query using IN, good for small collections
# - 'subquery' - Subquery approach, good for larger collections
# - 'dynamic' - Returns query object, good for filtering but can cause N+1
# - 'immediate' - Loads on parent load (deprecated, use selectin)


class OptimizedRelationships:
    """Centralized relationship loading optimizations."""
    
    # User model optimizations
    USER_WITH_PROFILE = [
        selectinload('tenant'),  # Usually single tenant
        selectinload('roles'),   # Usually 1-3 roles
        selectinload('permissions'),  # Cached frequently
    ]
    
    USER_WITH_ACTIVITIES = [
        subqueryload('activities').limit(100),  # Recent activities only
        selectinload('notifications').filter_by(is_read=False),  # Unread only
    ]
    
    # Beneficiary model optimizations
    BENEFICIARY_WITH_DETAILS = [
        joinedload('user'),  # Always needed together
        joinedload('trainer'),  # One-to-one relationship
        joinedload('tenant'),  # One-to-one relationship
        selectinload('documents').filter_by(is_archived=False),  # Active documents
    ]
    
    BENEFICIARY_WITH_PROGRESS = [
        joinedload('user'),
        selectinload('appointments').filter_by(status='scheduled'),
        selectinload('evaluations').order_by('created_at').limit(10),
        selectinload('ai_analytics'),
    ]
    
    BENEFICIARY_FOR_LIST = [
        joinedload('user'),  # For name display
        joinedload('trainer'),  # For assignment info
        lazyload('*'),  # Explicitly lazy load everything else
    ]
    
    # Program model optimizations
    PROGRAM_WITH_DETAILS = [
        selectinload('modules'),
        selectinload('trainers'),
        selectinload('beneficiaries').limit(100),  # Paginate if needed
        joinedload('created_by'),
    ]
    
    PROGRAM_FOR_DASHBOARD = [
        selectinload('modules'),
        lazyload('beneficiaries'),  # Load count separately
        selectinload('trainers'),
    ]
    
    # Appointment model optimizations
    APPOINTMENT_WITH_PARTICIPANTS = [
        joinedload('trainer'),
        joinedload('beneficiary').joinedload('user'),
        joinedload('tenant'),
        selectinload('documents'),
    ]
    
    APPOINTMENT_FOR_CALENDAR = [
        joinedload('trainer'),
        joinedload('beneficiary').joinedload('user'),
        lazyload('*'),
    ]
    
    # Evaluation model optimizations
    EVALUATION_WITH_DETAILS = [
        joinedload('created_by'),
        joinedload('beneficiary').joinedload('user'),
        selectinload('questions'),
        selectinload('results'),
        selectinload('feedback'),
    ]
    
    EVALUATION_FOR_LIST = [
        joinedload('beneficiary').joinedload('user'),
        joinedload('created_by'),
        lazyload('questions'),  # Load separately if needed
        lazyload('results'),
    ]
    
    # Document model optimizations
    DOCUMENT_WITH_METADATA = [
        joinedload('uploaded_by'),
        joinedload('beneficiary'),
        selectinload('tags'),
        selectinload('permissions'),
    ]
    
    # Notification model optimizations
    NOTIFICATION_WITH_USER = [
        joinedload('user'),
        joinedload('related_user'),
    ]


def optimize_query(query, optimization_strategy):
    """Apply optimization strategy to a query."""
    for option in optimization_strategy:
        query = query.options(option)
    return query


# Query optimization helpers
def get_beneficiaries_for_trainer(trainer_id, db_session):
    """Optimized query for getting beneficiaries for a trainer."""
    from app.models.beneficiary import Beneficiary
    
    return db_session.query(Beneficiary).options(
        *OptimizedRelationships.BENEFICIARY_WITH_DETAILS
    ).filter_by(
        trainer_id=trainer_id,
        is_active=True
    ).all()


def get_upcoming_appointments(user_id, limit=10):
    """Optimized query for upcoming appointments."""
    from app.models.appointment import Appointment
    from datetime import datetime
    
    return Appointment.query.options(
        *OptimizedRelationships.APPOINTMENT_FOR_CALENDAR
    ).filter(
        Appointment.start_time > datetime.utcnow(),
        (Appointment.trainer_id == user_id) | (Appointment.beneficiary_id == user_id)
    ).order_by(
        Appointment.start_time
    ).limit(limit).all()


def get_recent_evaluations_for_beneficiary(beneficiary_id, limit=10):
    """Optimized query for recent evaluations."""
    from app.models.evaluation import Evaluation
    
    return Evaluation.query.options(
        *OptimizedRelationships.EVALUATION_FOR_LIST
    ).filter_by(
        beneficiary_id=beneficiary_id
    ).order_by(
        Evaluation.created_at.desc()
    ).limit(limit).all()


def get_program_with_statistics(program_id):
    """Get program with aggregated statistics."""
    from app.models.program import Program
    from sqlalchemy import func
    
    # Get program with basic details
    program = Program.query.options(
        *OptimizedRelationships.PROGRAM_FOR_DASHBOARD
    ).filter_by(id=program_id).first()
    
    if program:
        # Get counts separately to avoid loading all relationships
        program._beneficiary_count = program.beneficiaries.count()
        program._module_count = len(program.modules)
        program._completion_rate = calculate_program_completion_rate(program_id)
    
    return program


def calculate_program_completion_rate(program_id):
    """Calculate program completion rate without loading all data."""
    from app.models.program import Program, ProgramProgress
    from sqlalchemy import func
    
    result = db.session.query(
        func.avg(ProgramProgress.completion_percentage)
    ).filter_by(
        program_id=program_id,
        is_active=True
    ).scalar()
    
    return result or 0.0


# Batch loading optimization
def load_users_with_roles(user_ids):
    """Efficiently load multiple users with their roles."""
    from app.models.user import User
    
    # First query: get all users
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    # Second query: load all roles for these users at once
    User.query.filter(
        User.id.in_(user_ids)
    ).options(
        selectinload('roles')
    ).all()
    
    return users