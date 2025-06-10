"""
Video conferencing integrations for BDC project.

Supports Zoom, Microsoft Teams, and Google Meet integrations.
"""

from .base_video import BaseVideoIntegration, VideoMeeting, VideoMeetingInput, Participant, RecordingInfo
from .zoom_integration import ZoomIntegration
from .teams_integration import TeamsIntegration
from .meet_integration import MeetIntegration

__all__ = [
    'BaseVideoIntegration',
    'VideoMeeting',
    'VideoMeetingInput', 
    'Participant',
    'RecordingInfo',
    'ZoomIntegration',
    'TeamsIntegration',
    'MeetIntegration'
]