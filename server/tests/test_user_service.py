import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Beneficiary
from app.services.user_service import UserService


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
        
        self.user_service = UserService()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_all_users(self):
        """Test getting all users"""
        users = self.user_service.get_all_users()
        
        assert len(users) >= 3  # At least our test users
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
    
    def test_get_user_by_id_not_found(self):
        """Test getting non-existent user"""
        user = self.user_service.get_user_by_id(999999)
        assert user is None
    
    def test_get_user_by_email(self):
        """Test getting user by email"""
        user = self.user_service.get_user_by_email('trainer@test.com')
        
        assert user is not None
        assert user.first_name == 'Trainer'
        assert user.role == 'trainer'
    
    def test_get_user_by_email_not_found(self):
        """Test getting user with non-existent email"""
        user = self.user_service.get_user_by_email('nonexistent@test.com')
        assert user is None
    
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
        assert new_user.verify_password('password123')
        
        # Verify user is in database
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None
    
    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email"""
        user_data = {
            'email': 'admin@test.com',  # Already exists
            'password': 'password123',
            'first_name': 'Duplicate',
            'last_name': 'User',
            'role': 'student'
        }
        
        new_user = self.user_service.create_user(**user_data)
        assert new_user is None
    
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
    
    def test_update_user_not_found(self):
        """Test updating non-existent user"""
        update_data = {'first_name': 'Updated'}
        
        updated_user = self.user_service.update_user(999999, **update_data)
        assert updated_user is None
    
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
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user"""
        result = self.user_service.delete_user(999999)
        assert result is False
    
    def test_get_users_by_role(self):
        """Test getting users by role"""
        trainers = self.user_service.get_users_by_role('trainer')
        
        assert len(trainers) >= 1
        assert all(u.role == 'trainer' for u in trainers)
        assert any(u.email == 'trainer@test.com' for u in trainers)
    
    def test_get_active_users(self):
        """Test getting active users"""
        # Create an inactive user
        inactive_user = User(
            email='inactive@test.com',
            first_name='Inactive',
            last_name='User',
            role='student',
            is_active=False
        )
        inactive_user.password = 'password123'
        db.session.add(inactive_user)
        db.session.commit()
        
        active_users = self.user_service.get_active_users()
        
        assert all(u.is_active for u in active_users)
        assert not any(u.email == 'inactive@test.com' for u in active_users)
    
    def test_update_password(self):
        """Test updating user password"""
        result = self.user_service.update_password(self.student_user.id, 'newpassword123')
        
        assert result is True
        
        # Verify password was updated
        user = User.query.get(self.student_user.id)
        assert user.verify_password('newpassword123')
        assert not user.verify_password('password123')
    
    def test_update_password_user_not_found(self):
        """Test updating password for non-existent user"""
        result = self.user_service.update_password(999999, 'newpassword123')
        assert result is False
    
    def test_toggle_user_status(self):
        """Test toggling user active status"""
        # Initially active
        assert self.student_user.is_active is True
        
        # Toggle to inactive
        result = self.user_service.toggle_user_status(self.student_user.id)
        assert result is True
        
        user = User.query.get(self.student_user.id)
        assert user.is_active is False
        
        # Toggle back to active
        result = self.user_service.toggle_user_status(self.student_user.id)
        assert result is True
        
        user = User.query.get(self.student_user.id)
        assert user.is_active is True
    
    def test_search_users(self):
        """Test searching users"""
        # Search by email
        results = self.user_service.search_users('admin@test.com')
        assert len(results) == 1
        assert results[0].email == 'admin@test.com'
        
        # Search by first name
        results = self.user_service.search_users('Trainer')
        assert len(results) >= 1
        assert any(u.first_name == 'Trainer' for u in results)
        
        # Search by last name
        results = self.user_service.search_users('User')
        assert len(results) >= 3  # All our test users have last name 'User'
    
    def test_get_user_stats(self):
        """Test getting user statistics"""
        stats = self.user_service.get_user_stats()
        
        assert 'total_users' in stats
        assert 'active_users' in stats
        assert 'users_by_role' in stats
        assert stats['total_users'] >= 3
        assert stats['active_users'] >= 3
        assert 'admin' in stats['users_by_role']
        assert 'trainer' in stats['users_by_role']
        assert 'student' in stats['users_by_role']
    
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
        
        # Admin should still be active
        admin = User.query.get(self.admin_user.id)
        assert admin.is_active is True