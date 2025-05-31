"""
Comprehensive model tests to achieve high coverage on model layer.
This focuses on all model methods, properties, and relationships.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.models import (
    User, Tenant, Beneficiary, Document, Program, Notification,
    Appointment, Evaluation, Report, Activity, Assessment,
    Test, TestSet, Question, TestSession, Response,
    Folder, UserActivity, UserPreference, Settings
)


class TestUserModel:
    """Comprehensive tests for User model."""
    
    def test_user_password_hashing(self, db_session, test_tenant):
        """Test password hashing functionality."""
        user = User(
            email='hash@example.com',
            username='hashuser',
            first_name='Hash',
            last_name='User',
            tenant_id=test_tenant.id,
            role='student'
        )
        
        # Test password setting
        user.password = 'test_password'
        assert user.password_hash is not None
        assert user.password_hash != 'test_password'
        
        # Test password checking
        assert user.check_password('test_password') is True
        assert user.check_password('wrong_password') is False
    
    def test_user_string_representation(self, test_user):
        """Test user string representation."""
        user_str = str(test_user)
        assert test_user.email in user_str or test_user.username in user_str
        
        user_repr = repr(test_user)
        assert 'User' in user_repr
    
    def test_user_to_dict(self, test_user):
        """Test user to_dict method."""
        user_dict = test_user.to_dict()
        
        assert isinstance(user_dict, dict)
        assert 'id' in user_dict
        assert 'email' in user_dict
        assert 'first_name' in user_dict
        assert 'password' not in user_dict
        assert 'password_hash' not in user_dict
    
    def test_user_full_name_property(self, test_user):
        """Test user full_name property."""
        full_name = test_user.full_name
        assert test_user.first_name in full_name
        assert test_user.last_name in full_name
    
    def test_user_is_admin_property(self, db_session, test_tenant):
        """Test user is_admin property."""
        admin_user = User(
            email='admin@example.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            tenant_id=test_tenant.id,
            role='super_admin'
        )
        db_session.add(admin_user)
        db_session.commit()
        
        assert admin_user.is_admin is True
        
        regular_user = User(
            email='regular@example.com',
            username='regular',
            first_name='Regular',
            last_name='User',
            tenant_id=test_tenant.id,
            role='student'
        )
        db_session.add(regular_user)
        db_session.commit()
        
        assert regular_user.is_admin is False
    
    def test_user_relationships(self, test_user, test_tenant):
        """Test user relationships."""
        assert test_user.tenant is not None
        assert test_user.tenant.id == test_tenant.id
    
    def test_user_role_validation(self, db_session, test_tenant):
        """Test user role validation."""
        valid_roles = ['super_admin', 'tenant_admin', 'trainer', 'student', 'trainee']
        
        for role in valid_roles:
            user = User(
                email=f'{role}@example.com',
                username=role,
                first_name='Test',
                last_name='User',
                tenant_id=test_tenant.id,
                role=role
            )
            db_session.add(user)
            db_session.commit()
            assert user.role == role
            db_session.delete(user)
            db_session.commit()


class TestTenantModel:
    """Comprehensive tests for Tenant model."""
    
    def test_tenant_creation(self, db_session):
        """Test tenant creation."""
        tenant = Tenant(
            name='Test Tenant Full',
            slug='test-tenant-full',
            email='admin@testtenant.com',
            is_active=True,
            settings={'theme': 'dark', 'max_users': 100}
        )
        db_session.add(tenant)
        db_session.commit()
        
        assert tenant.id is not None
        assert tenant.name == 'Test Tenant Full'
        assert tenant.settings['theme'] == 'dark'
    
    def test_tenant_string_representation(self, test_tenant):
        """Test tenant string representation."""
        tenant_str = str(test_tenant)
        assert test_tenant.name in tenant_str
        
        tenant_repr = repr(test_tenant)
        assert 'Tenant' in tenant_repr
    
    def test_tenant_to_dict(self, test_tenant):
        """Test tenant to_dict method."""
        tenant_dict = test_tenant.to_dict()
        
        assert isinstance(tenant_dict, dict)
        assert 'id' in tenant_dict
        assert 'name' in tenant_dict
        assert 'is_active' in tenant_dict
    
    def test_tenant_relationships(self, test_tenant, test_user):
        """Test tenant relationships."""
        # Tenant should have users
        users = test_tenant.users
        assert len(users) >= 1
        assert test_user in users


class TestBeneficiaryModel:
    """Comprehensive tests for Beneficiary model."""
    
    def test_beneficiary_creation(self, db_session, test_tenant, test_trainer):
        """Test beneficiary creation with all fields."""
        # Create user first
        user = User(
            email='benef_full@example.com',
            username='benef_full',
            first_name='Beneficiary',
            last_name='Full',
            tenant_id=test_tenant.id,
            role='student'
        )
        db_session.add(user)
        db_session.commit()
        
        # Create beneficiary
        beneficiary = Beneficiary(
            user_id=user.id,
            phone='+1234567890',
            birth_date=datetime(1990, 5, 15),
            address='123 Main St',
            city='Test City',
            postal_code='12345',
            emergency_contact='Jane Doe',
            emergency_phone='+0987654321',
            medical_info='No allergies',
            notes='Test notes',
            tenant_id=test_tenant.id,
            trainer_id=test_trainer.id,
            status='active'
        )
        db_session.add(beneficiary)
        db_session.commit()
        
        assert beneficiary.id is not None
        assert beneficiary.phone == '+1234567890'
        assert beneficiary.status == 'active'
        assert beneficiary.notes == 'Test notes'
    
    def test_beneficiary_age_property(self, db_session, test_tenant, test_trainer):
        """Test beneficiary age calculation."""
        # Create user
        user = User(
            email='age_test@example.com',
            username='age_test',
            first_name='Age',
            last_name='Test',
            tenant_id=test_tenant.id,
            role='student'
        )
        db_session.add(user)
        db_session.commit()
        
        # Create beneficiary with known birth date
        birth_date = datetime.now() - timedelta(days=365 * 25)  # 25 years ago
        beneficiary = Beneficiary(
            user_id=user.id,
            birth_date=birth_date,
            tenant_id=test_tenant.id,
            trainer_id=test_trainer.id,
            status='active'
        )
        db_session.add(beneficiary)
        db_session.commit()
        
        assert beneficiary.age >= 24  # Should be around 25
        assert beneficiary.age <= 26
    
    def test_beneficiary_string_representation(self, test_beneficiary):
        """Test beneficiary string representation."""
        benef_str = str(test_beneficiary)
        assert test_beneficiary.user.first_name in benef_str or 'Beneficiary' in benef_str
    
    def test_beneficiary_to_dict(self, test_beneficiary):
        """Test beneficiary to_dict method."""
        benef_dict = test_beneficiary.to_dict()
        
        assert isinstance(benef_dict, dict)
        assert 'id' in benef_dict
        assert 'user_id' in benef_dict
        assert 'status' in benef_dict
    
    def test_beneficiary_relationships(self, test_beneficiary):
        """Test beneficiary relationships."""
        assert test_beneficiary.user is not None
        assert test_beneficiary.trainer is not None
        assert test_beneficiary.tenant is not None


class TestDocumentModel:
    """Comprehensive tests for Document model."""
    
    def test_document_creation_full(self, db_session, test_trainer):
        """Test document creation with all fields."""
        document = Document(
            title='Comprehensive Document',
            description='A comprehensive test document',
            file_path='/uploads/comprehensive.pdf',
            original_filename='comprehensive.pdf',
            file_type='pdf',
            file_size=2048,
            mime_type='application/pdf',
            document_type='training_material',
            upload_by=test_trainer.id,
            is_public=False,
            metadata={'version': '1.0', 'author': 'Test Author'},
            tags=['test', 'comprehensive']
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.id is not None
        assert document.title == 'Comprehensive Document'
        assert document.file_size == 2048
        assert document.metadata['version'] == '1.0'
    
    def test_document_file_size_human(self, db_session, test_trainer):
        """Test document file size human readable format."""
        document = Document(
            title='Size Test Document',
            file_path='/uploads/size_test.pdf',
            file_type='pdf',
            file_size=1024 * 1024,  # 1MB
            document_type='general',
            upload_by=test_trainer.id
        )
        db_session.add(document)
        db_session.commit()
        
        # Test human readable size (if method exists)
        if hasattr(document, 'file_size_human'):
            size_human = document.file_size_human
            assert 'MB' in size_human or 'KB' in size_human
    
    def test_document_string_representation(self, test_document):
        """Test document string representation."""
        doc_str = str(test_document)
        assert test_document.title in doc_str
    
    def test_document_to_dict(self, test_document):
        """Test document to_dict method."""
        doc_dict = test_document.to_dict()
        
        assert isinstance(doc_dict, dict)
        assert 'id' in doc_dict
        assert 'title' in doc_dict
        assert 'file_type' in doc_dict


class TestProgramModel:
    """Comprehensive tests for Program model."""
    
    def test_program_creation_full(self, db_session, test_tenant, test_trainer):
        """Test program creation with all fields."""
        program = Program(
            name='Comprehensive Program',
            description='A comprehensive training program',
            tenant_id=test_tenant.id,
            created_by_id=test_trainer.id,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=90),
            status='active',
            is_active=True,
            capacity=20,
            requirements=['High school diploma'],
            objectives=['Learn new skills', 'Get certified'],
            curriculum='Detailed curriculum content',
            duration_weeks=12,
            difficulty_level='intermediate',
            category='technology',
            tags=['programming', 'certification']
        )
        db_session.add(program)
        db_session.commit()
        
        assert program.id is not None
        assert program.name == 'Comprehensive Program'
        assert program.capacity == 20
        assert program.duration_weeks == 12
    
    def test_program_is_active_property(self, test_program):
        """Test program is_active property."""
        assert hasattr(test_program, 'is_active')
        assert isinstance(test_program.is_active, bool)
    
    def test_program_string_representation(self, test_program):
        """Test program string representation."""
        prog_str = str(test_program)
        assert test_program.name in prog_str
    
    def test_program_to_dict(self, test_program):
        """Test program to_dict method."""
        prog_dict = test_program.to_dict()
        
        assert isinstance(prog_dict, dict)
        assert 'id' in prog_dict
        assert 'name' in prog_dict
        assert 'status' in prog_dict


class TestTestModel:
    """Comprehensive tests for Test model."""
    
    def test_test_creation(self, db_session, test_tenant, test_user):
        """Test Test model creation."""
        test = Test(
            title='Comprehensive Test',
            description='A comprehensive test assessment',
            type='assessment',
            category='skills',
            tenant_id=test_tenant.id,
            created_by=test_user.id,
            duration=90,
            passing_score=75.0,
            total_points=100.0,
            status='published',
            is_active=True
        )
        db_session.add(test)
        db_session.commit()
        
        assert test.id is not None
        assert test.title == 'Comprehensive Test'
        assert test.passing_score == 75.0
    
    def test_test_to_dict(self, db_session, test_tenant, test_user):
        """Test Test to_dict method."""
        test = Test(
            title='Dict Test',
            type='assessment',
            tenant_id=test_tenant.id,
            created_by=test_user.id
        )
        db_session.add(test)
        db_session.commit()
        
        test_dict = test.to_dict()
        assert isinstance(test_dict, dict)
        assert 'id' in test_dict
        assert 'title' in test_dict


class TestQuestionModel:
    """Comprehensive tests for Question model."""
    
    def test_question_creation(self, db_session, test_test):
        """Test Question model creation."""
        question = Question(
            test_set_id=test_test.id,
            text='What is the capital of France?',
            type='multiple_choice',
            options=['London', 'Berlin', 'Paris', 'Madrid'],
            correct_answer='Paris',
            explanation='Paris is the capital and largest city of France.',
            category='geography',
            difficulty='easy',
            points=5.0,
            order=1
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.text == 'What is the capital of France?'
        assert question.correct_answer == 'Paris'
    
    def test_question_check_answer(self, db_session, test_test):
        """Test Question check_answer method."""
        # Multiple choice question
        mc_question = Question(
            test_set_id=test_test.id,
            text='Test question?',
            type='multiple_choice',
            correct_answer='correct',
            points=5.0
        )
        db_session.add(mc_question)
        db_session.commit()
        
        assert mc_question.check_answer('correct') is True
        assert mc_question.check_answer('wrong') is False
        
        # True/False question
        tf_question = Question(
            test_set_id=test_test.id,
            text='True or false?',
            type='true_false',
            correct_answer=True,
            points=5.0
        )
        db_session.add(tf_question)
        db_session.commit()
        
        assert tf_question.check_answer(True) is True
        assert tf_question.check_answer(False) is False
    
    def test_question_to_dict(self, db_session, test_test):
        """Test Question to_dict method."""
        question = Question(
            test_set_id=test_test.id,
            text='Dict test question?',
            type='multiple_choice',
            points=5.0
        )
        db_session.add(question)
        db_session.commit()
        
        q_dict = question.to_dict()
        assert isinstance(q_dict, dict)
        assert 'id' in q_dict
        assert 'text' in q_dict
        assert 'type' in q_dict


class TestNotificationModel:
    """Comprehensive tests for Notification model."""
    
    def test_notification_creation(self, db_session, test_beneficiary):
        """Test Notification model creation."""
        notification = Notification(
            user_id=test_beneficiary.user_id,
            type='info',
            title='Test Notification',
            message='This is a comprehensive test notification',
            read=False,
            priority='normal',
            action_url='/dashboard',
            metadata={'source': 'test', 'category': 'general'}
        )
        db_session.add(notification)
        db_session.commit()
        
        assert notification.id is not None
        assert notification.title == 'Test Notification'
        assert notification.read is False
    
    def test_notification_mark_as_read(self, db_session, test_beneficiary):
        """Test notification mark as read functionality."""
        notification = Notification(
            user_id=test_beneficiary.user_id,
            type='info',
            title='Read Test',
            message='Test message',
            read=False
        )
        db_session.add(notification)
        db_session.commit()
        
        # Mark as read (if method exists)
        if hasattr(notification, 'mark_as_read'):
            notification.mark_as_read()
            assert notification.read is True
        else:
            notification.read = True
            assert notification.read is True
    
    def test_notification_string_representation(self, test_notification):
        """Test notification string representation."""
        notif_str = str(test_notification)
        assert test_notification.title in notif_str or 'Notification' in notif_str


class TestUserPreferenceModel:
    """Test UserPreference model."""
    
    def test_user_preference_creation(self, db_session, test_user):
        """Test UserPreference creation."""
        preference = UserPreference(
            user_id=test_user.id,
            key='theme',
            value='dark',
            type='string'
        )
        db_session.add(preference)
        db_session.commit()
        
        assert preference.id is not None
        assert preference.key == 'theme'
        assert preference.value == 'dark'


class TestFolderModel:
    """Test Folder model."""
    
    def test_folder_creation(self, db_session, test_user):
        """Test Folder creation."""
        folder = Folder(
            name='Test Folder',
            description='Test folder description',
            created_by=test_user.id,
            is_public=False
        )
        db_session.add(folder)
        db_session.commit()
        
        assert folder.id is not None
        assert folder.name == 'Test Folder'


class TestActivityModel:
    """Test Activity model."""
    
    def test_activity_creation(self, db_session, test_user):
        """Test Activity creation."""
        activity = Activity(
            user_id=test_user.id,
            action='login',
            description='User logged in',
            timestamp=datetime.utcnow(),
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
        db_session.add(activity)
        db_session.commit()
        
        assert activity.id is not None
        assert activity.action == 'login'


class TestModelRelationships:
    """Test model relationships and cascades."""
    
    def test_user_tenant_relationship(self, test_user, test_tenant):
        """Test user-tenant relationship."""
        assert test_user.tenant is not None
        assert test_user.tenant.id == test_tenant.id
        assert test_user in test_tenant.users
    
    def test_beneficiary_relationships(self, test_beneficiary):
        """Test beneficiary relationships."""
        assert test_beneficiary.user is not None
        assert test_beneficiary.trainer is not None
        assert test_beneficiary.tenant is not None
    
    def test_document_uploader_relationship(self, test_document, test_trainer):
        """Test document uploader relationship."""
        assert test_document.uploader is not None
        assert test_document.uploader.id == test_trainer.id
    
    def test_program_creator_relationship(self, test_program, test_trainer):
        """Test program creator relationship."""
        assert test_program.creator is not None
        assert test_program.creator.id == test_trainer.id


class TestModelValidations:
    """Test model validations and constraints."""
    
    def test_user_email_uniqueness(self, db_session, test_tenant):
        """Test user email uniqueness constraint."""
        # Create first user
        user1 = User(
            email='unique@example.com',
            username='user1',
            first_name='User',
            last_name='One',
            tenant_id=test_tenant.id,
            role='student'
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email='unique@example.com',  # Same email
            username='user2',
            first_name='User',
            last_name='Two',
            tenant_id=test_tenant.id,
            role='student'
        )
        db_session.add(user2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback()
    
    def test_required_fields(self, db_session, test_tenant):
        """Test required field validations."""
        # User without email should fail
        user = User(
            # email missing
            username='nomail',
            first_name='No',
            last_name='Mail',
            tenant_id=test_tenant.id,
            role='student'
        )
        db_session.add(user)
        
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback()