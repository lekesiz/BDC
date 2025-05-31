"""Test service classes to increase coverage."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db


class TestServicesCoverage:
    """Test various service classes."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        """Set up test environment."""
        self.app = test_app
    
    def test_user_service(self):
        """Test UserService methods."""
        with self.app.app_context():
            from app.services.user_service import UserService
            from app.models.user import User
            from app.models.tenant import Tenant
            
            # Create test tenant
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            db.session.flush()
            
            # Test create_user
            service = UserService()
            user_data = {
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'Test123!',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'student',
                'tenant_id': tenant.id
            }
            
            user = service.create_user(user_data)
            assert user is not None
            assert user.email == 'test@example.com'
            
            # Test get_user_by_email
            found_user = service.get_user_by_email('test@example.com')
            assert found_user is not None
            assert found_user.id == user.id
            
            # Test update_user
            updated = service.update_user(user.id, {'first_name': 'Updated'})
            assert updated.first_name == 'Updated'
            
            # Test get_users_by_tenant
            users = service.get_users_by_tenant(tenant.id)
            assert len(users) >= 1
    
    def test_beneficiary_service(self):
        """Test BeneficiaryService methods."""
        with self.app.app_context():
            from app.services.beneficiary_service import BeneficiaryService
            from app.models.user import User
            from app.models.tenant import Tenant
            from app.models.beneficiary import Beneficiary
            
            # Create test data
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            
            user = User(
                email='ben@test.com',
                username='benuser',
                first_name='Ben',
                last_name='User',
                role='student',
                tenant_id=tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            # Test create_beneficiary
            service = BeneficiaryService()
            ben_data = {
                'user_id': user.id,
                'tenant_id': tenant.id,
                'phone': '+1234567890',
                'birth_date': '1990-01-01',
                'status': 'active'
            }
            
            beneficiary = service.create_beneficiary(ben_data)
            assert beneficiary is not None
            assert beneficiary.user_id == user.id
            
            # Test get_beneficiary_by_user_id
            found = service.get_beneficiary_by_user_id(user.id)
            assert found is not None
            assert found.id == beneficiary.id
            
            # Test get_beneficiaries_by_tenant
            beneficiaries = service.get_beneficiaries_by_tenant(tenant.id)
            assert len(beneficiaries) >= 1
    
    def test_program_service(self):
        """Test ProgramService methods."""
        with self.app.app_context():
            from app.services.program_service import ProgramService
            from app.models.user import User
            from app.models.tenant import Tenant
            from app.models.program import Program
            
            # Create test data
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            
            user = User(
                email='admin@test.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role='super_admin',
                tenant_id=tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            # Test create_program
            service = ProgramService()
            program_data = {
                'name': 'Test Program',
                'description': 'Test Description',
                'tenant_id': tenant.id,
                'created_by_id': user.id,
                'duration': 30,
                'status': 'active'
            }
            
            program = service.create_program(program_data)
            assert program is not None
            assert program.name == 'Test Program'
            
            # Test get_active_programs
            programs = service.get_active_programs()
            assert len(programs) >= 1
            
            # Test get_programs_by_tenant
            tenant_programs = service.get_programs_by_tenant(tenant.id)
            assert len(tenant_programs) >= 1
    
    def test_notification_service(self):
        """Test NotificationService methods."""
        with self.app.app_context():
            from app.services.notification_service import NotificationService
            from app.models.user import User
            from app.models.tenant import Tenant
            
            # Create test data
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            
            user = User(
                email='user@test.com',
                username='user',
                first_name='User',
                last_name='Test',
                role='student',
                tenant_id=tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            # Test create_notification
            service = NotificationService()
            notif = service.create_notification(
                user_id=user.id,
                title='Test Notification',
                message='Test message',
                type='info'
            )
            assert notif is not None
            assert notif.title == 'Test Notification'
            
            # Test get_user_notifications
            notifications = service.get_user_notifications(user.id)
            assert len(notifications) >= 1
            
            # Test mark_as_read
            service.mark_as_read(notif.id)
            updated = service.get_notification_by_id(notif.id)
            assert updated.read is True
            
            # Test get_unread_count
            count = service.get_unread_count(user.id)
            assert isinstance(count, int)
    
    def test_document_service(self):
        """Test DocumentService methods."""
        with self.app.app_context():
            from app.services.document_service import DocumentService
            from app.models.user import User
            from app.models.tenant import Tenant
            
            # Create test data
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            
            user = User(
                email='user@test.com',
                username='user',
                first_name='User',
                last_name='Test',
                role='trainer',
                tenant_id=tenant.id
            )
            user.password = 'Test123!'
            db.session.add(user)
            db.session.flush()
            
            # Test create_document
            service = DocumentService()
            doc_data = {
                'title': 'Test Document',
                'filename': 'test.pdf',
                'file_path': '/uploads/test.pdf',
                'file_size': 1024,
                'mime_type': 'application/pdf',
                'uploaded_by_id': user.id,
                'tenant_id': tenant.id
            }
            
            doc = service.create_document(doc_data)
            assert doc is not None
            assert doc.title == 'Test Document'
            
            # Test get_document_by_id
            found = service.get_document_by_id(doc.id)
            assert found is not None
            assert found.id == doc.id
            
            # Test get_user_documents
            docs = service.get_user_documents(user.id)
            assert len(docs) >= 1
    
    def test_appointment_service(self):
        """Test AppointmentService methods."""
        with self.app.app_context():
            from app.services.appointment_service import AppointmentService
            from app.models.user import User
            from app.models.tenant import Tenant
            from app.models.beneficiary import Beneficiary
            
            # Create test data
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            
            trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=tenant.id
            )
            trainer.password = 'Test123!'
            db.session.add(trainer)
            
            student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=tenant.id
            )
            student.password = 'Test123!'
            db.session.add(student)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=student.id,
                tenant_id=tenant.id,
                status='active'
            )
            db.session.add(beneficiary)
            db.session.flush()
            
            # Test create_appointment
            service = AppointmentService()
            apt_data = {
                'title': 'Test Meeting',
                'trainer_id': trainer.id,
                'beneficiary_id': beneficiary.id,
                'start_time': datetime.now() + timedelta(days=1),
                'end_time': datetime.now() + timedelta(days=1, hours=1),
                'status': 'scheduled',
                'tenant_id': tenant.id
            }
            
            appointment = service.create_appointment(apt_data)
            assert appointment is not None
            assert appointment.title == 'Test Meeting'
            
            # Test get_trainer_appointments
            appointments = service.get_trainer_appointments(trainer.id)
            assert len(appointments) >= 1
            
            # Test get_beneficiary_appointments
            ben_apts = service.get_beneficiary_appointments(beneficiary.id)
            assert len(ben_apts) >= 1
    
    def test_evaluation_service(self):
        """Test evaluation service methods."""
        with self.app.app_context():
            from app.services.evaluation_service import EvaluationService
            from app.models.user import User
            from app.models.tenant import Tenant
            from app.models.beneficiary import Beneficiary
            from app.models.test import Test
            
            # Create test data
            tenant = Tenant(name='Test', slug='test', email='test@test.com')
            db.session.add(tenant)
            
            trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=tenant.id
            )
            trainer.password = 'Test123!'
            db.session.add(trainer)
            
            student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=tenant.id
            )
            student.password = 'Test123!'
            db.session.add(student)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=student.id,
                tenant_id=tenant.id,
                status='active'
            )
            db.session.add(beneficiary)
            
            test = Test(
                title='Test Assessment',
                type='assessment',
                tenant_id=tenant.id,
                created_by=trainer.id
            )
            db.session.add(test)
            db.session.flush()
            
            # Test create_evaluation
            service = EvaluationService()
            eval_data = {
                'beneficiary_id': beneficiary.id,
                'test_id': test.id,
                'trainer_id': trainer.id,
                'tenant_id': tenant.id,
                'status': 'in_progress'
            }
            
            evaluation = service.create_evaluation(eval_data)
            assert evaluation is not None
            assert evaluation.beneficiary_id == beneficiary.id
            
            # Test get_evaluation_by_id
            found = service.get_evaluation_by_id(evaluation.id)
            assert found is not None
            assert found.id == evaluation.id
            
            # Test update_evaluation_status
            service.update_evaluation_status(evaluation.id, 'completed')
            updated = service.get_evaluation_by_id(evaluation.id)
            assert updated.status == 'completed'
    
    @patch('app.services.ai_service.OpenAI')
    def test_ai_service(self, mock_openai):
        """Test AI service methods."""
        with self.app.app_context():
            from app.services.ai_service import AIService
            
            # Mock OpenAI response
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content='AI response'))]
            mock_client.chat.completions.create.return_value = mock_response
            
            # Test generate_feedback
            service = AIService()
            result = service.generate_feedback(
                responses=['Answer 1', 'Answer 2'],
                questions=['Question 1', 'Question 2']
            )
            assert result is not None
            
            # Test analyze_performance
            result = service.analyze_performance({
                'score': 85,
                'completion_time': 30,
                'correct_answers': 17,
                'total_questions': 20
            })
            assert result is not None
    
    def test_storage_service(self):
        """Test storage service methods."""
        with self.app.app_context():
            from app.services.storage_service import StorageService
            import tempfile
            import os
            
            # Test upload_file
            service = StorageService()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(b'Test content')
                tmp_path = tmp.name
            
            try:
                # Mock file object
                mock_file = MagicMock()
                mock_file.filename = 'test.txt'
                mock_file.save = MagicMock()
                
                result = service.save_file(mock_file, 'documents')
                assert result is not None
                assert 'path' in result
                assert 'filename' in result
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_cache_service(self):
        """Test cache service methods."""
        with self.app.app_context():
            from app.utils.cache import cache_key_wrapper, get_cache, set_cache, delete_cache
            
            # Test cache operations
            key = 'test_key'
            value = {'data': 'test_value'}
            
            # Test set_cache
            set_cache(key, value, timeout=60)
            
            # Test get_cache
            retrieved = get_cache(key)
            assert retrieved == value
            
            # Test delete_cache
            delete_cache(key)
            assert get_cache(key) is None
            
            # Test cache_key_wrapper
            wrapped_key = cache_key_wrapper('prefix', 'suffix')
            assert 'prefix' in wrapped_key
            assert 'suffix' in wrapped_key