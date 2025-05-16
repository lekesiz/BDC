"""Tests for Availability Service - Fixed version."""

import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, patch
from app import create_app, db
from app.services.availability_service import AvailabilityService
from app.models import AvailabilitySchedule, AvailabilitySlot, AvailabilityException
from config import TestingConfig


class TestAvailabilityServiceV2:
    """Test availability service functionality."""
    
    @pytest.fixture(scope='function')
    def app(self):
        """Create application for testing."""
        app = create_app(TestingConfig)
        with app.app_context():
            yield app
    
    @pytest.fixture
    def mock_db_session(self, app):
        """Mock database session."""
        with patch('app.services.availability_service.db.session') as mock_session:
            yield mock_session
    
    def test_get_or_create_default_schedule(self, app, mock_db_session):
        """Test getting or creating default availability schedule."""
        user_id = 1
        
        # Test when schedule doesn't exist
        with patch('app.models.AvailabilitySchedule.query') as mock_query, \
             patch('app.services.availability_service.AvailabilitySchedule') as MockSchedule:
            
            mock_query.filter_by.return_value.first.return_value = None
            mock_schedule = Mock()
            MockSchedule.return_value = mock_schedule
            
            result = AvailabilityService.get_or_create_default_schedule(user_id)
            
            MockSchedule.assert_called_once_with(
                user_id=user_id,
                is_active=True,
                timezone='UTC'
            )
            mock_db_session.add.assert_called_once_with(mock_schedule)
            assert result == mock_schedule
    
    def test_get_existing_schedule(self, app):
        """Test getting existing availability schedule."""
        user_id = 1
        mock_schedule = Mock()
        
        with patch('app.models.AvailabilitySchedule.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_schedule
            
            result = AvailabilityService.get_or_create_default_schedule(user_id)
            
            assert result == mock_schedule
    
    def test_create_availability_slot(self, app, mock_db_session):
        """Test creating an availability slot."""
        data = {
            'schedule_id': 1,
            'day_of_week': 1,  # Monday
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'is_recurring': True
        }
        
        with patch('app.services.availability_service.AvailabilitySlot') as MockSlot:
            mock_slot = Mock()
            MockSlot.return_value = mock_slot
            
            result = AvailabilityService.create_availability_slot(data)
            
            MockSlot.assert_called_once_with(**data)
            mock_db_session.add.assert_called_once_with(mock_slot)
            mock_db_session.commit.assert_called_once()
            assert result == mock_slot
    
    def test_update_availability_slot(self, app, mock_db_session):
        """Test updating an availability slot."""
        slot_id = 1
        data = {
            'start_time': time(10, 0),
            'end_time': time(18, 0)
        }
        
        mock_slot = Mock()
        mock_slot.start_time = time(9, 0)
        mock_slot.end_time = time(17, 0)
        
        with patch('app.models.AvailabilitySlot.query') as mock_query:
            mock_query.get.return_value = mock_slot
            
            result = AvailabilityService.update_availability_slot(slot_id, data)
            
            assert mock_slot.start_time == data['start_time']
            assert mock_slot.end_time == data['end_time']
            mock_db_session.commit.assert_called_once()
            assert result == mock_slot
    
    def test_delete_availability_slot(self, app, mock_db_session):
        """Test deleting an availability slot."""
        slot_id = 1
        mock_slot = Mock()
        
        with patch('app.models.AvailabilitySlot.query') as mock_query:
            mock_query.get.return_value = mock_slot
            
            result = AvailabilityService.delete_availability_slot(slot_id)
            
            mock_db_session.delete.assert_called_once_with(mock_slot)
            mock_db_session.commit.assert_called_once()
            assert result is True
    
    def test_add_availability_exception(self, app, mock_db_session):
        """Test adding an availability exception."""
        user_id = 1
        data = {
            'date': datetime.now().date(),
            'reason': 'Holiday',
            'is_available': False
        }
        
        with patch('app.services.availability_service.AvailabilityException') as MockException:
            mock_exception = Mock()
            MockException.return_value = mock_exception
            
            result = AvailabilityService.add_availability_exception(user_id, data)
            
            MockException.assert_called_once_with(
                user_id=user_id,
                **data
            )
            mock_db_session.add.assert_called_once_with(mock_exception)
            mock_db_session.commit.assert_called_once()
            assert result == mock_exception
    
    def test_get_available_slots(self, app):
        """Test getting available slots for a date range."""
        user_id = 1
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        # Mock schedule with slots
        mock_schedule = Mock()
        mock_slot1 = Mock()
        mock_slot1.day_of_week = start_date.weekday()
        mock_slot1.start_time = time(9, 0)
        mock_slot1.end_time = time(12, 0)
        mock_slot1.is_active = True
        
        mock_slot2 = Mock()
        mock_slot2.day_of_week = start_date.weekday()
        mock_slot2.start_time = time(14, 0)
        mock_slot2.end_time = time(17, 0)
        mock_slot2.is_active = True
        
        mock_schedule.slots = [mock_slot1, mock_slot2]
        
        # Mock exceptions
        mock_exception = Mock()
        mock_exception.date = start_date.date()
        mock_exception.is_available = False
        
        with patch.object(AvailabilityService, 'get_or_create_default_schedule') as mock_get_schedule, \
             patch('app.models.AvailabilityException.query') as mock_exception_query:
            
            mock_get_schedule.return_value = mock_schedule
            mock_exception_query.filter_by.return_value.filter.return_value.all.return_value = [mock_exception]
            
            slots = AvailabilityService.get_available_slots(user_id, start_date, end_date)
            
            # Should return slots for days without exceptions
            assert len(slots) > 0
            # First day should have no slots due to exception
            first_day_slots = [s for s in slots if s['date'].date() == start_date.date()]
            assert len(first_day_slots) == 0
    
    def test_check_slot_availability(self, app):
        """Test checking if a specific slot is available."""
        user_id = 1
        slot_datetime = datetime.now() + timedelta(days=1)
        duration = 60  # minutes
        
        # Mock schedule with matching slot
        mock_schedule = Mock()
        mock_slot = Mock()
        mock_slot.day_of_week = slot_datetime.weekday()
        mock_slot.start_time = time(9, 0)
        mock_slot.end_time = time(17, 0)
        mock_slot.is_active = True
        mock_schedule.slots = [mock_slot]
        
        with patch.object(AvailabilityService, 'get_or_create_default_schedule') as mock_get_schedule, \
             patch('app.models.AvailabilityException.query') as mock_exception_query, \
             patch('app.models.appointment.Appointment.query') as mock_appointment_query:
            
            mock_get_schedule.return_value = mock_schedule
            mock_exception_query.filter_by.return_value.filter.return_value.first.return_value = None
            mock_appointment_query.filter.return_value.filter.return_value.first.return_value = None
            
            is_available = AvailabilityService.check_slot_availability(
                user_id, slot_datetime, duration
            )
            
            assert is_available is True
    
    def test_check_slot_availability_with_conflict(self, app):
        """Test checking slot availability with appointment conflict."""
        user_id = 1
        slot_datetime = datetime.now() + timedelta(days=1)
        duration = 60  # minutes
        
        # Mock existing appointment
        mock_appointment = Mock()
        
        with patch('app.models.appointment.Appointment.query') as mock_query:
            mock_query.filter.return_value.filter.return_value.first.return_value = mock_appointment
            
            is_available = AvailabilityService.check_slot_availability(
                user_id, slot_datetime, duration
            )
            
            assert is_available is False
    
    def test_update_schedule_settings(self, app, mock_db_session):
        """Test updating availability schedule settings."""
        user_id = 1
        settings = {
            'timezone': 'America/New_York',
            'default_duration': 60,
            'buffer_time': 15
        }
        
        mock_schedule = Mock()
        
        with patch.object(AvailabilityService, 'get_or_create_default_schedule') as mock_get_schedule:
            mock_get_schedule.return_value = mock_schedule
            
            result = AvailabilityService.update_schedule_settings(user_id, settings)
            
            assert mock_schedule.timezone == settings['timezone']
            assert mock_schedule.default_duration == settings['default_duration']
            assert mock_schedule.buffer_time == settings['buffer_time']
            mock_db_session.commit.assert_called_once()
            assert result == mock_schedule
    
    def test_get_user_availability_summary(self, app):
        """Test getting user availability summary."""
        user_id = 1
        
        mock_schedule = Mock()
        mock_schedule.is_active = True
        mock_schedule.timezone = 'UTC'
        
        mock_slot1 = Mock()
        mock_slot1.to_dict.return_value = {'id': 1, 'day_of_week': 1}
        mock_slot2 = Mock()
        mock_slot2.to_dict.return_value = {'id': 2, 'day_of_week': 2}
        mock_schedule.slots = [mock_slot1, mock_slot2]
        
        with patch.object(AvailabilityService, 'get_or_create_default_schedule') as mock_get_schedule, \
             patch('app.models.AvailabilityException.query') as mock_exception_query:
            
            mock_get_schedule.return_value = mock_schedule
            mock_exception_query.filter_by.return_value.count.return_value = 3
            
            summary = AvailabilityService.get_user_availability_summary(user_id)
            
            assert summary['schedule_active'] is True
            assert summary['timezone'] == 'UTC'
            assert summary['total_slots'] == 2
            assert summary['total_exceptions'] == 3
            assert len(summary['slots']) == 2