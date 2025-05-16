"""Tests for availability service."""

import pytest
from datetime import datetime, timedelta
from app.models import User, AvailabilitySchedule, AvailabilitySlot, AvailabilityException
from app.services.availability_service import AvailabilityService
from app.extensions import db

@pytest.fixture
def availability_service():
    """Create availability service instance."""
    return AvailabilityService()

@pytest.fixture
def setup_availability_data(session, app):
    """Setup test data for availability service tests."""
    with app.app_context():
        # Create test users
        trainer = User(
            username='trainer',
            email='trainer@test.com',
            first_name='Test',
            last_name='Trainer',
            is_active=True,
            role='trainer',
            tenant_id=1
        )
        trainer.password = 'password123'
        session.add(trainer)
        session.commit()
        
        # Create schedule
        schedule = AvailabilitySchedule(
            user_id=trainer.id,
            title='Default Schedule',
            is_active=True,
            time_zone='UTC'
        )
        session.add(schedule)
        session.commit()
        
        # Create recurring availability slots
        monday_availability = AvailabilitySlot(
            schedule_id=schedule.id,
            day_of_week=0,  # Monday (0-based)
            start_time='09:00',
            end_time='17:00',
            is_available=True
        )
        
        wednesday_availability = AvailabilitySlot(
            schedule_id=schedule.id,
            day_of_week=2,  # Wednesday (0-based)
            start_time='10:00',
            end_time='16:00',
            is_available=True
        )
        
        # Create one-time availability exception
        specific_date = datetime.utcnow() + timedelta(days=7)
        one_time_exception = AvailabilityException(
            user_id=trainer.id,
            date=specific_date,
            start_time='14:00',
            end_time='18:00',
            is_available=True,
            title='Special session'
        )
        
        session.add_all([
            monday_availability, 
            wednesday_availability,
            one_time_exception
        ])
        session.commit()
        
        return {
            'trainer': trainer,
            'schedule': schedule,
            'monday_availability': monday_availability,
            'wednesday_availability': wednesday_availability,
            'one_time_exception': one_time_exception,
            'specific_date': specific_date
        }


def test_get_or_create_default_schedule(availability_service, setup_availability_data, app):
    """Test getting or creating default schedule."""
    with app.app_context():
        user_id = setup_availability_data['trainer'].id
        
        # Get existing schedule
        schedule = availability_service.get_or_create_default_schedule(user_id)
        
        assert schedule is not None
        assert schedule.user_id == user_id
        assert schedule.title == 'Default Schedule'
        assert schedule.is_active is True
        
        # Create default schedule for new user
        new_user = User(
            username='new_trainer',
            email='new_trainer@test.com',
            first_name='New',
            last_name='Trainer',
            is_active=True,
            role='trainer',
            tenant_id=1
        )
        new_user.password = 'password123'
        db.session.add(new_user)
        db.session.commit()
        
        new_schedule = availability_service.get_or_create_default_schedule(new_user.id)
        
        assert new_schedule is not None
        assert new_schedule.user_id == new_user.id
        assert new_schedule.title == 'Default Schedule'
        
        # Check if default slots were created (Mon-Fri, 9-5)
        slots = AvailabilitySlot.query.filter_by(schedule_id=new_schedule.id).all()
        assert len(slots) == 5  # 5 weekdays
        for slot in slots:
            assert slot.start_time == '09:00'
            assert slot.end_time == '17:00'
            assert slot.is_available is True
            assert slot.day_of_week in [0, 1, 2, 3, 4]  # Monday-Friday


def test_get_user_availability(availability_service, setup_availability_data, app):
    """Test getting user availability."""
    with app.app_context():
        user_id = setup_availability_data['trainer'].id
        
        # Get availability for next 7 days
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=7)
        
        availability = availability_service.get_user_availability(user_id, start_date, end_date)
        
        assert availability is not None
        assert availability['user_id'] == user_id
        assert availability['schedule_title'] == 'Default Schedule'
        assert len(availability['days']) == 8  # 8 days including both start and end dates
        
        # Check if Monday and Wednesday have available slots
        for day in availability['days']:
            if day['day_of_week'] == 0:  # Monday
                assert len(day['available_slots']) > 0
                assert any(slot['start_time'] == '09:00' for slot in day['available_slots'])
            elif day['day_of_week'] == 2:  # Wednesday
                assert len(day['available_slots']) > 0
                assert any(slot['start_time'] == '10:00' for slot in day['available_slots'])


def test_update_availability_schedule(availability_service, setup_availability_data, app):
    """Test updating availability schedule."""
    with app.app_context():
        schedule_id = setup_availability_data['schedule'].id
        
        updated_data = {
            'title': 'Updated Schedule',
            'time_zone': 'US/Eastern',
            'slots': [
                {
                    'day_of_week': 1,  # Tuesday
                    'start_time': '08:00',
                    'end_time': '16:00',
                    'is_available': True
                },
                {
                    'day_of_week': 4,  # Friday
                    'start_time': '09:00',
                    'end_time': '13:00',
                    'is_available': True
                }
            ]
        }
        
        updated_schedule = availability_service.update_availability_schedule(schedule_id, updated_data)
        
        assert updated_schedule is not None
        assert updated_schedule.title == 'Updated Schedule'
        assert updated_schedule.time_zone == 'US/Eastern'
        
        # Check if slots were updated
        slots = AvailabilitySlot.query.filter_by(schedule_id=schedule_id).all()
        assert len(slots) == 2
        days = [slot.day_of_week for slot in slots]
        assert 1 in days  # Tuesday
        assert 4 in days  # Friday


def test_add_availability_exception(availability_service, setup_availability_data, app):
    """Test adding availability exception."""
    with app.app_context():
        user_id = setup_availability_data['trainer'].id
        exception_date = datetime.utcnow() + timedelta(days=14)
        
        exception_data = {
            'date': exception_date.strftime('%Y-%m-%d'),
            'is_available': False,
            'title': 'Vacation day',
            'description': 'Out of office'
        }
        
        exception = availability_service.add_availability_exception(user_id, exception_data)
        
        assert exception is not None
        assert exception.user_id == user_id
        assert exception.date.date() == exception_date.date()
        assert exception.is_available is False
        assert exception.title == 'Vacation day'
        assert exception.description == 'Out of office'


def test_delete_availability_exception(availability_service, setup_availability_data, app):
    """Test deleting availability exception."""
    with app.app_context():
        exception_id = setup_availability_data['one_time_exception'].id
        user_id = setup_availability_data['trainer'].id
        
        result = availability_service.delete_availability_exception(exception_id, user_id)
        
        assert result is True
        
        # Verify it's deleted
        deleted = AvailabilityException.query.get(exception_id)
        assert deleted is None


def test_get_available_slots(availability_service, setup_availability_data, app):
    """Test getting available time slots."""
    with app.app_context():
        user_id = setup_availability_data['trainer'].id
        
        # Get next Monday
        today = datetime.utcnow()
        days_ahead = (0 - today.weekday() + 7) % 7  # Monday is 0
        if days_ahead == 0:
            days_ahead = 7
        next_monday = today + timedelta(days=days_ahead)
        
        slots = availability_service.get_available_slots(
            user_id=user_id,
            date=next_monday,
            duration_minutes=60
        )
        
        assert len(slots) > 0
        # Should have slots between 09:00 and 17:00
        for slot in slots:
            start_time = datetime.strptime(slot['start_time'], '%H:%M').time()
            assert start_time >= datetime.strptime('09:00', '%H:%M').time()
            assert start_time < datetime.strptime('16:00', '%H:%M').time()
            assert slot['duration_minutes'] == 60


def test_availability_with_exceptions(availability_service, setup_availability_data, app):
    """Test availability with exceptions applied."""
    with app.app_context():
        user_id = setup_availability_data['trainer'].id
        specific_date = setup_availability_data['specific_date']
        
        # Get availability for the date with the exception
        start_date = specific_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = specific_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        availability = availability_service.get_user_availability(user_id, start_date, end_date)
        
        assert availability is not None
        assert len(availability['days']) == 1
        
        day = availability['days'][0]
        # Should have the exception slot available
        exception_slots = [s for s in day['available_slots'] if s['type'] == 'exception']
        assert len(exception_slots) > 0
        assert any(slot['start_time'] == '14:00' for slot in exception_slots)


def test_availability_slots_consistency(availability_service, app):
    """Test that availability slots maintain consistency."""
    with app.app_context():
        # Create a new trainer
        trainer = User(
            username='test_consistency',
            email='consistency@test.com',
            first_name='Test',
            last_name='Consistency',
            is_active=True,
            role='trainer',
            tenant_id=1
        )
        trainer.password = 'password123'
        db.session.add(trainer)
        db.session.commit()
        
        # Create default schedule
        schedule = availability_service.get_or_create_default_schedule(trainer.id)
        
        # Update with non-overlapping slots
        update_data = {
            'slots': [
                {
                    'day_of_week': 0,  # Monday
                    'start_time': '09:00',
                    'end_time': '12:00',
                    'is_available': True
                },
                {
                    'day_of_week': 0,  # Monday
                    'start_time': '13:00',
                    'end_time': '17:00',
                    'is_available': True
                }
            ]
        }
        
        updated = availability_service.update_availability_schedule(schedule.id, update_data)
        assert updated is not None
        
        # Get available slots
        next_monday = datetime.utcnow() + timedelta(days=(7 - datetime.utcnow().weekday()) % 7)
        slots = availability_service.get_available_slots(trainer.id, next_monday, 60)
        
        # Should have slots in both morning and afternoon
        morning_slots = [s for s in slots if s['start_time'] < '12:00']
        afternoon_slots = [s for s in slots if s['start_time'] >= '13:00']
        
        assert len(morning_slots) > 0
        assert len(afternoon_slots) > 0