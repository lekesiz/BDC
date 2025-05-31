"""Service tests with correct imports and structure."""

import pytest
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.services.beneficiary_service import BeneficiaryService
from app.services.program_service import ProgramService
from app.services.evaluation_service import EvaluationService
from app.services.notification_service import NotificationService
from app.services.document_service import DocumentService
from app.services.calendar_service import CalendarService
from app.services.availability_service import AvailabilityService
from app.models import User, Beneficiary, Program, Evaluation
from app.extensions import db
from unittest.mock import Mock, patch


class TestAuthService:
    """Test AuthService functionality."""
    
    @patch('app.models.User')
    @patch('app.extensions.db')
    def test_register_user(self, mock_db, mock_user, test_app):
        """Test user registration."""
        with test_app.app_context():
            # Mock user creation
            mock_user.return_value = Mock(id=1, email='test@example.com')
            
            # Test registration
            user = AuthService.register(
                email='test@example.com',
                password='secure123',
                first_name='Test',
                last_name='User'
            )
            
            assert user is not None
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.User')
    def test_login(self, mock_user, test_app):
        """Test user login."""
        with test_app.app_context():
            # Mock user
            user_instance = Mock()
            user_instance.id = 1
            user_instance.email = 'test@example.com'
            user_instance.verify_password.return_value = True
            
            # Mock query
            mock_user.query.filter_by.return_value.first.return_value = user_instance
            
            # Test login
            result = AuthService.login('test@example.com', 'password')
            
            assert result is not None
            assert 'access_token' in result
            assert 'refresh_token' in result
    
    @patch('app.models.User')
    def test_get_user_by_email(self, mock_user, test_app):
        """Test getting user by email."""
        with test_app.app_context():
            # Mock user
            user_instance = Mock(id=1, email='test@example.com')
            mock_user.query.filter_by.return_value.first.return_value = user_instance
            
            # Test get user
            user = AuthService.get_user_by_email('test@example.com')
            
            assert user is not None
            assert user.email == 'test@example.com'


class TestBeneficiaryService:
    """Test BeneficiaryService functionality."""
    
    @patch('app.models.Beneficiary')
    @patch('app.extensions.db')
    def test_create_beneficiary(self, mock_db, mock_beneficiary, test_app):
        """Test creating a beneficiary."""
        with test_app.app_context():
            # Mock beneficiary
            beneficiary_instance = Mock(id=1)
            mock_beneficiary.return_value = beneficiary_instance
            
            # Test creation
            beneficiary = BeneficiaryService.create_beneficiary(
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                tenant_id=1
            )
            
            assert beneficiary is not None
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.Beneficiary')
    def test_get_beneficiary_by_id(self, mock_beneficiary, test_app):
        """Test getting beneficiary by ID."""
        with test_app.app_context():
            # Mock beneficiary
            beneficiary_instance = Mock(id=1, first_name='John')
            mock_beneficiary.query.get.return_value = beneficiary_instance
            
            # Test get
            beneficiary = BeneficiaryService.get_beneficiary_by_id(1)
            
            assert beneficiary is not None
            assert beneficiary.first_name == 'John'
    
    @patch('app.models.Beneficiary')
    def test_list_beneficiaries(self, mock_beneficiary, test_app):
        """Test listing beneficiaries."""
        with test_app.app_context():
            # Mock beneficiaries
            beneficiaries = [Mock(id=1), Mock(id=2)]
            mock_query = Mock()
            mock_beneficiary.query.filter_by.return_value.all.return_value = beneficiaries
            
            # Test list
            result = BeneficiaryService.list_beneficiaries(tenant_id=1)
            
            assert len(result) == 2


class TestProgramService:
    """Test ProgramService functionality."""
    
    @patch('app.models.Program')
    @patch('app.extensions.db')
    def test_create_program(self, mock_db, mock_program, test_app):
        """Test creating a program."""
        with test_app.app_context():
            # Mock program
            program_instance = Mock(id=1, name='Test Program')
            mock_program.return_value = program_instance
            
            # Test creation
            program = ProgramService.create_program(
                name='Test Program',
                tenant_id=1,
                description='Test description'
            )
            
            assert program is not None
            assert program.name == 'Test Program'
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.Program')
    def test_list_programs(self, mock_program, test_app):
        """Test listing programs."""
        with test_app.app_context():
            # Mock programs
            programs = [Mock(id=1), Mock(id=2)]
            mock_query = Mock()
            mock_program.query.filter_by.return_value.order_by.return_value.all.return_value = programs
            
            # Test list
            result = ProgramService.list_programs(tenant_id=1)
            
            assert len(result) == 2
    
    @patch('app.models.Program')
    @patch('app.extensions.db')
    def test_update_program(self, mock_db, mock_program, test_app):
        """Test updating a program."""
        with test_app.app_context():
            # Mock program
            program = Mock(id=1, name='Old Name')
            mock_program.query.get.return_value = program
            
            # Test update
            updated = ProgramService.update_program(
                program,
                name='New Name',
                description='New description'
            )
            
            assert updated.name == 'New Name'
            assert updated.description == 'New description'
            mock_db.session.commit.assert_called_once()


class TestEvaluationService:
    """Test EvaluationService functionality."""
    
    @patch('app.models.Evaluation')
    @patch('app.extensions.db')
    def test_create_evaluation(self, mock_db, mock_evaluation, test_app):
        """Test creating an evaluation."""
        with test_app.app_context():
            # Mock evaluation
            evaluation_instance = Mock(id=1, title='Test Evaluation')
            mock_evaluation.return_value = evaluation_instance
            
            # Test creation
            evaluation = EvaluationService.create_evaluation(
                beneficiary_id=1,
                title='Test Evaluation',
                evaluator_id=1
            )
            
            assert evaluation is not None
            assert evaluation.title == 'Test Evaluation'
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.Evaluation')
    def test_get_beneficiary_evaluations(self, mock_evaluation, test_app):
        """Test getting evaluations for a beneficiary."""
        with test_app.app_context():
            # Mock evaluations
            evaluations = [Mock(id=1), Mock(id=2)]
            mock_evaluation.query.filter_by.return_value.all.return_value = evaluations
            
            # Test get
            result = EvaluationService.get_beneficiary_evaluations(beneficiary_id=1)
            
            assert len(result) == 2


class TestNotificationService:
    """Test NotificationService functionality."""
    
    @patch('app.models.Notification')
    @patch('app.extensions.db')
    def test_create_notification(self, mock_db, mock_notification, test_app):
        """Test creating a notification."""
        with test_app.app_context():
            # Mock notification
            notification_instance = Mock(id=1, title='Test')
            mock_notification.return_value = notification_instance
            
            # Test creation
            notification = NotificationService.create_notification(
                user_id=1,
                title='Test',
                message='Test message'
            )
            
            assert notification is not None
            assert notification.title == 'Test'
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.Notification')
    def test_get_user_notifications(self, mock_notification, test_app):
        """Test getting user notifications."""
        with test_app.app_context():
            # Mock notifications
            notifications = [Mock(id=1), Mock(id=2)]
            mock_query = Mock()
            mock_notification.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = notifications
            
            # Test get
            result = NotificationService.get_user_notifications(user_id=1)
            
            assert len(result) == 2
    
    @patch('app.models.Notification')
    @patch('app.extensions.db')
    def test_mark_as_read(self, mock_db, mock_notification, test_app):
        """Test marking notification as read."""
        with test_app.app_context():
            # Mock notification
            notification = Mock(id=1, read=False)
            mock_notification.query.get.return_value = notification
            
            # Test mark as read
            result = NotificationService.mark_as_read(1)
            
            assert result is True
            assert notification.read is True
            assert notification.read_at is not None
            mock_db.session.commit.assert_called_once()


class TestCalendarService:
    """Test CalendarService functionality."""
    
    @patch('app.models.calendar.CalendarEvent')
    @patch('app.extensions.db')
    def test_create_event(self, mock_db, mock_event, test_app):
        """Test creating a calendar event."""
        with test_app.app_context():
            # Mock event
            event_instance = Mock(id=1, title='Meeting')
            mock_event.return_value = event_instance
            
            # Test creation
            event = CalendarService.create_event(
                user_id=1,
                title='Meeting',
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1)
            )
            
            assert event is not None
            assert event.title == 'Meeting'
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.calendar.CalendarEvent')
    def test_get_user_events(self, mock_event, test_app):
        """Test getting user calendar events."""
        with test_app.app_context():
            # Mock events
            events = [Mock(id=1), Mock(id=2)]
            mock_event.query.filter_by.return_value.all.return_value = events
            
            # Test get
            result = CalendarService.get_user_events(user_id=1)
            
            assert len(result) == 2


class TestAvailabilityService:
    """Test AvailabilityService functionality."""
    
    @patch('app.models.availability.AvailabilitySchedule')
    @patch('app.extensions.db')
    def test_create_schedule(self, mock_db, mock_schedule, test_app):
        """Test creating availability schedule."""
        with test_app.app_context():
            # Mock schedule
            schedule_instance = Mock(id=1, title='Weekly Schedule')
            mock_schedule.return_value = schedule_instance
            
            # Test creation
            schedule = AvailabilityService.create_schedule(
                user_id=1,
                title='Weekly Schedule'
            )
            
            assert schedule is not None
            assert schedule.title == 'Weekly Schedule'
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.models.availability.AvailabilitySchedule')
    def test_get_user_schedule(self, mock_schedule, test_app):
        """Test getting user schedule."""
        with test_app.app_context():
            # Mock schedule
            schedule_instance = Mock(id=1, title='Schedule')
            mock_schedule.query.filter_by.return_value.first.return_value = schedule_instance
            
            # Test get
            schedule = AvailabilityService.get_user_schedule(user_id=1)
            
            assert schedule is not None
            assert schedule.title == 'Schedule'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])