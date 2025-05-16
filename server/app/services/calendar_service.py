"""Google Calendar service module."""

import os
import datetime
import json
from flask import current_app, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.extensions import db


class CalendarService:
    """Google Calendar service."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CLIENT_SECRETS_FILE = 'client_secret.json'
    API_SERVICE_NAME = 'calendar'
    API_VERSION = 'v3'
    
    @classmethod
    def get_authorization_url(cls, user_id, redirect_uri=None):
        """
        Get a URL for authorizing the app to access Google Calendar.
        
        Args:
            user_id (int): The user's ID
            redirect_uri (str): The URI to redirect to after authorization
            
        Returns:
            str: The authorization URL
        """
        try:
            # Create a flow instance with the client secrets file
            client_secrets_path = os.path.join(
                current_app.root_path, 'credentials', cls.CLIENT_SECRETS_FILE
            )
            
            if not os.path.exists(client_secrets_path):
                current_app.logger.error(f"Client secrets file not found at {client_secrets_path}")
                return None
            
            flow = Flow.from_client_secrets_file(
                client_secrets_path,
                scopes=cls.SCOPES
            )
            
            # The redirect URI is the URL that the authorization server will redirect
            # the user back to after they authorize the application
            if not redirect_uri:
                redirect_uri = url_for('appointments.oauth2callback', _external=True)
            
            flow.redirect_uri = redirect_uri
            
            # Generate the authorization URL
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Store the state for later validation
            from app.models.integration import UserIntegration
            
            integration = UserIntegration.query.filter_by(
                user_id=user_id,
                provider='google_calendar'
            ).first()
            
            if not integration:
                integration = UserIntegration(
                    user_id=user_id,
                    provider='google_calendar',
                    status='pending',
                    data=json.dumps({'state': state})
                )
                db.session.add(integration)
            else:
                integration.status = 'pending'
                integration.data = json.dumps({'state': state})
                integration.updated_at = datetime.datetime.utcnow()
            
            db.session.commit()
            
            return authorization_url
        
        except Exception as e:
            current_app.logger.error(f"Error getting authorization URL: {str(e)}")
            return None
    
    @classmethod
    def handle_callback(cls, user_id, code, state):
        """
        Handle the callback from Google OAuth.
        
        Args:
            user_id (int): The user's ID
            code (str): Authorization code
            state (str): State token
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the stored state
            from app.models.integration import UserIntegration
            
            integration = UserIntegration.query.filter_by(
                user_id=user_id,
                provider='google_calendar'
            ).first()
            
            if not integration:
                current_app.logger.error(f"No integration found for user {user_id}")
                return False
            
            stored_state = json.loads(integration.data).get('state')
            
            if stored_state != state:
                current_app.logger.error(f"State mismatch for user {user_id}")
                return False
            
            # Create a flow instance with the client secrets file
            client_secrets_path = os.path.join(
                current_app.root_path, 'credentials', cls.CLIENT_SECRETS_FILE
            )
            
            flow = Flow.from_client_secrets_file(
                client_secrets_path,
                scopes=cls.SCOPES,
                state=state
            )
            
            flow.redirect_uri = url_for('appointments.oauth2callback', _external=True)
            
            # Exchange the authorization code for credentials
            flow.fetch_token(code=code)
            
            # Get the credentials
            credentials = flow.credentials
            
            # Store the credentials
            integration.status = 'active'
            integration.data = json.dumps({
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            })
            integration.updated_at = datetime.datetime.utcnow()
            
            db.session.commit()
            
            return True
        
        except Exception as e:
            current_app.logger.error(f"Error handling callback: {str(e)}")
            return False
    
    @classmethod
    def get_credentials(cls, user_id):
        """
        Get the credentials for a user.
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            Credentials: The credentials or None if not found
        """
        try:
            from app.models.integration import UserIntegration
            
            integration = UserIntegration.query.filter_by(
                user_id=user_id,
                provider='google_calendar',
                status='active'
            ).first()
            
            if not integration:
                return None
            
            data = json.loads(integration.data)
            
            # Create the credentials
            credentials = Credentials(
                token=data.get('token'),
                refresh_token=data.get('refresh_token'),
                token_uri=data.get('token_uri'),
                client_id=data.get('client_id'),
                client_secret=data.get('client_secret'),
                scopes=data.get('scopes')
            )
            
            if data.get('expiry'):
                credentials.expiry = datetime.datetime.fromisoformat(data.get('expiry'))
            
            return credentials
        
        except Exception as e:
            current_app.logger.error(f"Error getting credentials: {str(e)}")
            return None
    
    @classmethod
    def create_calendar_event(cls, user_id, appointment):
        """
        Create a calendar event for an appointment.
        
        Args:
            user_id (int): The user's ID
            appointment (dict): The appointment details
            
        Returns:
            str: The event ID or None if creation fails
        """
        try:
            # Get the credentials
            credentials = cls.get_credentials(user_id)
            
            if not credentials:
                return None
            
            # Build the service
            service = build(cls.API_SERVICE_NAME, cls.API_VERSION, credentials=credentials)
            
            # Create the event
            event = {
                'summary': appointment.get('title'),
                'description': appointment.get('description'),
                'start': {
                    'dateTime': appointment.get('start_time').isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': appointment.get('end_time').isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': email} for email in appointment.get('attendees', [])
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            # If location is provided, add it to the event
            if appointment.get('location'):
                event['location'] = appointment.get('location')
            
            # Create the event
            event = service.events().insert(calendarId='primary', body=event).execute()
            
            return event.get('id')
        
        except HttpError as e:
            current_app.logger.error(f"Error creating calendar event: {str(e)}")
            return None
        
        except Exception as e:
            current_app.logger.error(f"Error creating calendar event: {str(e)}")
            return None
    
    @classmethod
    def update_calendar_event(cls, user_id, event_id, appointment):
        """
        Update a calendar event.
        
        Args:
            user_id (int): The user's ID
            event_id (str): The event ID
            appointment (dict): The updated appointment details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the credentials
            credentials = cls.get_credentials(user_id)
            
            if not credentials:
                return False
            
            # Build the service
            service = build(cls.API_SERVICE_NAME, cls.API_VERSION, credentials=credentials)
            
            # Get the existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update the event
            event['summary'] = appointment.get('title')
            event['description'] = appointment.get('description')
            event['start']['dateTime'] = appointment.get('start_time').isoformat()
            event['end']['dateTime'] = appointment.get('end_time').isoformat()
            
            # Update attendees
            event['attendees'] = [
                {'email': email} for email in appointment.get('attendees', [])
            ]
            
            # If location is provided, update it
            if appointment.get('location'):
                event['location'] = appointment.get('location')
            
            # Update the event
            service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            
            return True
        
        except HttpError as e:
            current_app.logger.error(f"Error updating calendar event: {str(e)}")
            return False
        
        except Exception as e:
            current_app.logger.error(f"Error updating calendar event: {str(e)}")
            return False
    
    @classmethod
    def delete_calendar_event(cls, user_id, event_id):
        """
        Delete a calendar event.
        
        Args:
            user_id (int): The user's ID
            event_id (str): The event ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the credentials
            credentials = cls.get_credentials(user_id)
            
            if not credentials:
                return False
            
            # Build the service
            service = build(cls.API_SERVICE_NAME, cls.API_VERSION, credentials=credentials)
            
            # Delete the event
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            
            return True
        
        except HttpError as e:
            current_app.logger.error(f"Error deleting calendar event: {str(e)}")
            return False
        
        except Exception as e:
            current_app.logger.error(f"Error deleting calendar event: {str(e)}")
            return False
    
    @classmethod
    def get_calendar_events(cls, user_id, start_time=None, end_time=None, max_results=10):
        """
        Get calendar events for a user.
        
        Args:
            user_id (int): The user's ID
            start_time (datetime): The start time for the time range
            end_time (datetime): The end time for the time range
            max_results (int): The maximum number of results to return
            
        Returns:
            list: The events or None if retrieval fails
        """
        try:
            # Get the credentials
            credentials = cls.get_credentials(user_id)
            
            if not credentials:
                return None
            
            # Build the service
            service = build(cls.API_SERVICE_NAME, cls.API_VERSION, credentials=credentials)
            
            # Prepare parameters
            params = {
                'calendarId': 'primary',
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if start_time:
                params['timeMin'] = start_time.isoformat() + 'Z'
            
            if end_time:
                params['timeMax'] = end_time.isoformat() + 'Z'
            
            # Get the events
            events_result = service.events().list(**params).execute()
            
            # Get the events
            events = events_result.get('items', [])
            
            return events
        
        except HttpError as e:
            current_app.logger.error(f"Error getting calendar events: {str(e)}")
            return None
        
        except Exception as e:
            current_app.logger.error(f"Error getting calendar events: {str(e)}")
            return None