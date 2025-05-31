"""Unit tests for the refactored Calendar Service."""

import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.models.integration import UserIntegration
from app.services.calendar_service_refactored import (
    CalendarServiceRefactored,
    CalendarEvent,
    GoogleCalendarAPI,
    CalendarAPIProtocol
)
from app.exceptions import (
    NotFoundException,
    ValidationException,
    ExternalServiceException
)


# Test fixtures

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = Mock(spec=Session)
    session.query.return_value.filter_by.return_value.first.return_value = None
    return session


@pytest.fixture
def mock_calendar_api():
    """Create a mock calendar API."""
    api = Mock(spec=CalendarAPIProtocol)
    api.build_service.return_value = Mock()
    return api


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock()


@pytest.fixture
def calendar_service(mock_db_session, mock_calendar_api, mock_logger, tmp_path):
    """Create a CalendarService instance with mocked dependencies."""
    # Create a temporary client secrets file
    client_secrets_path = tmp_path / "client_secret.json"
    client_secrets_path.write_text(json.dumps({
        "web": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }))
    
    return CalendarServiceRefactored(
        db_session=mock_db_session,
        client_secrets_path=str(client_secrets_path),
        redirect_uri="http://localhost/callback",
        calendar_api=mock_calendar_api,
        logger=mock_logger
    )


@pytest.fixture
def sample_event():
    """Create a sample calendar event."""
    return CalendarEvent(
        title="Test Meeting",
        description="Test meeting description",
        start_time=datetime.utcnow() + timedelta(hours=1),
        end_time=datetime.utcnow() + timedelta(hours=2),
        location="Conference Room A",
        attendees=["user@example.com", "another@example.com"]
    )


@pytest.fixture
def mock_integration():
    """Create a mock user integration."""
    integration = Mock()
    integration.id = 1
    integration.user_id = 123
    integration.provider = 'google_calendar'
    integration.status = 'active'
    integration.data = json.dumps({
        'token': 'test_token',
        'refresh_token': 'test_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'scopes': ['https://www.googleapis.com/auth/calendar']
    })
    return integration


# Test CalendarEvent dataclass

def test_calendar_event_initialization():
    """Test CalendarEvent initialization."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=1)
    
    event = CalendarEvent(
        title="Test Event",
        description="Description",
        start_time=start_time,
        end_time=end_time,
        location="Location",
        attendees=["test@example.com"]
    )
    
    assert event.title == "Test Event"
    assert event.description == "Description"
    assert event.start_time == start_time
    assert event.end_time == end_time
    assert event.location == "Location"
    assert event.attendees == ["test@example.com"]


def test_calendar_event_default_attendees():
    """Test CalendarEvent with default empty attendees list."""
    event = CalendarEvent(
        title="Test Event",
        description=None,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=1)
    )
    
    assert event.attendees == []


# Test GoogleCalendarAPI

def test_google_calendar_api_build_service():
    """Test GoogleCalendarAPI.build_service method."""
    api = GoogleCalendarAPI()
    mock_credentials = Mock(spec=Credentials)
    
    with patch('app.services.calendar_service_refactored.build') as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        result = api.build_service(mock_credentials)
        
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_credentials)
        assert result == mock_service


# Test CalendarServiceRefactored initialization

def test_calendar_service_initialization(mock_db_session, tmp_path):
    """Test CalendarService initialization."""
    client_secrets_path = tmp_path / "client_secret.json"
    client_secrets_path.write_text("{}")
    
    service = CalendarServiceRefactored(
        db_session=mock_db_session,
        client_secrets_path=str(client_secrets_path),
        redirect_uri="http://localhost/callback"
    )
    
    assert service.db == mock_db_session
    assert service.client_secrets_path == str(client_secrets_path)
    assert service.redirect_uri == "http://localhost/callback"
    assert isinstance(service.calendar_api, GoogleCalendarAPI)
    assert service.logger is not None


# Test get_authorization_url

@patch('app.services.calendar_service_refactored.Flow')
def test_get_authorization_url_success(mock_flow_class, calendar_service, mock_db_session):
    """Test successful authorization URL generation."""
    # Setup mocks
    mock_flow = Mock()
    mock_flow.authorization_url.return_value = ("https://auth.url", "test_state")
    mock_flow_class.from_client_secrets_file.return_value = mock_flow
    
    # Mock existing integration
    mock_integration = Mock()
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    # Call method
    result = calendar_service.get_authorization_url(user_id=123)
    
    # Assertions
    assert result == {'url': 'https://auth.url'}
    assert mock_integration.status == 'pending'
    assert json.loads(mock_integration.data) == {'state': 'test_state'}
    mock_db_session.commit.assert_called_once()


def test_get_authorization_url_missing_client_secrets(calendar_service):
    """Test authorization URL generation with missing client secrets."""
    calendar_service.client_secrets_path = "/non/existent/path"
    
    with pytest.raises(ValidationException) as exc_info:
        calendar_service.get_authorization_url(user_id=123)
    
    assert "Client secrets file not found" in str(exc_info.value)


@patch('app.services.calendar_service_refactored.Flow')
def test_get_authorization_url_exception(mock_flow_class, calendar_service):
    """Test authorization URL generation with unexpected exception."""
    mock_flow_class.from_client_secrets_file.side_effect = Exception("Unexpected error")
    
    with pytest.raises(ExternalServiceException) as exc_info:
        calendar_service.get_authorization_url(user_id=123)
    
    assert "Failed to generate authorization URL" in str(exc_info.value)


# Test handle_oauth_callback

@patch('app.services.calendar_service_refactored.Flow')
def test_handle_oauth_callback_success(mock_flow_class, calendar_service, mock_db_session, mock_integration):
    """Test successful OAuth callback handling."""
    # Setup mocks
    mock_integration.data = json.dumps({'state': 'test_state'})
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_flow = Mock()
    mock_credentials = Mock(spec=Credentials)
    mock_credentials.token = 'new_token'
    mock_credentials.refresh_token = 'new_refresh_token'
    mock_credentials.token_uri = 'https://oauth2.googleapis.com/token'
    mock_credentials.client_id = 'client_id'
    mock_credentials.client_secret = 'client_secret'
    mock_credentials.scopes = ['scope1']
    mock_credentials.expiry = datetime.utcnow() + timedelta(hours=1)
    mock_flow.credentials = mock_credentials
    
    mock_flow_class.from_client_secrets_file.return_value = mock_flow
    
    # Call method
    result = calendar_service.handle_oauth_callback(
        user_id=123,
        code='auth_code',
        state='test_state'
    )
    
    # Assertions
    assert result['success'] is True
    assert result['message'] == 'Google Calendar connected successfully'
    assert mock_integration.status == 'active'
    mock_flow.fetch_token.assert_called_once_with(code='auth_code')
    mock_db_session.commit.assert_called_once()


def test_handle_oauth_callback_no_integration(calendar_service, mock_db_session):
    """Test OAuth callback with no integration found."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    with pytest.raises(NotFoundException) as exc_info:
        calendar_service.handle_oauth_callback(
            user_id=123,
            code='auth_code',
            state='test_state'
        )
    
    assert "No integration found for user 123" in str(exc_info.value)


def test_handle_oauth_callback_state_mismatch(calendar_service, mock_db_session, mock_integration):
    """Test OAuth callback with state mismatch."""
    mock_integration.data = json.dumps({'state': 'different_state'})
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    with pytest.raises(ValidationException) as exc_info:
        calendar_service.handle_oauth_callback(
            user_id=123,
            code='auth_code',
            state='test_state'
        )
    
    assert "Invalid state token" in str(exc_info.value)


# Test create_event

def test_create_event_success(calendar_service, mock_db_session, mock_integration, mock_calendar_api, sample_event):
    """Test successful event creation."""
    # Setup mocks
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    mock_events.insert.return_value.execute.return_value = {'id': 'event123'}
    mock_calendar_api.build_service.return_value = mock_service
    
    # Call method
    result = calendar_service.create_event(user_id=123, event=sample_event)
    
    # Assertions
    assert result == {'event_id': 'event123'}
    mock_events.insert.assert_called_once()
    call_args = mock_events.insert.call_args
    assert call_args[1]['calendarId'] == 'primary'
    assert call_args[1]['body']['summary'] == 'Test Meeting'


def test_create_event_no_integration(calendar_service, mock_db_session, sample_event):
    """Test event creation with no integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    with pytest.raises(NotFoundException) as exc_info:
        calendar_service.create_event(user_id=123, event=sample_event)
    
    assert "Google Calendar not connected" in str(exc_info.value)


def test_create_event_invalid_data(calendar_service, mock_db_session, mock_integration):
    """Test event creation with invalid data."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    # Event with empty title
    invalid_event = CalendarEvent(
        title="",
        description="Test",
        start_time=datetime.utcnow() + timedelta(hours=1),
        end_time=datetime.utcnow() + timedelta(hours=2)
    )
    
    with pytest.raises(ValidationException) as exc_info:
        calendar_service.create_event(user_id=123, event=invalid_event)
    
    assert "Event title is required" in str(exc_info.value)


def test_create_event_past_event(calendar_service, mock_db_session, mock_integration):
    """Test event creation with past dates."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    past_event = CalendarEvent(
        title="Past Event",
        description="Test",
        start_time=datetime.utcnow() - timedelta(hours=2),
        end_time=datetime.utcnow() - timedelta(hours=1)
    )
    
    with pytest.raises(ValidationException) as exc_info:
        calendar_service.create_event(user_id=123, event=past_event)
    
    assert "Cannot create events in the past" in str(exc_info.value)


def test_create_event_invalid_time_range(calendar_service, mock_db_session, mock_integration):
    """Test event creation with invalid time range."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    invalid_event = CalendarEvent(
        title="Invalid Event",
        description="Test",
        start_time=datetime.utcnow() + timedelta(hours=2),
        end_time=datetime.utcnow() + timedelta(hours=1)
    )
    
    with pytest.raises(ValidationException) as exc_info:
        calendar_service.create_event(user_id=123, event=invalid_event)
    
    assert "Start time must be before end time" in str(exc_info.value)


def test_create_event_api_error(calendar_service, mock_db_session, mock_integration, mock_calendar_api, sample_event):
    """Test event creation with API error."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    
    # Create HttpError
    resp = Mock()
    resp.status = 400
    error = HttpError(resp=resp, content=b'Bad Request')
    error._get_reason = Mock(return_value='Invalid request')
    
    mock_events.insert.return_value.execute.side_effect = error
    mock_calendar_api.build_service.return_value = mock_service
    
    with pytest.raises(ExternalServiceException) as exc_info:
        calendar_service.create_event(user_id=123, event=sample_event)
    
    assert "Failed to create calendar event" in str(exc_info.value)


# Test update_event

def test_update_event_success(calendar_service, mock_db_session, mock_integration, mock_calendar_api, sample_event):
    """Test successful event update."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    
    # Mock get existing event
    existing_event = {
        'id': 'event123',
        'etag': 'etag123',
        'summary': 'Old Meeting'
    }
    mock_events.get.return_value.execute.return_value = existing_event
    mock_events.update.return_value.execute.return_value = {'id': 'event123'}
    
    mock_calendar_api.build_service.return_value = mock_service
    
    # Call method
    result = calendar_service.update_event(user_id=123, event_id='event123', event=sample_event)
    
    # Assertions
    assert result == {'message': 'Event updated successfully'}
    mock_events.get.assert_called_once_with(calendarId='primary', eventId='event123')
    mock_events.update.assert_called_once()


def test_update_event_not_found(calendar_service, mock_db_session, mock_integration, mock_calendar_api, sample_event):
    """Test event update when event not found."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    
    # Mock event not found
    resp = Mock()
    resp.status = 404
    error = HttpError(resp=resp, content=b'Not Found')
    mock_events.get.return_value.execute.side_effect = error
    
    mock_calendar_api.build_service.return_value = mock_service
    
    with pytest.raises(NotFoundException) as exc_info:
        calendar_service.update_event(user_id=123, event_id='event123', event=sample_event)
    
    assert "Calendar event event123 not found" in str(exc_info.value)


# Test delete_event

def test_delete_event_success(calendar_service, mock_db_session, mock_integration, mock_calendar_api):
    """Test successful event deletion."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    mock_events.delete.return_value.execute.return_value = {}
    
    mock_calendar_api.build_service.return_value = mock_service
    
    # Call method
    result = calendar_service.delete_event(user_id=123, event_id='event123')
    
    # Assertions
    assert result == {'message': 'Event deleted successfully'}
    mock_events.delete.assert_called_once_with(calendarId='primary', eventId='event123')


def test_delete_event_already_deleted(calendar_service, mock_db_session, mock_integration, mock_calendar_api):
    """Test event deletion when event already deleted."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    
    # Mock 404 error
    resp = Mock()
    resp.status = 404
    error = HttpError(resp=resp, content=b'Not Found')
    mock_events.delete.return_value.execute.side_effect = error
    
    mock_calendar_api.build_service.return_value = mock_service
    
    # Call method
    result = calendar_service.delete_event(user_id=123, event_id='event123')
    
    # Assertions
    assert result == {'message': 'Event already deleted'}


# Test get_events

def test_get_events_success(calendar_service, mock_db_session, mock_integration, mock_calendar_api):
    """Test successful event retrieval."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    mock_service = Mock()
    mock_events = Mock()
    mock_service.events.return_value = mock_events
    
    # Mock events response
    google_events = {
        'items': [
            {
                'id': 'event1',
                'summary': 'Meeting 1',
                'description': 'Description 1',
                'location': 'Room 1',
                'start': {'dateTime': '2024-01-01T10:00:00Z'},
                'end': {'dateTime': '2024-01-01T11:00:00Z'},
                'attendees': [{'email': 'user1@example.com'}],
                'status': 'confirmed',
                'htmlLink': 'https://calendar.google.com/event1'
            },
            {
                'id': 'event2',
                'summary': 'Meeting 2',
                'start': {'date': '2024-01-02'},
                'end': {'date': '2024-01-03'},
                'status': 'confirmed'
            }
        ]
    }
    mock_events.list.return_value.execute.return_value = google_events
    
    mock_calendar_api.build_service.return_value = mock_service
    
    # Call method
    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 1, 31)
    result = calendar_service.get_events(
        user_id=123,
        start_time=start_time,
        end_time=end_time,
        max_results=20
    )
    
    # Assertions
    assert 'events' in result
    assert len(result['events']) == 2
    assert result['events'][0]['id'] == 'event1'
    assert result['events'][0]['title'] == 'Meeting 1'
    assert result['events'][0]['attendees'] == ['user1@example.com']
    
    # Check list parameters
    list_call = mock_events.list.call_args[1]
    assert list_call['calendarId'] == 'primary'
    assert list_call['maxResults'] == 20
    assert list_call['timeMin'] == '2024-01-01T00:00:00Z'
    assert list_call['timeMax'] == '2024-01-31T00:00:00Z'


def test_get_events_no_integration(calendar_service, mock_db_session):
    """Test event retrieval with no integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    with pytest.raises(NotFoundException) as exc_info:
        calendar_service.get_events(user_id=123)
    
    assert "Google Calendar not connected" in str(exc_info.value)


# Test is_connected

def test_is_connected_true(calendar_service, mock_db_session, mock_integration):
    """Test is_connected returns True when connected."""
    mock_integration.status = 'active'
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    result = calendar_service.is_connected(user_id=123)
    assert result is True


def test_is_connected_false_no_integration(calendar_service, mock_db_session):
    """Test is_connected returns False when no integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    result = calendar_service.is_connected(user_id=123)
    assert result is False


def test_is_connected_false_inactive(calendar_service, mock_db_session, mock_integration):
    """Test is_connected returns False when integration is inactive."""
    mock_integration.status = 'pending'
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    result = calendar_service.is_connected(user_id=123)
    assert result is False


# Test disconnect

def test_disconnect_success(calendar_service, mock_db_session, mock_integration):
    """Test successful disconnection."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    result = calendar_service.disconnect(user_id=123)
    
    assert result == {'message': 'Google Calendar disconnected successfully'}
    assert mock_integration.status == 'disconnected'
    assert mock_integration.data is None
    mock_db_session.commit.assert_called_once()


def test_disconnect_no_integration(calendar_service, mock_db_session):
    """Test disconnect with no integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    with pytest.raises(NotFoundException) as exc_info:
        calendar_service.disconnect(user_id=123)
    
    assert "Google Calendar integration not found" in str(exc_info.value)


# Test private helper methods

def test_get_or_create_integration_existing(calendar_service, mock_db_session, mock_integration):
    """Test _get_or_create_integration with existing integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    result = calendar_service._get_or_create_integration(user_id=123)
    
    assert result == mock_integration
    mock_db_session.add.assert_not_called()


def test_get_or_create_integration_new(calendar_service, mock_db_session):
    """Test _get_or_create_integration creates new integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    result = calendar_service._get_or_create_integration(user_id=123)
    
    mock_db_session.add.assert_called_once()
    mock_db_session.flush.assert_called_once()
    
    # Check the created integration
    created_integration = mock_db_session.add.call_args[0][0]
    assert created_integration.user_id == 123
    assert created_integration.provider == 'google_calendar'
    assert created_integration.status == 'pending'


def test_get_credentials_success(calendar_service, mock_db_session, mock_integration):
    """Test successful credentials retrieval."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    with patch('app.services.calendar_service_refactored.Credentials') as mock_creds_class:
        mock_creds = Mock(spec=Credentials)
        mock_creds_class.return_value = mock_creds
        
        result = calendar_service._get_credentials(user_id=123)
        
        assert result == mock_creds
        mock_creds_class.assert_called_once()


def test_get_credentials_no_integration(calendar_service, mock_db_session):
    """Test credentials retrieval with no integration."""
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    result = calendar_service._get_credentials(user_id=123)
    assert result is None


def test_get_credentials_inactive_integration(calendar_service, mock_db_session, mock_integration):
    """Test credentials retrieval with inactive integration."""
    mock_integration.status = 'pending'
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    result = calendar_service._get_credentials(user_id=123)
    assert result is None


def test_get_credentials_invalid_data(calendar_service, mock_db_session, mock_integration):
    """Test credentials retrieval with invalid data."""
    mock_integration.data = 'invalid json'
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_integration
    
    result = calendar_service._get_credentials(user_id=123)
    assert result is None


def test_build_event_body(calendar_service, sample_event):
    """Test _build_event_body method."""
    body = calendar_service._build_event_body(sample_event)
    
    assert body['summary'] == 'Test Meeting'
    assert body['description'] == 'Test meeting description'
    assert body['location'] == 'Conference Room A'
    assert body['attendees'] == [
        {'email': 'user@example.com'},
        {'email': 'another@example.com'}
    ]
    assert 'start' in body
    assert 'end' in body
    assert 'reminders' in body


def test_transform_event(calendar_service):
    """Test _transform_event method."""
    google_event = {
        'id': 'event123',
        'summary': 'Test Event',
        'description': 'Test Description',
        'location': 'Test Location',
        'start': {'dateTime': '2024-01-01T10:00:00Z'},
        'end': {'dateTime': '2024-01-01T11:00:00Z'},
        'attendees': [
            {'email': 'user1@example.com'},
            {'email': 'user2@example.com', 'responseStatus': 'accepted'}
        ],
        'status': 'confirmed',
        'htmlLink': 'https://calendar.google.com/event123'
    }
    
    result = calendar_service._transform_event(google_event)
    
    assert result['id'] == 'event123'
    assert result['title'] == 'Test Event'
    assert result['description'] == 'Test Description'
    assert result['location'] == 'Test Location'
    assert result['start_time'] == '2024-01-01T10:00:00Z'
    assert result['end_time'] == '2024-01-01T11:00:00Z'
    assert result['attendees'] == ['user1@example.com', 'user2@example.com']
    assert result['status'] == 'confirmed'
    assert result['html_link'] == 'https://calendar.google.com/event123'


# Test edge cases

def test_store_credentials_with_expiry(calendar_service, mock_integration):
    """Test storing credentials with expiry date."""
    mock_credentials = Mock(spec=Credentials)
    mock_credentials.token = 'token'
    mock_credentials.refresh_token = 'refresh'
    mock_credentials.token_uri = 'uri'
    mock_credentials.client_id = 'client'
    mock_credentials.client_secret = 'secret'
    mock_credentials.scopes = ['scope']
    mock_credentials.expiry = datetime(2024, 1, 1, 12, 0, 0)
    
    calendar_service._store_credentials(mock_integration, mock_credentials)
    
    stored_data = json.loads(mock_integration.data)
    assert stored_data['expiry'] == '2024-01-01T12:00:00'
    assert mock_integration.status == 'active'


def test_store_credentials_without_expiry(calendar_service, mock_integration):
    """Test storing credentials without expiry date."""
    mock_credentials = Mock(spec=Credentials)
    mock_credentials.token = 'token'
    mock_credentials.refresh_token = 'refresh'
    mock_credentials.token_uri = 'uri'
    mock_credentials.client_id = 'client'
    mock_credentials.client_secret = 'secret'
    mock_credentials.scopes = ['scope']
    mock_credentials.expiry = None
    
    calendar_service._store_credentials(mock_integration, mock_credentials)
    
    stored_data = json.loads(mock_integration.data)
    assert stored_data['expiry'] is None


# Integration tests

def test_full_oauth_flow(calendar_service, mock_db_session):
    """Test complete OAuth flow from authorization to token storage."""
    # Step 1: Get authorization URL
    with patch('app.services.calendar_service_refactored.Flow') as mock_flow_class:
        mock_flow = Mock()
        mock_flow.authorization_url.return_value = ("https://auth.url", "test_state")
        mock_flow_class.from_client_secrets_file.return_value = mock_flow
        
        # Initially no integration exists
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        auth_result = calendar_service.get_authorization_url(user_id=123)
        assert 'url' in auth_result
        
        # Verify integration was created
        assert mock_db_session.add.called
        created_integration = mock_db_session.add.call_args[0][0]
        
        # Step 2: Handle callback
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = created_integration
        created_integration.data = json.dumps({'state': 'test_state'})
        
        mock_credentials = Mock(spec=Credentials)
        mock_credentials.token = 'new_token'
        mock_credentials.refresh_token = 'new_refresh_token'
        mock_credentials.token_uri = 'https://oauth2.googleapis.com/token'
        mock_credentials.client_id = 'client_id'
        mock_credentials.client_secret = 'client_secret'
        mock_credentials.scopes = ['scope1']
        mock_credentials.expiry = None
        mock_flow.credentials = mock_credentials
        
        callback_result = calendar_service.handle_oauth_callback(
            user_id=123,
            code='auth_code',
            state='test_state'
        )
        
        assert callback_result['success'] is True
        assert created_integration.status == 'active'