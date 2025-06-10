"""
Progress Service

Manages progress tracking, milestone detection, and reward distribution.
Handles different types of progress: learning paths, skill development, 
program completion, and custom objectives.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from decimal import Decimal
import json

from app.models.gamification import Progress, Milestone, UserMilestone, ProgressGoal
from app.models.user import User
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProgressService(BaseService):
    """Service for tracking progress and managing milestones"""
    
    # Progress types and their tracking methods
    PROGRESS_TYPES = {
        'PROGRAM_COMPLETION': 'track_program_completion',
        'SKILL_DEVELOPMENT': 'track_skill_development',
        'EVALUATION_PERFORMANCE': 'track_evaluation_performance',
        'LEARNING_STREAK': 'track_learning_streak',
        'PARTICIPATION': 'track_participation',
        'SOCIAL_ENGAGEMENT': 'track_social_engagement',
        'CUSTOM_OBJECTIVE': 'track_custom_objective'
    }
    
    # Milestone templates
    MILESTONE_TEMPLATES = {
        'FIRST_COMPLETION': {
            'name': 'First Steps',
            'description': 'Complete your first evaluation',
            'type': 'EVALUATION_PERFORMANCE',
            'criteria': {'completed_count': 1},
            'rewards': {'xp': 100, 'badge': 'first_steps'}
        },
        'PERFECT_SCORE': {
            'name': 'Perfectionist',
            'description': 'Score 100% on any evaluation',
            'type': 'EVALUATION_PERFORMANCE',
            'criteria': {'perfect_scores': 1},
            'rewards': {'xp': 200, 'badge': 'perfectionist'}
        },
        'WEEKLY_STREAK': {
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day learning streak',
            'type': 'LEARNING_STREAK',
            'criteria': {'streak_days': 7},
            'rewards': {'xp': 300, 'badge': 'streak_master'}
        },
        'PROGRAM_MASTER': {
            'name': 'Program Master',
            'description': 'Complete an entire program',
            'type': 'PROGRAM_COMPLETION',
            'criteria': {'programs_completed': 1},
            'rewards': {'xp': 500, 'badge': 'program_master', 'title': 'Graduate'}
        },
        'SKILL_EXPERT': {
            'name': 'Skill Expert',
            'description': 'Master a skill (reach 90% proficiency)',
            'type': 'SKILL_DEVELOPMENT',
            'criteria': {'skill_mastery': 90},
            'rewards': {'xp': 400, 'badge': 'skill_expert'}
        }
    }
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_progress_tracker(self, user_id: int, progress_type: str, 
                              target_data: Dict[str, Any], 
                              goal_data: Optional[Dict] = None) -> Progress:
        """Create a new progress tracker for a user"""
        try:
            progress = Progress(
                user_id=user_id,
                progress_type=progress_type,
                target_data=target_data,
                current_value=0,
                target_value=target_data.get('target_value', 100),
                metadata={},
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
            
            # Create associated goal if provided
            if goal_data:
                self.create_progress_goal(progress.id, goal_data)
            
            logger.info(f"Created progress tracker for user {user_id}: {progress_type}")
            return progress
            
        except Exception as e:
            logger.error(f"Error creating progress tracker: {str(e)}")
            self.db.rollback()
            raise
    
    def update_progress(self, user_id: int, progress_type: str, 
                       update_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update progress and check for milestone achievements"""
        try:
            # Get active progress trackers for this user and type
            progress_trackers = self.db.query(Progress).filter_by(
                user_id=user_id,
                progress_type=progress_type,
                is_active=True
            ).all()
            
            achievements = []
            
            for progress in progress_trackers:
                # Update progress based on type
                if progress_type in self.PROGRESS_TYPES:
                    method_name = self.PROGRESS_TYPES[progress_type]
                    if hasattr(self, method_name):
                        method = getattr(self, method_name)
                        milestone_achieved = method(progress, update_data)
                        if milestone_achieved:
                            achievements.append(milestone_achieved)
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")
            return []
    
    def get_user_progress(self, user_id: int, progress_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all progress trackers for a user"""
        try:
            query = self.db.query(Progress).filter_by(user_id=user_id, is_active=True)
            
            if progress_type:
                query = query.filter_by(progress_type=progress_type)
            
            progress_trackers = query.all()
            
            result = []
            for progress in progress_trackers:
                progress_percentage = self._calculate_progress_percentage(progress)
                
                result.append({
                    'id': progress.id,
                    'type': progress.progress_type,
                    'current_value': progress.current_value,
                    'target_value': progress.target_value,
                    'percentage': progress_percentage,
                    'target_data': progress.target_data,
                    'metadata': progress.metadata,
                    'is_completed': progress_percentage >= 100,
                    'created_at': progress.created_at,
                    'updated_at': progress.updated_at
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user progress: {str(e)}")
            return []
    
    def create_milestone(self, milestone_data: Dict[str, Any]) -> Milestone:
        """Create a new milestone"""
        try:
            milestone = Milestone(
                name=milestone_data['name'],
                description=milestone_data['description'],
                category=milestone_data.get('category', 'achievement'),
                criteria=milestone_data['criteria'],
                rewards=milestone_data.get('rewards', {}),
                is_active=milestone_data.get('is_active', True),
                is_repeatable=milestone_data.get('is_repeatable', False),
                cooldown_days=milestone_data.get('cooldown_days', 0),
                created_by=milestone_data.get('created_by')
            )
            
            self.db.add(milestone)
            self.db.commit()
            self.db.refresh(milestone)
            
            logger.info(f"Created milestone: {milestone.name}")
            return milestone
            
        except Exception as e:
            logger.error(f"Error creating milestone: {str(e)}")
            self.db.rollback()
            raise
    
    def create_milestone_from_template(self, template_name: str, 
                                     custom_data: Optional[Dict] = None) -> Milestone:
        """Create a milestone from a predefined template"""
        try:
            if template_name not in self.MILESTONE_TEMPLATES:
                raise ValueError(f"Unknown milestone template: {template_name}")
            
            template = self.MILESTONE_TEMPLATES[template_name].copy()
            
            # Override with custom data if provided
            if custom_data:
                template.update(custom_data)
            
            return self.create_milestone(template)
            
        except Exception as e:
            logger.error(f"Error creating milestone from template: {str(e)}")
            raise
    
    def check_milestones(self, user_id: int, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check and award eligible milestones for a user"""
        try:
            achievements = []
            
            # Get active milestones
            milestones = self.db.query(Milestone).filter_by(is_active=True).all()
            
            for milestone in milestones:
                if self._is_milestone_eligible(user_id, milestone, context_data):
                    achievement = self.award_milestone(user_id, milestone.id, context_data)
                    if achievement:
                        achievements.append(achievement)
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error checking milestones: {str(e)}")
            return []
    
    def award_milestone(self, user_id: int, milestone_id: int, 
                       context_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Award a milestone to a user"""
        try:
            milestone = self.db.query(Milestone).get(milestone_id)
            if not milestone:
                return None
            
            # Check if user already has this milestone (if not repeatable)
            if not milestone.is_repeatable:
                existing = self.db.query(UserMilestone).filter_by(
                    user_id=user_id,
                    milestone_id=milestone_id
                ).first()
                
                if existing:
                    return None
            
            # Check cooldown for repeatable milestones
            if milestone.is_repeatable and milestone.cooldown_days > 0:
                cooldown_date = datetime.utcnow() - timedelta(days=milestone.cooldown_days)
                recent = self.db.query(UserMilestone).filter(
                    UserMilestone.user_id == user_id,
                    UserMilestone.milestone_id == milestone_id,
                    UserMilestone.achieved_at >= cooldown_date
                ).first()
                
                if recent:
                    return None
            
            # Award the milestone
            user_milestone = UserMilestone(
                user_id=user_id,
                milestone_id=milestone_id,
                achieved_at=datetime.utcnow(),
                context_data=context_data or {}
            )
            
            self.db.add(user_milestone)
            self.db.commit()
            self.db.refresh(user_milestone)
            
            # Process rewards
            rewards_granted = self._process_milestone_rewards(user_id, milestone)
            
            logger.info(f"Awarded milestone {milestone_id} to user {user_id}")
            
            return {
                'milestone': {
                    'id': milestone.id,
                    'name': milestone.name,
                    'description': milestone.description,
                    'category': milestone.category
                },
                'achieved_at': user_milestone.achieved_at,
                'rewards': rewards_granted
            }
            
        except Exception as e:
            logger.error(f"Error awarding milestone: {str(e)}")
            self.db.rollback()
            return None
    
    def get_user_milestones(self, user_id: int, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all milestones achieved by a user"""
        try:
            query = self.db.query(UserMilestone, Milestone).join(Milestone)
            query = query.filter(UserMilestone.user_id == user_id)
            
            if category:
                query = query.filter(Milestone.category == category)
            
            results = query.order_by(UserMilestone.achieved_at.desc()).all()
            
            return [
                {
                    'id': um.id,
                    'milestone': {
                        'id': m.id,
                        'name': m.name,
                        'description': m.description,
                        'category': m.category,
                        'rewards': m.rewards
                    },
                    'achieved_at': um.achieved_at,
                    'context_data': um.context_data
                }
                for um, m in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user milestones: {str(e)}")
            return []
    
    def get_progress_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive progress dashboard data"""
        try:
            # Get all active progress trackers
            progress_data = self.get_user_progress(user_id)
            
            # Get recent milestones (last 30 days)
            recent_milestones = self.db.query(UserMilestone, Milestone).join(Milestone).filter(
                UserMilestone.user_id == user_id,
                UserMilestone.achieved_at >= datetime.utcnow() - timedelta(days=30)
            ).order_by(UserMilestone.achieved_at.desc()).limit(5).all()
            
            # Calculate overall progress
            overall_progress = self._calculate_overall_progress(user_id)
            
            # Get next achievable milestones
            next_milestones = self._get_next_milestones(user_id)
            
            return {
                'progress_trackers': progress_data,
                'recent_milestones': [
                    {
                        'milestone': {
                            'name': m.name,
                            'description': m.description,
                            'category': m.category
                        },
                        'achieved_at': um.achieved_at
                    }
                    for um, m in recent_milestones
                ],
                'overall_progress': overall_progress,
                'next_milestones': next_milestones,
                'total_milestones': self.db.query(UserMilestone).filter_by(user_id=user_id).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting progress dashboard: {str(e)}")
            return {}
    
    def create_progress_goal(self, progress_id: int, goal_data: Dict[str, Any]) -> ProgressGoal:
        """Create a progress goal with deadline and rewards"""
        try:
            goal = ProgressGoal(
                progress_id=progress_id,
                name=goal_data['name'],
                description=goal_data.get('description', ''),
                target_value=goal_data['target_value'],
                deadline=goal_data.get('deadline'),
                rewards=goal_data.get('rewards', {}),
                is_active=True
            )
            
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            
            logger.info(f"Created progress goal: {goal.name}")
            return goal
            
        except Exception as e:
            logger.error(f"Error creating progress goal: {str(e)}")
            self.db.rollback()
            raise
    
    # Progress tracking methods for different types
    
    def track_program_completion(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track program completion progress"""
        try:
            program_id = progress.target_data.get('program_id')
            if not program_id:
                return None
            
            # Count completed evaluations in the program
            completed_count = self.db.query(func.count(Evaluation.id)).filter(
                Evaluation.user_id == progress.user_id,
                Evaluation.program_id == program_id,
                Evaluation.status == 'completed'
            ).scalar() or 0
            
            # Get total evaluations in program
            total_count = self.db.query(func.count(Evaluation.id)).filter(
                Evaluation.program_id == program_id
            ).scalar() or 1
            
            progress.current_value = completed_count
            progress.target_value = total_count
            progress.updated_at = datetime.utcnow()
            
            # Update metadata
            progress.metadata.update({
                'last_completed': update_data.get('evaluation_id'),
                'completion_rate': (completed_count / total_count) * 100
            })
            
            self.db.commit()
            
            # Check if program is completed
            if completed_count >= total_count:
                return self._create_milestone_achievement('PROGRAM_COMPLETED', progress, update_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error tracking program completion: {str(e)}")
            return None
    
    def track_skill_development(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track skill development progress"""
        try:
            skill_id = progress.target_data.get('skill_id')
            if not skill_id:
                return None
            
            # This would integrate with a skill assessment system
            # For now, we'll use a placeholder implementation
            current_proficiency = update_data.get('proficiency', 0)
            
            progress.current_value = current_proficiency
            progress.updated_at = datetime.utcnow()
            
            # Update metadata
            progress.metadata.update({
                'last_assessment': update_data.get('assessment_id'),
                'proficiency_history': progress.metadata.get('proficiency_history', []) + [
                    {'value': current_proficiency, 'date': datetime.utcnow().isoformat()}
                ]
            })
            
            self.db.commit()
            
            # Check for skill mastery milestone
            if current_proficiency >= progress.target_value:
                return self._create_milestone_achievement('SKILL_MASTERY', progress, update_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error tracking skill development: {str(e)}")
            return None
    
    def track_evaluation_performance(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track evaluation performance progress"""
        try:
            score = update_data.get('score', 0)
            evaluation_id = update_data.get('evaluation_id')
            
            # Update progress based on criteria
            criteria = progress.target_data.get('criteria', 'completion')
            
            if criteria == 'completion':
                progress.current_value += 1
            elif criteria == 'average_score':
                # Calculate running average
                evaluations_count = progress.metadata.get('evaluations_count', 0) + 1
                current_average = progress.metadata.get('average_score', 0)
                new_average = ((current_average * (evaluations_count - 1)) + score) / evaluations_count
                
                progress.current_value = new_average
                progress.metadata['evaluations_count'] = evaluations_count
                progress.metadata['average_score'] = new_average
            elif criteria == 'perfect_scores':
                if score == 100:
                    progress.current_value += 1
            
            progress.updated_at = datetime.utcnow()
            
            # Update metadata
            progress.metadata.update({
                'last_evaluation': evaluation_id,
                'last_score': score,
                'score_history': progress.metadata.get('score_history', []) + [
                    {'score': score, 'evaluation_id': evaluation_id, 'date': datetime.utcnow().isoformat()}
                ]
            })
            
            self.db.commit()
            
            # Check for milestones
            if progress.current_value >= progress.target_value:
                return self._create_milestone_achievement('PERFORMANCE_TARGET', progress, update_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error tracking evaluation performance: {str(e)}")
            return None
    
    def track_learning_streak(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track learning streak progress"""
        try:
            # Calculate current streak
            streak_days = self._calculate_learning_streak(progress.user_id)
            
            progress.current_value = streak_days
            progress.updated_at = datetime.utcnow()
            
            # Update metadata
            progress.metadata.update({
                'last_activity': datetime.utcnow().isoformat(),
                'streak_history': progress.metadata.get('streak_history', []) + [
                    {'streak': streak_days, 'date': datetime.utcnow().isoformat()}
                ]
            })
            
            self.db.commit()
            
            # Check for streak milestones
            if streak_days >= progress.target_value:
                return self._create_milestone_achievement('STREAK_MILESTONE', progress, update_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error tracking learning streak: {str(e)}")
            return None
    
    def track_participation(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track participation progress"""
        try:
            activity_type = update_data.get('activity_type', 'general')
            
            progress.current_value += 1
            progress.updated_at = datetime.utcnow()
            
            # Update metadata
            activities = progress.metadata.get('activities', {})
            activities[activity_type] = activities.get(activity_type, 0) + 1
            progress.metadata['activities'] = activities
            
            self.db.commit()
            
            # Check for participation milestones
            if progress.current_value >= progress.target_value:
                return self._create_milestone_achievement('PARTICIPATION_TARGET', progress, update_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error tracking participation: {str(e)}")
            return None
    
    def track_social_engagement(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track social engagement progress"""
        # Placeholder for social features
        return None
    
    def track_custom_objective(self, progress: Progress, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Track custom objective progress"""
        try:
            increment = update_data.get('increment', 1)
            progress.current_value += increment
            progress.updated_at = datetime.utcnow()
            
            # Update metadata
            progress.metadata.update(update_data.get('metadata', {}))
            
            self.db.commit()
            
            # Check for completion
            if progress.current_value >= progress.target_value:
                return self._create_milestone_achievement('CUSTOM_OBJECTIVE', progress, update_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error tracking custom objective: {str(e)}")
            return None
    
    # Helper methods
    
    def _calculate_progress_percentage(self, progress: Progress) -> float:
        """Calculate progress percentage"""
        if progress.target_value <= 0:
            return 0.0
        
        percentage = (progress.current_value / progress.target_value) * 100
        return min(100.0, max(0.0, percentage))
    
    def _is_milestone_eligible(self, user_id: int, milestone: Milestone, 
                              context_data: Dict[str, Any]) -> bool:
        """Check if user is eligible for a milestone"""
        try:
            criteria = milestone.criteria or {}
            
            # This would implement various milestone criteria checks
            # For now, returning True as a placeholder
            return True
            
        except Exception as e:
            logger.error(f"Error checking milestone eligibility: {str(e)}")
            return False
    
    def _process_milestone_rewards(self, user_id: int, milestone: Milestone) -> List[Dict[str, Any]]:
        """Process rewards for achieving a milestone"""
        try:
            rewards = milestone.rewards or {}
            granted_rewards = []
            
            # Process XP reward
            if 'xp' in rewards:
                # This would integrate with XP service
                granted_rewards.append({
                    'type': 'xp',
                    'amount': rewards['xp']
                })
            
            # Process badge reward
            if 'badge' in rewards:
                # This would integrate with badge service
                granted_rewards.append({
                    'type': 'badge',
                    'badge_id': rewards['badge']
                })
            
            # Process other rewards
            for reward_type, reward_value in rewards.items():
                if reward_type not in ['xp', 'badge']:
                    granted_rewards.append({
                        'type': reward_type,
                        'value': reward_value
                    })
            
            return granted_rewards
            
        except Exception as e:
            logger.error(f"Error processing milestone rewards: {str(e)}")
            return []
    
    def _calculate_overall_progress(self, user_id: int) -> Dict[str, Any]:
        """Calculate overall progress across all trackers"""
        try:
            progress_trackers = self.db.query(Progress).filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            if not progress_trackers:
                return {'percentage': 0, 'completed': 0, 'total': 0}
            
            total_percentage = sum(self._calculate_progress_percentage(p) for p in progress_trackers)
            average_percentage = total_percentage / len(progress_trackers)
            completed_trackers = sum(1 for p in progress_trackers if self._calculate_progress_percentage(p) >= 100)
            
            return {
                'percentage': round(average_percentage, 2),
                'completed': completed_trackers,
                'total': len(progress_trackers),
                'completion_rate': round((completed_trackers / len(progress_trackers)) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall progress: {str(e)}")
            return {'percentage': 0, 'completed': 0, 'total': 0}
    
    def _get_next_milestones(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get next achievable milestones for a user"""
        try:
            # Get milestones user hasn't achieved yet
            achieved_ids = self.db.query(UserMilestone.milestone_id).filter_by(
                user_id=user_id
            ).subquery()
            
            next_milestones = self.db.query(Milestone).filter(
                Milestone.is_active == True,
                ~Milestone.id.in_(achieved_ids)
            ).limit(limit).all()
            
            return [
                {
                    'id': m.id,
                    'name': m.name,
                    'description': m.description,
                    'category': m.category,
                    'rewards': m.rewards,
                    'progress': self._calculate_milestone_progress(user_id, m)
                }
                for m in next_milestones
            ]
            
        except Exception as e:
            logger.error(f"Error getting next milestones: {str(e)}")
            return []
    
    def _calculate_milestone_progress(self, user_id: int, milestone: Milestone) -> Dict[str, Any]:
        """Calculate user's progress towards a specific milestone"""
        try:
            # This would implement milestone progress calculation
            # For now, returning a placeholder
            return {
                'percentage': 0,
                'current': 0,
                'target': 1,
                'description': 'Progress calculation not implemented'
            }
            
        except Exception as e:
            logger.error(f"Error calculating milestone progress: {str(e)}")
            return {'percentage': 0, 'current': 0, 'target': 1}
    
    def _calculate_learning_streak(self, user_id: int) -> int:
        """Calculate user's current learning streak"""
        try:
            # This would calculate based on daily activity
            # For now, returning a placeholder
            return 0
            
        except Exception as e:
            logger.error(f"Error calculating learning streak: {str(e)}")
            return 0
    
    def _create_milestone_achievement(self, achievement_type: str, progress: Progress, 
                                    update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a milestone achievement record"""
        try:
            return {
                'type': achievement_type,
                'progress_id': progress.id,
                'user_id': progress.user_id,
                'achieved_at': datetime.utcnow(),
                'data': update_data
            }
            
        except Exception as e:
            logger.error(f"Error creating milestone achievement: {str(e)}")
            return {}