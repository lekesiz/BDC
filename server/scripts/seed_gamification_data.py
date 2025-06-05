#!/usr/bin/env python3
"""Seed initial gamification data for the BDC application."""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db
from app.models.gamification import (
    Badge, Leaderboard, Challenge, Reward, AchievementCategory, 
    LeaderboardType, ChallengeType, RewardType
)


def create_initial_badges():
    """Create initial set of badges."""
    badges_data = [
        # Learning Badges
        {
            'name': 'First Steps',
            'description': 'Complete your first evaluation',
            'category': AchievementCategory.LEARNING,
            'rarity': 'common',
            'points_value': 50,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'evaluation',
                'count': 1
            },
            'icon_url': '/static/badges/first_steps.png'
        },
        {
            'name': 'Evaluation Expert',
            'description': 'Complete 10 evaluations',
            'category': AchievementCategory.LEARNING,
            'rarity': 'uncommon',
            'points_value': 200,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'evaluation',
                'count': 10
            },
            'icon_url': '/static/badges/evaluation_expert.png'
        },
        {
            'name': 'Perfect Score',
            'description': 'Achieve a perfect score on an evaluation',
            'category': AchievementCategory.MASTERY,
            'rarity': 'rare',
            'points_value': 500,
            'unlock_conditions': {
                'type': 'score_threshold',
                'threshold': 100.0
            },
            'icon_url': '/static/badges/perfect_score.png'
        },
        {
            'name': 'High Achiever',
            'description': 'Score above 90% on 5 evaluations',
            'category': AchievementCategory.MASTERY,
            'rarity': 'rare',
            'points_value': 300,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'high_score',
                'count': 5,
                'threshold': 90.0
            },
            'icon_url': '/static/badges/high_achiever.png'
        },
        
        # Participation Badges
        {
            'name': 'Active Learner',
            'description': 'Log in for 7 consecutive days',
            'category': AchievementCategory.CONSISTENCY,
            'rarity': 'uncommon',
            'points_value': 150,
            'unlock_conditions': {
                'type': 'streak',
                'streak': 7
            },
            'icon_url': '/static/badges/active_learner.png'
        },
        {
            'name': 'Dedicated Student',
            'description': 'Log in for 30 consecutive days',
            'category': AchievementCategory.CONSISTENCY,
            'rarity': 'epic',
            'points_value': 1000,
            'unlock_conditions': {
                'type': 'streak',
                'streak': 30
            },
            'icon_url': '/static/badges/dedicated_student.png'
        },
        {
            'name': 'Program Graduate',
            'description': 'Complete your first program',
            'category': AchievementCategory.PARTICIPATION,
            'rarity': 'uncommon',
            'points_value': 300,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'program',
                'count': 1
            },
            'icon_url': '/static/badges/program_graduate.png'
        },
        
        # Social Badges
        {
            'name': 'Team Player',
            'description': 'Join your first team',
            'category': AchievementCategory.SOCIAL,
            'rarity': 'common',
            'points_value': 50,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'team_join',
                'count': 1
            },
            'icon_url': '/static/badges/team_player.png'
        },
        {
            'name': 'Helper',
            'description': 'Provide help to 5 other users',
            'category': AchievementCategory.SOCIAL,
            'rarity': 'uncommon',
            'points_value': 200,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'help_provided',
                'count': 5
            },
            'icon_url': '/static/badges/helper.png'
        },
        
        # Level Badges
        {
            'name': 'Rising Star',
            'description': 'Reach level 5',
            'category': AchievementCategory.MASTERY,
            'rarity': 'common',
            'points_value': 100,
            'unlock_conditions': {
                'type': 'level',
                'level': 5
            },
            'icon_url': '/static/badges/rising_star.png'
        },
        {
            'name': 'Expert Learner',
            'description': 'Reach level 10',
            'category': AchievementCategory.MASTERY,
            'rarity': 'uncommon',
            'points_value': 250,
            'unlock_conditions': {
                'type': 'level',
                'level': 10
            },
            'icon_url': '/static/badges/expert_learner.png'
        },
        {
            'name': 'Master Student',
            'description': 'Reach level 25',
            'category': AchievementCategory.MASTERY,
            'rarity': 'epic',
            'points_value': 1000,
            'unlock_conditions': {
                'type': 'level',
                'level': 25
            },
            'icon_url': '/static/badges/master_student.png'
        },
        
        # Special Badges
        {
            'name': 'Early Adopter',
            'description': 'One of the first 100 users',
            'category': AchievementCategory.SPECIAL,
            'rarity': 'legendary',
            'points_value': 2000,
            'unlock_conditions': {
                'type': 'special',
                'key': 'early_adopter'
            },
            'icon_url': '/static/badges/early_adopter.png',
            'is_secret': True
        },
        {
            'name': 'Challenge Champion',
            'description': 'Complete 10 challenges',
            'category': AchievementCategory.PARTICIPATION,
            'rarity': 'rare',
            'points_value': 500,
            'unlock_conditions': {
                'type': 'count',
                'entity_type': 'challenge_completion',
                'count': 10
            },
            'icon_url': '/static/badges/challenge_champion.png'
        }
    ]
    
    for badge_data in badges_data:
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    print(f"Created {len(badges_data)} badges")


def create_initial_leaderboards():
    """Create initial leaderboards."""
    leaderboards_data = [
        {
            'name': 'Global XP Leaders',
            'description': 'Top learners by total experience points',
            'type': LeaderboardType.GLOBAL,
            'metric': 'total_xp',
            'max_entries': 100
        },
        {
            'name': 'Level Leaders',
            'description': 'Highest level achievers',
            'type': LeaderboardType.GLOBAL,
            'metric': 'level',
            'max_entries': 50
        },
        {
            'name': 'Streak Masters',
            'description': 'Longest current streaks',
            'type': LeaderboardType.GLOBAL,
            'metric': 'current_streak',
            'max_entries': 50
        },
        {
            'name': 'Weekly Champions',
            'description': 'Top performers this week',
            'type': LeaderboardType.WEEKLY,
            'metric': 'total_xp',
            'start_date': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=datetime.utcnow().weekday()),
            'end_date': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=datetime.utcnow().weekday()) + timedelta(days=7),
            'max_entries': 25
        },
        {
            'name': 'Monthly Stars',
            'description': 'Top performers this month',
            'type': LeaderboardType.MONTHLY,
            'metric': 'total_xp',
            'start_date': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            'end_date': (datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
            'max_entries': 25
        }
    ]
    
    for leaderboard_data in leaderboards_data:
        existing = Leaderboard.query.filter_by(name=leaderboard_data['name']).first()
        if not existing:
            leaderboard = Leaderboard(**leaderboard_data)
            db.session.add(leaderboard)
    
    print(f"Created {len(leaderboards_data)} leaderboards")


def create_initial_challenges():
    """Create initial challenges."""
    challenges_data = [
        {
            'title': 'First Week Challenge',
            'description': 'Complete 3 evaluations in your first week',
            'type': ChallengeType.INDIVIDUAL,
            'goals': {
                'evaluations': {
                    'type': 'evaluation_count',
                    'target': 3,
                    'description': 'Complete 3 evaluations'
                }
            },
            'rewards': {
                'points': 200,
                'badge_id': None  # Could link to a specific badge
            },
            'difficulty': 'easy',
            'duration_hours': 168,  # 1 week
            'is_featured': True
        },
        {
            'title': 'Perfect Score Hunt',
            'description': 'Achieve a perfect score on any evaluation',
            'type': ChallengeType.INDIVIDUAL,
            'goals': {
                'perfect_score': {
                    'type': 'perfect_score',
                    'target': 1,
                    'description': 'Get 100% on an evaluation'
                }
            },
            'rewards': {
                'points': 500
            },
            'difficulty': 'hard'
        },
        {
            'title': 'Daily Dedication',
            'description': 'Log in every day for a week',
            'type': ChallengeType.INDIVIDUAL,
            'goals': {
                'daily_login': {
                    'type': 'streak',
                    'target': 7,
                    'description': 'Log in 7 days in a row'
                }
            },
            'rewards': {
                'points': 300
            },
            'difficulty': 'medium',
            'duration_hours': 168  # 1 week
        },
        {
            'title': 'Team Learning Sprint',
            'description': 'Team challenge: Complete 50 evaluations together',
            'type': ChallengeType.TEAM,
            'goals': {
                'team_evaluations': {
                    'type': 'team_evaluation_count',
                    'target': 50,
                    'description': 'Complete 50 evaluations as a team'
                }
            },
            'rewards': {
                'points': 1000
            },
            'difficulty': 'expert',
            'min_participants': 3,
            'max_participants': 10,
            'duration_hours': 336  # 2 weeks
        },
        {
            'title': 'Monthly Mastery',
            'description': 'Complete a full program this month',
            'type': ChallengeType.INDIVIDUAL,
            'goals': {
                'program_completion': {
                    'type': 'program_completion',
                    'target': 1,
                    'description': 'Complete any program'
                }
            },
            'rewards': {
                'points': 750
            },
            'difficulty': 'hard',
            'duration_hours': 720,  # 30 days
            'is_featured': True
        }
    ]
    
    for challenge_data in challenges_data:
        existing = Challenge.query.filter_by(title=challenge_data['title']).first()
        if not existing:
            challenge = Challenge(**challenge_data)
            db.session.add(challenge)
    
    print(f"Created {len(challenges_data)} challenges")


def create_initial_rewards():
    """Create initial rewards."""
    rewards_data = [
        {
            'name': 'Certificate of Achievement',
            'description': 'Digital certificate for completing challenges',
            'type': RewardType.CERTIFICATION,
            'cost': 500,
            'value': {
                'certificate_type': 'achievement',
                'template': 'standard'
            },
            'rarity': 'common'
        },
        {
            'name': 'Profile Badge Slot',
            'description': 'Unlock an additional badge display slot',
            'type': RewardType.UNLOCKABLE_CONTENT,
            'cost': 200,
            'value': {
                'feature': 'badge_slot',
                'quantity': 1
            },
            'rarity': 'uncommon',
            'total_quantity': 100
        },
        {
            'name': 'Custom Avatar Frame',
            'description': 'Exclusive avatar frame for your profile',
            'type': RewardType.VIRTUAL_ITEM,
            'cost': 300,
            'value': {
                'item_type': 'avatar_frame',
                'design': 'golden_star'
            },
            'rarity': 'rare',
            'total_quantity': 50
        },
        {
            'name': 'XP Booster (24h)',
            'description': '2x XP multiplier for 24 hours',
            'type': RewardType.VIRTUAL_ITEM,
            'cost': 400,
            'value': {
                'multiplier': 2.0,
                'duration_hours': 24
            },
            'rarity': 'uncommon',
            'total_quantity': 200
        },
        {
            'name': 'Learning Path Access',
            'description': 'Access to premium learning content',
            'type': RewardType.UNLOCKABLE_CONTENT,
            'cost': 1000,
            'value': {
                'feature': 'premium_content',
                'duration_days': 30
            },
            'rarity': 'epic',
            'total_quantity': 25
        },
        {
            'name': 'Mentor Session',
            'description': 'One-on-one session with a learning mentor',
            'type': RewardType.REAL_WORLD,
            'cost': 2000,
            'value': {
                'service': 'mentor_session',
                'duration_minutes': 60
            },
            'rarity': 'legendary',
            'total_quantity': 10
        },
        {
            'name': 'Point Bonus',
            'description': 'Instant 100 bonus points',
            'type': RewardType.POINTS,
            'cost': 50,
            'value': {
                'points': 100
            },
            'rarity': 'common'
        }
    ]
    
    for reward_data in rewards_data:
        existing = Reward.query.filter_by(name=reward_data['name']).first()
        if not existing:
            reward_data['remaining_quantity'] = reward_data.get('total_quantity')
            reward = Reward(**reward_data)
            db.session.add(reward)
    
    print(f"Created {len(rewards_data)} rewards")


def main():
    """Main function to seed gamification data."""
    app = create_app()
    
    with app.app_context():
        print("Seeding gamification data...")
        
        try:
            # Create initial data
            create_initial_badges()
            create_initial_leaderboards()
            create_initial_challenges()
            create_initial_rewards()
            
            # Commit all changes
            db.session.commit()
            print("✅ Gamification data seeded successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding gamification data: {str(e)}")
            return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)