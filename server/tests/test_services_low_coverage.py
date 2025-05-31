"""Tests for services with low coverage."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone, timedelta
import json
import os
from werkzeug.datastructures import FileStorage

# Test auth_service.py
class TestAuthService:
    """Test cases for AuthService."""
    
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_authenticate_user_success(self, mock_user_model, mock_db):
        """Test successful user authentication."""
        from app.services.auth_service import AuthService
        
        # Create mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.check_password.return_value = True
        mock_user.is_active = True
        mock_user.failed_login_attempts = 0
        
        # Mock query
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        user = AuthService.authenticate_user('test@example.com', 'password123')
        
        assert user == mock_user
        mock_user.check_password.assert_called_once_with('password123')
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_authenticate_user_invalid_password(self, mock_user_model):
        """Test authentication with invalid password."""
        from app.services.auth_service import AuthService
        
        mock_user = Mock()
        mock_user.check_password.return_value = False
        mock_user.failed_login_attempts = 0
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        user = AuthService.authenticate_user('test@example.com', 'wrongpassword')
        
        assert user is None
        assert mock_user.failed_login_attempts == 1
    
    @patch('app.services.auth_service.User')
    def test_authenticate_user_locked_account(self, mock_user_model):
        """Test authentication with locked account."""
        from app.services.auth_service import AuthService
        
        mock_user = Mock()
        mock_user.failed_login_attempts = 5
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_user
        mock_user_model.query = mock_query
        
        user = AuthService.authenticate_user('test@example.com', 'password')
        
        assert user is None
    
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.User')
    def test_create_user_success(self, mock_user_model, mock_db):
        """Test successful user creation."""
        from app.services.auth_service import AuthService
        
        # Mock that user doesn't exist
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_user_model.query = mock_query
        
        # Mock new user
        mock_new_user = Mock()
        mock_user_model.return_value = mock_new_user
        
        user_data = {
            'email': 'new@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        
        user = AuthService.create_user(user_data)
        
        assert user == mock_new_user
        mock_db.session.add.assert_called_once_with(mock_new_user)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    def test_create_user_already_exists(self, mock_user_model):
        """Test creating user that already exists."""
        from app.services.auth_service import AuthService
        from app.exceptions import ValidationException
        
        # Mock that user exists
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = Mock()  # User exists
        mock_user_model.query = mock_query
        
        user_data = {
            'email': 'existing@example.com',
            'password': 'password123'
        }
        
        with pytest.raises(ValidationException):
            AuthService.create_user(user_data)
    
    @patch('app.services.auth_service.db')
    def test_reset_password(self, mock_db):
        """Test password reset."""
        from app.services.auth_service import AuthService
        
        mock_user = Mock()
        mock_user.set_password = Mock()
        
        AuthService.reset_password(mock_user, 'newpassword123')
        
        mock_user.set_password.assert_called_once_with('newpassword123')
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.db')
    @patch('app.services.auth_service.PasswordResetToken')
    def test_generate_reset_token(self, mock_token_model, mock_db):
        """Test generating password reset token."""
        from app.services.auth_service import AuthService
        
        mock_user = Mock()
        mock_user.id = 1
        
        mock_token = Mock()
        mock_token.token = 'reset-token-123'
        mock_token_model.return_value = mock_token
        
        token = AuthService.generate_reset_token(mock_user)
        
        assert token == 'reset-token-123'
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.auth_service.PasswordResetToken')
    def test_validate_reset_token(self, mock_token_model):
        """Test validating reset token."""
        from app.services.auth_service import AuthService
        
        mock_token = Mock()
        mock_token.user = Mock(id=1)
        mock_token.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_token.used = False
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_token
        mock_token_model.query = mock_query
        
        user = AuthService.validate_reset_token('valid-token')
        
        assert user == mock_token.user
    
    @patch('app.services.auth_service.Session')
    def test_create_session(self, mock_session_model):
        """Test creating user session."""
        from app.services.auth_service import AuthService
        
        mock_user = Mock()
        mock_user.id = 1
        
        with patch('app.services.auth_service.db') as mock_db:
            mock_session = Mock()
            mock_session.token = 'session-token'
            mock_session_model.return_value = mock_session
            
            session = AuthService.create_session(mock_user, '127.0.0.1', 'Chrome')
            
            assert session == mock_session
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()


# Test beneficiary_service.py
class TestBeneficiaryService:
    """Test cases for BeneficiaryService."""
    
    @patch('app.services.beneficiary_service.db')
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_get_beneficiaries(self, mock_beneficiary_model, mock_db):
        """Test getting beneficiaries list."""
        from app.services.beneficiary_service import BeneficiaryService
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.paginate.return_value = Mock(
            items=[Mock(id=1), Mock(id=2)],
            total=2,
            pages=1,
            page=1
        )
        mock_beneficiary_model.query = mock_query
        
        result = BeneficiaryService.get_beneficiaries(tenant_id=100, page=1)
        
        assert 'beneficiaries' in result
        assert result['total'] == 2
    
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_get_beneficiary_by_id(self, mock_beneficiary_model):
        """Test getting beneficiary by ID."""
        from app.services.beneficiary_service import BeneficiaryService
        
        mock_beneficiary = Mock(id=1, tenant_id=100)
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_beneficiary
        mock_beneficiary_model.query = mock_query
        
        result = BeneficiaryService.get_beneficiary_by_id(1, tenant_id=100)
        
        assert result == mock_beneficiary
    
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_get_beneficiary_by_id_not_found(self, mock_beneficiary_model):
        """Test getting non-existent beneficiary."""
        from app.services.beneficiary_service import BeneficiaryService
        from app.exceptions import NotFoundException
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_beneficiary_model.query = mock_query
        
        with pytest.raises(NotFoundException):
            BeneficiaryService.get_beneficiary_by_id(999, tenant_id=100)
    
    @patch('app.services.beneficiary_service.db')
    @patch('app.services.beneficiary_service.User')
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_create_beneficiary(self, mock_beneficiary_model, mock_user_model, mock_db):
        """Test creating beneficiary."""
        from app.services.beneficiary_service import BeneficiaryService
        
        # Mock user doesn't exist
        mock_user_query = Mock()
        mock_user_query.filter_by.return_value = mock_user_query
        mock_user_query.first.return_value = None
        mock_user_model.query = mock_user_query
        
        # Mock new instances
        mock_user = Mock(id=1)
        mock_user_model.return_value = mock_user
        
        mock_beneficiary = Mock(id=1)
        mock_beneficiary_model.return_value = mock_beneficiary
        
        user_data = {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123'
        }
        beneficiary_data = {
            'tenant_id': 100,
            'phone': '1234567890'
        }
        
        result = BeneficiaryService.create_beneficiary(user_data, beneficiary_data)
        
        assert result == mock_beneficiary
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()
    
    @patch('app.services.beneficiary_service.db')
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_update_beneficiary(self, mock_beneficiary_model, mock_db):
        """Test updating beneficiary."""
        from app.services.beneficiary_service import BeneficiaryService
        
        mock_beneficiary = Mock(id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_beneficiary
        mock_beneficiary_model.query = mock_query
        
        update_data = {
            'phone': '9876543210',
            'address': '123 New St'
        }
        
        result = BeneficiaryService.update_beneficiary(1, update_data, tenant_id=100)
        
        assert mock_beneficiary.phone == '9876543210'
        assert mock_beneficiary.address == '123 New St'
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.beneficiary_service.db')
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_delete_beneficiary(self, mock_beneficiary_model, mock_db):
        """Test deleting beneficiary."""
        from app.services.beneficiary_service import BeneficiaryService
        
        mock_beneficiary = Mock(id=1, user=Mock())
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_beneficiary
        mock_beneficiary_model.query = mock_query
        
        result = BeneficiaryService.delete_beneficiary(1, tenant_id=100)
        
        assert result is True
        mock_db.session.delete.assert_called()
        mock_db.session.commit.assert_called()
    
    @patch('app.services.beneficiary_service.Beneficiary')
    def test_search_beneficiaries(self, mock_beneficiary_model):
        """Test searching beneficiaries."""
        from app.services.beneficiary_service import BeneficiaryService
        
        mock_query = Mock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.all.return_value = [Mock(id=1), Mock(id=2)]
        mock_beneficiary_model.query = mock_query
        
        result = BeneficiaryService.search_beneficiaries('john', tenant_id=100)
        
        assert len(result) == 2
    
    @patch('app.services.beneficiary_service.db')
    @patch('app.services.beneficiary_service.Note')
    def test_add_note(self, mock_note_model, mock_db):
        """Test adding note to beneficiary."""
        from app.services.beneficiary_service import BeneficiaryService
        
        mock_note = Mock(id=1)
        mock_note_model.return_value = mock_note
        
        result = BeneficiaryService.add_note(
            beneficiary_id=1,
            user_id=1,
            content='Test note',
            note_type='general'
        )
        
        assert result == mock_note
        mock_db.session.add.assert_called_once_with(mock_note)
        mock_db.session.commit.assert_called_once()


# Test document_service.py
class TestDocumentService:
    """Test cases for DocumentService."""
    
    @patch('app.services.document_service.Document')
    def test_get_documents(self, mock_document_model):
        """Test getting documents."""
        from app.services.document_service import DocumentService
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.all.return_value = [Mock(id=1), Mock(id=2)]
        mock_document_model.query = mock_query
        
        result = DocumentService.get_documents(beneficiary_id=1)
        
        assert len(result) == 2
    
    @patch('app.services.document_service.Document')
    def test_get_document_by_id(self, mock_document_model):
        """Test getting document by ID."""
        from app.services.document_service import DocumentService
        
        mock_document = Mock(id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_document
        mock_document_model.query = mock_query
        
        result = DocumentService.get_document_by_id(1)
        
        assert result == mock_document
    
    @patch('app.services.document_service.db')
    @patch('app.services.document_service.Document')
    @patch('app.services.document_service.secure_filename')
    def test_upload_document(self, mock_secure_filename, mock_document_model, mock_db):
        """Test uploading document."""
        from app.services.document_service import DocumentService
        
        # Mock file
        mock_file = Mock(spec=FileStorage)
        mock_file.filename = 'test.pdf'
        mock_file.save = Mock()
        
        mock_secure_filename.return_value = 'test.pdf'
        
        # Mock document
        mock_document = Mock(id=1)
        mock_document_model.return_value = mock_document
        
        with patch('os.makedirs'):
            result = DocumentService.upload_document(
                file=mock_file,
                beneficiary_id=1,
                user_id=1,
                title='Test Document'
            )
            
            assert result == mock_document
            mock_file.save.assert_called_once()
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    @patch('app.services.document_service.db')
    @patch('app.services.document_service.Document')
    def test_delete_document(self, mock_document_model, mock_db):
        """Test deleting document."""
        from app.services.document_service import DocumentService
        
        mock_document = Mock(id=1, file_path='uploads/test.pdf')
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_document
        mock_document_model.query = mock_query
        
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                result = DocumentService.delete_document(1)
                
                assert result is True
                mock_remove.assert_called_once()
                mock_db.session.delete.assert_called_once_with(mock_document)
                mock_db.session.commit.assert_called_once()
    
    @patch('app.services.document_service.db')
    @patch('app.services.document_service.DocumentShare')
    def test_share_document(self, mock_share_model, mock_db):
        """Test sharing document."""
        from app.services.document_service import DocumentService
        
        mock_share = Mock()
        mock_share_model.return_value = mock_share
        
        result = DocumentService.share_document(
            document_id=1,
            shared_by=1,
            shared_with=2,
            permissions='read'
        )
        
        assert result == mock_share
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    def test_check_document_access(self):
        """Test checking document access."""
        from app.services.document_service import DocumentService
        
        # Mock document with owner
        mock_document = Mock()
        mock_document.user_id = 1
        mock_document.beneficiary_id = 10
        mock_document.is_public = False
        mock_document.shares = []
        
        # Owner has access
        assert DocumentService.check_document_access(mock_document, 1) is True
        
        # Non-owner no access
        assert DocumentService.check_document_access(mock_document, 2) is False
        
        # Public document - everyone has access
        mock_document.is_public = True
        assert DocumentService.check_document_access(mock_document, 3) is True


# Test appointment_service.py
class TestAppointmentService:
    """Test cases for AppointmentService."""
    
    @patch('app.services.appointment_service.Appointment')
    def test_get_appointments(self, mock_appointment_model):
        """Test getting appointments."""
        from app.services.appointment_service import AppointmentService
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [Mock(id=1), Mock(id=2)]
        mock_appointment_model.query = mock_query
        
        result = AppointmentService.get_appointments(
            user_id=1,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        
        assert len(result) == 2
    
    @patch('app.services.appointment_service.db')
    @patch('app.services.appointment_service.Appointment')
    def test_create_appointment(self, mock_appointment_model, mock_db):
        """Test creating appointment."""
        from app.services.appointment_service import AppointmentService
        
        mock_appointment = Mock(id=1)
        mock_appointment_model.return_value = mock_appointment
        
        # Mock conflict check
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # No conflict
        mock_appointment_model.query = mock_query
        
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': datetime.now() + timedelta(hours=1),
            'end_time': datetime.now() + timedelta(hours=2),
            'beneficiary_id': 10,
            'user_id': 1
        }
        
        result = AppointmentService.create_appointment(appointment_data)
        
        assert result == mock_appointment
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.appointment_service.Appointment')
    def test_create_appointment_conflict(self, mock_appointment_model):
        """Test creating appointment with conflict."""
        from app.services.appointment_service import AppointmentService
        from app.exceptions import ValidationException
        
        # Mock conflict exists
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = Mock()  # Conflict exists
        mock_appointment_model.query = mock_query
        
        appointment_data = {
            'title': 'Test Appointment',
            'start_time': datetime.now() + timedelta(hours=1),
            'end_time': datetime.now() + timedelta(hours=2),
            'beneficiary_id': 10,
            'user_id': 1
        }
        
        with pytest.raises(ValidationException):
            AppointmentService.create_appointment(appointment_data)
    
    @patch('app.services.appointment_service.db')
    @patch('app.services.appointment_service.Appointment')
    def test_update_appointment(self, mock_appointment_model, mock_db):
        """Test updating appointment."""
        from app.services.appointment_service import AppointmentService
        
        mock_appointment = Mock(id=1)
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_appointment
        mock_appointment_model.query = mock_query
        
        update_data = {
            'title': 'Updated Appointment',
            'status': 'confirmed'
        }
        
        result = AppointmentService.update_appointment(1, update_data)
        
        assert mock_appointment.title == 'Updated Appointment'
        assert mock_appointment.status == 'confirmed'
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.appointment_service.db')
    @patch('app.services.appointment_service.Appointment')
    def test_cancel_appointment(self, mock_appointment_model, mock_db):
        """Test canceling appointment."""
        from app.services.appointment_service import AppointmentService
        
        mock_appointment = Mock(id=1, status='scheduled')
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_appointment
        mock_appointment_model.query = mock_query
        
        result = AppointmentService.cancel_appointment(1)
        
        assert result is True
        assert mock_appointment.status == 'cancelled'
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.appointment_service.Appointment')
    def test_get_appointment_slots(self, mock_appointment_model):
        """Test getting available appointment slots."""
        from app.services.appointment_service import AppointmentService
        
        # Mock existing appointments
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []  # No appointments
        mock_appointment_model.query = mock_query
        
        slots = AppointmentService.get_available_slots(
            user_id=1,
            date=datetime.now().date(),
            duration=60
        )
        
        assert isinstance(slots, list)
        assert len(slots) > 0


# Test notification_service.py
class TestNotificationService:
    """Test cases for NotificationService."""
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_create_notification(self, mock_notification_model, mock_db):
        """Test creating notification."""
        from app.services.notification_service import NotificationService
        
        mock_notification = Mock(id=1)
        mock_notification_model.return_value = mock_notification
        
        result = NotificationService.create_notification(
            user_id=1,
            title='Test Notification',
            message='Test message',
            notification_type='info'
        )
        
        assert result == mock_notification
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.notification_service.Notification')
    def test_get_user_notifications(self, mock_notification_model):
        """Test getting user notifications."""
        from app.services.notification_service import NotificationService
        
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [Mock(id=1), Mock(id=2)]
        mock_notification_model.query = mock_query
        
        result = NotificationService.get_user_notifications(user_id=1, limit=10)
        
        assert len(result) == 2
    
    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_as_read(self, mock_notification_model, mock_db):
        """Test marking notification as read."""
        from app.services.notification_service import NotificationService
        
        mock_notification = Mock(id=1, is_read=False)
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_notification
        mock_notification_model.query = mock_query
        
        result = NotificationService.mark_as_read(1, user_id=1)
        
        assert result is True
        assert mock_notification.is_read is True
        assert mock_notification.read_at is not None
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.notification_service.socketio')
    def test_send_realtime_notification(self, mock_socketio):
        """Test sending realtime notification."""
        from app.services.notification_service import NotificationService
        
        NotificationService.send_realtime_notification(
            user_id=1,
            notification={'title': 'Test', 'message': 'Hello'}
        )
        
        mock_socketio.emit.assert_called_once()
    
    @patch('app.services.notification_service.db')
    def test_send_bulk_notifications(self, mock_db):
        """Test sending bulk notifications."""
        from app.services.notification_service import NotificationService
        
        user_ids = [1, 2, 3]
        
        with patch('app.services.notification_service.Notification') as mock_model:
            result = NotificationService.send_bulk_notifications(
                user_ids=user_ids,
                title='Bulk Notification',
                message='Test message'
            )
            
            assert result == len(user_ids)
            assert mock_db.session.add.call_count == len(user_ids)
            mock_db.session.commit.assert_called_once()