"""
Badge Service

Manages the badge system including badge creation, assignment, and visual customization.
Handles different badge types: achievement badges, skill badges, participation badges, etc.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json

from app.models.gamification import Badge, UserBadge, BadgeCategory
from app.models.user import User
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BadgeService(BaseService):
    """Service for managing badges and badge assignments"""
    
    # Predefined badge templates with designs
    BADGE_TEMPLATES = {
        'FIRST_STEPS': {
            'name': 'First Steps',
            'description': 'Complete your first evaluation',
            'icon': '👶',
            'color': '#4CAF50',
            'design': {
                'shape': 'circle',
                'background': 'linear-gradient(135deg, #4CAF50, #8BC34A)',
                'border': '2px solid #2E7D32',
                'text_color': '#FFFFFF'
            },
            'rarity': 'common'
        },
        'PERFECTIONIST': {
            'name': 'Perfectionist',
            'description': 'Score 100% on an evaluation',
            'icon': '💯',
            'color': '#FFD700',
            'design': {
                'shape': 'star',
                'background': 'linear-gradient(135deg, #FFD700, #FFA000)',
                'border': '3px solid #FF8F00',
                'text_color': '#1A1A1A',
                'glow': 'rgba(255, 215, 0, 0.6)'
            },
            'rarity': 'rare'
        },
        'STREAK_MASTER': {
            'name': 'Streak Master',
            'description': 'Maintain a 7-day learning streak',
            'icon': '🔥',
            'color': '#FF5722',
            'design': {
                'shape': 'hexagon',
                'background': 'linear-gradient(135deg, #FF5722, #E64A19)',
                'border': '2px solid #BF360C',
                'text_color': '#FFFFFF',
                'animation': 'pulse'
            },
            'rarity': 'uncommon'
        },
        'SOCIAL_BUTTERFLY': {
            'name': 'Social Butterfly',
            'description': 'Participate in 5 team challenges',
            'icon': '🦋',
            'color': '#9C27B0',
            'design': {
                'shape': 'shield',
                'background': 'linear-gradient(135deg, #9C27B0, #673AB7)',
                'border': '2px solid #4A148C',
                'text_color': '#FFFFFF'
            },
            'rarity': 'uncommon'
        },
        'KNOWLEDGE_SEEKER': {
            'name': 'Knowledge Seeker',
            'description': 'Complete 10 different learning modules',
            'icon': '📚',
            'color': '#2196F3',
            'design': {
                'shape': 'diamond',
                'background': 'linear-gradient(135deg, #2196F3, #1976D2)',
                'border': '2px solid #0D47A1',
                'text_color': '#FFFFFF'
            },
            'rarity': 'common'
        },
        'LEGEND': {
            'name': 'Legend',
            'description': 'Reach level 50',
            'icon': '👑',
            'color': '#9C27B0',
            'design': {
                'shape': 'crown',
                'background': 'linear-gradient(135deg, #9C27B0, #673AB7, #FFD700)',
                'border': '3px solid #4A148C',
                'text_color': '#FFFFFF',
                'glow': 'rgba(156, 39, 176, 0.8)',
                'animation': 'sparkle'
            },
            'rarity': 'legendary'
        }
    }
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.rarity_weights = {
            'common': 1,
            'uncommon': 2,
            'rare': 3,
            'epic': 4,
            'legendary': 5
        }
    
    def create_badge(self, badge_data: Dict[str, Any]) -> Badge:
        """Create a new badge"""
        try:
            badge = Badge(
                name=badge_data['name'],
                description=badge_data['description'],
                icon=badge_data.get('icon', '🏆'),
                color=badge_data.get('color', '#4CAF50'),
                design=badge_data.get('design', {}),
                category=badge_data.get('category', 'achievement'),
                rarity=badge_data.get('rarity', 'common'),
                criteria=badge_data.get('criteria', {}),
                is_active=badge_data.get('is_active', True),
                points=badge_data.get('points', 10),
                created_by=badge_data.get('created_by')
            )
            
            self.db.add(badge)
            self.db.commit()
            self.db.refresh(badge)
            
            logger.info(f"Created badge: {badge.name}")
            return badge
            
        except Exception as e:
            logger.error(f"Error creating badge: {str(e)}")
            self.db.rollback()
            raise
    
    def create_badge_from_template(self, template_name: str, custom_data: Optional[Dict] = None) -> Badge:
        """Create a badge from a predefined template"""
        try:
            if template_name not in self.BADGE_TEMPLATES:
                raise ValueError(f"Unknown badge template: {template_name}")
            
            template = self.BADGE_TEMPLATES[template_name].copy()
            
            # Override with custom data if provided
            if custom_data:
                template.update(custom_data)
            
            return self.create_badge(template)
            
        except Exception as e:
            logger.error(f"Error creating badge from template: {str(e)}")
            raise
    
    def award_badge(self, user_id: int, badge_id: int, 
                   awarded_by: Optional[int] = None,
                   metadata: Optional[Dict] = None) -> UserBadge:
        """Award a badge to a user"""
        try:
            # Check if user already has this badge
            existing = self.db.query(UserBadge).filter_by(
                user_id=user_id,
                badge_id=badge_id
            ).first()
            
            if existing:
                logger.warning(f"User {user_id} already has badge {badge_id}")
                return existing
            
            # Create user badge record
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                earned_at=datetime.utcnow(),
                awarded_by=awarded_by,
                metadata=metadata or {}
            )
            
            self.db.add(user_badge)
            
            # Update user's badge count and points
            badge = self.db.query(Badge).get(badge_id)
            if badge:
                user = self.db.query(User).get(user_id)
                if user:
                    user.total_badges = (user.total_badges or 0) + 1
                    user.total_badge_points = (user.total_badge_points or 0) + badge.points
            
            self.db.commit()
            self.db.refresh(user_badge)
            
            logger.info(f"Awarded badge {badge_id} to user {user_id}")
            return user_badge
            
        except Exception as e:
            logger.error(f"Error awarding badge: {str(e)}")
            self.db.rollback()
            raise
    
    def get_user_badges(self, user_id: int, category: Optional[str] = None) -> List[Dict]:
        """Get all badges earned by a user"""
        try:
            query = self.db.query(UserBadge, Badge).join(Badge)
            query = query.filter(UserBadge.user_id == user_id)
            
            if category:
                query = query.filter(Badge.category == category)
            
            results = query.order_by(UserBadge.earned_at.desc()).all()
            
            return [
                {
                    'id': ub.id,
                    'badge': {
                        'id': b.id,
                        'name': b.name,
                        'description': b.description,
                        'icon': b.icon,
                        'color': b.color,
                        'design': b.design,
                        'category': b.category,
                        'rarity': b.rarity,
                        'points': b.points
                    },
                    'earned_at': ub.earned_at,
                    'metadata': ub.metadata
                }
                for ub, b in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting user badges: {str(e)}")
            return []
    
    def get_badge_showcase(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get user's most impressive badges for showcase"""
        try:
            # Get badges ordered by rarity and recency
            query = self.db.query(UserBadge, Badge).join(Badge)
            query = query.filter(UserBadge.user_id == user_id)
            
            results = query.all()
            
            # Sort by rarity weight and recency
            sorted_badges = sorted(results, key=lambda x: (
                -self.rarity_weights.get(x[1].rarity, 1),
                -x[0].earned_at.timestamp()
            ))
            
            return [
                {
                    'id': ub.id,
                    'badge': {
                        'id': b.id,
                        'name': b.name,
                        'description': b.description,
                        'icon': b.icon,
                        'color': b.color,
                        'design': b.design,
                        'category': b.category,
                        'rarity': b.rarity,
                        'points': b.points
                    },
                    'earned_at': ub.earned_at
                }
                for ub, b in sorted_badges[:limit]
            ]
            
        except Exception as e:
            logger.error(f"Error getting badge showcase: {str(e)}")
            return []
    
    def get_available_badges(self, user_id: int, category: Optional[str] = None) -> List[Dict]:
        """Get badges available to earn (not yet earned by user)"""
        try:
            # Get user's earned badge IDs
            earned_ids = self.db.query(UserBadge.badge_id).filter_by(
                user_id=user_id
            ).subquery()
            
            # Get available badges
            query = self.db.query(Badge).filter(
                Badge.is_active == True,
                ~Badge.id.in_(earned_ids)
            )
            
            if category:
                query = query.filter(Badge.category == category)
            
            badges = query.all()
            
            return [
                {
                    'id': badge.id,
                    'name': badge.name,
                    'description': badge.description,
                    'icon': badge.icon,
                    'color': badge.color,
                    'design': badge.design,
                    'category': badge.category,
                    'rarity': badge.rarity,
                    'points': badge.points,
                    'criteria': badge.criteria
                }
                for badge in badges
            ]
            
        except Exception as e:
            logger.error(f"Error getting available badges: {str(e)}")
            return []
    
    def get_badge_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get badge statistics for a user or globally"""
        try:
            if user_id:
                # User-specific statistics
                user_badges = self.db.query(UserBadge).filter_by(user_id=user_id).count()
                user_badge_points = self.db.query(func.sum(Badge.points)).join(UserBadge).filter(
                    UserBadge.user_id == user_id
                ).scalar() or 0
                
                # Badges by rarity
                rarity_counts = {}
                results = self.db.query(Badge.rarity, func.count(UserBadge.id)).join(UserBadge).filter(
                    UserBadge.user_id == user_id
                ).group_by(Badge.rarity).all()
                
                for rarity, count in results:
                    rarity_counts[rarity] = count
                
                # Recent badges (last 30 days)
                recent_count = self.db.query(UserBadge).filter(
                    UserBadge.user_id == user_id,
                    UserBadge.earned_at >= datetime.utcnow() - timedelta(days=30)
                ).count()
                
                return {
                    'total_badges': user_badges,
                    'total_points': user_badge_points,
                    'badges_by_rarity': rarity_counts,
                    'recent_badges': recent_count,
                    'completion_rate': self._calculate_completion_rate(user_id)
                }
            else:
                # Global statistics
                total_badges = self.db.query(Badge).filter_by(is_active=True).count()
                total_awarded = self.db.query(UserBadge).count()
                
                return {
                    'total_badges': total_badges,
                    'total_awarded': total_awarded,
                    'most_earned': self._get_most_earned_badges(),
                    'rarest_badges': self._get_rarest_badges()
                }
                
        except Exception as e:
            logger.error(f"Error getting badge statistics: {str(e)}")
            return {}
    
    def create_custom_badge_design(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom badge design"""
        try:
            design = {
                'shape': design_data.get('shape', 'circle'),
                'background': design_data.get('background', '#4CAF50'),
                'border': design_data.get('border', '2px solid #2E7D32'),
                'text_color': design_data.get('text_color', '#FFFFFF'),
                'font_family': design_data.get('font_family', 'Arial, sans-serif'),
                'font_size': design_data.get('font_size', '14px'),
                'padding': design_data.get('padding', '8px'),
                'shadow': design_data.get('shadow', '0 2px 4px rgba(0,0,0,0.2)')
            }
            
            # Add optional properties
            if design_data.get('glow'):
                design['glow'] = design_data['glow']
            if design_data.get('animation'):
                design['animation'] = design_data['animation']
            if design_data.get('gradient_stops'):
                design['gradient_stops'] = design_data['gradient_stops']
            
            return design
            
        except Exception as e:
            logger.error(f"Error creating custom badge design: {str(e)}")
            return {}
    
    def generate_badge_css(self, badge: Badge) -> str:
        """Generate CSS for a badge design"""
        try:
            design = badge.design or {}
            css_class = f"badge-{badge.id}"
            
            css = f"""
.{css_class} {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: {design.get('background', badge.color)};
    border: {design.get('border', '2px solid #ccc')};
    color: {design.get('text_color', '#FFFFFF')};
    font-family: {design.get('font_family', 'Arial, sans-serif')};
    font-size: {design.get('font_size', '14px')};
    padding: {design.get('padding', '8px')};
    box-shadow: {design.get('shadow', '0 2px 4px rgba(0,0,0,0.2)')};
    position: relative;
    overflow: hidden;
}}
"""
            
            # Add shape-specific styles
            shape = design.get('shape', 'circle')
            if shape == 'circle':
                css += f".{css_class} {{ border-radius: 50%; width: 60px; height: 60px; }}\n"
            elif shape == 'hexagon':
                css += f".{css_class} {{ clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); width: 60px; height: 60px; }}\n"
            elif shape == 'star':
                css += f".{css_class} {{ clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%); width: 60px; height: 60px; }}\n"
            elif shape == 'diamond':
                css += f".{css_class} {{ transform: rotate(45deg); width: 50px; height: 50px; }}\n"
            elif shape == 'shield':
                css += f".{css_class} {{ clip-path: polygon(50% 0%, 100% 25%, 82% 100%, 18% 100%, 0% 25%); width: 60px; height: 70px; }}\n"
            
            # Add glow effect
            if design.get('glow'):
                css += f".{css_class}::before {{ content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; background: {design['glow']}; border-radius: inherit; z-index: -1; filter: blur(8px); }}\n"
            
            # Add animations
            if design.get('animation') == 'pulse':
                css += f".{css_class} {{ animation: badge-pulse 2s infinite; }}\n"
                css += "@keyframes badge-pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }\n"
            elif design.get('animation') == 'sparkle':
                css += f".{css_class} {{ animation: badge-sparkle 3s infinite; }}\n"
                css += "@keyframes badge-sparkle { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.3) saturate(1.2); } }\n"
            
            return css
            
        except Exception as e:
            logger.error(f"Error generating badge CSS: {str(e)}")
            return ""
    
    def _calculate_completion_rate(self, user_id: int) -> float:
        """Calculate user's badge completion rate"""
        try:
            total_badges = self.db.query(Badge).filter_by(is_active=True).count()
            earned_badges = self.db.query(UserBadge).filter_by(user_id=user_id).count()
            
            if total_badges == 0:
                return 0.0
            
            return round((earned_badges / total_badges) * 100, 2)
            
        except Exception as e:
            logger.error(f"Error calculating completion rate: {str(e)}")
            return 0.0
    
    def _get_most_earned_badges(self, limit: int = 5) -> List[Dict]:
        """Get most frequently earned badges"""
        try:
            results = self.db.query(
                Badge,
                func.count(UserBadge.id).label('count')
            ).join(UserBadge).group_by(Badge.id).order_by(
                func.count(UserBadge.id).desc()
            ).limit(limit).all()
            
            return [
                {
                    'badge': {
                        'id': badge.id,
                        'name': badge.name,
                        'icon': badge.icon,
                        'rarity': badge.rarity
                    },
                    'count': count
                }
                for badge, count in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting most earned badges: {str(e)}")
            return []
    
    def _get_rarest_badges(self, limit: int = 5) -> List[Dict]:
        """Get rarest badges (least earned)"""
        try:
            results = self.db.query(
                Badge,
                func.count(UserBadge.id).label('count')
            ).outerjoin(UserBadge).group_by(Badge.id).order_by(
                func.count(UserBadge.id).asc()
            ).limit(limit).all()
            
            return [
                {
                    'badge': {
                        'id': badge.id,
                        'name': badge.name,
                        'icon': badge.icon,
                        'rarity': badge.rarity
                    },
                    'count': count
                }
                for badge, count in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting rarest badges: {str(e)}")
            return []