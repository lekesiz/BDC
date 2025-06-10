"""Comprehensive Gamification API endpoints for BDC application."""

from datetime import datetime, timedelta
from typing import Dict, List
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import Range, Length
from sqlalchemy import desc, func

from app.extensions import db
from app.models.gamification import (
    Badge, UserBadge, UserXP, PointTransaction, Leaderboard, LeaderboardEntry,
    Challenge, ChallengeParticipant, GamificationTeam, Reward, RewardRedemption,
    UserGoal, GamificationEvent, UserProgress,
    AchievementCategory, PointActivityType, LeaderboardType, ChallengeType, RewardType
)
from app.models.user import User
from app.services.gamification_service import GamificationService
from app.utils.decorators import handle_exceptions

from app.utils.logging import logger

# Initialize Blueprint
gamification_bp = Blueprint('gamification', __name__, url_prefix='/api/gamification')

# Initialize service
gamification_service = GamificationService()


# ========== Schemas for Request/Response Validation ==========

class BadgeSchema(Schema):
    name = fields.String(required=True, validate=Length(min=1, max=100))
    description = fields.String(load_default='')
    category = fields.String(required=True)
    rarity = fields.String(load_default='common')
    points_value = fields.Integer(load_default=0)
    unlock_conditions = fields.Dict(required=True)
    icon_url = fields.String(load_default='')
    is_secret = fields.Boolean(load_default=False)

class ChallengeSchema(Schema):
    title = fields.String(required=True, validate=Length(min=1, max=100))
    description = fields.String(required=True)
    type = fields.String(required=True)
    goals = fields.Dict(required=True)
    rewards = fields.Dict(load_default=dict)
    difficulty = fields.String(load_default='medium')
    start_date = fields.DateTime(load_default=None)
    end_date = fields.DateTime(load_default=None)
    duration_hours = fields.Integer(load_default=None)
    max_participants = fields.Integer(load_default=None)

class RewardSchema(Schema):
    name = fields.String(required=True, validate=Length(min=1, max=100))
    type = fields.String(required=True)
    cost = fields.Integer(required=True, validate=Range(min=0))
    value = fields.Dict(required=True)
    description = fields.String(load_default='')
    rarity = fields.String(load_default='common')
    total_quantity = fields.Integer(load_default=None)
    available_from = fields.DateTime(load_default=None)
    available_until = fields.DateTime(load_default=None)

class TeamSchema(Schema):
    name = fields.String(required=True, validate=Length(min=1, max=100))
    description = fields.String(load_default='')
    max_members = fields.Integer(load_default=10)
    is_open = fields.Boolean(load_default=True)

class GoalSchema(Schema):
    title = fields.String(required=True, validate=Length(min=1, max=100))
    description = fields.String(load_default='')
    goal_type = fields.String(required=True)
    target_value = fields.Float(required=True)
    deadline = fields.DateTime(load_default=None)

class LeaderboardSchema(Schema):
    name = fields.String(required=True, validate=Length(min=1, max=100))
    type = fields.String(required=True)
    metric = fields.String(required=True)
    description = fields.String(load_default='')
    start_date = fields.DateTime(load_default=None)
    end_date = fields.DateTime(load_default=None)
    max_entries = fields.Integer(load_default=100)


# ========== User XP and Progress Endpoints ==========

@gamification_bp.route('/xp', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_user_xp():
    """Get current user's XP and level information."""
    user_id = get_jwt_identity()
    user_xp = gamification_service.get_user_xp(user_id)
    
    return jsonify({
        'success': True,
        'data': user_xp.to_dict()
    })

@gamification_bp.route('/xp/history', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_xp_history():
    """Get user's XP transaction history."""
    user_id = get_jwt_identity()
    user_xp = gamification_service.get_user_xp(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    transactions = PointTransaction.query.filter_by(
        user_xp_id=user_xp.id
    ).order_by(desc(PointTransaction.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'transactions': [t.to_dict() for t in transactions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transactions.total,
                'pages': transactions.pages
            }
        }
    })

@gamification_bp.route('/progress/summary', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_progress_summary():
    """Get comprehensive progress summary for current user."""
    user_id = get_jwt_identity()
    summary = gamification_service.get_user_progress_summary(user_id)
    
    return jsonify({
        'success': True,
        'data': summary
    })

@gamification_bp.route('/engagement/metrics', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_engagement_metrics():
    """Get user engagement metrics."""
    user_id = get_jwt_identity()
    days = request.args.get('days', 30, type=int)
    
    metrics = gamification_service.get_engagement_metrics(user_id, days)
    
    return jsonify({
        'success': True,
        'data': metrics
    })


# ========== Badge and Achievement Endpoints ==========

@gamification_bp.route('/badges', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_user_badges():
    """Get user's earned badges."""
    user_id = get_jwt_identity()
    category = request.args.get('category')
    
    if category:
        try:
            category_enum = AchievementCategory(category)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400
    else:
        category_enum = None
    
    badges = gamification_service.get_user_badges(user_id, category_enum)
    
    return jsonify({
        'success': True,
        'data': [badge.to_dict() for badge in badges]
    })

@gamification_bp.route('/badges/available', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_available_badges():
    """Get badges available to earn."""
    user_id = get_jwt_identity()
    category = request.args.get('category')
    
    if category:
        try:
            category_enum = AchievementCategory(category)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400
    else:
        category_enum = None
    
    badges = gamification_service.get_available_badges(user_id, category_enum)
    
    # Filter out secret badges for non-admin users
    filtered_badges = [badge for badge in badges if not badge.is_secret]
    
    return jsonify({
        'success': True,
        'data': [badge.to_dict() for badge in filtered_badges]
    })

@gamification_bp.route('/admin/badges', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_badge():
    """Create a new badge (admin only)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    
    try:
        schema = BadgeSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    try:
        category = AchievementCategory(data['category'])
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid category'}), 400
    
    badge = gamification_service.create_badge(
        name=data['name'],
        description=data['description'],
        category=category,
        unlock_conditions=data['unlock_conditions'],
        rarity=data['rarity'],
        points_value=data['points_value'],
        icon_url=data['icon_url'],
        is_secret=data['is_secret']
    )
    
    return jsonify({
        'success': True,
        'data': badge.to_dict(),
        'message': 'Badge created successfully'
    }), 201

@gamification_bp.route('/admin/badges/<int:badge_id>/award', methods=['POST'])
@jwt_required()
@handle_exceptions
def award_badge_manual():
    """Manually award a badge to a user (admin only)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    
    target_user_id = request.json.get('user_id')
    metadata = request.json.get('metadata', {})
    
    if not target_user_id:
        return jsonify({'success': False, 'message': 'user_id is required'}), 400
    
    try:
        user_badge = gamification_service.award_badge(badge_id, target_user_id, metadata)
        return jsonify({
            'success': True,
            'data': user_badge.to_dict(),
            'message': 'Badge awarded successfully'
        })
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ========== Leaderboard Endpoints ==========

@gamification_bp.route('/leaderboards', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_leaderboards():
    """Get available leaderboards."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    leaderboard_type = request.args.get('type')
    
    query = Leaderboard.query.filter_by(is_active=True, is_public=True)
    
    if leaderboard_type:
        try:
            type_enum = LeaderboardType(leaderboard_type)
            query = query.filter_by(type=type_enum)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid leaderboard type'}), 400
    
    # For class leaderboards, filter by user's tenant
    if user.tenant_id:
        query = query.filter(
            (Leaderboard.tenant_id == user.tenant_id) | 
            (Leaderboard.tenant_id.is_(None))
        )
    
    leaderboards = query.order_by(Leaderboard.type, Leaderboard.name).all()
    
    return jsonify({
        'success': True,
        'data': [lb.to_dict() for lb in leaderboards]
    })

@gamification_bp.route('/leaderboards/<int:leaderboard_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_leaderboard():
    """Get specific leaderboard with entries."""
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 100)  # Max 100 entries
    
    leaderboard_data = gamification_service.get_leaderboard(leaderboard_id, limit)
    
    if not leaderboard_data:
        return jsonify({'success': False, 'message': 'Leaderboard not found'}), 404
    
    return jsonify({
        'success': True,
        'data': leaderboard_data
    })

@gamification_bp.route('/leaderboards/<int:leaderboard_id>/position', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_user_leaderboard_position():
    """Get current user's position in a leaderboard."""
    user_id = get_jwt_identity()
    position = gamification_service.get_user_leaderboard_position(user_id, leaderboard_id)
    
    return jsonify({
        'success': True,
        'data': {'position': position}
    })

@gamification_bp.route('/admin/leaderboards', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_leaderboard():
    """Create a new leaderboard (admin only)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    
    try:
        schema = LeaderboardSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    try:
        leaderboard_type = LeaderboardType(data['type'])
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid leaderboard type'}), 400
    
    # For tenant admins, set tenant_id
    tenant_id = None
    if user.role == 'tenant_admin':
        tenant_id = user.tenant_id
    
    leaderboard = gamification_service.create_leaderboard(
        name=data['name'],
        leaderboard_type=leaderboard_type,
        metric=data['metric'],
        description=data['description'],
        tenant_id=tenant_id,
        start_date=data['start_date'],
        end_date=data['end_date'],
        max_entries=data['max_entries']
    )
    
    return jsonify({
        'success': True,
        'data': leaderboard.to_dict(),
        'message': 'Leaderboard created successfully'
    }), 201


# ========== Challenge Endpoints ==========

@gamification_bp.route('/challenges', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_challenges():
    """Get active challenges."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    challenges = gamification_service.get_active_challenges(user_id, user.tenant_id)
    
    return jsonify({
        'success': True,
        'data': [challenge.to_dict() for challenge in challenges]
    })

@gamification_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_challenge():
    """Get specific challenge details."""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    return jsonify({
        'success': True,
        'data': challenge.to_dict()
    })

@gamification_bp.route('/challenges/<int:challenge_id>/join', methods=['POST'])
@jwt_required()
@handle_exceptions
def join_challenge():
    """Join a challenge."""
    user_id = get_jwt_identity()
    team_id = request.json.get('team_id')
    
    try:
        participant = gamification_service.join_challenge(user_id, challenge_id, team_id)
        return jsonify({
            'success': True,
            'data': participant.to_dict(),
            'message': 'Successfully joined challenge'
        })
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@gamification_bp.route('/challenges/my', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_my_challenges():
    """Get current user's challenge participations."""
    user_id = get_jwt_identity()
    participations = gamification_service.get_user_challenges(user_id)
    
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in participations]
    })

@gamification_bp.route('/admin/challenges', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_challenge():
    """Create a new challenge (admin only)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    
    try:
        schema = ChallengeSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    try:
        challenge_type = ChallengeType(data['type'])
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid challenge type'}), 400
    
    # For tenant admins, set tenant_id
    tenant_id = None
    if user.role == 'tenant_admin':
        tenant_id = user.tenant_id
    
    challenge = gamification_service.create_challenge(
        title=data['title'],
        description=data['description'],
        challenge_type=challenge_type,
        goals=data['goals'],
        rewards=data['rewards'],
        difficulty=data['difficulty'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        duration_hours=data['duration_hours'],
        max_participants=data['max_participants'],
        tenant_id=tenant_id
    )
    
    return jsonify({
        'success': True,
        'data': challenge.to_dict(),
        'message': 'Challenge created successfully'
    }), 201


# ========== Team Endpoints ==========

@gamification_bp.route('/teams', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_teams():
    """Get available teams."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    query = GamificationTeam.query
    
    # Filter by tenant if applicable
    if user.tenant_id:
        query = query.filter(
            (GamificationTeam.tenant_id == user.tenant_id) |
            (GamificationTeam.tenant_id.is_(None))
        )
    
    # Only show open teams or teams user is already in
    query = query.filter(
        (GamificationTeam.is_open == True) |
        (GamificationTeam.members.any(User.id == user_id))
    )
    
    teams = query.order_by(GamificationTeam.name).all()
    
    return jsonify({
        'success': True,
        'data': [team.to_dict() for team in teams]
    })

@gamification_bp.route('/teams', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_team():
    """Create a new team."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    try:
        schema = TeamSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    team = gamification_service.create_team(
        name=data['name'],
        leader_id=user_id,
        description=data['description'],
        max_members=data['max_members'],
        is_open=data['is_open'],
        tenant_id=user.tenant_id
    )
    
    return jsonify({
        'success': True,
        'data': team.to_dict(),
        'message': 'Team created successfully'
    }), 201

@gamification_bp.route('/teams/<int:team_id>/join', methods=['POST'])
@jwt_required()
@handle_exceptions
def join_team():
    """Join a team."""
    user_id = get_jwt_identity()
    
    success = gamification_service.join_team(user_id, team_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Successfully joined team'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to join team'
        }), 400

@gamification_bp.route('/teams/<int:team_id>/leave', methods=['POST'])
@jwt_required()
@handle_exceptions
def leave_team():
    """Leave a team."""
    user_id = get_jwt_identity()
    
    success = gamification_service.leave_team(user_id, team_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Successfully left team'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to leave team'
        }), 400


# ========== Reward Endpoints ==========

@gamification_bp.route('/rewards', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_rewards():
    """Get available rewards."""
    user_id = get_jwt_identity()
    affordable_only = request.args.get('affordable_only', 'false').lower() == 'true'
    
    if affordable_only:
        rewards = gamification_service.get_available_rewards(user_id)
    else:
        rewards = gamification_service.get_available_rewards()
    
    return jsonify({
        'success': True,
        'data': [reward.to_dict() for reward in rewards]
    })

@gamification_bp.route('/rewards/<int:reward_id>/redeem', methods=['POST'])
@jwt_required()
@handle_exceptions
def redeem_reward():
    """Redeem a reward."""
    user_id = get_jwt_identity()
    
    try:
        redemption = gamification_service.redeem_reward(user_id, reward_id)
        return jsonify({
            'success': True,
            'data': redemption.to_dict(),
            'message': 'Reward redeemed successfully'
        })
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@gamification_bp.route('/rewards/my', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_my_rewards():
    """Get user's reward redemptions."""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    redemptions = RewardRedemption.query.filter_by(
        user_id=user_id
    ).order_by(desc(RewardRedemption.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'redemptions': [r.to_dict() for r in redemptions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': redemptions.total,
                'pages': redemptions.pages
            }
        }
    })

@gamification_bp.route('/admin/rewards', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_reward():
    """Create a new reward (admin only)."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role not in ['super_admin', 'tenant_admin']:
        return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
    
    try:
        schema = RewardSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    try:
        reward_type = RewardType(data['type'])
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid reward type'}), 400
    
    reward = gamification_service.create_reward(
        name=data['name'],
        reward_type=reward_type,
        cost=data['cost'],
        value=data['value'],
        description=data['description'],
        rarity=data['rarity'],
        total_quantity=data['total_quantity'],
        available_from=data['available_from'],
        available_until=data['available_until']
    )
    
    return jsonify({
        'success': True,
        'data': reward.to_dict(),
        'message': 'Reward created successfully'
    }), 201


# ========== Goal Endpoints ==========

@gamification_bp.route('/goals', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_goals():
    """Get user's goals."""
    user_id = get_jwt_identity()
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    goals = gamification_service.get_user_goals(user_id, active_only)
    
    return jsonify({
        'success': True,
        'data': [goal.to_dict() for goal in goals]
    })

@gamification_bp.route('/goals', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_goal():
    """Create a personal goal."""
    user_id = get_jwt_identity()
    
    try:
        schema = GoalSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'success': False, 'errors': e.messages}), 400
    
    goal = gamification_service.create_user_goal(
        user_id=user_id,
        title=data['title'],
        goal_type=data['goal_type'],
        target_value=data['target_value'],
        description=data['description'],
        deadline=data['deadline']
    )
    
    return jsonify({
        'success': True,
        'data': goal.to_dict(),
        'message': 'Goal created successfully'
    }), 201

@gamification_bp.route('/goals/<int:goal_id>', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_goal():
    """Update a goal."""
    user_id = get_jwt_identity()
    goal = UserGoal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
    
    data = request.json
    
    if 'is_active' in data:
        goal.is_active = data['is_active']
    
    if 'current_value' in data:
        goal.update_progress(data['current_value'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': goal.to_dict(),
        'message': 'Goal updated successfully'
    })


# ========== Event Logging and Analytics ==========

@gamification_bp.route('/events', methods=['POST'])
@jwt_required()
@handle_exceptions
def log_event():
    """Log a gamification event."""
    user_id = get_jwt_identity()
    
    event_type = request.json.get('event_type')
    event_data = request.json.get('event_data', {})
    session_id = request.json.get('session_id')
    
    if not event_type:
        return jsonify({'success': False, 'message': 'event_type is required'}), 400
    
    gamification_service.log_event(
        user_id=user_id,
        event_type=event_type,
        event_data=event_data,
        session_id=session_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Event logged successfully'
    })


# ========== Integration Endpoints ==========

@gamification_bp.route('/integration/login', methods=['POST'])
@jwt_required()
@handle_exceptions
def handle_login():
    """Handle login gamification (called by auth system)."""
    user_id = get_jwt_identity()
    
    results = gamification_service.handle_user_login(user_id)
    
    return jsonify({
        'success': True,
        'data': results,
        'message': 'Login processed successfully'
    })

@gamification_bp.route('/integration/evaluation-completed', methods=['POST'])
@jwt_required()
@handle_exceptions
def handle_evaluation_completion():
    """Handle evaluation completion gamification."""
    user_id = get_jwt_identity()
    
    evaluation_id = request.json.get('evaluation_id')
    score = request.json.get('score')
    
    if not evaluation_id or score is None:
        return jsonify({
            'success': False, 
            'message': 'evaluation_id and score are required'
        }), 400
    
    results = gamification_service.handle_evaluation_completion(user_id, evaluation_id, score)
    
    return jsonify({
        'success': True,
        'data': results,
        'message': 'Evaluation completion processed successfully'
    })

@gamification_bp.route('/integration/program-completed', methods=['POST'])
@jwt_required()
@handle_exceptions
def handle_program_completion():
    """Handle program completion gamification."""
    user_id = get_jwt_identity()
    
    program_id = request.json.get('program_id')
    
    if not program_id:
        return jsonify({
            'success': False, 
            'message': 'program_id is required'
        }), 400
    
    results = gamification_service.handle_program_completion(user_id, program_id)
    
    return jsonify({
        'success': True,
        'data': results,
        'message': 'Program completion processed successfully'
    })


# ========== Social Features ==========

@gamification_bp.route('/social/friends', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_friends():
    """Get user's friends list (placeholder for future implementation)."""
    user_id = get_jwt_identity()
    
    # This would be implemented with friend relationship logic
    return jsonify({
        'success': True,
        'data': [],
        'message': 'Friends feature coming soon'
    })

@gamification_bp.route('/social/activity-feed', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_activity_feed():
    """Get social activity feed (placeholder for future implementation)."""
    user_id = get_jwt_identity()
    
    # This would show friends' achievements, challenge completions, etc.
    return jsonify({
        'success': True,
        'data': [],
        'message': 'Activity feed feature coming soon'
    })


# ========== Error Handlers ==========

@gamification_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@gamification_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'message': 'Access forbidden'
    }), 403

@gamification_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500