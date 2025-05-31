import pytest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add parent directory to path to find config module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, User, Tenant, Beneficiary, Program
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def test_app():
    """Create and configure a new app instance for each test session."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    from config import TestingConfig
    app = create_app(TestingConfig)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture(scope='function')
def runner(test_app):
    """A test runner for the app's Click commands."""
    return test_app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(test_app):
    """Create a clean database session for each test function."""
    with test_app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        db.session.bind = connection
        session = db.session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    tenant = Tenant(
        name=f'Test Organization {unique_id}',
        slug=f'test-org-{unique_id}',
        email=f'admin-{unique_id}@test.org',
        settings={'max_users': 100},
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    return tenant

@pytest.fixture
def test_user(db_session, test_tenant):
    """Create a test user."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f'test-{unique_id}@example.com',
        username=f'testuser-{unique_id}',
        first_name='Test',
        last_name='User',
        tenant_id=test_tenant.id,
        role='tenant_admin',
        is_active=True
    )
    user.password = 'password123'
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_trainer(db_session, test_tenant):
    """Create a test trainer."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    trainer = User(
        email=f'trainer-{unique_id}@example.com',
        username=f'trainer-{unique_id}',
        first_name='Training',
        last_name='Trainer',
        tenant_id=test_tenant.id,
        role='trainer',
        is_active=True
    )
    trainer.password = 'password123'
    db_session.add(trainer)
    db_session.commit()
    return trainer

@pytest.fixture
def test_student(db_session, test_tenant):
    """Create a test student."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    student = User(
        email=f'student-{unique_id}@example.com',
        username=f'student-{unique_id}',
        first_name='Study',
        last_name='Student',
        tenant_id=test_tenant.id,
        role='student',
        is_active=True
    )
    student.password = 'password123'
    db_session.add(student)
    db_session.commit()
    return student

@pytest.fixture
def test_admin(db_session, test_tenant):
    """Create a test admin."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    admin = User(
        email=f'admin-{unique_id}@example.com',
        username=f'admin-{unique_id}',
        first_name='Admin',
        last_name='User',
        tenant_id=test_tenant.id,
        role='super_admin',
        is_active=True
    )
    admin.password = 'password123'
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def test_beneficiary(db_session, test_tenant, test_trainer):
    """Create a test beneficiary."""
    # First create a user for the beneficiary
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    beneficiary_user = User(
        email=f'beneficiary-{unique_id}@example.com',
        username=f'beneficiary-{unique_id}',
        first_name='John',
        last_name='Doe',
        tenant_id=test_tenant.id,
        role='student',
        is_active=True
    )
    beneficiary_user.password = 'password123'
    db_session.add(beneficiary_user)
    db_session.commit()
    
    # Now create the beneficiary profile
    beneficiary = Beneficiary(
        user_id=beneficiary_user.id,
        phone='+1234567890',
        birth_date=datetime(1990, 1, 1),
        tenant_id=test_tenant.id,
        trainer_id=test_trainer.id,
        status='active'
    )
    db_session.add(beneficiary)
    db_session.commit()
    return beneficiary

@pytest.fixture
def test_program(db_session, test_tenant, test_trainer):
    """Create a test program."""
    program = Program(
        name='Test Program',
        description='A test training program',
        tenant_id=test_tenant.id,
        created_by_id=test_trainer.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status='active',
        is_active=True
    )
    db_session.add(program)
    db_session.commit()
    return program

@pytest.fixture
def test_test(db_session, test_tenant, test_user):
    """Create a test assessment."""
    from app.models.test import TestSet
    test = TestSet(
        title='Test Assessment',
        description='A test assessment',
        tenant_id=test_tenant.id,
        creator_id=test_user.id,
        time_limit=60,
        passing_score=70,
        status='active'
    )
    db_session.add(test)
    db_session.commit()
    return test

@pytest.fixture
def test_document(db_session, test_trainer):
    """Create a test document."""
    from app.models.document import Document
    document = Document(
        title='Test Document',
        description='A test document',
        file_path='/uploads/test.pdf',
        file_type='pdf',
        file_size=1024,
        document_type='general',
        upload_by=test_trainer.id
    )
    db_session.add(document)
    db_session.commit()
    return document

@pytest.fixture
def test_notification(db_session, test_beneficiary):
    """Create a test notification."""
    from app.models.notification import Notification
    notification = Notification(
        user_id=test_beneficiary.user.id,
        type='info',
        title='Test Notification',
        message='This is a test notification',
        read=False
    )
    db_session.add(notification)
    db_session.commit()
    return notification

@pytest.fixture
def test_question(db_session, test_test):
    """Create a test question."""
    from app.models.test import Question
    question = Question(
        test_set_id=test_test.id,
        text='What is 2 + 2?',
        type='multiple_choice',
        points=10,
        correct_answer='4',
        options=['1', '2', '3', '4']
    )
    db_session.add(question)
    db_session.commit()
    return question

@pytest.fixture
def auth_headers(test_user):
    """Generate authorization headers for authenticated requests."""
    access_token = create_access_token(
        identity=test_user.id,
        additional_claims={
            'tenant_id': test_user.tenant_id,
            'role': test_user.role
        }
    )
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def trainer_headers(test_trainer):
    """Generate authorization headers for trainer requests."""
    access_token = create_access_token(
        identity=test_trainer.id,
        additional_claims={
            'tenant_id': test_trainer.tenant_id,
            'role': test_trainer.role
        }
    )
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def student_headers(test_student):
    """Generate authorization headers for student requests."""
    access_token = create_access_token(
        identity=test_student.id,
        additional_claims={
            'tenant_id': test_student.tenant_id,
            'role': test_student.role
        }
    )
    return {'Authorization': f'Bearer {access_token}'}