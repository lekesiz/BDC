"""
Question Randomization Service - Usage Examples

This file provides comprehensive examples of how to use the Question Randomization Service
with different strategies and configurations to prevent cheating while maintaining fairness.
"""

from app.services.question_randomization_service import (

from app.utils.logging import logger
    question_randomization_service,
    RandomizationStrategy,
    QuestionOrderTemplate
)


# Example 1: Simple Random Shuffle
def example_simple_random():
    """
    Basic randomization - randomly shuffle all questions.
    Good for: Quick assessments, low-stakes testing
    """
    config = {
        'strategy': RandomizationStrategy.SIMPLE_RANDOM,
        'anchor_positions': {
            '1': 0,  # Always start with question 1 (instructions)
            '50': -1  # Always end with question 50 (feedback form)
        }
    }
    return config


# Example 2: Stratified Randomization by Difficulty
def example_stratified_difficulty():
    """
    Balanced randomization ensuring equal distribution of difficulty levels.
    Good for: Standardized tests, formal assessments
    """
    config = {
        'strategy': RandomizationStrategy.STRATIFIED,
        'strata_key': 'difficulty',  # Group by difficulty
        'ensure_balance': True,      # Maintain balance across strata
        'blocking_rules': [
            {
                'type': 'together',
                'question_ids': [15, 16, 17],  # Reading comprehension passage
                'description': 'Keep passage questions together'
            }
        ]
    }
    return config


# Example 3: Topic-Based Stratified Randomization
def example_stratified_topic():
    """
    Randomization that ensures balanced topic coverage.
    Good for: Comprehensive exams, multi-domain assessments
    """
    config = {
        'strategy': RandomizationStrategy.STRATIFIED,
        'strata_key': 'topic',
        'topic_balance_weight': 0.8,  # 80% weight on topic balance
        'min_topic_gap': 2,           # At least 2 questions between same topic
        'anchor_positions': {
            '1': 0,    # Introduction question
            '25': 12,  # Mid-test checkpoint
            '50': -1   # Conclusion question
        }
    }
    return config


# Example 4: Deterministic Pseudo-Random
def example_deterministic():
    """
    Reproducible randomization for parallel test forms.
    Good for: Multiple test sessions, makeup exams, research studies
    """
    config = {
        'strategy': RandomizationStrategy.DETERMINISTIC,
        'time_based_seed': True,
        'time_window': 'daily',       # Same order for same day
        'include_attempt_number': True,
        'include_user_id': True,
        'salt': 'assessment_2024',    # Additional randomness component
        'blocking_rules': [
            {
                'type': 'apart',
                'question_ids': [10, 20, 30],  # Similar questions
                'min_distance': 5,
                'description': 'Keep similar questions apart'
            }
        ]
    }
    return config


# Example 5: Adaptive Randomization
def example_adaptive():
    """
    Personalized randomization based on user history and performance.
    Good for: Personalized learning, adaptive testing, remediation
    """
    config = {
        'strategy': RandomizationStrategy.ADAPTIVE,
        'prioritize_weak_areas': True,
        'exposure_penalty_weight': 0.3,    # Reduce score for overexposed questions
        'performance_weight': 0.4,         # Higher weight for poor performance
        'time_since_seen_weight': 0.3,     # Boost questions not seen recently
        'randomness_factor': 0.2,          # 20% randomness to prevent predictability
        'lookback_sessions': 5,             # Consider last 5 sessions
        'min_gap_between_exposure': 3,     # Minimum questions between repeats
        'topic_balancing': True,
        'prevent_repetition': True
    }
    return config


# Example 6: Template-Based Easy to Hard
def example_easy_to_hard():
    """
    Progressive difficulty ordering with randomization within levels.
    Good for: Building confidence, learning assessments, skill progression
    """
    config = {
        'strategy': RandomizationStrategy.TEMPLATE_BASED,
        'template': QuestionOrderTemplate.EASY_TO_HARD,
        'randomize_within_levels': True,   # Randomize within each difficulty level
        'transition_questions': [15, 30], # Mark difficulty transitions
        'warm_up_questions': 3,           # Easy questions at start
        'anchor_positions': {
            '1': 0,   # Warm-up question
            '45': -5, # Pre-conclusion question
            '50': -1  # Final question
        }
    }
    return config


# Example 7: Topic-Grouped Template
def example_topic_grouped():
    """
    Group questions by topic with randomization within groups.
    Good for: Subject-area tests, learning modules, topic mastery
    """
    config = {
        'strategy': RandomizationStrategy.TEMPLATE_BASED,
        'template': QuestionOrderTemplate.TOPIC_GROUPED,
        'topic_order': ['basics', 'intermediate', 'advanced'],  # Preferred topic order
        'randomize_topic_order': False,   # Keep topic order fixed
        'randomize_within_topics': True,  # Randomize within each topic
        'topic_transition_markers': True, # Add markers between topics
        'min_questions_per_topic': 3,    # Minimum questions per topic
        'max_questions_per_topic': 10    # Maximum questions per topic
    }
    return config


# Example 8: Balanced Distribution
def example_balanced():
    """
    Comprehensive balancing of all question characteristics.
    Good for: High-stakes testing, certification exams, research studies
    """
    config = {
        'strategy': RandomizationStrategy.BALANCED,
        'balance_factors': ['difficulty', 'topic', 'question_type', 'cognitive_level'],
        'segment_size': 5,                # Balance within every 5 questions
        'global_balance_weight': 0.7,     # 70% weight on global balance
        'local_balance_weight': 0.3,      # 30% weight on local balance
        'avoid_patterns': True,           # Prevent AAAA, BBBB patterns
        'ensure_variety': True,           # Ensure variety in each segment
        'blocking_rules': [
            {
                'type': 'together',
                'question_ids': [8, 9, 10],  # Case study questions
            },
            {
                'type': 'apart',
                'question_ids': [15, 25, 35], # Similar format questions
                'min_distance': 4
            }
        ]
    }
    return config


# Example 9: Answer Randomization Configuration
def example_answer_randomization():
    """
    Configuration for randomizing multiple choice answer options.
    """
    config = {
        'enable_answer_randomization': True,
        'preserve_answer_positions': [0],      # Always keep A in first position
        'avoid_patterns': True,               # Prevent obvious patterns
        'maintain_logical_order': False,      # Don't maintain "All of the above" at end
        'consistent_across_sessions': True,   # Same randomization per user session
        'pattern_detection': True,           # Detect and avoid answer patterns
        'balanced_distribution': True        # Ensure even distribution of correct answers
    }
    return config


# Example 10: High-Security Configuration
def example_high_security():
    """
    Maximum security configuration for high-stakes testing.
    Good for: Certification exams, entrance tests, professional licensing
    """
    config = {
        'strategy': RandomizationStrategy.BALANCED,
        'enable_answer_randomization': True,
        'time_based_seed': True,
        'time_window': 'hourly',              # Change every hour
        'prevent_repetition': True,
        'lookback_sessions': 10,              # Long lookback period
        'min_gap_between_exposure': 8,        # Large gap between repeats
        'exposure_tracking': True,
        'max_exposure_rate': 0.15,           # Max 15% exposure rate per question
        'session_uniqueness': 0.8,          # 80% unique questions per session
        'pattern_avoidance': True,
        'cheating_detection': True,
        'blocking_rules': [
            {
                'type': 'apart',
                'question_ids': 'all_similar_format',  # Keep similar questions apart
                'min_distance': 6
            }
        ],
        'anchor_positions': {
            '1': 0,     # Security notice
            '100': -1   # Exit survey
        },
        'quality_control': {
            'min_difficulty_distribution': 0.15,  # At least 15% of each difficulty
            'max_topic_clustering': 3,            # Max 3 consecutive same-topic questions
            'balance_check_frequency': 10         # Check balance every 10 questions
        }
    }
    return config


# Example Usage Functions

def create_basic_assessment_config():
    """Create configuration for a basic classroom assessment."""
    return {
        'randomization_enabled': True,
        'randomization_strategy': 'stratified',
        'randomization_config': example_stratified_difficulty(),
        'answer_randomization': True,
        'time_based_seed': False,
        'blocking_rules': []
    }


def create_adaptive_learning_config():
    """Create configuration for adaptive learning system."""
    return {
        'randomization_enabled': True,
        'randomization_strategy': 'adaptive',
        'randomization_config': example_adaptive(),
        'answer_randomization': True,
        'time_based_seed': False,
        'blocking_rules': [
            {
                'type': 'apart',
                'question_ids': 'prerequisite_check',
                'min_distance': 5
            }
        ]
    }


def create_certification_exam_config():
    """Create configuration for high-stakes certification exam."""
    return {
        'randomization_enabled': True,
        'randomization_strategy': 'balanced',
        'randomization_config': example_high_security(),
        'answer_randomization': True,
        'time_based_seed': True,
        'blocking_rules': [
            {
                'type': 'together',
                'question_ids': 'case_study_group_1'
            },
            {
                'type': 'apart',
                'question_ids': 'format_similar_questions',
                'min_distance': 6
            }
        ]
    }


# Integration Example

def apply_randomization_to_test_session(test_set, beneficiary_id, session_id):
    """
    Example of how to apply randomization to a test session.
    
    Args:
        test_set: TestSet model instance
        beneficiary_id: ID of the beneficiary taking the test
        session_id: Test session ID
        
    Returns:
        Tuple of (randomized_questions, answer_mappings)
    """
    # Get questions for the test set
    from app.models import Question
    questions = Question.query.filter_by(test_set_id=test_set.id).all()
    
    if not questions:
        return [], {}
    
    # Get strategy from test set configuration
    try:
        strategy = RandomizationStrategy(test_set.randomization_strategy)
    except (ValueError, AttributeError):
        strategy = RandomizationStrategy.SIMPLE_RANDOM
    
    # Prepare configuration
    config = test_set.randomization_config or {}
    
    # Add test set specific settings
    if test_set.anchor_questions:
        config['anchor_positions'] = test_set.anchor_questions
    
    if test_set.blocking_rules:
        config['blocking_rules'] = test_set.blocking_rules
    
    if test_set.question_order_template:
        config['template'] = test_set.question_order_template
    
    # Apply repetition prevention if enabled
    if config.get('prevent_repetition', True):
        questions = question_randomization_service.prevent_question_repetition(
            questions,
            beneficiary_id,
            config.get('lookback_sessions', 3),
            config.get('min_gap_between_exposure', 5)
        )
    
    # Randomize questions
    randomized_questions = question_randomization_service.randomize_questions(
        questions,
        strategy,
        beneficiary_id,
        session_id,
        config
    )
    
    # Handle answer randomization
    answer_mappings = {}
    if test_set.answer_randomization:
        for question in randomized_questions:
            if question.type == 'multiple_choice' and question.options:
                result = question_randomization_service.randomize_multiple_choice_answers(
                    question,
                    preserve_position=config.get('preserve_answer_positions', []),
                    avoid_patterns=config.get('avoid_patterns', True)
                )
                answer_mappings[question.id] = result['mapping']
    
    # Track exposure
    for question in randomized_questions:
        question_randomization_service.track_question_exposure(
            question.id,
            beneficiary_id,
            session_id
        )
    
    return randomized_questions, answer_mappings


# Best Practices Documentation

BEST_PRACTICES = {
    'security': [
        "Use deterministic randomization with time-based seeds for high-stakes tests",
        "Implement question exposure tracking to prevent overuse",
        "Apply blocking rules to separate similar questions",
        "Use answer randomization for multiple choice questions",
        "Set minimum gaps between question repetitions"
    ],
    
    'fairness': [
        "Ensure balanced difficulty distribution across all test forms",
        "Maintain consistent topic coverage for all students",
        "Use stratified randomization for formal assessments",
        "Anchor important questions (instructions, transitions) at fixed positions",
        "Test randomization configurations before deployment"
    ],
    
    'learning': [
        "Use adaptive randomization for personalized learning paths",
        "Apply easy-to-hard templates for skill building",
        "Group related questions together when appropriate",
        "Consider cognitive load when ordering questions",
        "Provide consistent experiences within user sessions"
    ],
    
    'technical': [
        "Cache randomization results for session consistency",
        "Store question orders and answer mappings for reproducibility",
        "Monitor exposure rates and adjust configurations",
        "Use proper seeding for deterministic results",
        "Implement fallbacks for configuration errors"
    ]
}


if __name__ == '__main__':
    # Example usage
    logger.info("Question Randomization Service Examples")
    logger.info("=====================================")
    
    # Display example configurations
    examples = [
        ("Simple Random", example_simple_random()),
        ("Stratified by Difficulty", example_stratified_difficulty()),
        ("Adaptive Randomization", example_adaptive()),
        ("High Security", example_high_security())
    ]
    
    for name, config in examples:
        logger.info(f"\n{name}:")
        for key, value in config.items():
            logger.info(f"  {key}: {value}")
    
    logger.info("\nBest Practices:")
    for category, practices in BEST_PRACTICES.items():
        logger.info(f"\n{category.title()}:")
        for practice in practices:
            logger.info(f"  - {practice}")