"""Comprehensive Gamification Service for BDC application."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.gamification import (
    Badge, UserBadge, UserXP, PointTransaction, Leaderboard, LeaderboardEntry,
    Challenge, ChallengeParticipant, GamificationTeam, Reward, RewardRedemption,
    UserGoal, GamificationEvent, UserProgress,
    AchievementCategory, PointActivityType, LeaderboardType, ChallengeType, RewardType
)
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.program import ProgramEnrollment
from app.services.notification_service import NotificationService


class GamificationService:
    """Main service for gamification features."""
    
    def __init__(self):
        # self.notification_service = NotificationService()  # TODO: Fix repository dependency
        self.notification_service = None
    
    # ========== User XP and Levels Management ==========
    
    def get_user_xp(self, user_id: int) -> UserXP:
        """Get or create user XP profile."""
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            user_xp = UserXP(user_id=user_id)
            db.session.add(user_xp)
            db.session.commit()
        return user_xp
    
    def award_points(self, user_id: int, points: int, activity_type: PointActivityType, 
                    related_entity_type: str = None, related_entity_id: int = None,
                    metadata: dict = None) -> int:
        """Award points to a user and handle level progression."""
        user_xp = self.get_user_xp(user_id)
        
        # Award points and handle level up
        actual_points = user_xp.add_xp(points, activity_type, metadata)
        
        # Log the transaction with related entity info
        if user_xp.point_transactions.filter_by(
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        ).first() is None:  # Prevent duplicate points for same entity
            
            transaction = PointTransaction(
                user_xp_id=user_xp.id,
                activity_type=activity_type,
                points_earned=actual_points,
                multiplier_applied=user_xp.xp_multiplier,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                metadata=metadata
            )
            db.session.add(transaction)
        
        # Check for achievements triggered by points/level
        self.check_and_award_achievements(user_id, activity_type, metadata)
        
        # Update leaderboards
        self.update_user_leaderboards(user_id)
        
        # Log gamification event
        self.log_event(user_id, 'points_earned', {
            'points': actual_points,
            'activity_type': activity_type.value,
            'total_xp': user_xp.total_xp,
            'level': user_xp.current_level
        })
        
        db.session.commit()
        return actual_points
    
    def update_streak(self, user_id: int) -> int:
        """Update user's activity streak."""
        user_xp = self.get_user_xp(user_id)
        streak = user_xp.update_streak()
        
        # Award streak bonus points
        if streak > 1:
            streak_bonus = min(streak * 5, 50)  # Max 50 bonus points
            self.award_points(user_id, streak_bonus, PointActivityType.STREAK_BONUS, 
                            metadata={'streak_length': streak})
        
        # Check for streak achievements
        self.check_streak_achievements(user_id, streak)
        
        db.session.commit()
        return streak
    
    def apply_xp_multiplier(self, user_id: int, multiplier: float, duration_hours: int) -> bool:
        """Apply temporary XP multiplier to user."""
        user_xp = self.get_user_xp(user_id)
        user_xp.xp_multiplier = multiplier
        user_xp.multiplier_expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        db.session.commit()
        return True
    
    # ========== Badge and Achievement System ==========
    
    def create_badge(self, name: str, description: str, category: AchievementCategory,
                    unlock_conditions: dict, rarity: str = 'common', 
                    points_value: int = 0, icon_url: str = None, 
                    is_secret: bool = False) -> Badge:
        """Create a new badge."""
        badge = Badge(
            name=name,
            description=description,
            category=category,
            unlock_conditions=unlock_conditions,
            rarity=rarity,
            points_value=points_value,
            icon_url=icon_url,
            is_secret=is_secret
        )
        db.session.add(badge)
        db.session.commit()
        return badge
    
    def award_badge(self, user_id: int, badge_id: int, metadata: dict = None) -> UserBadge:
        """Award a badge to a user."""
        # Check if user already has this badge
        existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first()
        if existing:
            return existing
        
        badge = Badge.query.get(badge_id)
        if not badge:
            raise ValueError("Badge not found")
        
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            metadata=metadata
        )
        db.session.add(user_badge)
        
        # Award badge points
        if badge.points_value > 0:
            self.award_points(user_id, badge.points_value, PointActivityType.BADGE_EARNED,
                            'badge', badge_id, {'badge_name': badge.name})
        
        # Send notification
        user = User.query.get(user_id)
        self.notification_service.create_notification(
            user_id, f"🏆 Badge Earned: {badge.name}",
            f"Congratulations! You've earned the {badge.name} badge."
        )
        
        # Log event
        self.log_event(user_id, 'badge_earned', {
            'badge_id': badge_id,
            'badge_name': badge.name,
            'category': badge.category.value,
            'rarity': badge.rarity
        })
        
        db.session.commit()
        return user_badge
    
    def check_and_award_achievements(self, user_id: int, activity_type: PointActivityType = None, metadata: dict = None):
        """Check and award achievements based on user activity."""
        user_xp = self.get_user_xp(user_id)
        
        # Level-based achievements
        self._check_level_achievements(user_id, user_xp.current_level)
        
        # Activity-specific achievements
        if activity_type:
            self._check_activity_achievements(user_id, activity_type, metadata)
        
        # Progress-based achievements
        self._check_progress_achievements(user_id)
    
    def _check_level_achievements(self, user_id: int, level: int):
        """Check for level-based achievements."""
        level_badges = Badge.query.filter(
            Badge.category == AchievementCategory.MASTERY,
            Badge.unlock_conditions.contains({'type': 'level'})
        ).all()
        
        for badge in level_badges:
            required_level = badge.unlock_conditions.get('level', 0)
            if level >= required_level:
                # Check if user already has this badge
                if not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
                    self.award_badge(user_id, badge.id, {'level_achieved': level})
    
    def _check_activity_achievements(self, user_id: int, activity_type: PointActivityType, metadata: dict):
        """Check for activity-based achievements."""
        activity_badges = Badge.query.filter(
            Badge.unlock_conditions.contains({'activity_type': activity_type.value})
        ).all()
        
        for badge in activity_badges:
            conditions = badge.unlock_conditions
            if self._evaluate_achievement_conditions(user_id, conditions):
                if not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
                    self.award_badge(user_id, badge.id, metadata)
    
    def _check_progress_achievements(self, user_id: int):
        """Check for progress-based achievements."""
        # Check evaluation completion achievements
        evaluation_count = Evaluation.query.filter_by(
            beneficiary_id=user_id, status='completed'
        ).count()
        
        # Check program completion achievements
        program_completions = ProgramEnrollment.query.filter_by(
            user_id=user_id, status='completed'
        ).count()
        
        # Add more progress checks as needed
        progress_data = {
            'evaluations_completed': evaluation_count,
            'programs_completed': program_completions
        }
        
        # Check badges that require progress milestones
        progress_badges = Badge.query.filter(
            Badge.category == AchievementCategory.PARTICIPATION
        ).all()
        
        for badge in progress_badges:
            if self._evaluate_progress_conditions(progress_data, badge.unlock_conditions):
                if not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
                    self.award_badge(user_id, badge.id, progress_data)
    
    def check_streak_achievements(self, user_id: int, streak: int):
        """Check for streak-based achievements."""
        streak_badges = Badge.query.filter(
            Badge.category == AchievementCategory.CONSISTENCY,
            Badge.unlock_conditions.contains({'type': 'streak'})
        ).all()
        
        for badge in streak_badges:
            required_streak = badge.unlock_conditions.get('streak', 0)
            if streak >= required_streak:
                if not UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
                    self.award_badge(user_id, badge.id, {'streak_achieved': streak})
    
    def _evaluate_achievement_conditions(self, user_id: int, conditions: dict) -> bool:
        """Evaluate if achievement conditions are met."""
        # Implement specific condition evaluation logic
        condition_type = conditions.get('type')
        
        if condition_type == 'count':
            # Count-based conditions (e.g., complete X evaluations)
            entity_type = conditions.get('entity_type')
            required_count = conditions.get('count', 1)
            
            if entity_type == 'evaluation':
                count = Evaluation.query.filter_by(
                    beneficiary_id=user_id, status='completed'
                ).count()
                return count >= required_count
            
            elif entity_type == 'perfect_score':
                count = Evaluation.query.filter_by(
                    beneficiary_id=user_id, score=100.0
                ).count()
                return count >= required_count
        
        elif condition_type == 'score_threshold':
            # Score-based conditions
            threshold = conditions.get('threshold', 0)
            evaluation = Evaluation.query.filter_by(
                beneficiary_id=user_id
            ).order_by(desc(Evaluation.score)).first()
            
            return evaluation and evaluation.score >= threshold
        
        return False
    
    def _evaluate_progress_conditions(self, progress_data: dict, conditions: dict) -> bool:
        """Evaluate progress-based conditions."""
        for key, required_value in conditions.items():
            if key in progress_data and progress_data[key] >= required_value:
                return True
        return False
    
    def get_user_badges(self, user_id: int, category: AchievementCategory = None) -> List[UserBadge]:
        """Get user's earned badges."""
        query = UserBadge.query.filter_by(user_id=user_id).options(joinedload(UserBadge.badge))
        
        if category:
            query = query.join(Badge).filter(Badge.category == category)
        
        return query.order_by(desc(UserBadge.earned_at)).all()
    
    def get_available_badges(self, user_id: int, category: AchievementCategory = None) -> List[Badge]:
        """Get badges available to earn (not yet earned by user)."""
        earned_badge_ids = db.session.query(UserBadge.badge_id).filter_by(user_id=user_id).subquery()
        
        query = Badge.query.filter(
            Badge.is_active == True,
            ~Badge.id.in_(earned_badge_ids)
        )
        
        if category:
            query = query.filter(Badge.category == category)
        
        return query.order_by(Badge.rarity, Badge.name).all()
    
    # ========== Leaderboard System ==========
    
    def create_leaderboard(self, name: str, leaderboard_type: LeaderboardType, 
                          metric: str, description: str = None, tenant_id: int = None,
                          start_date: datetime = None, end_date: datetime = None,
                          max_entries: int = 100) -> Leaderboard:
        """Create a new leaderboard."""
        leaderboard = Leaderboard(
            name=name,
            type=leaderboard_type,
            metric=metric,
            description=description,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            max_entries=max_entries
        )
        db.session.add(leaderboard)
        db.session.commit()
        return leaderboard
    
    def update_user_leaderboards(self, user_id: int):
        """Update user's position in all relevant leaderboards."""
        user_xp = self.get_user_xp(user_id)
        
        # Update global leaderboards
        global_boards = Leaderboard.query.filter_by(
            type=LeaderboardType.GLOBAL, is_active=True
        ).all()
        
        for board in global_boards:
            self._update_leaderboard_entry(board, user_id, user_xp)
        
        # Update class leaderboards (if user has tenant)
        user = User.query.get(user_id)
        if user and user.tenant_id:
            class_boards = Leaderboard.query.filter_by(
                type=LeaderboardType.CLASS, 
                tenant_id=user.tenant_id,
                is_active=True
            ).all()
            
            for board in class_boards:
                self._update_leaderboard_entry(board, user_id, user_xp)
        
        # Update time-based leaderboards
        self._update_time_based_leaderboards(user_id, user_xp)
    
    def _update_leaderboard_entry(self, leaderboard: Leaderboard, user_id: int, user_xp: UserXP):
        """Update or create a leaderboard entry for a user."""
        score = self._calculate_leaderboard_score(leaderboard.metric, user_xp)
        
        entry = LeaderboardEntry.query.filter_by(
            leaderboard_id=leaderboard.id, user_id=user_id
        ).first()
        
        if entry:
            entry.score = score
            entry.updated_at = datetime.utcnow()
        else:
            entry = LeaderboardEntry(
                leaderboard_id=leaderboard.id,
                user_id=user_id,
                score=score,
                position=0  # Will be calculated later
            )
            db.session.add(entry)
        
        # Recalculate positions for this leaderboard
        self._recalculate_leaderboard_positions(leaderboard.id)
    
    def _calculate_leaderboard_score(self, metric: str, user_xp: UserXP) -> float:
        """Calculate score for leaderboard metric."""
        if metric == 'total_xp':
            return float(user_xp.total_xp)
        elif metric == 'level':
            return float(user_xp.current_level)
        elif metric == 'current_streak':
            return float(user_xp.current_streak)
        elif metric == 'longest_streak':
            return float(user_xp.longest_streak)
        else:
            return 0.0
    
    def _recalculate_leaderboard_positions(self, leaderboard_id: int):
        """Recalculate positions for all entries in a leaderboard."""
        entries = LeaderboardEntry.query.filter_by(
            leaderboard_id=leaderboard_id
        ).order_by(desc(LeaderboardEntry.score)).all()
        
        for i, entry in enumerate(entries, 1):
            entry.position = i
            if i > entry.leaderboard.max_entries:
                db.session.delete(entry)
    
    def _update_time_based_leaderboards(self, user_id: int, user_xp: UserXP):
        """Update weekly and monthly leaderboards."""
        now = datetime.utcnow()
        
        # Weekly leaderboards
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)
        
        weekly_boards = Leaderboard.query.filter_by(
            type=LeaderboardType.WEEKLY, is_active=True
        ).filter(
            Leaderboard.start_date >= week_start,
            Leaderboard.end_date <= week_end
        ).all()
        
        for board in weekly_boards:
            self._update_leaderboard_entry(board, user_id, user_xp)
        
        # Monthly leaderboards
        month_start = now.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        monthly_boards = Leaderboard.query.filter_by(
            type=LeaderboardType.MONTHLY, is_active=True
        ).filter(
            Leaderboard.start_date >= month_start,
            Leaderboard.end_date <= month_end
        ).all()
        
        for board in monthly_boards:
            self._update_leaderboard_entry(board, user_id, user_xp)
    
    def get_leaderboard(self, leaderboard_id: int, limit: int = 10) -> Dict:
        """Get leaderboard with top entries."""
        leaderboard = Leaderboard.query.get(leaderboard_id)
        if not leaderboard:
            return None
        
        entries = LeaderboardEntry.query.filter_by(
            leaderboard_id=leaderboard_id
        ).options(joinedload(LeaderboardEntry.user)).order_by(
            LeaderboardEntry.position
        ).limit(limit).all()
        
        return {
            'leaderboard': leaderboard.to_dict(),
            'entries': [entry.to_dict() for entry in entries]
        }
    
    def get_user_leaderboard_position(self, user_id: int, leaderboard_id: int) -> Optional[int]:
        """Get user's position in a specific leaderboard."""
        entry = LeaderboardEntry.query.filter_by(
            leaderboard_id=leaderboard_id, user_id=user_id
        ).first()
        
        return entry.position if entry else None
    
    # ========== Challenge System ==========
    
    def create_challenge(self, title: str, description: str, challenge_type: ChallengeType,
                        goals: dict, rewards: dict = None, difficulty: str = 'medium',
                        start_date: datetime = None, end_date: datetime = None,
                        duration_hours: int = None, max_participants: int = None,
                        tenant_id: int = None) -> Challenge:
        """Create a new challenge."""
        challenge = Challenge(
            title=title,
            description=description,
            type=challenge_type,
            goals=goals,
            rewards=rewards,
            difficulty=difficulty,
            start_date=start_date,
            end_date=end_date,
            duration_hours=duration_hours,
            max_participants=max_participants,
            tenant_id=tenant_id
        )
        db.session.add(challenge)
        db.session.commit()
        return challenge
    
    def join_challenge(self, user_id: int, challenge_id: int, team_id: int = None) -> ChallengeParticipant:
        """Join a user to a challenge."""
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            raise ValueError("Challenge not found")
        
        if not challenge.is_ongoing:
            raise ValueError("Challenge is not active")
        
        # Check if already participating
        existing = ChallengeParticipant.query.filter_by(
            user_id=user_id, challenge_id=challenge_id
        ).first()
        if existing:
            return existing
        
        # Check participant limits
        if challenge.max_participants:
            current_count = ChallengeParticipant.query.filter_by(
                challenge_id=challenge_id
            ).count()
            if current_count >= challenge.max_participants:
                raise ValueError("Challenge is full")
        
        participant = ChallengeParticipant(
            user_id=user_id,
            challenge_id=challenge_id,
            team_id=team_id
        )
        db.session.add(participant)
        
        # Log event
        self.log_event(user_id, 'challenge_joined', {
            'challenge_id': challenge_id,
            'challenge_title': challenge.title
        })
        
        db.session.commit()
        return participant
    
    def update_challenge_progress(self, user_id: int, challenge_id: int, 
                                 goal_key: str, value: float):
        """Update user's progress on a challenge goal."""
        participant = ChallengeParticipant.query.filter_by(
            user_id=user_id, challenge_id=challenge_id
        ).first()
        
        if not participant:
            raise ValueError("User is not participating in this challenge")
        
        participant.update_progress(goal_key, value)
        
        # Check if challenge is completed
        if participant.is_completed:
            self._handle_challenge_completion(participant)
        
        db.session.commit()
    
    def _handle_challenge_completion(self, participant: ChallengeParticipant):
        """Handle challenge completion rewards and notifications."""
        challenge = participant.challenge
        user_id = participant.user_id
        
        # Award completion rewards
        if challenge.rewards:
            for reward_type, reward_value in challenge.rewards.items():
                if reward_type == 'points':
                    self.award_points(user_id, reward_value, PointActivityType.CHALLENGE_COMPLETION,
                                    'challenge', challenge.id, {'challenge_title': challenge.title})
                elif reward_type == 'badge_id':
                    self.award_badge(user_id, reward_value, {'challenge_id': challenge.id})
        
        # Send notification
        self.notification_service.create_notification(
            user_id, f"🎉 Challenge Completed: {challenge.title}",
            f"Congratulations! You've completed the {challenge.title} challenge."
        )
        
        # Log event
        self.log_event(user_id, 'challenge_completed', {
            'challenge_id': challenge.id,
            'challenge_title': challenge.title,
            'completion_time': participant.completed_at.isoformat()
        })
    
    def get_active_challenges(self, user_id: int = None, tenant_id: int = None) -> List[Challenge]:
        """Get active challenges for a user or tenant."""
        query = Challenge.query.filter(Challenge.is_active == True)
        
        if tenant_id:
            query = query.filter(or_(Challenge.tenant_id == tenant_id, Challenge.tenant_id.is_(None)))
        
        now = datetime.utcnow()
        query = query.filter(
            or_(
                Challenge.start_date.is_(None),
                Challenge.start_date <= now
            ),
            or_(
                Challenge.end_date.is_(None),
                Challenge.end_date >= now
            )
        )
        
        return query.order_by(desc(Challenge.is_featured), Challenge.created_at).all()
    
    def get_user_challenges(self, user_id: int) -> List[ChallengeParticipant]:
        """Get user's challenge participations."""
        return ChallengeParticipant.query.filter_by(
            user_id=user_id
        ).options(joinedload(ChallengeParticipant.challenge)).order_by(
            desc(ChallengeParticipant.joined_at)
        ).all()
    
    # ========== Team System ==========
    
    def create_team(self, name: str, leader_id: int, description: str = None,
                   max_members: int = 10, is_open: bool = True, 
                   tenant_id: int = None) -> GamificationTeam:
        """Create a new team."""
        team = GamificationTeam(
            name=name,
            leader_id=leader_id,
            description=description,
            max_members=max_members,
            is_open=is_open,
            tenant_id=tenant_id
        )
        db.session.add(team)
        
        # Add leader as member
        leader = User.query.get(leader_id)
        team.members.append(leader)
        
        db.session.commit()
        return team
    
    def join_team(self, user_id: int, team_id: int) -> bool:
        """Join a user to a team."""
        team = GamificationTeam.query.get(team_id)
        user = User.query.get(user_id)
        
        if not team or not user:
            return False
        
        if len(team.members) >= team.max_members:
            return False
        
        if user not in team.members:
            team.members.append(user)
            db.session.commit()
        
        return True
    
    def leave_team(self, user_id: int, team_id: int) -> bool:
        """Remove a user from a team."""
        team = GamificationTeam.query.get(team_id)
        user = User.query.get(user_id)
        
        if not team or not user:
            return False
        
        if user in team.members:
            team.members.remove(user)
            
            # If leader leaves, assign new leader
            if team.leader_id == user_id and team.members:
                team.leader_id = team.members[0].id
            
            db.session.commit()
        
        return True
    
    # ========== Reward System ==========
    
    def create_reward(self, name: str, reward_type: RewardType, cost: int,
                     value: dict, description: str = None, rarity: str = 'common',
                     total_quantity: int = None, available_from: datetime = None,
                     available_until: datetime = None) -> Reward:
        """Create a new reward."""
        reward = Reward(
            name=name,
            type=reward_type,
            cost=cost,
            value=value,
            description=description,
            rarity=rarity,
            total_quantity=total_quantity,
            remaining_quantity=total_quantity,
            available_from=available_from,
            available_until=available_until
        )
        db.session.add(reward)
        db.session.commit()
        return reward
    
    def redeem_reward(self, user_id: int, reward_id: int) -> RewardRedemption:
        """Redeem a reward for a user."""
        reward = Reward.query.get(reward_id)
        user_xp = self.get_user_xp(user_id)
        
        if not reward or not reward.is_available:
            raise ValueError("Reward not available")
        
        if user_xp.total_xp < reward.cost:
            raise ValueError("Insufficient points")
        
        # Deduct points
        user_xp.total_xp -= reward.cost
        
        # Reduce remaining quantity
        if reward.remaining_quantity:
            reward.remaining_quantity -= 1
        
        # Create redemption record
        redemption = RewardRedemption(
            user_id=user_id,
            reward_id=reward_id,
            points_spent=reward.cost
        )
        db.session.add(redemption)
        
        # Log transaction (negative points)
        transaction = PointTransaction(
            user_xp_id=user_xp.id,
            activity_type=PointActivityType.POINTS,
            points_earned=-reward.cost,
            related_entity_type='reward',
            related_entity_id=reward_id,
            metadata={'reward_name': reward.name}
        )
        db.session.add(transaction)
        
        # Send notification
        self.notification_service.create_notification(
            user_id, f"🎁 Reward Redeemed: {reward.name}",
            f"You've successfully redeemed {reward.name} for {reward.cost} points."
        )
        
        # Log event
        self.log_event(user_id, 'reward_redeemed', {
            'reward_id': reward_id,
            'reward_name': reward.name,
            'points_spent': reward.cost
        })
        
        db.session.commit()
        return redemption
    
    def get_available_rewards(self, user_id: int = None) -> List[Reward]:
        """Get available rewards, optionally filtered by user's points."""
        query = Reward.query.filter(Reward.is_active == True)
        
        now = datetime.utcnow()
        query = query.filter(
            or_(Reward.available_from.is_(None), Reward.available_from <= now),
            or_(Reward.available_until.is_(None), Reward.available_until >= now),
            or_(Reward.remaining_quantity.is_(None), Reward.remaining_quantity > 0)
        )
        
        if user_id:
            user_xp = self.get_user_xp(user_id)
            query = query.filter(Reward.cost <= user_xp.total_xp)
        
        return query.order_by(Reward.cost, Reward.name).all()
    
    # ========== Goal System ==========
    
    def create_user_goal(self, user_id: int, title: str, goal_type: str,
                        target_value: float, description: str = None,
                        deadline: datetime = None) -> UserGoal:
        """Create a personal goal for a user."""
        goal = UserGoal(
            user_id=user_id,
            title=title,
            description=description,
            goal_type=goal_type,
            target_value=target_value,
            deadline=deadline
        )
        db.session.add(goal)
        db.session.commit()
        return goal
    
    def update_goal_progress(self, user_id: int, goal_type: str, new_value: float):
        """Update progress on user goals."""
        goals = UserGoal.query.filter_by(
            user_id=user_id, goal_type=goal_type, is_active=True
        ).all()
        
        for goal in goals:
            goal.update_progress(new_value)
            if goal.is_completed:
                # Award completion points
                self.award_points(user_id, 100, PointActivityType.MILESTONE,
                                'goal', goal.id, {'goal_title': goal.title})
        
        db.session.commit()
    
    def get_user_goals(self, user_id: int, active_only: bool = True) -> List[UserGoal]:
        """Get user's goals."""
        query = UserGoal.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(desc(UserGoal.created_at)).all()
    
    # ========== Analytics and Events ==========
    
    def log_event(self, user_id: int, event_type: str, event_data: dict,
                 session_id: str = None, ip_address: str = None, 
                 user_agent: str = None):
        """Log a gamification event for analytics."""
        event = GamificationEvent(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(event)
        # Note: commit should be handled by caller
    
    def get_user_progress_summary(self, user_id: int) -> Dict:
        """Get comprehensive progress summary for a user."""
        user_xp = self.get_user_xp(user_id)
        badges = self.get_user_badges(user_id)
        goals = self.get_user_goals(user_id)
        challenges = self.get_user_challenges(user_id)
        
        return {
            'xp': user_xp.to_dict(),
            'badges': [badge.to_dict() for badge in badges],
            'goals': [goal.to_dict() for goal in goals],
            'challenges': [challenge.to_dict() for challenge in challenges],
            'stats': {
                'total_badges': len(badges),
                'active_goals': len([g for g in goals if g.is_active]),
                'completed_challenges': len([c for c in challenges if c.is_completed])
            }
        }
    
    def get_engagement_metrics(self, user_id: int, days: int = 30) -> Dict:
        """Get user engagement metrics for the specified period."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get events in period
        events = GamificationEvent.query.filter(
            GamificationEvent.user_id == user_id,
            GamificationEvent.created_at >= start_date
        ).all()
        
        # Get point transactions in period
        user_xp = self.get_user_xp(user_id)
        transactions = PointTransaction.query.filter(
            PointTransaction.user_xp_id == user_xp.id,
            PointTransaction.created_at >= start_date
        ).all()
        
        return {
            'period_days': days,
            'total_events': len(events),
            'total_points_earned': sum(t.points_earned for t in transactions if t.points_earned > 0),
            'event_types': {event.event_type: len([e for e in events if e.event_type == event.event_type]) 
                           for event in events},
            'daily_activity': self._calculate_daily_activity(events, start_date, end_date),
            'average_session_length': self._calculate_average_session_length(events)
        }
    
    def _calculate_daily_activity(self, events: List[GamificationEvent], 
                                 start_date: datetime, end_date: datetime) -> Dict:
        """Calculate daily activity levels."""
        daily_counts = {}
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            daily_events = [e for e in events if e.created_at.date() == current_date]
            daily_counts[current_date.isoformat()] = len(daily_events)
            current_date += timedelta(days=1)
        
        return daily_counts
    
    def _calculate_average_session_length(self, events: List[GamificationEvent]) -> float:
        """Calculate average session length in minutes."""
        sessions = {}
        
        for event in events:
            session_id = event.session_id
            if session_id:
                if session_id not in sessions:
                    sessions[session_id] = {'start': event.created_at, 'end': event.created_at}
                else:
                    if event.created_at < sessions[session_id]['start']:
                        sessions[session_id]['start'] = event.created_at
                    if event.created_at > sessions[session_id]['end']:
                        sessions[session_id]['end'] = event.created_at
        
        if not sessions:
            return 0.0
        
        total_duration = sum(
            (session['end'] - session['start']).total_seconds() / 60
            for session in sessions.values()
        )
        
        return total_duration / len(sessions)
    
    # ========== Activity Tracking Integration ==========
    
    def handle_user_login(self, user_id: int) -> Dict:
        """Handle gamification for user login."""
        results = {}
        
        # Update streak
        streak = self.update_streak(user_id)
        results['streak'] = streak
        
        # Award login points
        points = self.award_points(user_id, 10, PointActivityType.LOGIN)
        results['points_earned'] = points
        
        # Log login event
        self.log_event(user_id, 'login', {'streak': streak, 'points': points})
        
        return results
    
    def handle_evaluation_completion(self, user_id: int, evaluation_id: int, score: float) -> Dict:
        """Handle gamification for evaluation completion."""
        results = {}
        
        # Base points for completion
        base_points = 50
        
        # Bonus points for high scores
        if score >= 90:
            bonus_points = 50
            results['perfect_score_bonus'] = True
        elif score >= 80:
            bonus_points = 25
        elif score >= 70:
            bonus_points = 10
        else:
            bonus_points = 0
        
        total_points = base_points + bonus_points
        
        # Award points
        points = self.award_points(
            user_id, total_points, PointActivityType.COMPLETE_TEST,
            'evaluation', evaluation_id, {'score': score}
        )
        results['points_earned'] = points
        
        # Special handling for perfect scores
        if score == 100:
            perfect_points = self.award_points(
                user_id, 100, PointActivityType.PERFECT_SCORE,
                'evaluation', evaluation_id
            )
            results['perfect_score_points'] = perfect_points
        
        # Update goal progress
        self.update_goal_progress(user_id, 'evaluations_completed', 1)
        self.update_goal_progress(user_id, 'average_score', score)
        
        # Update challenge progress
        self._update_evaluation_challenges(user_id, score)
        
        return results
    
    def handle_program_completion(self, user_id: int, program_id: int) -> Dict:
        """Handle gamification for program completion."""
        results = {}
        
        # Award completion points
        points = self.award_points(
            user_id, 200, PointActivityType.PROGRAM_COMPLETION,
            'program', program_id
        )
        results['points_earned'] = points
        
        # Update goal progress
        self.update_goal_progress(user_id, 'programs_completed', 1)
        
        # Update challenge progress
        self._update_program_challenges(user_id, program_id)
        
        return results
    
    def _update_evaluation_challenges(self, user_id: int, score: float):
        """Update challenge progress for evaluation-related challenges."""
        participations = ChallengeParticipant.query.filter_by(
            user_id=user_id, is_completed=False
        ).all()
        
        for participation in participations:
            challenge = participation.challenge
            if challenge.goals:
                for goal_key, goal_config in challenge.goals.items():
                    if goal_config.get('type') == 'evaluation_count':
                        current = participation.progress.get(goal_key, 0)
                        self.update_challenge_progress(user_id, challenge.id, goal_key, current + 1)
                    elif goal_config.get('type') == 'average_score' and score >= goal_config.get('min_score', 0):
                        current = participation.progress.get(goal_key, 0)
                        self.update_challenge_progress(user_id, challenge.id, goal_key, current + 1)
    
    def _update_program_challenges(self, user_id: int, program_id: int):
        """Update challenge progress for program-related challenges."""
        participations = ChallengeParticipant.query.filter_by(
            user_id=user_id, is_completed=False
        ).all()
        
        for participation in participations:
            challenge = participation.challenge
            if challenge.goals:
                for goal_key, goal_config in challenge.goals.items():
                    if goal_config.get('type') == 'program_completion':
                        current = participation.progress.get(goal_key, 0)
                        self.update_challenge_progress(user_id, challenge.id, goal_key, current + 1)