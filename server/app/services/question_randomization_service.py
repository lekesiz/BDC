"""
Question Randomization Service

This service provides comprehensive randomization strategies for evaluations
and assessments to prevent cheating while maintaining test fairness.
"""

import random
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set, Any
from enum import Enum
from collections import defaultdict, Counter
import numpy as np

from app.extensions import db
from app.models import (
    Question, TestSession, Response, Beneficiary, 
    AdaptiveQuestion, AdaptiveTestSession
)
from app.utils import cache
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RandomizationStrategy(Enum):
    """Randomization strategies available."""
    SIMPLE_RANDOM = "simple_random"
    STRATIFIED = "stratified"
    DETERMINISTIC = "deterministic"
    ADAPTIVE = "adaptive"
    TEMPLATE_BASED = "template_based"
    BALANCED = "balanced"


class QuestionOrderTemplate(Enum):
    """Pre-defined question order templates."""
    EASY_TO_HARD = "easy_to_hard"
    HARD_TO_EASY = "hard_to_easy"
    MIXED_DIFFICULTY = "mixed_difficulty"
    TOPIC_GROUPED = "topic_grouped"
    ALTERNATING_DIFFICULTY = "alternating_difficulty"
    COGNITIVE_PROGRESSION = "cognitive_progression"  # Remember -> Understand -> Apply -> Analyze


class QuestionRandomizationService:
    """Service for randomizing questions with multiple strategies."""
    
    def __init__(self):
        self.exposure_tracker = QuestionExposureTracker()
        self.history_tracker = QuestionHistoryTracker()
    
    def randomize_questions(
        self,
        questions: List[Question],
        strategy: RandomizationStrategy = RandomizationStrategy.SIMPLE_RANDOM,
        beneficiary_id: Optional[int] = None,
        session_id: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> List[Question]:
        """
        Randomize questions based on selected strategy.
        
        Args:
            questions: List of questions to randomize
            strategy: Randomization strategy to use
            beneficiary_id: ID of the beneficiary (for adaptive/history-based strategies)
            session_id: Session ID for tracking
            config: Additional configuration options
            
        Returns:
            List of randomized questions
        """
        config = config or {}
        
        if strategy == RandomizationStrategy.SIMPLE_RANDOM:
            return self._simple_random_shuffle(questions, config)
        elif strategy == RandomizationStrategy.STRATIFIED:
            return self._stratified_randomization(questions, config)
        elif strategy == RandomizationStrategy.DETERMINISTIC:
            return self._deterministic_randomization(questions, beneficiary_id, session_id, config)
        elif strategy == RandomizationStrategy.ADAPTIVE:
            return self._adaptive_randomization(questions, beneficiary_id, config)
        elif strategy == RandomizationStrategy.TEMPLATE_BASED:
            return self._template_based_randomization(questions, config)
        elif strategy == RandomizationStrategy.BALANCED:
            return self._balanced_randomization(questions, config)
        else:
            logger.warning(f"Unknown randomization strategy: {strategy}. Using simple random.")
            return self._simple_random_shuffle(questions, config)
    
    def _simple_random_shuffle(self, questions: List[Question], config: Dict) -> List[Question]:
        """Simple random shuffle of questions."""
        randomized = questions.copy()
        
        # Handle anchor questions
        anchored = self._extract_anchor_questions(randomized, config)
        
        # Shuffle remaining questions
        random.shuffle(randomized)
        
        # Re-insert anchor questions
        return self._insert_anchor_questions(randomized, anchored, config)
    
    def _stratified_randomization(self, questions: List[Question], config: Dict) -> List[Question]:
        """
        Stratified randomization by difficulty and topic.
        Ensures balanced distribution across strata.
        """
        # Group questions by strata
        strata = defaultdict(list)
        strata_key = config.get('strata_key', 'difficulty')  # Can be 'difficulty', 'topic', or both
        
        for question in questions:
            if strata_key == 'difficulty':
                key = question.difficulty
            elif strata_key == 'topic':
                key = question.category or 'general'
            else:  # both
                key = (question.difficulty, question.category or 'general')
            strata[key].append(question)
        
        # Shuffle within each stratum
        for key in strata:
            random.shuffle(strata[key])
        
        # Interleave strata for balanced distribution
        result = []
        max_items = max(len(items) for items in strata.values())
        
        for i in range(max_items):
            for key in sorted(strata.keys()):  # Sort for consistency
                if i < len(strata[key]):
                    result.append(strata[key][i])
        
        # Handle anchor questions
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def _deterministic_randomization(
        self, 
        questions: List[Question], 
        beneficiary_id: Optional[int],
        session_id: Optional[int],
        config: Dict
    ) -> List[Question]:
        """
        Deterministic pseudo-random ordering for reproducibility.
        Uses a seed based on various factors.
        """
        # Generate seed based on multiple factors
        seed_components = [
            str(beneficiary_id or 0),
            str(session_id or 0),
            config.get('test_id', '0'),
            config.get('attempt_number', '1')
        ]
        
        # Add time-based component if configured
        if config.get('time_based_seed', False):
            time_window = config.get('time_window', 'daily')
            if time_window == 'daily':
                seed_components.append(datetime.now().strftime('%Y-%m-%d'))
            elif time_window == 'weekly':
                seed_components.append(datetime.now().strftime('%Y-%W'))
            elif time_window == 'monthly':
                seed_components.append(datetime.now().strftime('%Y-%m'))
        
        # Create deterministic seed
        seed_string = '-'.join(seed_components)
        seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
        
        # Use seed for randomization
        rng = random.Random(seed)
        randomized = questions.copy()
        
        # Handle anchor questions
        anchored = self._extract_anchor_questions(randomized, config)
        
        # Shuffle with deterministic seed
        rng.shuffle(randomized)
        
        return self._insert_anchor_questions(randomized, anchored, config)
    
    def _adaptive_randomization(
        self, 
        questions: List[Question], 
        beneficiary_id: Optional[int],
        config: Dict
    ) -> List[Question]:
        """
        Adaptive randomization based on user history and performance.
        Prioritizes questions the user hasn't seen or struggled with.
        """
        if not beneficiary_id:
            logger.warning("Adaptive randomization requires beneficiary_id. Falling back to simple random.")
            return self._simple_random_shuffle(questions, config)
        
        # Get user history
        history = self.history_tracker.get_user_history(beneficiary_id)
        
        # Score questions based on multiple factors
        scored_questions = []
        for question in questions:
            score = self._calculate_adaptive_score(question, history, config)
            scored_questions.append((score, question))
        
        # Sort by score (higher score = higher priority)
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        
        # Add some randomness to prevent predictability
        randomness_factor = config.get('randomness_factor', 0.2)
        if randomness_factor > 0:
            # Shuffle within score brackets
            brackets = self._create_score_brackets(scored_questions, num_brackets=5)
            result = []
            for bracket in brackets:
                random.shuffle(bracket)
                result.extend(bracket)
            randomized = [q for _, q in result]
        else:
            randomized = [q for _, q in scored_questions]
        
        # Handle anchor questions
        anchored = self._extract_anchor_questions(randomized, config)
        return self._insert_anchor_questions(randomized, anchored, config)
    
    def _template_based_randomization(self, questions: List[Question], config: Dict) -> List[Question]:
        """Apply pre-defined ordering templates."""
        template = config.get('template', QuestionOrderTemplate.MIXED_DIFFICULTY)
        
        if isinstance(template, str):
            try:
                template = QuestionOrderTemplate(template)
            except ValueError:
                logger.warning(f"Invalid template: {template}. Using MIXED_DIFFICULTY.")
                template = QuestionOrderTemplate.MIXED_DIFFICULTY
        
        if template == QuestionOrderTemplate.EASY_TO_HARD:
            return self._order_by_difficulty(questions, ascending=True, config=config)
        elif template == QuestionOrderTemplate.HARD_TO_EASY:
            return self._order_by_difficulty(questions, ascending=False, config=config)
        elif template == QuestionOrderTemplate.MIXED_DIFFICULTY:
            return self._mixed_difficulty_order(questions, config)
        elif template == QuestionOrderTemplate.TOPIC_GROUPED:
            return self._topic_grouped_order(questions, config)
        elif template == QuestionOrderTemplate.ALTERNATING_DIFFICULTY:
            return self._alternating_difficulty_order(questions, config)
        elif template == QuestionOrderTemplate.COGNITIVE_PROGRESSION:
            return self._cognitive_progression_order(questions, config)
        else:
            return self._simple_random_shuffle(questions, config)
    
    def _balanced_randomization(self, questions: List[Question], config: Dict) -> List[Question]:
        """
        Ensure balanced distribution of question characteristics.
        Considers difficulty, topics, and question types.
        """
        # Analyze question distribution
        difficulty_groups = defaultdict(list)
        topic_groups = defaultdict(list)
        type_groups = defaultdict(list)
        
        for q in questions:
            difficulty_groups[q.difficulty].append(q)
            topic_groups[q.category or 'general'].append(q)
            type_groups[q.type].append(q)
        
        # Shuffle within each group
        for group in [difficulty_groups, topic_groups, type_groups]:
            for items in group.values():
                random.shuffle(items)
        
        # Create balanced sequence
        result = []
        used_ids = set()
        
        # Ensure each segment has variety
        segment_size = max(3, len(questions) // 10)  # At least 3 questions per segment
        num_segments = (len(questions) + segment_size - 1) // segment_size
        
        for segment in range(num_segments):
            segment_questions = []
            
            # Try to add one of each difficulty to the segment
            for difficulty in ['easy', 'medium', 'hard']:
                candidates = [q for q in difficulty_groups[difficulty] if q.id not in used_ids]
                if candidates and len(segment_questions) < segment_size:
                    selected = candidates[0]
                    segment_questions.append(selected)
                    used_ids.add(selected.id)
            
            # Fill remaining slots with diverse topics
            while len(segment_questions) < segment_size and len(used_ids) < len(questions):
                # Find least represented topic in this segment
                segment_topics = Counter(q.category or 'general' for q in segment_questions)
                all_topics = list(topic_groups.keys())
                
                # Sort topics by representation (least first)
                all_topics.sort(key=lambda t: segment_topics.get(t, 0))
                
                for topic in all_topics:
                    candidates = [q for q in topic_groups[topic] if q.id not in used_ids]
                    if candidates:
                        selected = candidates[0]
                        segment_questions.append(selected)
                        used_ids.add(selected.id)
                        break
            
            # Shuffle within segment for unpredictability
            random.shuffle(segment_questions)
            result.extend(segment_questions)
        
        # Handle anchor questions
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def randomize_multiple_choice_answers(
        self, 
        question: Question, 
        preserve_position: Optional[List[int]] = None,
        avoid_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Randomize multiple choice answer options.
        
        Args:
            question: The question with options to randomize
            preserve_position: List of option indices to keep in place
            avoid_patterns: Whether to avoid common patterns (e.g., all A's)
            
        Returns:
            Dictionary with randomized options and mapping
        """
        if not question.options or question.type != 'multiple_choice':
            return {'options': question.options, 'mapping': {}}
        
        options = question.options.copy()
        original_indices = list(range(len(options)))
        preserve_position = preserve_position or []
        
        # Extract options to shuffle
        fixed_options = [(i, opt) for i, opt in enumerate(options) if i in preserve_position]
        shuffle_options = [(i, opt) for i, opt in enumerate(options) if i not in preserve_position]
        
        # Shuffle the shuffleable options
        random.shuffle(shuffle_options)
        
        # Reconstruct the options list
        result_options = [None] * len(options)
        mapping = {}
        
        # Place fixed options
        for orig_idx, opt in fixed_options:
            result_options[orig_idx] = opt
            mapping[orig_idx] = orig_idx
        
        # Place shuffled options in remaining slots
        shuffle_idx = 0
        for i in range(len(result_options)):
            if result_options[i] is None:
                orig_idx, opt = shuffle_options[shuffle_idx]
                result_options[i] = opt
                mapping[orig_idx] = i
                shuffle_idx += 1
        
        # Check for patterns if enabled
        if avoid_patterns and self._has_answer_pattern(result_options, question.correct_answer):
            # Re-shuffle if pattern detected
            return self.randomize_multiple_choice_answers(question, preserve_position, avoid_patterns)
        
        return {
            'options': result_options,
            'mapping': mapping,
            'correct_answer_index': mapping.get(question.correct_answer) if isinstance(question.correct_answer, int) else None
        }
    
    def prevent_question_repetition(
        self,
        questions: List[Question],
        beneficiary_id: int,
        lookback_sessions: int = 3,
        min_gap_between_exposure: int = 5
    ) -> List[Question]:
        """
        Filter questions to prevent repetition across recent sessions.
        
        Args:
            questions: Available questions
            beneficiary_id: Beneficiary ID
            lookback_sessions: Number of recent sessions to check
            min_gap_between_exposure: Minimum number of other questions between repeats
            
        Returns:
            Filtered list of questions
        """
        # Get recent question exposure
        recent_questions = self.history_tracker.get_recent_questions(
            beneficiary_id, 
            lookback_sessions
        )
        
        # Calculate exposure scores
        exposure_scores = {}
        for q in questions:
            exposure = recent_questions.get(q.id, {'count': 0, 'last_seen': None})
            
            # Higher score = less recently seen
            if exposure['count'] == 0:
                score = 1000  # Never seen
            elif exposure['last_seen']:
                days_ago = (datetime.utcnow() - exposure['last_seen']).days
                score = days_ago / (exposure['count'] + 1)
            else:
                score = 100 / (exposure['count'] + 1)
            
            exposure_scores[q.id] = score
        
        # Filter based on minimum gap
        filtered = []
        recent_window = set()
        
        for q in sorted(questions, key=lambda x: exposure_scores[x.id], reverse=True):
            if q.id not in recent_window or exposure_scores[q.id] > 50:
                filtered.append(q)
                recent_window.add(q.id)
                
                # Maintain window size
                if len(recent_window) > min_gap_between_exposure:
                    recent_window.pop()
        
        # Ensure minimum questions
        if len(filtered) < len(questions) * 0.5:  # If we filtered out too many
            # Add back some questions with lowest exposure
            remaining = [q for q in questions if q not in filtered]
            remaining.sort(key=lambda x: exposure_scores[x.id], reverse=True)
            filtered.extend(remaining[:int(len(questions) * 0.5) - len(filtered)])
        
        return filtered
    
    def apply_time_based_seed(
        self,
        window: str = 'daily',
        offset_hours: int = 0
    ) -> str:
        """
        Generate time-based randomization seed.
        
        Args:
            window: Time window ('daily', 'weekly', 'monthly')
            offset_hours: Hours to offset (for timezone adjustment)
            
        Returns:
            Time-based seed string
        """
        now = datetime.utcnow() + timedelta(hours=offset_hours)
        
        if window == 'daily':
            return now.strftime('%Y-%m-%d')
        elif window == 'weekly':
            return now.strftime('%Y-W%W')
        elif window == 'monthly':
            return now.strftime('%Y-%m')
        elif window == 'hourly':
            return now.strftime('%Y-%m-%d-%H')
        else:
            return now.strftime('%Y-%m-%d')
    
    def track_question_exposure(
        self,
        question_id: int,
        beneficiary_id: int,
        session_id: int
    ):
        """Track that a question was shown to a user."""
        self.exposure_tracker.record_exposure(question_id, beneficiary_id, session_id)
        self.history_tracker.record_question_shown(question_id, beneficiary_id, session_id)
    
    def get_exposure_rates(self, question_ids: List[int]) -> Dict[int, float]:
        """Get exposure rates for questions."""
        return self.exposure_tracker.get_exposure_rates(question_ids)
    
    def apply_question_blocking(
        self,
        questions: List[Question],
        blocking_rules: List[Dict[str, Any]]
    ) -> List[Question]:
        """
        Apply question blocking rules (keep together/apart).
        
        Args:
            questions: List of questions
            blocking_rules: List of blocking rules
                - type: 'together' or 'apart'
                - question_ids: List of question IDs
                - min_distance: Minimum distance for 'apart' rules
                
        Returns:
            Reordered questions following blocking rules
        """
        result = questions.copy()
        
        for rule in blocking_rules:
            rule_type = rule.get('type')
            question_ids = set(rule.get('question_ids', []))
            
            if rule_type == 'together':
                # Extract questions that should be together
                together = [q for q in result if q.id in question_ids]
                others = [q for q in result if q.id not in question_ids]
                
                if together:
                    # Insert as a block at a random position
                    insert_pos = random.randint(0, len(others))
                    result = others[:insert_pos] + together + others[insert_pos:]
                    
            elif rule_type == 'apart':
                min_distance = rule.get('min_distance', 3)
                
                # Ensure questions are separated by minimum distance
                positions = {}
                for i, q in enumerate(result):
                    if q.id in question_ids:
                        positions[q.id] = i
                
                # Check and adjust positions
                for q_id in sorted(positions.keys()):
                    current_pos = positions[q_id]
                    
                    # Check distance to other blocked questions
                    for other_id in positions:
                        if other_id != q_id:
                            other_pos = positions[other_id]
                            if abs(current_pos - other_pos) < min_distance:
                                # Need to move this question
                                new_pos = self._find_valid_position(
                                    result, positions, q_id, min_distance
                                )
                                if new_pos is not None and new_pos != current_pos:
                                    # Move the question
                                    q = result.pop(current_pos)
                                    result.insert(new_pos, q)
                                    # Update positions
                                    positions = {q.id: i for i, q in enumerate(result) if q.id in question_ids}
        
        return result
    
    # Helper methods
    
    def _extract_anchor_questions(
        self, 
        questions: List[Question], 
        config: Dict
    ) -> List[Tuple[int, Question]]:
        """Extract questions that should appear at fixed positions."""
        anchors = []
        anchor_positions = config.get('anchor_positions', {})
        
        remaining = []
        for q in questions:
            if str(q.id) in anchor_positions:
                position = anchor_positions[str(q.id)]
                anchors.append((position, q))
            else:
                remaining.append(q)
        
        questions.clear()
        questions.extend(remaining)
        
        return anchors
    
    def _insert_anchor_questions(
        self,
        questions: List[Question],
        anchors: List[Tuple[int, Question]],
        config: Dict
    ) -> List[Question]:
        """Insert anchor questions at their designated positions."""
        if not anchors:
            return questions
        
        result = questions.copy()
        
        # Sort anchors by position
        anchors.sort(key=lambda x: x[0])
        
        for position, question in anchors:
            # Adjust position if needed
            actual_pos = min(position, len(result))
            result.insert(actual_pos, question)
        
        return result
    
    def _calculate_adaptive_score(
        self,
        question: Question,
        history: Dict,
        config: Dict
    ) -> float:
        """Calculate adaptive score for a question based on user history."""
        score = 100.0
        
        # Exposure penalty
        exposure_count = history.get('exposures', {}).get(question.id, 0)
        score -= exposure_count * 20
        
        # Time since last seen bonus
        last_seen = history.get('last_seen', {}).get(question.id)
        if last_seen:
            days_ago = (datetime.utcnow() - last_seen).days
            score += min(days_ago * 2, 50)  # Cap at 50 points
        
        # Performance-based adjustment
        performance = history.get('performance', {}).get(question.id, {})
        if performance:
            # Prioritize questions user struggled with
            accuracy = performance.get('accuracy', 1.0)
            score += (1 - accuracy) * 30
        
        # Topic balance
        topic_exposure = history.get('topic_exposure', {}).get(question.category, 0)
        avg_topic_exposure = sum(history.get('topic_exposure', {}).values()) / max(len(history.get('topic_exposure', {})), 1)
        if topic_exposure < avg_topic_exposure:
            score += 20  # Bonus for underexposed topics
        
        return max(score, 0)
    
    def _create_score_brackets(
        self,
        scored_items: List[Tuple[float, Any]],
        num_brackets: int = 5
    ) -> List[List[Tuple[float, Any]]]:
        """Create score brackets for randomization within tiers."""
        if not scored_items:
            return []
        
        # Sort by score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Create equal-sized brackets
        bracket_size = max(1, len(scored_items) // num_brackets)
        brackets = []
        
        for i in range(0, len(scored_items), bracket_size):
            brackets.append(scored_items[i:i + bracket_size])
        
        return brackets
    
    def _order_by_difficulty(
        self,
        questions: List[Question],
        ascending: bool = True,
        config: Dict = None
    ) -> List[Question]:
        """Order questions by difficulty."""
        config = config or {}
        difficulty_order = ['easy', 'medium', 'hard']
        if not ascending:
            difficulty_order.reverse()
        
        # Group by difficulty
        grouped = defaultdict(list)
        for q in questions:
            grouped[q.difficulty].append(q)
        
        # Shuffle within each difficulty level
        for difficulty in grouped:
            random.shuffle(grouped[difficulty])
        
        # Combine in order
        result = []
        for difficulty in difficulty_order:
            result.extend(grouped[difficulty])
        
        # Handle anchors
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def _mixed_difficulty_order(self, questions: List[Question], config: Dict) -> List[Question]:
        """Create a mixed difficulty order with good distribution."""
        # Group by difficulty
        by_difficulty = defaultdict(list)
        for q in questions:
            by_difficulty[q.difficulty].append(q)
        
        # Shuffle each group
        for group in by_difficulty.values():
            random.shuffle(group)
        
        # Interleave difficulties
        result = []
        difficulties = ['easy', 'medium', 'hard']
        
        while any(by_difficulty[d] for d in difficulties):
            for difficulty in difficulties:
                if by_difficulty[difficulty]:
                    result.append(by_difficulty[difficulty].pop(0))
        
        # Handle anchors
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def _topic_grouped_order(self, questions: List[Question], config: Dict) -> List[Question]:
        """Group questions by topic, randomize within groups."""
        # Group by topic
        by_topic = defaultdict(list)
        for q in questions:
            topic = q.category or 'general'
            by_topic[topic].append(q)
        
        # Randomize order of topics
        topics = list(by_topic.keys())
        random.shuffle(topics)
        
        # Build result
        result = []
        for topic in topics:
            topic_questions = by_topic[topic]
            random.shuffle(topic_questions)
            result.extend(topic_questions)
        
        # Handle anchors
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def _alternating_difficulty_order(self, questions: List[Question], config: Dict) -> List[Question]:
        """Alternate between difficulty levels."""
        # Group by difficulty
        by_difficulty = {
            'easy': [q for q in questions if q.difficulty == 'easy'],
            'medium': [q for q in questions if q.difficulty == 'medium'],
            'hard': [q for q in questions if q.difficulty == 'hard']
        }
        
        # Shuffle each group
        for group in by_difficulty.values():
            random.shuffle(group)
        
        # Create alternating pattern
        result = []
        pattern = ['easy', 'medium', 'hard', 'medium']  # Alternating pattern
        pattern_idx = 0
        
        while any(by_difficulty[d] for d in by_difficulty):
            # Find next non-empty difficulty in pattern
            attempts = 0
            while attempts < len(pattern):
                difficulty = pattern[pattern_idx % len(pattern)]
                if by_difficulty[difficulty]:
                    result.append(by_difficulty[difficulty].pop(0))
                    break
                pattern_idx += 1
                attempts += 1
            else:
                # Pattern exhausted, add remaining questions
                for difficulty in ['easy', 'medium', 'hard']:
                    if by_difficulty[difficulty]:
                        result.append(by_difficulty[difficulty].pop(0))
                        break
            
            pattern_idx += 1
        
        # Handle anchors
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def _cognitive_progression_order(self, questions: List[Question], config: Dict) -> List[Question]:
        """Order by cognitive level progression (Bloom's taxonomy)."""
        # Map questions to cognitive levels (if available)
        cognitive_order = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
        
        by_cognitive = defaultdict(list)
        for q in questions:
            level = getattr(q, 'cognitive_level', None) or 'apply'  # Default to 'apply'
            by_cognitive[level].append(q)
        
        # Shuffle within each level
        for group in by_cognitive.values():
            random.shuffle(group)
        
        # Build result in cognitive order
        result = []
        for level in cognitive_order:
            result.extend(by_cognitive[level])
        
        # Handle anchors
        anchored = self._extract_anchor_questions(result, config)
        return self._insert_anchor_questions(result, anchored, config)
    
    def _has_answer_pattern(self, options: List[Any], correct_answer: Any) -> bool:
        """Check if answer arrangement has obvious patterns."""
        if not options or len(options) < 4:
            return False
        
        # Check for all answers being the same position
        # This would be checked across multiple questions in practice
        # For now, just ensure some randomness
        
        return False  # Simplified for now
    
    def _find_valid_position(
        self,
        questions: List[Question],
        blocked_positions: Dict[int, int],
        question_id: int,
        min_distance: int
    ) -> Optional[int]:
        """Find a valid position for a question given blocking constraints."""
        current_pos = blocked_positions[question_id]
        valid_positions = []
        
        for i in range(len(questions)):
            is_valid = True
            
            # Check distance to all other blocked questions
            for other_id, other_pos in blocked_positions.items():
                if other_id != question_id and abs(i - other_pos) < min_distance:
                    is_valid = False
                    break
            
            if is_valid:
                valid_positions.append(i)
        
        if not valid_positions:
            return None
        
        # Choose position closest to current
        valid_positions.sort(key=lambda x: abs(x - current_pos))
        return valid_positions[0]


class QuestionExposureTracker:
    """Track question exposure rates."""
    
    def __init__(self):
        self.cache_key_prefix = "question_exposure"
    
    def record_exposure(self, question_id: int, beneficiary_id: int, session_id: int):
        """Record that a question was shown."""
        key = f"{self.cache_key_prefix}:{question_id}"
        current = cache.get(key) or {'total': 0, 'unique_users': set(), 'sessions': []}
        
        current['total'] += 1
        current['unique_users'].add(beneficiary_id)
        current['sessions'].append({
            'session_id': session_id,
            'beneficiary_id': beneficiary_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only recent sessions (last 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        current['sessions'] = [
            s for s in current['sessions'][-1000:]  # Keep max 1000 recent sessions
            if datetime.fromisoformat(s['timestamp']) > cutoff
        ]
        
        # Convert set to list for caching
        current['unique_users'] = list(current['unique_users'])
        
        cache.set(key, current, timeout=86400 * 30)  # 30 days
    
    def get_exposure_rates(self, question_ids: List[int]) -> Dict[int, float]:
        """Get exposure rates for questions."""
        rates = {}
        
        # Get total sessions in period
        total_sessions_key = f"{self.cache_key_prefix}:total_sessions"
        total_sessions = cache.get(total_sessions_key) or 1
        
        for q_id in question_ids:
            key = f"{self.cache_key_prefix}:{q_id}"
            data = cache.get(key)
            
            if data:
                rates[q_id] = data['total'] / total_sessions
            else:
                rates[q_id] = 0.0
        
        return rates


class QuestionHistoryTracker:
    """Track user question history."""
    
    def __init__(self):
        self.cache_key_prefix = "question_history"
    
    def record_question_shown(self, question_id: int, beneficiary_id: int, session_id: int):
        """Record that a question was shown to a user."""
        key = f"{self.cache_key_prefix}:{beneficiary_id}"
        history = cache.get(key) or {
            'exposures': {},
            'last_seen': {},
            'performance': {},
            'topic_exposure': {}
        }
        
        # Update exposures
        history['exposures'][question_id] = history['exposures'].get(question_id, 0) + 1
        
        # Update last seen
        history['last_seen'][question_id] = datetime.utcnow()
        
        # Note: Performance would be updated when answer is submitted
        
        cache.set(key, history, timeout=86400 * 90)  # 90 days
    
    def get_user_history(self, beneficiary_id: int) -> Dict:
        """Get user's question history."""
        key = f"{self.cache_key_prefix}:{beneficiary_id}"
        return cache.get(key) or {
            'exposures': {},
            'last_seen': {},
            'performance': {},
            'topic_exposure': {}
        }
    
    def get_recent_questions(
        self,
        beneficiary_id: int,
        lookback_sessions: int = 3
    ) -> Dict[int, Dict]:
        """Get recently shown questions for a user."""
        # Query recent test sessions
        recent_sessions = TestSession.query.filter_by(
            beneficiary_id=beneficiary_id,
            status='completed'
        ).order_by(TestSession.created_at.desc()).limit(lookback_sessions).all()
        
        recent_questions = {}
        
        for session in recent_sessions:
            responses = Response.query.filter_by(session_id=session.id).all()
            
            for response in responses:
                q_id = response.question_id
                if q_id not in recent_questions:
                    recent_questions[q_id] = {
                        'count': 0,
                        'last_seen': response.created_at
                    }
                recent_questions[q_id]['count'] += 1
                
                # Keep most recent timestamp
                if response.created_at > recent_questions[q_id]['last_seen']:
                    recent_questions[q_id]['last_seen'] = response.created_at
        
        return recent_questions
    
    def update_performance(
        self,
        beneficiary_id: int,
        question_id: int,
        is_correct: bool,
        response_time: float
    ):
        """Update performance data for a question."""
        key = f"{self.cache_key_prefix}:{beneficiary_id}"
        history = cache.get(key) or {
            'exposures': {},
            'last_seen': {},
            'performance': {},
            'topic_exposure': {}
        }
        
        # Update performance
        if question_id not in history['performance']:
            history['performance'][question_id] = {
                'attempts': 0,
                'correct': 0,
                'total_time': 0,
                'accuracy': 0.0
            }
        
        perf = history['performance'][question_id]
        perf['attempts'] += 1
        if is_correct:
            perf['correct'] += 1
        perf['total_time'] += response_time
        perf['accuracy'] = perf['correct'] / perf['attempts']
        
        cache.set(key, history, timeout=86400 * 90)  # 90 days


# Create service instance
question_randomization_service = QuestionRandomizationService()