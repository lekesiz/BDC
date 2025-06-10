"""
Gamification Manager

Central orchestrator for all gamification features.
Coordinates between different gamification services and handles complex workflows.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from contextlib import contextmanager

from .achievement_service import AchievementService
from .badge_service import BadgeService
from .xp_service import XPService
from .level_service import LevelService
from .progress_service import ProgressService
from .leaderboard_service import LeaderboardService
from .social_service import SocialService
from .learning_path_service import LearningPathService

from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GamificationManager(BaseService):
    """Central manager for all gamification features"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        
        # Initialize all gamification services
        self.achievement_service = AchievementService(db)
        self.badge_service = BadgeService(db)
        self.xp_service = XPService(db)
        self.level_service = LevelService(db)
        self.progress_service = ProgressService(db)
        self.leaderboard_service = LeaderboardService(db)
        self.social_service = SocialService(db)
        self.learning_path_service = LearningPathService(db)
        
        # Event handlers for gamification triggers
        self.event_handlers = {
            'evaluation_completed': self.handle_evaluation_completed,
            'program_completed': self.handle_program_completed,
            'daily_login': self.handle_daily_login,
            'perfect_score': self.handle_perfect_score,
            'first_evaluation': self.handle_first_evaluation,
            'streak_milestone': self.handle_streak_milestone,
            'social_interaction': self.handle_social_interaction,
            'learning_path_node_completed': self.handle_learning_path_node_completed,
            'team_challenge_completed': self.handle_team_challenge_completed
        }
    
    def trigger_event(self, event_type: str, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for triggering gamification events"""
        try:
            logger.info(f"Triggering gamification event: {event_type} for user {user_id}")
            
            if event_type not in self.event_handlers:
                logger.warning(f"No handler for event type: {event_type}")
                return {'success': False, 'error': 'Unknown event type'}
            
            handler = self.event_handlers[event_type]
            result = handler(user_id, event_data)
            
            # Update leaderboards if significant changes occurred
            if result.get('level_changed') or result.get('xp_awarded', 0) > 0:
                self._update_relevant_leaderboards(user_id)
            
            logger.info(f"Gamification event processed successfully: {event_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing gamification event {event_type}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_user_gamification_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive gamification summary for a user"""
        try:
            # Get data from all services
            xp_stats = self.xp_service.get_xp_statistics(user_id)
            level_progress = self.level_service.get_level_progress(user_id)
            user_badges = self.badge_service.get_user_badges(user_id)
            badge_showcase = self.badge_service.get_badge_showcase(user_id)
            user_achievements = self.achievement_service.get_user_achievements(user_id)
            progress_dashboard = self.progress_service.get_progress_dashboard(user_id)
            user_rankings = self.leaderboard_service.get_user_rankings(user_id)
            user_teams = self.social_service.get_user_teams(user_id)
            learning_paths = self.learning_path_service.get_user_learning_paths(user_id)
            
            # Calculate overall gamification score
            overall_score = self._calculate_overall_gamification_score(
                xp_stats, level_progress, len(user_badges), len(user_achievements)
            )
            
            return {
                'user_id': user_id,
                'overall_score': overall_score,
                'xp': {
                    'total': xp_stats.get('total_xp', 0),
                    'this_week': xp_stats.get('week_xp', 0),
                    'today': xp_stats.get('today_xp', 0),
                    'current_streak': xp_stats.get('current_streak', 0)
                },
                'level': {
                    'current': level_progress.get('current_level', 1),
                    'progress_percentage': level_progress.get('progress_percentage', 0),
                    'title': level_progress.get('title', {}),
                    'xp_needed_for_next': level_progress.get('xp_needed_for_next', 0)
                },
                'badges': {
                    'total_count': len(user_badges),
                    'showcase': badge_showcase,
                    'recent': user_badges[:5] if user_badges else []
                },
                'achievements': {
                    'total_count': len(user_achievements),
                    'recent': user_achievements[:5] if user_achievements else []
                },
                'progress': {
                    'overall_progress': progress_dashboard.get('overall_progress', {}),
                    'recent_milestones': progress_dashboard.get('recent_milestones', [])
                },
                'rankings': user_rankings.get('rankings', {}),
                'social': {
                    'teams_count': len(user_teams),
                    'teams': user_teams
                },
                'learning_paths': {
                    'active_count': len([p for p in learning_paths if p.get('status') == 'in_progress']),
                    'completed_count': len([p for p in learning_paths if p.get('status') == 'completed']),
                    'paths': learning_paths[:3]  # Show top 3
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user gamification summary: {str(e)}")
            return {}
    
    def get_gamification_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get gamification dashboard data optimized for UI display"""
        try:
            summary = self.get_user_gamification_summary(user_id)
            
            # Get recommendations
            recommended_paths = self.learning_path_service.get_recommended_paths(user_id, 3)
            available_achievements = self.achievement_service.get_available_achievements(user_id)
            available_badges = self.badge_service.get_available_badges(user_id)
            
            # Get social feed
            social_feed = self.social_service.get_social_feed(user_id, limit=10)
            
            # Get active competitions
            active_competitions = self.leaderboard_service.get_active_competitions(user_id)
            
            # Get global leaderboards for context
            global_leaderboards = self.leaderboard_service.get_global_leaderboards(5)
            
            return {
                'summary': summary,
                'recommendations': {
                    'learning_paths': recommended_paths,
                    'achievements': available_achievements[:5],
                    'badges': available_badges[:5]
                },
                'social': {
                    'feed': social_feed,
                    'competitions': active_competitions
                },
                'leaderboards': global_leaderboards,
                'quick_stats': {
                    'rank_improvements': self._get_recent_rank_improvements(user_id),
                    'streak_status': self._get_streak_status(user_id),
                    'upcoming_milestones': self._get_upcoming_milestones(user_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting gamification dashboard: {str(e)}")
            return {}
    
    def create_gamification_challenge(self, challenge_data: Dict[str, Any], creator_id: int) -> Dict[str, Any]:
        """Create a comprehensive gamification challenge"""
        try:
            challenge_type = challenge_data.get('type', 'individual')
            
            if challenge_type == 'team':
                # Create team challenge
                team_challenge = self.social_service.create_team_challenge(challenge_data, creator_id)
                return {'type': 'team_challenge', 'id': team_challenge.id, 'challenge': team_challenge}
            
            elif challenge_type == 'learning_path':
                # Create learning path challenge
                learning_path = self.learning_path_service.create_learning_path(challenge_data, creator_id)
                return {'type': 'learning_path', 'id': learning_path.id, 'challenge': learning_path}
            
            elif challenge_type == 'achievement':
                # Create achievement challenge
                achievement = self.achievement_service.create_achievement(challenge_data)
                return {'type': 'achievement', 'id': achievement.id, 'challenge': achievement}
            
            else:
                return {'success': False, 'error': 'Unknown challenge type'}
                
        except Exception as e:
            logger.error(f"Error creating gamification challenge: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def bulk_award_rewards(self, rewards_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Award multiple rewards in a single transaction"""
        try:
            awarded_rewards = []
            
            with self._transaction():
                for reward in rewards_data:
                    user_id = reward['user_id']
                    reward_type = reward['type']
                    
                    if reward_type == 'xp':
                        transaction = self.xp_service.award_xp(
                            user_id=user_id,
                            source=reward.get('source', 'bulk_award'),
                            base_amount=reward['amount'],
                            metadata=reward.get('metadata', {})
                        )
                        awarded_rewards.append({
                            'user_id': user_id,
                            'type': 'xp',
                            'amount': reward['amount'],
                            'transaction_id': transaction.id
                        })
                    
                    elif reward_type == 'badge':
                        user_badge = self.badge_service.award_badge(
                            user_id=user_id,
                            badge_id=reward['badge_id'],
                            metadata=reward.get('metadata', {})
                        )
                        awarded_rewards.append({
                            'user_id': user_id,
                            'type': 'badge',
                            'badge_id': reward['badge_id'],
                            'user_badge_id': user_badge.id
                        })
                    
                    elif reward_type == 'achievement':
                        user_achievement = self.achievement_service.award_achievement(
                            user_id=user_id,
                            achievement_id=reward['achievement_id'],
                            progress_data=reward.get('progress_data', {})
                        )
                        awarded_rewards.append({
                            'user_id': user_id,
                            'type': 'achievement',
                            'achievement_id': reward['achievement_id'],
                            'user_achievement_id': user_achievement.id
                        })
            
            return {'success': True, 'awarded_rewards': awarded_rewards}
            
        except Exception as e:
            logger.error(f"Error in bulk reward awarding: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Event Handlers
    
    def handle_evaluation_completed(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle evaluation completion event"""
        try:
            score = event_data.get('score', 0)
            evaluation_id = event_data.get('evaluation_id')
            program_id = event_data.get('program_id')
            
            results = {'success': True, 'rewards': []}
            
            # Award base XP for completion
            xp_transaction = self.xp_service.award_activity_xp(
                user_id=user_id,
                activity='evaluation_completed',
                metadata=event_data,
                reference_id=evaluation_id,
                reference_type='evaluation'
            )
            
            if xp_transaction:
                results['rewards'].append({
                    'type': 'xp',
                    'amount': xp_transaction.amount,
                    'source': 'evaluation_completed'
                })
            
            # Award bonus XP for perfect score
            if score == 100:
                bonus_xp = self.xp_service.award_activity_xp(
                    user_id=user_id,
                    activity='evaluation_perfect_score',
                    metadata=event_data,
                    reference_id=evaluation_id,
                    reference_type='evaluation'
                )
                
                if bonus_xp:
                    results['rewards'].append({
                        'type': 'xp',
                        'amount': bonus_xp.amount,
                        'source': 'perfect_score'
                    })
            
            # Check level progression
            level_result = self.level_service.update_user_level(user_id)
            if level_result and level_result.get('level_up'):
                results['level_up'] = level_result
                results['level_changed'] = True
                
                # Award level up rewards
                level_rewards = level_result.get('rewards', [])
                for reward in level_rewards:
                    if reward['type'] == 'badge':
                        badge = self.badge_service.create_badge_from_template(reward['name'])
                        self.badge_service.award_badge(user_id, badge.id)
                        results['rewards'].append({
                            'type': 'badge',
                            'badge_id': badge.id,
                            'name': reward['name']
                        })
            
            # Check achievements
            achievements = self.achievement_service.check_achievements_for_user(
                user_id, 'evaluation_completed', event_data
            )
            
            for achievement in achievements:
                results['rewards'].append({
                    'type': 'achievement',
                    'achievement_id': achievement.achievement_id,
                    'name': achievement.achievement.name
                })
            
            # Update progress trackers
            progress_achievements = self.progress_service.update_progress(
                user_id, 'EVALUATION_PERFORMANCE', event_data
            )
            
            results['progress_achievements'] = progress_achievements
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling evaluation completed event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_program_completed(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle program completion event"""
        try:
            program_id = event_data.get('program_id')
            
            results = {'success': True, 'rewards': []}
            
            # Award significant XP for program completion
            xp_transaction = self.xp_service.award_activity_xp(
                user_id=user_id,
                activity='program_completed',
                metadata=event_data,
                reference_id=program_id,
                reference_type='program'
            )
            
            if xp_transaction:
                results['rewards'].append({
                    'type': 'xp',
                    'amount': xp_transaction.amount,
                    'source': 'program_completed'
                })
            
            # Award program completion badge
            badge = self.badge_service.create_badge_from_template('PROGRAM_MASTER')
            user_badge = self.badge_service.award_badge(user_id, badge.id)
            
            results['rewards'].append({
                'type': 'badge',
                'badge_id': badge.id,
                'name': 'Program Master'
            })
            
            # Check level progression
            level_result = self.level_service.update_user_level(user_id)
            if level_result and level_result.get('level_up'):
                results['level_up'] = level_result
                results['level_changed'] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling program completed event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_daily_login(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle daily login event"""
        try:
            results = {'success': True, 'rewards': []}
            
            # Award daily login XP
            xp_transaction = self.xp_service.award_activity_xp(
                user_id=user_id,
                activity='daily_login',
                metadata=event_data
            )
            
            if xp_transaction:
                results['rewards'].append({
                    'type': 'xp',
                    'amount': xp_transaction.amount,
                    'source': 'daily_login'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling daily login event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_perfect_score(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle perfect score achievement event"""
        try:
            results = {'success': True, 'rewards': []}
            
            # Award perfectionist badge if it's their first perfect score
            existing_badge = self.badge_service.get_user_badges(user_id, 'achievement')
            perfectionist_earned = any(b['badge']['name'] == 'Perfectionist' for b in existing_badge)
            
            if not perfectionist_earned:
                badge = self.badge_service.create_badge_from_template('PERFECTIONIST')
                self.badge_service.award_badge(user_id, badge.id)
                
                results['rewards'].append({
                    'type': 'badge',
                    'badge_id': badge.id,
                    'name': 'Perfectionist'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling perfect score event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_first_evaluation(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle first evaluation completion event"""
        try:
            results = {'success': True, 'rewards': []}
            
            # Award first steps badge
            badge = self.badge_service.create_badge_from_template('FIRST_STEPS')
            self.badge_service.award_badge(user_id, badge.id)
            
            results['rewards'].append({
                'type': 'badge',
                'badge_id': badge.id,
                'name': 'First Steps'
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling first evaluation event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_streak_milestone(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle streak milestone event"""
        try:
            streak_days = event_data.get('streak_days', 0)
            results = {'success': True, 'rewards': []}
            
            if streak_days >= 7:
                badge = self.badge_service.create_badge_from_template('STREAK_MASTER')
                self.badge_service.award_badge(user_id, badge.id)
                
                results['rewards'].append({
                    'type': 'badge',
                    'badge_id': badge.id,
                    'name': 'Streak Master'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling streak milestone event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_social_interaction(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle social interaction event"""
        try:
            results = {'success': True, 'rewards': []}
            
            # Award social interaction XP
            xp_transaction = self.xp_service.award_activity_xp(
                user_id=user_id,
                activity='social_interaction',
                metadata=event_data
            )
            
            if xp_transaction:
                results['rewards'].append({
                    'type': 'xp',
                    'amount': xp_transaction.amount,
                    'source': 'social_interaction'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling social interaction event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_learning_path_node_completed(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle learning path node completion event"""
        try:
            path_id = event_data.get('path_id')
            node_id = event_data.get('node_id')
            
            results = {'success': True, 'rewards': []}
            
            # Complete the node and get rewards
            completion_result = self.learning_path_service.complete_node(
                user_id, path_id, node_id, event_data
            )
            
            if completion_result.get('success'):
                if completion_result.get('xp_awarded', 0) > 0:
                    results['rewards'].append({
                        'type': 'xp',
                        'amount': completion_result['xp_awarded'],
                        'source': 'learning_path_node'
                    })
                
                if completion_result.get('path_completed'):
                    # Award path completion badge
                    badge = self.badge_service.create_badge_from_template('KNOWLEDGE_SEEKER')
                    self.badge_service.award_badge(user_id, badge.id)
                    
                    results['rewards'].append({
                        'type': 'badge',
                        'badge_id': badge.id,
                        'name': 'Knowledge Seeker'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling learning path node completed event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_team_challenge_completed(self, user_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle team challenge completion event"""
        try:
            results = {'success': True, 'rewards': []}
            
            # Award team participation XP
            xp_transaction = self.xp_service.award_activity_xp(
                user_id=user_id,
                activity='participation',
                metadata=event_data
            )
            
            if xp_transaction:
                results['rewards'].append({
                    'type': 'xp',
                    'amount': xp_transaction.amount,
                    'source': 'team_challenge'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error handling team challenge completed event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Helper Methods
    
    def _update_relevant_leaderboards(self, user_id: int):
        """Update leaderboards that might be affected by user's actions"""
        try:
            # This would identify and update relevant leaderboards
            # For now, just logging
            logger.info(f"Updating leaderboards for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating leaderboards: {str(e)}")
    
    def _calculate_overall_gamification_score(self, xp_stats: Dict, level_progress: Dict,
                                            badges_count: int, achievements_count: int) -> float:
        """Calculate overall gamification engagement score"""
        try:
            # Weight different components
            xp_score = min(100, (xp_stats.get('total_xp', 0) / 10000) * 100)
            level_score = min(100, (level_progress.get('current_level', 1) / 50) * 100)
            badge_score = min(100, (badges_count / 20) * 100)
            achievement_score = min(100, (achievements_count / 15) * 100)
            
            # Weighted average
            overall_score = (
                xp_score * 0.4 +
                level_score * 0.3 +
                badge_score * 0.2 +
                achievement_score * 0.1
            )
            
            return round(overall_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating overall gamification score: {str(e)}")
            return 0.0
    
    def _get_recent_rank_improvements(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recent rank improvements for user"""
        # This would track rank changes over time
        return []
    
    def _get_streak_status(self, user_id: int) -> Dict[str, Any]:
        """Get current streak status"""
        xp_stats = self.xp_service.get_xp_statistics(user_id)
        return {
            'current_streak': xp_stats.get('current_streak', 0),
            'best_streak': 0,  # Would track historically
            'streak_risk': False  # Would check if streak is at risk
        }
    
    def _get_upcoming_milestones(self, user_id: int) -> List[Dict[str, Any]]:
        """Get upcoming milestones for user"""
        # This would identify next achievable milestones
        return []
    
    @contextmanager
    def _transaction(self):
        """Context manager for database transactions"""
        try:
            yield
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise