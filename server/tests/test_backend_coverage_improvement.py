"""
Backend coverage improvement tests focusing on models and simple utilities.
"""
import pytest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Tenant, Beneficiary, Program, Document, Evaluation, Appointment
from app.utils.cache import generate_cache_key, invalidate_cache


class TestModelsCore:
    """Test core model functionality."""
    
    def test_user_model_basic(self, db_session):
        """Test basic user model operations."""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='staff'
        )
        user.password = 'password123'
        
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.full_name == 'Test User'
        assert check_password_hash(user.password_hash, 'password123')
        assert user.is_active is True
    
    def test_tenant_model_basic(self, db_session):
        """Test basic tenant model operations."""
        tenant = Tenant(
            name='Test Company',
            slug='test-company',
            email='info@testcompany.com'
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        assert tenant.id is not None
        assert tenant.is_active is True
        assert tenant.settings is not None
    
    def test_beneficiary_model_basic(self, db_session):
        """Test basic beneficiary model operations."""
        # Create tenant and user first
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        user = User(email='ben@example.com', first_name='Ben', last_name='User', role='beneficiary')
        user.password = 'test123'
        db.session.add_all([tenant, user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=user.id,
            tenant_id=tenant.id,
            gender='male',
            birth_date=datetime.utcnow() - timedelta(days=365*25),
            phone='+1234567890',
            city='Test City',
            country='Test Country'
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        assert beneficiary.id is not None
        assert beneficiary.first_name == 'Ben'
        assert beneficiary.last_name == 'User'
        assert beneficiary.age >= 24  # Approximately 25 years
    
    def test_program_model_basic(self, db_session):
        """Test basic program model operations."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='Creator', last_name='User', role='admin')
        creator.password = 'test123'
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Test Program',
            code='TST-001',
            description='A test program',
            duration=30,
            level='beginner'
        )
        
        db.session.add(program)
        db.session.commit()
        
        assert program.id is not None
        assert program.is_active is True
        assert program.duration == 30
    
    def test_document_model_basic(self, db_session):
        """Test basic document model operations."""
        uploader = User(email='uploader@example.com', first_name='Upload', last_name='User', role='staff')
        uploader.password = 'test123'
        db.session.add(uploader)
        db.session.commit()
        
        document = Document(
            title='Test Document',
            file_path='/uploads/test.pdf',
            file_type='pdf',
            file_size=1024,
            upload_by=uploader.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        assert document.id is not None
        assert document.is_active is True
        assert document.file_size == 1024
    
    def test_evaluation_model_basic(self, db_session):
        """Test basic evaluation model operations."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='Trainer', last_name='User', role='trainer')
        trainer.password = 'test123'
        ben_user = User(email='ben@example.com', first_name='Ben', last_name='User', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='female',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            score=85,
            feedback='Good progress',
            status='completed'
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        assert evaluation.id is not None
        assert evaluation.score == 85
        assert evaluation.status == 'completed'
    
    def test_appointment_model_basic(self, db_session):
        """Test basic appointment model operations."""
        trainer = User(email='trainer@example.com', first_name='Trainer', last_name='User', role='trainer')
        trainer.password = 'test123'
        ben_user = User(email='ben@example.com', first_name='Ben', last_name='User', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([trainer, ben_user])
        db.session.commit()
        
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        db.session.add(tenant)
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='male',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        appointment = Appointment(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            title='Training Session',
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=2),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        assert appointment.id is not None
        assert appointment.status == 'scheduled'
        # Calculate duration manually since it's not a model property
        duration = appointment.end_time - appointment.start_time
        assert duration.total_seconds() == 3600  # 1 hour


class TestUtilities:
    """Test utility functions."""
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = generate_cache_key('test', 'arg1', 'arg2')
        key2 = generate_cache_key('test', 'arg1', 'arg2')
        key3 = generate_cache_key('test', 'arg1', 'arg3')
        
        assert key1 == key2
        assert key1 != key3
        assert 'test' in key1
    
    def test_cache_key_with_kwargs(self):
        """Test cache key generation with kwargs."""
        key1 = generate_cache_key('test', page=1, limit=10)
        key2 = generate_cache_key('test', limit=10, page=1)
        key3 = generate_cache_key('test', page=2, limit=10)
        
        assert key1 == key2  # Order shouldn't matter
        assert key1 != key3
    


class TestModelRelationships:
    """Test model relationships."""
    
    def test_user_tenant_relationship(self, db_session):
        """Test user-tenant relationship."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        db.session.add(tenant)
        db.session.commit()
        
        user = User(
            email='user@example.com',
            first_name='Test',
            last_name='User',
            role='staff',
            tenant_id=tenant.id
        )
        user.password = 'test123'
        db.session.add(user)
        db.session.commit()
        
        assert user.tenant == tenant
        assert user in tenant.users
    
    def test_beneficiary_relationships(self, db_session):
        """Test beneficiary relationships."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        user = User(email='ben@example.com', first_name='Ben', last_name='User', role='beneficiary')
        user.password = 'test123'
        trainer = User(email='trainer@example.com', first_name='Trainer', last_name='User', role='trainer')
        trainer.password = 'test123'
        db.session.add_all([tenant, user, trainer])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=user.id,
            tenant_id=tenant.id,
            trainer_id=trainer.id,
            gender='female',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        assert beneficiary.user == user
        assert beneficiary.tenant == tenant
        assert beneficiary.trainer == trainer
    
    def test_evaluation_relationships(self, db_session):
        """Test evaluation relationships."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='Trainer', last_name='User', role='trainer')
        trainer.password = 'test123'
        ben_user = User(email='ben@example.com', first_name='Ben', last_name='User', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='male',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            score=90
        )
        db.session.add(evaluation)
        db.session.commit()
        
        assert evaluation.beneficiary == beneficiary
        assert evaluation.trainer == trainer
        assert evaluation.tenant == tenant
        assert evaluation in beneficiary.evaluations


class TestModelValidation:
    """Test model validation and constraints."""
    
    def test_user_unique_email(self, db_session):
        """Test user email uniqueness."""
        user1 = User(email='unique@example.com', first_name='User', last_name='One', role='staff')
        user1.password = 'test123'
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(email='unique@example.com', first_name='User', last_name='Two', role='staff')
        user2.password = 'test123'
        db.session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()
    
    def test_tenant_unique_slug(self, db_session):
        """Test tenant slug uniqueness."""
        tenant1 = Tenant(name='Company One', slug='unique-slug', email='one@example.com')
        db.session.add(tenant1)
        db.session.commit()
        
        tenant2 = Tenant(name='Company Two', slug='unique-slug', email='two@example.com')
        db.session.add(tenant2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()
    
    def test_required_fields(self, db_session):
        """Test required fields validation."""
        # User without email should fail
        user = User(first_name='Test', last_name='User', role='staff')
        user.password = 'test123'
        db.session.add(user)
        
        with pytest.raises(Exception):
            db.session.commit()


class TestModelMethods:
    """Test model methods and properties."""
    
    def test_user_methods(self, db_session):
        """Test user model methods."""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            role='staff'
        )
        user.password = 'secret123'
        db.session.add(user)
        db.session.commit()
        
        # Test full_name property
        assert user.full_name == 'John Doe'
        
        # Test password verification
        assert user.verify_password('secret123')
        assert not user.verify_password('wrong')
        
        # Test to_dict
        user_dict = user.to_dict()
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['role'] == 'staff'
        assert 'password_hash' not in user_dict
    
    def test_beneficiary_age_calculation(self, db_session):
        """Test beneficiary age calculation."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        user = User(email='ben@example.com', first_name='Ben', last_name='User', role='beneficiary')
        user.password = 'test123'
        db.session.add_all([tenant, user])
        db.session.commit()
        
        # Create beneficiary born 20 years ago
        birth_date = datetime.utcnow() - timedelta(days=365*20 + 5)  # Account for leap years
        beneficiary = Beneficiary(
            user_id=user.id,
            tenant_id=tenant.id,
            gender='male',
            birth_date=birth_date
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        assert beneficiary.age >= 19
        assert beneficiary.age <= 21  # Allow for calculation differences