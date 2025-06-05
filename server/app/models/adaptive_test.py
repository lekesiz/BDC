"""Adaptive Test models for implementing Computerized Adaptive Testing (CAT) system."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.extensions import db


class AdaptiveTestPool(db.Model):
    """Question pool for adaptive testing with IRT parameters."""
    __tablename__ = 'adaptive_test_pools'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pool configuration
    subject = Column(String(100), nullable=True)
    grade_level = Column(String(50), nullable=True)
    
    # Pool metadata
    total_questions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='adaptive_test_pools')
    questions = relationship('AdaptiveQuestion', back_populates='pool', cascade='all, delete-orphan')
    sessions = relationship('AdaptiveTestSession', back_populates='pool')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_adaptive_pool_tenant', 'tenant_id'),
        Index('idx_adaptive_pool_subject', 'subject'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'subject': self.subject,
            'grade_level': self.grade_level,
            'total_questions': self.total_questions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AdaptiveQuestion(db.Model):
    """Questions with Item Response Theory (IRT) parameters for adaptive testing."""
    __tablename__ = 'adaptive_questions'
    
    id = Column(Integer, primary_key=True)
    pool_id = Column(Integer, ForeignKey('adaptive_test_pools.id'), nullable=False)
    
    # Question content
    text = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # multiple_choice, true_false, etc.
    options = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # IRT parameters (3-parameter logistic model)
    difficulty = Column(Float, nullable=False)  # b parameter (-3 to 3)
    discrimination = Column(Float, nullable=False, default=1.0)  # a parameter (0.1 to 2.5)
    guessing = Column(Float, nullable=False, default=0.0)  # c parameter (0 to 0.3)
    
    # Categorization
    difficulty_level = Column(Integer, nullable=False)  # 1-10 scale
    topic = Column(String(100), nullable=True)
    subtopic = Column(String(100), nullable=True)
    cognitive_level = Column(String(50), nullable=True)  # remember, understand, apply, analyze, evaluate, create
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)  # in seconds
    
    # Quality metrics
    exposure_rate = Column(Float, default=0.0)  # How often this question is shown
    information_value = Column(Float, nullable=True)  # Information function value
    
    # Status
    is_active = Column(Boolean, default=True)
    review_status = Column(String(20), default='approved')  # draft, approved, needs_review
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pool = relationship('AdaptiveTestPool', back_populates='questions')
    responses = relationship('AdaptiveResponse', back_populates='question')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_adaptive_question_pool', 'pool_id'),
        Index('idx_adaptive_question_difficulty', 'difficulty_level'),
        Index('idx_adaptive_question_topic', 'topic'),
        Index('idx_adaptive_question_irt', 'difficulty', 'discrimination'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'text': self.text,
            'type': self.type,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'discrimination': self.discrimination,
            'guessing': self.guessing,
            'difficulty_level': self.difficulty_level,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'cognitive_level': self.cognitive_level,
            'usage_count': self.usage_count,
            'correct_count': self.correct_count,
            'average_response_time': self.average_response_time,
            'exposure_rate': self.exposure_rate,
            'information_value': self.information_value,
            'is_active': self.is_active,
            'review_status': self.review_status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def calculate_probability(self, ability):
        """Calculate probability of correct response given ability level."""
        # 3-parameter logistic model: P(θ) = c + (1-c) / (1 + exp(-a(θ-b)))
        import math
        exp_val = math.exp(-self.discrimination * (ability - self.difficulty))
        probability = self.guessing + (1 - self.guessing) / (1 + exp_val)
        return probability
    
    def calculate_information(self, ability):
        """Calculate information value at given ability level."""
        # Information function: I(θ) = a²(P-c)²(1-P) / ((1-c)²P)
        p = self.calculate_probability(ability)
        if p == 0 or p == 1:
            return 0
        
        numerator = (self.discrimination ** 2) * ((p - self.guessing) ** 2) * (1 - p)
        denominator = ((1 - self.guessing) ** 2) * p
        
        if denominator == 0:
            return 0
            
        return numerator / denominator


class AdaptiveTestSession(db.Model):
    """Adaptive test session tracking."""
    __tablename__ = 'adaptive_test_sessions'
    
    id = Column(Integer, primary_key=True)
    pool_id = Column(Integer, ForeignKey('adaptive_test_pools.id'), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    test_id = Column(Integer, ForeignKey('test_sets.id'), nullable=True)  # Link to regular test if applicable
    
    # Session configuration
    max_questions = Column(Integer, nullable=False, default=20)
    max_time = Column(Integer, nullable=True)  # in minutes
    standard_error_threshold = Column(Float, nullable=False, default=0.3)
    initial_ability = Column(Float, nullable=False, default=0.0)
    
    # Current state
    current_ability = Column(Float, nullable=False, default=0.0)
    ability_se = Column(Float, nullable=True)  # Standard error of ability estimate
    questions_answered = Column(Integer, default=0)
    status = Column(String(20), default='in_progress')  # in_progress, completed, abandoned
    
    # Question selection strategy
    selection_method = Column(String(50), default='maximum_information')
    topic_balancing = Column(Boolean, default=True)
    exposure_control = Column(Boolean, default=True)
    
    # Session metadata
    asked_questions = Column(JSON, default=list)  # List of question IDs already asked
    topic_coverage = Column(JSON, default=dict)  # Track topic coverage
    ability_history = Column(JSON, default=list)  # Ability estimates after each question
    
    # Results
    final_ability = Column(Float, nullable=True)
    final_se = Column(Float, nullable=True)
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    
    # Timing
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    total_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pool = relationship('AdaptiveTestPool', back_populates='sessions')
    beneficiary = relationship('Beneficiary', backref='adaptive_test_sessions')
    responses = relationship('AdaptiveResponse', back_populates='session', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_adaptive_session_beneficiary', 'beneficiary_id'),
        Index('idx_adaptive_session_status', 'status'),
        Index('idx_adaptive_session_pool', 'pool_id'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'beneficiary_id': self.beneficiary_id,
            'test_id': self.test_id,
            'max_questions': self.max_questions,
            'max_time': self.max_time,
            'standard_error_threshold': self.standard_error_threshold,
            'initial_ability': self.initial_ability,
            'current_ability': self.current_ability,
            'ability_se': self.ability_se,
            'questions_answered': self.questions_answered,
            'status': self.status,
            'selection_method': self.selection_method,
            'topic_balancing': self.topic_balancing,
            'exposure_control': self.exposure_control,
            'asked_questions': self.asked_questions,
            'topic_coverage': self.topic_coverage,
            'ability_history': self.ability_history,
            'final_ability': self.final_ability,
            'final_se': self.final_se,
            'confidence_interval_lower': self.confidence_interval_lower,
            'confidence_interval_upper': self.confidence_interval_upper,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_time_seconds': self.total_time_seconds,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def should_stop(self):
        """Check if test should stop based on stopping criteria."""
        # Check maximum questions
        if self.questions_answered >= self.max_questions:
            return True, "Maximum questions reached"
        
        # Check time limit
        if self.max_time:
            elapsed_minutes = (datetime.utcnow() - self.start_time).total_seconds() / 60
            if elapsed_minutes >= self.max_time:
                return True, "Time limit reached"
        
        # Check standard error threshold
        if self.ability_se and self.ability_se <= self.standard_error_threshold:
            return True, "Standard error threshold met"
        
        # Minimum questions before SE check
        if self.questions_answered < 5:
            return False, "Minimum questions not met"
        
        return False, "Continue testing"


class AdaptiveResponse(db.Model):
    """Responses in adaptive test sessions."""
    __tablename__ = 'adaptive_responses'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('adaptive_test_sessions.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('adaptive_questions.id'), nullable=False)
    
    # Response data
    answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    response_time = Column(Float, nullable=True)  # in seconds
    
    # Ability tracking
    ability_before = Column(Float, nullable=False)
    ability_after = Column(Float, nullable=False)
    se_after = Column(Float, nullable=True)
    
    # Question metadata at time of response
    question_difficulty = Column(Float, nullable=False)
    question_discrimination = Column(Float, nullable=False)
    question_guessing = Column(Float, nullable=False)
    
    # Sequence
    question_number = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship('AdaptiveTestSession', back_populates='responses')
    question = relationship('AdaptiveQuestion', back_populates='responses')
    
    # Indexes
    __table_args__ = (
        Index('idx_adaptive_response_session', 'session_id'),
        Index('idx_adaptive_response_question', 'question_id'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'answer': self.answer,
            'is_correct': self.is_correct,
            'response_time': self.response_time,
            'ability_before': self.ability_before,
            'ability_after': self.ability_after,
            'se_after': self.se_after,
            'question_difficulty': self.question_difficulty,
            'question_discrimination': self.question_discrimination,
            'question_guessing': self.question_guessing,
            'question_number': self.question_number,
            'created_at': self.created_at.isoformat(),
            'answered_at': self.answered_at.isoformat()
        }


class AdaptiveTestReport(db.Model):
    """Detailed reports for adaptive test sessions."""
    __tablename__ = 'adaptive_test_reports'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('adaptive_test_sessions.id'), nullable=False, unique=True)
    
    # Overall performance
    final_ability = Column(Float, nullable=False)
    ability_percentile = Column(Float, nullable=True)  # Percentile rank
    performance_level = Column(String(50), nullable=True)  # e.g., "Advanced", "Proficient", "Basic"
    
    # Topic analysis
    topic_strengths = Column(JSON, nullable=True)  # Topics where user excelled
    topic_weaknesses = Column(JSON, nullable=True)  # Topics needing improvement
    topic_scores = Column(JSON, nullable=True)  # Detailed scores by topic
    
    # Learning insights
    learning_profile = Column(JSON, nullable=True)  # Learning style indicators
    response_patterns = Column(JSON, nullable=True)  # Pattern analysis
    
    # Recommendations
    recommended_topics = Column(JSON, nullable=True)
    recommended_difficulty = Column(Float, nullable=True)
    next_steps = Column(JSON, nullable=True)
    
    # Statistical summary
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    average_difficulty = Column(Float, nullable=True)
    response_consistency = Column(Float, nullable=True)  # Measure of response pattern consistency
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship('AdaptiveTestSession', backref='report', uselist=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'final_ability': self.final_ability,
            'ability_percentile': self.ability_percentile,
            'performance_level': self.performance_level,
            'topic_strengths': self.topic_strengths,
            'topic_weaknesses': self.topic_weaknesses,
            'topic_scores': self.topic_scores,
            'learning_profile': self.learning_profile,
            'response_patterns': self.response_patterns,
            'recommended_topics': self.recommended_topics,
            'recommended_difficulty': self.recommended_difficulty,
            'next_steps': self.next_steps,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'average_difficulty': self.average_difficulty,
            'response_consistency': self.response_consistency,
            'generated_at': self.generated_at.isoformat()
        }