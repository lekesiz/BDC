"""Evaluation model for the BDC system."""
from datetime import datetime
from app.extensions import db


class Evaluation(db.Model):
    """Evaluation results model."""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id', ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    responses = db.Column(db.JSON)  # User responses to test questions
    evaluation_extra_data = db.Column(db.JSON)  # Additional evaluation data
    
    # Randomization settings
    randomization_enabled = db.Column(db.Boolean, default=True)
    randomization_strategy = db.Column(db.String(50), default='simple_random')  # simple_random, stratified, deterministic, adaptive, template_based, balanced
    randomization_config = db.Column(db.JSON)  # Strategy-specific configuration
    question_order_template = db.Column(db.String(50), nullable=True)  # For template-based strategy
    anchor_questions = db.Column(db.JSON)  # Fixed position questions
    answer_randomization = db.Column(db.Boolean, default=True)
    blocking_rules = db.Column(db.JSON)  # Question blocking rules
    time_based_seed = db.Column(db.Boolean, default=False)
    
    # Adaptive testing fields
    is_adaptive = db.Column(db.Boolean, default=False)
    adaptive_session_id = db.Column(db.Integer, db.ForeignKey('adaptive_test_sessions.id', ondelete='SET NULL'), nullable=True)
    
    status = db.Column(db.String(50), default='in_progress')  # in_progress, completed, reviewed
    completed_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = db.relationship('Beneficiary', back_populates='evaluations', lazy='select')
    test = db.relationship('Test', backref='evaluations', lazy='select')
    trainer = db.relationship('User', foreign_keys=[trainer_id], backref='evaluations_as_trainer', lazy='select')
    creator = db.relationship('User', foreign_keys=[creator_id], backref='evaluations_created', lazy='select')
    tenant = db.relationship('Tenant', backref='evaluations', lazy='select')
    adaptive_session = db.relationship('AdaptiveTestSession', backref='evaluation', lazy='select')
    
    def to_dict(self):
        """Convert evaluation to dictionary."""
        return {
            'id': self.id,
            'beneficiary_id': self.beneficiary_id,
            'test_id': self.test_id,
            'trainer_id': self.trainer_id,
            'score': self.score,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendations': self.recommendations,
            'responses': self.responses,
            'metadata': self.evaluation_extra_data,
            'status': self.status,
            'is_adaptive': self.is_adaptive,
            'adaptive_session_id': self.adaptive_session_id,
            'randomization_enabled': self.randomization_enabled,
            'randomization_strategy': self.randomization_strategy,
            'randomization_config': self.randomization_config,
            'question_order_template': self.question_order_template,
            'anchor_questions': self.anchor_questions,
            'answer_randomization': self.answer_randomization,
            'blocking_rules': self.blocking_rules,
            'time_based_seed': self.time_based_seed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def calculate_score(self):
        """Calculate evaluation score based on responses."""
        if not self.responses:
            return 0
        
        # Simple calculation - can be customized based on test type
        correct_count = sum(1 for response in self.responses if response.get('is_correct', False))
        total_questions = len(self.responses)
        
        if total_questions > 0:
            self.score = (correct_count / total_questions) * 100
            
        return self.score
    
    def complete(self):
        """Mark evaluation as completed."""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        # Note: db.session.commit() should be called by the service layer, not the model
        
    def review(self):
        """Mark evaluation as reviewed."""
        self.status = 'reviewed'
        self.reviewed_at = datetime.utcnow()
        # Note: db.session.commit() should be called by the service layer, not the model