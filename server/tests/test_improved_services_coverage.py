"""
Comprehensive tests for improved services using dependency injection architecture.
These tests focus on achieving high coverage for the refactored service layer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import service interfaces
from app.services.interfaces.auth_service_interface import IAuthService
from app.services.interfaces.document_service_interface import IDocumentService
from app.services.interfaces.evaluation_service_interface import IEvaluationService
from app.services.interfaces.program_service_interface import IProgramService
from app.services.interfaces.notification_service_interface import INotificationService
from app.services.interfaces.calendar_service_interface import ICalendarService

# Import service implementations
from app.services.improved_auth_service import ImprovedAuthService
from app.services.improved_document_service import ImprovedDocumentService
from app.services.improved_evaluation_service import ImprovedEvaluationService
from app.services.improved_program_service import ImprovedProgramService
from app.services.improved_notification_service import ImprovedNotificationService
from app.services.improved_calendar_service import ImprovedCalendarService

# Import repository interfaces
from app.services.interfaces.user_repository_interface import IUserRepository
from app.repositories.interfaces.document_repository_interface import IDocumentRepository
from app.repositories.interfaces.evaluation_repository_interface import IEvaluationRepository
from app.repositories.interfaces.program_repository_interface import IProgramRepository
from app.repositories.interfaces.notification_repository_interface import INotificationRepository
from app.repositories.interfaces.calendar_repository_interface import ICalendarRepository


class TestImprovedAuthService:
    """Test cases for ImprovedAuthService with mocked dependencies."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return Mock(spec=IUserRepository)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def auth_service(self, mock_user_repository, mock_db_session):
        """Create auth service with mocked dependencies."""
        return ImprovedAuthService(
            user_repository=mock_user_repository,
            db_session=mock_db_session
        )
    
    def test_service_implements_interface(self, auth_service):
        """Test that service implements the interface."""
        assert isinstance(auth_service, IAuthService)
    
    @patch('app.services.improved_auth_service.jwt')
    def test_login_success(self, mock_jwt, auth_service, mock_user_repository):
        """Test successful login."""
        # Arrange
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.is_active = True
        mock_user.check_password.return_value = True
        mock_user.role = 'user'
        mock_user.tenant_id = 1
        
        mock_user_repository.get_by_email.return_value = mock_user
        mock_jwt.create_access_token.return_value = 'test_token'
        
        # Act
        result = auth_service.login('test@example.com', 'password')
        
        # Assert
        assert result['success'] is True
        assert result['token'] == 'test_token'
        assert result['user']['id'] == 1
        mock_user_repository.get_by_email.assert_called_once_with('test@example.com')
    
    def test_login_invalid_email(self, auth_service, mock_user_repository):
        """Test login with invalid email."""
        # Arrange
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        result = auth_service.login('invalid@example.com', 'password')
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    def test_login_inactive_user(self, auth_service, mock_user_repository):
        """Test login with inactive user."""
        # Arrange
        mock_user = Mock()
        mock_user.is_active = False
        mock_user_repository.get_by_email.return_value = mock_user
        
        # Act
        result = auth_service.login('test@example.com', 'password')
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    def test_login_wrong_password(self, auth_service, mock_user_repository):
        """Test login with wrong password."""
        # Arrange
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.check_password.return_value = False
        mock_user_repository.get_by_email.return_value = mock_user
        
        # Act
        result = auth_service.login('test@example.com', 'wrong_password')
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    def test_register_success(self, auth_service, mock_user_repository, mock_db_session):
        """Test successful user registration."""
        # Arrange
        user_data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.create.return_value = Mock(id=1, email='newuser@example.com')
        
        # Act
        result = auth_service.register(user_data)
        
        # Assert
        assert result['success'] is True
        assert 'user' in result
        mock_user_repository.create.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_register_existing_email(self, auth_service, mock_user_repository):
        """Test registration with existing email."""
        # Arrange
        user_data = {'email': 'existing@example.com', 'password': 'password123'}
        mock_user_repository.get_by_email.return_value = Mock()
        
        # Act
        result = auth_service.register(user_data)
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    @patch('app.services.improved_auth_service.jwt')
    def test_verify_token_success(self, mock_jwt, auth_service):
        """Test successful token verification."""
        # Arrange
        mock_jwt.decode_token.return_value = {'user_id': 1, 'role': 'user'}
        
        # Act
        result = auth_service.verify_token('valid_token')
        
        # Assert
        assert result['valid'] is True
        assert result['user_id'] == 1
    
    @patch('app.services.improved_auth_service.jwt')
    def test_verify_token_invalid(self, mock_jwt, auth_service):
        """Test invalid token verification."""
        # Arrange
        mock_jwt.decode_token.side_effect = Exception('Invalid token')
        
        # Act
        result = auth_service.verify_token('invalid_token')
        
        # Assert
        assert result['valid'] is False
        assert 'error' in result


class TestImprovedDocumentService:
    """Test cases for ImprovedDocumentService with mocked dependencies."""
    
    @pytest.fixture
    def mock_document_repository(self):
        """Mock document repository."""
        return Mock(spec=IDocumentRepository)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def document_service(self, mock_document_repository, mock_db_session):
        """Create document service with mocked dependencies."""
        return ImprovedDocumentService(
            document_repository=mock_document_repository,
            db_session=mock_db_session
        )
    
    def test_service_implements_interface(self, document_service):
        """Test that service implements the interface."""
        assert isinstance(document_service, IDocumentService)
    
    def test_create_document_success(self, document_service, mock_document_repository, mock_db_session):
        """Test successful document creation."""
        # Arrange
        document_data = {
            'title': 'Test Document',
            'description': 'Test description',
            'file_path': '/uploads/test.pdf',
            'file_type': 'pdf',
            'upload_by': 1
        }
        
        mock_document = Mock()
        mock_document.id = 1
        mock_document.title = 'Test Document'
        mock_document_repository.create.return_value = mock_document
        
        # Act
        result = document_service.create_document(document_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_document_repository.create.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_get_document_by_id(self, document_service, mock_document_repository):
        """Test getting document by ID."""
        # Arrange
        mock_document = Mock()
        mock_document.id = 1
        mock_document_repository.get_by_id.return_value = mock_document
        
        # Act
        result = document_service.get_document_by_id(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_document_repository.get_by_id.assert_called_once_with(1)
    
    def test_update_document(self, document_service, mock_document_repository, mock_db_session):
        """Test document update."""
        # Arrange
        mock_document = Mock()
        mock_document.id = 1
        mock_document_repository.get_by_id.return_value = mock_document
        
        update_data = {'title': 'Updated Title'}
        
        # Act
        result = document_service.update_document(1, update_data)
        
        # Assert
        assert result is not None
        mock_document_repository.update.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_delete_document(self, document_service, mock_document_repository, mock_db_session):
        """Test document deletion."""
        # Arrange
        mock_document = Mock()
        mock_document_repository.get_by_id.return_value = mock_document
        
        # Act
        result = document_service.delete_document(1)
        
        # Assert
        assert result is True
        mock_document_repository.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_list_documents(self, document_service, mock_document_repository):
        """Test listing documents."""
        # Arrange
        mock_documents = [Mock(), Mock()]
        mock_document_repository.get_all.return_value = mock_documents
        
        # Act
        result = document_service.list_documents()
        
        # Assert
        assert len(result) == 2
        mock_document_repository.get_all.assert_called_once()


class TestImprovedEvaluationService:
    """Test cases for ImprovedEvaluationService with mocked dependencies."""
    
    @pytest.fixture
    def mock_evaluation_repository(self):
        """Mock evaluation repository."""
        return Mock(spec=IEvaluationRepository)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def evaluation_service(self, mock_evaluation_repository, mock_db_session):
        """Create evaluation service with mocked dependencies."""
        return ImprovedEvaluationService(
            evaluation_repository=mock_evaluation_repository,
            db_session=mock_db_session
        )
    
    def test_service_implements_interface(self, evaluation_service):
        """Test that service implements the interface."""
        assert isinstance(evaluation_service, IEvaluationService)
    
    def test_create_evaluation(self, evaluation_service, mock_evaluation_repository, mock_db_session):
        """Test evaluation creation."""
        # Arrange
        evaluation_data = {
            'title': 'Test Evaluation',
            'description': 'Test evaluation description',
            'created_by': 1,
            'tenant_id': 1
        }
        
        mock_evaluation = Mock()
        mock_evaluation.id = 1
        mock_evaluation_repository.create.return_value = mock_evaluation
        
        # Act
        result = evaluation_service.create_evaluation(evaluation_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_evaluation_repository.create.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_get_evaluation_by_id(self, evaluation_service, mock_evaluation_repository):
        """Test getting evaluation by ID."""
        # Arrange
        mock_evaluation = Mock()
        mock_evaluation.id = 1
        mock_evaluation_repository.get_by_id.return_value = mock_evaluation
        
        # Act
        result = evaluation_service.get_evaluation_by_id(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_evaluation_repository.get_by_id.assert_called_once_with(1)
    
    def test_submit_evaluation(self, evaluation_service, mock_evaluation_repository, mock_db_session):
        """Test evaluation submission."""
        # Arrange
        mock_evaluation = Mock()
        mock_evaluation.id = 1
        mock_evaluation.status = 'draft'
        mock_evaluation_repository.get_by_id.return_value = mock_evaluation
        
        submission_data = {
            'responses': [{'question_id': 1, 'answer': 'test answer'}],
            'beneficiary_id': 1
        }
        
        # Act
        result = evaluation_service.submit_evaluation(1, submission_data)
        
        # Assert
        assert result is not None
        mock_db_session.commit.assert_called_once()


class TestImprovedProgramService:
    """Test cases for ImprovedProgramService with mocked dependencies."""
    
    @pytest.fixture
    def mock_program_repository(self):
        """Mock program repository."""
        return Mock(spec=IProgramRepository)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def program_service(self, mock_program_repository, mock_db_session):
        """Create program service with mocked dependencies."""
        return ImprovedProgramService(
            program_repository=mock_program_repository,
            db_session=mock_db_session
        )
    
    def test_service_implements_interface(self, program_service):
        """Test that service implements the interface."""
        assert isinstance(program_service, IProgramService)
    
    def test_create_program(self, program_service, mock_program_repository, mock_db_session):
        """Test program creation."""
        # Arrange
        program_data = {
            'name': 'Test Program',
            'description': 'Test program description',
            'created_by_id': 1,
            'tenant_id': 1,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=30)
        }
        
        mock_program = Mock()
        mock_program.id = 1
        mock_program_repository.create.return_value = mock_program
        
        # Act
        result = program_service.create_program(program_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_program_repository.create.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_enroll_beneficiary(self, program_service, mock_program_repository, mock_db_session):
        """Test beneficiary enrollment."""
        # Arrange
        mock_program = Mock()
        mock_program.id = 1
        mock_program_repository.get_by_id.return_value = mock_program
        
        # Act
        result = program_service.enroll_beneficiary(1, 1)
        
        # Assert
        assert result is not None
        mock_db_session.commit.assert_called_once()


class TestImprovedNotificationService:
    """Test cases for ImprovedNotificationService with mocked dependencies."""
    
    @pytest.fixture
    def mock_notification_repository(self):
        """Mock notification repository."""
        return Mock(spec=INotificationRepository)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def notification_service(self, mock_notification_repository, mock_db_session):
        """Create notification service with mocked dependencies."""
        return ImprovedNotificationService(
            notification_repository=mock_notification_repository,
            db_session=mock_db_session
        )
    
    def test_service_implements_interface(self, notification_service):
        """Test that service implements the interface."""
        assert isinstance(notification_service, INotificationService)
    
    def test_send_notification(self, notification_service, mock_notification_repository, mock_db_session):
        """Test sending notification."""
        # Arrange
        notification_data = {
            'user_id': 1,
            'type': 'info',
            'title': 'Test Notification',
            'message': 'Test message'
        }
        
        mock_notification = Mock()
        mock_notification.id = 1
        mock_notification_repository.create.return_value = mock_notification
        
        # Act
        result = notification_service.send_notification(notification_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_notification_repository.create.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_mark_as_read(self, notification_service, mock_notification_repository, mock_db_session):
        """Test marking notification as read."""
        # Arrange
        mock_notification = Mock()
        mock_notification.id = 1
        mock_notification.read = False
        mock_notification_repository.get_by_id.return_value = mock_notification
        
        # Act
        result = notification_service.mark_as_read(1)
        
        # Assert
        assert result is True
        assert mock_notification.read is True
        mock_db_session.commit.assert_called_once()


class TestImprovedCalendarService:
    """Test cases for ImprovedCalendarService with mocked dependencies."""
    
    @pytest.fixture
    def mock_calendar_repository(self):
        """Mock calendar repository."""
        return Mock(spec=ICalendarRepository)
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def calendar_service(self, mock_calendar_repository, mock_db_session):
        """Create calendar service with mocked dependencies."""
        return ImprovedCalendarService(
            calendar_repository=mock_calendar_repository,
            db_session=mock_db_session
        )
    
    def test_service_implements_interface(self, calendar_service):
        """Test that service implements the interface."""
        assert isinstance(calendar_service, ICalendarService)
    
    def test_create_appointment(self, calendar_service, mock_calendar_repository, mock_db_session):
        """Test appointment creation."""
        # Arrange
        appointment_data = {
            'title': 'Test Appointment',
            'description': 'Test appointment description',
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(hours=1),
            'user_id': 1,
            'beneficiary_id': 1
        }
        
        mock_appointment = Mock()
        mock_appointment.id = 1
        mock_calendar_repository.create_appointment.return_value = mock_appointment
        
        # Act
        result = calendar_service.create_appointment(appointment_data)
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_calendar_repository.create_appointment.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_get_appointments_for_user(self, calendar_service, mock_calendar_repository):
        """Test getting appointments for user."""
        # Arrange
        mock_appointments = [Mock(), Mock()]
        mock_calendar_repository.get_appointments_for_user.return_value = mock_appointments
        
        # Act
        result = calendar_service.get_appointments_for_user(1)
        
        # Assert
        assert len(result) == 2
        mock_calendar_repository.get_appointments_for_user.assert_called_once_with(1)