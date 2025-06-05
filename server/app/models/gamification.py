"""Comprehensive Gamification system models for the BDC application."""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum

from app.extensions import db


# Achievement Categories
class AchievementCategory(enum.Enum):
    LEARNING = 'learning'
    PARTICIPATION = 'participation'
    SOCIAL = 'social'
    MASTERY = 'mastery'
    CONSISTENCY = 'consistency'
    SPECIAL = 'special'


# Achievement Types
class AchievementType(enum.Enum):
    ONE_TIME = 'one_time'
    PROGRESSIVE = 'progressive'
    REPEATABLE = 'repeatable'


# Point Activity Types
class PointActivityType(enum.Enum):
    LOGIN = 'login'
    COMPLETE_TEST = 'complete_test'
    PERFECT_SCORE = 'perfect_score'
    STREAK_BONUS = 'streak_bonus'
    SOCIAL_INTERACTION = 'social_interaction'
    PROGRAM_COMPLETION = 'program_completion'
    CHALLENGE_COMPLETION = 'challenge_completion'
    BADGE_EARNED = 'badge_earned'
    REFERRAL = 'referral'
    MILESTONE = 'milestone'


# Leaderboard Types
class LeaderboardType(enum.Enum):
    GLOBAL = 'global'
    CLASS = 'class'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    SEASONAL = 'seasonal'


# Challenge Types
class ChallengeType(enum.Enum):
    INDIVIDUAL = 'individual'
    TEAM = 'team'
    GLOBAL = 'global'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    SPECIAL_EVENT = 'special_event'


# Reward Types
class RewardType(enum.Enum):
    VIRTUAL_ITEM = 'virtual_item'
    UNLOCKABLE_CONTENT = 'unlockable_content'
    CERTIFICATION = 'certification'
    REAL_WORLD = 'real_world'
    POINTS = 'points'
    BADGE = 'badge'


# User friendship association table
user_friends = Table(
    'user_friends',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('status', String(20), default='pending')  # pending, accepted, blocked
)

# Team members association table
team_members = Table(
    'team_members',
    db.Model.metadata,
    Column('team_id', Integer, ForeignKey('gamification_teams.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow),
    Column('role', String(20), default='member')  # leader, member
)


class Badge(db.Model):
    """Badge model for achievements."""
    __tablename__ = 'gamification_badges'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    category = Column(Enum(AchievementCategory), nullable=False)
    rarity = Column(String(20), default='common')  # common, uncommon, rare, epic, legendary
    points_value = Column(Integer, default=0)
    
    # Badge unlock conditions
    unlock_conditions = Column(JSON)  # Flexible conditions structure
    is_secret = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_badges = relationship('UserBadge', back_populates='badge', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url,
            'category': self.category.value if self.category else None,
            'rarity': self.rarity,
            'points_value': self.points_value,
            'unlock_conditions': self.unlock_conditions,
            'is_secret': self.is_secret,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class UserBadge(db.Model):
    """User's earned badges."""
    __tablename__ = 'gamification_user_badges'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    badge_id = Column(Integer, ForeignKey('gamification_badges.id'), nullable=False)
    
    earned_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Float, default=0.0)  # For progressive badges
    extra_data = Column(JSON)  # Additional context about earning
    
    # Relationships
    user = relationship('User', backref='user_badges')
    badge = relationship('Badge', back_populates='user_badges')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'earned_at': self.earned_at.isoformat(),
            'progress': self.progress,
            'metadata': self.extra_data,
            'badge': self.badge.to_dict() if self.badge else None
        }


class UserXP(db.Model):
    """User experience points and levels."""
    __tablename__ = 'gamification_user_xp'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    total_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    xp_to_next_level = Column(Integer, default=100)
    
    # Streak tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    
    # Multipliers
    xp_multiplier = Column(Float, default=1.0)
    multiplier_expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='xp_profile')
    point_transactions = relationship('PointTransaction', back_populates='user_xp', lazy='dynamic')
    
    @hybrid_property
    def level_progress(self):
        """Calculate progress within current level."""
        if self.current_level == 1:
            current_level_xp = self.total_xp
        else:
            prev_level_xp = self.calculate_level_xp(self.current_level - 1)
            current_level_xp = self.total_xp - prev_level_xp
        
        current_level_required = self.calculate_level_xp(self.current_level) - (
            self.calculate_level_xp(self.current_level - 1) if self.current_level > 1 else 0)
        
        return (current_level_xp / current_level_required) * 100 if current_level_required > 0 else 0
    
    @staticmethod
    def calculate_level_xp(level):
        """Calculate total XP required for a given level."""
        if level <= 1:
            return 0
        # Formula: XP = 100 * level^1.5
        return int(100 * (level ** 1.5))
    
    def add_xp(self, amount, activity_type=None, metadata=None):
        """Add XP and handle level ups."""
        # Apply multiplier
        actual_amount = int(amount * self.xp_multiplier)
        
        # Create transaction record
        transaction = PointTransaction(
            user_xp_id=self.id,
            activity_type=activity_type,
            points_earned=actual_amount,
            metadata=metadata
        )
        db.session.add(transaction)
        
        self.total_xp += actual_amount
        
        # Check for level up
        old_level = self.current_level
        new_level = self.calculate_level_from_xp(self.total_xp)
        
        if new_level > old_level:
            self.current_level = new_level
            # Calculate XP needed for next level
            next_level_xp = self.calculate_level_xp(new_level + 1)
            self.xp_to_next_level = next_level_xp - self.total_xp
            
            # Trigger level up achievement
            self.trigger_level_achievement(new_level)
        else:
            # Update XP to next level
            next_level_xp = self.calculate_level_xp(self.current_level + 1)
            self.xp_to_next_level = next_level_xp - self.total_xp
        
        self.updated_at = datetime.utcnow()
        return actual_amount
    
    @staticmethod
    def calculate_level_from_xp(total_xp):
        """Calculate level from total XP."""
        level = 1
        while UserXP.calculate_level_xp(level + 1) <= total_xp:
            level += 1
        return level
    
    def update_streak(self):
        """Update login streak."""
        today = datetime.utcnow().date()
        
        if self.last_activity_date:
            last_date = self.last_activity_date.date()
            
            if last_date == today:
                # Already updated today
                return self.current_streak
            elif last_date == today - timedelta(days=1):
                # Consecutive day
                self.current_streak += 1
            else:
                # Streak broken
                self.current_streak = 1
        else:
            # First activity
            self.current_streak = 1
        
        self.last_activity_date = datetime.utcnow()
        
        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        # Trigger streak achievements
        self.trigger_streak_achievements()
        
        return self.current_streak
    
    def trigger_level_achievement(self, level):
        """Trigger achievements for reaching a level."""
        # This would be implemented in the service layer
        pass
    
    def trigger_streak_achievements(self):
        """Trigger achievements for streaks."""
        # This would be implemented in the service layer
        pass
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_xp': self.total_xp,
            'current_level': self.current_level,
            'xp_to_next_level': self.xp_to_next_level,
            'level_progress': self.level_progress,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'xp_multiplier': self.xp_multiplier,
            'multiplier_expires_at': self.multiplier_expires_at.isoformat() if self.multiplier_expires_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PointTransaction(db.Model):
    """Point transaction history."""
    __tablename__ = 'gamification_point_transactions'
    
    id = Column(Integer, primary_key=True)
    user_xp_id = Column(Integer, ForeignKey('gamification_user_xp.id'), nullable=False)
    
    activity_type = Column(Enum(PointActivityType), nullable=False)
    points_earned = Column(Integer, nullable=False)
    multiplier_applied = Column(Float, default=1.0)
    
    # Context information
    related_entity_type = Column(String(50))  # evaluation, program, challenge, etc.
    related_entity_id = Column(Integer)
    extra_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_xp = relationship('UserXP', back_populates='point_transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_xp_id': self.user_xp_id,
            'activity_type': self.activity_type.value if self.activity_type else None,
            'points_earned': self.points_earned,
            'multiplier_applied': self.multiplier_applied,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'metadata': self.extra_data,
            'created_at': self.created_at.isoformat()
        }


class Leaderboard(db.Model):
    """Leaderboard configurations."""
    __tablename__ = 'gamification_leaderboards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(LeaderboardType), nullable=False)
    
    # Configuration
    metric = Column(String(50), nullable=False)  # total_xp, level, streak, etc.
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)  # For class leaderboards
    
    # Time period (for weekly/monthly)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Settings
    max_entries = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = relationship('LeaderboardEntry', back_populates='leaderboard', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'metric': self.metric,
            'tenant_id': self.tenant_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_entries': self.max_entries,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class LeaderboardEntry(db.Model):
    """Individual leaderboard entries."""
    __tablename__ = 'gamification_leaderboard_entries'
    
    id = Column(Integer, primary_key=True)
    leaderboard_id = Column(Integer, ForeignKey('gamification_leaderboards.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    position = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    extra_data = Column(JSON)  # Additional ranking info
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leaderboard = relationship('Leaderboard', back_populates='entries')
    user = relationship('User', backref='leaderboard_entries')
    
    def to_dict(self):
        return {
            'id': self.id,
            'leaderboard_id': self.leaderboard_id,
            'user_id': self.user_id,
            'position': self.position,
            'score': self.score,
            'metadata': self.extra_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }


class Challenge(db.Model):
    """Challenges and quests."""
    __tablename__ = 'gamification_challenges'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Enum(ChallengeType), nullable=False)
    
    # Challenge configuration
    goals = Column(JSON, nullable=False)  # Challenge objectives
    rewards = Column(JSON)  # Rewards for completion
    difficulty = Column(String(20), default='medium')  # easy, medium, hard, expert
    
    # Time constraints
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration_hours = Column(Integer)  # For timed challenges
    
    # Participation settings
    max_participants = Column(Integer)
    min_participants = Column(Integer)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participants = relationship('ChallengeParticipant', back_populates='challenge', lazy='dynamic')
    
    @hybrid_property
    def participant_count(self):
        return self.participants.count()
    
    @hybrid_property
    def is_ongoing(self):
        now = datetime.utcnow()
        if self.start_date and self.end_date:
            return self.start_date <= now <= self.end_date
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'goals': self.goals,
            'rewards': self.rewards,
            'difficulty': self.difficulty,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_hours': self.duration_hours,
            'max_participants': self.max_participants,
            'min_participants': self.min_participants,
            'tenant_id': self.tenant_id,
            'participant_count': self.participant_count,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'is_ongoing': self.is_ongoing,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ChallengeParticipant(db.Model):
    """Challenge participation tracking."""
    __tablename__ = 'gamification_challenge_participants'
    
    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey('gamification_challenges.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('gamification_teams.id'), nullable=True)
    
    # Progress tracking
    progress = Column(JSON, default=dict)  # Progress on challenge goals
    completion_percentage = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    # Performance
    score = Column(Float, default=0.0)
    rank = Column(Integer)
    
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge = relationship('Challenge', back_populates='participants')
    user = relationship('User', backref='challenge_participations')
    team = relationship('GamificationTeam', backref='challenge_participations')
    
    def update_progress(self, goal_key, value):
        """Update progress for a specific goal."""
        if not self.progress:
            self.progress = {}
        
        self.progress[goal_key] = value
        
        # Calculate completion percentage
        total_goals = len(self.challenge.goals) if self.challenge.goals else 1
        completed_goals = sum(1 for goal in self.challenge.goals.values() 
                            if self.progress.get(goal.get('key', ''), 0) >= goal.get('target', 1))
        
        self.completion_percentage = (completed_goals / total_goals) * 100
        
        # Check if completed
        if self.completion_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'progress': self.progress,
            'completion_percentage': self.completion_percentage,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'score': self.score,
            'rank': self.rank,
            'joined_at': self.joined_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }


class GamificationTeam(db.Model):
    """Teams for collaborative challenges."""
    __tablename__ = 'gamification_teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    leader_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True)
    
    # Team settings
    max_members = Column(Integer, default=10)
    is_open = Column(Boolean, default=True)  # Allow joining without invitation
    
    # Team statistics
    total_xp = Column(Integer, default=0)
    challenges_completed = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leader = relationship('User', foreign_keys=[leader_id], backref='led_teams')
    members = relationship('User', secondary=team_members, backref='teams')
    
    @hybrid_property
    def member_count(self):
        return len(self.members)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'leader_id': self.leader_id,
            'tenant_id': self.tenant_id,
            'max_members': self.max_members,
            'member_count': self.member_count,
            'is_open': self.is_open,
            'total_xp': self.total_xp,
            'challenges_completed': self.challenges_completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'leader': self.leader.to_dict() if self.leader else None
        }


class Reward(db.Model):
    """Rewards and incentives."""
    __tablename__ = 'gamification_rewards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(RewardType), nullable=False)
    
    # Reward configuration
    cost = Column(Integer, default=0)  # Point cost to redeem
    value = Column(JSON)  # Reward value/content
    rarity = Column(String(20), default='common')
    
    # Availability
    total_quantity = Column(Integer)  # Null for unlimited
    remaining_quantity = Column(Integer)
    is_active = Column(Boolean, default=True)
    
    # Time constraints
    available_from = Column(DateTime)
    available_until = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    redemptions = relationship('RewardRedemption', back_populates='reward', lazy='dynamic')
    
    @hybrid_property
    def is_available(self):
        now = datetime.utcnow()
        
        # Check time constraints
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        
        # Check quantity
        if self.total_quantity and (not self.remaining_quantity or self.remaining_quantity <= 0):
            return False
        
        return self.is_active
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'cost': self.cost,
            'value': self.value,
            'rarity': self.rarity,
            'total_quantity': self.total_quantity,
            'remaining_quantity': self.remaining_quantity,
            'is_active': self.is_active,
            'is_available': self.is_available,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_until': self.available_until.isoformat() if self.available_until else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class RewardRedemption(db.Model):
    """User reward redemptions."""
    __tablename__ = 'gamification_reward_redemptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reward_id = Column(Integer, ForeignKey('gamification_rewards.id'), nullable=False)
    
    points_spent = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')  # pending, processed, delivered, cancelled
    
    # Delivery information
    delivery_info = Column(JSON)
    processed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='reward_redemptions')
    reward = relationship('Reward', back_populates='redemptions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reward_id': self.reward_id,
            'points_spent': self.points_spent,
            'status': self.status,
            'delivery_info': self.delivery_info,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat(),
            'reward': self.reward.to_dict() if self.reward else None
        }


class UserGoal(db.Model):
    """User personal goals and milestones."""
    __tablename__ = 'gamification_user_goals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Goal configuration
    goal_type = Column(String(50), nullable=False)  # xp_target, streak_target, etc.
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    
    # Time constraints
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', backref='personal_goals')
    
    @hybrid_property
    def progress_percentage(self):
        if self.target_value <= 0:
            return 0
        return min((self.current_value / self.target_value) * 100, 100)
    
    def update_progress(self, new_value):
        """Update goal progress."""
        self.current_value = new_value
        
        if self.current_value >= self.target_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'progress_percentage': self.progress_percentage,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class GamificationEvent(db.Model):
    """Track gamification events for analytics."""
    __tablename__ = 'gamification_events'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON)
    
    # Context
    session_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='gamification_events')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat()
        }


class UserProgress(db.Model):
    """Track user progress across different areas."""
    __tablename__ = 'gamification_user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Progress categories
    category = Column(String(50), nullable=False)  # program, skill, course, etc.
    entity_id = Column(Integer)  # Related entity ID
    
    # Progress metrics
    progress_percentage = Column(Float, default=0.0)
    milestones_reached = Column(JSON, default=list)
    
    # Time tracking
    time_spent_minutes = Column(Integer, default=0)
    last_activity = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='progress_tracking')
    
    def add_milestone(self, milestone_name):
        """Add a reached milestone."""
        if not self.milestones_reached:
            self.milestones_reached = []
        
        if milestone_name not in self.milestones_reached:
            self.milestones_reached.append(milestone_name)
            self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'entity_id': self.entity_id,
            'progress_percentage': self.progress_percentage,
            'milestones_reached': self.milestones_reached or [],
            'time_spent_minutes': self.time_spent_minutes,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }