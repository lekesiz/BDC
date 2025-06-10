"""
Level Service

Manages user levels, level progression, and level-based rewards.
Handles level calculations, requirements, and milestone rewards.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import math

from app.models.user import User
from app.models.gamification import Level, UserLevel, LevelReward
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LevelService(BaseService):
    """Service for managing user levels and progression"""
    
    # Level progression formulas
    PROGRESSION_FORMULAS = {
        'linear': lambda level: level * 1000,  # 1000 XP per level
        'exponential': lambda level: int(1000 * (1.2 ** (level - 1))),  # Exponential growth
        'quadratic': lambda level: int(500 * (level ** 1.5)),  # Quadratic growth
        'fibonacci': lambda level: LevelService._fibonacci_xp(level),  # Fibonacci-based
        'milestone': lambda level: LevelService._milestone_xp(level)  # Milestone-based
    }
    
    # Level titles and descriptions
    LEVEL_TITLES = {
        1: {'title': 'Beginner', 'description': 'Just starting your learning journey'},
        5: {'title': 'Novice', 'description': 'Getting familiar with the basics'},
        10: {'title': 'Apprentice', 'description': 'Building fundamental skills'},
        15: {'title': 'Student', 'description': 'Actively learning and growing'},
        20: {'title': 'Practitioner', 'description': 'Applying knowledge effectively'},
        25: {'title': 'Scholar', 'description': 'Demonstrating expertise'},
        30: {'title': 'Expert', 'description': 'Mastering advanced concepts'},
        35: {'title': 'Mentor', 'description': 'Helping others learn'},
        40: {'title': 'Master', 'description': 'Exceptional knowledge and skill'},
        45: {'title': 'Sage', 'description': 'Wisdom through experience'},
        50: {'title': 'Legend', 'description': 'Legendary achievement unlocked'},
        60: {'title': 'Champion', 'description': 'Champion of learning'},
        70: {'title': 'Hero', 'description': 'Hero of knowledge'},
        80: {'title': 'Titan', 'description': 'Titanic achievement'},
        90: {'title': 'Demigod', 'description': 'Near-divine mastery'},
        100: {'title': 'Transcendent', 'description': 'Transcended mortal limits'}
    }
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.progression_formula = 'exponential'  # Default formula
    
    def calculate_level_from_xp(self, total_xp: int, formula: str = None) -> Tuple[int, int, int]:
        """
        Calculate user level from total XP
        Returns: (current_level, xp_for_current_level, xp_for_next_level)
        """
        try:
            if total_xp <= 0:
                return 1, 0, self._get_xp_for_level(1)
            
            formula = formula or self.progression_formula
            level = 1
            
            # Find the highest level achievable with current XP
            while level <= 100:  # Cap at level 100
                xp_required = self._get_xp_for_level(level + 1, formula)
                if total_xp < xp_required:
                    break
                level += 1
            
            current_level_xp = self._get_xp_for_level(level, formula)
            next_level_xp = self._get_xp_for_level(level + 1, formula)
            
            return level, current_level_xp, next_level_xp
            
        except Exception as e:
            logger.error(f"Error calculating level from XP: {str(e)}")
            return 1, 0, 1000
    
    def update_user_level(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Update user's level based on current XP and check for level up"""
        try:
            user = self.db.query(User).get(user_id)
            if not user:
                return None
            
            total_xp = user.total_xp or 0
            old_level = user.level or 1
            
            # Calculate new level
            new_level, current_level_xp, next_level_xp = self.calculate_level_from_xp(total_xp)
            
            # Update user level if changed
            if new_level != old_level:
                user.level = new_level
                user.level_updated_at = datetime.utcnow()
                
                # Create level record if it doesn't exist
                user_level = self.db.query(UserLevel).filter_by(
                    user_id=user_id,
                    level=new_level
                ).first()
                
                if not user_level:
                    user_level = UserLevel(
                        user_id=user_id,
                        level=new_level,
                        achieved_at=datetime.utcnow(),
                        total_xp_at_achievement=total_xp
                    )
                    self.db.add(user_level)
                
                self.db.commit()
                
                # Return level up information
                return {
                    'level_up': True,
                    'old_level': old_level,
                    'new_level': new_level,
                    'title': self.get_level_title(new_level),
                    'rewards': self.get_level_rewards(new_level),
                    'progress': self.get_level_progress(user_id)
                }
            
            return {
                'level_up': False,
                'current_level': new_level,
                'progress': self.get_level_progress(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error updating user level: {str(e)}")
            return None
    
    def get_level_progress(self, user_id: int) -> Dict[str, Any]:
        """Get detailed level progress information for a user"""
        try:
            user = self.db.query(User).get(user_id)
            if not user:
                return {}
            
            total_xp = user.total_xp or 0
            current_level, current_level_xp, next_level_xp = self.calculate_level_from_xp(total_xp)
            
            # Calculate progress within current level
            xp_in_current_level = total_xp - current_level_xp
            xp_needed_for_next = next_level_xp - current_level_xp
            progress_percentage = (xp_in_current_level / xp_needed_for_next) * 100 if xp_needed_for_next > 0 else 100
            
            return {
                'current_level': current_level,
                'total_xp': total_xp,
                'current_level_xp': current_level_xp,
                'next_level_xp': next_level_xp,
                'xp_in_current_level': xp_in_current_level,
                'xp_needed_for_next': next_level_xp - total_xp,
                'progress_percentage': min(100, progress_percentage),
                'title': self.get_level_title(current_level),
                'next_title': self.get_level_title(current_level + 1) if current_level < 100 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting level progress: {str(e)}")
            return {}
    
    def get_level_title(self, level: int) -> Dict[str, str]:
        """Get title and description for a level"""
        try:
            # Find the appropriate title for this level
            applicable_levels = [l for l in self.LEVEL_TITLES.keys() if l <= level]
            if applicable_levels:
                title_level = max(applicable_levels)
                return self.LEVEL_TITLES[title_level]
            
            return {'title': 'Beginner', 'description': 'Just starting your learning journey'}
            
        except Exception as e:
            logger.error(f"Error getting level title: {str(e)}")
            return {'title': 'Unknown', 'description': ''}
    
    def get_level_rewards(self, level: int) -> List[Dict[str, Any]]:
        """Get rewards for achieving a specific level"""
        try:
            rewards = []
            
            # Milestone rewards
            if level % 5 == 0:  # Every 5 levels
                rewards.append({
                    'type': 'badge',
                    'name': f'Level {level} Master',
                    'description': f'Reached level {level}',
                    'icon': '🏆'
                })
            
            if level % 10 == 0:  # Every 10 levels
                rewards.append({
                    'type': 'title',
                    'name': self.get_level_title(level)['title'],
                    'description': f'Unlocked new title'
                })
            
            # Special milestone rewards
            milestone_rewards = {
                10: [{'type': 'feature', 'name': 'Custom Avatar', 'description': 'Unlock avatar customization'}],
                20: [{'type': 'multiplier', 'name': 'XP Boost', 'description': '1.1x XP multiplier for 24 hours'}],
                25: [{'type': 'feature', 'name': 'Mentor Access', 'description': 'Access to mentor features'}],
                50: [{'type': 'achievement', 'name': 'Legend Status', 'description': 'Legendary achievement unlocked'}],
                75: [{'type': 'cosmetic', 'name': 'Golden Badge', 'description': 'All badges get golden borders'}],
                100: [{'type': 'exclusive', 'name': 'Hall of Fame', 'description': 'Permanent Hall of Fame entry'}]
            }
            
            if level in milestone_rewards:
                rewards.extend(milestone_rewards[level])
            
            return rewards
            
        except Exception as e:
            logger.error(f"Error getting level rewards: {str(e)}")
            return []
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get level-based leaderboard"""
        try:
            results = self.db.query(User).filter(
                User.level.isnot(None),
                User.total_xp.isnot(None)
            ).order_by(
                User.level.desc(),
                User.total_xp.desc()
            ).limit(limit).all()
            
            return [
                {
                    'rank': idx + 1,
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                    'level': user.level or 1,
                    'total_xp': user.total_xp or 0,
                    'title': self.get_level_title(user.level or 1),
                    'avatar_url': getattr(user, 'avatar_url', None)
                }
                for idx, user in enumerate(results)
            ]
            
        except Exception as e:
            logger.error(f"Error getting level leaderboard: {str(e)}")
            return []
    
    def get_level_statistics(self) -> Dict[str, Any]:
        """Get global level statistics"""
        try:
            # Level distribution
            level_distribution = {}
            results = self.db.query(
                User.level,
                func.count(User.id).label('count')
            ).filter(
                User.level.isnot(None)
            ).group_by(User.level).all()
            
            for level, count in results:
                level_distribution[level] = count
            
            # Average level
            avg_level = self.db.query(func.avg(User.level)).filter(
                User.level.isnot(None)
            ).scalar() or 0
            
            # Highest level
            max_level = self.db.query(func.max(User.level)).filter(
                User.level.isnot(None)
            ).scalar() or 1
            
            # Recent level ups (last 7 days)
            recent_levelups = self.db.query(UserLevel).filter(
                UserLevel.achieved_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                'level_distribution': level_distribution,
                'average_level': round(avg_level, 2),
                'highest_level': max_level,
                'recent_levelups': recent_levelups,
                'total_leveled_users': sum(level_distribution.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting level statistics: {str(e)}")
            return {}
    
    def create_custom_level_system(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom level progression system"""
        try:
            system = {
                'name': system_data['name'],
                'description': system_data.get('description', ''),
                'formula': system_data.get('formula', 'exponential'),
                'max_level': system_data.get('max_level', 100),
                'base_xp': system_data.get('base_xp', 1000),
                'multiplier': system_data.get('multiplier', 1.2),
                'milestones': system_data.get('milestones', {}),
                'titles': system_data.get('titles', {}),
                'rewards': system_data.get('rewards', {}),
                'created_at': datetime.utcnow()
            }
            
            # Validate the system
            if self._validate_level_system(system):
                logger.info(f"Created custom level system: {system['name']}")
                return system
            else:
                raise ValueError("Invalid level system configuration")
            
        except Exception as e:
            logger.error(f"Error creating custom level system: {str(e)}")
            raise
    
    def preview_level_progression(self, formula: str = 'exponential', levels: int = 50) -> List[Dict[str, Any]]:
        """Preview XP requirements for level progression"""
        try:
            progression = []
            
            for level in range(1, levels + 1):
                xp_required = self._get_xp_for_level(level, formula)
                title_info = self.get_level_title(level)
                rewards = self.get_level_rewards(level)
                
                progression.append({
                    'level': level,
                    'xp_required': xp_required,
                    'cumulative_xp': sum(self._get_xp_for_level(i, formula) for i in range(1, level + 1)),
                    'title': title_info['title'],
                    'description': title_info['description'],
                    'rewards': rewards
                })
            
            return progression
            
        except Exception as e:
            logger.error(f"Error previewing level progression: {str(e)}")
            return []
    
    def _get_xp_for_level(self, level: int, formula: str = None) -> int:
        """Get XP required to reach a specific level"""
        try:
            formula = formula or self.progression_formula
            
            if formula in self.PROGRESSION_FORMULAS:
                return self.PROGRESSION_FORMULAS[formula](level)
            else:
                # Default to exponential
                return self.PROGRESSION_FORMULAS['exponential'](level)
                
        except Exception as e:
            logger.error(f"Error getting XP for level: {str(e)}")
            return level * 1000  # Fallback to linear
    
    @staticmethod
    def _fibonacci_xp(level: int) -> int:
        """Calculate XP using Fibonacci sequence"""
        if level <= 2:
            return 1000
        
        a, b = 1000, 1500
        for _ in range(level - 2):
            a, b = b, a + b
        
        return min(b, 50000)  # Cap to prevent overflow
    
    @staticmethod
    def _milestone_xp(level: int) -> int:
        """Calculate XP using milestone-based progression"""
        if level <= 10:
            return level * 500
        elif level <= 25:
            return 5000 + (level - 10) * 750
        elif level <= 50:
            return 16250 + (level - 25) * 1000
        else:
            return 41250 + (level - 50) * 1500
    
    def _validate_level_system(self, system: Dict[str, Any]) -> bool:
        """Validate a level system configuration"""
        try:
            required_fields = ['name', 'formula', 'max_level', 'base_xp']
            
            for field in required_fields:
                if field not in system:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate formula
            if system['formula'] not in self.PROGRESSION_FORMULAS:
                logger.error(f"Unknown formula: {system['formula']}")
                return False
            
            # Validate numeric values
            if system['max_level'] <= 0 or system['max_level'] > 1000:
                logger.error("Invalid max_level")
                return False
            
            if system['base_xp'] <= 0:
                logger.error("Invalid base_xp")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating level system: {str(e)}")
            return False