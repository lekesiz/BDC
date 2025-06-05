"""Video Conference schemas for request/response validation."""

from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from datetime import datetime


class VideoConferenceSettingsSchema(Schema):
    """Schema for video conference settings."""
    
    waiting_room_enabled = fields.Boolean(missing=True)
    require_authentication = fields.Boolean(missing=False)
    allow_recording = fields.Boolean(missing=True)
    auto_record = fields.Boolean(missing=False)
    meeting_password = fields.String(allow_none=True, validate=validate.Length(min=4, max=20))
    max_participants = fields.Integer(validate=validate.Range(min=2, max=100), missing=10)
    allow_screen_sharing = fields.Boolean(missing=True)
    allow_chat = fields.Boolean(missing=True)
    mute_on_entry = fields.Boolean(missing=True)


class CreateVideoConferenceSchema(Schema):
    """Schema for creating a video conference."""
    
    appointment_id = fields.Integer(required=True, validate=validate.Range(min=1))
    provider = fields.String(
        required=False,
        missing='zoom',
        validate=validate.OneOf(['zoom', 'google_meet', 'microsoft_teams', 'webrtc'])
    )
    settings = fields.Nested(VideoConferenceSettingsSchema, missing=dict)


class UpdateVideoConferenceSchema(Schema):
    """Schema for updating a video conference."""
    
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(validate=validate.Length(max=1000))
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    waiting_room_enabled = fields.Boolean()
    require_authentication = fields.Boolean()
    allow_recording = fields.Boolean()
    auto_record = fields.Boolean()
    
    @validates_schema
    def validate_times(self, data, **kwargs):
        """Validate start and end times."""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError('Start time must be before end time.')
            
            if start_time < datetime.utcnow():
                raise ValidationError('Start time cannot be in the past.')


class AddParticipantSchema(Schema):
    """Schema for adding a participant to a conference."""
    
    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    role = fields.String(
        missing='participant',
        validate=validate.OneOf(['host', 'co_host', 'participant'])
    )
    user_id = fields.Integer(validate=validate.Range(min=1), allow_none=True)


class SendInvitationSchema(Schema):
    """Schema for sending conference invitations."""
    
    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    delivery_method = fields.String(
        missing='email',
        validate=validate.OneOf(['email', 'sms', 'both'])
    )
    phone_number = fields.String(
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$'),
        allow_none=True
    )
    
    @validates_schema
    def validate_delivery_method(self, data, **kwargs):
        """Validate delivery method requirements."""
        delivery_method = data.get('delivery_method')
        phone_number = data.get('phone_number')
        
        if delivery_method in ['sms', 'both'] and not phone_number:
            raise ValidationError('Phone number is required for SMS delivery.')


class VideoConferenceParticipantSchema(Schema):
    """Schema for video conference participant response."""
    
    id = fields.Integer()
    conference_id = fields.Integer()
    user_id = fields.Integer(allow_none=True)
    email = fields.Email()
    name = fields.String()
    role = fields.String()
    joined_at = fields.DateTime(allow_none=True)
    left_at = fields.DateTime(allow_none=True)
    duration_minutes = fields.Integer(allow_none=True)
    invitation_sent = fields.Boolean()
    invitation_sent_at = fields.DateTime(allow_none=True)
    has_joined = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    user = fields.Raw(allow_none=True)  # User details if available


class VideoConferenceRecordingSchema(Schema):
    """Schema for video conference recording response."""
    
    id = fields.Integer()
    conference_id = fields.Integer()
    title = fields.String()
    file_name = fields.String(allow_none=True)
    file_size_bytes = fields.Integer(allow_none=True)
    duration_minutes = fields.Integer(allow_none=True)
    storage_provider = fields.String(allow_none=True)
    storage_path = fields.String(allow_none=True)
    download_url = fields.String(allow_none=True)
    provider_recording_id = fields.String(allow_none=True)
    provider_download_url = fields.String(allow_none=True)
    status = fields.String()
    processing_progress = fields.Integer()
    started_at = fields.DateTime(allow_none=True)
    ended_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    is_public = fields.Boolean()
    password_protected = fields.Boolean()
    expires_at = fields.DateTime(allow_none=True)
    has_transcription = fields.Boolean()


class VideoConferenceAnalyticsSchema(Schema):
    """Schema for video conference analytics response."""
    
    id = fields.Integer()
    conference_id = fields.Integer()
    total_participants = fields.Integer()
    max_concurrent_participants = fields.Integer()
    average_duration_minutes = fields.Integer()
    total_chat_messages = fields.Integer()
    screen_share_duration_minutes = fields.Integer()
    questions_asked = fields.Integer()
    average_audio_quality = fields.Integer()
    average_video_quality = fields.Integer()
    connection_issues_count = fields.Integer()
    bandwidth_usage_mb = fields.Integer()
    cpu_usage_percent = fields.Integer()
    memory_usage_mb = fields.Integer()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class VideoConferenceSchema(Schema):
    """Schema for video conference response."""
    
    id = fields.Integer()
    appointment_id = fields.Integer()
    host_id = fields.Integer()
    title = fields.String()
    description = fields.String(allow_none=True)
    provider = fields.String()
    status = fields.String()
    meeting_id = fields.String(allow_none=True)
    meeting_url = fields.String(allow_none=True)
    meeting_password = fields.String(allow_none=True)
    start_time = fields.DateTime(allow_none=True)
    end_time = fields.DateTime(allow_none=True)
    duration_minutes = fields.Integer(allow_none=True)
    actual_duration_minutes = fields.Integer(allow_none=True)
    waiting_room_enabled = fields.Boolean()
    require_authentication = fields.Boolean()
    allow_recording = fields.Boolean()
    auto_record = fields.Boolean()
    provider_settings = fields.Raw(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    started_at = fields.DateTime(allow_none=True)
    ended_at = fields.DateTime(allow_none=True)
    host = fields.Raw(allow_none=True)  # Host user details
    participants = fields.List(fields.Nested(VideoConferenceParticipantSchema))
    recordings = fields.List(fields.Nested(VideoConferenceRecordingSchema))


class VideoConferenceListSchema(Schema):
    """Schema for paginated video conference list."""
    
    conferences = fields.List(fields.Nested(VideoConferenceSchema))
    total = fields.Integer()
    pages = fields.Integer()
    current_page = fields.Integer()
    per_page = fields.Integer()


class VideoConferenceProviderSchema(Schema):
    """Schema for video conference provider information."""
    
    value = fields.String()
    name = fields.String()
    description = fields.String()


class VideoConferenceProvidersSchema(Schema):
    """Schema for available providers response."""
    
    providers = fields.List(fields.Nested(VideoConferenceProviderSchema))


class VideoConferenceDashboardSchema(Schema):
    """Schema for video conference dashboard response."""
    
    today_conferences = fields.List(fields.Nested(VideoConferenceSchema))
    upcoming_conferences = fields.List(fields.Nested(VideoConferenceSchema))
    recent_recordings = fields.List(fields.Nested(VideoConferenceRecordingSchema))
    statistics = fields.Raw()  # Statistics data


class WebRTCConfigSchema(Schema):
    """Schema for WebRTC configuration response."""
    
    ice_servers = fields.List(fields.Raw())
    websocket_url = fields.String()
    max_participants = fields.Integer()
    recording_enabled = fields.Boolean()
    screen_sharing_enabled = fields.Boolean()
    chat_enabled = fields.Boolean()


class WebRTCRoomSchema(Schema):
    """Schema for WebRTC room information."""
    
    room_id = fields.String()
    conference_id = fields.Integer(allow_none=True)
    created_at = fields.String()
    host_id = fields.String(allow_none=True)
    is_recording = fields.Boolean()
    screen_sharing = fields.String(allow_none=True)
    participant_count = fields.Integer()
    participants = fields.List(fields.Raw())
    chat_message_count = fields.Integer()


class WebRTCJoinRoomSchema(Schema):
    """Schema for WebRTC room join response."""
    
    room_id = fields.String()
    user_info = fields.Raw()
    ice_servers = fields.List(fields.Raw())
    websocket_url = fields.String()


class WebRTCActiveSessionSchema(Schema):
    """Schema for WebRTC active session information."""
    
    room_id = fields.String()
    participant_id = fields.String()
    conference_id = fields.Integer(allow_none=True)
    conference_title = fields.String(allow_none=True)
    joined_at = fields.String()
    is_host = fields.Boolean()
    participant_count = fields.Integer()
    is_recording = fields.Boolean()
    screen_sharing_active = fields.Boolean()


class WebRTCActiveSessionsSchema(Schema):
    """Schema for WebRTC active sessions response."""
    
    active_sessions = fields.List(fields.Nested(WebRTCActiveSessionSchema))
    total_active = fields.Integer()


class CreateWebRTCRoomSchema(Schema):
    """Schema for creating a WebRTC room."""
    
    conference_id = fields.Integer(validate=validate.Range(min=1), allow_none=True)


class WebRTCCreateRoomResponseSchema(Schema):
    """Schema for WebRTC room creation response."""
    
    room_id = fields.String()
    conference_id = fields.Integer(allow_none=True)
    join_url = fields.String()


class WebRTCStatsSchema(Schema):
    """Schema for WebRTC room statistics."""
    
    room_id = fields.String()
    session_duration_minutes = fields.Integer()
    active_participants = fields.Integer()
    total_participants_joined = fields.Integer()
    is_recording = fields.Boolean()
    screen_sharing_active = fields.Boolean()
    chat_messages = fields.Integer()
    created_at = fields.String()


class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    
    error = fields.String(required=True)