"""Setup utilities for Adaptive Test System."""

from app.models import AdaptiveTestPool, AdaptiveQuestion
from app.services.adaptive_test_service import AdaptiveTestService
from app.extensions import db


def create_sample_adaptive_pool(tenant_id: int):
    """Create a sample adaptive test pool with questions."""
    
    # Create pool
    pool_data = {
        'name': 'Mathematics Adaptive Test Pool',
        'description': 'Adaptive test pool for mathematics assessment covering algebra, geometry, and calculus',
        'subject': 'Mathematics',
        'grade_level': 'High School'
    }
    
    pool = AdaptiveTestService.create_question_pool(tenant_id, pool_data)
    
    # Sample questions with varying difficulty and topics
    sample_questions = [
        # Easy questions (difficulty -2 to -1)
        {
            'text': 'What is 2 + 2?',
            'type': 'multiple_choice',
            'options': {'A': '3', 'B': '4', 'C': '5', 'D': '6'},
            'correct_answer': 'B',
            'explanation': '2 + 2 = 4',
            'difficulty': -2.0,
            'discrimination': 1.2,
            'guessing': 0.25,
            'difficulty_level': 1,
            'topic': 'Arithmetic',
            'subtopic': 'Addition',
            'cognitive_level': 'remember'
        },
        {
            'text': 'What is 5 × 3?',
            'type': 'multiple_choice',
            'options': {'A': '8', 'B': '12', 'C': '15', 'D': '18'},
            'correct_answer': 'C',
            'explanation': '5 × 3 = 15',
            'difficulty': -1.5,
            'discrimination': 1.3,
            'guessing': 0.25,
            'difficulty_level': 2,
            'topic': 'Arithmetic',
            'subtopic': 'Multiplication',
            'cognitive_level': 'remember'
        },
        
        # Medium questions (difficulty -1 to 1)
        {
            'text': 'Solve for x: 2x + 5 = 13',
            'type': 'multiple_choice',
            'options': {'A': '4', 'B': '6', 'C': '8', 'D': '9'},
            'correct_answer': 'A',
            'explanation': '2x + 5 = 13; 2x = 8; x = 4',
            'difficulty': 0.0,
            'discrimination': 1.5,
            'guessing': 0.25,
            'difficulty_level': 5,
            'topic': 'Algebra',
            'subtopic': 'Linear Equations',
            'cognitive_level': 'apply'
        },
        {
            'text': 'What is the area of a rectangle with length 8 and width 5?',
            'type': 'multiple_choice',
            'options': {'A': '13', 'B': '26', 'C': '40', 'D': '80'},
            'correct_answer': 'C',
            'explanation': 'Area = length × width = 8 × 5 = 40',
            'difficulty': -0.5,
            'discrimination': 1.4,
            'guessing': 0.25,
            'difficulty_level': 3,
            'topic': 'Geometry',
            'subtopic': 'Area',
            'cognitive_level': 'apply'
        },
        {
            'text': 'If f(x) = x² + 3x - 2, what is f(2)?',
            'type': 'multiple_choice',
            'options': {'A': '4', 'B': '6', 'C': '8', 'D': '10'},
            'correct_answer': 'C',
            'explanation': 'f(2) = 2² + 3(2) - 2 = 4 + 6 - 2 = 8',
            'difficulty': 0.5,
            'discrimination': 1.6,
            'guessing': 0.25,
            'difficulty_level': 6,
            'topic': 'Algebra',
            'subtopic': 'Functions',
            'cognitive_level': 'apply'
        },
        
        # Hard questions (difficulty 1 to 3)
        {
            'text': 'Find the derivative of f(x) = 3x² - 2x + 5',
            'type': 'multiple_choice',
            'options': {'A': '6x - 2', 'B': '6x + 2', 'C': '3x - 2', 'D': '6x² - 2'},
            'correct_answer': 'A',
            'explanation': "f'(x) = 6x - 2",
            'difficulty': 1.5,
            'discrimination': 1.8,
            'guessing': 0.25,
            'difficulty_level': 8,
            'topic': 'Calculus',
            'subtopic': 'Derivatives',
            'cognitive_level': 'analyze'
        },
        {
            'text': 'What is the limit of (x² - 4)/(x - 2) as x approaches 2?',
            'type': 'multiple_choice',
            'options': {'A': '0', 'B': '2', 'C': '4', 'D': 'undefined'},
            'correct_answer': 'C',
            'explanation': 'Factor: (x² - 4)/(x - 2) = (x + 2)(x - 2)/(x - 2) = x + 2, so limit is 4',
            'difficulty': 2.0,
            'discrimination': 2.0,
            'guessing': 0.25,
            'difficulty_level': 9,
            'topic': 'Calculus',
            'subtopic': 'Limits',
            'cognitive_level': 'analyze'
        },
        
        # True/False questions
        {
            'text': 'The sum of angles in a triangle is always 180 degrees.',
            'type': 'true_false',
            'correct_answer': True,
            'explanation': 'This is a fundamental property of Euclidean geometry.',
            'difficulty': -1.0,
            'discrimination': 1.2,
            'guessing': 0.5,  # Higher guessing for true/false
            'difficulty_level': 3,
            'topic': 'Geometry',
            'subtopic': 'Angles',
            'cognitive_level': 'remember'
        },
        {
            'text': 'All prime numbers are odd.',
            'type': 'true_false',
            'correct_answer': False,
            'explanation': '2 is a prime number and it is even.',
            'difficulty': 0.0,
            'discrimination': 1.5,
            'guessing': 0.5,
            'difficulty_level': 5,
            'topic': 'Number Theory',
            'subtopic': 'Prime Numbers',
            'cognitive_level': 'understand'
        }
    ]
    
    # Add questions to pool
    for question_data in sample_questions:
        AdaptiveTestService.add_question_to_pool(pool.id, question_data)
    
    return pool


def create_advanced_math_pool(tenant_id: int):
    """Create an advanced mathematics adaptive pool."""
    
    pool_data = {
        'name': 'Advanced Mathematics Adaptive Assessment',
        'description': 'Comprehensive adaptive assessment for advanced mathematics topics',
        'subject': 'Advanced Mathematics',
        'grade_level': 'College'
    }
    
    pool = AdaptiveTestService.create_question_pool(tenant_id, pool_data)
    
    # Advanced questions
    advanced_questions = [
        {
            'text': 'Evaluate the integral: ∫(x²sin(x))dx',
            'type': 'multiple_choice',
            'options': {
                'A': '-x²cos(x) + 2xsin(x) + 2cos(x) + C',
                'B': 'x²cos(x) - 2xsin(x) - 2cos(x) + C',
                'C': '-x²cos(x) + 2xsin(x) - 2cos(x) + C',
                'D': 'x²sin(x) + 2xcos(x) + 2sin(x) + C'
            },
            'correct_answer': 'A',
            'explanation': 'Using integration by parts twice',
            'difficulty': 2.5,
            'discrimination': 2.2,
            'guessing': 0.25,
            'difficulty_level': 10,
            'topic': 'Calculus',
            'subtopic': 'Integration by Parts',
            'cognitive_level': 'analyze'
        },
        {
            'text': 'Find the eigenvalues of the matrix [[3, 1], [2, 4]]',
            'type': 'multiple_choice',
            'options': {
                'A': '2 and 5',
                'B': '1 and 6',
                'C': '2 and 4',
                'D': '3 and 4'
            },
            'correct_answer': 'A',
            'explanation': 'Solve det(A - λI) = 0',
            'difficulty': 2.0,
            'discrimination': 1.9,
            'guessing': 0.25,
            'difficulty_level': 9,
            'topic': 'Linear Algebra',
            'subtopic': 'Eigenvalues',
            'cognitive_level': 'apply'
        }
    ]
    
    for question_data in advanced_questions:
        AdaptiveTestService.add_question_to_pool(pool.id, question_data)
    
    return pool


def demo_adaptive_test_session(pool_id: int, beneficiary_id: int):
    """Demonstrate an adaptive test session."""
    
    # Start session with custom configuration
    config = {
        'max_questions': 10,
        'standard_error_threshold': 0.25,
        'initial_ability': 0.0,
        'selection_method': 'maximum_information',
        'topic_balancing': True,
        'exposure_control': True
    }
    
    session = AdaptiveTestService.start_adaptive_session(
        pool_id=pool_id,
        beneficiary_id=beneficiary_id,
        config=config
    )
    
    print(f"Started adaptive session {session.id}")
    print(f"Initial ability: {session.current_ability}")
    
    # Simulate test taking
    question_count = 0
    while session.status == 'in_progress' and question_count < 10:
        # Get next question
        question = AdaptiveTestService.get_next_question(session.id)
        if not question:
            break
        
        question_count += 1
        print(f"\nQuestion {question_count}: {question.text}")
        print(f"Difficulty: {question.difficulty}")
        
        # Simulate answer (for demo purposes)
        # In real scenario, this would come from user input
        if question.type == 'multiple_choice':
            # Simulate answer based on ability vs difficulty
            prob_correct = question.calculate_probability(session.current_ability)
            import random
            is_correct = random.random() < prob_correct
            answer = question.correct_answer if is_correct else 'A'
        elif question.type == 'true_false':
            answer = question.correct_answer
        else:
            answer = 'Sample answer'
        
        # Submit response
        response, new_ability, se = AdaptiveTestService.submit_response(
            session_id=session.id,
            question_id=question.id,
            answer=answer,
            response_time=random.uniform(10, 60)  # Random response time
        )
        
        print(f"Answer correct: {response.is_correct}")
        print(f"New ability: {new_ability:.3f} (SE: {se:.3f})")
        
        # Check if should stop
        session = AdaptiveTestSession.query.get(session.id)
        should_stop, reason = session.should_stop()
        if should_stop:
            print(f"\nStopping: {reason}")
            break
    
    # Complete session
    session = AdaptiveTestService.complete_session(session.id)
    print(f"\nSession completed!")
    print(f"Final ability: {session.final_ability:.3f}")
    print(f"Confidence interval: [{session.confidence_interval_lower:.3f}, {session.confidence_interval_upper:.3f}]")
    
    # Get report
    report = AdaptiveTestService.generate_report(session.id)
    if report:
        print(f"\nPerformance Level: {report.performance_level}")
        print(f"Percentile: {report.ability_percentile:.1f}%")
        if report.topic_strengths:
            print(f"Strengths: {', '.join(report.topic_strengths)}")
        if report.topic_weaknesses:
            print(f"Weaknesses: {', '.join(report.topic_weaknesses)}")
    
    return session, report