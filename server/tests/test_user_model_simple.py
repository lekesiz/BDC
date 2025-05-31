import pytest
from datetime import datetime, timezone
from werkzeug.security import check_password_hash

from app import create_app, db
from app.models import User, Tenant, TokenBlocklist


class TestUserModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test creating a user"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        user.password = 'password123'
        
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.role == 'student'
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_password_hashing(self):
        """Test password hashing"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        user.password = 'password123'
        
        # Password should be hashed
        assert user.password_hash is not None
        assert user.password_hash != 'password123'
        assert check_password_hash(user.password_hash, 'password123')
    
    def test_user_verify_password(self):
        """Test password verification"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        user.password = 'password123'
        
        assert user.verify_password('password123') is True
        assert user.verify_password('wrongpassword') is False
    
    def test_user_password_not_readable(self):
        """Test that password property cannot be read"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        user.password = 'password123'
        
        with pytest.raises(AttributeError):
            _ = user.password
    
    def test_user_full_name(self):
        """Test full name property"""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            role='student'
        )
        
        assert user.full_name == 'John Doe'
    
    def test_user_to_dict_basic(self):
        """Test converting user to dictionary without profile"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='trainer',
            username='testuser'
        )
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict(include_profile=False)
        
        assert user_dict['id'] == user.id
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['first_name'] == 'Test'
        assert user_dict['last_name'] == 'User'
        assert user_dict['full_name'] == 'Test User'
        assert user_dict['role'] == 'trainer'
        assert user_dict['username'] == 'testuser'
        assert user_dict['is_active'] is True
        assert 'password_hash' not in user_dict
        assert 'phone' not in user_dict  # Profile not included
    
    def test_user_to_dict_with_profile(self):
        """Test converting user to dictionary with profile"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='trainer',
            phone='+1234567890',
            bio='Test bio',
            city='Test City',
            country='Test Country'
        )
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict(include_profile=True)
        
        assert user_dict['phone'] == '+1234567890'
        assert user_dict['bio'] == 'Test bio'
        assert user_dict['city'] == 'Test City'
        assert user_dict['country'] == 'Test Country'
    
    def test_user_tenant_relationship(self):
        """Test user-tenant many-to-many relationship"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        user.password = 'password123'
        
        tenant1 = Tenant(name='Tenant 1', slug='tenant-1', email='tenant1@example.com')
        tenant2 = Tenant(name='Tenant 2', slug='tenant-2', email='tenant2@example.com')
        
        user.tenants.append(tenant1)
        user.tenants.append(tenant2)
        
        db.session.add_all([user, tenant1, tenant2])
        db.session.commit()
        
        assert len(user.tenants) == 2
        assert tenant1 in user.tenants
        assert tenant2 in user.tenants
        assert user in tenant1.users
        assert user in tenant2.users
    
    def test_user_string_representation(self):
        """Test string representation of user"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        
        assert str(user) == '<User test@example.com>'
    
    def test_user_default_values(self):
        """Test user default values"""
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        
        assert user.is_active is True
        assert user.email_notifications is True
        assert user.push_notifications is False
        assert user.sms_notifications is False
        assert user.language == 'en'
        assert user.theme == 'light'
    
    def test_user_role_constants(self):
        """Test user role constants"""
        from app.models.user import UserRole
        
        assert UserRole.SUPER_ADMIN == 'super_admin'
        assert UserRole.TENANT_ADMIN == 'tenant_admin'
        assert UserRole.TRAINER == 'trainer'
        assert UserRole.STUDENT == 'student'
        assert UserRole.TRAINEE == 'trainee'
        assert len(UserRole.ROLES) == 5


class TestTokenBlocklist:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test user
        self.user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='student'
        )
        self.user.password = 'password123'
        db.session.add(self.user)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_token_blocklist_creation(self):
        """Test creating a token blocklist entry"""
        token = TokenBlocklist(
            jti='test-jti-123',
            token_type='access',
            user_id=self.user.id,
            expires_at=datetime.utcnow()
        )
        
        db.session.add(token)
        db.session.commit()
        
        assert token.id is not None
        assert token.jti == 'test-jti-123'
        assert token.token_type == 'access'
        assert token.user_id == self.user.id
        assert token.revoked_at is not None
    
    def test_token_blocklist_to_dict(self):
        """Test converting token blocklist to dictionary"""
        expires = datetime.utcnow()
        token = TokenBlocklist(
            jti='test-jti-123',
            token_type='refresh',
            user_id=self.user.id,
            expires_at=expires
        )
        
        db.session.add(token)
        db.session.commit()
        
        token_dict = token.to_dict()
        
        assert token_dict['id'] == token.id
        assert token_dict['jti'] == 'test-jti-123'
        assert token_dict['token_type'] == 'refresh'
        assert token_dict['user_id'] == self.user.id
        assert 'revoked_at' in token_dict
        assert 'expires_at' in token_dict