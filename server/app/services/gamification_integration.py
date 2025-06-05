"""Gamification Integration Service - Hooks into existing BDC systems."""

from datetime import datetime
from typing import Dict, Any, Optional
from flask import current_app

from app.extensions import db
from app.services.gamification_service import GamificationService
from app.models.gamification import PointActivityType
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.program import ProgramEnrollment
from app.models.appointment import Appointment


class GamificationIntegration:
    """Service for integrating gamification with existing BDC systems."""
    
    def __init__(self):
        self.gamification_service = GamificationService()
    
    # ========== Authentication Integration ==========
    
    def handle_user_login(self, user_id: int, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification for user login."""
        try:
            # Update streak and award points
            results = self.gamification_service.handle_user_login(user_id)
            
            # Log additional session data if provided
            if session_data:
                self.gamification_service.log_event(
                    user_id, 'login_detailed', {
                        **results,
                        'session_info': session_data
                    }
                )
            
            return {
                'success': True,
                'gamification_results': results
            }
        except Exception as e:
            current_app.logger.error(f"Gamification login error for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_user_logout(self, user_id: int, session_duration_minutes: int = None) -> Dict[str, Any]:
        """Handle gamification for user logout."""
        try:
            # Log session duration if provided
            if session_duration_minutes:
                self.gamification_service.log_event(
                    user_id, 'logout', {
                        'session_duration_minutes': session_duration_minutes
                    }
                )
            
            return {'success': True}
        except Exception as e:
            current_app.logger.error(f"Gamification logout error for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Evaluation Integration ==========
    
    def handle_evaluation_started(self, user_id: int, evaluation_id: int, 
                                 evaluation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user starts an evaluation."""
        try:
            # Award points for starting evaluation
            points = self.gamification_service.award_points(
                user_id, 5, PointActivityType.COMPLETE_TEST,
                'evaluation', evaluation_id, 
                {'action': 'started', **(evaluation_data or {})}
            )
            
            # Update challenge progress for evaluation attempts
            self._update_evaluation_challenges(user_id, 'started')
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification evaluation start error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_evaluation_completed(self, user_id: int, evaluation_id: int, 
                                   score: float, evaluation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user completes an evaluation."""
        try:
            # Use the main gamification service method
            results = self.gamification_service.handle_evaluation_completion(
                user_id, evaluation_id, score
            )
            
            # Additional integration-specific logic
            if evaluation_data:
                # Award bonus points for specific evaluation types
                evaluation_type = evaluation_data.get('type')
                if evaluation_type == 'adaptive':
                    bonus_points = self.gamification_service.award_points(
                        user_id, 25, PointActivityType.COMPLETE_TEST,
                        'evaluation', evaluation_id,
                        {'bonus_type': 'adaptive_test'}
                    )
                    results['adaptive_bonus'] = bonus_points
                
                # Check for improvement achievements
                self._check_improvement_achievements(user_id, evaluation_id, score)
            
            return {
                'success': True,
                'gamification_results': results
            }
        except Exception as e:
            current_app.logger.error(f"Gamification evaluation completion error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_evaluation_reviewed(self, trainer_id: int, evaluation_id: int,
                                  feedback_quality: str = 'good') -> Dict[str, Any]:
        """Handle gamification when trainer reviews an evaluation."""
        try:
            # Award points to trainer for reviewing
            base_points = 15
            if feedback_quality == 'excellent':
                base_points = 25
            elif feedback_quality == 'good':
                base_points = 20
            
            points = self.gamification_service.award_points(
                trainer_id, base_points, PointActivityType.SOCIAL_INTERACTION,
                'evaluation', evaluation_id,
                {'action': 'reviewed', 'quality': feedback_quality}
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification evaluation review error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Program Integration ==========
    
    def handle_program_enrollment(self, user_id: int, program_id: int,
                                 program_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user enrolls in a program."""
        try:
            # Award points for enrollment
            points = self.gamification_service.award_points(
                user_id, 20, PointActivityType.PROGRAM_COMPLETION,
                'program', program_id,
                {'action': 'enrolled', **(program_data or {})}
            )
            
            # Update program enrollment goals
            self.gamification_service.update_goal_progress(
                user_id, 'program_enrollments', 1
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification program enrollment error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_program_module_completed(self, user_id: int, program_id: int, 
                                       module_id: int, completion_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user completes a program module."""
        try:
            # Award points based on module completion
            base_points = 30
            
            # Bonus for perfect completion
            if completion_data and completion_data.get('completion_percentage', 0) == 100:
                base_points += 20
            
            points = self.gamification_service.award_points(
                user_id, base_points, PointActivityType.PROGRAM_COMPLETION,
                'program_module', module_id,
                {'program_id': program_id, **(completion_data or {})}
            )
            
            # Update challenge progress
            self._update_program_challenges(user_id, 'module_completed')
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification module completion error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_program_completed(self, user_id: int, program_id: int,
                               completion_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user completes a program."""
        try:
            # Use the main gamification service method
            results = self.gamification_service.handle_program_completion(user_id, program_id)
            
            # Additional completion bonuses
            if completion_data:
                completion_time = completion_data.get('completion_time_days')
                if completion_time and completion_time <= 30:  # Completed in 30 days
                    bonus_points = self.gamification_service.award_points(
                        user_id, 100, PointActivityType.MILESTONE,
                        'program', program_id,
                        {'bonus_type': 'quick_completion', 'days': completion_time}
                    )
                    results['quick_completion_bonus'] = bonus_points
            
            return {
                'success': True,
                'gamification_results': results
            }
        except Exception as e:
            current_app.logger.error(f"Gamification program completion error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Appointment Integration ==========
    
    def handle_appointment_scheduled(self, user_id: int, appointment_id: int,
                                   appointment_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user schedules an appointment."""
        try:
            # Award points for proactive scheduling
            points = self.gamification_service.award_points(
                user_id, 10, PointActivityType.SOCIAL_INTERACTION,
                'appointment', appointment_id,
                {'action': 'scheduled', **(appointment_data or {})}
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification appointment scheduling error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_appointment_attended(self, user_id: int, appointment_id: int,
                                  attendance_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user attends an appointment."""
        try:
            # Award points for attendance
            base_points = 25
            
            # Bonus for early arrival
            if attendance_data and attendance_data.get('arrived_early', False):
                base_points += 10
            
            points = self.gamification_service.award_points(
                user_id, base_points, PointActivityType.SOCIAL_INTERACTION,
                'appointment', appointment_id,
                {'action': 'attended', **(attendance_data or {})}
            )
            
            # Update attendance goals
            self.gamification_service.update_goal_progress(
                user_id, 'appointments_attended', 1
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification appointment attendance error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Document Integration ==========
    
    def handle_document_uploaded(self, user_id: int, document_id: int,
                                document_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user uploads a document."""
        try:
            # Award points for document uploads
            points = self.gamification_service.award_points(
                user_id, 15, PointActivityType.SOCIAL_INTERACTION,
                'document', document_id,
                {'action': 'uploaded', **(document_data or {})}
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification document upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_document_shared(self, user_id: int, document_id: int, 
                              shared_with_count: int = 1) -> Dict[str, Any]:
        """Handle gamification when user shares a document."""
        try:
            # Award points based on sharing scope
            points = min(shared_with_count * 5, 50)  # Max 50 points
            
            awarded_points = self.gamification_service.award_points(
                user_id, points, PointActivityType.SOCIAL_INTERACTION,
                'document', document_id,
                {'action': 'shared', 'shared_with_count': shared_with_count}
            )
            
            return {
                'success': True,
                'points_earned': awarded_points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification document sharing error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Social Integration ==========
    
    def handle_message_sent(self, user_id: int, message_id: int,
                           message_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user sends a message."""
        try:
            # Award points for communication
            points = self.gamification_service.award_points(
                user_id, 5, PointActivityType.SOCIAL_INTERACTION,
                'message', message_id,
                {'action': 'sent', **(message_data or {})}
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification message sending error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_help_request(self, user_id: int, help_request_id: int,
                           help_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle gamification when user requests help."""
        try:
            # Award points for seeking help (encouraging engagement)
            points = self.gamification_service.award_points(
                user_id, 10, PointActivityType.SOCIAL_INTERACTION,
                'help_request', help_request_id,
                {'action': 'requested', **(help_data or {})}
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification help request error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_help_provided(self, user_id: int, help_request_id: int,
                            help_quality: str = 'good') -> Dict[str, Any]:
        """Handle gamification when user provides help."""
        try:
            # Award points based on help quality
            base_points = 20
            if help_quality == 'excellent':
                base_points = 35
            elif help_quality == 'good':
                base_points = 25
            
            points = self.gamification_service.award_points(
                user_id, base_points, PointActivityType.SOCIAL_INTERACTION,
                'help_request', help_request_id,
                {'action': 'provided', 'quality': help_quality}
            )
            
            return {
                'success': True,
                'points_earned': points
            }
        except Exception as e:
            current_app.logger.error(f"Gamification help provision error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Achievement Integration ==========
    
    def trigger_custom_achievement(self, user_id: int, achievement_key: str,
                                  context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a custom achievement for specific events."""
        try:
            # This could be used for special achievements like "First Perfect Score"
            self.gamification_service.log_event(
                user_id, f'custom_achievement_{achievement_key}',
                context_data or {}
            )
            
            # Check if this should trigger any badges
            self.gamification_service.check_and_award_achievements(
                user_id, metadata={'achievement_key': achievement_key, **(context_data or {})}
            )
            
            return {'success': True}
        except Exception as e:
            current_app.logger.error(f"Gamification custom achievement error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ========== Batch Integration ==========
    
    def handle_bulk_activity(self, activities: list) -> Dict[str, Any]:
        """Handle multiple gamification activities in batch."""
        results = []
        errors = []
        
        for activity in activities:
            try:
                activity_type = activity.get('type')
                user_id = activity.get('user_id')
                
                if not activity_type or not user_id:
                    errors.append({'activity': activity, 'error': 'Missing type or user_id'})
                    continue
                
                # Route to appropriate handler
                result = self._route_activity(activity_type, activity)
                results.append({'activity': activity, 'result': result})
                
            except Exception as e:
                errors.append({'activity': activity, 'error': str(e)})
        
        return {
            'success': len(errors) == 0,
            'processed': len(results),
            'errors': len(errors),
            'results': results,
            'error_details': errors
        }
    
    def _route_activity(self, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route activity to appropriate handler."""
        handlers = {
            'login': lambda data: self.handle_user_login(data['user_id'], data.get('session_data')),
            'evaluation_completed': lambda data: self.handle_evaluation_completed(
                data['user_id'], data['evaluation_id'], data['score'], data.get('evaluation_data')
            ),
            'program_completed': lambda data: self.handle_program_completed(
                data['user_id'], data['program_id'], data.get('completion_data')
            ),
            'appointment_attended': lambda data: self.handle_appointment_attended(
                data['user_id'], data['appointment_id'], data.get('attendance_data')
            ),
            'document_uploaded': lambda data: self.handle_document_uploaded(
                data['user_id'], data['document_id'], data.get('document_data')
            ),
        }
        
        handler = handlers.get(activity_type)
        if handler:
            return handler(activity_data)
        else:
            raise ValueError(f"Unknown activity type: {activity_type}")
    
    # ========== Helper Methods ==========
    
    def _update_evaluation_challenges(self, user_id: int, action: str):
        """Update challenge progress for evaluation-related challenges."""
        try:
            # Get active challenges that track evaluations
            participations = self.gamification_service.get_user_challenges(user_id)
            
            for participation in participations:
                if not participation.is_completed and participation.challenge.goals:
                    for goal_key, goal_config in participation.challenge.goals.items():
                        if goal_config.get('type') == f'evaluation_{action}':
                            current = participation.progress.get(goal_key, 0)
                            self.gamification_service.update_challenge_progress(
                                user_id, participation.challenge_id, goal_key, current + 1
                            )
        except Exception as e:
            current_app.logger.error(f"Error updating evaluation challenges: {str(e)}")
    
    def _update_program_challenges(self, user_id: int, action: str):
        """Update challenge progress for program-related challenges."""
        try:
            # Get active challenges that track programs
            participations = self.gamification_service.get_user_challenges(user_id)
            
            for participation in participations:
                if not participation.is_completed and participation.challenge.goals:
                    for goal_key, goal_config in participation.challenge.goals.items():
                        if goal_config.get('type') == f'program_{action}':
                            current = participation.progress.get(goal_key, 0)
                            self.gamification_service.update_challenge_progress(
                                user_id, participation.challenge_id, goal_key, current + 1
                            )
        except Exception as e:
            current_app.logger.error(f"Error updating program challenges: {str(e)}")
    
    def _check_improvement_achievements(self, user_id: int, evaluation_id: int, score: float):
        """Check for improvement-based achievements."""
        try:
            # Get previous evaluations to check for improvement
            previous_evaluations = Evaluation.query.filter(
                Evaluation.beneficiary_id == user_id,
                Evaluation.id != evaluation_id,
                Evaluation.status == 'completed'
            ).order_by(Evaluation.completed_at.desc()).limit(5).all()
            
            if previous_evaluations:
                previous_scores = [e.score for e in previous_evaluations if e.score is not None]
                if previous_scores:
                    avg_previous = sum(previous_scores) / len(previous_scores)
                    improvement = score - avg_previous
                    
                    # Award improvement bonus
                    if improvement >= 20:  # 20+ point improvement
                        self.gamification_service.award_points(
                            user_id, 50, PointActivityType.MILESTONE,
                            'evaluation', evaluation_id,
                            {'improvement': improvement, 'bonus_type': 'significant_improvement'}
                        )
                    elif improvement >= 10:  # 10+ point improvement
                        self.gamification_service.award_points(
                            user_id, 25, PointActivityType.MILESTONE,
                            'evaluation', evaluation_id,
                            {'improvement': improvement, 'bonus_type': 'good_improvement'}
                        )
        except Exception as e:
            current_app.logger.error(f"Error checking improvement achievements: {str(e)}")
    
    # ========== Analytics Integration ==========
    
    def get_user_engagement_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive engagement summary including gamification data."""
        try:
            # Get base gamification metrics
            metrics = self.gamification_service.get_engagement_metrics(user_id, days)
            
            # Add integration-specific metrics
            progress_summary = self.gamification_service.get_user_progress_summary(user_id)
            
            return {
                'success': True,
                'period_days': days,
                'engagement_metrics': metrics,
                'progress_summary': progress_summary,
                'gamification_health': {
                    'active_goals': len([g for g in progress_summary['goals'] if g['is_active']]),
                    'recent_badges': len([b for b in progress_summary['badges'] 
                                        if (datetime.utcnow() - datetime.fromisoformat(b['earned_at'].replace('Z', '+00:00'))).days <= days]),
                    'active_challenges': len([c for c in progress_summary['challenges'] 
                                           if not c['is_completed']])
                }
            }
        except Exception as e:
            current_app.logger.error(f"Error getting engagement summary: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========== Global Integration Instance ==========

gamification_integration = GamificationIntegration()