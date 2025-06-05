"""Add gamification tables to the database.

This migration adds all the necessary tables for the comprehensive 
gamification system including badges, XP, leaderboards, challenges, 
teams, rewards, and social features.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime


def upgrade():
    """Add gamification tables."""
    
    # Create gamification_badges table
    op.create_table(
        'gamification_badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(length=255), nullable=True),
        sa.Column('category', sa.Enum('learning', 'participation', 'social', 'mastery', 'consistency', 'special', name='achievementcategory'), nullable=False),
        sa.Column('rarity', sa.String(length=20), nullable=True, default='common'),
        sa.Column('points_value', sa.Integer(), nullable=True, default=0),
        sa.Column('unlock_conditions', sa.JSON(), nullable=True),
        sa.Column('is_secret', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_badges_category', 'gamification_badges', ['category'])
    op.create_index('ix_badges_rarity', 'gamification_badges', ['rarity'])
    op.create_index('ix_badges_active', 'gamification_badges', ['is_active'])
    
    # Create gamification_user_xp table
    op.create_table(
        'gamification_user_xp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_xp', sa.Integer(), nullable=True, default=0),
        sa.Column('current_level', sa.Integer(), nullable=True, default=1),
        sa.Column('xp_to_next_level', sa.Integer(), nullable=True, default=100),
        sa.Column('current_streak', sa.Integer(), nullable=True, default=0),
        sa.Column('longest_streak', sa.Integer(), nullable=True, default=0),
        sa.Column('last_activity_date', sa.DateTime(), nullable=True),
        sa.Column('xp_multiplier', sa.Float(), nullable=True, default=1.0),
        sa.Column('multiplier_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_xp_level', 'gamification_user_xp', ['current_level'])
    op.create_index('ix_user_xp_total', 'gamification_user_xp', ['total_xp'])
    
    # Create gamification_user_badges table
    op.create_table(
        'gamification_user_badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('progress', sa.Float(), nullable=True, default=0.0),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['badge_id'], ['gamification_badges.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_badges_user', 'gamification_user_badges', ['user_id'])
    op.create_index('ix_user_badges_earned', 'gamification_user_badges', ['earned_at'])
    op.create_unique_constraint('uq_user_badge', 'gamification_user_badges', ['user_id', 'badge_id'])
    
    # Create gamification_point_transactions table
    op.create_table(
        'gamification_point_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_xp_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.Enum('login', 'complete_test', 'perfect_score', 'streak_bonus', 'social_interaction', 'program_completion', 'challenge_completion', 'badge_earned', 'referral', 'milestone', name='pointactivitytype'), nullable=False),
        sa.Column('points_earned', sa.Integer(), nullable=False),
        sa.Column('multiplier_applied', sa.Float(), nullable=True, default=1.0),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_xp_id'], ['gamification_user_xp.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transactions_user_xp', 'gamification_point_transactions', ['user_xp_id'])
    op.create_index('ix_transactions_activity', 'gamification_point_transactions', ['activity_type'])
    op.create_index('ix_transactions_created', 'gamification_point_transactions', ['created_at'])
    
    # Create gamification_leaderboards table
    op.create_table(
        'gamification_leaderboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('global', 'class', 'weekly', 'monthly', 'seasonal', name='leaderboardtype'), nullable=False),
        sa.Column('metric', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('max_entries', sa.Integer(), nullable=True, default=100),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leaderboards_type', 'gamification_leaderboards', ['type'])
    op.create_index('ix_leaderboards_active', 'gamification_leaderboards', ['is_active'])
    op.create_index('ix_leaderboards_tenant', 'gamification_leaderboards', ['tenant_id'])
    
    # Create gamification_leaderboard_entries table
    op.create_table(
        'gamification_leaderboard_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('leaderboard_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['leaderboard_id'], ['gamification_leaderboards.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_entries_leaderboard', 'gamification_leaderboard_entries', ['leaderboard_id'])
    op.create_index('ix_entries_position', 'gamification_leaderboard_entries', ['position'])
    op.create_unique_constraint('uq_leaderboard_user', 'gamification_leaderboard_entries', ['leaderboard_id', 'user_id'])
    
    # Create gamification_teams table
    op.create_table(
        'gamification_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leader_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('max_members', sa.Integer(), nullable=True, default=10),
        sa.Column('is_open', sa.Boolean(), nullable=True, default=True),
        sa.Column('total_xp', sa.Integer(), nullable=True, default=0),
        sa.Column('challenges_completed', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['leader_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teams_leader', 'gamification_teams', ['leader_id'])
    op.create_index('ix_teams_tenant', 'gamification_teams', ['tenant_id'])
    op.create_index('ix_teams_open', 'gamification_teams', ['is_open'])
    
    # Create team_members association table
    op.create_table(
        'team_members',
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('role', sa.String(length=20), nullable=True, default='member'),
        sa.ForeignKeyConstraint(['team_id'], ['gamification_teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('team_id', 'user_id')
    )
    
    # Create gamification_challenges table
    op.create_table(
        'gamification_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('type', sa.Enum('individual', 'team', 'global', 'daily', 'weekly', 'special_event', name='challengetype'), nullable=False),
        sa.Column('goals', sa.JSON(), nullable=False),
        sa.Column('rewards', sa.JSON(), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True, default='medium'),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('min_participants', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_challenges_type', 'gamification_challenges', ['type'])
    op.create_index('ix_challenges_active', 'gamification_challenges', ['is_active'])
    op.create_index('ix_challenges_featured', 'gamification_challenges', ['is_featured'])
    op.create_index('ix_challenges_dates', 'gamification_challenges', ['start_date', 'end_date'])
    
    # Create gamification_challenge_participants table
    op.create_table(
        'gamification_challenge_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('progress', sa.JSON(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True, default=0.0),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['challenge_id'], ['gamification_challenges.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['gamification_teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_participants_challenge', 'gamification_challenge_participants', ['challenge_id'])
    op.create_index('ix_participants_user', 'gamification_challenge_participants', ['user_id'])
    op.create_index('ix_participants_completed', 'gamification_challenge_participants', ['is_completed'])
    op.create_unique_constraint('uq_challenge_user', 'gamification_challenge_participants', ['challenge_id', 'user_id'])
    
    # Create gamification_rewards table
    op.create_table(
        'gamification_rewards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('virtual_item', 'unlockable_content', 'certification', 'real_world', 'points', 'badge', name='rewardtype'), nullable=False),
        sa.Column('cost', sa.Integer(), nullable=True, default=0),
        sa.Column('value', sa.JSON(), nullable=True),
        sa.Column('rarity', sa.String(length=20), nullable=True, default='common'),
        sa.Column('total_quantity', sa.Integer(), nullable=True),
        sa.Column('remaining_quantity', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('available_from', sa.DateTime(), nullable=True),
        sa.Column('available_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rewards_type', 'gamification_rewards', ['type'])
    op.create_index('ix_rewards_cost', 'gamification_rewards', ['cost'])
    op.create_index('ix_rewards_active', 'gamification_rewards', ['is_active'])
    op.create_index('ix_rewards_availability', 'gamification_rewards', ['available_from', 'available_until'])
    
    # Create gamification_reward_redemptions table
    op.create_table(
        'gamification_reward_redemptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reward_id', sa.Integer(), nullable=False),
        sa.Column('points_spent', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.Column('delivery_info', sa.JSON(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['reward_id'], ['gamification_rewards.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_redemptions_user', 'gamification_reward_redemptions', ['user_id'])
    op.create_index('ix_redemptions_status', 'gamification_reward_redemptions', ['status'])
    op.create_index('ix_redemptions_created', 'gamification_reward_redemptions', ['created_at'])
    
    # Create gamification_user_goals table
    op.create_table(
        'gamification_user_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal_type', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=True, default=0.0),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_goals_user', 'gamification_user_goals', ['user_id'])
    op.create_index('ix_goals_type', 'gamification_user_goals', ['goal_type'])
    op.create_index('ix_goals_active', 'gamification_user_goals', ['is_active'])
    op.create_index('ix_goals_completed', 'gamification_user_goals', ['is_completed'])
    
    # Create gamification_events table
    op.create_table(
        'gamification_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_user', 'gamification_events', ['user_id'])
    op.create_index('ix_events_type', 'gamification_events', ['event_type'])
    op.create_index('ix_events_session', 'gamification_events', ['session_id'])
    op.create_index('ix_events_created', 'gamification_events', ['created_at'])
    
    # Create gamification_user_progress table
    op.create_table(
        'gamification_user_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('milestones_reached', sa.JSON(), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True, default=0),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_progress_user', 'gamification_user_progress', ['user_id'])
    op.create_index('ix_progress_category', 'gamification_user_progress', ['category'])
    op.create_index('ix_progress_entity', 'gamification_user_progress', ['entity_id'])
    op.create_unique_constraint('uq_user_progress', 'gamification_user_progress', ['user_id', 'category', 'entity_id'])
    
    # Create user_friends association table
    op.create_table(
        'user_friends',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('friend_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.ForeignKeyConstraint(['friend_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'friend_id')
    )
    op.create_index('ix_friends_status', 'user_friends', ['status'])


def downgrade():
    """Remove gamification tables."""
    
    # Drop all tables in reverse order
    op.drop_table('user_friends')
    op.drop_table('gamification_user_progress')
    op.drop_table('gamification_events')
    op.drop_table('gamification_user_goals')
    op.drop_table('gamification_reward_redemptions')
    op.drop_table('gamification_rewards')
    op.drop_table('gamification_challenge_participants')
    op.drop_table('gamification_challenges')
    op.drop_table('team_members')
    op.drop_table('gamification_teams')
    op.drop_table('gamification_leaderboard_entries')
    op.drop_table('gamification_leaderboards')
    op.drop_table('gamification_point_transactions')
    op.drop_table('gamification_user_badges')
    op.drop_table('gamification_user_xp')
    op.drop_table('gamification_badges')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS challengetype')
    op.execute('DROP TYPE IF EXISTS rewardtype')
    op.execute('DROP TYPE IF EXISTS leaderboardtype')
    op.execute('DROP TYPE IF EXISTS pointactivitytype')
    op.execute('DROP TYPE IF EXISTS achievementcategory')