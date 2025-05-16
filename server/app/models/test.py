"""Test engine models module."""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.extensions import db


class Test(db.Model):
    """Test model for BDC system."""
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # questionnaire, assessment, skill_test, etc.
    category = Column(String(50), nullable=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    duration = Column(Integer, nullable=True)  # in minutes
    passing_score = Column(Float, nullable=True)
    total_points = Column(Float, nullable=True)
    
    status = Column(String(20), default='draft')  # draft, published, archived
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='tests')
    creator = relationship('User', backref='created_tests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'category': self.category,
            'tenant_id': self.tenant_id,
            'created_by': self.created_by,
            'duration': self.duration,
            'passing_score': self.passing_score,
            'total_points': self.total_points,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class TestSet(db.Model):
    """Test set model for evaluations."""
    __tablename__ = 'test_sets'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=True)
    
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    type = Column(String(20), default='assessment')  # assessment, quiz, survey, etc.
    category = Column(String(50), nullable=True)
    
    # Configuration
    time_limit = Column(Integer, nullable=True)  # in minutes, None means no limit
    passing_score = Column(Float, nullable=True)
    is_randomized = Column(Boolean, default=False)
    allow_resume = Column(Boolean, default=True)
    max_attempts = Column(Integer, default=1)  # 0 means unlimited
    show_results = Column(Boolean, default=True)
    
    # Status
    status = Column(String(20), default='draft')  # draft, active, archived
    is_template = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='test_sets')
    creator = relationship('User', foreign_keys=[creator_id], backref='created_test_sets')
    questions = relationship('Question', backref='evaluation', lazy='dynamic')
    sessions = relationship('TestSession', backref='evaluation', lazy='dynamic')
    
    def to_dict(self):
        """Return a dict representation of the evaluation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'creator_id': self.creator_id,
            'beneficiary_id': self.beneficiary_id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'type': self.type,
            'category': self.category,
            'time_limit': self.time_limit,
            'passing_score': self.passing_score,
            'is_randomized': self.is_randomized,
            'allow_resume': self.allow_resume,
            'max_attempts': self.max_attempts,
            'show_results': self.show_results,
            'status': self.status,
            'is_template': self.is_template,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Question(db.Model):
    """Question model for evaluation questions."""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    test_set_id = Column(Integer, ForeignKey('test_sets.id'), nullable=False)
    
    text = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # multiple_choice, text, true_false, matching, ordering
    options = Column(JSON, nullable=True)  # Stores question options as a JSON object
    correct_answer = Column(JSON, nullable=True)  # Stores correct answer(s) as a JSON object
    explanation = Column(Text, nullable=True)
    
    # Metadata
    category = Column(String(50), nullable=True)
    difficulty = Column(String(20), default='medium')  # easy, medium, hard
    points = Column(Float, default=1.0)
    order = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = relationship('Response', backref='question', lazy='dynamic')
    
    def to_dict(self):
        """Return a dict representation of the question."""
        return {
            'id': self.id,
            'test_set_id': self.test_set_id,
            'text': self.text,
            'type': self.type,
            'options': self.options,
            'explanation': self.explanation,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points,
            'order': self.order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def check_answer(self, answer):
        """Check if the given answer is correct."""
        if self.type == 'multiple_choice':
            if isinstance(self.correct_answer, list):
                return sorted(answer) == sorted(self.correct_answer)
            return answer == self.correct_answer
        elif self.type == 'true_false':
            return answer == self.correct_answer
        elif self.type == 'matching':
            return answer == self.correct_answer
        elif self.type == 'ordering':
            return answer == self.correct_answer
        elif self.type == 'text':
            # For text questions, this might require more sophisticated checking
            # like keyword matching or AI-based evaluation
            return True  # Always mark as correct for now
        return False


class TestSession(db.Model):
    """Test session model for tracking beneficiary evaluation attempts."""
    __tablename__ = 'test_sessions'
    
    id = Column(Integer, primary_key=True)
    test_set_id = Column(Integer, ForeignKey('test_sets.id'), nullable=False)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    
    # Session state
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    time_spent = Column(Integer, nullable=True)  # in seconds
    current_question = Column(Integer, nullable=True)
    status = Column(String(20), default='in_progress')  # in_progress, completed, abandoned
    
    # Results
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = relationship('Beneficiary', backref='test_sessions')
    responses = relationship('Response', backref='session', lazy='dynamic')
    
    def to_dict(self):
        """Return a dict representation of the test session."""
        return {
            'id': self.id,
            'test_set_id': self.test_set_id,
            'beneficiary_id': self.beneficiary_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'time_spent': self.time_spent,
            'current_question': self.current_question,
            'status': self.status,
            'score': self.score,
            'max_score': self.max_score,
            'passed': self.passed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Response(db.Model):
    """Response model for tracking beneficiary responses to questions."""
    __tablename__ = 'responses'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('test_sessions.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    
    # Response data
    answer = Column(JSON, nullable=True)  # Stores the beneficiary's answer as a JSON object
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)
    
    # Timing data
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    time_spent = Column(Integer, nullable=True)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Return a dict representation of the response."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'answer': self.answer,
            'is_correct': self.is_correct,
            'score': self.score,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AIFeedback(db.Model):
    """AI-generated feedback model."""
    __tablename__ = 'ai_feedback'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('test_sessions.id'), nullable=False)
    
    # Feedback content
    summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)
    areas_to_improve = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    next_steps = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default='draft')  # draft, approved, rejected
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    rejected_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship('TestSession', backref='ai_feedback')
    approver = relationship('User', backref='approved_feedback')
    
    def to_dict(self):
        """Return a dict representation of the AI feedback."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'summary': self.summary,
            'strengths': self.strengths,
            'areas_to_improve': self.areas_to_improve,
            'recommendations': self.recommendations,
            'next_steps': self.next_steps,
            'status': self.status,
            'approved_by': self.approved_by,
            'rejected_reason': self.rejected_reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }