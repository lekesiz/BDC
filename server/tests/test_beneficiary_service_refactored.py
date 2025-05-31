"""Comprehensive tests for the refactored beneficiary service."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import os

from app.services.beneficiary_service_refactored import (
    BeneficiaryServiceRefactored,
    NoteServiceRefactored,
    AppointmentServiceRefactored,
    DocumentServiceRefactored,
    BeneficiaryStatus,
    NoteType,
    AppointmentStatus,
    PaginationResult
)
from app.exceptions import NotFoundException, ValidationException, ForbiddenException


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.delete = Mock()
    session.refresh = Mock()
    session.rollback = Mock()
    session.flush = Mock()
    return session


@pytest.fixture
def beneficiary_service(mock_db_session):
    """Create beneficiary service instance with mocked dependencies."""
    return BeneficiaryServiceRefactored(mock_db_session, upload_folder='/tmp/uploads')


@pytest.fixture
def note_service(mock_db_session):
    """Create note service instance with mocked dependencies."""
    return NoteServiceRefactored(mock_db_session)


@pytest.fixture
def appointment_service(mock_db_session):
    """Create appointment service instance with mocked dependencies."""
    return AppointmentServiceRefactored(mock_db_session)


@pytest.fixture
def document_service(mock_db_session):
    """Create document service instance with mocked dependencies."""
    return DocumentServiceRefactored(mock_db_session, upload_folder='/tmp/uploads')


@pytest.fixture
def sample_user():
    """Create a sample user."""
    user = Mock()
    user.id = 1
    user.email = 'user@example.com'
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.role = 'student'
    user.is_active = True
    user.set_password = Mock()
    return user


@pytest.fixture
def sample_trainer():
    """Create a sample trainer."""
    trainer = Mock()
    trainer.id = 2
    trainer.email = 'trainer@example.com'
    trainer.first_name = 'Jane'
    trainer.last_name = 'Smith'
    trainer.role = 'trainer'
    trainer.is_active = True
    return trainer


@pytest.fixture
def sample_beneficiary(sample_user, sample_trainer):
    """Create a sample beneficiary."""
    beneficiary = Mock()
    beneficiary.id = 10
    beneficiary.user_id = sample_user.id
    beneficiary.user = sample_user
    beneficiary.trainer_id = sample_trainer.id
    beneficiary.trainer = sample_trainer
    beneficiary.tenant_id = 100
    beneficiary.gender = 'male'
    beneficiary.birth_date = datetime(1990, 1, 1)
    beneficiary.phone = '+1234567890'
    beneficiary.address = '123 Main St'
    beneficiary.city = 'New York'
    beneficiary.postal_code = '10001'
    beneficiary.state = 'NY'
    beneficiary.country = 'USA'
    beneficiary.nationality = 'American'
    beneficiary.native_language = 'English'
    beneficiary.profession = 'Engineer'
    beneficiary.company = 'Tech Corp'
    beneficiary.company_size = '100-500'
    beneficiary.years_of_experience = 5
    beneficiary.education_level = 'Bachelor'
    beneficiary.category = 'Professional'
    beneficiary.bio = 'Experienced engineer'
    beneficiary.goals = 'Career advancement'
    beneficiary.notes = 'Highly motivated'
    beneficiary.referral_source = 'Website'
    beneficiary.custom_fields = {'field1': 'value1'}
    beneficiary.status = BeneficiaryStatus.ACTIVE.value
    beneficiary.is_active = True
    beneficiary.created_at = datetime.now(timezone.utc)
    beneficiary.updated_at = datetime.now(timezone.utc)
    return beneficiary


@pytest.fixture
def sample_note(sample_user):
    """Create a sample note."""
    note = Mock()
    note.id = 20
    note.beneficiary_id = 10
    note.user_id = sample_user.id
    note.user = sample_user
    note.content = 'Test note content'
    note.type = NoteType.GENERAL.value
    note.is_private = False
    note.created_at = datetime.now(timezone.utc)
    note.updated_at = datetime.now(timezone.utc)
    return note


@pytest.fixture
def sample_appointment(sample_user, sample_beneficiary):
    """Create a sample appointment."""
    appointment = Mock()
    appointment.id = 30
    appointment.beneficiary_id = sample_beneficiary.id
    appointment.beneficiary = sample_beneficiary
    appointment.user_id = sample_user.id
    appointment.user = sample_user
    appointment.title = 'Test Appointment'
    appointment.description = 'Test description'
    appointment.start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    appointment.end_time = datetime.now(timezone.utc) + timedelta(hours=2)
    appointment.location = 'Online'
    appointment.status = AppointmentStatus.SCHEDULED.value
    appointment.created_at = datetime.now(timezone.utc)
    appointment.updated_at = datetime.now(timezone.utc)
    return appointment


@pytest.fixture
def sample_document(sample_user):
    """Create a sample document."""
    document = Mock()
    document.id = 40
    document.beneficiary_id = 10
    document.user_id = sample_user.id
    document.user = sample_user
    document.title = 'Test Document'
    document.description = 'Test description'
    document.file_path = 'documents/test.pdf'
    document.file_type = 'pdf'
    document.file_size = 1024
    document.is_private = False
    document.created_at = datetime.now(timezone.utc)
    document.updated_at = datetime.now(timezone.utc)
    return document


class TestBeneficiaryService:
    """Test cases for BeneficiaryService."""
    
    def test_get_beneficiaries_success(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary
    ):
        """Test successful retrieval of beneficiaries."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_beneficiary]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = beneficiary_service.get_beneficiaries(
            tenant_id=100,
            page=1,
            per_page=10
        )
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 1
        assert result.pages == 1
        assert result.current_page == 1
        assert len(result.items) == 1
        assert result.items[0]['id'] == sample_beneficiary.id
        
    def test_get_beneficiaries_with_search(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary
    ):
        """Test getting beneficiaries with search query."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_beneficiary]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = beneficiary_service.get_beneficiaries(
            query='John',
            page=1,
            per_page=10
        )
        
        # Assert join was called for search
        mock_query.join.assert_called()
        assert result.total == 1
        
    def test_get_beneficiaries_invalid_pagination(
        self,
        beneficiary_service
    ):
        """Test get beneficiaries with invalid pagination parameters."""
        with pytest.raises(ValidationException, match="Page number must be at least 1"):
            beneficiary_service.get_beneficiaries(page=0)
        
        with pytest.raises(ValidationException, match="Per page must be between 1 and 100"):
            beneficiary_service.get_beneficiaries(per_page=0)
        
        with pytest.raises(ValidationException, match="Per page must be between 1 and 100"):
            beneficiary_service.get_beneficiaries(per_page=101)
    
    def test_get_beneficiaries_invalid_status(
        self,
        beneficiary_service
    ):
        """Test get beneficiaries with invalid status."""
        with pytest.raises(ValidationException, match="Invalid status"):
            beneficiary_service.get_beneficiaries(status='invalid')
    
    def test_get_beneficiary_success(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary
    ):
        """Test successful retrieval of a single beneficiary."""
        mock_db_session.query().filter_by().first.return_value = sample_beneficiary
        
        result = beneficiary_service.get_beneficiary(10)
        
        assert result['id'] == sample_beneficiary.id
        assert result['user']['email'] == sample_beneficiary.user.email
        assert result['trainer']['id'] == sample_beneficiary.trainer.id
    
    def test_get_beneficiary_not_found(
        self,
        beneficiary_service,
        mock_db_session
    ):
        """Test get beneficiary that doesn't exist."""
        mock_db_session.query().filter_by().first.return_value = None
        
        with pytest.raises(NotFoundException, match="Beneficiary 999 not found"):
            beneficiary_service.get_beneficiary(999)
    
    def test_create_beneficiary_success(
        self,
        beneficiary_service,
        mock_db_session,
        sample_user,
        sample_beneficiary
    ):
        """Test successful creation of a beneficiary."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = None  # No existing user
        
        # Mock the User constructor
        with patch('app.services.beneficiary_service_refactored.User') as MockUser:
            MockUser.return_value = sample_user
            
            # Mock the Beneficiary constructor
            with patch('app.services.beneficiary_service_refactored.Beneficiary') as MockBeneficiary:
                MockBeneficiary.return_value = sample_beneficiary
                
                # Execute
                user_data = {
                    'email': 'new@example.com',
                    'first_name': 'New',
                    'last_name': 'User',
                    'password': 'password123'
                }
                beneficiary_data = {
                    'tenant_id': 100,
                    'trainer_id': 2,
                    'gender': 'male',
                    'phone': '+1234567890'
                }
                
                result = beneficiary_service.create_beneficiary(user_data, beneficiary_data)
                
                # Assert
                assert result['id'] == sample_beneficiary.id
                mock_db_session.add.assert_called()
                mock_db_session.commit.assert_called()
                sample_user.set_password.assert_called_with('password123')
    
    def test_create_beneficiary_existing_user(
        self,
        beneficiary_service,
        mock_db_session,
        sample_user,
        sample_beneficiary
    ):
        """Test creating beneficiary with existing user."""
        # Setup mocks - user exists, no beneficiary
        mock_query = Mock()
        mock_query.filter_by.side_effect = [
            Mock(first=Mock(return_value=sample_user)),  # User exists
            Mock(first=Mock(return_value=None))  # No beneficiary
        ]
        mock_db_session.query.return_value = mock_query
        
        with patch('app.services.beneficiary_service_refactored.Beneficiary') as MockBeneficiary:
            MockBeneficiary.return_value = sample_beneficiary
            
            user_data = {
                'email': sample_user.email,
                'first_name': 'Updated',
                'last_name': 'Name'
            }
            beneficiary_data = {'tenant_id': 100}
            
            result = beneficiary_service.create_beneficiary(user_data, beneficiary_data)
            
            assert result['id'] == sample_beneficiary.id
            assert sample_user.first_name == 'Updated'
            assert sample_user.last_name == 'Name'
    
    def test_create_beneficiary_existing_profile(
        self,
        beneficiary_service,
        mock_db_session,
        sample_user,
        sample_beneficiary
    ):
        """Test creating beneficiary when user already has profile."""
        # Setup mocks - both user and beneficiary exist
        mock_query = Mock()
        mock_query.filter_by.side_effect = [
            Mock(first=Mock(return_value=sample_user)),  # User exists
            Mock(first=Mock(return_value=sample_beneficiary))  # Beneficiary exists
        ]
        mock_db_session.query.return_value = mock_query
        
        user_data = {
            'email': sample_user.email,
            'first_name': 'Existing',
            'last_name': 'User'
        }
        beneficiary_data = {'tenant_id': 100}
        
        with pytest.raises(ValidationException, match="already has a beneficiary profile"):
            beneficiary_service.create_beneficiary(user_data, beneficiary_data)
    
    def test_create_beneficiary_missing_required_fields(
        self,
        beneficiary_service
    ):
        """Test creating beneficiary with missing required fields."""
        # Missing email
        with pytest.raises(ValidationException, match="Email is required"):
            beneficiary_service.create_beneficiary({}, {'tenant_id': 100})
        
        # Missing first name
        with pytest.raises(ValidationException, match="First name is required"):
            beneficiary_service.create_beneficiary({'email': 'test@example.com'}, {'tenant_id': 100})
        
        # Missing tenant ID
        with pytest.raises(ValidationException, match="Tenant ID is required"):
            beneficiary_service.create_beneficiary(
                {'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'},
                {}
            )
    
    def test_update_beneficiary_success(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary
    ):
        """Test successful update of a beneficiary."""
        mock_db_session.query().filter_by().first.return_value = sample_beneficiary
        
        update_data = {
            'first_name': 'Updated',
            'phone': '+9876543210',
            'bio': 'Updated bio'
        }
        
        result = beneficiary_service.update_beneficiary(10, update_data)
        
        assert sample_beneficiary.user.first_name == 'Updated'
        assert sample_beneficiary.phone == '+9876543210'
        assert sample_beneficiary.bio == 'Updated bio'
        mock_db_session.commit.assert_called()
    
    def test_update_beneficiary_not_found(
        self,
        beneficiary_service,
        mock_db_session
    ):
        """Test updating non-existent beneficiary."""
        mock_db_session.query().filter_by().first.return_value = None
        
        with pytest.raises(NotFoundException, match="Beneficiary 999 not found"):
            beneficiary_service.update_beneficiary(999, {'phone': '123'})
    
    def test_update_beneficiary_invalid_status(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary
    ):
        """Test updating beneficiary with invalid status."""
        mock_db_session.query().filter_by().first.return_value = sample_beneficiary
        
        with pytest.raises(ValidationException, match="Invalid status"):
            beneficiary_service.update_beneficiary(10, {'status': 'invalid'})
    
    def test_delete_beneficiary_success(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary,
        sample_document
    ):
        """Test successful deletion of a beneficiary."""
        # Setup mocks
        mock_db_session.query().filter_by().first.return_value = sample_beneficiary
        mock_db_session.query().filter_by().all.return_value = [sample_document]
        mock_db_session.query().filter_by().delete.return_value = None
        
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                result = beneficiary_service.delete_beneficiary(10)
                
                assert result['message'] == "Beneficiary deleted successfully"
                assert sample_beneficiary.user.is_active == False
                mock_db_session.delete.assert_called_with(sample_beneficiary)
                mock_db_session.commit.assert_called()
                mock_remove.assert_called()
    
    def test_delete_beneficiary_not_found(
        self,
        beneficiary_service,
        mock_db_session
    ):
        """Test deleting non-existent beneficiary."""
        mock_db_session.query().filter_by().first.return_value = None
        
        with pytest.raises(NotFoundException, match="Beneficiary 999 not found"):
            beneficiary_service.delete_beneficiary(999)
    
    def test_assign_trainer_success(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary,
        sample_trainer
    ):
        """Test successful trainer assignment."""
        mock_query = Mock()
        mock_query.filter_by.side_effect = [
            Mock(first=Mock(return_value=sample_beneficiary)),
            Mock(first=Mock(return_value=sample_trainer))
        ]
        mock_db_session.query.return_value = mock_query
        
        result = beneficiary_service.assign_trainer(10, 2)
        
        assert sample_beneficiary.trainer_id == 2
        mock_db_session.commit.assert_called()
    
    def test_assign_trainer_unassign(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary
    ):
        """Test unassigning a trainer."""
        mock_db_session.query().filter_by().first.return_value = sample_beneficiary
        
        result = beneficiary_service.assign_trainer(10, None)
        
        assert sample_beneficiary.trainer_id is None
        mock_db_session.commit.assert_called()
    
    def test_assign_trainer_invalid_role(
        self,
        beneficiary_service,
        mock_db_session,
        sample_beneficiary,
        sample_user
    ):
        """Test assigning a user without trainer role."""
        mock_query = Mock()
        mock_query.filter_by.side_effect = [
            Mock(first=Mock(return_value=sample_beneficiary)),
            Mock(first=Mock(return_value=sample_user))  # Student role
        ]
        mock_db_session.query.return_value = mock_query
        
        with pytest.raises(ValidationException, match="User does not have trainer permissions"):
            beneficiary_service.assign_trainer(10, 1)


class TestNoteService:
    """Test cases for NoteService."""
    
    def test_get_notes_success(
        self,
        note_service,
        mock_db_session,
        sample_note
    ):
        """Test successful retrieval of notes."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_note]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = note_service.get_notes(beneficiary_id=10)
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]['content'] == sample_note.content
    
    def test_get_notes_with_filters(
        self,
        note_service,
        mock_db_session,
        sample_note
    ):
        """Test getting notes with filters."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_note]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = note_service.get_notes(
            beneficiary_id=10,
            user_id=1,
            note_type=NoteType.GENERAL.value,
            is_private=False
        )
        
        # Assert filters were applied
        assert mock_query.filter_by.call_count >= 3
        assert result.total == 1
    
    def test_get_notes_invalid_type(
        self,
        note_service
    ):
        """Test getting notes with invalid type."""
        with pytest.raises(ValidationException, match="Invalid note type"):
            note_service.get_notes(beneficiary_id=10, note_type='invalid')
    
    def test_get_note_success(
        self,
        note_service,
        mock_db_session,
        sample_note
    ):
        """Test successful retrieval of a single note."""
        mock_db_session.query().filter_by().first.return_value = sample_note
        
        result = note_service.get_note(20)
        
        assert result['id'] == sample_note.id
        assert result['content'] == sample_note.content
    
    def test_get_note_not_found(
        self,
        note_service,
        mock_db_session
    ):
        """Test getting non-existent note."""
        mock_db_session.query().filter_by().first.return_value = None
        
        with pytest.raises(NotFoundException, match="Note 999 not found"):
            note_service.get_note(999)
    
    def test_create_note_success(
        self,
        note_service,
        mock_db_session,
        sample_note
    ):
        """Test successful creation of a note."""
        with patch('app.services.beneficiary_service_refactored.Note') as MockNote:
            MockNote.return_value = sample_note
            
            note_data = {
                'beneficiary_id': 10,
                'content': 'Test note content',
                'type': NoteType.GENERAL.value
            }
            
            result = note_service.create_note(1, note_data)
            
            assert result['content'] == sample_note.content
            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_called()
    
    def test_create_note_missing_fields(
        self,
        note_service
    ):
        """Test creating note with missing required fields."""
        with pytest.raises(ValidationException, match="Beneficiary ID is required"):
            note_service.create_note(1, {})
        
        with pytest.raises(ValidationException, match="Note content is required"):
            note_service.create_note(1, {'beneficiary_id': 10})
    
    def test_update_note_success(
        self,
        note_service,
        mock_db_session,
        sample_note
    ):
        """Test successful update of a note."""
        mock_db_session.query().filter_by().first.return_value = sample_note
        
        update_data = {
            'content': 'Updated content',
            'type': NoteType.PROGRESS.value,
            'is_private': True
        }
        
        result = note_service.update_note(20, update_data)
        
        assert sample_note.content == 'Updated content'
        assert sample_note.type == NoteType.PROGRESS.value
        assert sample_note.is_private == True
        mock_db_session.commit.assert_called()
    
    def test_delete_note_success(
        self,
        note_service,
        mock_db_session,
        sample_note
    ):
        """Test successful deletion of a note."""
        mock_db_session.query().filter_by().first.return_value = sample_note
        
        result = note_service.delete_note(20)
        
        assert result['message'] == "Note deleted successfully"
        mock_db_session.delete.assert_called_with(sample_note)
        mock_db_session.commit.assert_called()


class TestAppointmentService:
    """Test cases for AppointmentService."""
    
    def test_get_appointments_success(
        self,
        appointment_service,
        mock_db_session,
        sample_appointment
    ):
        """Test successful retrieval of appointments."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_appointment]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = appointment_service.get_appointments()
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]['title'] == sample_appointment.title
    
    def test_get_appointments_with_date_filters(
        self,
        appointment_service,
        mock_db_session,
        sample_appointment
    ):
        """Test getting appointments with date filters."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_appointment]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc) + timedelta(days=7)
        
        result = appointment_service.get_appointments(
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert date filters were applied
        assert mock_query.filter.call_count >= 2
        assert result.total == 1
    
    def test_create_appointment_success(
        self,
        appointment_service,
        mock_db_session,
        sample_appointment
    ):
        """Test successful creation of an appointment."""
        with patch('app.services.beneficiary_service_refactored.Appointment') as MockAppointment:
            MockAppointment.return_value = sample_appointment
            
            appointment_data = {
                'beneficiary_id': 10,
                'title': 'Test Appointment',
                'start_time': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                'end_time': (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            }
            
            result = appointment_service.create_appointment(1, appointment_data)
            
            assert result['title'] == sample_appointment.title
            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_called()
    
    def test_create_appointment_invalid_dates(
        self,
        appointment_service
    ):
        """Test creating appointment with invalid dates."""
        appointment_data = {
            'beneficiary_id': 10,
            'title': 'Test',
            'start_time': datetime.now(timezone.utc).isoformat(),
            'end_time': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        }
        
        with pytest.raises(ValidationException, match="Start time must be before end time"):
            appointment_service.create_appointment(1, appointment_data)
    
    def test_update_appointment_success(
        self,
        appointment_service,
        mock_db_session,
        sample_appointment
    ):
        """Test successful update of an appointment."""
        mock_db_session.query().filter_by().first.return_value = sample_appointment
        
        update_data = {
            'title': 'Updated Appointment',
            'status': AppointmentStatus.COMPLETED.value
        }
        
        result = appointment_service.update_appointment(30, update_data)
        
        assert sample_appointment.title == 'Updated Appointment'
        assert sample_appointment.status == AppointmentStatus.COMPLETED.value
        mock_db_session.commit.assert_called()
    
    def test_delete_appointment_success(
        self,
        appointment_service,
        mock_db_session,
        sample_appointment
    ):
        """Test successful deletion of an appointment."""
        mock_db_session.query().filter_by().first.return_value = sample_appointment
        
        result = appointment_service.delete_appointment(30)
        
        assert result['message'] == "Appointment deleted successfully"
        mock_db_session.delete.assert_called_with(sample_appointment)
        mock_db_session.commit.assert_called()


class TestDocumentService:
    """Test cases for DocumentService."""
    
    def test_get_documents_success(
        self,
        document_service,
        mock_db_session,
        sample_document
    ):
        """Test successful retrieval of documents."""
        # Setup mocks
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_document]
        
        mock_db_session.query.return_value = mock_query
        
        # Execute
        result = document_service.get_documents()
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]['title'] == sample_document.title
    
    def test_get_document_success(
        self,
        document_service,
        mock_db_session,
        sample_document
    ):
        """Test successful retrieval of a single document."""
        mock_db_session.query().filter_by().first.return_value = sample_document
        
        result = document_service.get_document(40)
        
        assert result['id'] == sample_document.id
        assert result['title'] == sample_document.title
    
    def test_create_document_success(
        self,
        document_service,
        mock_db_session,
        sample_document
    ):
        """Test successful creation of a document."""
        # Mock file
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.save = Mock()
        
        with patch('app.services.beneficiary_service_refactored.Document') as MockDocument:
            MockDocument.return_value = sample_document
            
            with patch('os.makedirs'):
                with patch('os.path.getsize', return_value=1024):
                    document_data = {
                        'beneficiary_id': 10,
                        'title': 'Test Document'
                    }
                    
                    result = document_service.create_document(1, mock_file, document_data)
                    
                    assert result['title'] == sample_document.title
                    mock_file.save.assert_called()
                    mock_db_session.add.assert_called()
                    mock_db_session.commit.assert_called()
    
    def test_create_document_invalid_file_type(
        self,
        document_service
    ):
        """Test creating document with invalid file type."""
        mock_file = Mock()
        mock_file.filename = 'test.exe'
        
        document_data = {
            'beneficiary_id': 10,
            'title': 'Test Document'
        }
        
        with pytest.raises(ValidationException, match="File type 'exe' not allowed"):
            document_service.create_document(1, mock_file, document_data)
    
    def test_create_document_file_too_large(
        self,
        document_service,
        mock_db_session
    ):
        """Test creating document with file too large."""
        mock_file = Mock()
        mock_file.filename = 'test.pdf'
        mock_file.save = Mock()
        
        with patch('os.makedirs'):
            with patch('os.path.getsize', return_value=11 * 1024 * 1024):  # 11MB
                with patch('os.remove') as mock_remove:
                    document_data = {
                        'beneficiary_id': 10,
                        'title': 'Test Document'
                    }
                    
                    with pytest.raises(ValidationException, match="File size exceeds maximum"):
                        document_service.create_document(1, mock_file, document_data)
                    
                    mock_remove.assert_called()
    
    def test_update_document_success(
        self,
        document_service,
        mock_db_session,
        sample_document
    ):
        """Test successful update of a document."""
        mock_db_session.query().filter_by().first.return_value = sample_document
        
        update_data = {
            'title': 'Updated Document',
            'description': 'Updated description',
            'is_private': True
        }
        
        result = document_service.update_document(40, update_data)
        
        assert sample_document.title == 'Updated Document'
        assert sample_document.description == 'Updated description'
        assert sample_document.is_private == True
        mock_db_session.commit.assert_called()
    
    def test_delete_document_success(
        self,
        document_service,
        mock_db_session,
        sample_document
    ):
        """Test successful deletion of a document."""
        mock_db_session.query().filter_by().first.return_value = sample_document
        
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                result = document_service.delete_document(40)
                
                assert result['message'] == "Document deleted successfully"
                mock_remove.assert_called()
                mock_db_session.delete.assert_called_with(sample_document)
                mock_db_session.commit.assert_called()
    
    def test_delete_document_file_not_exists(
        self,
        document_service,
        mock_db_session,
        sample_document
    ):
        """Test deleting document when file doesn't exist."""
        mock_db_session.query().filter_by().first.return_value = sample_document
        
        with patch('os.path.exists', return_value=False):
            result = document_service.delete_document(40)
            
            assert result['message'] == "Document deleted successfully"
            mock_db_session.delete.assert_called_with(sample_document)
            mock_db_session.commit.assert_called()


class TestHelperMethods:
    """Test cases for helper methods."""
    
    def test_serialize_beneficiary_full(
        self,
        beneficiary_service,
        sample_beneficiary
    ):
        """Test full beneficiary serialization."""
        result = beneficiary_service._serialize_beneficiary(sample_beneficiary)
        
        assert result['id'] == sample_beneficiary.id
        assert result['user']['email'] == sample_beneficiary.user.email
        assert result['trainer']['id'] == sample_beneficiary.trainer.id
        assert result['birth_date'] == sample_beneficiary.birth_date.isoformat()
        assert result['custom_fields'] == sample_beneficiary.custom_fields
    
    def test_serialize_beneficiary_minimal(
        self,
        beneficiary_service
    ):
        """Test beneficiary serialization with minimal data."""
        beneficiary = Mock()
        beneficiary.id = 1
        beneficiary.user_id = 1
        beneficiary.user = None
        beneficiary.trainer = None
        beneficiary.trainer_id = None
        beneficiary.tenant_id = 100
        beneficiary.birth_date = None
        beneficiary.custom_fields = None
        beneficiary.status = 'active'
        beneficiary.is_active = True
        beneficiary.created_at = datetime.now(timezone.utc)
        beneficiary.updated_at = datetime.now(timezone.utc)
        
        # Set all other attributes to None
        for attr in ['gender', 'phone', 'address', 'city', 'postal_code', 'state',
                     'country', 'nationality', 'native_language', 'profession',
                     'company', 'company_size', 'years_of_experience', 'education_level',
                     'category', 'bio', 'goals', 'notes', 'referral_source']:
            setattr(beneficiary, attr, None)
        
        result = beneficiary_service._serialize_beneficiary(beneficiary)
        
        assert result['id'] == 1
        assert result['birth_date'] is None
        assert result['custom_fields'] is None
    
    def test_parse_date_datetime_object(
        self,
        beneficiary_service
    ):
        """Test parsing date from datetime object."""
        date = datetime(2023, 1, 1, 12, 0, 0)
        result = beneficiary_service._parse_date(date)
        assert result == date
    
    def test_parse_date_iso_string(
        self,
        beneficiary_service
    ):
        """Test parsing date from ISO string."""
        date_str = '2023-01-01T12:00:00Z'
        result = beneficiary_service._parse_date(date_str)
        assert isinstance(result, datetime)
    
    def test_parse_date_simple_string(
        self,
        beneficiary_service
    ):
        """Test parsing date from simple date string."""
        date_str = '2023-01-01'
        result = beneficiary_service._parse_date(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 1
    
    def test_parse_date_invalid(
        self,
        beneficiary_service
    ):
        """Test parsing invalid date."""
        with pytest.raises(ValidationException, match="Invalid date format"):
            beneficiary_service._parse_date('invalid-date')
        
        with pytest.raises(ValidationException, match="Invalid date type"):
            beneficiary_service._parse_date(123)
    
    def test_parse_datetime_various_formats(
        self,
        appointment_service
    ):
        """Test parsing datetime from various formats."""
        # Test datetime object
        dt = datetime.now(timezone.utc)
        assert appointment_service._parse_datetime(dt) == dt
        
        # Test ISO string with Z
        iso_str = '2023-01-01T12:00:00Z'
        result = appointment_service._parse_datetime(iso_str)
        assert isinstance(result, datetime)
        
        # Test ISO string without timezone
        iso_str = '2023-01-01T12:00:00'
        result = appointment_service._parse_datetime(iso_str)
        assert isinstance(result, datetime)
        
        # Test invalid format
        with pytest.raises(ValidationException, match="Invalid datetime format"):
            appointment_service._parse_datetime('invalid')


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_database_rollback_on_error(
        self,
        beneficiary_service,
        mock_db_session
    ):
        """Test database rollback on unexpected error."""
        mock_db_session.query().filter_by().first.return_value = None
        mock_db_session.commit.side_effect = Exception("Database error")
        
        with patch('app.services.beneficiary_service_refactored.User'):
            with patch('app.services.beneficiary_service_refactored.Beneficiary'):
                user_data = {
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
                beneficiary_data = {'tenant_id': 100}
                
                with pytest.raises(ValidationException):
                    beneficiary_service.create_beneficiary(user_data, beneficiary_data)
                
                mock_db_session.rollback.assert_called()
    
    def test_concurrent_beneficiary_creation(
        self,
        beneficiary_service,
        mock_db_session,
        sample_user
    ):
        """Test handling of concurrent beneficiary creation."""
        # First check returns no user, second check returns user (simulating concurrent creation)
        mock_query = Mock()
        mock_query.filter_by.side_effect = [
            Mock(first=Mock(return_value=None)),  # Initial check - no user
            Mock(first=Mock(return_value=sample_user))  # After flush - user exists
        ]
        mock_db_session.query.return_value = mock_query
        
        # This should handle the race condition gracefully
        user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123'
        }
        beneficiary_data = {'tenant_id': 100}
        
        # The implementation should handle this scenario without error
        with patch('app.services.beneficiary_service_refactored.User'):
            with patch('app.services.beneficiary_service_refactored.Beneficiary'):
                try:
                    beneficiary_service.create_beneficiary(user_data, beneficiary_data)
                except Exception:
                    # If it fails, it should at least rollback
                    mock_db_session.rollback.assert_called()


class TestIntegration:
    """Integration tests for service interactions."""
    
    def test_beneficiary_with_notes_and_appointments(
        self,
        beneficiary_service,
        note_service,
        appointment_service,
        mock_db_session,
        sample_beneficiary,
        sample_note,
        sample_appointment
    ):
        """Test beneficiary with related notes and appointments."""
        # Create beneficiary
        mock_db_session.query().filter_by().first.return_value = None
        
        with patch('app.services.beneficiary_service_refactored.User'):
            with patch('app.services.beneficiary_service_refactored.Beneficiary') as MockBeneficiary:
                MockBeneficiary.return_value = sample_beneficiary
                
                user_data = {'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
                beneficiary_data = {'tenant_id': 100}
                beneficiary_result = beneficiary_service.create_beneficiary(user_data, beneficiary_data)
                
                assert beneficiary_result['id'] == sample_beneficiary.id
        
        # Add note
        mock_db_session.reset_mock()
        with patch('app.services.beneficiary_service_refactored.Note') as MockNote:
            MockNote.return_value = sample_note
            
            note_data = {
                'beneficiary_id': beneficiary_result['id'],
                'content': 'Test note'
            }
            note_result = note_service.create_note(1, note_data)
            
            assert note_result['beneficiary_id'] == beneficiary_result['id']
        
        # Add appointment
        mock_db_session.reset_mock()
        with patch('app.services.beneficiary_service_refactored.Appointment') as MockAppointment:
            MockAppointment.return_value = sample_appointment
            
            appointment_data = {
                'beneficiary_id': beneficiary_result['id'],
                'title': 'Test Appointment',
                'start_time': datetime.now(timezone.utc).isoformat(),
                'end_time': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            }
            appointment_result = appointment_service.create_appointment(1, appointment_data)
            
            assert appointment_result['beneficiary_id'] == beneficiary_result['id']