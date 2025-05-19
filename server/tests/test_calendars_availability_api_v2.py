"""Tests for calendar availability API endpoints."""

import pytest
from datetime import datetime, timedelta
from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException


class TestCalendarAvailabilityAPI:
    """Test calendar availability API endpoints."""
    
    def test_get_empty_availability(self, client, trainer_headers):
        """Test getting availability when none exists."""
        response = client.get('/api/calendars/availability', headers=trainer_headers)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        assert response.status_code == 200
        assert response.json['schedules'] == []
    
    def test_create_availability_schedule(self, client, trainer_headers):
        """Test creating a new availability schedule."""
        data = {
            'title': 'Regular Hours',
            'time_zone': 'America/New_York',
            'is_active': True,
            'slots': [
                {
                    'day_of_week': 1,  # Tuesday
                    'start_time': '09:00',
                    'end_time': '17:00',
                    'is_available': True
                },
                {
                    'day_of_week': 3,  # Thursday
                    'start_time': '13:00',
                    'end_time': '20:00',
                    'is_available': True
                }
            ]
        }
        
        response = client.post('/api/calendars/availability', json=data, headers=trainer_headers)
        assert response.status_code == 201
        assert response.json['title'] == 'Regular Hours'
        assert len(response.json['slots']) == 2
    
    def test_create_availability_without_auth(self, client):
        """Test creating availability without authentication."""
        data = {'title': 'Test Schedule'}
        response = client.post('/api/calendars/availability', json=data)
        assert response.status_code == 401
    
    def test_update_availability_schedule(self, client, trainer_headers, test_trainer, db_session):
        """Test updating an existing availability schedule."""
        # Create a schedule first
        schedule = AvailabilitySchedule(
            user_id=test_trainer.id,
            title='Old Title',
            time_zone='UTC',
            is_active=True
        )
        db_session.add(schedule)
        db_session.commit()
        schedule_id = schedule.id
        
        # Update the schedule
        update_data = {
            'title': 'New Title',
            'time_zone': 'America/Los_Angeles',
            'is_active': False
        }
        
        response = client.put(
            f'/api/calendars/availability/{schedule_id}',
            json=update_data,
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert response.json['title'] == 'New Title'
        assert response.json['time_zone'] == 'America/Los_Angeles'
        assert response.json['is_active'] is False
    
    def test_update_nonexistent_schedule(self, client, trainer_headers):
        """Test updating a schedule that doesn't exist."""
        response = client.put(
            '/api/calendars/availability/9999',
            json={'title': 'Test'},
            headers=trainer_headers
        )
        assert response.status_code == 404
    
    def test_delete_availability_schedule(self, client, trainer_headers, test_trainer, db_session):
        """Test deleting an availability schedule."""
        # Create a schedule first
        schedule = AvailabilitySchedule(
            user_id=test_trainer.id,
            title='To Delete',
            time_zone='UTC',
            is_active=True
        )
        db_session.add(schedule)
        db_session.commit()
        schedule_id = schedule.id
        
        # Delete the schedule
        response = client.delete(
            f'/api/calendars/availability/{schedule_id}',
            headers=trainer_headers
        )
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get('/api/calendars/availability', headers=trainer_headers)
        assert response.status_code == 200
        assert response.json['schedules'] == []
    
    def test_create_availability_exception(self, client, trainer_headers):
        """Test creating an availability exception."""
        exception_date = datetime.utcnow() + timedelta(days=7)
        
        data = {
            'date': exception_date.isoformat(),
            'is_available': False,
            'title': 'Day Off',
            'description': 'Personal day',
            'start_time': None,
            'end_time': None
        }
        
        response = client.post(
            '/api/calendars/availability/exceptions',
            json=data,
            headers=trainer_headers
        )
        assert response.status_code == 201
        assert response.json['title'] == 'Day Off'
        assert response.json['is_available'] is False
    
    def test_get_availability_exceptions(self, client, trainer_headers, test_trainer, db_session):
        """Test getting availability exceptions."""
        # Create an exception first
        exception = AvailabilityException(
            user_id=test_trainer.id,
            date=datetime.utcnow() + timedelta(days=10),
            is_available=False,
            title='Holiday',
            description='National holiday'
        )
        db_session.add(exception)
        db_session.commit()
        
        response = client.get('/api/calendars/availability/exceptions', headers=trainer_headers)
        assert response.status_code == 200
        assert len(response.json['exceptions']) == 1
        assert response.json['exceptions'][0]['title'] == 'Holiday'
    
    def test_invalid_time_format(self, client, trainer_headers):
        """Test creating availability with invalid time format."""
        data = {
            'title': 'Invalid Time',
            'slots': [
                {
                    'day_of_week': 1,
                    'start_time': '25:00',  # Invalid time
                    'end_time': '17:00'
                }
            ]
        }
        
        response = client.post('/api/calendars/availability', json=data, headers=trainer_headers)
        assert response.status_code == 400
    
    def test_overlapping_time_slots(self, client, trainer_headers):
        """Test creating schedule with overlapping time slots."""
        data = {
            'title': 'Overlapping Times',
            'slots': [
                {
                    'day_of_week': 1,
                    'start_time': '09:00',
                    'end_time': '13:00'
                },
                {
                    'day_of_week': 1,
                    'start_time': '12:00',  # Overlaps with previous
                    'end_time': '17:00'
                }
            ]
        }
        
        response = client.post('/api/calendars/availability', json=data, headers=trainer_headers)
        # API should handle overlapping gracefully or return error
        assert response.status_code in [201, 400]