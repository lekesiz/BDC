"""
Experience Points (XP) Service

Manages experience points calculation, distribution, and tracking.
Handles XP multipliers, bonus events, and different XP sources.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from decimal import Decimal

from app.models.gamification import XPTransaction, XPMultiplier, XPSource
from app.models.user import User
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class XPService(BaseService):
    """Service for managing experience points"""
    
    # Base XP values for different activities
    BASE_XP_VALUES = {
        'evaluation_completed': 100,
        'evaluation_perfect_score': 50,  # Bonus for 100% score
        'streak_day': 25,
        'first_attempt_success': 30,
        'quick_completion': 20,  # Completing within time limit
        'participation': 15,
        'social_interaction': 10,
        'daily_login': 5,
        'module_completed': 75,
        'program_completed': 500,
        'badge_earned': 25,
        'achievement_unlocked': 50,
        'mentor_feedback': 20,
        'peer_help': 15,
        'content_created': 40,
        'quiz_completed': 50
    }
    
    # XP multiplier events
    MULTIPLIER_EVENTS = {
        'weekend_warrior': {'multiplier': 1.5, 'days': [5, 6]},  # Sat, Sun
        'early_bird': {'multiplier': 1.2, 'hours': [6, 7, 8, 9]},  # 6-9 AM
        'night_owl': {'multiplier': 1.1, 'hours': [20, 21, 22, 23]},  # 8-11 PM
        'streak_bonus': {'multiplier': 2.0, 'min_streak': 7},
        'perfect_week': {'multiplier': 3.0, 'condition': 'all_days_active'}
    }
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def award_xp(self, user_id: int, source: str, base_amount: int,
                 multiplier: float = 1.0, metadata: Optional[Dict] = None,
                 reference_id: Optional[int] = None, 
                 reference_type: Optional[str] = None) -> XPTransaction:
        """Award XP to a user for a specific activity"""
        try:
            # Calculate total XP with multipliers
            total_multiplier = self._calculate_total_multiplier(user_id, source, multiplier)
            final_amount = int(base_amount * total_multiplier)
            
            # Create XP transaction
            transaction = XPTransaction(
                user_id=user_id,
                source=source,
                amount=final_amount,
                base_amount=base_amount,
                multiplier=total_multiplier,
                metadata=metadata or {},
                reference_id=reference_id,
                reference_type=reference_type,
                earned_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            
            # Update user's total XP
            user = self.db.query(User).get(user_id)
            if user:
                user.total_xp = (user.total_xp or 0) + final_amount
                user.last_xp_earned = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Awarded {final_amount} XP to user {user_id} from {source}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error awarding XP: {str(e)}")
            self.db.rollback()
            raise
    
    def award_activity_xp(self, user_id: int, activity: str, 
                         metadata: Optional[Dict] = None,
                         reference_id: Optional[int] = None,
                         reference_type: Optional[str] = None) -> Optional[XPTransaction]:
        """Award XP for a predefined activity"""
        try:
            if activity not in self.BASE_XP_VALUES:
                logger.warning(f"Unknown activity type: {activity}")
                return None
            
            base_amount = self.BASE_XP_VALUES[activity]
            
            # Check for special conditions that modify XP
            bonus_multiplier = self._calculate_activity_bonus(user_id, activity, metadata)
            
            return self.award_xp(
                user_id=user_id,
                source=activity,
                base_amount=base_amount,
                multiplier=bonus_multiplier,
                metadata=metadata,
                reference_id=reference_id,
                reference_type=reference_type
            )
            
        except Exception as e:
            logger.error(f"Error awarding activity XP: {str(e)}")
            return None
    
    def get_user_xp_history(self, user_id: int, days: int = 30,
                           source: Optional[str] = None) -> List[Dict]:
        """Get user's XP transaction history"""
        try:
            query = self.db.query(XPTransaction).filter(
                XPTransaction.user_id == user_id,
                XPTransaction.earned_at >= datetime.utcnow() - timedelta(days=days)
            )
            
            if source:
                query = query.filter(XPTransaction.source == source)
            
            transactions = query.order_by(XPTransaction.earned_at.desc()).all()
            
            return [
                {
                    'id': t.id,
                    'source': t.source,
                    'amount': t.amount,
                    'base_amount': t.base_amount,
                    'multiplier': t.multiplier,
                    'metadata': t.metadata,
                    'reference_id': t.reference_id,
                    'reference_type': t.reference_type,
                    'earned_at': t.earned_at
                }
                for t in transactions
            ]
            
        except Exception as e:
            logger.error(f"Error getting XP history: {str(e)}")
            return []
    
    def get_xp_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive XP statistics for a user"""
        try:
            user = self.db.query(User).get(user_id)
            if not user:
                return {}
            
            # Total XP
            total_xp = user.total_xp or 0
            
            # XP this week
            week_start = datetime.utcnow() - timedelta(days=7)
            week_xp = self.db.query(func.sum(XPTransaction.amount)).filter(
                XPTransaction.user_id == user_id,
                XPTransaction.earned_at >= week_start
            ).scalar() or 0
            
            # XP today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_xp = self.db.query(func.sum(XPTransaction.amount)).filter(
                XPTransaction.user_id == user_id,
                XPTransaction.earned_at >= today_start
            ).scalar() or 0
            
            # XP by source (last 30 days)
            source_stats = {}
            results = self.db.query(
                XPTransaction.source,
                func.sum(XPTransaction.amount).label('total'),
                func.count(XPTransaction.id).label('count')
            ).filter(
                XPTransaction.user_id == user_id,
                XPTransaction.earned_at >= datetime.utcnow() - timedelta(days=30)
            ).group_by(XPTransaction.source).all()
            
            for source, total, count in results:
                source_stats[source] = {'total': total, 'count': count}
            
            # Current streak
            current_streak = self._calculate_current_streak(user_id)
            
            # Average XP per day (last 30 days)
            avg_xp = week_xp / 7 if week_xp > 0 else 0
            
            return {
                'total_xp': total_xp,
                'week_xp': week_xp,
                'today_xp': today_xp,
                'source_breakdown': source_stats,
                'current_streak': current_streak,
                'average_daily_xp': round(avg_xp, 2),
                'last_earned': user.last_xp_earned
            }
            
        except Exception as e:
            logger.error(f"Error getting XP statistics: {str(e)}")
            return {}
    
    def get_xp_leaderboard(self, timeframe: str = 'all_time', limit: int = 10) -> List[Dict]:
        """Get XP leaderboard for different timeframes"""
        try:
            if timeframe == 'today':
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                query = self.db.query(
                    User.id,
                    User.username,
                    User.first_name,
                    User.last_name,
                    func.sum(XPTransaction.amount).label('xp')
                ).join(XPTransaction).filter(
                    XPTransaction.earned_at >= start_date
                ).group_by(User.id)
            elif timeframe == 'week':
                start_date = datetime.utcnow() - timedelta(days=7)
                query = self.db.query(
                    User.id,
                    User.username,
                    User.first_name,
                    User.last_name,
                    func.sum(XPTransaction.amount).label('xp')
                ).join(XPTransaction).filter(
                    XPTransaction.earned_at >= start_date
                ).group_by(User.id)
            elif timeframe == 'month':
                start_date = datetime.utcnow() - timedelta(days=30)
                query = self.db.query(
                    User.id,
                    User.username,
                    User.first_name,
                    User.last_name,
                    func.sum(XPTransaction.amount).label('xp')
                ).join(XPTransaction).filter(
                    XPTransaction.earned_at >= start_date
                ).group_by(User.id)
            else:  # all_time
                query = self.db.query(
                    User.id,
                    User.username,
                    User.first_name,
                    User.last_name,
                    User.total_xp.label('xp')
                ).filter(User.total_xp.isnot(None))
            
            results = query.order_by(func.coalesce(func.sum(XPTransaction.amount), User.total_xp).desc()).limit(limit).all()
            
            return [
                {
                    'rank': idx + 1,
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'display_name': f"{first_name} {last_name}" if first_name and last_name else username,
                    'xp': int(xp) if xp else 0
                }
                for idx, (user_id, username, first_name, last_name, xp) in enumerate(results)
            ]
            
        except Exception as e:
            logger.error(f"Error getting XP leaderboard: {str(e)}")
            return []
    
    def create_xp_multiplier(self, multiplier_data: Dict[str, Any]) -> XPMultiplier:
        """Create a temporary XP multiplier event"""
        try:
            multiplier = XPMultiplier(
                name=multiplier_data['name'],
                description=multiplier_data.get('description', ''),
                multiplier=multiplier_data['multiplier'],
                start_date=multiplier_data['start_date'],
                end_date=multiplier_data['end_date'],
                conditions=multiplier_data.get('conditions', {}),
                target_users=multiplier_data.get('target_users', []),
                target_activities=multiplier_data.get('target_activities', []),
                is_active=multiplier_data.get('is_active', True),
                created_by=multiplier_data.get('created_by')
            )
            
            self.db.add(multiplier)
            self.db.commit()
            self.db.refresh(multiplier)
            
            logger.info(f"Created XP multiplier: {multiplier.name}")
            return multiplier
            
        except Exception as e:
            logger.error(f"Error creating XP multiplier: {str(e)}")
            self.db.rollback()
            raise
    
    def _calculate_total_multiplier(self, user_id: int, source: str, base_multiplier: float) -> float:
        """Calculate total multiplier including active events and conditions"""
        try:
            total_multiplier = base_multiplier
            now = datetime.utcnow()
            
            # Check for active XP multiplier events
            active_multipliers = self.db.query(XPMultiplier).filter(
                XPMultiplier.is_active == True,
                XPMultiplier.start_date <= now,
                XPMultiplier.end_date >= now
            ).all()
            
            for multiplier in active_multipliers:
                # Check if this multiplier applies to this user and activity
                if self._multiplier_applies(user_id, source, multiplier):
                    total_multiplier *= multiplier.multiplier
            
            # Check for time-based multipliers
            time_multiplier = self._get_time_based_multiplier(now)
            total_multiplier *= time_multiplier
            
            # Check for streak multipliers
            streak_multiplier = self._get_streak_multiplier(user_id)
            total_multiplier *= streak_multiplier
            
            return total_multiplier
            
        except Exception as e:
            logger.error(f"Error calculating total multiplier: {str(e)}")
            return base_multiplier
    
    def _calculate_activity_bonus(self, user_id: int, activity: str, metadata: Optional[Dict]) -> float:
        """Calculate bonus multiplier for specific activity conditions"""
        try:
            bonus = 1.0
            
            if not metadata:
                return bonus
            
            # Perfect score bonus
            if activity == 'evaluation_completed' and metadata.get('score') == 100:
                bonus *= 1.2
            
            # Quick completion bonus
            if metadata.get('completed_quickly'):
                bonus *= 1.1
            
            # First attempt success
            if metadata.get('first_attempt') and metadata.get('success'):
                bonus *= 1.15
            
            # Difficulty bonus
            difficulty = metadata.get('difficulty', 'medium')
            difficulty_multipliers = {'easy': 1.0, 'medium': 1.1, 'hard': 1.25, 'expert': 1.5}
            bonus *= difficulty_multipliers.get(difficulty, 1.0)
            
            return bonus
            
        except Exception as e:
            logger.error(f"Error calculating activity bonus: {str(e)}")
            return 1.0
    
    def _multiplier_applies(self, user_id: int, source: str, multiplier: XPMultiplier) -> bool:
        """Check if a multiplier applies to this user and activity"""
        try:
            # Check target users
            if multiplier.target_users and user_id not in multiplier.target_users:
                return False
            
            # Check target activities
            if multiplier.target_activities and source not in multiplier.target_activities:
                return False
            
            # Check additional conditions
            conditions = multiplier.conditions or {}
            
            # Example: Check user level requirement
            if conditions.get('min_level'):
                # This would require integration with level service
                pass
            
            # Example: Check user role requirement
            if conditions.get('required_roles'):
                # This would require checking user roles
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking multiplier applicability: {str(e)}")
            return False
    
    def _get_time_based_multiplier(self, timestamp: datetime) -> float:
        """Get time-based XP multipliers"""
        try:
            multiplier = 1.0
            
            # Weekend warrior bonus
            if timestamp.weekday() in [5, 6]:  # Saturday, Sunday
                multiplier *= 1.2
            
            # Early bird bonus (6-9 AM)
            if 6 <= timestamp.hour < 10:
                multiplier *= 1.1
            
            # Night owl bonus (8-11 PM)
            elif 20 <= timestamp.hour < 24:
                multiplier *= 1.05
            
            return multiplier
            
        except Exception as e:
            logger.error(f"Error getting time-based multiplier: {str(e)}")
            return 1.0
    
    def _get_streak_multiplier(self, user_id: int) -> float:
        """Get streak-based XP multiplier"""
        try:
            streak = self._calculate_current_streak(user_id)
            
            if streak >= 30:
                return 2.0
            elif streak >= 14:
                return 1.5
            elif streak >= 7:
                return 1.25
            elif streak >= 3:
                return 1.1
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error getting streak multiplier: {str(e)}")
            return 1.0
    
    def _calculate_current_streak(self, user_id: int) -> int:
        """Calculate user's current daily activity streak"""
        try:
            # Get the last 30 days of activity
            start_date = datetime.utcnow() - timedelta(days=30)
            
            # Group transactions by date
            results = self.db.query(
                func.date(XPTransaction.earned_at).label('date'),
                func.count(XPTransaction.id).label('count')
            ).filter(
                XPTransaction.user_id == user_id,
                XPTransaction.earned_at >= start_date
            ).group_by(func.date(XPTransaction.earned_at)).order_by(
                func.date(XPTransaction.earned_at).desc()
            ).all()
            
            if not results:
                return 0
            
            # Calculate streak from most recent day backwards
            streak = 0
            today = datetime.utcnow().date()
            
            for i, (date, count) in enumerate(results):
                expected_date = today - timedelta(days=i)
                
                if date == expected_date:
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating current streak: {str(e)}")
            return 0