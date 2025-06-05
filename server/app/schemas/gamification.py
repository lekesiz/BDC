"""Schemas for Gamification system validation and serialization."""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import datetime


class BadgeSchema(Schema):
    """Schema for Badge model."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    icon_url = fields.String(missing='', validate=validate.Length(max=255))
    category = fields.String(required=True, validate=validate.OneOf([
        'learning', 'participation', 'social', 'mastery', 'consistency', 'special'
    ]))
    rarity = fields.String(missing='common', validate=validate.OneOf([
        'common', 'uncommon', 'rare', 'epic', 'legendary'
    ]))
    points_value = fields.Integer(missing=0, validate=validate.Range(min=0))
    unlock_conditions = fields.Dict(required=True)
    is_secret = fields.Boolean(missing=False)
    is_active = fields.Boolean(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserBadgeSchema(Schema):
    """Schema for UserBadge model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    badge_id = fields.Integer(required=True)
    earned_at = fields.DateTime(dump_only=True)
    progress = fields.Float(missing=0.0, validate=validate.Range(min=0.0, max=100.0))
    metadata = fields.Dict(missing=dict)
    badge = fields.Nested(BadgeSchema, dump_only=True)


class UserXPSchema(Schema):
    """Schema for UserXP model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    total_xp = fields.Integer(dump_only=True)
    current_level = fields.Integer(dump_only=True)
    xp_to_next_level = fields.Integer(dump_only=True)
    level_progress = fields.Float(dump_only=True)
    current_streak = fields.Integer(dump_only=True)
    longest_streak = fields.Integer(dump_only=True)
    last_activity_date = fields.DateTime(dump_only=True)
    xp_multiplier = fields.Float(dump_only=True)
    multiplier_expires_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PointTransactionSchema(Schema):
    """Schema for PointTransaction model."""
    id = fields.Integer(dump_only=True)
    user_xp_id = fields.Integer(required=True)
    activity_type = fields.String(required=True, validate=validate.OneOf([
        'login', 'complete_test', 'perfect_score', 'streak_bonus',
        'social_interaction', 'program_completion', 'challenge_completion',
        'badge_earned', 'referral', 'milestone'
    ]))
    points_earned = fields.Integer(required=True)
    multiplier_applied = fields.Float(missing=1.0)
    related_entity_type = fields.String(allow_none=True)
    related_entity_id = fields.Integer(allow_none=True)
    metadata = fields.Dict(missing=dict)
    created_at = fields.DateTime(dump_only=True)


class LeaderboardSchema(Schema):
    """Schema for Leaderboard model."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    type = fields.String(required=True, validate=validate.OneOf([
        'global', 'class', 'weekly', 'monthly', 'seasonal'
    ]))
    metric = fields.String(required=True, validate=validate.Length(min=1, max=50))
    tenant_id = fields.Integer(allow_none=True)
    start_date = fields.DateTime(allow_none=True)
    end_date = fields.DateTime(allow_none=True)
    max_entries = fields.Integer(missing=100, validate=validate.Range(min=1, max=1000))
    is_active = fields.Boolean(missing=True)
    is_public = fields.Boolean(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that end_date is after start_date."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise ValidationError('end_date must be after start_date')


class LeaderboardEntrySchema(Schema):
    """Schema for LeaderboardEntry model."""
    id = fields.Integer(dump_only=True)
    leaderboard_id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    position = fields.Integer(required=True, validate=validate.Range(min=1))
    score = fields.Float(required=True)
    metadata = fields.Dict(missing=dict)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user = fields.Dict(dump_only=True)  # User info will be populated


class ChallengeSchema(Schema):
    """Schema for Challenge model."""
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    type = fields.String(required=True, validate=validate.OneOf([
        'individual', 'team', 'global', 'daily', 'weekly', 'special_event'
    ]))
    goals = fields.Dict(required=True)
    rewards = fields.Dict(missing=dict)
    difficulty = fields.String(missing='medium', validate=validate.OneOf([
        'easy', 'medium', 'hard', 'expert'
    ]))
    start_date = fields.DateTime(allow_none=True)
    end_date = fields.DateTime(allow_none=True)
    duration_hours = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    max_participants = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    min_participants = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    tenant_id = fields.Integer(allow_none=True)
    participant_count = fields.Integer(dump_only=True)
    is_active = fields.Boolean(missing=True)
    is_featured = fields.Boolean(missing=False)
    is_ongoing = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_challenge(self, data, **kwargs):
        """Validate challenge data."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        min_participants = data.get('min_participants')
        max_participants = data.get('max_participants')
        
        # Validate dates
        if start_date and end_date and end_date <= start_date:
            raise ValidationError('end_date must be after start_date')
        
        # Validate participant limits
        if (min_participants is not None and max_participants is not None 
            and min_participants > max_participants):
            raise ValidationError('min_participants cannot be greater than max_participants')


class ChallengeParticipantSchema(Schema):
    """Schema for ChallengeParticipant model."""
    id = fields.Integer(dump_only=True)
    challenge_id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    team_id = fields.Integer(allow_none=True)
    progress = fields.Dict(missing=dict)
    completion_percentage = fields.Float(dump_only=True)
    is_completed = fields.Boolean(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)
    score = fields.Float(missing=0.0)
    rank = fields.Integer(allow_none=True)
    joined_at = fields.DateTime(dump_only=True)
    user = fields.Dict(dump_only=True)  # User info will be populated


class GamificationTeamSchema(Schema):
    """Schema for GamificationTeam model."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    leader_id = fields.Integer(required=True)
    tenant_id = fields.Integer(allow_none=True)
    max_members = fields.Integer(missing=10, validate=validate.Range(min=1, max=100))
    member_count = fields.Integer(dump_only=True)
    is_open = fields.Boolean(missing=True)
    total_xp = fields.Integer(dump_only=True)
    challenges_completed = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    leader = fields.Dict(dump_only=True)  # Leader info will be populated


class RewardSchema(Schema):
    """Schema for Reward model."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    type = fields.String(required=True, validate=validate.OneOf([
        'virtual_item', 'unlockable_content', 'certification', 'real_world', 'points', 'badge'
    ]))
    cost = fields.Integer(required=True, validate=validate.Range(min=0))
    value = fields.Dict(required=True)
    rarity = fields.String(missing='common', validate=validate.OneOf([
        'common', 'uncommon', 'rare', 'epic', 'legendary'
    ]))
    total_quantity = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    remaining_quantity = fields.Integer(allow_none=True)
    is_active = fields.Boolean(missing=True)
    is_available = fields.Boolean(dump_only=True)
    available_from = fields.DateTime(allow_none=True)
    available_until = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_availability(self, data, **kwargs):
        """Validate availability dates."""
        available_from = data.get('available_from')
        available_until = data.get('available_until')
        
        if (available_from and available_until 
            and available_until <= available_from):
            raise ValidationError('available_until must be after available_from')


class RewardRedemptionSchema(Schema):
    """Schema for RewardRedemption model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    reward_id = fields.Integer(required=True)
    points_spent = fields.Integer(required=True, validate=validate.Range(min=0))
    status = fields.String(missing='pending', validate=validate.OneOf([
        'pending', 'processed', 'delivered', 'cancelled'
    ]))
    delivery_info = fields.Dict(missing=dict)
    processed_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    reward = fields.Nested(RewardSchema, dump_only=True)


class UserGoalSchema(Schema):
    """Schema for UserGoal model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    goal_type = fields.String(required=True, validate=validate.Length(min=1, max=50))
    target_value = fields.Float(required=True, validate=validate.Range(min=0))
    current_value = fields.Float(missing=0.0, validate=validate.Range(min=0))
    progress_percentage = fields.Float(dump_only=True)
    deadline = fields.DateTime(allow_none=True)
    is_active = fields.Boolean(missing=True)
    is_completed = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_goal(self, data, **kwargs):
        """Validate goal data."""
        deadline = data.get('deadline')
        
        if deadline and deadline <= datetime.utcnow():
            raise ValidationError('deadline must be in the future')


class GamificationEventSchema(Schema):
    """Schema for GamificationEvent model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    event_type = fields.String(required=True, validate=validate.Length(min=1, max=50))
    event_data = fields.Dict(missing=dict)
    session_id = fields.String(allow_none=True, validate=validate.Length(max=100))
    ip_address = fields.String(allow_none=True, validate=validate.Length(max=45))
    user_agent = fields.String(allow_none=True, validate=validate.Length(max=255))
    created_at = fields.DateTime(dump_only=True)


class UserProgressSchema(Schema):
    """Schema for UserProgress model."""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    category = fields.String(required=True, validate=validate.Length(min=1, max=50))
    entity_id = fields.Integer(allow_none=True)
    progress_percentage = fields.Float(missing=0.0, validate=validate.Range(min=0.0, max=100.0))
    milestones_reached = fields.List(fields.String(), missing=list)
    time_spent_minutes = fields.Integer(missing=0, validate=validate.Range(min=0))
    last_activity = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# ========== Request Schemas ==========

class BadgeCreateRequestSchema(Schema):
    """Schema for creating a new badge."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    category = fields.String(required=True, validate=validate.OneOf([
        'learning', 'participation', 'social', 'mastery', 'consistency', 'special'
    ]))
    rarity = fields.String(missing='common', validate=validate.OneOf([
        'common', 'uncommon', 'rare', 'epic', 'legendary'
    ]))
    points_value = fields.Integer(missing=0, validate=validate.Range(min=0))
    unlock_conditions = fields.Dict(required=True)
    icon_url = fields.String(missing='', validate=validate.Length(max=255))
    is_secret = fields.Boolean(missing=False)


class ChallengeCreateRequestSchema(Schema):
    """Schema for creating a new challenge."""
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    type = fields.String(required=True, validate=validate.OneOf([
        'individual', 'team', 'global', 'daily', 'weekly', 'special_event'
    ]))
    goals = fields.Dict(required=True)
    rewards = fields.Dict(missing=dict)
    difficulty = fields.String(missing='medium', validate=validate.OneOf([
        'easy', 'medium', 'hard', 'expert'
    ]))
    start_date = fields.DateTime(allow_none=True)
    end_date = fields.DateTime(allow_none=True)
    duration_hours = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    max_participants = fields.Integer(allow_none=True, validate=validate.Range(min=1))


class RewardCreateRequestSchema(Schema):
    """Schema for creating a new reward."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    type = fields.String(required=True, validate=validate.OneOf([
        'virtual_item', 'unlockable_content', 'certification', 'real_world', 'points', 'badge'
    ]))
    cost = fields.Integer(required=True, validate=validate.Range(min=0))
    value = fields.Dict(required=True)
    rarity = fields.String(missing='common', validate=validate.OneOf([
        'common', 'uncommon', 'rare', 'epic', 'legendary'
    ]))
    total_quantity = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    available_from = fields.DateTime(allow_none=True)
    available_until = fields.DateTime(allow_none=True)


class TeamCreateRequestSchema(Schema):
    """Schema for creating a new team."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    max_members = fields.Integer(missing=10, validate=validate.Range(min=1, max=100))
    is_open = fields.Boolean(missing=True)


class GoalCreateRequestSchema(Schema):
    """Schema for creating a new goal."""
    title = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    goal_type = fields.String(required=True, validate=validate.Length(min=1, max=50))
    target_value = fields.Float(required=True, validate=validate.Range(min=0))
    deadline = fields.DateTime(allow_none=True)


class LeaderboardCreateRequestSchema(Schema):
    """Schema for creating a new leaderboard."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(missing='', validate=validate.Length(max=500))
    type = fields.String(required=True, validate=validate.OneOf([
        'global', 'class', 'weekly', 'monthly', 'seasonal'
    ]))
    metric = fields.String(required=True, validate=validate.Length(min=1, max=50))
    start_date = fields.DateTime(allow_none=True)
    end_date = fields.DateTime(allow_none=True)
    max_entries = fields.Integer(missing=100, validate=validate.Range(min=1, max=1000))


class EventLogRequestSchema(Schema):
    """Schema for logging gamification events."""
    event_type = fields.String(required=True, validate=validate.Length(min=1, max=50))
    event_data = fields.Dict(missing=dict)
    session_id = fields.String(allow_none=True, validate=validate.Length(max=100))


class ChallengeJoinRequestSchema(Schema):
    """Schema for joining a challenge."""
    team_id = fields.Integer(allow_none=True)


class AwardBadgeRequestSchema(Schema):
    """Schema for manually awarding a badge."""
    user_id = fields.Integer(required=True)
    metadata = fields.Dict(missing=dict)


class EvaluationCompletionRequestSchema(Schema):
    """Schema for evaluation completion notification."""
    evaluation_id = fields.Integer(required=True)
    score = fields.Float(required=True, validate=validate.Range(min=0, max=100))


class ProgramCompletionRequestSchema(Schema):
    """Schema for program completion notification."""
    program_id = fields.Integer(required=True)


class GoalUpdateRequestSchema(Schema):
    """Schema for updating goal progress."""
    current_value = fields.Float(validate=validate.Range(min=0))
    is_active = fields.Boolean()


# ========== Response Schemas ==========

class ProgressSummaryResponseSchema(Schema):
    """Schema for progress summary response."""
    xp = fields.Nested(UserXPSchema)
    badges = fields.List(fields.Nested(UserBadgeSchema))
    goals = fields.List(fields.Nested(UserGoalSchema))
    challenges = fields.List(fields.Nested(ChallengeParticipantSchema))
    stats = fields.Dict()


class EngagementMetricsResponseSchema(Schema):
    """Schema for engagement metrics response."""
    period_days = fields.Integer()
    total_events = fields.Integer()
    total_points_earned = fields.Integer()
    event_types = fields.Dict()
    daily_activity = fields.Dict()
    average_session_length = fields.Float()


class LeaderboardResponseSchema(Schema):
    """Schema for leaderboard response."""
    leaderboard = fields.Nested(LeaderboardSchema)
    entries = fields.List(fields.Nested(LeaderboardEntrySchema))


class PaginatedResponseSchema(Schema):
    """Schema for paginated responses."""
    pagination = fields.Dict(keys=fields.String(), values=fields.Integer())


class SuccessResponseSchema(Schema):
    """Schema for success responses."""
    success = fields.Boolean()
    message = fields.String()
    data = fields.Raw(allow_none=True)