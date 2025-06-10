"""
Enhanced Gamification API Routes

Provides comprehensive endpoints for all gamification features including
achievements, badges, XP, levels, progress tracking, leaderboards, and social features.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.extensions import db
from app.services.gamification.gamification_manager import GamificationManager
from app.services.gamification.achievement_service import AchievementService
from app.services.gamification.badge_service import BadgeService
from app.services.gamification.xp_service import XPService
from app.services.gamification.level_service import LevelService
from app.services.gamification.progress_service import ProgressService
from app.services.gamification.leaderboard_service import LeaderboardService
from app.services.gamification.social_service import SocialService
from app.services.gamification.learning_path_service import LearningPathService
from app.utils.logger import get_logger

logger = get_logger(__name__)

gamification_v2_bp = Blueprint('gamification_v2', __name__, url_prefix='/api/v2/gamification')


def get_current_user_id():
    """Get current user ID from JWT token"""
    return get_jwt_identity()


def create_error_response(message: str, status_code: int = 400) -> tuple:
    """Create standardized error response"""
    return jsonify({'error': message, 'success': False}), status_code


def create_success_response(data: Any, message: str = 'Success') -> tuple:
    """Create standardized success response"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }), 200


# Dashboard and Overview Routes

@gamification_v2_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@jwt_required()
def get_gamification_dashboard(user_id: int):
    """Get comprehensive gamification dashboard for a user"""
    try:
        current_user_id = get_current_user_id()
        
        # Check if user can access this dashboard
        if current_user_id != user_id:
            # Add admin check here if needed
            pass
        
        manager = GamificationManager(db.session)
        dashboard_data = manager.get_gamification_dashboard(user_id)
        
        if not dashboard_data:
            return create_error_response('Failed to load dashboard data', 404)
        
        return create_success_response(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting gamification dashboard: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/summary/<int:user_id>', methods=['GET'])
@jwt_required()
def get_gamification_summary(user_id: int):
    """Get gamification summary for a user"""
    try:
        manager = GamificationManager(db.session)
        summary = manager.get_user_gamification_summary(user_id)
        
        return create_success_response(summary)
        
    except Exception as e:
        logger.error(f"Error getting gamification summary: {str(e)}")
        return create_error_response('Internal server error', 500)


# Event Triggering Routes

@gamification_v2_bp.route('/events/trigger', methods=['POST'])
@jwt_required()
def trigger_gamification_event():
    """Trigger a gamification event"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided')
        
        event_type = data.get('event_type')
        user_id = data.get('user_id') or get_current_user_id()
        event_data = data.get('event_data', {})
        
        if not event_type:
            return create_error_response('Event type is required')
        
        manager = GamificationManager(db.session)
        result = manager.trigger_event(event_type, user_id, event_data)
        
        return create_success_response(result)
        
    except Exception as e:
        logger.error(f"Error triggering gamification event: {str(e)}")
        return create_error_response('Internal server error', 500)


# XP and Level Routes

@gamification_v2_bp.route('/xp/award', methods=['POST'])
@jwt_required()
def award_xp():
    """Award XP to a user"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id') or get_current_user_id()
        source = data.get('source', 'manual')
        amount = data.get('amount', 0)
        multiplier = data.get('multiplier', 1.0)
        metadata = data.get('metadata', {})
        
        if amount <= 0:
            return create_error_response('Amount must be positive')
        
        xp_service = XPService(db.session)
        transaction = xp_service.award_xp(
            user_id=user_id,
            source=source,
            base_amount=amount,
            multiplier=multiplier,
            metadata=metadata
        )
        
        # Check for level up
        level_service = LevelService(db.session)
        level_result = level_service.update_user_level(user_id)
        
        response_data = {
            'xp_transaction': {
                'id': transaction.id,
                'amount': transaction.amount,
                'source': transaction.source,
                'multiplier': transaction.multiplier
            },
            'level_result': level_result
        }
        
        return create_success_response(response_data, 'XP awarded successfully')
        
    except Exception as e:
        logger.error(f"Error awarding XP: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/xp/history/<int:user_id>', methods=['GET'])
@jwt_required()
def get_xp_history(user_id: int):
    """Get XP transaction history for a user"""
    try:
        days = request.args.get('days', 30, type=int)
        source = request.args.get('source')
        
        xp_service = XPService(db.session)
        history = xp_service.get_user_xp_history(user_id, days, source)
        
        return create_success_response(history)
        
    except Exception as e:
        logger.error(f"Error getting XP history: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/xp/stats/<int:user_id>', methods=['GET'])
@jwt_required()
def get_xp_statistics(user_id: int):
    """Get XP statistics for a user"""
    try:
        xp_service = XPService(db.session)
        stats = xp_service.get_xp_statistics(user_id)
        
        return create_success_response(stats)
        
    except Exception as e:
        logger.error(f"Error getting XP statistics: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/level/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_level_progress(user_id: int):
    """Get level progress for a user"""
    try:
        level_service = LevelService(db.session)
        progress = level_service.get_level_progress(user_id)
        
        return create_success_response(progress)
        
    except Exception as e:
        logger.error(f"Error getting level progress: {str(e)}")
        return create_error_response('Internal server error', 500)


# Badge Routes

@gamification_v2_bp.route('/badges', methods=['POST'])
@jwt_required()
def create_badge():
    """Create a new badge"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided')
        
        badge_service = BadgeService(db.session)
        badge = badge_service.create_badge(data)
        
        return create_success_response({
            'id': badge.id,
            'name': badge.name,
            'description': badge.description,
            'rarity': badge.rarity
        }, 'Badge created successfully')
        
    except Exception as e:
        logger.error(f"Error creating badge: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/badges/award', methods=['POST'])
@jwt_required()
def award_badge():
    """Award a badge to a user"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id') or get_current_user_id()
        badge_id = data.get('badge_id')
        awarded_by = get_current_user_id()
        metadata = data.get('metadata', {})
        
        if not badge_id:
            return create_error_response('Badge ID is required')
        
        badge_service = BadgeService(db.session)
        user_badge = badge_service.award_badge(user_id, badge_id, awarded_by, metadata)
        
        return create_success_response({
            'id': user_badge.id,
            'earned_at': user_badge.earned_at.isoformat()
        }, 'Badge awarded successfully')
        
    except Exception as e:
        logger.error(f"Error awarding badge: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/badges/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_badges(user_id: int):
    """Get badges earned by a user"""
    try:
        category = request.args.get('category')
        
        badge_service = BadgeService(db.session)
        badges = badge_service.get_user_badges(user_id, category)
        
        return create_success_response(badges)
        
    except Exception as e:
        logger.error(f"Error getting user badges: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/badges/showcase/<int:user_id>', methods=['GET'])
@jwt_required()
def get_badge_showcase(user_id: int):
    """Get badge showcase for a user"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        badge_service = BadgeService(db.session)
        showcase = badge_service.get_badge_showcase(user_id, limit)
        
        return create_success_response(showcase)
        
    except Exception as e:
        logger.error(f"Error getting badge showcase: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/badges/available/<int:user_id>', methods=['GET'])
@jwt_required()
def get_available_badges(user_id: int):
    """Get badges available for a user to earn"""
    try:
        category = request.args.get('category')
        
        badge_service = BadgeService(db.session)
        badges = badge_service.get_available_badges(user_id, category)
        
        return create_success_response(badges)
        
    except Exception as e:
        logger.error(f"Error getting available badges: {str(e)}")
        return create_error_response('Internal server error', 500)


# Achievement Routes

@gamification_v2_bp.route('/achievements', methods=['POST'])
@jwt_required()
def create_achievement():
    """Create a new achievement"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided')
        
        data['created_by'] = get_current_user_id()
        
        achievement_service = AchievementService(db.session)
        achievement = achievement_service.create_achievement(data)
        
        return create_success_response({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description
        }, 'Achievement created successfully')
        
    except Exception as e:
        logger.error(f"Error creating achievement: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/achievements/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_achievements(user_id: int):
    """Get achievements earned by a user"""
    try:
        category = request.args.get('category')
        
        achievement_service = AchievementService(db.session)
        achievements = achievement_service.get_user_achievements(user_id, category)
        
        return create_success_response(achievements)
        
    except Exception as e:
        logger.error(f"Error getting user achievements: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/achievements/available/<int:user_id>', methods=['GET'])
@jwt_required()
def get_available_achievements(user_id: int):
    """Get achievements available for a user"""
    try:
        category = request.args.get('category')
        
        achievement_service = AchievementService(db.session)
        achievements = achievement_service.get_available_achievements(user_id, category)
        
        return create_success_response(achievements)
        
    except Exception as e:
        logger.error(f"Error getting available achievements: {str(e)}")
        return create_error_response('Internal server error', 500)


# Leaderboard Routes

@gamification_v2_bp.route('/leaderboards', methods=['POST'])
@jwt_required()
def create_leaderboard():
    """Create a new leaderboard"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided')
        
        data['created_by'] = get_current_user_id()
        
        leaderboard_service = LeaderboardService(db.session)
        leaderboard = leaderboard_service.create_leaderboard(data)
        
        return create_success_response({
            'id': leaderboard.id,
            'name': leaderboard.name,
            'type': leaderboard.leaderboard_type
        }, 'Leaderboard created successfully')
        
    except Exception as e:
        logger.error(f"Error creating leaderboard: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/leaderboards/<int:leaderboard_id>', methods=['GET'])
@jwt_required()
def get_leaderboard(leaderboard_id: int):
    """Get leaderboard data"""
    try:
        user_id = get_current_user_id()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        leaderboard_service = LeaderboardService(db.session)
        leaderboard_data = leaderboard_service.get_leaderboard(
            leaderboard_id, user_id, limit, offset
        )
        
        return create_success_response(leaderboard_data)
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/leaderboards/type/<leaderboard_type>', methods=['GET'])
@jwt_required()
def get_leaderboard_by_type(leaderboard_type: str):
    """Get leaderboard by type"""
    try:
        time_frame = request.args.get('time_frame', 'all_time')
        limit = request.args.get('limit', 50, type=int)
        
        leaderboard_service = LeaderboardService(db.session)
        leaderboard_data = leaderboard_service.get_leaderboard_by_type(
            leaderboard_type, time_frame, limit
        )
        
        return create_success_response(leaderboard_data)
        
    except Exception as e:
        logger.error(f"Error getting leaderboard by type: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/leaderboards/global', methods=['GET'])
@jwt_required()
def get_global_leaderboards():
    """Get global leaderboards"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        leaderboard_service = LeaderboardService(db.session)
        leaderboards = leaderboard_service.get_global_leaderboards(limit)
        
        return create_success_response(leaderboards)
        
    except Exception as e:
        logger.error(f"Error getting global leaderboards: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/leaderboards/rankings/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_rankings(user_id: int):
    """Get user's rankings across leaderboards"""
    try:
        leaderboard_service = LeaderboardService(db.session)
        rankings = leaderboard_service.get_user_rankings(user_id)
        
        return create_success_response(rankings)
        
    except Exception as e:
        logger.error(f"Error getting user rankings: {str(e)}")
        return create_error_response('Internal server error', 500)


# Social Features Routes

@gamification_v2_bp.route('/social/teams', methods=['POST'])
@jwt_required()
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided')
        
        creator_id = get_current_user_id()
        
        social_service = SocialService(db.session)
        team = social_service.create_team(data, creator_id)
        
        return create_success_response({
            'id': team.id,
            'name': team.name,
            'join_code': team.join_code
        }, 'Team created successfully')
        
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/social/teams/join', methods=['POST'])
@jwt_required()
def join_team():
    """Join a team"""
    try:
        data = request.get_json()
        
        user_id = get_current_user_id()
        team_id = data.get('team_id')
        join_code = data.get('join_code')
        
        if not team_id and not join_code:
            return create_error_response('Team ID or join code is required')
        
        social_service = SocialService(db.session)
        team_member = social_service.join_team(user_id, team_id, join_code)
        
        if not team_member:
            return create_error_response('Failed to join team', 400)
        
        return create_success_response({
            'team_id': team_member.team_id,
            'role': team_member.role,
            'joined_at': team_member.joined_at.isoformat()
        }, 'Joined team successfully')
        
    except Exception as e:
        logger.error(f"Error joining team: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/social/teams/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_teams(user_id: int):
    """Get teams a user belongs to"""
    try:
        social_service = SocialService(db.session)
        teams = social_service.get_user_teams(user_id)
        
        return create_success_response(teams)
        
    except Exception as e:
        logger.error(f"Error getting user teams: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/social/feed/<int:user_id>', methods=['GET'])
@jwt_required()
def get_social_feed(user_id: int):
    """Get social feed for a user"""
    try:
        team_id = request.args.get('team_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        social_service = SocialService(db.session)
        feed = social_service.get_social_feed(user_id, team_id, limit, offset)
        
        return create_success_response(feed)
        
    except Exception as e:
        logger.error(f"Error getting social feed: {str(e)}")
        return create_error_response('Internal server error', 500)


# Learning Path Routes

@gamification_v2_bp.route('/learning-paths', methods=['POST'])
@jwt_required()
def create_learning_path():
    """Create a new learning path"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('No data provided')
        
        creator_id = get_current_user_id()
        
        learning_path_service = LearningPathService(db.session)
        path = learning_path_service.create_learning_path(data, creator_id)
        
        return create_success_response({
            'id': path.id,
            'name': path.name,
            'description': path.description
        }, 'Learning path created successfully')
        
    except Exception as e:
        logger.error(f"Error creating learning path: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/learning-paths/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_learning_paths(user_id: int):
    """Get learning paths for a user"""
    try:
        status = request.args.get('status')
        
        learning_path_service = LearningPathService(db.session)
        paths = learning_path_service.get_user_learning_paths(user_id, status)
        
        return create_success_response(paths)
        
    except Exception as e:
        logger.error(f"Error getting user learning paths: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/learning-paths/recommended/<int:user_id>', methods=['GET'])
@jwt_required()
def get_recommended_learning_paths(user_id: int):
    """Get recommended learning paths for a user"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        learning_path_service = LearningPathService(db.session)
        recommendations = learning_path_service.get_recommended_paths(user_id, limit)
        
        return create_success_response(recommendations)
        
    except Exception as e:
        logger.error(f"Error getting recommended learning paths: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/learning-paths/<int:path_id>/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_learning_path_progress(path_id: int, user_id: int):
    """Get progress for a specific learning path"""
    try:
        learning_path_service = LearningPathService(db.session)
        progress = learning_path_service.get_path_progress(user_id, path_id)
        
        return create_success_response(progress)
        
    except Exception as e:
        logger.error(f"Error getting learning path progress: {str(e)}")
        return create_error_response('Internal server error', 500)


# Progress Tracking Routes

@gamification_v2_bp.route('/progress/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_progress(user_id: int):
    """Get progress trackers for a user"""
    try:
        progress_type = request.args.get('type')
        
        progress_service = ProgressService(db.session)
        progress = progress_service.get_user_progress(user_id, progress_type)
        
        return create_success_response(progress)
        
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/progress/dashboard/<int:user_id>', methods=['GET'])
@jwt_required()
def get_progress_dashboard(user_id: int):
    """Get progress dashboard for a user"""
    try:
        progress_service = ProgressService(db.session)
        dashboard = progress_service.get_progress_dashboard(user_id)
        
        return create_success_response(dashboard)
        
    except Exception as e:
        logger.error(f"Error getting progress dashboard: {str(e)}")
        return create_error_response('Internal server error', 500)


# Utility Routes

@gamification_v2_bp.route('/stats/global', methods=['GET'])
@jwt_required()
def get_global_stats():
    """Get global gamification statistics"""
    try:
        # This would aggregate stats from all services
        stats = {
            'total_users': 0,  # Would query from user service
            'total_xp_awarded': 0,  # Would aggregate from XP service
            'total_badges_earned': 0,  # Would aggregate from badge service
            'total_achievements_unlocked': 0,  # Would aggregate from achievement service
            'active_learning_paths': 0,  # Would query from learning path service
            'active_teams': 0  # Would query from social service
        }
        
        return create_success_response(stats)
        
    except Exception as e:
        logger.error(f"Error getting global stats: {str(e)}")
        return create_error_response('Internal server error', 500)


@gamification_v2_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'gamification_v2',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# Error Handlers

@gamification_v2_bp.errorhandler(400)
def bad_request(error):
    return create_error_response('Bad request', 400)


@gamification_v2_bp.errorhandler(401)
def unauthorized(error):
    return create_error_response('Unauthorized', 401)


@gamification_v2_bp.errorhandler(403)
def forbidden(error):
    return create_error_response('Forbidden', 403)


@gamification_v2_bp.errorhandler(404)
def not_found(error):
    return create_error_response('Not found', 404)


@gamification_v2_bp.errorhandler(500)
def internal_error(error):
    return create_error_response('Internal server error', 500)