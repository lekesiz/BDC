"""Tests for appointment repository."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository


class TestAppointmentRepository:
    """Test suite for appointment repository."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def appointment_repository(self, mock_session):
        """Create appointment repository instance."""
        return AppointmentRepository(mock_session)
    
    @pytest.fixture
    def sample_appointment_data(self):
        """Create sample appointment data."""
        return {
            'trainer_id': 1,
            'beneficiary_id': 2,
            'title': 'Test Appointment',
            'description': 'Test description',
            'start_time': datetime.utcnow() + timedelta(hours=1),
            'end_time': datetime.utcnow() + timedelta(hours=2),
            'status': 'scheduled',
            'location': 'Room 101'
        }
    
    def test_find_by_id_success(self, appointment_repository, mock_session):
        """Test successful appointment retrieval by ID."""
        mock_appointment = Mock(spec=Appointment)
        mock_appointment.id = 1
        mock_session.get.return_value = mock_appointment
        
        result = appointment_repository.find_by_id(1)
        
        mock_session.get.assert_called_once_with(Appointment, 1)
        assert result == mock_appointment
    
    def test_find_by_id_not_found(self, appointment_repository, mock_session):
        """Test appointment not found by ID."""
        mock_session.get.return_value = None
        
        result = appointment_repository.find_by_id(999)
        
        mock_session.get.assert_called_once_with(Appointment, 999)
        assert result is None
    
    @patch('app.repositories.appointment_repository.Appointment')
    def test_find_all_with_filters(self, mock_appointment_class, appointment_repository, mock_session):
        """Test find all appointments with filters."""
        # Create mock query
        mock_query = Mock()
        mock_appointment_class.query = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = Mock(
            items=[Mock(spec=Appointment)],
            total=1,
            pages=1
        )
        
        filters = {
            'user_id': 1,
            'role': 'trainer',
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + timedelta(days=7),
            'status': 'scheduled'
        }
        
        result = appointment_repository.find_all(
            filters=filters,
            pagination={'page': 1, 'per_page': 10}
        )
        
        assert result['total'] == 1
        assert result['pages'] == 1
        assert len(result['items']) == 1
    
    @patch('app.repositories.appointment_repository.Appointment')
    def test_find_all_student_role(self, mock_appointment_class, appointment_repository, mock_session):
        """Test find all appointments for student role."""
        # Create mock query
        mock_query = Mock()
        mock_appointment_class.query = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Appointment)]
        
        filters = {
            'user_id': 1,
            'role': 'student'
        }
        
        result = appointment_repository.find_all(filters=filters)
        
        mock_query.join.assert_called_once()
        assert len(result) == 1
    
    def test_create_success(self, appointment_repository, mock_session, sample_appointment_data):
        """Test successful appointment creation."""
        mock_appointment = Mock(spec=Appointment)
        
        with patch('app.repositories.appointment_repository.Appointment') as mock_appointment_class:
            mock_appointment_class.return_value = mock_appointment
            
            result = appointment_repository.create(sample_appointment_data)
            
            mock_appointment_class.assert_called_once_with(**sample_appointment_data)
            mock_session.add.assert_called_once_with(mock_appointment)
            mock_session.commit.assert_called_once()
            assert result == mock_appointment
    
    def test_update_success(self, appointment_repository, mock_session):
        """Test successful appointment update."""
        mock_appointment = Mock(spec=Appointment)
        appointment_repository.find_by_id = Mock(return_value=mock_appointment)
        
        update_data = {
            'title': 'Updated Title',
            'status': 'completed'
        }
        
        result = appointment_repository.update(1, update_data)
        
        appointment_repository.find_by_id.assert_called_once_with(1)
        assert mock_appointment.title == 'Updated Title'
        assert mock_appointment.status == 'completed'
        mock_session.commit.assert_called_once()
        assert result == mock_appointment
    
    def test_update_not_found(self, appointment_repository, mock_session):
        """Test update non-existent appointment."""
        appointment_repository.find_by_id = Mock(return_value=None)
        
        result = appointment_repository.update(999, {'title': 'Updated'})
        
        appointment_repository.find_by_id.assert_called_once_with(999)
        mock_session.commit.assert_not_called()
        assert result is None
    
    def test_delete_success(self, appointment_repository, mock_session):
        """Test successful appointment deletion."""
        mock_appointment = Mock(spec=Appointment)
        appointment_repository.find_by_id = Mock(return_value=mock_appointment)
        
        result = appointment_repository.delete(1)
        
        appointment_repository.find_by_id.assert_called_once_with(1)
        mock_session.delete.assert_called_once_with(mock_appointment)
        mock_session.commit.assert_called_once()
        assert result is True
    
    def test_delete_not_found(self, appointment_repository, mock_session):
        """Test delete non-existent appointment."""
        appointment_repository.find_by_id = Mock(return_value=None)
        
        result = appointment_repository.delete(999)
        
        appointment_repository.find_by_id.assert_called_once_with(999)
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()
        assert result is False
    
    @patch('app.repositories.appointment_repository.Appointment')
    def test_find_by_beneficiary(self, mock_appointment_class, appointment_repository, mock_session):
        """Test find appointments by beneficiary."""
        # Create mock query
        mock_query = Mock()
        mock_appointment_class.query = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = Mock(
            items=[Mock(spec=Appointment)],
            total=1,
            pages=1
        )
        
        result = appointment_repository.find_by_beneficiary(
            beneficiary_id=1,
            pagination={'page': 1, 'per_page': 10}
        )
        
        mock_query.filter_by.assert_called_once_with(beneficiary_id=1)
        assert result['total'] == 1
        assert result['pages'] == 1
        assert len(result['items']) == 1
    
    @patch('app.repositories.appointment_repository.Appointment')
    def test_find_by_trainer(self, mock_appointment_class, appointment_repository, mock_session):
        """Test find appointments by trainer."""
        # Create mock query
        mock_query = Mock()
        mock_appointment_class.query = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [Mock(spec=Appointment)]
        
        result = appointment_repository.find_by_trainer(trainer_id=1)
        
        mock_query.filter_by.assert_called_once_with(trainer_id=1)
        assert len(result) == 1