"""
Leaderboard Service

Manages various types of leaderboards and competitive elements.
Handles rankings, competitions, and performance comparisons.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from enum import Enum

from app.models.user import User
from app.models.gamification import Leaderboard, LeaderboardEntry, Competition
from app.models.evaluation import Evaluation
from app.models.program import Program
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LeaderboardType(Enum):
    """Leaderboard types"""
    XP = "xp"
    LEVEL = "level"
    BADGES = "badges"
    ACHIEVEMENTS = "achievements"
    EVALUATION_SCORE = "evaluation_score"
    COMPLETION_RATE = "completion_rate"
    STREAK = "streak"
    PROGRAM_PROGRESS = "program_progress"
    PARTICIPATION = "participation"
    CUSTOM = "custom"


class TimeFrame(Enum):
    """Leaderboard time frames"""
    ALL_TIME = "all_time"
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"


class LeaderboardService(BaseService):
    """Service for managing leaderboards and competitions"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.leaderboard_calculators = {
            LeaderboardType.XP: self._calculate_xp_leaderboard,
            LeaderboardType.LEVEL: self._calculate_level_leaderboard,
            LeaderboardType.BADGES: self._calculate_badges_leaderboard,
            LeaderboardType.ACHIEVEMENTS: self._calculate_achievements_leaderboard,
            LeaderboardType.EVALUATION_SCORE: self._calculate_evaluation_score_leaderboard,
            LeaderboardType.COMPLETION_RATE: self._calculate_completion_rate_leaderboard,
            LeaderboardType.STREAK: self._calculate_streak_leaderboard,
            LeaderboardType.PROGRAM_PROGRESS: self._calculate_program_progress_leaderboard,
            LeaderboardType.PARTICIPATION: self._calculate_participation_leaderboard
        }
    
    def create_leaderboard(self, leaderboard_data: Dict[str, Any]) -> Leaderboard:
        """Create a new leaderboard"""
        try:
            leaderboard = Leaderboard(
                name=leaderboard_data['name'],
                description=leaderboard_data.get('description', ''),
                leaderboard_type=leaderboard_data['type'],
                time_frame=leaderboard_data.get('time_frame', TimeFrame.ALL_TIME.value),
                criteria=leaderboard_data.get('criteria', {}),
                is_active=leaderboard_data.get('is_active', True),
                is_public=leaderboard_data.get('is_public', True),
                max_entries=leaderboard_data.get('max_entries', 100),
                update_frequency=leaderboard_data.get('update_frequency', 'daily'),
                created_by=leaderboard_data.get('created_by')
            )
            
            self.db.add(leaderboard)
            self.db.commit()
            self.db.refresh(leaderboard)
            
            logger.info(f"Created leaderboard: {leaderboard.name}")
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error creating leaderboard: {str(e)}")
            self.db.rollback()
            raise
    
    def get_leaderboard(self, leaderboard_id: int, user_id: Optional[int] = None,
                       limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get leaderboard data with optional user position"""
        try:
            leaderboard = self.db.query(Leaderboard).get(leaderboard_id)
            if not leaderboard:
                return {}
            
            # Get leaderboard entries
            entries_query = self.db.query(LeaderboardEntry).filter_by(
                leaderboard_id=leaderboard_id
            ).order_by(LeaderboardEntry.rank.asc())
            
            total_entries = entries_query.count()
            entries = entries_query.offset(offset).limit(limit).all()
            
            # Get user's position if requested
            user_position = None
            if user_id:
                user_entry = self.db.query(LeaderboardEntry).filter_by(
                    leaderboard_id=leaderboard_id,
                    user_id=user_id
                ).first()
                
                if user_entry:
                    user_position = {
                        'rank': user_entry.rank,
                        'score': user_entry.score,
                        'metadata': user_entry.metadata
                    }
            
            # Format entries
            formatted_entries = []
            for entry in entries:
                user = self.db.query(User).get(entry.user_id)
                formatted_entries.append({
                    'rank': entry.rank,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'display_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                        'avatar_url': getattr(user, 'avatar_url', None)
                    },
                    'score': entry.score,
                    'metadata': entry.metadata,
                    'last_updated': entry.last_updated
                })
            
            return {
                'leaderboard': {
                    'id': leaderboard.id,
                    'name': leaderboard.name,
                    'description': leaderboard.description,
                    'type': leaderboard.leaderboard_type,
                    'time_frame': leaderboard.time_frame,
                    'last_updated': leaderboard.last_updated
                },
                'entries': formatted_entries,
                'total_entries': total_entries,
                'user_position': user_position,
                'pagination': {
                    'offset': offset,
                    'limit': limit,
                    'has_more': offset + limit < total_entries
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return {}
    
    def get_leaderboard_by_type(self, leaderboard_type: str, time_frame: str = TimeFrame.ALL_TIME.value,
                               limit: int = 50, criteria: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get leaderboard data by type and time frame"""
        try:
            # Check if we have a calculator for this type
            lb_type = LeaderboardType(leaderboard_type)
            if lb_type not in self.leaderboard_calculators:
                return []
            
            # Calculate leaderboard data
            calculator = self.leaderboard_calculators[lb_type]
            return calculator(time_frame, limit, criteria or {})
            
        except Exception as e:
            logger.error(f"Error getting leaderboard by type: {str(e)}")
            return []
    
    def update_leaderboard(self, leaderboard_id: int) -> bool:
        """Update a leaderboard with fresh data"""
        try:
            leaderboard = self.db.query(Leaderboard).get(leaderboard_id)
            if not leaderboard:
                return False
            
            # Calculate new rankings
            lb_type = LeaderboardType(leaderboard.leaderboard_type)
            if lb_type not in self.leaderboard_calculators:
                return False
            
            calculator = self.leaderboard_calculators[lb_type]
            new_data = calculator(leaderboard.time_frame, leaderboard.max_entries, leaderboard.criteria)
            
            # Clear existing entries
            self.db.query(LeaderboardEntry).filter_by(leaderboard_id=leaderboard_id).delete()
            
            # Insert new entries
            for rank, entry in enumerate(new_data, 1):
                leaderboard_entry = LeaderboardEntry(
                    leaderboard_id=leaderboard_id,
                    user_id=entry['user_id'],
                    rank=rank,
                    score=entry['score'],
                    metadata=entry.get('metadata', {}),
                    last_updated=datetime.utcnow()
                )
                self.db.add(leaderboard_entry)
            
            # Update leaderboard timestamp
            leaderboard.last_updated = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Updated leaderboard {leaderboard_id} with {len(new_data)} entries")
            return True
            
        except Exception as e:
            logger.error(f"Error updating leaderboard: {str(e)}")
            self.db.rollback()
            return False
    
    def get_user_rankings(self, user_id: int) -> Dict[str, Any]:
        """Get user's rankings across all leaderboards"""
        try:
            rankings = {}
            
            # Get user's positions in all active leaderboards
            entries = self.db.query(LeaderboardEntry, Leaderboard).join(Leaderboard).filter(
                LeaderboardEntry.user_id == user_id,
                Leaderboard.is_active == True
            ).all()
            
            for entry, leaderboard in entries:
                rankings[leaderboard.leaderboard_type] = {
                    'leaderboard_id': leaderboard.id,
                    'leaderboard_name': leaderboard.name,
                    'rank': entry.rank,
                    'score': entry.score,
                    'time_frame': leaderboard.time_frame,
                    'last_updated': entry.last_updated
                }
            
            # Calculate overall ranking score
            overall_score = self._calculate_overall_ranking_score(rankings)
            
            return {
                'rankings': rankings,
                'overall_score': overall_score,
                'total_leaderboards': len(rankings)
            }
            
        except Exception as e:
            logger.error(f"Error getting user rankings: {str(e)}")
            return {}
    
    def create_competition(self, competition_data: Dict[str, Any]) -> Competition:
        """Create a new competition"""
        try:
            competition = Competition(
                name=competition_data['name'],
                description=competition_data.get('description', ''),
                competition_type=competition_data['type'],
                start_date=competition_data['start_date'],
                end_date=competition_data['end_date'],
                rules=competition_data.get('rules', {}),
                prizes=competition_data.get('prizes', {}),
                max_participants=competition_data.get('max_participants'),
                is_active=competition_data.get('is_active', True),
                is_public=competition_data.get('is_public', True),
                created_by=competition_data.get('created_by')
            )
            
            self.db.add(competition)
            self.db.commit()
            self.db.refresh(competition)
            
            logger.info(f"Created competition: {competition.name}")
            return competition
            
        except Exception as e:
            logger.error(f"Error creating competition: {str(e)}")
            self.db.rollback()
            raise
    
    def get_active_competitions(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get active competitions"""
        try:
            now = datetime.utcnow()
            
            query = self.db.query(Competition).filter(
                Competition.is_active == True,
                Competition.start_date <= now,
                Competition.end_date >= now
            )
            
            competitions = query.all()
            
            result = []
            for comp in competitions:
                competition_data = {
                    'id': comp.id,
                    'name': comp.name,
                    'description': comp.description,
                    'type': comp.competition_type,
                    'start_date': comp.start_date,
                    'end_date': comp.end_date,
                    'rules': comp.rules,
                    'prizes': comp.prizes,
                    'max_participants': comp.max_participants,
                    'is_public': comp.is_public,
                    'participant_count': self._get_competition_participant_count(comp.id)
                }
                
                # Add user participation status if user_id provided
                if user_id:
                    competition_data['user_participating'] = self._is_user_participating(comp.id, user_id)
                    competition_data['user_rank'] = self._get_user_competition_rank(comp.id, user_id)
                
                result.append(competition_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting active competitions: {str(e)}")
            return []
    
    def get_global_leaderboards(self, limit: int = 10) -> Dict[str, Any]:
        """Get multiple global leaderboards"""
        try:
            leaderboards = {}
            
            # XP Leaderboard
            leaderboards['xp'] = self.get_leaderboard_by_type(
                LeaderboardType.XP.value, TimeFrame.ALL_TIME.value, limit
            )
            
            # Level Leaderboard
            leaderboards['level'] = self.get_leaderboard_by_type(
                LeaderboardType.LEVEL.value, TimeFrame.ALL_TIME.value, limit
            )
            
            # Weekly XP Leaderboard
            leaderboards['weekly_xp'] = self.get_leaderboard_by_type(
                LeaderboardType.XP.value, TimeFrame.WEEKLY.value, limit
            )
            
            # Badges Leaderboard
            leaderboards['badges'] = self.get_leaderboard_by_type(
                LeaderboardType.BADGES.value, TimeFrame.ALL_TIME.value, limit
            )
            
            return leaderboards
            
        except Exception as e:
            logger.error(f"Error getting global leaderboards: {str(e)}")
            return {}
    
    # Leaderboard calculators for different types
    
    def _calculate_xp_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate XP-based leaderboard"""
        try:
            if time_frame == TimeFrame.ALL_TIME.value:
                # Use total_xp from user table
                results = self.db.query(User).filter(
                    User.total_xp.isnot(None),
                    User.total_xp > 0
                ).order_by(desc(User.total_xp)).limit(limit).all()
                
                return [
                    {
                        'user_id': user.id,
                        'score': user.total_xp,
                        'metadata': {'username': user.username}
                    }
                    for user in results
                ]
            else:
                # Calculate from XP transactions for time-based leaderboards
                start_date = self._get_timeframe_start_date(time_frame)
                
                # This would require XPTransaction model
                # For now, returning empty list
                return []
                
        except Exception as e:
            logger.error(f"Error calculating XP leaderboard: {str(e)}")
            return []
    
    def _calculate_level_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate level-based leaderboard"""
        try:
            results = self.db.query(User).filter(
                User.level.isnot(None),
                User.level > 0
            ).order_by(desc(User.level), desc(User.total_xp)).limit(limit).all()
            
            return [
                {
                    'user_id': user.id,
                    'score': user.level,
                    'metadata': {
                        'username': user.username,
                        'total_xp': user.total_xp
                    }
                }
                for user in results
            ]
            
        except Exception as e:
            logger.error(f"Error calculating level leaderboard: {str(e)}")
            return []
    
    def _calculate_badges_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate badges-based leaderboard"""
        try:
            results = self.db.query(User).filter(
                User.total_badges.isnot(None),
                User.total_badges > 0
            ).order_by(desc(User.total_badges)).limit(limit).all()
            
            return [
                {
                    'user_id': user.id,
                    'score': user.total_badges,
                    'metadata': {'username': user.username}
                }
                for user in results
            ]
            
        except Exception as e:
            logger.error(f"Error calculating badges leaderboard: {str(e)}")
            return []
    
    def _calculate_achievements_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate achievements-based leaderboard"""
        try:
            # This would require UserAchievement model
            # For now, returning empty list
            return []
            
        except Exception as e:
            logger.error(f"Error calculating achievements leaderboard: {str(e)}")
            return []
    
    def _calculate_evaluation_score_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate evaluation score-based leaderboard"""
        try:
            start_date = self._get_timeframe_start_date(time_frame)
            
            # Calculate average scores
            query = self.db.query(
                Evaluation.user_id,
                func.avg(Evaluation.score).label('avg_score'),
                func.count(Evaluation.id).label('evaluation_count')
            ).filter(
                Evaluation.status == 'completed',
                Evaluation.score.isnot(None)
            )
            
            if start_date:
                query = query.filter(Evaluation.completed_at >= start_date)
            
            results = query.group_by(Evaluation.user_id).having(
                func.count(Evaluation.id) >= criteria.get('min_evaluations', 1)
            ).order_by(desc('avg_score')).limit(limit).all()
            
            leaderboard_data = []
            for user_id, avg_score, eval_count in results:
                user = self.db.query(User).get(user_id)
                if user:
                    leaderboard_data.append({
                        'user_id': user_id,
                        'score': float(avg_score),
                        'metadata': {
                            'username': user.username,
                            'evaluation_count': eval_count
                        }
                    })
            
            return leaderboard_data
            
        except Exception as e:
            logger.error(f"Error calculating evaluation score leaderboard: {str(e)}")
            return []
    
    def _calculate_completion_rate_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate completion rate-based leaderboard"""
        try:
            # This would calculate program/module completion rates
            # For now, returning empty list
            return []
            
        except Exception as e:
            logger.error(f"Error calculating completion rate leaderboard: {str(e)}")
            return []
    
    def _calculate_streak_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate streak-based leaderboard"""
        try:
            # This would calculate learning streaks
            # For now, returning empty list
            return []
            
        except Exception as e:
            logger.error(f"Error calculating streak leaderboard: {str(e)}")
            return []
    
    def _calculate_program_progress_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate program progress-based leaderboard"""
        try:
            program_id = criteria.get('program_id')
            if not program_id:
                return []
            
            # Calculate completion percentage for specific program
            # This would require more complex query with program structure
            # For now, returning empty list
            return []
            
        except Exception as e:
            logger.error(f"Error calculating program progress leaderboard: {str(e)}")
            return []
    
    def _calculate_participation_leaderboard(self, time_frame: str, limit: int, criteria: Dict) -> List[Dict[str, Any]]:
        """Calculate participation-based leaderboard"""
        try:
            start_date = self._get_timeframe_start_date(time_frame)
            
            # Count activities/evaluations
            query = self.db.query(
                Evaluation.user_id,
                func.count(Evaluation.id).label('activity_count')
            )
            
            if start_date:
                query = query.filter(Evaluation.created_at >= start_date)
            
            results = query.group_by(Evaluation.user_id).order_by(
                desc('activity_count')
            ).limit(limit).all()
            
            leaderboard_data = []
            for user_id, activity_count in results:
                user = self.db.query(User).get(user_id)
                if user:
                    leaderboard_data.append({
                        'user_id': user_id,
                        'score': activity_count,
                        'metadata': {'username': user.username}
                    })
            
            return leaderboard_data
            
        except Exception as e:
            logger.error(f"Error calculating participation leaderboard: {str(e)}")
            return []
    
    # Helper methods
    
    def _get_timeframe_start_date(self, time_frame: str) -> Optional[datetime]:
        """Get start date for time frame"""
        now = datetime.utcnow()
        
        if time_frame == TimeFrame.DAILY.value:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_frame == TimeFrame.WEEKLY.value:
            days_since_monday = now.weekday()
            return (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_frame == TimeFrame.MONTHLY.value:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_frame == TimeFrame.YEARLY.value:
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # ALL_TIME
            return None
    
    def _calculate_overall_ranking_score(self, rankings: Dict[str, Any]) -> float:
        """Calculate overall ranking score across all leaderboards"""
        try:
            if not rankings:
                return 0.0
            
            # Weight different leaderboard types
            weights = {
                'xp': 0.3,
                'level': 0.25,
                'badges': 0.2,
                'evaluation_score': 0.15,
                'participation': 0.1
            }
            
            total_score = 0.0
            total_weight = 0.0
            
            for lb_type, ranking in rankings.items():
                weight = weights.get(lb_type, 0.1)
                # Convert rank to score (lower rank = higher score)
                rank_score = max(0, 100 - ranking['rank'])
                total_score += rank_score * weight
                total_weight += weight
            
            return total_score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating overall ranking score: {str(e)}")
            return 0.0
    
    def _get_competition_participant_count(self, competition_id: int) -> int:
        """Get number of participants in a competition"""
        # This would require a CompetitionParticipant model
        return 0
    
    def _is_user_participating(self, competition_id: int, user_id: int) -> bool:
        """Check if user is participating in a competition"""
        # This would check CompetitionParticipant table
        return False
    
    def _get_user_competition_rank(self, competition_id: int, user_id: int) -> Optional[int]:
        """Get user's rank in a competition"""
        # This would calculate rank in competition
        return None