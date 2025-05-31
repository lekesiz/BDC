"""Program model."""

from datetime import datetime
from app.extensions import db

class Program(db.Model):
    """Model for training programs."""
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(50), unique=True)
    
    # Program details
    duration = db.Column(db.Integer)  # in days
    level = db.Column(db.String(20))  # beginner, intermediate, advanced
    category = db.Column(db.String(50))  # technical, soft-skills, leadership, etc.
    
    # Requirements
    prerequisites = db.Column(db.Text)
    minimum_attendance = db.Column(db.Float, default=80.0)
    passing_score = db.Column(db.Float, default=70.0)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, archived
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadata
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    max_participants = db.Column(db.Integer)
    
    # Foreign keys
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='programs', lazy='select')
    created_by = db.relationship('User', back_populates='programs_created', lazy='select')
    modules = db.relationship('ProgramModule', back_populates='program', cascade='all, delete-orphan', lazy='dynamic')
    enrollments = db.relationship('ProgramEnrollment', back_populates='program', cascade='all, delete-orphan', lazy='dynamic')
    sessions = db.relationship('TrainingSession', back_populates='program', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self):
        """Convert program to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'duration': self.duration,
            'duration_weeks': round(self.duration / 7.0, 2) if self.duration else None,
            'level': self.level,
            'category': self.category,
            'prerequisites': self.prerequisites,
            'minimum_attendance': self.minimum_attendance,
            'passing_score': self.passing_score,
            'status': self.status,
            'is_active': self.is_active,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_participants': self.max_participants,
            'enrolled_count': len(self.enrollments),
            'module_count': len(self.modules),
            'session_count': len(self.sessions),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProgramModule(db.Model):
    """Model for program modules."""
    __tablename__ = 'program_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    
    # Module content
    content = db.Column(db.Text)
    resources = db.Column(db.JSON, default=[])
    
    # Requirements
    duration = db.Column(db.Integer)  # in hours
    is_mandatory = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = db.relationship('Program', back_populates='modules', lazy='select')
    sessions = db.relationship('TrainingSession', back_populates='module', lazy='dynamic')
    
    def to_dict(self):
        """Convert module to dictionary."""
        return {
            'id': self.id,
            'program_id': self.program_id,
            'name': self.name,
            'description': self.description,
            'order': self.order,
            'content': self.content,
            'resources': self.resources,
            'duration': self.duration,
            'is_mandatory': self.is_mandatory,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProgramEnrollment(db.Model):
    """Model for program enrollments."""
    __tablename__ = 'program_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id', ondelete='CASCADE'), nullable=False)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id', ondelete='CASCADE'), nullable=False)
    
    # Enrollment details
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='enrolled')  # enrolled, active, completed, withdrawn
    
    # Progress tracking
    progress = db.Column(db.Float, default=0.0)
    attendance_rate = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Completion
    completion_date = db.Column(db.DateTime)
    certificate_issued = db.Column(db.Boolean, default=False)
    certificate_number = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = db.relationship('Program', back_populates='enrollments', lazy='select')
    beneficiary = db.relationship('Beneficiary', back_populates='program_enrollments', lazy='select')
    
    def to_dict(self):
        """Convert enrollment to dictionary."""
        return {
            'id': self.id,
            'program': {
                'id': self.program.id,
                'name': self.program.name,
                'code': self.program.code
            } if self.program else None,
            'beneficiary': {
                'id': self.beneficiary.id,
                'name': f"{self.beneficiary.first_name} {self.beneficiary.last_name}"
            } if self.beneficiary else None,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status,
            'progress': self.progress,
            'attendance_rate': self.attendance_rate,
            'overall_score': self.overall_score,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'certificate_issued': self.certificate_issued,
            'certificate_number': self.certificate_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TrainingSession(db.Model):
    """Model for training sessions."""
    __tablename__ = 'training_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('program_modules.id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    session_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    location = db.Column(db.String(255))
    online_link = db.Column(db.String(500))
    
    # Attendance
    max_participants = db.Column(db.Integer)
    attendance_required = db.Column(db.Boolean, default=True)
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, ongoing, completed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = db.relationship('Program', back_populates='sessions')
    module = db.relationship('ProgramModule', back_populates='sessions')
    trainer = db.relationship('User', back_populates='training_sessions')
    attendance_records = db.relationship('SessionAttendance', back_populates='session', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'program': {
                'id': self.program.id,
                'name': self.program.name
            } if self.program else None,
            'module': {
                'id': self.module.id,
                'name': self.module.name
            } if self.module else None,
            'trainer': {
                'id': self.trainer.id,
                'name': f"{self.trainer.first_name} {self.trainer.last_name}"
            } if self.trainer else None,
            'title': self.title,
            'description': self.description,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'duration': self.duration,
            'duration_weeks': round(self.duration / 7.0, 2) if self.duration else None,
            'location': self.location,
            'online_link': self.online_link,
            'max_participants': self.max_participants,
            'attendance_required': self.attendance_required,
            'status': self.status,
            'attendee_count': len(self.attendance_records),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SessionAttendance(db.Model):
    """Model for session attendance."""
    __tablename__ = 'session_attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id'), nullable=False)
    
    # Attendance details
    status = db.Column(db.String(20), default='registered')  # registered, present, absent, excused
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    
    # Feedback
    rating = db.Column(db.Integer)  # 1-5
    feedback = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = db.relationship('TrainingSession', back_populates='attendance_records')
    beneficiary = db.relationship('Beneficiary', back_populates='session_attendance')
    
    def to_dict(self):
        """Convert attendance to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'beneficiary': {
                'id': self.beneficiary.id,
                'name': f"{self.beneficiary.first_name} {self.beneficiary.last_name}"
            } if self.beneficiary else None,
            'status': self.status,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }