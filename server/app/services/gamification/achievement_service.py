"""
Achievement Service

Handles the creation, management, and tracking of user achievements.
Includes both automatic achievements (triggered by system events) and 
manual achievements (awarded by trainers/admins).
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.gamification import Achievement, UserAchievement, AchievementCriteria
from app.models.user import User
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AchievementService(BaseService):
    """Service for managing achievements and tracking user progress"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.achievement_types = {
            'COMPLETION': self._check_completion_achievements,
            'STREAK': self._check_streak_achievements,
            'PERFORMANCE': self._check_performance_achievements,
            'PARTICIPATION': self._check_participation_achievements,
            'MILESTONE': self._check_milestone_achievements,
            'SOCIAL': self._check_social_achievements,
            'LEARNING_PATH': self._check_learning_path_achievements
        }
    
    def create_achievement(self, achievement_data: Dict[str, Any]) -> Achievement:
        """Create a new achievement definition"""
        try:
            achievement = Achievement(
                name=achievement_data['name'],
                description=achievement_data['description'],
                icon=achievement_data.get('icon', '🏆'),
                category=achievement_data['category'],
                points=achievement_data.get('points', 100),
                rarity=achievement_data.get('rarity', 'common'),
                is_active=achievement_data.get('is_active', True),
                criteria=achievement_data.get('criteria', {}),
                unlock_message=achievement_data.get('unlock_message'),
                created_by=achievement_data.get('created_by')
            )
            
            self.db.add(achievement)
            self.db.commit()
            self.db.refresh(achievement)
            
            logger.info(f"Created achievement: {achievement.name}")
            return achievement
            
        except Exception as e:
            logger.error(f"Error creating achievement: {str(e)}")
            self.db.rollback()
            raise
    
    def award_achievement(self, user_id: int, achievement_id: int, 
                         awarded_by: Optional[int] = None, 
                         progress_data: Optional[Dict] = None) -> UserAchievement:
        """Award an achievement to a user"""
        try:
            # Check if user already has this achievement
            existing = self.db.query(UserAchievement).filter_by(
                user_id=user_id,
                achievement_id=achievement_id
            ).first()
            
            if existing:
                logger.warning(f"User {user_id} already has achievement {achievement_id}")
                return existing
            
            # Create user achievement record
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id,
                earned_at=datetime.utcnow(),
                awarded_by=awarded_by,
                progress_data=progress_data or {}
            )
            
            self.db.add(user_achievement)
            
            # Update user's total achievement points
            achievement = self.db.query(Achievement).get(achievement_id)
            if achievement:
                user = self.db.query(User).get(user_id)
                if user:
                    user.total_achievement_points = (user.total_achievement_points or 0) + achievement.points
            
            self.db.commit()
            self.db.refresh(user_achievement)
            
            logger.info(f"Awarded achievement {achievement_id} to user {user_id}")
            return user_achievement
            
        except Exception as e:
            logger.error(f"Error awarding achievement: {str(e)}")
            self.db.rollback()
            raise
    
    def check_achievements_for_user(self, user_id: int, event_type: str, 
                                  event_data: Dict[str, Any]) -> List[UserAchievement]:
        """Check and award eligible achievements for a user based on an event"""
        try:
            awarded_achievements = []
            
            # Get active achievements for this event type
            achievements = self.db.query(Achievement).filter(
                Achievement.is_active == True,
                Achievement.trigger_events.contains([event_type])
            ).all()
            
            for achievement in achievements:
                if self._is_achievement_eligible(user_id, achievement, event_data):
                    user_achievement = self.award_achievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        progress_data=event_data
                    )
                    awarded_achievements.append(user_achievement)
            
            return awarded_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {str(e)}")
            return []
    
    def get_user_achievements(self, user_id: int, category: Optional[str] = None) -> List[Dict]:
        """Get all achievements earned by a user"""
        try:
            query = self.db.query(UserAchievement, Achievement).join(Achievement)
            query = query.filter(UserAchievement.user_id == user_id)
            
            if category:
                query = query.filter(Achievement.category == category)
            
            results = query.order_by(UserAchievement.earned_at.desc()).all()
            
            return [
                {
                    'id': ua.id,
                    'achievement': {
                        'id': a.id,
                        'name': a.name,
                        'description': a.description,
                        'icon': a.icon,
                        'category': a.category,
                        'points': a.points,
                        'rarity': a.rarity
                    },
                    'earned_at': ua.earned_at,
                    'progress_data': ua.progress_data
                }
                for ua, a in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {str(e)}")
            return []
    
    def get_achievement_progress(self, user_id: int, achievement_id: int) -> Dict[str, Any]:
        """Get user's progress towards a specific achievement"""
        try:
            achievement = self.db.query(Achievement).get(achievement_id)
            if not achievement:
                return {}
            
            # Check if user already has this achievement
            user_achievement = self.db.query(UserAchievement).filter_by(
                user_id=user_id,
                achievement_id=achievement_id
            ).first()
            
            if user_achievement:
                return {
                    'completed': True,
                    'progress': 100,
                    'earned_at': user_achievement.earned_at,
                    'progress_data': user_achievement.progress_data
                }
            
            # Calculate current progress
            progress_data = self._calculate_achievement_progress(user_id, achievement)
            
            return {
                'completed': False,
                'progress': progress_data.get('percentage', 0),
                'current_value': progress_data.get('current_value', 0),
                'target_value': progress_data.get('target_value', 1),
                'description': progress_data.get('description', ''),
                'next_milestone': progress_data.get('next_milestone')
            }
            
        except Exception as e:
            logger.error(f"Error getting achievement progress: {str(e)}")
            return {}
    
    def get_available_achievements(self, user_id: int, category: Optional[str] = None) -> List[Dict]:
        """Get achievements available to earn (not yet earned by user)"""
        try:
            # Get user's earned achievement IDs
            earned_ids = self.db.query(UserAchievement.achievement_id).filter_by(
                user_id=user_id
            ).subquery()
            
            # Get available achievements
            query = self.db.query(Achievement).filter(
                Achievement.is_active == True,
                ~Achievement.id.in_(earned_ids)
            )
            
            if category:
                query = query.filter(Achievement.category == category)
            
            achievements = query.all()
            
            result = []
            for achievement in achievements:
                progress = self.get_achievement_progress(user_id, achievement.id)
                result.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'category': achievement.category,
                    'points': achievement.points,
                    'rarity': achievement.rarity,
                    'progress': progress
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting available achievements: {str(e)}")
            return []
    
    def _is_achievement_eligible(self, user_id: int, achievement: Achievement, 
                               event_data: Dict[str, Any]) -> bool:
        """Check if user is eligible for an achievement based on criteria"""
        try:
            criteria = achievement.criteria or {}
            
            # Check achievement type specific criteria
            achievement_type = criteria.get('type', 'COMPLETION')
            if achievement_type in self.achievement_types:
                return self.achievement_types[achievement_type](user_id, criteria, event_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking achievement eligibility: {str(e)}")
            return False
    
    def _calculate_achievement_progress(self, user_id: int, achievement: Achievement) -> Dict[str, Any]:
        """Calculate user's current progress towards an achievement"""
        try:
            criteria = achievement.criteria or {}
            achievement_type = criteria.get('type', 'COMPLETION')
            
            if achievement_type == 'COMPLETION':
                return self._calculate_completion_progress(user_id, criteria)
            elif achievement_type == 'STREAK':
                return self._calculate_streak_progress(user_id, criteria)
            elif achievement_type == 'PERFORMANCE':
                return self._calculate_performance_progress(user_id, criteria)
            elif achievement_type == 'PARTICIPATION':
                return self._calculate_participation_progress(user_id, criteria)
            elif achievement_type == 'MILESTONE':
                return self._calculate_milestone_progress(user_id, criteria)
            
            return {'percentage': 0, 'current_value': 0, 'target_value': 1}
            
        except Exception as e:
            logger.error(f"Error calculating achievement progress: {str(e)}")
            return {'percentage': 0, 'current_value': 0, 'target_value': 1}
    
    def _check_completion_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check completion-based achievements"""
        target_count = criteria.get('target_count', 1)
        program_id = criteria.get('program_id')
        
        # Count completed evaluations/modules
        query = self.db.query(func.count(Evaluation.id)).filter(
            Evaluation.user_id == user_id,
            Evaluation.status == 'completed'
        )
        
        if program_id:
            query = query.filter(Evaluation.program_id == program_id)
        
        completed_count = query.scalar() or 0
        return completed_count >= target_count
    
    def _check_streak_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check streak-based achievements"""
        # Implementation for streak checking
        # This would check for consecutive days of activity
        return False  # Placeholder
    
    def _check_performance_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check performance-based achievements"""
        min_score = criteria.get('min_score', 80)
        score = event_data.get('score', 0)
        return score >= min_score
    
    def _check_participation_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check participation-based achievements"""
        # Implementation for participation checking
        return False  # Placeholder
    
    def _check_milestone_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check milestone-based achievements"""
        # Implementation for milestone checking
        return False  # Placeholder
    
    def _check_social_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check social-based achievements"""
        # Implementation for social achievements
        return False  # Placeholder
    
    def _check_learning_path_achievements(self, user_id: int, criteria: Dict, event_data: Dict) -> bool:
        """Check learning path achievements"""
        # Implementation for learning path achievements
        return False  # Placeholder
    
    def _calculate_completion_progress(self, user_id: int, criteria: Dict) -> Dict[str, Any]:
        """Calculate progress for completion achievements"""
        target_count = criteria.get('target_count', 1)
        program_id = criteria.get('program_id')
        
        query = self.db.query(func.count(Evaluation.id)).filter(
            Evaluation.user_id == user_id,
            Evaluation.status == 'completed'
        )
        
        if program_id:
            query = query.filter(Evaluation.program_id == program_id)
        
        current_count = query.scalar() or 0
        percentage = min(100, (current_count / target_count) * 100)
        
        return {
            'percentage': percentage,
            'current_value': current_count,
            'target_value': target_count,
            'description': f'Complete {current_count}/{target_count} evaluations'
        }
    
    def _calculate_streak_progress(self, user_id: int, criteria: Dict) -> Dict[str, Any]:
        """Calculate progress for streak achievements"""
        # Placeholder implementation
        return {'percentage': 0, 'current_value': 0, 'target_value': 1}
    
    def _calculate_performance_progress(self, user_id: int, criteria: Dict) -> Dict[str, Any]:
        """Calculate progress for performance achievements"""
        # Placeholder implementation
        return {'percentage': 0, 'current_value': 0, 'target_value': 1}
    
    def _calculate_participation_progress(self, user_id: int, criteria: Dict) -> Dict[str, Any]:
        """Calculate progress for participation achievements"""
        # Placeholder implementation
        return {'percentage': 0, 'current_value': 0, 'target_value': 1}
    
    def _calculate_milestone_progress(self, user_id: int, criteria: Dict) -> Dict[str, Any]:
        """Calculate progress for milestone achievements"""
        # Placeholder implementation
        return {'percentage': 0, 'current_value': 0, 'target_value': 1}