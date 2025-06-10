"""
Social Service

Manages social features including team challenges, sharing, collaboration,
and social interactions within the gamification system.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from enum import Enum
import json

from app.models.gamification import Team, TeamMember, TeamChallenge, SocialShare, Collaboration
from app.models.user import User
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TeamRole(Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ChallengeStatus(Enum):
    """Challenge statuses"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShareType(Enum):
    """Types of social shares"""
    ACHIEVEMENT = "achievement"
    BADGE = "badge"
    MILESTONE = "milestone"
    LEVEL_UP = "level_up"
    EVALUATION_RESULT = "evaluation_result"
    PROGRESS = "progress"
    CUSTOM = "custom"


class SocialService(BaseService):
    """Service for social features and team interactions"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    # Team Management
    
    def create_team(self, team_data: Dict[str, Any], creator_id: int) -> Team:
        """Create a new team"""
        try:
            team = Team(
                name=team_data['name'],
                description=team_data.get('description', ''),
                avatar_url=team_data.get('avatar_url'),
                is_public=team_data.get('is_public', True),
                max_members=team_data.get('max_members', 50),
                join_code=self._generate_join_code(),
                settings=team_data.get('settings', {}),
                created_by=creator_id
            )
            
            self.db.add(team)
            self.db.flush()  # Get team ID
            
            # Add creator as team owner
            team_member = TeamMember(
                team_id=team.id,
                user_id=creator_id,
                role=TeamRole.OWNER.value,
                joined_at=datetime.utcnow()
            )
            
            self.db.add(team_member)
            self.db.commit()
            self.db.refresh(team)
            
            logger.info(f"Created team: {team.name} by user {creator_id}")
            return team
            
        except Exception as e:
            logger.error(f"Error creating team: {str(e)}")
            self.db.rollback()
            raise
    
    def join_team(self, user_id: int, team_id: Optional[int] = None, 
                  join_code: Optional[str] = None) -> Optional[TeamMember]:
        """Join a team by ID or join code"""
        try:
            # Find team
            if team_id:
                team = self.db.query(Team).get(team_id)
            elif join_code:
                team = self.db.query(Team).filter_by(join_code=join_code).first()
            else:
                return None
            
            if not team:
                return None
            
            # Check if user is already a member
            existing_member = self.db.query(TeamMember).filter_by(
                team_id=team.id,
                user_id=user_id
            ).first()
            
            if existing_member:
                return existing_member
            
            # Check team capacity
            current_members = self.db.query(TeamMember).filter_by(team_id=team.id).count()
            if current_members >= team.max_members:
                return None
            
            # Add user to team
            team_member = TeamMember(
                team_id=team.id,
                user_id=user_id,
                role=TeamRole.MEMBER.value,
                joined_at=datetime.utcnow()
            )
            
            self.db.add(team_member)
            self.db.commit()
            self.db.refresh(team_member)
            
            logger.info(f"User {user_id} joined team {team.id}")
            return team_member
            
        except Exception as e:
            logger.error(f"Error joining team: {str(e)}")
            self.db.rollback()
            return None
    
    def leave_team(self, user_id: int, team_id: int) -> bool:
        """Leave a team"""
        try:
            team_member = self.db.query(TeamMember).filter_by(
                team_id=team_id,
                user_id=user_id
            ).first()
            
            if not team_member:
                return False
            
            # Check if user is the owner
            if team_member.role == TeamRole.OWNER.value:
                # Transfer ownership to another admin or member
                other_admin = self.db.query(TeamMember).filter(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id != user_id,
                    TeamMember.role == TeamRole.ADMIN.value
                ).first()
                
                if other_admin:
                    other_admin.role = TeamRole.OWNER.value
                else:
                    # Find any other member to promote
                    other_member = self.db.query(TeamMember).filter(
                        TeamMember.team_id == team_id,
                        TeamMember.user_id != user_id
                    ).first()
                    
                    if other_member:
                        other_member.role = TeamRole.OWNER.value
                    else:
                        # No other members, delete the team
                        self.db.query(Team).filter_by(id=team_id).delete()
            
            # Remove user from team
            self.db.delete(team_member)
            self.db.commit()
            
            logger.info(f"User {user_id} left team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving team: {str(e)}")
            self.db.rollback()
            return False
    
    def get_user_teams(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all teams a user belongs to"""
        try:
            results = self.db.query(TeamMember, Team).join(Team).filter(
                TeamMember.user_id == user_id
            ).all()
            
            teams = []
            for member, team in results:
                # Get team stats
                member_count = self.db.query(TeamMember).filter_by(team_id=team.id).count()
                active_challenges = self.db.query(TeamChallenge).filter_by(
                    team_id=team.id,
                    status=ChallengeStatus.ACTIVE.value
                ).count()
                
                teams.append({
                    'id': team.id,
                    'name': team.name,
                    'description': team.description,
                    'avatar_url': team.avatar_url,
                    'is_public': team.is_public,
                    'member_count': member_count,
                    'max_members': team.max_members,
                    'user_role': member.role,
                    'joined_at': member.joined_at,
                    'active_challenges': active_challenges,
                    'join_code': team.join_code if member.role in [TeamRole.OWNER.value, TeamRole.ADMIN.value] else None
                })
            
            return teams
            
        except Exception as e:
            logger.error(f"Error getting user teams: {str(e)}")
            return []
    
    def get_team_details(self, team_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get detailed team information"""
        try:
            team = self.db.query(Team).get(team_id)
            if not team:
                return None
            
            # Get team members
            members_query = self.db.query(TeamMember, User).join(User).filter(
                TeamMember.team_id == team_id
            ).order_by(TeamMember.joined_at.asc())
            
            members = []
            user_role = None
            
            for member, user in members_query:
                if user_id and user.id == user_id:
                    user_role = member.role
                
                members.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                    'avatar_url': getattr(user, 'avatar_url', None),
                    'role': member.role,
                    'joined_at': member.joined_at,
                    'last_activity': getattr(user, 'last_login', None)
                })
            
            # Get team statistics
            stats = self._get_team_statistics(team_id)
            
            # Get active challenges
            active_challenges = self.get_team_challenges(team_id, status=ChallengeStatus.ACTIVE.value)
            
            return {
                'id': team.id,
                'name': team.name,
                'description': team.description,
                'avatar_url': team.avatar_url,
                'is_public': team.is_public,
                'max_members': team.max_members,
                'join_code': team.join_code if user_role in [TeamRole.OWNER.value, TeamRole.ADMIN.value] else None,
                'settings': team.settings,
                'created_at': team.created_at,
                'members': members,
                'user_role': user_role,
                'statistics': stats,
                'active_challenges': active_challenges
            }
            
        except Exception as e:
            logger.error(f"Error getting team details: {str(e)}")
            return None
    
    # Team Challenges
    
    def create_team_challenge(self, challenge_data: Dict[str, Any], creator_id: int) -> TeamChallenge:
        """Create a new team challenge"""
        try:
            challenge = TeamChallenge(
                team_id=challenge_data['team_id'],
                name=challenge_data['name'],
                description=challenge_data.get('description', ''),
                challenge_type=challenge_data['type'],
                criteria=challenge_data.get('criteria', {}),
                rewards=challenge_data.get('rewards', {}),
                start_date=challenge_data.get('start_date', datetime.utcnow()),
                end_date=challenge_data['end_date'],
                status=ChallengeStatus.DRAFT.value,
                max_participants=challenge_data.get('max_participants'),
                created_by=creator_id
            )
            
            self.db.add(challenge)
            self.db.commit()
            self.db.refresh(challenge)
            
            logger.info(f"Created team challenge: {challenge.name}")
            return challenge
            
        except Exception as e:
            logger.error(f"Error creating team challenge: {str(e)}")
            self.db.rollback()
            raise
    
    def start_team_challenge(self, challenge_id: int, user_id: int) -> bool:
        """Start a team challenge"""
        try:
            challenge = self.db.query(TeamChallenge).get(challenge_id)
            if not challenge:
                return False
            
            # Check if user has permission to start challenge
            team_member = self.db.query(TeamMember).filter_by(
                team_id=challenge.team_id,
                user_id=user_id
            ).first()
            
            if not team_member or team_member.role not in [TeamRole.OWNER.value, TeamRole.ADMIN.value]:
                return False
            
            # Update challenge status
            challenge.status = ChallengeStatus.ACTIVE.value
            challenge.started_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Started team challenge {challenge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting team challenge: {str(e)}")
            self.db.rollback()
            return False
    
    def get_team_challenges(self, team_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get team challenges"""
        try:
            query = self.db.query(TeamChallenge).filter_by(team_id=team_id)
            
            if status:
                query = query.filter_by(status=status)
            
            challenges = query.order_by(TeamChallenge.created_at.desc()).all()
            
            result = []
            for challenge in challenges:
                # Get participation stats
                participant_count = self._get_challenge_participant_count(challenge.id)
                
                result.append({
                    'id': challenge.id,
                    'name': challenge.name,
                    'description': challenge.description,
                    'type': challenge.challenge_type,
                    'criteria': challenge.criteria,
                    'rewards': challenge.rewards,
                    'start_date': challenge.start_date,
                    'end_date': challenge.end_date,
                    'status': challenge.status,
                    'participant_count': participant_count,
                    'max_participants': challenge.max_participants,
                    'created_at': challenge.created_at
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting team challenges: {str(e)}")
            return []
    
    # Social Sharing
    
    def create_social_share(self, share_data: Dict[str, Any], user_id: int) -> SocialShare:
        """Create a social share"""
        try:
            share = SocialShare(
                user_id=user_id,
                share_type=share_data['type'],
                content=share_data['content'],
                metadata=share_data.get('metadata', {}),
                is_public=share_data.get('is_public', True),
                team_id=share_data.get('team_id')
            )
            
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            
            logger.info(f"Created social share by user {user_id}")
            return share
            
        except Exception as e:
            logger.error(f"Error creating social share: {str(e)}")
            self.db.rollback()
            raise
    
    def get_social_feed(self, user_id: int, team_id: Optional[int] = None, 
                       limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get social feed for user"""
        try:
            query = self.db.query(SocialShare, User).join(User)
            
            if team_id:
                # Team-specific feed
                query = query.filter(SocialShare.team_id == team_id)
            else:
                # Get shares from user's teams and public shares
                user_teams = self.db.query(TeamMember.team_id).filter_by(user_id=user_id).subquery()
                query = query.filter(
                    or_(
                        SocialShare.is_public == True,
                        SocialShare.team_id.in_(user_teams),
                        SocialShare.user_id == user_id
                    )
                )
            
            results = query.order_by(SocialShare.created_at.desc()).offset(offset).limit(limit).all()
            
            feed = []
            for share, user in results:
                feed.append({
                    'id': share.id,
                    'type': share.share_type,
                    'content': share.content,
                    'metadata': share.metadata,
                    'created_at': share.created_at,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'display_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                        'avatar_url': getattr(user, 'avatar_url', None)
                    },
                    'reactions': self._get_share_reactions(share.id),
                    'is_public': share.is_public,
                    'team_id': share.team_id
                })
            
            return feed
            
        except Exception as e:
            logger.error(f"Error getting social feed: {str(e)}")
            return []
    
    def react_to_share(self, share_id: int, user_id: int, reaction_type: str) -> bool:
        """React to a social share"""
        try:
            # This would require a ShareReaction model
            # For now, just logging the action
            logger.info(f"User {user_id} reacted to share {share_id} with {reaction_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error reacting to share: {str(e)}")
            return False
    
    # Collaboration Features
    
    def create_collaboration(self, collaboration_data: Dict[str, Any], creator_id: int) -> Collaboration:
        """Create a collaboration session"""
        try:
            collaboration = Collaboration(
                name=collaboration_data['name'],
                description=collaboration_data.get('description', ''),
                collaboration_type=collaboration_data['type'],
                team_id=collaboration_data.get('team_id'),
                settings=collaboration_data.get('settings', {}),
                is_active=True,
                created_by=creator_id
            )
            
            self.db.add(collaboration)
            self.db.commit()
            self.db.refresh(collaboration)
            
            logger.info(f"Created collaboration: {collaboration.name}")
            return collaboration
            
        except Exception as e:
            logger.error(f"Error creating collaboration: {str(e)}")
            self.db.rollback()
            raise
    
    def get_team_leaderboard(self, team_id: int, metric: str = 'xp') -> List[Dict[str, Any]]:
        """Get team leaderboard for a specific metric"""
        try:
            # Get team members with their stats
            members_query = self.db.query(TeamMember, User).join(User).filter(
                TeamMember.team_id == team_id
            )
            
            leaderboard = []
            for member, user in members_query:
                score = 0
                if metric == 'xp':
                    score = user.total_xp or 0
                elif metric == 'level':
                    score = user.level or 1
                elif metric == 'badges':
                    score = user.total_badges or 0
                
                leaderboard.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                    'avatar_url': getattr(user, 'avatar_url', None),
                    'score': score,
                    'role': member.role
                })
            
            # Sort by score
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            
            # Add ranks
            for i, entry in enumerate(leaderboard):
                entry['rank'] = i + 1
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting team leaderboard: {str(e)}")
            return []
    
    # Helper Methods
    
    def _generate_join_code(self) -> str:
        """Generate a unique team join code"""
        import secrets
        import string
        
        length = 8
        characters = string.ascii_uppercase + string.digits
        
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            # Check if code already exists
            existing = self.db.query(Team).filter_by(join_code=code).first()
            if not existing:
                return code
    
    def _get_team_statistics(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics"""
        try:
            # Get team members
            members = self.db.query(TeamMember).filter_by(team_id=team_id).all()
            member_count = len(members)
            
            if member_count == 0:
                return {}
            
            # Calculate aggregate stats
            member_ids = [m.user_id for m in members]
            users = self.db.query(User).filter(User.id.in_(member_ids)).all()
            
            total_xp = sum(u.total_xp or 0 for u in users)
            total_badges = sum(u.total_badges or 0 for u in users)
            avg_level = sum(u.level or 1 for u in users) / len(users)
            
            return {
                'member_count': member_count,
                'total_xp': total_xp,
                'average_xp': total_xp // member_count,
                'total_badges': total_badges,
                'average_level': round(avg_level, 1),
                'active_challenges': self.db.query(TeamChallenge).filter_by(
                    team_id=team_id,
                    status=ChallengeStatus.ACTIVE.value
                ).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting team statistics: {str(e)}")
            return {}
    
    def _get_challenge_participant_count(self, challenge_id: int) -> int:
        """Get number of participants in a challenge"""
        # This would require a ChallengeParticipant model
        return 0
    
    def _get_share_reactions(self, share_id: int) -> Dict[str, int]:
        """Get reactions for a social share"""
        # This would require a ShareReaction model
        return {'likes': 0, 'loves': 0, 'congratulations': 0}