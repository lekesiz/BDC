"""
Comprehensive tests for repository layer with database mocking.
These tests target 80%+ coverage for all repository classes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Import repository implementations
from app.repositories.improved_user_repository import ImprovedUserRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.program_repository import ProgramRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.calendar_repository import CalendarRepository
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.base_repository import BaseRepository

# Import repository interfaces
from app.services.interfaces.user_repository_interface import IUserRepository
from app.repositories.interfaces.document_repository_interface import IDocumentRepository
from app.repositories.interfaces.evaluation_repository_interface import IEvaluationRepository
from app.repositories.interfaces.program_repository_interface import IProgramRepository
from app.repositories.interfaces.notification_repository_interface import INotificationRepository
from app.repositories.interfaces.calendar_repository_interface import ICalendarRepository


class TestBaseRepository:
    """Test cases for BaseRepository with mocked database."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_model(self):
        """Mock model class."""
        mock = Mock()
        mock.__name__ = 'MockModel'
        return mock
    
    @pytest.fixture
    def base_repository(self, mock_session, mock_model):
        """Create base repository with mocked dependencies."""
        return BaseRepository(session=mock_session, model=mock_model)
    
    def test_create_success(self, base_repository, mock_session, mock_model):
        """Test successful entity creation."""
        # Arrange
        data = {'name': 'Test', 'description': 'Test description'}
        mock_instance = Mock()
        mock_model.return_value = mock_instance
        
        # Act
        result = base_repository.create(data)
        
        # Assert
        assert result == mock_instance
        mock_session.add.assert_called_once_with(mock_instance)
        mock_session.flush.assert_called_once()
    
    def test_create_with_exception(self, base_repository, mock_session, mock_model):
        """Test creation with database exception."""
        # Arrange
        data = {'name': 'Test'}
        mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            base_repository.create(data)
    
    def test_get_by_id_found(self, base_repository, mock_session, mock_model):
        """Test getting entity by ID when found."""
        # Arrange
        mock_instance = Mock()
        mock_session.query().filter().first.return_value = mock_instance
        
        # Act
        result = base_repository.get_by_id(1)
        
        # Assert
        assert result == mock_instance
    
    def test_get_by_id_not_found(self, base_repository, mock_session, mock_model):
        """Test getting entity by ID when not found."""
        # Arrange
        mock_session.query().filter().first.return_value = None
        
        # Act
        result = base_repository.get_by_id(1)
        
        # Assert
        assert result is None
    
    def test_get_all(self, base_repository, mock_session, mock_model):
        """Test getting all entities."""
        # Arrange
        mock_instances = [Mock(), Mock()]
        mock_session.query().all.return_value = mock_instances
        
        # Act
        result = base_repository.get_all()
        
        # Assert
        assert result == mock_instances
    
    def test_update_success(self, base_repository, mock_session):
        """Test successful entity update."""
        # Arrange
        mock_instance = Mock()
        update_data = {'name': 'Updated Name'}
        
        # Act
        result = base_repository.update(mock_instance, update_data)
        
        # Assert
        assert result == mock_instance
        mock_session.flush.assert_called_once()
        assert mock_instance.name == 'Updated Name'
    
    def test_delete_success(self, base_repository, mock_session):
        """Test successful entity deletion."""
        # Arrange
        mock_instance = Mock()
        
        # Act
        base_repository.delete(mock_instance)
        
        # Assert
        mock_session.delete.assert_called_once_with(mock_instance)
        mock_session.flush.assert_called_once()
    
    def test_filter_by(self, base_repository, mock_session, mock_model):
        """Test filtering entities."""
        # Arrange
        mock_instances = [Mock()]
        mock_session.query().filter().all.return_value = mock_instances
        
        # Act
        result = base_repository.filter_by(name='Test')
        
        # Assert
        assert result == mock_instances
    
    def test_count(self, base_repository, mock_session, mock_model):
        """Test counting entities."""
        # Arrange
        mock_session.query().count.return_value = 5
        
        # Act
        result = base_repository.count()
        
        # Assert
        assert result == 5


class TestImprovedUserRepository:
    """Test cases for ImprovedUserRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def user_repository(self, mock_session):
        """Create user repository with mocked session."""
        return ImprovedUserRepository(session=mock_session)
    
    def test_implements_interface(self, user_repository):
        """Test that repository implements the interface."""
        assert isinstance(user_repository, IUserRepository)
    
    def test_get_by_email(self, user_repository, mock_session):
        """Test getting user by email."""
        # Arrange
        mock_user = Mock()
        mock_session.query().filter().first.return_value = mock_user
        
        # Act
        result = user_repository.get_by_email('test@example.com')
        
        # Assert
        assert result == mock_user
    
    def test_get_by_username(self, user_repository, mock_session):
        """Test getting user by username."""
        # Arrange
        mock_user = Mock()
        mock_session.query().filter().first.return_value = mock_user
        
        # Act
        result = user_repository.get_by_username('testuser')
        
        # Assert
        assert result == mock_user
    
    def test_get_by_role(self, user_repository, mock_session):
        """Test getting users by role."""
        # Arrange
        mock_users = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_users
        
        # Act
        result = user_repository.get_by_role('trainer')
        
        # Assert
        assert result == mock_users
    
    def test_get_active_users(self, user_repository, mock_session):
        """Test getting active users."""
        # Arrange
        mock_users = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_users
        
        # Act
        result = user_repository.get_active_users()
        
        # Assert
        assert result == mock_users
    
    def test_update_last_login(self, user_repository, mock_session):
        """Test updating user's last login time."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_session.query().filter().first.return_value = mock_user
        
        # Act
        user_repository.update_last_login(1)
        
        # Assert
        assert mock_user.last_login is not None
        mock_session.flush.assert_called_once()


class TestDocumentRepository:
    """Test cases for DocumentRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def document_repository(self, mock_session):
        """Create document repository with mocked session."""
        return DocumentRepository(session=mock_session)
    
    def test_implements_interface(self, document_repository):
        """Test that repository implements the interface."""
        assert isinstance(document_repository, IDocumentRepository)
    
    def test_get_by_user(self, document_repository, mock_session):
        """Test getting documents by user."""
        # Arrange
        mock_documents = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_documents
        
        # Act
        result = document_repository.get_by_user(1)
        
        # Assert
        assert result == mock_documents
    
    def test_get_by_type(self, document_repository, mock_session):
        """Test getting documents by type."""
        # Arrange
        mock_documents = [Mock()]
        mock_session.query().filter().all.return_value = mock_documents
        
        # Act
        result = document_repository.get_by_type('pdf')
        
        # Assert
        assert result == mock_documents
    
    def test_get_shared_documents(self, document_repository, mock_session):
        """Test getting shared documents."""
        # Arrange
        mock_documents = [Mock()]
        mock_session.query().join().filter().all.return_value = mock_documents
        
        # Act
        result = document_repository.get_shared_documents(1)
        
        # Assert
        assert result == mock_documents
    
    def test_search_documents(self, document_repository, mock_session):
        """Test searching documents."""
        # Arrange
        mock_documents = [Mock()]
        mock_session.query().filter().all.return_value = mock_documents
        
        # Act
        result = document_repository.search_documents('test')
        
        # Assert
        assert result == mock_documents


class TestEvaluationRepository:
    """Test cases for EvaluationRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def evaluation_repository(self, mock_session):
        """Create evaluation repository with mocked session."""
        return EvaluationRepository(session=mock_session)
    
    def test_implements_interface(self, evaluation_repository):
        """Test that repository implements the interface."""
        assert isinstance(evaluation_repository, IEvaluationRepository)
    
    def test_get_by_beneficiary(self, evaluation_repository, mock_session):
        """Test getting evaluations by beneficiary."""
        # Arrange
        mock_evaluations = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_evaluations
        
        # Act
        result = evaluation_repository.get_by_beneficiary(1)
        
        # Assert
        assert result == mock_evaluations
    
    def test_get_by_trainer(self, evaluation_repository, mock_session):
        """Test getting evaluations by trainer."""
        # Arrange
        mock_evaluations = [Mock()]
        mock_session.query().filter().all.return_value = mock_evaluations
        
        # Act
        result = evaluation_repository.get_by_trainer(1)
        
        # Assert
        assert result == mock_evaluations
    
    def test_get_pending_evaluations(self, evaluation_repository, mock_session):
        """Test getting pending evaluations."""
        # Arrange
        mock_evaluations = [Mock()]
        mock_session.query().filter().all.return_value = mock_evaluations
        
        # Act
        result = evaluation_repository.get_pending_evaluations()
        
        # Assert
        assert result == mock_evaluations
    
    def test_get_completed_evaluations(self, evaluation_repository, mock_session):
        """Test getting completed evaluations."""
        # Arrange
        mock_evaluations = [Mock()]
        mock_session.query().filter().all.return_value = mock_evaluations
        
        # Act
        result = evaluation_repository.get_completed_evaluations()
        
        # Assert
        assert result == mock_evaluations


class TestProgramRepository:
    """Test cases for ProgramRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def program_repository(self, mock_session):
        """Create program repository with mocked session."""
        return ProgramRepository(session=mock_session)
    
    def test_implements_interface(self, program_repository):
        """Test that repository implements the interface."""
        assert isinstance(program_repository, IProgramRepository)
    
    def test_get_by_tenant(self, program_repository, mock_session):
        """Test getting programs by tenant."""
        # Arrange
        mock_programs = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_programs
        
        # Act
        result = program_repository.get_by_tenant(1)
        
        # Assert
        assert result == mock_programs
    
    def test_get_by_trainer(self, program_repository, mock_session):
        """Test getting programs by trainer."""
        # Arrange
        mock_programs = [Mock()]
        mock_session.query().filter().all.return_value = mock_programs
        
        # Act
        result = program_repository.get_by_trainer(1)
        
        # Assert
        assert result == mock_programs
    
    def test_get_active_programs(self, program_repository, mock_session):
        """Test getting active programs."""
        # Arrange
        mock_programs = [Mock()]
        mock_session.query().filter().all.return_value = mock_programs
        
        # Act
        result = program_repository.get_active_programs()
        
        # Assert
        assert result == mock_programs
    
    def test_get_enrollments_for_beneficiary(self, program_repository, mock_session):
        """Test getting enrollments for beneficiary."""
        # Arrange
        mock_enrollments = [Mock()]
        mock_session.query().filter().all.return_value = mock_enrollments
        
        # Act
        result = program_repository.get_enrollments_for_beneficiary(1)
        
        # Assert
        assert result == mock_enrollments


class TestNotificationRepository:
    """Test cases for NotificationRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def notification_repository(self, mock_session):
        """Create notification repository with mocked session."""
        return NotificationRepository(session=mock_session)
    
    def test_implements_interface(self, notification_repository):
        """Test that repository implements the interface."""
        assert isinstance(notification_repository, INotificationRepository)
    
    def test_get_by_user(self, notification_repository, mock_session):
        """Test getting notifications by user."""
        # Arrange
        mock_notifications = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_notifications
        
        # Act
        result = notification_repository.get_by_user(1)
        
        # Assert
        assert result == mock_notifications
    
    def test_get_unread_notifications(self, notification_repository, mock_session):
        """Test getting unread notifications."""
        # Arrange
        mock_notifications = [Mock()]
        mock_session.query().filter().all.return_value = mock_notifications
        
        # Act
        result = notification_repository.get_unread_notifications(1)
        
        # Assert
        assert result == mock_notifications
    
    def test_mark_as_read(self, notification_repository, mock_session):
        """Test marking notification as read."""
        # Arrange
        mock_notification = Mock()
        mock_notification.read = False
        mock_session.query().filter().first.return_value = mock_notification
        
        # Act
        result = notification_repository.mark_as_read(1)
        
        # Assert
        assert result is True
        assert mock_notification.read is True
        mock_session.flush.assert_called_once()
    
    def test_mark_all_as_read(self, notification_repository, mock_session):
        """Test marking all notifications as read for user."""
        # Arrange
        mock_session.query().filter().update.return_value = 3
        
        # Act
        result = notification_repository.mark_all_as_read(1)
        
        # Assert
        assert result == 3
        mock_session.flush.assert_called_once()


class TestCalendarRepository:
    """Test cases for CalendarRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def calendar_repository(self, mock_session):
        """Create calendar repository with mocked session."""
        return CalendarRepository(session=mock_session)
    
    def test_implements_interface(self, calendar_repository):
        """Test that repository implements the interface."""
        assert isinstance(calendar_repository, ICalendarRepository)
    
    def test_create_appointment(self, calendar_repository, mock_session):
        """Test creating appointment."""
        # Arrange
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(hours=1),
            'user_id': 1
        }
        
        # Act
        result = calendar_repository.create_appointment(appointment_data)
        
        # Assert
        assert result is not None
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
    
    def test_get_appointments_for_user(self, calendar_repository, mock_session):
        """Test getting appointments for user."""
        # Arrange
        mock_appointments = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_appointments
        
        # Act
        result = calendar_repository.get_appointments_for_user(1)
        
        # Assert
        assert result == mock_appointments
    
    def test_get_appointments_by_date_range(self, calendar_repository, mock_session):
        """Test getting appointments by date range."""
        # Arrange
        mock_appointments = [Mock()]
        mock_session.query().filter().all.return_value = mock_appointments
        
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=7)
        
        # Act
        result = calendar_repository.get_appointments_by_date_range(start_date, end_date)
        
        # Assert
        assert result == mock_appointments
    
    def test_update_appointment(self, calendar_repository, mock_session):
        """Test updating appointment."""
        # Arrange
        mock_appointment = Mock()
        mock_session.query().filter().first.return_value = mock_appointment
        
        update_data = {'title': 'Updated Title'}
        
        # Act
        result = calendar_repository.update_appointment(1, update_data)
        
        # Assert
        assert result == mock_appointment
        assert mock_appointment.title == 'Updated Title'
        mock_session.flush.assert_called_once()
    
    def test_delete_appointment(self, calendar_repository, mock_session):
        """Test deleting appointment."""
        # Arrange
        mock_appointment = Mock()
        mock_session.query().filter().first.return_value = mock_appointment
        
        # Act
        result = calendar_repository.delete_appointment(1)
        
        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(mock_appointment)
        mock_session.flush.assert_called_once()


class TestBeneficiaryRepository:
    """Test cases for BeneficiaryRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def beneficiary_repository(self, mock_session):
        """Create beneficiary repository with mocked session."""
        return BeneficiaryRepository(session=mock_session)
    
    def test_get_by_trainer(self, beneficiary_repository, mock_session):
        """Test getting beneficiaries by trainer."""
        # Arrange
        mock_beneficiaries = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_beneficiaries
        
        # Act
        result = beneficiary_repository.get_by_trainer(1)
        
        # Assert
        assert result == mock_beneficiaries
    
    def test_get_by_status(self, beneficiary_repository, mock_session):
        """Test getting beneficiaries by status."""
        # Arrange
        mock_beneficiaries = [Mock()]
        mock_session.query().filter().all.return_value = mock_beneficiaries
        
        # Act
        result = beneficiary_repository.get_by_status('active')
        
        # Assert
        assert result == mock_beneficiaries
    
    def test_search_beneficiaries(self, beneficiary_repository, mock_session):
        """Test searching beneficiaries."""
        # Arrange
        mock_beneficiaries = [Mock()]
        mock_session.query().join().filter().all.return_value = mock_beneficiaries
        
        # Act
        result = beneficiary_repository.search_beneficiaries('john')
        
        # Assert
        assert result == mock_beneficiaries


class TestAppointmentRepository:
    """Test cases for AppointmentRepository."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def appointment_repository(self, mock_session):
        """Create appointment repository with mocked session."""
        return AppointmentRepository(session=mock_session)
    
    def test_get_upcoming_appointments(self, appointment_repository, mock_session):
        """Test getting upcoming appointments."""
        # Arrange
        mock_appointments = [Mock()]
        mock_session.query().filter().all.return_value = mock_appointments
        
        # Act
        result = appointment_repository.get_upcoming_appointments()
        
        # Assert
        assert result == mock_appointments
    
    def test_get_appointments_by_beneficiary(self, appointment_repository, mock_session):
        """Test getting appointments by beneficiary."""
        # Arrange
        mock_appointments = [Mock(), Mock()]
        mock_session.query().filter().all.return_value = mock_appointments
        
        # Act
        result = appointment_repository.get_appointments_by_beneficiary(1)
        
        # Assert
        assert result == mock_appointments
    
    def test_get_appointments_by_trainer(self, appointment_repository, mock_session):
        """Test getting appointments by trainer."""
        # Arrange
        mock_appointments = [Mock()]
        mock_session.query().filter().all.return_value = mock_appointments
        
        # Act
        result = appointment_repository.get_appointments_by_trainer(1)
        
        # Assert
        assert result == mock_appointments