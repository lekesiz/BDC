import pytest
from datetime import datetime, timedelta, date

from app import create_app, db
from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession, SessionAttendance
from app.models.tenant import Tenant
from app.models.user import User
from app.models.beneficiary import Beneficiary

@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    ctx = app.app_context()
    ctx.push()
    
    # Create tables
    db.create_all()
    
    # Setup test data
    tenant = Tenant(name="Test Tenant")
    db.session.add(tenant)
    
    admin_user = User(
        email="admin@test.com",
        password="password",
        first_name="Admin",
        last_name="User",
        role="tenant_admin",
        tenant_id=1
    )
    db.session.add(admin_user)
    
    beneficiary = Beneficiary(
        first_name="Test",
        last_name="Beneficiary",
        email="ben@test.com",
        tenant_id=1
    )
    db.session.add(beneficiary)
    
    db.session.commit()
    
    yield app
    
    # Teardown
    db.session.remove()
    db.drop_all()
    ctx.pop()


def test_program_table_empty(app_ctx):
    assert Program.query.count() == 0


def test_program_create_and_to_dict(app_ctx):
    """Test creation of a program and conversion to dictionary."""
    # Create a program
    program = Program(
        name="Test Program",
        description="Test Description",
        code="TP-001",
        duration=30,
        level="intermediate",
        category="technical",
        prerequisites="Basic knowledge",
        minimum_attendance=85.0,
        passing_score=75.0,
        status="active",
        is_active=True,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        max_participants=20,
        tenant_id=1,
        created_by_id=1
    )
    
    db.session.add(program)
    db.session.commit()
    
    # Retrieve program and check fields
    saved_program = Program.query.get(1)
    assert saved_program.name == "Test Program"
    assert saved_program.description == "Test Description"
    assert saved_program.code == "TP-001"
    assert saved_program.duration == 30
    assert saved_program.level == "intermediate"
    assert saved_program.category == "technical"
    assert saved_program.minimum_attendance == 85.0
    assert saved_program.passing_score == 75.0
    
    # Test to_dict method
    program_dict = saved_program.to_dict()
    assert program_dict['name'] == "Test Program"
    assert program_dict['duration'] == 30
    assert program_dict['duration_weeks'] == round(30 / 7.0, 2)
    assert program_dict['is_active'] is True
    assert program_dict['enrolled_count'] == 0
    assert program_dict['module_count'] == 0
    assert program_dict['session_count'] == 0
    

def test_program_module_relationships(app_ctx):
    """Test program module relationships."""
    # Create a program
    program = Program(
        name="Module Test Program",
        tenant_id=1,
        created_by_id=1
    )
    db.session.add(program)
    db.session.commit()
    
    # Add modules to program
    module1 = ProgramModule(
        program_id=program.id,
        name="Module 1",
        description="First module",
        order=1,
        content="Module content",
        resources=["resource1", "resource2"],
        duration=120,
        is_mandatory=True
    )
    
    module2 = ProgramModule(
        program_id=program.id,
        name="Module 2",
        description="Second module",
        order=2,
        duration=90,
        is_mandatory=False
    )
    
    db.session.add_all([module1, module2])
    db.session.commit()
    
    # Test relationship access
    assert len(program.modules) == 2
    assert program.modules[0].name == "Module 1"
    assert program.modules[1].name == "Module 2"
    
    # Test module to_dict
    module_dict = module1.to_dict()
    assert module_dict['name'] == "Module 1"
    assert module_dict['program_id'] == program.id
    assert module_dict['duration'] == 120
    assert module_dict['is_mandatory'] is True
    assert "resource1" in module_dict['resources']
    
    # Test program to_dict with modules
    program_dict = program.to_dict()
    assert program_dict['module_count'] == 2


def test_program_enrollment(app_ctx):
    """Test program enrollment functionality."""
    # Create a program
    program = Program(
        name="Enrollment Test Program",
        tenant_id=1,
        created_by_id=1
    )
    db.session.add(program)
    db.session.commit()
    
    # Enroll a beneficiary
    enrollment = ProgramEnrollment(
        program_id=program.id,
        beneficiary_id=1,
        enrollment_date=datetime.utcnow(),
        status="enrolled",
        progress=10.0,
        attendance_rate=90.0,
        overall_score=85.0
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    # Test relationship access
    assert len(program.enrollments) == 1
    assert program.enrollments[0].beneficiary_id == 1
    assert program.enrollments[0].status == "enrolled"
    
    # Test enrollment to_dict
    enrollment_dict = enrollment.to_dict()
    assert enrollment_dict['status'] == "enrolled"
    assert enrollment_dict['progress'] == 10.0
    assert enrollment_dict['attendance_rate'] == 90.0
    assert enrollment_dict['overall_score'] == 85.0
    assert enrollment_dict['beneficiary']['id'] == 1
    
    # Complete the enrollment
    enrollment.status = "completed"
    enrollment.completion_date = datetime.utcnow()
    enrollment.certificate_issued = True
    enrollment.certificate_number = "CERT-001"
    db.session.commit()
    
    # Check updated fields
    updated_enrollment = ProgramEnrollment.query.get(1)
    assert updated_enrollment.status == "completed"
    assert updated_enrollment.certificate_issued is True
    assert updated_enrollment.certificate_number == "CERT-001"


def test_training_session_and_attendance(app_ctx):
    """Test training session and attendance tracking."""
    # Create a program
    program = Program(
        name="Session Test Program",
        tenant_id=1,
        created_by_id=1
    )
    db.session.add(program)
    
    # Create a module
    module = ProgramModule(
        program_id=1,
        name="Session Module",
        order=1
    )
    db.session.add(module)
    db.session.commit()
    
    # Create a training session
    session = TrainingSession(
        program_id=program.id,
        module_id=module.id,
        trainer_id=1,
        title="Training Session 1",
        description="First training session",
        session_date=datetime.utcnow() + timedelta(days=1),
        duration=120,
        location="Room 101",
        online_link="https://meet.example.com/session1",
        max_participants=15,
        attendance_required=True,
        status="scheduled"
    )
    db.session.add(session)
    db.session.commit()
    
    # Add attendance record
    attendance = SessionAttendance(
        session_id=session.id,
        beneficiary_id=1,
        status="registered"
    )
    db.session.add(attendance)
    db.session.commit()
    
    # Test relationships
    assert len(program.sessions) == 1
    assert program.sessions[0].title == "Training Session 1"
    assert len(session.attendance_records) == 1
    
    # Test session to_dict
    session_dict = session.to_dict()
    assert session_dict['title'] == "Training Session 1"
    assert session_dict['location'] == "Room 101"
    assert session_dict['online_link'] == "https://meet.example.com/session1"
    assert session_dict['attendee_count'] == 1
    
    # Mark attendance
    attendance.status = "present"
    attendance.check_in_time = datetime.utcnow()
    attendance.check_out_time = datetime.utcnow() + timedelta(hours=2)
    attendance.rating = 5
    attendance.feedback = "Great session!"
    db.session.commit()
    
    # Check updated attendance
    updated_attendance = SessionAttendance.query.get(1)
    assert updated_attendance.status == "present"
    assert updated_attendance.rating == 5
    assert updated_attendance.feedback == "Great session!"
    
    # Test attendance to_dict
    attendance_dict = updated_attendance.to_dict()
    assert attendance_dict['status'] == "present"
    assert attendance_dict['rating'] == 5
    assert attendance_dict['feedback'] == "Great session!"
    assert attendance_dict['beneficiary']['id'] == 1