"""
iCal (WebDAV) calendar integration.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urljoin

try:
    import aiohttp
    from icalendar import Calendar as ICalCalendar, Event as ICalEvent
    import caldav
    ICAL_AVAILABLE = True
except ImportError:
    ICAL_AVAILABLE = False

from ..base import BaseIntegration, IntegrationConfig, AuthenticationError, ServiceUnavailableError
from ..registry import register_integration
from .base_calendar import (
    BaseCalendarIntegration, CalendarEvent, CalendarEventInput, Calendar,
    EventStatus, EventVisibility
)

logger = logging.getLogger(__name__)


@register_integration('ical_calendar')
class ICalCalendarIntegration(BaseCalendarIntegration):
    """iCal/WebDAV calendar integration."""
    
    def __init__(self, config: IntegrationConfig):
        if not ICAL_AVAILABLE:
            raise ImportError("iCal dependencies not available. Install icalendar caldav")
        
        super().__init__(config)
        self._client = None
        self._principal = None
        
    @property
    def provider_name(self) -> str:
        return "ical"
    
    async def _authenticate(self) -> bool:
        """Authenticate with CalDAV server."""
        try:
            server_url = self.config.credentials.get('server_url')
            username = self.config.credentials.get('username')
            password = self.config.credentials.get('password')
            
            if not all([server_url, username, password]):
                return False
            
            # Run CalDAV operations in thread pool
            loop = asyncio.get_event_loop()
            
            def connect_caldav():
                client = caldav.DAVClient(
                    url=server_url,
                    username=username,
                    password=password
                )
                principal = client.principal()
                return client, principal
            
            self._client, self._principal = await loop.run_in_executor(None, connect_caldav)
            return True
            
        except Exception as e:
            logger.error(f"CalDAV authentication failed: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connect to CalDAV server."""
        return await self.authenticate(self.config.credentials)
    
    async def disconnect(self) -> bool:
        """Disconnect from CalDAV server."""
        self._client = None
        self._principal = None
        return True
    
    async def test_connection(self) -> bool:
        """Test CalDAV connection."""
        try:
            if not self._principal:
                return False
            
            loop = asyncio.get_event_loop()
            calendars = await loop.run_in_executor(
                None,
                lambda: self._principal.calendars()
            )
            return len(calendars) >= 0  # Even 0 calendars means connection works
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_calendars(self) -> List[Calendar]:
        """Get list of CalDAV calendars."""
        if not self._principal:
            raise ServiceUnavailableError("Not connected to CalDAV server", "calendar")
        
        try:
            loop = asyncio.get_event_loop()
            caldav_calendars = await loop.run_in_executor(
                None,
                lambda: self._principal.calendars()
            )
            
            calendars = []
            for cal in caldav_calendars:
                # Get calendar properties
                props = await loop.run_in_executor(None, cal.get_properties, [
                    caldav.dav.DisplayName(),
                    caldav.caldav.CalendarDescription(),
                    caldav.caldav.CalendarTimeZone()
                ])
                
                calendar = Calendar(
                    id=cal.url,
                    name=props.get(caldav.dav.DisplayName.tag, str(cal.url)).strip(),
                    description=props.get(caldav.caldav.CalendarDescription.tag, '').strip(),
                    timezone=self._extract_timezone_from_cal_props(props),
                    primary=False  # CalDAV doesn't have a primary calendar concept
                )
                calendars.append(calendar)
            
            return calendars
        except Exception as e:
            logger.error(f"Failed to get calendars: {e}")
            raise ServiceUnavailableError(f"Failed to get calendars: {e}", "calendar")
    
    async def get_primary_calendar(self) -> Optional[Calendar]:
        """Get the first available calendar as 'primary'."""
        calendars = await self.get_calendars()
        return calendars[0] if calendars else None
    
    async def create_event(self, calendar_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Create a new event in CalDAV calendar."""
        if not self._principal:
            raise ServiceUnavailableError("Not connected to CalDAV server", "calendar")
        
        try:
            # Find the calendar
            calendar = await self._get_calendar_by_id(calendar_id)
            if not calendar:
                raise ServiceUnavailableError(f"Calendar not found: {calendar_id}", "calendar")
            
            # Create iCal event
            ical_event = self._convert_to_ical_event(event_data)
            
            # Save to CalDAV
            loop = asyncio.get_event_loop()
            caldav_event = await loop.run_in_executor(
                None,
                lambda: calendar.save_event(ical_event.to_ical().decode('utf-8'))
            )
            
            # Return the created event
            return await self._convert_from_caldav_event(caldav_event)
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise ServiceUnavailableError(f"Failed to create event: {e}", "calendar")
    
    async def get_event(self, calendar_id: str, event_id: str) -> Optional[CalendarEvent]:
        """Get a specific event from CalDAV calendar."""
        if not self._principal:
            raise ServiceUnavailableError("Not connected to CalDAV server", "calendar")
        
        try:
            calendar = await self._get_calendar_by_id(calendar_id)
            if not calendar:
                return None
            
            loop = asyncio.get_event_loop()
            
            # Search for event by UID
            events = await loop.run_in_executor(
                None,
                lambda: calendar.search(uid=event_id)
            )
            
            if not events:
                return None
            
            return await self._convert_from_caldav_event(events[0])
            
        except Exception as e:
            logger.error(f"Failed to get event: {e}")
            return None
    
    async def update_event(self, calendar_id: str, event_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Update an existing event in CalDAV calendar."""
        if not self._principal:
            raise ServiceUnavailableError("Not connected to CalDAV server", "calendar")
        
        try:
            calendar = await self._get_calendar_by_id(calendar_id)
            if not calendar:
                raise ServiceUnavailableError(f"Calendar not found: {calendar_id}", "calendar")
            
            loop = asyncio.get_event_loop()
            
            # Find existing event
            events = await loop.run_in_executor(
                None,
                lambda: calendar.search(uid=event_id)
            )
            
            if not events:
                raise ServiceUnavailableError(f"Event not found: {event_id}", "calendar")
            
            caldav_event = events[0]
            
            # Update the event data
            updated_ical = self._convert_to_ical_event(event_data, event_id)
            
            # Save updated event
            await loop.run_in_executor(
                None,
                lambda: caldav_event.save(updated_ical.to_ical().decode('utf-8'))
            )
            
            return await self._convert_from_caldav_event(caldav_event)
            
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            raise ServiceUnavailableError(f"Failed to update event: {e}", "calendar")
    
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete an event from CalDAV calendar."""
        if not self._principal:
            raise ServiceUnavailableError("Not connected to CalDAV server", "calendar")
        
        try:
            calendar = await self._get_calendar_by_id(calendar_id)
            if not calendar:
                return False
            
            loop = asyncio.get_event_loop()
            
            # Find and delete event
            events = await loop.run_in_executor(
                None,
                lambda: calendar.search(uid=event_id)
            )
            
            if not events:
                return True  # Already deleted
            
            await loop.run_in_executor(None, events[0].delete)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return False
    
    async def list_events(
        self, 
        calendar_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[CalendarEvent]:
        """List events from CalDAV calendar."""
        if not self._principal:
            raise ServiceUnavailableError("Not connected to CalDAV server", "calendar")
        
        try:
            calendar = await self._get_calendar_by_id(calendar_id)
            if not calendar:
                raise ServiceUnavailableError(f"Calendar not found: {calendar_id}", "calendar")
            
            loop = asyncio.get_event_loop()
            
            # Search events within time range
            search_kwargs = {}
            if start_time:
                search_kwargs['start'] = start_time
            if end_time:
                search_kwargs['end'] = end_time
            
            caldav_events = await loop.run_in_executor(
                None,
                lambda: calendar.date_search(**search_kwargs)
            )
            
            # Convert to CalendarEvent objects
            events = []
            for caldav_event in caldav_events[:max_results]:
                try:
                    event = await self._convert_from_caldav_event(caldav_event)
                    events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to convert event: {e}")
                    continue
            
            # Sort by start time
            events.sort(key=lambda e: e.start_time)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            raise ServiceUnavailableError(f"Failed to list events: {e}", "calendar")
    
    async def search_events(self, calendar_id: str, query: str) -> List[CalendarEvent]:
        """Search for events in CalDAV calendar."""
        # CalDAV doesn't support text search natively, so we'll get all events
        # and filter them locally
        all_events = await self.list_events(calendar_id)
        
        query_lower = query.lower()
        matching_events = []
        
        for event in all_events:
            if (query_lower in event.title.lower() or 
                (event.description and query_lower in event.description.lower()) or
                (event.location and query_lower in event.location.lower())):
                matching_events.append(event)
        
        return matching_events
    
    async def _get_calendar_by_id(self, calendar_id: str):
        """Get CalDAV calendar object by ID (URL)."""
        if not self._principal:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            calendars = await loop.run_in_executor(
                None,
                lambda: self._principal.calendars()
            )
            
            for cal in calendars:
                if cal.url == calendar_id or cal.url.rstrip('/') == calendar_id.rstrip('/'):
                    return cal
            
            return None
        except Exception as e:
            logger.error(f"Failed to get calendar: {e}")
            return None
    
    def _convert_to_ical_event(self, event_data: CalendarEventInput, uid: Optional[str] = None) -> ICalEvent:
        """Convert CalendarEventInput to iCal event."""
        event = ICalEvent()
        
        # Basic properties
        event.add('summary', event_data.title)
        event.add('dtstart', event_data.start_time)
        event.add('dtend', event_data.end_time)
        
        if uid:
            event.add('uid', uid)
        else:
            # Generate UID
            import uuid
            event.add('uid', str(uuid.uuid4()))
        
        if event_data.description:
            event.add('description', event_data.description)
        
        if event_data.location:
            event.add('location', event_data.location)
        
        # Attendees
        for attendee in event_data.attendees:
            event.add('attendee', f'mailto:{attendee}')
        
        # Timestamps
        event.add('dtstamp', datetime.now(timezone.utc))
        event.add('created', datetime.now(timezone.utc))
        
        return event
    
    async def _convert_from_caldav_event(self, caldav_event) -> CalendarEvent:
        """Convert CalDAV event to CalendarEvent."""
        loop = asyncio.get_event_loop()
        
        # Get event data
        ical_data = await loop.run_in_executor(None, caldav_event.data)
        ical_calendar = ICalCalendar.from_ical(ical_data)
        
        # Find the event component
        event_component = None
        for component in ical_calendar.walk():
            if component.name == "VEVENT":
                event_component = component
                break
        
        if not event_component:
            raise ValueError("No VEVENT component found")
        
        # Extract event data
        uid = str(event_component.get('uid', ''))
        title = str(event_component.get('summary', ''))
        description = str(event_component.get('description', '')) if event_component.get('description') else None
        location = str(event_component.get('location', '')) if event_component.get('location') else None
        
        # Parse dates
        start_time = event_component.get('dtstart').dt
        end_time = event_component.get('dtend').dt
        
        # Ensure datetime objects
        if not isinstance(start_time, datetime):
            start_time = datetime.combine(start_time, datetime.min.time())
        if not isinstance(end_time, datetime):
            end_time = datetime.combine(end_time, datetime.min.time())
        
        # Parse attendees
        attendees = []
        attendee_props = event_component.get('attendee', [])
        if not isinstance(attendee_props, list):
            attendee_props = [attendee_props]
        
        for attendee in attendee_props:
            if str(attendee).startswith('mailto:'):
                attendees.append(str(attendee)[7:])  # Remove 'mailto:'
        
        # Parse timestamps
        created_at = event_component.get('created')
        if created_at:
            created_at = created_at.dt if hasattr(created_at, 'dt') else created_at
        
        last_modified = event_component.get('last-modified')
        if last_modified:
            last_modified = last_modified.dt if hasattr(last_modified, 'dt') else last_modified
        
        return CalendarEvent(
            id=uid,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees,
            organizer=None,  # Could be extracted from ORGANIZER property
            status=EventStatus.CONFIRMED,  # Could be extracted from STATUS property
            all_day=not isinstance(event_component.get('dtstart').dt, datetime),
            created_at=created_at,
            updated_at=last_modified
        )
    
    def _extract_timezone_from_cal_props(self, props: Dict) -> Optional[str]:
        """Extract timezone from calendar properties."""
        tz_prop = props.get(caldav.caldav.CalendarTimeZone.tag)
        if tz_prop:
            # Parse VTIMEZONE component to get timezone ID
            try:
                tz_cal = ICalCalendar.from_ical(tz_prop)
                for component in tz_cal.walk():
                    if component.name == "VTIMEZONE":
                        return str(component.get('tzid', ''))
            except Exception:
                pass
        return None