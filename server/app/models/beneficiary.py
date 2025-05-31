"""Beneficiary model module."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.extensions import db


class Beneficiary(db.Model):
    """Beneficiary (Student) model."""
    __tablename__ = 'beneficiaries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    
    # Personal information
    gender = Column(String(10), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    nationality = Column(String(100), nullable=True)
    native_language = Column(String(100), nullable=True)
    
    # Professional information
    profession = Column(String(100), nullable=True)
    company = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    education_level = Column(String(100), nullable=True)
    
    # Additional information
    category = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    referral_source = Column(String(200), nullable=True)
    custom_fields = Column(JSON, nullable=True)
    
    # Computed fields for statistics
    @property
    def evaluation_count(self):
        """Get total evaluation count."""
        return self.evaluations.count() if hasattr(self, 'evaluations') else 0
    
    @property
    def completed_evaluation_count(self):
        """Get completed evaluation count."""
        if hasattr(self, 'evaluations'):
            return self.evaluations.filter_by(status='completed').count()
        return 0
    
    @property
    def session_count(self):
        """Get total session count."""
        # session_attendance is the correct relationship for sessions
        return self.session_attendance.count() if hasattr(self, 'session_attendance') else 0
    
    @property
    def trainer_count(self):
        """Get trainer count."""
        return 1 if self.trainer else 0
    
    @property
    def first_name(self):
        """Get first name from associated user."""
        return self.user.first_name if self.user else None
    
    @property
    def last_name(self):
        """Get last name from associated user."""
        return self.user.last_name if self.user else None
    
    # Status
    status = Column(String(20), default='active')  # active, inactive, archived
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='beneficiary_profile', lazy='select')
    trainer = relationship('User', foreign_keys=[trainer_id], backref='trainees', lazy='select')
    tenant = relationship('Tenant', backref='beneficiaries', lazy='select')
    appointments = relationship('Appointment', back_populates='beneficiary', lazy='dynamic', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='beneficiary', lazy='dynamic')
    evaluations = relationship('Evaluation', back_populates='beneficiary', lazy='dynamic')
    notes_rel = relationship('Note', back_populates='beneficiary', lazy='dynamic', cascade='all, delete-orphan')
    program_enrollments = relationship('ProgramEnrollment', back_populates='beneficiary', lazy='dynamic')
    session_attendance = relationship('SessionAttendance', back_populates='beneficiary', lazy='dynamic')
    
    def to_dict(self):
        """Return a dict representation of the beneficiary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trainer_id': self.trainer_id,
            'tenant_id': self.tenant_id,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'profession': self.profession,
            'company': self.company,
            'company_size': self.company_size,
            'years_of_experience': self.years_of_experience,
            'education_level': self.education_level,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the beneficiary."""
        return f'<Beneficiary {self.user.first_name} {self.user.last_name}>'


class Note(db.Model):
    """Note model for beneficiary notes."""
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Who created the note
    
    content = Column(Text, nullable=False)
    type = Column(String(20), default='general')  # general, private, assessment, etc.
    is_private = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = relationship('Beneficiary', back_populates='notes_rel', lazy='select')
    user = relationship('User', backref='notes', lazy='select')
    
    def to_dict(self):
        """Return a dict representation of the note."""
        return {
            'id': self.id,
            'beneficiary_id': self.beneficiary_id,
            'user_id': self.user_id,
            'content': self.content,
            'type': self.type,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class BeneficiaryAppointment(db.Model):
    """Appointment model for scheduling with beneficiaries."""
    __tablename__ = 'beneficiary_appointments'
    
    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # The trainer or admin
    
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(100), default='Online')
    status = Column(String(20), default='scheduled')  # scheduled, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='appointments')
    
    def to_dict(self):
        """Return a dict representation of the appointment."""
        return {
            'id': self.id,
            'beneficiary_id': self.beneficiary_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class BeneficiaryDocument(db.Model):
    """Document model for beneficiary documents."""
    __tablename__ = 'beneficiary_documents'
    
    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Who uploaded the document
    
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)  # In bytes
    is_private = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='documents')
    
    def to_dict(self):
        """Return a dict representation of the document."""
        return {
            'id': self.id,
            'beneficiary_id': self.beneficiary_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }