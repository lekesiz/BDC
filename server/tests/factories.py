"""
Factory classes for test data generation in BDC application
"""
import random
import datetime
from faker import Faker
import factory
from factory.alchemy import SQLAlchemyModelFactory

from app import db
from app.models import (
    User, Beneficiary, Evaluation, Appointment, 
    Program, Document
)

fake = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory class for all models"""
    
    class Meta:
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    """Factory for User model"""
    
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    password = 'password123'  # Will use the password setter property
    role = 'student'  # Default role
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.datetime.now())
    last_login = factory.LazyFunction(lambda: datetime.datetime.now())
    tenant_id = 1  # Default tenant


class BeneficiaryFactory(BaseFactory):
    """Factory for Beneficiary model"""
    
    class Meta:
        model = Beneficiary

    user = factory.SubFactory(UserFactory)
    date_of_birth = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=18, maximum_age=35).strftime('%Y-%m-%d'))
    address = factory.LazyFunction(lambda: fake.address())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    status = factory.LazyFunction(lambda: random.choice(['active', 'inactive', 'suspended', 'graduated']))
    created_at = factory.LazyFunction(lambda: datetime.datetime.now())
    tenant_id = 1


class EvaluationFactory(BaseFactory):
    """Factory for Evaluation model"""
    
    class Meta:
        model = Evaluation

    beneficiary = factory.SubFactory(BeneficiaryFactory)
    evaluator = factory.SubFactory(UserFactory, role='trainer')
    type = factory.LazyFunction(lambda: random.choice(['initial', 'progress', 'final']))
    date = factory.LazyFunction(lambda: datetime.datetime.now().date())
    score = factory.LazyFunction(lambda: random.randint(0, 100))
    feedback = factory.LazyFunction(lambda: fake.paragraph())
    status = factory.LazyFunction(lambda: random.choice(['draft', 'submitted', 'reviewed', 'approved']))
    created_at = factory.LazyFunction(lambda: datetime.datetime.now())
    tenant_id = 1


class AppointmentFactory(BaseFactory):
    """Factory for Appointment model"""
    
    class Meta:
        model = Appointment

    beneficiary = factory.SubFactory(BeneficiaryFactory)
    trainer = factory.SubFactory(UserFactory, role='trainer')
    date = factory.LazyFunction(lambda: (datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30))).date())
    start_time = factory.LazyFunction(lambda: datetime.time(hour=random.randint(9, 16), minute=random.choice([0, 30])))
    end_time = factory.LazyAttribute(lambda o: datetime.time(hour=o.start_time.hour + 1, minute=o.start_time.minute))
    purpose = factory.LazyFunction(lambda: random.choice(['initial_consultation', 'progress_review', 'skill_assessment', 'mentoring', 'career_guidance']))
    status = factory.LazyFunction(lambda: random.choice(['scheduled', 'completed', 'cancelled', 'rescheduled']))
    notes = factory.LazyFunction(lambda: fake.paragraph())
    created_at = factory.LazyFunction(lambda: datetime.datetime.now())
    tenant_id = 1


class ProgramFactory(BaseFactory):
    """Factory for Program model"""
    
    class Meta:
        model = Program

    name = factory.LazyFunction(lambda: f"{fake.word().capitalize()} {fake.word().capitalize()} Program")
    description = factory.LazyFunction(lambda: fake.paragraph())
    start_date = factory.LazyFunction(lambda: datetime.datetime.now().date())
    end_date = factory.LazyFunction(lambda: (datetime.datetime.now() + datetime.timedelta(days=90)).date())
    status = factory.LazyFunction(lambda: random.choice(['active', 'inactive', 'completed', 'planned']))
    created_by = factory.SubFactory(UserFactory, role='admin')
    created_at = factory.LazyFunction(lambda: datetime.datetime.now())
    tenant_id = 1


class DocumentFactory(BaseFactory):
    """Factory for Document model"""
    
    class Meta:
        model = Document

    title = factory.LazyFunction(lambda: fake.sentence())
    file_path = factory.LazyFunction(lambda: f"uploads/{fake.uuid4()}.pdf")
    file_type = 'pdf'
    file_size = factory.LazyFunction(lambda: random.randint(100000, 5000000))
    uploaded_by = factory.SubFactory(UserFactory)
    beneficiary = factory.SubFactory(BeneficiaryFactory)
    category = factory.LazyFunction(lambda: random.choice(['id', 'diploma', 'certificate', 'contract', 'other']))
    description = factory.LazyFunction(lambda: fake.paragraph())
    created_at = factory.LazyFunction(lambda: datetime.datetime.now())
    tenant_id = 1


# Removed CategoryFactory as Category model no longer exists 