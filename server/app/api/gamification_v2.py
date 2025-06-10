_('api_gamification_v2.message.enhanced_gamification_api_rou')
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
from flask_babel import _, lazy_gettext as _l
logger = get_logger(__name__)
gamification_v2_bp = Blueprint(_(
    'api_gamification_v2.message.gamification_v2_1'), __name__, url_prefix=
    '/api/v2/gamification')


def get_current_user_id():
    """Get current user ID from JWT token"""
    return get_jwt_identity()


def create_error_response(message: str, status_code: int=400) ->tuple:
    _('api_gamification_v2.error.create_standardized_error_resp')
    return jsonify({'error': message, 'success': False}), status_code


def create_success_response(data: Any, message: str=_(
    'i18n_translation_service.success.success')) ->tuple:
    _('api_gamification_v2.success.create_standardized_success_re')
    return jsonify({'success': True, 'message': message, 'data': data}), 200


@gamification_v2_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@jwt_required()
def get_gamification_dashboard(user_id: int):
    _('api_gamification_v2.message.get_comprehensive_gamification')
    try:
        current_user_id = get_current_user_id()
        if current_user_id != user_id:
            pass
        manager = GamificationManager(db.session)
        dashboard_data = manager.get_gamification_dashboard(user_id)
        if not dashboard_data:
            return create_error_response(_(
                'api_gamification_v2.error.failed_to_load_dashboard_data'), 404
                )
        return create_success_response(dashboard_data)
    except Exception as e:
        logger.error(f'Error getting gamification dashboard: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/summary/<int:user_id>', methods=['GET'])
@jwt_required()
def get_gamification_summary(user_id: int):
    _('api_gamification_v2.message.get_gamification_summary_for_a')
    try:
        manager = GamificationManager(db.session)
        summary = manager.get_user_gamification_summary(user_id)
        return create_success_response(summary)
    except Exception as e:
        logger.error(f'Error getting gamification summary: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/events/trigger', methods=['POST'])
@jwt_required()
def trigger_gamification_event():
    _('api_gamification_v2.message.trigger_a_gamification_event')
    try:
        data = request.get_json()
        if not data:
            return create_error_response(_(
                'api_ai_question_generation.label.no_data_provided_3'))
        event_type = data.get('event_type')
        user_id = data.get('user_id') or get_current_user_id()
        event_data = data.get('event_data', {})
        if not event_type:
            return create_error_response(_(
                'api_gamification_v2.validation.event_type_is_required'))
        manager = GamificationManager(db.session)
        result = manager.trigger_event(event_type, user_id, event_data)
        return create_success_response(result)
    except Exception as e:
        logger.error(f'Error triggering gamification event: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/xp/award', methods=['POST'])
@jwt_required()
def award_xp():
    _('api_gamification_v2.message.award_xp_to_a_user')
    try:
        data = request.get_json()
        user_id = data.get('user_id') or get_current_user_id()
        source = data.get('source', 'manual')
        amount = data.get('amount', 0)
        multiplier = data.get('multiplier', 1.0)
        metadata = data.get('metadata', {})
        if amount <= 0:
            return create_error_response(_(
                'api_gamification_v2.validation.amount_must_be_positive'))
        xp_service = XPService(db.session)
        transaction = xp_service.award_xp(user_id=user_id, source=source,
            base_amount=amount, multiplier=multiplier, metadata=metadata)
        level_service = LevelService(db.session)
        level_result = level_service.update_user_level(user_id)
        response_data = {'xp_transaction': {'id': transaction.id, 'amount':
            transaction.amount, 'source': transaction.source, 'multiplier':
            transaction.multiplier}, 'level_result': level_result}
        return create_success_response(response_data, _(
            'api_gamification_v2.success.xp_awarded_successfully'))
    except Exception as e:
        logger.error(f'Error awarding XP: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/xp/history/<int:user_id>', methods=['GET'])
@jwt_required()
def get_xp_history(user_id: int):
    _('api_gamification_v2.message.get_xp_transaction_history_for')
    try:
        days = request.args.get('days', 30, type=int)
        source = request.args.get('source')
        xp_service = XPService(db.session)
        history = xp_service.get_user_xp_history(user_id, days, source)
        return create_success_response(history)
    except Exception as e:
        logger.error(f'Error getting XP history: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/xp/stats/<int:user_id>', methods=['GET'])
@jwt_required()
def get_xp_statistics(user_id: int):
    _('api_gamification_v2.message.get_xp_statistics_for_a_user')
    try:
        xp_service = XPService(db.session)
        stats = xp_service.get_xp_statistics(user_id)
        return create_success_response(stats)
    except Exception as e:
        logger.error(f'Error getting XP statistics: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/level/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_level_progress(user_id: int):
    _('api_gamification_v2.message.get_level_progress_for_a_user')
    try:
        level_service = LevelService(db.session)
        progress = level_service.get_level_progress(user_id)
        return create_success_response(progress)
    except Exception as e:
        logger.error(f'Error getting level progress: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/badges', methods=['POST'])
@jwt_required()
def create_badge():
    _('gamification_badge_service.message.create_a_new_badge')
    try:
        data = request.get_json()
        if not data:
            return create_error_response(_(
                'api_ai_question_generation.label.no_data_provided_3'))
        badge_service = BadgeService(db.session)
        badge = badge_service.create_badge(data)
        return create_success_response({'id': badge.id, 'name': badge.name,
            'description': badge.description, 'rarity': badge.rarity}, _(
            'api_gamification.success.badge_created_successfully'))
    except Exception as e:
        logger.error(f'Error creating badge: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/badges/award', methods=['POST'])
@jwt_required()
def award_badge():
    _('gamification_badge_service.message.award_a_badge_to_a_user')
    try:
        data = request.get_json()
        user_id = data.get('user_id') or get_current_user_id()
        badge_id = data.get('badge_id')
        awarded_by = get_current_user_id()
        metadata = data.get('metadata', {})
        if not badge_id:
            return create_error_response(_(
                'api_gamification_v2.validation.badge_id_is_required'))
        badge_service = BadgeService(db.session)
        user_badge = badge_service.award_badge(user_id, badge_id,
            awarded_by, metadata)
        return create_success_response({'id': user_badge.id, 'earned_at':
            user_badge.earned_at.isoformat()}, _(
            'api_gamification.success.badge_awarded_successfully'))
    except Exception as e:
        logger.error(f'Error awarding badge: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/badges/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_badges(user_id: int):
    _('api_gamification_v2.message.get_badges_earned_by_a_user')
    try:
        category = request.args.get('category')
        badge_service = BadgeService(db.session)
        badges = badge_service.get_user_badges(user_id, category)
        return create_success_response(badges)
    except Exception as e:
        logger.error(f'Error getting user badges: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/badges/showcase/<int:user_id>', methods=['GET'])
@jwt_required()
def get_badge_showcase(user_id: int):
    _('api_gamification_v2.message.get_badge_showcase_for_a_user')
    try:
        limit = request.args.get('limit', 5, type=int)
        badge_service = BadgeService(db.session)
        showcase = badge_service.get_badge_showcase(user_id, limit)
        return create_success_response(showcase)
    except Exception as e:
        logger.error(f'Error getting badge showcase: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/badges/available/<int:user_id>', methods=['GET'])
@jwt_required()
def get_available_badges(user_id: int):
    _('api_gamification_v2.message.get_badges_available_for_a_use')
    try:
        category = request.args.get('category')
        badge_service = BadgeService(db.session)
        badges = badge_service.get_available_badges(user_id, category)
        return create_success_response(badges)
    except Exception as e:
        logger.error(f'Error getting available badges: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/achievements', methods=['POST'])
@jwt_required()
def create_achievement():
    _('api_gamification_v2.message.create_a_new_achievement')
    try:
        data = request.get_json()
        if not data:
            return create_error_response(_(
                'api_ai_question_generation.label.no_data_provided_3'))
        data['created_by'] = get_current_user_id()
        achievement_service = AchievementService(db.session)
        achievement = achievement_service.create_achievement(data)
        return create_success_response({'id': achievement.id, 'name':
            achievement.name, 'description': achievement.description}, _(
            'api_gamification_v2.success.achievement_created_successful'))
    except Exception as e:
        logger.error(f'Error creating achievement: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/achievements/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_achievements(user_id: int):
    _('api_gamification_v2.message.get_achievements_earned_by_a_u')
    try:
        category = request.args.get('category')
        achievement_service = AchievementService(db.session)
        achievements = achievement_service.get_user_achievements(user_id,
            category)
        return create_success_response(achievements)
    except Exception as e:
        logger.error(f'Error getting user achievements: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/achievements/available/<int:user_id>', methods=
    ['GET'])
@jwt_required()
def get_available_achievements(user_id: int):
    _('api_gamification_v2.message.get_achievements_available_for')
    try:
        category = request.args.get('category')
        achievement_service = AchievementService(db.session)
        achievements = achievement_service.get_available_achievements(user_id,
            category)
        return create_success_response(achievements)
    except Exception as e:
        logger.error(f'Error getting available achievements: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/leaderboards', methods=['POST'])
@jwt_required()
def create_leaderboard():
    _('gamification_leaderboard_service.message.create_a_new_leaderboard')
    try:
        data = request.get_json()
        if not data:
            return create_error_response(_(
                'api_ai_question_generation.label.no_data_provided_3'))
        data['created_by'] = get_current_user_id()
        leaderboard_service = LeaderboardService(db.session)
        leaderboard = leaderboard_service.create_leaderboard(data)
        return create_success_response({'id': leaderboard.id, 'name':
            leaderboard.name, 'type': leaderboard.leaderboard_type}, _(
            'api_gamification.success.leaderboard_created_successful'))
    except Exception as e:
        logger.error(f'Error creating leaderboard: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/leaderboards/<int:leaderboard_id>', methods=['GET']
    )
@jwt_required()
def get_leaderboard(leaderboard_id: int):
    _('api_gamification_v2.label.get_leaderboard_data')
    try:
        user_id = get_current_user_id()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        leaderboard_service = LeaderboardService(db.session)
        leaderboard_data = leaderboard_service.get_leaderboard(leaderboard_id,
            user_id, limit, offset)
        return create_success_response(leaderboard_data)
    except Exception as e:
        logger.error(f'Error getting leaderboard: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/leaderboards/type/<leaderboard_type>', methods=
    ['GET'])
@jwt_required()
def get_leaderboard_by_type(leaderboard_type: str):
    _('api_gamification_v2.message.get_leaderboard_by_type')
    try:
        time_frame = request.args.get('time_frame', 'all_time')
        limit = request.args.get('limit', 50, type=int)
        leaderboard_service = LeaderboardService(db.session)
        leaderboard_data = leaderboard_service.get_leaderboard_by_type(
            leaderboard_type, time_frame, limit)
        return create_success_response(leaderboard_data)
    except Exception as e:
        logger.error(f'Error getting leaderboard by type: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/leaderboards/global', methods=['GET'])
@jwt_required()
def get_global_leaderboards():
    _('api_gamification_v2.label.get_global_leaderboards')
    try:
        limit = request.args.get('limit', 10, type=int)
        leaderboard_service = LeaderboardService(db.session)
        leaderboards = leaderboard_service.get_global_leaderboards(limit)
        return create_success_response(leaderboards)
    except Exception as e:
        logger.error(f'Error getting global leaderboards: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/leaderboards/rankings/<int:user_id>', methods=[
    'GET'])
@jwt_required()
def get_user_rankings(user_id: int):
    _('api_gamification_v2.message.get_user_s_rankings_across_lea')
    try:
        leaderboard_service = LeaderboardService(db.session)
        rankings = leaderboard_service.get_user_rankings(user_id)
        return create_success_response(rankings)
    except Exception as e:
        logger.error(f'Error getting user rankings: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/social/teams', methods=['POST'])
@jwt_required()
def create_team():
    _('gamification_social_service.message.create_a_new_team')
    try:
        data = request.get_json()
        if not data:
            return create_error_response(_(
                'api_ai_question_generation.label.no_data_provided_3'))
        creator_id = get_current_user_id()
        social_service = SocialService(db.session)
        team = social_service.create_team(data, creator_id)
        return create_success_response({'id': team.id, 'name': team.name,
            'join_code': team.join_code}, _(
            'api_gamification.success.team_created_successfully'))
    except Exception as e:
        logger.error(f'Error creating team: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/social/teams/join', methods=['POST'])
@jwt_required()
def join_team():
    _('api_gamification_v2.label.join_a_team')
    try:
        data = request.get_json()
        user_id = get_current_user_id()
        team_id = data.get('team_id')
        join_code = data.get('join_code')
        if not team_id and not join_code:
            return create_error_response(_(
                'api_gamification_v2.validation.team_id_or_join_code_is_requir'
                ))
        social_service = SocialService(db.session)
        team_member = social_service.join_team(user_id, team_id, join_code)
        if not team_member:
            return create_error_response(_(
                'api_gamification.error.failed_to_join_team'), 400)
        return create_success_response({'team_id': team_member.team_id,
            'role': team_member.role, 'joined_at': team_member.joined_at.
            isoformat()}, _(
            'api_gamification_v2.success.joined_team_successfully'))
    except Exception as e:
        logger.error(f'Error joining team: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/social/teams/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_teams(user_id: int):
    _('api_gamification_v2.message.get_teams_a_user_belongs_to')
    try:
        social_service = SocialService(db.session)
        teams = social_service.get_user_teams(user_id)
        return create_success_response(teams)
    except Exception as e:
        logger.error(f'Error getting user teams: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/social/feed/<int:user_id>', methods=['GET'])
@jwt_required()
def get_social_feed(user_id: int):
    _('api_gamification_v2.message.get_social_feed_for_a_user')
    try:
        team_id = request.args.get('team_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        social_service = SocialService(db.session)
        feed = social_service.get_social_feed(user_id, team_id, limit, offset)
        return create_success_response(feed)
    except Exception as e:
        logger.error(f'Error getting social feed: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/learning-paths', methods=['POST'])
@jwt_required()
def create_learning_path():
    _('gamification_learning_path_service.message.create_a_new_learning_path')
    try:
        data = request.get_json()
        if not data:
            return create_error_response(_(
                'api_ai_question_generation.label.no_data_provided_3'))
        creator_id = get_current_user_id()
        learning_path_service = LearningPathService(db.session)
        path = learning_path_service.create_learning_path(data, creator_id)
        return create_success_response({'id': path.id, 'name': path.name,
            'description': path.description}, _(
            'api_gamification_v2.success.learning_path_created_successf'))
    except Exception as e:
        logger.error(f'Error creating learning path: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/learning-paths/user/<int:user_id>', methods=['GET']
    )
@jwt_required()
def get_user_learning_paths(user_id: int):
    _('api_gamification_v2.message.get_learning_paths_for_a_user')
    try:
        status = request.args.get('status')
        learning_path_service = LearningPathService(db.session)
        paths = learning_path_service.get_user_learning_paths(user_id, status)
        return create_success_response(paths)
    except Exception as e:
        logger.error(f'Error getting user learning paths: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/learning-paths/recommended/<int:user_id>',
    methods=['GET'])
@jwt_required()
def get_recommended_learning_paths(user_id: int):
    _('gamification_learning_path_service.message.get_recommended_learning_paths'
        )
    try:
        limit = request.args.get('limit', 5, type=int)
        learning_path_service = LearningPathService(db.session)
        recommendations = learning_path_service.get_recommended_paths(user_id,
            limit)
        return create_success_response(recommendations)
    except Exception as e:
        logger.error(f'Error getting recommended learning paths: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route(
    '/learning-paths/<int:path_id>/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_learning_path_progress(path_id: int, user_id: int):
    _('api_gamification_v2.message.get_progress_for_a_specific_le')
    try:
        learning_path_service = LearningPathService(db.session)
        progress = learning_path_service.get_path_progress(user_id, path_id)
        return create_success_response(progress)
    except Exception as e:
        logger.error(f'Error getting learning path progress: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/progress/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_progress(user_id: int):
    _('api_gamification_v2.message.get_progress_trackers_for_a_us')
    try:
        progress_type = request.args.get('type')
        progress_service = ProgressService(db.session)
        progress = progress_service.get_user_progress(user_id, progress_type)
        return create_success_response(progress)
    except Exception as e:
        logger.error(f'Error getting user progress: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/progress/dashboard/<int:user_id>', methods=['GET'])
@jwt_required()
def get_progress_dashboard(user_id: int):
    _('api_gamification_v2.message.get_progress_dashboard_for_a_u')
    try:
        progress_service = ProgressService(db.session)
        dashboard = progress_service.get_progress_dashboard(user_id)
        return create_success_response(dashboard)
    except Exception as e:
        logger.error(f'Error getting progress dashboard: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/stats/global', methods=['GET'])
@jwt_required()
def get_global_stats():
    _('api_gamification_v2.message.get_global_gamification_statis')
    try:
        stats = {'total_users': 0, 'total_xp_awarded': 0,
            'total_badges_earned': 0, 'total_achievements_unlocked': 0,
            'active_learning_paths': 0, 'active_teams': 0}
        return create_success_response(stats)
    except Exception as e:
        logger.error(f'Error getting global stats: {str(e)}')
        return create_error_response(_(
            'file_upload_api_example.error.internal_server_error_6'), 500)


@gamification_v2_bp.route('/health', methods=['GET'])
def health_check():
    _('api_gamification_v2.label.health_check_endpoint')
    return jsonify({'status': 'healthy', 'service': _(
        'api_gamification_v2.message.gamification_v2_1'), 'timestamp':
        datetime.utcnow().isoformat()}), 200


@gamification_v2_bp.errorhandler(400)
def bad_request(error):
    return create_error_response(_(
        'api_video_conferences.label.bad_request'), 400)


@gamification_v2_bp.errorhandler(401)
def unauthorized(error):
    return create_error_response(_(
        'programs_v2_session_routes.label.unauthorized_4'), 401)


@gamification_v2_bp.errorhandler(403)
def forbidden(error):
    return create_error_response(_(
        'beneficiaries_v2_notes_routes.label.forbidden_3'), 403)


@gamification_v2_bp.errorhandler(404)
def not_found(error):
    return create_error_response(_(
        'programs_v2_crud_routes.label.not_found_1'), 404)


@gamification_v2_bp.errorhandler(500)
def internal_error(error):
    return create_error_response(_(
        'file_upload_api_example.error.internal_server_error_6'), 500)
