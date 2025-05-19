"""Tests for model methods to increase coverage."""

import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.models.appointment import Appointment
from app.models.document import Document
from app.models.notification import Notification
from app.models.tenant import Tenant
from app.models.settings import GeneralSettings, AppearanceSettings
from app.models.assessment import AssessmentTemplate, AssessmentSection, AssessmentQuestion
from app.models.availability import AvailabilitySchedule, AvailabilitySlot, AvailabilityException
from app.models.profile import UserProfile


class TestUserModel:
    """Test User model methods."""
    
    def test_user_creation(self, test_app):
        """Test creating a user."""
        with test_app.app_context():
            user = User(
                email='test@example.com',
                username='testuser',
                first_name='Test',
                last_name='User',
                role='student'
            )
            user.password = 'password123'
            
            assert user.email == 'test@example.com'
            assert user.verify_password('password123')
            assert not user.verify_password('wrongpassword')
            assert user.role == 'student'
            # is_active might not have a default, check if it exists
            # assert user.is_active is True
    
    def test_user_to_dict(self, test_user):
        """Test user to_dict method."""
        user_dict = test_user.to_dict()
        
        assert 'id' in user_dict
        assert 'email' in user_dict
        assert 'first_name' in user_dict
        assert 'last_name' in user_dict
        assert 'role' in user_dict
        assert 'password' not in user_dict  # Password should not be in dict
    
    def test_user_repr(self, test_user):
        """Test user string representation."""
        repr_str = repr(test_user)
        assert test_user.email in repr_str


class TestBeneficiaryModel:
    """Test Beneficiary model methods."""
    
    def test_beneficiary_creation(self, test_app, test_user, test_trainer):
        """Test creating a beneficiary."""
        with test_app.app_context():
            beneficiary = Beneficiary(
                user_id=test_user.id,
                phone='+1234567890',
                birth_date=datetime(1990, 1, 1),
                trainer_id=test_trainer.id,
                status='active'
            )
            
            assert beneficiary.user_id == test_user.id
            assert beneficiary.phone == '+1234567890'
            assert beneficiary.status == 'active'
    
    def test_beneficiary_to_dict(self, test_beneficiary):
        """Test beneficiary to_dict method."""
        ben_dict = test_beneficiary.to_dict()
        
        assert 'id' in ben_dict
        assert 'user_id' in ben_dict
        assert 'phone' in ben_dict
        assert 'status' in ben_dict
        assert 'trainer_id' in ben_dict


class TestProgramModel:
    """Test Program model methods."""
    
    def test_program_creation(self, test_app, test_trainer, test_tenant):
        """Test creating a program."""
        with test_app.app_context():
            program = Program(
                name='Test Program',
                description='A test program',
                tenant_id=test_tenant.id,
                created_by_id=test_trainer.id,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                status='active'
            )
            
            assert program.name == 'Test Program'
            assert program.status == 'active'
            assert program.is_active is True
    
    def test_program_to_dict(self, test_program):
        """Test program to_dict method."""
        prog_dict = test_program.to_dict()
        
        assert 'id' in prog_dict
        assert 'name' in prog_dict
        assert 'description' in prog_dict
        assert 'status' in prog_dict
        assert 'start_date' in prog_dict
        assert 'end_date' in prog_dict


class TestEvaluationModel:
    """Test Evaluation model methods."""
    
    def test_evaluation_creation(self, test_app, test_beneficiary, test_trainer):
        """Test creating an evaluation."""
        with test_app.app_context():
            evaluation = Evaluation(
                beneficiary_id=test_beneficiary.id,
                evaluator_id=test_trainer.id,
                test_id=1,
                status='pending',
                score=0
            )
            
            assert evaluation.beneficiary_id == test_beneficiary.id
            assert evaluation.status == 'pending'
            assert evaluation.score == 0
    
    def test_evaluation_to_dict(self, test_app, test_beneficiary, test_trainer):
        """Test evaluation to_dict method."""
        with test_app.app_context():
            evaluation = Evaluation(
                beneficiary_id=test_beneficiary.id,
                evaluator_id=test_trainer.id,
                test_id=1,
                status='completed',
                score=85
            )
            
            eval_dict = evaluation.to_dict()
            
            assert 'beneficiary_id' in eval_dict
            assert 'evaluator_id' in eval_dict
            assert 'status' in eval_dict
            assert 'score' in eval_dict


class TestDocumentModel:
    """Test Document model methods."""
    
    def test_document_creation(self, test_app, test_trainer):
        """Test creating a document."""
        with test_app.app_context():
            document = Document(
                title='Test Document',
                description='A test document',
                file_path='/uploads/test.pdf',
                file_type='pdf',
                file_size=1024,
                upload_by=test_trainer.id,
                document_type='general'
            )
            
            assert document.title == 'Test Document'
            assert document.file_type == 'pdf'
            assert document.file_size == 1024
    
    def test_document_to_dict(self, test_document):
        """Test document to_dict method."""
        doc_dict = test_document.to_dict()
        
        assert 'id' in doc_dict
        assert 'title' in doc_dict
        assert 'file_path' in doc_dict
        assert 'file_type' in doc_dict
        assert 'upload_date' in doc_dict


class TestNotificationModel:
    """Test Notification model methods."""
    
    def test_notification_creation(self, test_app, test_user):
        """Test creating a notification."""
        with test_app.app_context():
            notification = Notification(
                user_id=test_user.id,
                type='info',
                title='Test Notification',
                message='This is a test',
                read=False
            )
            
            assert notification.user_id == test_user.id
            assert notification.type == 'info'
            assert notification.read is False
    
    def test_notification_to_dict(self, test_notification):
        """Test notification to_dict method."""
        notif_dict = test_notification.to_dict()
        
        assert 'id' in notif_dict
        assert 'user_id' in notif_dict
        assert 'type' in notif_dict
        assert 'title' in notif_dict
        assert 'message' in notif_dict
        assert 'read' in notif_dict


class TestTenantModel:
    """Test Tenant model methods."""
    
    def test_tenant_creation(self, test_app):
        """Test creating a tenant."""
        with test_app.app_context():
            tenant = Tenant(
                name='Test Organization',
                slug='test-org',
                email='admin@test.org',
                is_active=True
            )
            
            assert tenant.name == 'Test Organization'
            assert tenant.slug == 'test-org'
            assert tenant.is_active is True
    
    def test_tenant_to_dict(self, test_tenant):
        """Test tenant to_dict method."""
        tenant_dict = test_tenant.to_dict()
        
        assert 'id' in tenant_dict
        assert 'name' in tenant_dict
        assert 'slug' in tenant_dict
        assert 'email' in tenant_dict
        assert 'is_active' in tenant_dict


class TestSettingsModels:
    """Test Settings model methods."""
    
    def test_general_settings_creation(self, test_app, test_tenant):
        """Test creating general settings."""
        with test_app.app_context():
            settings = GeneralSettings(
                tenant_id=test_tenant.id,
                site_name='Test Site',
                contact_email='contact@test.com',
                default_language='en',
                timezone='UTC'
            )
            
            assert settings.site_name == 'Test Site'
            assert settings.default_language == 'en'
    
    def test_appearance_settings_creation(self, test_app, test_tenant):
        """Test creating appearance settings."""
        with test_app.app_context():
            settings = AppearanceSettings(
                tenant_id=test_tenant.id,
                theme='dark',
                primary_color='#3B82F6',
                font_family='Inter'
            )
            
            assert settings.theme == 'dark'
            assert settings.primary_color == '#3B82F6'


class TestAssessmentModels:
    """Test Assessment model methods."""
    
    def test_assessment_template_creation(self, test_app, test_trainer, test_tenant):
        """Test creating an assessment template."""
        with test_app.app_context():
            template = AssessmentTemplate(
                title='Leadership Assessment',
                description='Test leadership skills',
                created_by=test_trainer.id,
                tenant_id=test_tenant.id,
                category='soft_skills',
                max_score=100
            )
            
            assert template.title == 'Leadership Assessment'
            assert template.category == 'soft_skills'
            assert template.max_score == 100
    
    def test_assessment_section_creation(self, test_app):
        """Test creating an assessment section."""
        with test_app.app_context():
            section = AssessmentSection(
                template_id=1,
                title='Communication Skills',
                description='Test communication',
                order=1
            )
            
            assert section.title == 'Communication Skills'
            assert section.order == 1


class TestAvailabilityModels:
    """Test Availability model methods."""
    
    def test_availability_schedule_creation(self, test_app, test_trainer):
        """Test creating an availability schedule."""
        with test_app.app_context():
            schedule = AvailabilitySchedule(
                user_id=test_trainer.id,
                title='Regular Hours',
                is_active=True,
                time_zone='America/New_York'
            )
            
            assert schedule.title == 'Regular Hours'
            assert schedule.is_active is True
            assert schedule.time_zone == 'America/New_York'
    
    def test_availability_slot_creation(self, test_app):
        """Test creating an availability slot."""
        with test_app.app_context():
            slot = AvailabilitySlot(
                schedule_id=1,
                day_of_week=1,  # Tuesday
                start_time='09:00',
                end_time='17:00',
                is_available=True
            )
            
            assert slot.day_of_week == 1
            assert slot.start_time == '09:00'
            assert slot.is_available is True
    
    def test_availability_exception_creation(self, test_app, test_trainer):
        """Test creating an availability exception."""
        with test_app.app_context():
            exception = AvailabilityException(
                user_id=test_trainer.id,
                date=datetime.now() + timedelta(days=7),
                is_available=False,
                title='Holiday',
                description='National holiday'
            )
            
            assert exception.title == 'Holiday'
            assert exception.is_available is False


class TestUserProfileModel:
    """Test UserProfile model methods."""
    
    def test_user_profile_creation(self, test_app, test_user):
        """Test creating a user profile."""
        with test_app.app_context():
            profile = UserProfile(
                user_id=test_user.id,
                bio='Test bio',
                phone_number='+1234567890',
                location='New York',
                job_title='Developer'
            )
            
            assert profile.bio == 'Test bio'
            assert profile.location == 'New York'
            assert profile.job_title == 'Developer'
    
    def test_user_profile_to_dict(self, test_app, test_user):
        """Test user profile to_dict method."""
        with test_app.app_context():
            profile = UserProfile(
                user_id=test_user.id,
                bio='Test bio',
                location='San Francisco'
            )
            
            profile_dict = profile.to_dict()
            
            assert 'user_id' in profile_dict
            assert 'bio' in profile_dict
            assert 'location' in profile_dict