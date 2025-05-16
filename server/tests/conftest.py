import pytest
import os
import tempfile
from datetime import datetime, timedelta
from app import create_app
from app.models import db, User, Tenant, Beneficiary, Program, Test, TestQuestion
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def test_app():
    """Create and configure a new app instance for each test session."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
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
        
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        db.session = session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant."""
    tenant = Tenant(
        name='Test Organization',
        domain='test.org',
        settings={'max_users': 100},
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    return tenant

@pytest.fixture
def test_user(db_session, test_tenant):
    """Create a test user."""
    user = User(
        email='test@example.com',
        username='testuser',
        tenant_id=test_tenant.id,
        role='tenant_admin',
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_trainer(db_session, test_tenant):
    """Create a test trainer."""
    trainer = User(
        email='trainer@example.com',
        username='trainer',
        tenant_id=test_tenant.id,
        role='trainer',
        is_active=True
    )
    trainer.set_password('password123')
    db_session.add(trainer)
    db_session.commit()
    return trainer

@pytest.fixture
def test_student(db_session, test_tenant):
    """Create a test student."""
    student = User(
        email='student@example.com',
        username='student',
        tenant_id=test_tenant.id,
        role='student',
        is_active=True
    )
    student.set_password('password123')
    db_session.add(student)
    db_session.commit()
    return student

@pytest.fixture
def test_beneficiary(db_session, test_tenant, test_trainer):
    """Create a test beneficiary."""
    beneficiary = Beneficiary(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='+1234567890',
        date_of_birth=datetime(1990, 1, 1),
        tenant_id=test_tenant.id,
        trainer_id=test_trainer.id,
        status='active'
    )
    db_session.add(beneficiary)
    db_session.commit()
    return beneficiary

@pytest.fixture
def test_program(db_session, test_tenant):
    """Create a test program."""
    program = Program(
        name='Test Program',
        description='A test training program',
        tenant_id=test_tenant.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        is_active=True
    )
    db_session.add(program)
    db_session.commit()
    return program

@pytest.fixture
def test_test(db_session, test_tenant, test_user):
    """Create a test assessment."""
    test = Test(
        name='Test Assessment',
        description='A test assessment',
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        duration_minutes=60,
        passing_score=70,
        is_active=True
    )
    db_session.add(test)
    db_session.commit()
    return test

@pytest.fixture
def test_question(db_session, test_test):
    """Create a test question."""
    question = TestQuestion(
        test_id=test_test.id,
        question_text='What is 2 + 2?',
        question_type='multiple_choice',
        points=10,
        correct_answer='4',
        answer_options=['1', '2', '3', '4']
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