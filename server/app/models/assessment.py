"""Assessment models."""

from app.extensions import db
from datetime import datetime


class AssessmentTemplate(db.Model):
    """Assessment template model."""
    __tablename__ = 'assessment_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.String(20), default='medium')  # easy, medium, hard
    time_limit = db.Column(db.Integer, default=60)  # in minutes
    total_points = db.Column(db.Integer, default=100)
    passing_score = db.Column(db.Integer, default=70)
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='assessment_templates')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_templates')
    sections = db.relationship('AssessmentSection', cascade='all, delete-orphan', backref='template')
    assessments = db.relationship('Assessment', backref='template')
    
    def __repr__(self):
        return f'<AssessmentTemplate {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'time_limit': self.time_limit,
            'total_points': self.total_points,
            'passing_score': self.passing_score,
            'instructions': self.instructions,
            'is_active': self.is_active,
            'tenant_id': self.tenant_id,
            'created_by': self.created_by,
            'sections': [section.to_dict() for section in self.sections],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AssessmentSection(db.Model):
    """Assessment section model."""
    __tablename__ = 'assessment_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('assessment_templates.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    order_index = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('AssessmentQuestion', cascade='all, delete-orphan', backref='section')
    
    def __repr__(self):
        return f'<AssessmentSection {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'order_index': self.order_index,
            'points': self.points,
            'questions': [question.to_dict() for question in self.questions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AssessmentQuestion(db.Model):
    """Assessment question model."""
    __tablename__ = 'assessment_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('assessment_sections.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # multiple_choice, true_false, short_answer, essay, etc.
    points = db.Column(db.Integer, default=1)
    correct_answer = db.Column(db.JSON)  # For automated grading
    answer_options = db.Column(db.JSON)  # For multiple choice questions
    order_index = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AssessmentQuestion {self.id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'section_id': self.section_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'points': self.points,
            'correct_answer': self.correct_answer,
            'answer_options': self.answer_options,
            'order_index': self.order_index,
            'is_required': self.is_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Assessment(db.Model):
    """Assessment instance model."""
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('assessment_templates.id'), nullable=False)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='assigned')  # assigned, in_progress, completed, graded
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    submit_time = db.Column(db.DateTime)
    score = db.Column(db.Float)
    passed = db.Column(db.Boolean)
    feedback = db.Column(db.Text)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    graded_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = db.relationship('Beneficiary', backref='assessments')
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='assigned_assessments')
    grader = db.relationship('User', foreign_keys=[graded_by], backref='graded_assessments')
    responses = db.relationship('AssessmentResponse', cascade='all, delete-orphan', backref='assessment')
    
    def __repr__(self):
        return f'<Assessment {self.id} - {self.status}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'template_id': self.template_id,
            'beneficiary_id': self.beneficiary_id,
            'assigned_by': self.assigned_by,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'submit_time': self.submit_time.isoformat() if self.submit_time else None,
            'score': self.score,
            'passed': self.passed,
            'feedback': self.feedback,
            'graded_by': self.graded_by,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AssessmentResponse(db.Model):
    """Assessment response model."""
    __tablename__ = 'assessment_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('assessment_questions.id'), nullable=False)
    answer = db.Column(db.JSON)
    is_correct = db.Column(db.Boolean)
    points_earned = db.Column(db.Float, default=0)
    feedback = db.Column(db.Text)
    time_spent = db.Column(db.Integer)  # in seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question = db.relationship('AssessmentQuestion', backref='responses')
    
    def __repr__(self):
        return f'<AssessmentResponse {self.id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'question_id': self.question_id,
            'answer': self.answer,
            'is_correct': self.is_correct,
            'points_earned': self.points_earned,
            'feedback': self.feedback,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }