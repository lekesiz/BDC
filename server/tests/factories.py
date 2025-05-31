"""Test factories for generating test data."""

import factory
from factory.fuzzy import FuzzyChoice
from faker import Faker
from datetime import datetime, timedelta
from app.models import (
    User, Tenant, Beneficiary, Program, Evaluation, 
    Appointment, Document, Notification, Message
)
from app.models.test import Test, Question, TestSession
from app.models.profile import UserProfile
from app.models.settings import GeneralSettings, AppearanceSettings
from app.models.calendar import CalendarEvent
from app.models.availability import AvailabilitySchedule, AvailabilitySlot
from app.models.assessment import AssessmentTemplate, AssessmentSection, AssessmentQuestion
from app.extensions import db

fake = Faker()


class TenantFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Tenant instances."""
    
    class Meta:
        model = Tenant
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = factory.LazyAttribute(lambda _: fake.company())
    domain = factory.LazyAttribute(lambda _: fake.domain_name())
    is_active = True
    settings = factory.Dict({
        'max_users': 100,
        'features': ['evaluations', 'reports', 'analytics']
    })
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    role = FuzzyChoice(['admin', 'tenant_admin', 'trainer', 'student'])
    is_active = True
    tenant = factory.SubFactory(TenantFactory)
    password_hash = 'hashed_password'  # Will be set properly in tests
    created_at = factory.LazyFunction(datetime.utcnow)
    
    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        if create and extracted:
            obj.set_password(extracted)


class UserProfileFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating UserProfile instances."""
    
    class Meta:
        model = UserProfile
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    bio = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    avatar_url = factory.LazyAttribute(lambda _: fake.image_url())
    preferences = factory.Dict({
        'theme': 'light',
        'language': 'en',
        'notifications': True
    })


class BeneficiaryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Beneficiary instances."""
    
    class Meta:
        model = Beneficiary
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    phone = factory.LazyAttribute(lambda _: fake.phone_number())
    date_of_birth = factory.LazyAttribute(lambda _: fake.date_of_birth(minimum_age=18, maximum_age=65))
    user = factory.SubFactory(UserFactory, role='student')
    tenant = factory.SubFactory(TenantFactory)
    status = 'active'
    created_at = factory.LazyFunction(datetime.utcnow)


class ProgramFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Program instances."""
    
    class Meta:
        model = Program
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = factory.LazyAttribute(lambda _: fake.catch_phrase())
    description = factory.LazyAttribute(lambda _: fake.text())
    tenant = factory.SubFactory(TenantFactory)
    start_date = factory.LazyFunction(datetime.utcnow)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=90))
    is_active = True
    max_participants = 20
    created_at = factory.LazyFunction(datetime.utcnow)


class EvaluationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Evaluation instances."""
    
    class Meta:
        model = Evaluation
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    beneficiary = factory.SubFactory(BeneficiaryFactory)
    evaluator = factory.SubFactory(UserFactory, role='trainer')
    title = factory.LazyAttribute(lambda _: f"Evaluation - {fake.catch_phrase()}")
    description = factory.LazyAttribute(lambda _: fake.text())
    status = FuzzyChoice(['pending', 'in_progress', 'completed'])
    score = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))
    created_at = factory.LazyFunction(datetime.utcnow)


class AppointmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Appointment instances."""
    
    class Meta:
        model = Appointment
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    beneficiary = factory.SubFactory(BeneficiaryFactory)
    trainer = factory.SubFactory(UserFactory, role='trainer')
    title = factory.LazyAttribute(lambda _: f"Session - {fake.catch_phrase()}")
    description = factory.LazyAttribute(lambda _: fake.text())
    start_time = factory.LazyAttribute(lambda _: fake.future_datetime(end_date='+30d'))
    end_time = factory.LazyAttribute(lambda o: o.start_time + timedelta(hours=1))
    status = 'scheduled'
    location = factory.LazyAttribute(lambda _: fake.address())
    created_at = factory.LazyFunction(datetime.utcnow)


class DocumentFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Document instances."""
    
    class Meta:
        model = Document
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = factory.LazyAttribute(lambda _: f"{fake.word()}_{fake.file_extension()}")
    file_path = factory.LazyAttribute(lambda o: f"/uploads/{o.name}")
    beneficiary = factory.SubFactory(BeneficiaryFactory)
    uploaded_by = factory.SubFactory(UserFactory)
    file_type = FuzzyChoice(['pdf', 'docx', 'jpg', 'png'])
    file_size = factory.LazyAttribute(lambda _: fake.random_int(min=1000, max=10000000))
    created_at = factory.LazyFunction(datetime.utcnow)


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Notification instances."""
    
    class Meta:
        model = Notification
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    type = FuzzyChoice(['info', 'warning', 'error', 'success'])
    title = factory.LazyAttribute(lambda _: fake.sentence())
    message = factory.LazyAttribute(lambda _: fake.text())
    read = False
    created_at = factory.LazyFunction(datetime.utcnow)


class TestFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Test instances."""
    
    class Meta:
        model = Test
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = factory.LazyAttribute(lambda _: f"Test - {fake.catch_phrase()}")
    description = factory.LazyAttribute(lambda _: fake.text())
    organization = factory.SubFactory(TenantFactory)
    test_type = FuzzyChoice(['cognitive', 'psychomotor', 'behavioral'])
    duration_minutes = factory.LazyAttribute(lambda _: fake.random_int(min=30, max=120))
    passing_score = 70
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class TestQuestionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating TestQuestion instances."""
    
    class Meta:
        model = TestQuestion
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    test = factory.SubFactory(TestFactory)
    text = factory.LazyAttribute(lambda _: fake.sentence() + "?")
    question_type = FuzzyChoice(['multiple_choice', 'true_false', 'essay'])
    points = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=10))
    order = factory.Sequence(lambda n: n)
    options = factory.LazyAttribute(lambda _: [fake.word() for _ in range(4)])
    correct_answer = factory.LazyAttribute(lambda o: o.options[0] if o.options else None)


class AssessmentTemplateFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating AssessmentTemplate instances."""
    
    class Meta:
        model = AssessmentTemplate
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    title = factory.LazyAttribute(lambda _: f"Assessment - {fake.catch_phrase()}")
    description = factory.LazyAttribute(lambda _: fake.text())
    organization = factory.SubFactory(TenantFactory)
    assessment_type = FuzzyChoice(['initial', 'progress', 'final'])
    version = "1.0"
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class CalendarEventFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating CalendarEvent instances."""
    
    class Meta:
        model = CalendarEvent
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence())
    description = factory.LazyAttribute(lambda _: fake.text())
    start_time = factory.LazyAttribute(lambda _: fake.future_datetime())
    end_time = factory.LazyAttribute(lambda o: o.start_time + timedelta(hours=1))
    event_type = FuzzyChoice(['meeting', 'appointment', 'training', 'other'])
    location = factory.LazyAttribute(lambda _: fake.address())
    created_at = factory.LazyFunction(datetime.utcnow)


# Batch creation functions
def create_test_data():
    """Create a comprehensive set of test data."""
    # Create tenants
    tenants = TenantFactory.create_batch(3)
    
    # Create users for each tenant
    for tenant in tenants:
        # Admin users
        UserFactory.create_batch(2, tenant=tenant, role='admin')
        # Trainers
        UserFactory.create_batch(5, tenant=tenant, role='trainer')
        # Students
        UserFactory.create_batch(10, tenant=tenant, role='student')
    
    # Create programs
    programs = []
    for tenant in tenants:
        programs.extend(ProgramFactory.create_batch(3, tenant=tenant))
    
    # Create beneficiaries
    beneficiaries = []
    for tenant in tenants:
        beneficiaries.extend(BeneficiaryFactory.create_batch(15, tenant=tenant))
    
    # Create evaluations
    for beneficiary in beneficiaries:
        EvaluationFactory.create_batch(3, beneficiary=beneficiary)
    
    # Create appointments
    trainers = User.query.filter_by(role='trainer').all()
    for beneficiary in beneficiaries[:10]:  # First 10 beneficiaries
        for trainer in trainers[:2]:  # First 2 trainers
            AppointmentFactory.create(beneficiary=beneficiary, trainer=trainer)
    
    return {
        'tenants': tenants,
        'programs': programs,
        'beneficiaries': beneficiaries
    }