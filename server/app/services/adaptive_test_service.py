"""Adaptive Test Service implementing Computerized Adaptive Testing (CAT) with IRT."""

import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import (
    AdaptiveTestPool, AdaptiveQuestion, AdaptiveTestSession,
    AdaptiveResponse, AdaptiveTestReport, Beneficiary
)
from app.utils import clear_model_cache


class AdaptiveTestService:
    """Service for managing adaptive tests using CAT algorithm and IRT."""
    
    # Constants for IRT calculations
    D = 1.7  # Scaling constant for logistic function
    MIN_SE = 0.01  # Minimum standard error to avoid division by zero
    MAX_ABILITY = 3.0  # Maximum ability estimate
    MIN_ABILITY = -3.0  # Minimum ability estimate
    
    @staticmethod
    def create_question_pool(tenant_id: int, data: Dict[str, Any]) -> AdaptiveTestPool:
        """Create a new adaptive test question pool."""
        try:
            pool = AdaptiveTestPool(
                tenant_id=tenant_id,
                name=data['name'],
                description=data.get('description'),
                subject=data.get('subject'),
                grade_level=data.get('grade_level'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(pool)
            db.session.commit()
            
            clear_model_cache('adaptive_test_pools')
            return pool
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def add_question_to_pool(pool_id: int, data: Dict[str, Any]) -> AdaptiveQuestion:
        """Add a question with IRT parameters to the pool."""
        try:
            # Validate IRT parameters
            difficulty = data.get('difficulty', 0.0)
            discrimination = data.get('discrimination', 1.0)
            guessing = data.get('guessing', 0.0)
            
            # Ensure parameters are within reasonable bounds
            difficulty = max(MIN_ABILITY, min(MAX_ABILITY, difficulty))
            discrimination = max(0.1, min(2.5, discrimination))
            guessing = max(0.0, min(0.3, guessing))
            
            question = AdaptiveQuestion(
                pool_id=pool_id,
                text=data['text'],
                type=data['type'],
                options=data.get('options'),
                correct_answer=data.get('correct_answer'),
                explanation=data.get('explanation'),
                difficulty=difficulty,
                discrimination=discrimination,
                guessing=guessing,
                difficulty_level=data.get('difficulty_level', 5),
                topic=data.get('topic'),
                subtopic=data.get('subtopic'),
                cognitive_level=data.get('cognitive_level'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(question)
            
            # Update pool total questions
            pool = AdaptiveTestPool.query.get(pool_id)
            if pool:
                pool.total_questions += 1
                pool.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            clear_model_cache('adaptive_questions')
            return question
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def start_adaptive_session(
        pool_id: int,
        beneficiary_id: int,
        config: Optional[Dict[str, Any]] = None
    ) -> AdaptiveTestSession:
        """Start a new adaptive test session."""
        try:
            # Check for existing in-progress session
            existing_session = AdaptiveTestSession.query.filter_by(
                pool_id=pool_id,
                beneficiary_id=beneficiary_id,
                status='in_progress'
            ).first()
            
            if existing_session:
                return existing_session
            
            # Default configuration
            default_config = {
                'max_questions': 20,
                'max_time': None,
                'standard_error_threshold': 0.3,
                'initial_ability': 0.0,
                'selection_method': 'maximum_information',
                'topic_balancing': True,
                'exposure_control': True
            }
            
            if config:
                default_config.update(config)
            
            session = AdaptiveTestSession(
                pool_id=pool_id,
                beneficiary_id=beneficiary_id,
                test_id=config.get('test_id') if config else None,
                max_questions=default_config['max_questions'],
                max_time=default_config['max_time'],
                standard_error_threshold=default_config['standard_error_threshold'],
                initial_ability=default_config['initial_ability'],
                current_ability=default_config['initial_ability'],
                selection_method=default_config['selection_method'],
                topic_balancing=default_config['topic_balancing'],
                exposure_control=default_config['exposure_control'],
                asked_questions=[],
                topic_coverage={},
                ability_history=[default_config['initial_ability']]
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_next_question(session_id: int) -> Optional[AdaptiveQuestion]:
        """Select the next question based on CAT algorithm."""
        session = AdaptiveTestSession.query.get(session_id)
        if not session or session.status != 'in_progress':
            return None
        
        # Check stopping criteria
        should_stop, reason = session.should_stop()
        if should_stop:
            AdaptiveTestService._complete_session(session, reason)
            return None
        
        # Get available questions
        available_questions = AdaptiveTestService._get_available_questions(session)
        if not available_questions:
            AdaptiveTestService._complete_session(session, "No more questions available")
            return None
        
        # Select next question based on method
        if session.selection_method == 'maximum_information':
            next_question = AdaptiveTestService._select_by_maximum_information(
                available_questions, session.current_ability
            )
        elif session.selection_method == 'closest_difficulty':
            next_question = AdaptiveTestService._select_by_closest_difficulty(
                available_questions, session.current_ability
            )
        else:
            # Default to random selection
            next_question = random.choice(available_questions)
        
        # Apply exposure control if enabled
        if session.exposure_control and next_question:
            next_question = AdaptiveTestService._apply_exposure_control(
                next_question, available_questions, session
            )
        
        return next_question
    
    @staticmethod
    def submit_response(
        session_id: int,
        question_id: int,
        answer: Any,
        response_time: Optional[float] = None
    ) -> Tuple[AdaptiveResponse, float, float]:
        """Submit response and update ability estimate."""
        try:
            session = AdaptiveTestSession.query.get(session_id)
            if not session or session.status != 'in_progress':
                raise ValueError("Invalid or completed session")
            
            question = AdaptiveQuestion.query.get(question_id)
            if not question:
                raise ValueError("Invalid question")
            
            # Check if answer is correct
            is_correct = AdaptiveTestService._check_answer(question, answer)
            
            # Store current ability before update
            ability_before = session.current_ability
            
            # Update ability estimate using Maximum Likelihood Estimation
            new_ability, se = AdaptiveTestService._update_ability_estimate(
                session, is_correct, question
            )
            
            # Create response record
            response = AdaptiveResponse(
                session_id=session_id,
                question_id=question_id,
                answer=answer,
                is_correct=is_correct,
                response_time=response_time,
                ability_before=ability_before,
                ability_after=new_ability,
                se_after=se,
                question_difficulty=question.difficulty,
                question_discrimination=question.discrimination,
                question_guessing=question.guessing,
                question_number=session.questions_answered + 1
            )
            
            db.session.add(response)
            
            # Update session
            session.current_ability = new_ability
            session.ability_se = se
            session.questions_answered += 1
            session.ability_history.append(new_ability)
            
            # Update asked questions
            if session.asked_questions is None:
                session.asked_questions = []
            session.asked_questions.append(question_id)
            
            # Update topic coverage
            if question.topic:
                if session.topic_coverage is None:
                    session.topic_coverage = {}
                if question.topic not in session.topic_coverage:
                    session.topic_coverage[question.topic] = 0
                session.topic_coverage[question.topic] += 1
            
            # Update question statistics
            question.usage_count += 1
            if is_correct:
                question.correct_count += 1
            
            # Update average response time
            if response_time:
                if question.average_response_time:
                    # Weighted average
                    question.average_response_time = (
                        (question.average_response_time * (question.usage_count - 1) + response_time) /
                        question.usage_count
                    )
                else:
                    question.average_response_time = response_time
            
            # Update exposure rate
            total_sessions = AdaptiveTestSession.query.filter_by(
                pool_id=session.pool_id,
                status='completed'
            ).count() + 1
            question.exposure_rate = question.usage_count / total_sessions
            
            session.updated_at = datetime.utcnow()
            db.session.commit()
            
            return response, new_ability, se
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def complete_session(session_id: int) -> AdaptiveTestSession:
        """Complete an adaptive test session and generate report."""
        try:
            session = AdaptiveTestSession.query.get(session_id)
            if not session or session.status == 'completed':
                raise ValueError("Invalid or already completed session")
            
            # Complete the session
            session.status = 'completed'
            session.end_time = datetime.utcnow()
            session.total_time_seconds = int(
                (session.end_time - session.start_time).total_seconds()
            )
            
            # Calculate final ability and confidence interval
            session.final_ability = session.current_ability
            session.final_se = session.ability_se or 0.3
            
            # 95% confidence interval
            z_score = 1.96
            session.confidence_interval_lower = max(
                MIN_ABILITY, session.final_ability - z_score * session.final_se
            )
            session.confidence_interval_upper = min(
                MAX_ABILITY, session.final_ability + z_score * session.final_se
            )
            
            db.session.commit()
            
            # Generate report
            AdaptiveTestService.generate_report(session_id)
            
            clear_model_cache('adaptive_test_sessions')
            return session
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def generate_report(session_id: int) -> AdaptiveTestReport:
        """Generate detailed report for completed session."""
        try:
            session = AdaptiveTestSession.query.get(session_id)
            if not session or session.status != 'completed':
                raise ValueError("Session not completed")
            
            # Check if report already exists
            existing_report = AdaptiveTestReport.query.filter_by(
                session_id=session_id
            ).first()
            if existing_report:
                return existing_report
            
            # Get all responses
            responses = AdaptiveResponse.query.filter_by(
                session_id=session_id
            ).order_by(AdaptiveResponse.question_number).all()
            
            # Calculate statistics
            total_questions = len(responses)
            correct_answers = sum(1 for r in responses if r.is_correct)
            
            # Calculate average difficulty
            avg_difficulty = sum(r.question_difficulty for r in responses) / total_questions if total_questions > 0 else 0
            
            # Analyze by topic
            topic_performance = {}
            for response in responses:
                question = AdaptiveQuestion.query.get(response.question_id)
                if question and question.topic:
                    if question.topic not in topic_performance:
                        topic_performance[question.topic] = {
                            'total': 0,
                            'correct': 0,
                            'avg_difficulty': 0,
                            'difficulties': []
                        }
                    
                    topic_performance[question.topic]['total'] += 1
                    if response.is_correct:
                        topic_performance[question.topic]['correct'] += 1
                    topic_performance[question.topic]['difficulties'].append(question.difficulty)
            
            # Calculate topic scores and identify strengths/weaknesses
            topic_scores = {}
            topic_strengths = []
            topic_weaknesses = []
            
            for topic, stats in topic_performance.items():
                score = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                avg_topic_difficulty = sum(stats['difficulties']) / len(stats['difficulties'])
                
                topic_scores[topic] = {
                    'score': score,
                    'total_questions': stats['total'],
                    'correct_answers': stats['correct'],
                    'average_difficulty': avg_topic_difficulty
                }
                
                if score >= 80:
                    topic_strengths.append(topic)
                elif score < 50:
                    topic_weaknesses.append(topic)
            
            # Determine performance level
            ability_percentile = AdaptiveTestService._calculate_percentile(session.final_ability)
            
            if ability_percentile >= 90:
                performance_level = "Advanced"
            elif ability_percentile >= 70:
                performance_level = "Proficient"
            elif ability_percentile >= 30:
                performance_level = "Basic"
            else:
                performance_level = "Below Basic"
            
            # Generate recommendations
            recommended_topics = []
            if topic_weaknesses:
                recommended_topics = topic_weaknesses[:3]  # Top 3 weak topics
            
            recommended_difficulty = session.final_ability + 0.5  # Slightly above current level
            
            next_steps = []
            if performance_level == "Advanced":
                next_steps.append("Consider advanced topics and challenging materials")
                next_steps.append("Explore teaching or mentoring opportunities")
            elif performance_level == "Proficient":
                next_steps.append("Focus on mastering remaining concepts")
                next_steps.append("Challenge yourself with harder problems")
            else:
                next_steps.append("Review fundamental concepts")
                next_steps.append("Practice regularly with guided exercises")
                if topic_weaknesses:
                    next_steps.append(f"Focus on improving: {', '.join(topic_weaknesses[:2])}")
            
            # Analyze response patterns
            response_patterns = AdaptiveTestService._analyze_response_patterns(responses)
            
            # Create report
            report = AdaptiveTestReport(
                session_id=session_id,
                final_ability=session.final_ability,
                ability_percentile=ability_percentile,
                performance_level=performance_level,
                topic_strengths=topic_strengths,
                topic_weaknesses=topic_weaknesses,
                topic_scores=topic_scores,
                response_patterns=response_patterns,
                recommended_topics=recommended_topics,
                recommended_difficulty=recommended_difficulty,
                next_steps=next_steps,
                total_questions=total_questions,
                correct_answers=correct_answers,
                average_difficulty=avg_difficulty,
                response_consistency=AdaptiveTestService._calculate_consistency(responses)
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    # Helper methods
    
    @staticmethod
    def _get_available_questions(session: AdaptiveTestSession) -> List[AdaptiveQuestion]:
        """Get questions that haven't been asked yet."""
        query = AdaptiveQuestion.query.filter(
            AdaptiveQuestion.pool_id == session.pool_id,
            AdaptiveQuestion.is_active == True,
            ~AdaptiveQuestion.id.in_(session.asked_questions or [])
        )
        
        # Apply topic balancing if enabled
        if session.topic_balancing and session.topic_coverage:
            # Find topics with fewer questions asked
            avg_coverage = sum(session.topic_coverage.values()) / len(session.topic_coverage)
            underrepresented_topics = [
                topic for topic, count in session.topic_coverage.items()
                if count < avg_coverage
            ]
            
            if underrepresented_topics:
                # Prioritize underrepresented topics
                query = query.filter(
                    AdaptiveQuestion.topic.in_(underrepresented_topics)
                )
        
        return query.all()
    
    @staticmethod
    def _select_by_maximum_information(
        questions: List[AdaptiveQuestion],
        current_ability: float
    ) -> Optional[AdaptiveQuestion]:
        """Select question that provides maximum information at current ability."""
        if not questions:
            return None
        
        max_info = -1
        best_question = None
        
        for question in questions:
            info = question.calculate_information(current_ability)
            
            # Update question's information value
            question.information_value = info
            
            if info > max_info:
                max_info = info
                best_question = question
        
        return best_question
    
    @staticmethod
    def _select_by_closest_difficulty(
        questions: List[AdaptiveQuestion],
        current_ability: float
    ) -> Optional[AdaptiveQuestion]:
        """Select question with difficulty closest to current ability."""
        if not questions:
            return None
        
        return min(questions, key=lambda q: abs(q.difficulty - current_ability))
    
    @staticmethod
    def _apply_exposure_control(
        selected_question: AdaptiveQuestion,
        available_questions: List[AdaptiveQuestion],
        session: AdaptiveTestSession
    ) -> AdaptiveQuestion:
        """Apply exposure control to prevent overuse of questions."""
        # If exposure rate is too high, select alternative
        if selected_question.exposure_rate > 0.3:  # 30% exposure threshold
            # Find questions with similar information value but lower exposure
            alternatives = [
                q for q in available_questions
                if q.exposure_rate < 0.3 and
                abs(q.calculate_information(session.current_ability) - 
                    selected_question.calculate_information(session.current_ability)) < 0.1
            ]
            
            if alternatives:
                return random.choice(alternatives)
        
        return selected_question
    
    @staticmethod
    def _check_answer(question: AdaptiveQuestion, answer: Any) -> bool:
        """Check if the answer is correct."""
        if question.type == 'multiple_choice':
            if isinstance(question.correct_answer, list):
                return sorted(answer) == sorted(question.correct_answer)
            return answer == question.correct_answer
        elif question.type == 'true_false':
            return answer == question.correct_answer
        elif question.type == 'matching':
            return answer == question.correct_answer
        elif question.type == 'ordering':
            return answer == question.correct_answer
        else:
            # For other types, may need custom logic
            return True
    
    @staticmethod
    def _update_ability_estimate(
        session: AdaptiveTestSession,
        is_correct: bool,
        question: AdaptiveQuestion
    ) -> Tuple[float, float]:
        """Update ability estimate using Maximum Likelihood Estimation."""
        # Get all responses for this session
        responses = AdaptiveResponse.query.filter_by(
            session_id=session.id
        ).all()
        
        # Add current response
        current_response = {
            'is_correct': is_correct,
            'difficulty': question.difficulty,
            'discrimination': question.discrimination,
            'guessing': question.guessing
        }
        
        # Newton-Raphson method for MLE
        theta = session.current_ability  # Initial estimate
        max_iterations = 50
        tolerance = 0.001
        
        for _ in range(max_iterations):
            # Calculate first and second derivatives
            sum_info = 0
            sum_score = 0
            
            # Include all previous responses
            for response in responses:
                q = AdaptiveQuestion.query.get(response.question_id)
                if q:
                    p = q.calculate_probability(theta)
                    info = q.calculate_information(theta)
                    
                    sum_info += info
                    if response.is_correct:
                        sum_score += (1 - p) * q.discrimination
                    else:
                        sum_score += -p * q.discrimination
            
            # Include current response
            p_current = question.calculate_probability(theta)
            info_current = question.calculate_information(theta)
            
            sum_info += info_current
            if is_correct:
                sum_score += (1 - p_current) * question.discrimination
            else:
                sum_score += -p_current * question.discrimination
            
            # Prevent division by zero
            if sum_info < MIN_SE:
                sum_info = MIN_SE
            
            # Update theta
            delta = sum_score / sum_info
            theta_new = theta + delta
            
            # Bound theta
            theta_new = max(MIN_ABILITY, min(MAX_ABILITY, theta_new))
            
            # Check convergence
            if abs(theta_new - theta) < tolerance:
                break
            
            theta = theta_new
        
        # Calculate standard error
        se = 1 / math.sqrt(sum_info) if sum_info > 0 else 1.0
        
        return theta, se
    
    @staticmethod
    def _complete_session(session: AdaptiveTestSession, reason: str):
        """Complete a session with given reason."""
        session.status = 'completed'
        session.end_time = datetime.utcnow()
        session.total_time_seconds = int(
            (session.end_time - session.start_time).total_seconds()
        )
        session.final_ability = session.current_ability
        session.final_se = session.ability_se or 0.3
        
        # Calculate confidence interval
        z_score = 1.96
        session.confidence_interval_lower = max(
            MIN_ABILITY, session.final_ability - z_score * session.final_se
        )
        session.confidence_interval_upper = min(
            MAX_ABILITY, session.final_ability + z_score * session.final_se
        )
        
        db.session.commit()
    
    @staticmethod
    def _calculate_percentile(ability: float) -> float:
        """Calculate percentile rank for given ability."""
        # Assuming normal distribution with mean=0, sd=1
        # Using approximation of normal CDF
        import scipy.stats
        percentile = scipy.stats.norm.cdf(ability) * 100
        return round(percentile, 1)
    
    @staticmethod
    def _analyze_response_patterns(responses: List[AdaptiveResponse]) -> Dict[str, Any]:
        """Analyze patterns in responses."""
        patterns = {
            'response_time_trend': None,
            'accuracy_trend': None,
            'difficulty_adaptation': None
        }
        
        if len(responses) < 3:
            return patterns
        
        # Analyze response time trend
        response_times = [r.response_time for r in responses if r.response_time]
        if len(response_times) > 3:
            # Simple linear trend
            x = list(range(len(response_times)))
            y = response_times
            if len(x) == len(y):
                slope = (y[-1] - y[0]) / (len(y) - 1) if len(y) > 1 else 0
                patterns['response_time_trend'] = 'increasing' if slope > 1 else 'decreasing' if slope < -1 else 'stable'
        
        # Analyze accuracy trend (moving average)
        window_size = 3
        accuracy_windows = []
        for i in range(len(responses) - window_size + 1):
            window = responses[i:i + window_size]
            accuracy = sum(1 for r in window if r.is_correct) / window_size
            accuracy_windows.append(accuracy)
        
        if accuracy_windows:
            if accuracy_windows[-1] > accuracy_windows[0] + 0.2:
                patterns['accuracy_trend'] = 'improving'
            elif accuracy_windows[-1] < accuracy_windows[0] - 0.2:
                patterns['accuracy_trend'] = 'declining'
            else:
                patterns['accuracy_trend'] = 'stable'
        
        # Analyze difficulty adaptation
        difficulties = [r.question_difficulty for r in responses]
        if difficulties:
            avg_first_half = sum(difficulties[:len(difficulties)//2]) / (len(difficulties)//2)
            avg_second_half = sum(difficulties[len(difficulties)//2:]) / (len(difficulties) - len(difficulties)//2)
            
            if avg_second_half > avg_first_half + 0.3:
                patterns['difficulty_adaptation'] = 'increased'
            elif avg_second_half < avg_first_half - 0.3:
                patterns['difficulty_adaptation'] = 'decreased'
            else:
                patterns['difficulty_adaptation'] = 'stable'
        
        return patterns
    
    @staticmethod
    def _calculate_consistency(responses: List[AdaptiveResponse]) -> float:
        """Calculate response consistency score."""
        if len(responses) < 5:
            return 1.0  # Not enough data
        
        # Group responses by difficulty ranges
        difficulty_ranges = [
            (-3, -1),  # Easy
            (-1, 1),   # Medium
            (1, 3)     # Hard
        ]
        
        consistency_scores = []
        
        for min_diff, max_diff in difficulty_ranges:
            range_responses = [
                r for r in responses
                if min_diff <= r.question_difficulty <= max_diff
            ]
            
            if len(range_responses) >= 2:
                # Calculate consistency within this difficulty range
                correct_count = sum(1 for r in range_responses if r.is_correct)
                expected_rate = sum(
                    AdaptiveQuestion.query.get(r.question_id).calculate_probability(r.ability_before)
                    for r in range_responses
                ) / len(range_responses)
                
                actual_rate = correct_count / len(range_responses)
                
                # Consistency is how close actual is to expected
                consistency = 1 - abs(actual_rate - expected_rate)
                consistency_scores.append(consistency)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 1.0


class AdaptiveQuestionService:
    """Service for managing adaptive questions."""
    
    @staticmethod
    def calibrate_irt_parameters(question_id: int) -> Dict[str, float]:
        """Calibrate IRT parameters based on response data."""
        question = AdaptiveQuestion.query.get(question_id)
        if not question:
            return None
        
        # Get all responses for this question
        responses = AdaptiveResponse.query.filter_by(
            question_id=question_id
        ).all()
        
        if len(responses) < 30:  # Need sufficient data
            return {
                'difficulty': question.difficulty,
                'discrimination': question.discrimination,
                'guessing': question.guessing,
                'status': 'insufficient_data'
            }
        
        # Simple calibration using response data
        # Group by ability ranges
        ability_ranges = [
            (-3, -2), (-2, -1), (-1, 0), (0, 1), (1, 2), (2, 3)
        ]
        
        calibration_data = []
        
        for min_ability, max_ability in ability_ranges:
            range_responses = [
                r for r in responses
                if min_ability <= r.ability_before < max_ability
            ]
            
            if range_responses:
                avg_ability = sum(r.ability_before for r in range_responses) / len(range_responses)
                success_rate = sum(1 for r in range_responses if r.is_correct) / len(range_responses)
                calibration_data.append((avg_ability, success_rate))
        
        if len(calibration_data) < 3:
            return {
                'difficulty': question.difficulty,
                'discrimination': question.discrimination,
                'guessing': question.guessing,
                'status': 'insufficient_variation'
            }
        
        # Estimate parameters (simplified)
        # Find ability level where success rate is ~0.5
        interpolated_difficulty = 0.0
        for i in range(len(calibration_data) - 1):
            ability1, rate1 = calibration_data[i]
            ability2, rate2 = calibration_data[i + 1]
            
            if rate1 >= 0.5 >= rate2:
                # Linear interpolation
                interpolated_difficulty = ability1 + (ability2 - ability1) * (0.5 - rate1) / (rate2 - rate1)
                break
        
        # Estimate discrimination from slope at difficulty point
        # Higher slope = higher discrimination
        max_slope = 0
        for i in range(len(calibration_data) - 1):
            ability1, rate1 = calibration_data[i]
            ability2, rate2 = calibration_data[i + 1]
            slope = abs((rate2 - rate1) / (ability2 - ability1))
            max_slope = max(max_slope, slope)
        
        new_discrimination = min(2.5, max(0.1, max_slope * 2))  # Scale and bound
        
        # Estimate guessing from lowest ability success rate
        lowest_ability_rate = calibration_data[0][1] if calibration_data else 0
        new_guessing = min(0.3, max(0, lowest_ability_rate))
        
        # Update question parameters
        question.difficulty = interpolated_difficulty or question.difficulty
        question.discrimination = new_discrimination
        question.guessing = new_guessing
        db.session.commit()
        
        return {
            'difficulty': question.difficulty,
            'discrimination': question.discrimination,
            'guessing': question.guessing,
            'status': 'calibrated',
            'sample_size': len(responses)
        }
    
    @staticmethod
    def get_question_statistics(question_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a question."""
        question = AdaptiveQuestion.query.get(question_id)
        if not question:
            return None
        
        responses = AdaptiveResponse.query.filter_by(
            question_id=question_id
        ).all()
        
        if not responses:
            return {
                'usage_count': 0,
                'correct_rate': 0,
                'average_response_time': 0,
                'exposure_rate': 0,
                'discrimination_index': 0
            }
        
        # Calculate discrimination index
        # Compare performance of high vs low ability groups
        sorted_responses = sorted(responses, key=lambda r: r.ability_before)
        
        # Top and bottom 27%
        cutoff = int(len(sorted_responses) * 0.27)
        if cutoff > 0:
            low_group = sorted_responses[:cutoff]
            high_group = sorted_responses[-cutoff:]
            
            low_correct = sum(1 for r in low_group if r.is_correct) / len(low_group)
            high_correct = sum(1 for r in high_group if r.is_correct) / len(high_group)
            
            discrimination_index = high_correct - low_correct
        else:
            discrimination_index = 0
        
        return {
            'usage_count': question.usage_count,
            'correct_rate': question.correct_count / question.usage_count if question.usage_count > 0 else 0,
            'average_response_time': question.average_response_time,
            'exposure_rate': question.exposure_rate,
            'discrimination_index': discrimination_index,
            'irt_parameters': {
                'difficulty': question.difficulty,
                'discrimination': question.discrimination,
                'guessing': question.guessing
            },
            'information_curve': [
                {
                    'ability': ability,
                    'information': question.calculate_information(ability)
                }
                for ability in [-3, -2, -1, 0, 1, 2, 3]
            ]
        }


class AdaptiveTestIntegrationService:
    """Service for integrating adaptive tests with regular evaluation system."""
    
    @staticmethod
    def create_adaptive_evaluation(
        test_set_id: int,
        pool_id: int,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an evaluation that uses adaptive testing."""
        from app.models import TestSet
        
        test_set = TestSet.query.get(test_set_id)
        if not test_set:
            raise ValueError("Test set not found")
        
        # Update test set to indicate adaptive mode
        test_set.metadata = test_set.metadata or {}
        test_set.metadata['adaptive_mode'] = True
        test_set.metadata['adaptive_pool_id'] = pool_id
        test_set.metadata['adaptive_config'] = config or {}
        
        db.session.commit()
        
        return {
            'test_set_id': test_set_id,
            'pool_id': pool_id,
            'adaptive_mode': True,
            'config': config
        }
    
    @staticmethod
    def sync_adaptive_session_to_evaluation(
        adaptive_session_id: int,
        evaluation_id: int
    ) -> bool:
        """Sync adaptive test results to regular evaluation."""
        from app.models import Evaluation
        
        try:
            adaptive_session = AdaptiveTestSession.query.get(adaptive_session_id)
            evaluation = Evaluation.query.get(evaluation_id)
            
            if not adaptive_session or not evaluation:
                return False
            
            # Update evaluation with adaptive test results
            evaluation.score = (adaptive_session.final_ability + 3) / 6 * 100  # Convert to 0-100 scale
            evaluation.responses = evaluation.responses or []
            
            # Convert adaptive responses to regular format
            adaptive_responses = AdaptiveResponse.query.filter_by(
                session_id=adaptive_session_id
            ).all()
            
            for response in adaptive_responses:
                evaluation.responses.append({
                    'question_id': response.question_id,
                    'answer': response.answer,
                    'is_correct': response.is_correct,
                    'response_time': response.response_time,
                    'difficulty': response.question_difficulty
                })
            
            # Add adaptive test metadata
            evaluation.evaluation_metadata = evaluation.evaluation_metadata or {}
            evaluation.evaluation_metadata['adaptive_session_id'] = adaptive_session_id
            evaluation.evaluation_metadata['final_ability'] = adaptive_session.final_ability
            evaluation.evaluation_metadata['ability_se'] = adaptive_session.final_se
            evaluation.evaluation_metadata['confidence_interval'] = [
                adaptive_session.confidence_interval_lower,
                adaptive_session.confidence_interval_upper
            ]
            
            # Get report if available
            report = AdaptiveTestReport.query.filter_by(
                session_id=adaptive_session_id
            ).first()
            
            if report:
                evaluation.strengths = ', '.join(report.topic_strengths) if report.topic_strengths else None
                evaluation.weaknesses = ', '.join(report.topic_weaknesses) if report.topic_weaknesses else None
                evaluation.recommendations = '\n'.join(report.next_steps) if report.next_steps else None
                evaluation.evaluation_metadata['performance_level'] = report.performance_level
                evaluation.evaluation_metadata['ability_percentile'] = report.ability_percentile
            
            evaluation.status = 'completed'
            evaluation.completed_at = adaptive_session.end_time
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise e