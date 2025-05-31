import pytest
from datetime import datetime, timezone

from app import create_app, db
from app.models import User, Beneficiary, Note, BeneficiaryAppointment, BeneficiaryDocument


class TestBeneficiaryModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test users
        self.trainer = User(
            email='trainer@test.com',
            first_name='Trainer',
            last_name='User',
            role='trainer'
        )
        self.trainer.password = 'password123'
        
        self.student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        self.student.password = 'password123'
        
        db.session.add_all([self.trainer, self.student])
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_beneficiary_creation(self):
        """Test creating a beneficiary"""
        beneficiary = Beneficiary(
            user_id=self.student.id,
            trainer_id=self.trainer.id,
            date_of_birth='1990-01-01',
            gender='male',
            phone='+1234567890',
            emergency_contact='Emergency Person',
            emergency_phone='+0987654321',
            goals='Test goals',
            is_active=True
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        assert beneficiary.id is not None
        assert beneficiary.user_id == self.student.id
        assert beneficiary.trainer_id == self.trainer.id
        assert beneficiary.goals == 'Test goals'
        assert beneficiary.is_active is True
    
    def test_beneficiary_relationships(self):
        """Test beneficiary relationships"""
        beneficiary = Beneficiary(
            user_id=self.student.id,
            trainer_id=self.trainer.id
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        # Test user relationship
        assert beneficiary.user == self.student
        assert beneficiary.user.email == 'student@test.com'
        
        # Test trainer relationship
        assert beneficiary.trainer == self.trainer
        assert beneficiary.trainer.email == 'trainer@test.com'
    
    def test_beneficiary_to_dict(self):
        """Test converting beneficiary to dictionary"""
        beneficiary = Beneficiary(
            user_id=self.student.id,
            trainer_id=self.trainer.id,
            date_of_birth='1990-01-01',
            gender='female',
            phone='+1234567890',
            profession='Software Developer',
            is_active=True
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        beneficiary_dict = beneficiary.to_dict()
        
        assert beneficiary_dict['id'] == beneficiary.id
        assert beneficiary_dict['user_id'] == self.student.id
        assert beneficiary_dict['trainer_id'] == self.trainer.id
        assert beneficiary_dict['date_of_birth'] == '1990-01-01'
        assert beneficiary_dict['gender'] == 'female'
        assert beneficiary_dict['profession'] == 'Software Developer'
        assert beneficiary_dict['is_active'] is True
    
    def test_beneficiary_string_representation(self):
        """Test string representation of beneficiary"""
        beneficiary = Beneficiary(user_id=self.student.id)
        db.session.add(beneficiary)
        db.session.commit()
        
        assert str(beneficiary) == f'<Beneficiary {beneficiary.id}>'


class TestNoteModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.trainer = User(
            email='trainer@test.com',
            first_name='Trainer',
            last_name='User',
            role='trainer'
        )
        self.trainer.password = 'password123'
        
        self.student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        self.student.password = 'password123'
        
        db.session.add_all([self.trainer, self.student])
        db.session.commit()
        
        self.beneficiary = Beneficiary(
            user_id=self.student.id,
            trainer_id=self.trainer.id
        )
        db.session.add(self.beneficiary)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_note_creation(self):
        """Test creating a note"""
        note = Note(
            beneficiary_id=self.beneficiary.id,
            author_id=self.trainer.id,
            content='Test note content',
            note_type='progress'
        )
        
        db.session.add(note)
        db.session.commit()
        
        assert note.id is not None
        assert note.beneficiary_id == self.beneficiary.id
        assert note.author_id == self.trainer.id
        assert note.content == 'Test note content'
        assert note.note_type == 'progress'
    
    def test_note_relationships(self):
        """Test note relationships"""
        note = Note(
            beneficiary_id=self.beneficiary.id,
            author_id=self.trainer.id,
            content='Test note'
        )
        
        db.session.add(note)
        db.session.commit()
        
        assert note.beneficiary == self.beneficiary
        assert note.author == self.trainer
    
    def test_note_to_dict(self):
        """Test converting note to dictionary"""
        note = Note(
            beneficiary_id=self.beneficiary.id,
            author_id=self.trainer.id,
            content='Important note',
            note_type='observation'
        )
        
        db.session.add(note)
        db.session.commit()
        
        note_dict = note.to_dict()
        
        assert note_dict['id'] == note.id
        assert note_dict['beneficiary_id'] == self.beneficiary.id
        assert note_dict['author_id'] == self.trainer.id
        assert note_dict['content'] == 'Important note'
        assert note_dict['note_type'] == 'observation'
        assert 'created_at' in note_dict


class TestBeneficiaryAppointmentModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.trainer = User(
            email='trainer@test.com',
            first_name='Trainer',
            last_name='User',
            role='trainer'
        )
        self.trainer.password = 'password123'
        
        self.student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        self.student.password = 'password123'
        
        db.session.add_all([self.trainer, self.student])
        db.session.commit()
        
        self.beneficiary = Beneficiary(
            user_id=self.student.id,
            trainer_id=self.trainer.id
        )
        db.session.add(self.beneficiary)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_beneficiary_appointment_creation(self):
        """Test creating a beneficiary appointment"""
        appointment = BeneficiaryAppointment(
            beneficiary_id=self.beneficiary.id,
            trainer_id=self.trainer.id,
            title='Training Session',
            description='Weekly training',
            appointment_date=datetime.now(timezone.utc),
            duration=60,
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        assert appointment.id is not None
        assert appointment.title == 'Training Session'
        assert appointment.duration == 60
        assert appointment.status == 'scheduled'
    
    def test_beneficiary_appointment_relationships(self):
        """Test appointment relationships"""
        appointment = BeneficiaryAppointment(
            beneficiary_id=self.beneficiary.id,
            trainer_id=self.trainer.id,
            title='Session',
            appointment_date=datetime.now(timezone.utc)
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        assert appointment.beneficiary == self.beneficiary
        assert appointment.trainer == self.trainer
    
    def test_beneficiary_appointment_to_dict(self):
        """Test converting appointment to dictionary"""
        now = datetime.now(timezone.utc)
        appointment = BeneficiaryAppointment(
            beneficiary_id=self.beneficiary.id,
            trainer_id=self.trainer.id,
            title='Evaluation',
            description='Monthly evaluation',
            appointment_date=now,
            duration=90,
            status='completed',
            notes='Good progress'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        appointment_dict = appointment.to_dict()
        
        assert appointment_dict['id'] == appointment.id
        assert appointment_dict['title'] == 'Evaluation'
        assert appointment_dict['duration'] == 90
        assert appointment_dict['status'] == 'completed'
        assert appointment_dict['notes'] == 'Good progress'


class TestBeneficiaryDocumentModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.trainer = User(
            email='trainer@test.com',
            first_name='Trainer',
            last_name='User',
            role='trainer'
        )
        self.trainer.password = 'password123'
        
        self.student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        self.student.password = 'password123'
        
        db.session.add_all([self.trainer, self.student])
        db.session.commit()
        
        self.beneficiary = Beneficiary(
            user_id=self.student.id,
            trainer_id=self.trainer.id
        )
        db.session.add(self.beneficiary)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_beneficiary_document_creation(self):
        """Test creating a beneficiary document"""
        document = BeneficiaryDocument(
            beneficiary_id=self.beneficiary.id,
            uploaded_by=self.trainer.id,
            title='Progress Report',
            description='Monthly progress report',
            file_path='/uploads/report.pdf',
            file_size=1024,
            file_type='pdf'
        )
        
        db.session.add(document)
        db.session.commit()
        
        assert document.id is not None
        assert document.title == 'Progress Report'
        assert document.file_size == 1024
        assert document.file_type == 'pdf'
    
    def test_beneficiary_document_relationships(self):
        """Test document relationships"""
        document = BeneficiaryDocument(
            beneficiary_id=self.beneficiary.id,
            uploaded_by=self.trainer.id,
            title='Document',
            file_path='/uploads/doc.pdf'
        )
        
        db.session.add(document)
        db.session.commit()
        
        assert document.beneficiary == self.beneficiary
        assert document.uploader == self.trainer
    
    def test_beneficiary_document_to_dict(self):
        """Test converting document to dictionary"""
        document = BeneficiaryDocument(
            beneficiary_id=self.beneficiary.id,
            uploaded_by=self.trainer.id,
            title='Certificate',
            description='Training certificate',
            file_path='/uploads/cert.pdf',
            file_size=2048,
            file_type='pdf',
            is_active=True
        )
        
        db.session.add(document)
        db.session.commit()
        
        document_dict = document.to_dict()
        
        assert document_dict['id'] == document.id
        assert document_dict['title'] == 'Certificate'
        assert document_dict['file_size'] == 2048
        assert document_dict['is_active'] is True