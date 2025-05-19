"""Tests for calendar availability API endpoints."""

import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.config import TestConfig
from app.models.user import User
from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create authentication headers for a test user."""
    with app.app_context():
        # Create a test user
        user = User(
            email='trainer@test.com',
            username='trainer',
            password='password123',
            first_name='Trainer',
            last_name='User',
            role='trainer',
            tenant_id=1
        )
        db.session.add(user)
        db.session.commit()
        
        # Create an access token
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}


class TestCalendarAvailabilityAPI:
    """Test calendar availability API endpoints."""
    
    def test_get_empty_availability(self, client, auth_headers):
        """Test getting availability when none exists."""
        response = client.get('/api/calendars/availability', headers=auth_headers)
        assert response.status_code == 200
        assert response.json['schedules'] == []
    
    def test_create_availability_schedule(self, client, auth_headers):
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
        
        response = client.post('/api/calendars/availability', json=data, headers=auth_headers)
        assert response.status_code == 201
        assert response.json['title'] == 'Regular Hours'
        assert len(response.json['slots']) == 2
    
    def test_create_availability_without_auth(self, client):
        """Test creating availability without authentication."""
        data = {'title': 'Test Schedule'}
        response = client.post('/api/calendars/availability', json=data)
        assert response.status_code == 401
    
    def test_update_availability_schedule(self, client, auth_headers, app):
        """Test updating an existing availability schedule."""
        with app.app_context():
            # Create a schedule first
            user_id = User.query.filter_by(email='trainer@test.com').first().id
            schedule = AvailabilitySchedule(
                user_id=user_id,
                title='Old Title',
                time_zone='UTC',
                is_active=True
            )
            db.session.add(schedule)
            db.session.commit()
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
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json['title'] == 'New Title'
        assert response.json['time_zone'] == 'America/Los_Angeles'
        assert response.json['is_active'] is False
    
    def test_update_nonexistent_schedule(self, client, auth_headers):
        """Test updating a schedule that doesn't exist."""
        response = client.put(
            '/api/calendars/availability/9999',
            json={'title': 'Test'},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_availability_schedule(self, client, auth_headers, app):
        """Test deleting an availability schedule."""
        with app.app_context():
            # Create a schedule first
            user_id = User.query.filter_by(email='trainer@test.com').first().id
            schedule = AvailabilitySchedule(
                user_id=user_id,
                title='To Delete',
                time_zone='UTC',
                is_active=True
            )
            db.session.add(schedule)
            db.session.commit()
            schedule_id = schedule.id
        
        # Delete the schedule
        response = client.delete(
            f'/api/calendars/availability/{schedule_id}',
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get('/api/calendars/availability', headers=auth_headers)
        assert response.status_code == 200
        assert response.json['schedules'] == []
    
    def test_create_availability_exception(self, client, auth_headers):
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
            headers=auth_headers
        )
        assert response.status_code == 201
        assert response.json['title'] == 'Day Off'
        assert response.json['is_available'] is False
    
    def test_get_availability_exceptions(self, client, auth_headers, app):
        """Test getting availability exceptions."""
        with app.app_context():
            # Create an exception first
            user_id = User.query.filter_by(email='trainer@test.com').first().id
            exception = AvailabilityException(
                user_id=user_id,
                date=datetime.utcnow() + timedelta(days=10),
                is_available=False,
                title='Holiday',
                description='National holiday'
            )
            db.session.add(exception)
            db.session.commit()
        
        response = client.get('/api/calendars/availability/exceptions', headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json['exceptions']) == 1
        assert response.json['exceptions'][0]['title'] == 'Holiday'
    
    def test_invalid_time_format(self, client, auth_headers):
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
        
        response = client.post('/api/calendars/availability', json=data, headers=auth_headers)
        assert response.status_code == 400
    
    def test_overlapping_time_slots(self, client, auth_headers):
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
        
        response = client.post('/api/calendars/availability', json=data, headers=auth_headers)
        # API should handle overlapping gracefully or return error
        assert response.status_code in [201, 400]