"""Tests for Program models."""

import pytest
from datetime import datetime, date
from unittest.mock import Mock
from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession, SessionAttendance


class TestProgramModel:
    """Test the Program model."""
    
    @pytest.fixture
    def program(self):
        """Create a test program."""
        return Program(
            name='Test Program',
            description='Test Description',
            code='TST001',
            duration=30,
            level='beginner',
            category='technical',
            tenant_id=1,
            created_by_id=1
        )
    
    def test_program_creation(self, program):
        """Test program creation with basic fields."""
        assert program.name == 'Test Program'
        assert program.description == 'Test Description'
        assert program.code == 'TST001'
        assert program.duration == 30
        assert program.level == 'beginner'
        assert program.category == 'technical'
        assert program.status == 'draft'
        assert program.is_active is True
    
    def test_program_defaults(self):
        """Test program default values."""
        program = Program(name='Minimal', tenant_id=1, created_by_id=1)
        assert program.status == 'draft'
        assert program.is_active is True
        assert program.minimum_attendance == 80.0
        assert program.passing_score == 70.0
    
    def test_program_to_dict_basic(self, program):
        """Test program to_dict method."""
        # Mock relationships
        program.enrollments = []
        program.modules = []
        program.sessions = []
        
        result = program.to_dict()
        
        assert result['name'] == 'Test Program'
        assert result['code'] == 'TST001'
        assert result['duration'] == 30
        assert result['duration_weeks'] == 4.29
        assert result['enrolled_count'] == 0
        assert result['module_count'] == 0
        assert result['session_count'] == 0
    
    def test_program_to_dict_with_dates(self, program):
        """Test program to_dict with dates."""
        program.start_date = date(2024, 1, 1)
        program.end_date = date(2024, 2, 1)
        program.enrollments = []
        program.modules = []
        program.sessions = []
        
        result = program.to_dict()
        
        assert result['start_date'] == '2024-01-01'
        assert result['end_date'] == '2024-02-01'
    
    def test_program_relationships(self, program):
        """Test program relationships."""
        assert hasattr(program, 'tenant')
        assert hasattr(program, 'created_by')
        assert hasattr(program, 'modules')
        assert hasattr(program, 'enrollments')
        assert hasattr(program, 'sessions')


class TestProgramModule:
    """Test the ProgramModule model."""
    
    @pytest.fixture
    def module(self):
        """Create a test module."""
        return ProgramModule(
            program_id=1,
            name='Module 1',
            description='First module',
            order=1,
            duration=8
        )
    
    def test_module_creation(self, module):
        """Test module creation."""
        assert module.name == 'Module 1'
        assert module.description == 'First module'
        assert module.order == 1
        assert module.duration == 8
        assert module.is_mandatory is True
    
    def test_module_defaults(self):
        """Test module default values."""
        module = ProgramModule(program_id=1, name='Test')
        assert module.order == 0
        assert module.is_mandatory is True
        assert module.resources == []
    
    def test_module_to_dict(self, module):
        """Test module to_dict method."""
        result = module.to_dict()
        
        assert result['name'] == 'Module 1'
        assert result['order'] == 1
        assert result['duration'] == 8
        assert result['is_mandatory'] is True


class TestProgramEnrollment:
    """Test the ProgramEnrollment model."""
    
    @pytest.fixture
    def enrollment(self):
        """Create a test enrollment."""
        enrollment = ProgramEnrollment(
            program_id=1,
            beneficiary_id=1,
            status='enrolled'
        )
        # Mock relationships
        enrollment.program = Mock()
        enrollment.program.id = 1
        enrollment.program.name = 'Test Program'
        enrollment.program.code = 'TST001'
        
        enrollment.beneficiary = Mock()
        enrollment.beneficiary.id = 1
        enrollment.beneficiary.first_name = 'John'
        enrollment.beneficiary.last_name = 'Doe'
        
        return enrollment
    
    def test_enrollment_creation(self, enrollment):
        """Test enrollment creation."""
        assert enrollment.program_id == 1
        assert enrollment.beneficiary_id == 1
        assert enrollment.status == 'enrolled'
        assert enrollment.progress == 0.0
        assert enrollment.attendance_rate == 0.0
    
    def test_enrollment_defaults(self):
        """Test enrollment default values."""
        enrollment = ProgramEnrollment(program_id=1, beneficiary_id=1)
        assert enrollment.status == 'enrolled'
        assert enrollment.progress == 0.0
        assert enrollment.certificate_issued is False
    
    def test_enrollment_to_dict(self, enrollment):
        """Test enrollment to_dict method."""
        enrollment.enrollment_date = datetime(2024, 1, 1, 10, 0, 0)
        
        result = enrollment.to_dict()
        
        assert result['program']['name'] == 'Test Program'
        assert result['program']['code'] == 'TST001'
        assert result['beneficiary']['name'] == 'John Doe'
        assert result['status'] == 'enrolled'
        assert result['enrollment_date'] == '2024-01-01T10:00:00'
    
    def test_enrollment_to_dict_completed(self, enrollment):
        """Test enrollment to_dict for completed enrollment."""
        enrollment.status = 'completed'
        enrollment.completion_date = datetime(2024, 2, 1, 15, 0, 0)
        enrollment.certificate_issued = True
        enrollment.certificate_number = 'CERT-001'
        
        result = enrollment.to_dict()
        
        assert result['status'] == 'completed'
        assert result['completion_date'] == '2024-02-01T15:00:00'
        assert result['certificate_issued'] is True
        assert result['certificate_number'] == 'CERT-001'


class TestTrainingSession:
    """Test the TrainingSession model."""
    
    @pytest.fixture
    def session(self):
        """Create a test session."""
        session = TrainingSession(
            program_id=1,
            trainer_id=1,
            title='Introduction Session',
            session_date=datetime(2024, 1, 15, 10, 0, 0),
            duration=120
        )
        # Mock relationships
        session.program = Mock()
        session.program.id = 1
        session.program.name = 'Test Program'
        
        session.trainer = Mock()
        session.trainer.id = 1
        session.trainer.first_name = 'Jane'
        session.trainer.last_name = 'Smith'
        
        session.attendance_records = []
        
        return session
    
    def test_session_creation(self, session):
        """Test session creation."""
        assert session.title == 'Introduction Session'
        assert session.duration == 120
        assert session.status == 'scheduled'
        assert session.attendance_required is True
    
    def test_session_to_dict(self, session):
        """Test session to_dict method."""
        result = session.to_dict()
        
        assert result['title'] == 'Introduction Session'
        assert result['program']['name'] == 'Test Program'
        assert result['trainer']['name'] == 'Jane Smith'
        assert result['duration'] == 120
        assert result['duration_weeks'] == 2.57
        assert result['session_date'] == '2024-01-15T10:00:00'
        assert result['attendee_count'] == 0
    
    def test_session_with_module(self, session):
        """Test session with module."""
        session.module = Mock()
        session.module.id = 1
        session.module.name = 'Module 1'
        
        result = session.to_dict()
        
        assert result['module']['id'] == 1
        assert result['module']['name'] == 'Module 1'


class TestSessionAttendance:
    """Test the SessionAttendance model."""
    
    @pytest.fixture
    def attendance(self):
        """Create a test attendance record."""
        attendance = SessionAttendance(
            session_id=1,
            beneficiary_id=1,
            status='present'
        )
        # Mock beneficiary
        attendance.beneficiary = Mock()
        attendance.beneficiary.id = 1
        attendance.beneficiary.first_name = 'John'
        attendance.beneficiary.last_name = 'Doe'
        
        return attendance
    
    def test_attendance_creation(self, attendance):
        """Test attendance creation."""
        assert attendance.session_id == 1
        assert attendance.beneficiary_id == 1
        assert attendance.status == 'present'
    
    def test_attendance_defaults(self):
        """Test attendance default values."""
        attendance = SessionAttendance(session_id=1, beneficiary_id=1)
        assert attendance.status == 'registered'
    
    def test_attendance_to_dict(self, attendance):
        """Test attendance to_dict method."""
        attendance.check_in_time = datetime(2024, 1, 15, 9, 55, 0)
        attendance.check_out_time = datetime(2024, 1, 15, 12, 5, 0)
        attendance.rating = 5
        attendance.feedback = 'Great session!'
        
        result = attendance.to_dict()
        
        assert result['beneficiary']['name'] == 'John Doe'
        assert result['status'] == 'present'
        assert result['check_in_time'] == '2024-01-15T09:55:00'
        assert result['check_out_time'] == '2024-01-15T12:05:00'
        assert result['rating'] == 5
        assert result['feedback'] == 'Great session!'