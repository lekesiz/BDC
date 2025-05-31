"""Test model methods to increase coverage."""
import pytest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.beneficiary import Beneficiary
from app.models.program import Program, ProgramModule, ProgramEnrollment
from app.models.evaluation import Evaluation
from app.models.document import Document
from app.models.appointment import Appointment
from app.models.test import Test, TestSet, Question, TestSession, Response
from app.models.notification import Notification
from app.models.folder import Folder
from app.models.activity import Activity


class TestModelsCoverage:
    """Test model methods and properties."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        """Set up test environment."""
        self.app = test_app
        
        with test_app.app_context():
            # Create base test data
            self.tenant = Tenant(
                name='Test Tenant',
                slug='test-tenant',
                email='tenant@test.com',
                is_active=True
            )
            db.session.add(self.tenant)
            db.session.commit()
    
    def test_user_model_methods(self):
        """Test User model methods."""
        with self.app.app_context():
            user = User(
                email='test@example.com',
                username='testuser',
                first_name='Test',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id,
                is_active=True
            )
            
            # Test password setter and verification
            user.password = 'TestPassword123!'
            assert user.verify_password('TestPassword123!')
            assert not user.verify_password('WrongPassword')
            
            # Test full_name property
            assert user.full_name == 'Test User'
            
            # Test to_dict method
            user_dict = user.to_dict()
            assert user_dict['email'] == 'test@example.com'
            assert user_dict['role'] == 'trainer'
            assert 'password' not in user_dict
            
            # Test has_role method
            assert user.has_role('trainer')
            assert not user.has_role('admin')
            
            db.session.add(user)
            db.session.commit()
    
    def test_tenant_model_methods(self):
        """Test Tenant model methods."""
        with self.app.app_context():
            tenant = Tenant(
                name='New Tenant',
                slug='new-tenant',
                email='new@tenant.com',
                phone='+1234567890',
                address='123 Test St',
                settings={'theme': 'dark'},
                is_active=True
            )
            
            # Test to_dict method
            tenant_dict = tenant.to_dict()
            assert tenant_dict['name'] == 'New Tenant'
            assert tenant_dict['slug'] == 'new-tenant'
            assert tenant_dict['is_active'] is True
            
            db.session.add(tenant)
            db.session.commit()
    
    def test_beneficiary_model_methods(self):
        """Test Beneficiary model methods."""
        with self.app.app_context():
            # Create user for beneficiary
            user = User(
                email='ben@test.com',
                username='benuser',
                first_name='Ben',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=user.id,
                tenant_id=self.tenant.id,
                phone='+9876543210',
                birth_date=datetime(1990, 5, 15),
                gender='male',
                address='456 Test Ave',
                city='Test City',
                country='Test Country',
                emergency_contact='Emergency Person',
                emergency_phone='+1111111111',
                status='active',
                enrollment_date=datetime.now()
            )
            
            # Test to_dict method
            ben_dict = beneficiary.to_dict()
            assert ben_dict['phone'] == '+9876543210'
            assert ben_dict['status'] == 'active'
            assert 'user' in ben_dict
            
            # Test age calculation
            if hasattr(beneficiary, 'age'):
                assert isinstance(beneficiary.age, int)
            
            db.session.add(beneficiary)
            db.session.commit()
    
    def test_program_model_methods(self):
        """Test Program model methods."""
        with self.app.app_context():
            # Create user
            user = User(
                email='creator@test.com',
                username='creator',
                first_name='Creator',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            program = Program(
                name='Test Program',
                code='TST101',
                description='Test program description',
                objectives='Learn testing',
                prerequisites='Basic knowledge',
                duration=30,
                level='beginner',
                category='technical',
                max_participants=20,
                min_participants=5,
                price=1000.0,
                status='active',
                tenant_id=self.tenant.id,
                created_by_id=user.id,
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=30)).date()
            )
            
            # Test to_dict method
            program_dict = program.to_dict()
            assert program_dict['name'] == 'Test Program'
            assert program_dict['duration'] == 30
            assert program_dict['status'] == 'active'
            
            # Test duration_in_weeks property
            if hasattr(program, 'duration_in_weeks'):
                assert program.duration_in_weeks > 0
            
            db.session.add(program)
            db.session.commit()
    
    def test_evaluation_model_methods(self):
        """Test Evaluation model methods."""
        with self.app.app_context():
            # Create required objects
            trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            trainer.password = 'Test123!'
            db.session.add(trainer)
            
            student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id
            )
            student.password = 'Test123!'
            db.session.add(student)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=student.id,
                tenant_id=self.tenant.id,
                status='active'
            )
            db.session.add(beneficiary)
            
            test = Test(
                title='Test Assessment',
                type='assessment',
                tenant_id=self.tenant.id,
                created_by=trainer.id
            )
            db.session.add(test)
            db.session.flush()
            
            evaluation = Evaluation(
                beneficiary_id=beneficiary.id,
                test_id=test.id,
                trainer_id=trainer.id,
                tenant_id=self.tenant.id,
                score=85.5,
                feedback='Good performance',
                strengths='Strong analytical skills',
                weaknesses='Time management',
                recommendations='Practice more',
                status='completed',
                completed_at=datetime.now()
            )
            
            # Test to_dict method
            eval_dict = evaluation.to_dict()
            assert eval_dict['score'] == 85.5
            assert eval_dict['status'] == 'completed'
            assert eval_dict['feedback'] == 'Good performance'
            
            # Test calculate_score method
            evaluation.responses = [
                {'is_correct': True},
                {'is_correct': True},
                {'is_correct': False},
                {'is_correct': True}
            ]
            score = evaluation.calculate_score()
            assert score == 75.0
            
            # Test complete method
            evaluation.status = 'in_progress'
            evaluation.complete()
            assert evaluation.status == 'completed'
            assert evaluation.completed_at is not None
            
            # Test review method
            evaluation.review()
            assert evaluation.status == 'reviewed'
            assert evaluation.reviewed_at is not None
            
            db.session.add(evaluation)
            db.session.commit()
    
    def test_document_model_methods(self):
        """Test Document model methods."""
        with self.app.app_context():
            user = User(
                email='uploader@test.com',
                username='uploader',
                first_name='Uploader',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            document = Document(
                title='Test Document',
                description='Test document description',
                filename='test_file.pdf',
                file_path='/uploads/test_file.pdf',
                file_size=2048576,  # 2MB
                mime_type='application/pdf',
                document_type='manual',
                category='training',
                tags=['test', 'document'],
                version='1.0',
                uploaded_by_id=user.id,
                tenant_id=self.tenant.id,
                is_public=False,
                access_level='internal'
            )
            
            # Test to_dict method
            doc_dict = document.to_dict()
            assert doc_dict['title'] == 'Test Document'
            assert doc_dict['file_size'] == 2048576
            assert 'tags' in doc_dict
            
            # Test file_size_human property
            if hasattr(document, 'file_size_human'):
                assert '2' in document.file_size_human  # Should show ~2MB
            
            db.session.add(document)
            db.session.commit()
    
    def test_appointment_model_methods(self):
        """Test Appointment model methods."""
        with self.app.app_context():
            trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            trainer.password = 'Test123!'
            db.session.add(trainer)
            
            student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id
            )
            student.password = 'Test123!'
            db.session.add(student)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=student.id,
                tenant_id=self.tenant.id,
                status='active'
            )
            db.session.add(beneficiary)
            db.session.flush()
            
            appointment = Appointment(
                title='Training Session',
                description='One-on-one training',
                trainer_id=trainer.id,
                beneficiary_id=beneficiary.id,
                start_time=datetime.now() + timedelta(hours=1),
                end_time=datetime.now() + timedelta(hours=2),
                appointment_type='training',
                status='scheduled',
                location='Room 101',
                meeting_link='https://meet.example.com/abc123',
                tenant_id=self.tenant.id,
                notes='Bring laptop'
            )
            
            # Test to_dict method
            apt_dict = appointment.to_dict()
            assert apt_dict['title'] == 'Training Session'
            assert apt_dict['status'] == 'scheduled'
            assert apt_dict['appointment_type'] == 'training'
            
            # Test duration property
            if hasattr(appointment, 'duration'):
                assert appointment.duration == 60  # 1 hour in minutes
            
            db.session.add(appointment)
            db.session.commit()
    
    def test_test_model_methods(self):
        """Test Test and TestSet model methods."""
        with self.app.app_context():
            user = User(
                email='creator@test.com',
                username='creator',
                first_name='Creator',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            # Test Test model
            test = Test(
                title='Knowledge Test',
                description='Test your knowledge',
                type='quiz',
                category='general',
                duration=30,
                passing_score=70.0,
                total_points=100.0,
                status='published',
                is_active=True,
                tenant_id=self.tenant.id,
                created_by=user.id
            )
            
            test_dict = test.to_dict()
            assert test_dict['title'] == 'Knowledge Test'
            assert test_dict['passing_score'] == 70.0
            
            db.session.add(test)
            
            # Test TestSet model
            test_set = TestSet(
                title='Assessment Set',
                description='Complete assessment',
                instructions='Answer all questions',
                type='assessment',
                category='technical',
                time_limit=60,
                passing_score=75.0,
                is_randomized=True,
                allow_resume=True,
                max_attempts=3,
                show_results=True,
                status='active',
                tenant_id=self.tenant.id,
                creator_id=user.id
            )
            
            test_set_dict = test_set.to_dict()
            assert test_set_dict['title'] == 'Assessment Set'
            assert test_set_dict['is_randomized'] is True
            
            db.session.add(test_set)
            db.session.flush()
            
            # Test Question model
            question = Question(
                test_set_id=test_set.id,
                text='What is 2 + 2?',
                type='multiple_choice',
                options=['2', '3', '4', '5'],
                correct_answer='4',
                explanation='Basic addition',
                category='math',
                difficulty='easy',
                points=5.0,
                order=1
            )
            
            question_dict = question.to_dict()
            assert question_dict['text'] == 'What is 2 + 2?'
            assert question_dict['points'] == 5.0
            
            # Test check_answer method
            assert question.check_answer('4') is True
            assert question.check_answer('3') is False
            
            db.session.add(question)
            db.session.commit()
    
    def test_notification_model_methods(self):
        """Test Notification model methods."""
        with self.app.app_context():
            user = User(
                email='user@test.com',
                username='user',
                first_name='User',
                last_name='Test',
                role='student',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            notification = Notification(
                user_id=user.id,
                title='Important Notice',
                message='Please check your schedule',
                type='warning',
                priority='high',
                category='schedule',
                data={'appointment_id': 123},
                read=False,
                read_at=None
            )
            
            # Test to_dict method
            notif_dict = notification.to_dict()
            assert notif_dict['title'] == 'Important Notice'
            assert notif_dict['type'] == 'warning'
            assert notif_dict['read'] is False
            
            # Test mark_as_read method
            if hasattr(notification, 'mark_as_read'):
                notification.mark_as_read()
                assert notification.read is True
                assert notification.read_at is not None
            
            db.session.add(notification)
            db.session.commit()
    
    def test_activity_model_methods(self):
        """Test Activity model methods."""
        with self.app.app_context():
            user = User(
                email='active@test.com',
                username='active',
                first_name='Active',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            activity = Activity(
                user_id=user.id,
                action='login',
                resource_type='auth',
                resource_id=user.id,
                details={'ip': '127.0.0.1', 'user_agent': 'TestBrowser'},
                ip_address='127.0.0.1',
                user_agent='TestBrowser/1.0'
            )
            
            # Test to_dict method
            activity_dict = activity.to_dict()
            assert activity_dict['action'] == 'login'
            assert activity_dict['resource_type'] == 'auth'
            assert activity_dict['ip_address'] == '127.0.0.1'
            
            db.session.add(activity)
            db.session.commit()
    
    def test_folder_model_methods(self):
        """Test Folder model methods."""
        with self.app.app_context():
            user = User(
                email='folder@test.com',
                username='folder',
                first_name='Folder',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            # Create parent folder
            parent_folder = Folder(
                name='Parent Folder',
                description='Main folder',
                tenant_id=self.tenant.id,
                created_by_id=user.id
            )
            db.session.add(parent_folder)
            db.session.flush()
            
            # Create child folder
            child_folder = Folder(
                name='Child Folder',
                description='Sub folder',
                parent_id=parent_folder.id,
                tenant_id=self.tenant.id,
                created_by_id=user.id
            )
            
            # Test to_dict method
            folder_dict = child_folder.to_dict()
            assert folder_dict['name'] == 'Child Folder'
            assert folder_dict['parent_id'] == parent_folder.id
            
            # Test path property
            if hasattr(child_folder, 'path'):
                db.session.add(child_folder)
                db.session.flush()
                assert 'Parent Folder' in child_folder.path
                assert 'Child Folder' in child_folder.path
            
            db.session.commit()