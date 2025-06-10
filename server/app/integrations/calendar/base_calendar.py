"""
Base calendar integration functionality.
"""

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..base import BaseIntegration, IntegrationConfig


class EventStatus(Enum):
    """Calendar event status."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class EventVisibility(Enum):
    """Calendar event visibility."""
    DEFAULT = "default"
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


@dataclass
class CalendarEventInput:
    """Input data for creating/updating calendar events."""
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    timezone: Optional[str] = None
    all_day: bool = False
    recurrence: Optional[Dict[str, Any]] = None
    reminders: Optional[List[Dict[str, Any]]] = None
    visibility: EventVisibility = EventVisibility.DEFAULT
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.reminders is None:
            self.reminders = []


@dataclass
class CalendarEvent:
    """Represents a calendar event."""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    organizer: Optional[str] = None
    status: EventStatus = EventStatus.CONFIRMED
    visibility: EventVisibility = EventVisibility.DEFAULT
    timezone: Optional[str] = None
    all_day: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    html_link: Optional[str] = None
    meeting_link: Optional[str] = None
    recurrence: Optional[Dict[str, Any]] = None
    reminders: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.reminders is None:
            self.reminders = []


@dataclass
class Calendar:
    """Represents a calendar."""
    id: str
    name: str
    description: Optional[str] = None
    timezone: Optional[str] = None
    primary: bool = False
    access_role: Optional[str] = None
    color: Optional[str] = None


class BaseCalendarIntegration(BaseIntegration):
    """Base class for calendar integrations."""
    
    @property
    def integration_type(self) -> str:
        return "calendar"
    
    @abstractmethod
    async def get_calendars(self) -> List[Calendar]:
        """Get list of available calendars."""
        pass
    
    @abstractmethod
    async def get_primary_calendar(self) -> Optional[Calendar]:
        """Get the primary calendar."""
        pass
    
    @abstractmethod
    async def create_event(self, calendar_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Create a new event in the specified calendar."""
        pass
    
    @abstractmethod
    async def get_event(self, calendar_id: str, event_id: str) -> Optional[CalendarEvent]:
        """Get a specific event by ID."""
        pass
    
    @abstractmethod
    async def update_event(self, calendar_id: str, event_id: str, event_data: CalendarEventInput) -> CalendarEvent:
        """Update an existing event."""
        pass
    
    @abstractmethod
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete an event."""
        pass
    
    @abstractmethod
    async def list_events(
        self, 
        calendar_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[CalendarEvent]:
        """List events in a calendar within the specified time range."""
        pass
    
    @abstractmethod
    async def search_events(self, calendar_id: str, query: str) -> List[CalendarEvent]:
        """Search for events by text query."""
        pass
    
    async def get_availability(
        self, 
        calendar_id: str,
        start_time: datetime,
        end_time: datetime,
        duration_minutes: int = 60
    ) -> List[Dict[str, datetime]]:
        """Find available time slots in the calendar."""
        events = await self.list_events(calendar_id, start_time, end_time)
        
        # Sort events by start time
        events.sort(key=lambda e: e.start_time)
        
        available_slots = []
        current_time = start_time
        
        for event in events:
            # Skip all-day events or cancelled events
            if event.all_day or event.status == EventStatus.CANCELLED:
                continue
            
            # If there's a gap before this event
            if current_time + timedelta(minutes=duration_minutes) <= event.start_time:
                available_slots.append({
                    'start': current_time,
                    'end': event.start_time
                })
            
            # Move past this event
            current_time = max(current_time, event.end_time)
        
        # Check if there's time after the last event
        if current_time + timedelta(minutes=duration_minutes) <= end_time:
            available_slots.append({
                'start': current_time,
                'end': end_time
            })
        
        return available_slots
    
    def _parse_recurrence_rule(self, rrule: str) -> Dict[str, Any]:
        """Parse RRULE string into a dictionary."""
        if not rrule:
            return {}
        
        rule_parts = {}
        for part in rrule.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                rule_parts[key] = value
        
        return rule_parts
    
    def _build_recurrence_rule(self, recurrence: Dict[str, Any]) -> str:
        """Build RRULE string from dictionary."""
        if not recurrence:
            return ""
        
        rule_parts = []
        for key, value in recurrence.items():
            rule_parts.append(f"{key}={value}")
        
        return ';'.join(rule_parts)