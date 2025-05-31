import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app import create_app, db
from app.models import User


class MockUserService:
    """Simple mock user service for testing basic functionality."""
    
    def get_all_users(self):
        return User.query.all()
    
    def get_user_by_id(self, user_id):
        return User.query.get(user_id)
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()
    
    def create_user(self, **kwargs):
        try:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception:
            db.session.rollback()
            return None
    
    def update_user(self, user_id, **kwargs):
        user = User.query.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        try:
            db.session.commit()
            return user
        except Exception:
            db.session.rollback()
            return None
    
    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def get_users_by_role(self, role):
        return User.query.filter_by(role=role).all()
    
    def get_active_users(self):
        return User.query.filter_by(is_active=True).all()
    
    def update_password(self, user_id, new_password):
        user = User.query.get(user_id)
        if not user:
            return False
        
        user.password = new_password
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def toggle_user_status(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False
        
        user.is_active = not user.is_active
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def search_users(self, query):
        return User.query.filter(
            db.or_(
                User.email.contains(query),
                User.first_name.contains(query),
                User.last_name.contains(query)
            )
        ).all()
    
    def get_user_stats(self):
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        users_by_role = {}
        for role in ['admin', 'trainer', 'student']:
            count = User.query.filter_by(role=role).count()
            users_by_role[role] = count
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'users_by_role': users_by_role
        }
    
    def bulk_update_users(self, user_ids, **kwargs):
        updated_count = 0
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                updated_count += 1
        
        try:
            db.session.commit()
            return updated_count
        except Exception:
            db.session.rollback()
            return 0


class TestUserService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # Create test users
        self.admin_user = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        self.admin_user.password = 'password123'
        
        self.trainer_user = User(
            email='trainer@test.com',
            first_name='Trainer',
            last_name='User',
            role='trainer',
            is_active=True
        )
        self.trainer_user.password = 'password123'
        
        self.student_user = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student',
            is_active=True
        )
        self.student_user.password = 'password123'
        
        db.session.add_all([self.admin_user, self.trainer_user, self.student_user])
        db.session.commit()
        
        self.user_service = MockUserService()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_all_users(self):
        """Test getting all users"""
        users = self.user_service.get_all_users()
        
        assert len(users) >= 3
        emails = [u.email for u in users]
        assert 'admin@test.com' in emails
        assert 'trainer@test.com' in emails
        assert 'student@test.com' in emails
    
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        user = self.user_service.get_user_by_id(self.admin_user.id)
        
        assert user is not None
        assert user.email == 'admin@test.com'
        assert user.role == 'admin'
    
    def test_get_user_by_email(self):
        """Test getting user by email"""
        user = self.user_service.get_user_by_email('trainer@test.com')
        
        assert user is not None
        assert user.first_name == 'Trainer'
        assert user.role == 'trainer'
    
    def test_create_user(self):
        """Test creating a new user"""
        user_data = {
            'email': 'newuser@test.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        
        new_user = self.user_service.create_user(**user_data)
        
        assert new_user is not None
        assert new_user.email == 'newuser@test.com'
        assert new_user.first_name == 'New'
        
        # Verify user is in database
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None
    
    def test_update_user(self):
        """Test updating user information"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Admin',
            'phone': '+1234567890'
        }
        
        updated_user = self.user_service.update_user(self.admin_user.id, **update_data)
        
        assert updated_user is not None
        assert updated_user.first_name == 'Updated'
        assert updated_user.last_name == 'Admin'
        assert updated_user.phone == '+1234567890'
    
    def test_delete_user(self):
        """Test deleting a user"""
        # Create a user to delete
        user_to_delete = User(
            email='delete@test.com',
            first_name='Delete',
            last_name='Me',
            role='student',
            is_active=True
        )
        user_to_delete.password = 'password123'
        db.session.add(user_to_delete)
        db.session.commit()
        user_id = user_to_delete.id
        
        # Delete the user
        result = self.user_service.delete_user(user_id)
        
        assert result is True
        
        # Verify user is deleted
        user = User.query.get(user_id)
        assert user is None
    
    def test_get_users_by_role(self):
        """Test getting users by role"""
        trainers = self.user_service.get_users_by_role('trainer')
        
        assert len(trainers) >= 1
        assert all(u.role == 'trainer' for u in trainers)
        assert any(u.email == 'trainer@test.com' for u in trainers)
    
    def test_get_active_users(self):
        """Test getting active users"""
        active_users = self.user_service.get_active_users()
        
        assert all(u.is_active for u in active_users)
        assert len(active_users) >= 3
    
    def test_update_password(self):
        """Test updating user password"""
        result = self.user_service.update_password(self.student_user.id, 'newpassword123')
        
        assert result is True
        
        # Verify password was updated
        user = User.query.get(self.student_user.id)
        assert user.verify_password('newpassword123')
    
    def test_toggle_user_status(self):
        """Test toggling user active status"""
        # Initially active
        assert self.student_user.is_active is True
        
        # Toggle to inactive
        result = self.user_service.toggle_user_status(self.student_user.id)
        assert result is True
        
        user = User.query.get(self.student_user.id)
        assert user.is_active is False
    
    def test_search_users(self):
        """Test searching users"""
        # Search by email
        results = self.user_service.search_users('admin@test.com')
        assert len(results) == 1
        assert results[0].email == 'admin@test.com'
    
    def test_get_user_stats(self):
        """Test getting user statistics"""
        stats = self.user_service.get_user_stats()
        
        assert 'total_users' in stats
        assert 'active_users' in stats
        assert 'users_by_role' in stats
        assert stats['total_users'] >= 3
    
    def test_bulk_update_users(self):
        """Test bulk updating users"""
        user_ids = [self.trainer_user.id, self.student_user.id]
        update_data = {'is_active': False}
        
        result = self.user_service.bulk_update_users(user_ids, **update_data)
        
        assert result == 2  # Number of updated users
        
        # Verify users were updated
        trainer = User.query.get(self.trainer_user.id)
        student = User.query.get(self.student_user.id)
        assert trainer.is_active is False
        assert student.is_active is False