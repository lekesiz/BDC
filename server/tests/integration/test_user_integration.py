"""Integration tests for user service and API."""
import pytest
import json
import os
from io import BytesIO

from tests.integration.base_integration_test import BaseIntegrationTest
from app.core.container import get_user_service
from app.models import User, UserProfile, UserActivity


class TestUserIntegration(BaseIntegrationTest):
    """Test user service integration."""
    
    def test_create_user_via_service(self, app, session, test_tenant):
        """Test creating user through service."""
        with app.app_context():
            user_service = get_user_service()
            
            user_data = {
                'email': 'service@example.com',
                'password': 'Service123!',
                'name': 'Service',
                'surname': 'User',
                'role': 'user',
                'tenant_id': test_tenant.id
            }
            
            user = user_service.create_user(user_data)
            
            assert user.email == 'service@example.com'
            assert user.name == 'Service'
            
            # Check profile was created
            profile = user_service.get_user_profile(user.id)
            assert profile is not None
    
    def test_search_users(self, app, session, test_tenant):
        """Test searching users."""
        with app.app_context():
            user_service = get_user_service()
            
            # Create multiple users
            for i in range(5):
                user_service.create_user({
                    'email': f'user{i}@example.com',
                    'password': 'Password123!',
                    'name': f'User{i}',
                    'surname': 'Test',
                    'role': 'user',
                    'tenant_id': test_tenant.id
                })
            
            # Search by name
            results = user_service.search_users('User2')
            assert results['total'] == 1
            assert results['items'][0].email == 'user2@example.com'
            
            # Search with filters
            results = user_service.search_users('', {'role': 'user'})
            assert results['total'] >= 5
    
    def test_user_statistics(self, app, session, test_user):
        """Test user statistics generation."""
        with app.app_context():
            user_service = get_user_service()
            
            # Log some activities
            user_service.log_user_activity(test_user.id, 'login', {})
            user_service.log_user_activity(test_user.id, 'profile_update', {})
            
            # Get statistics
            stats = user_service.get_user_statistics(test_user.id)
            
            assert stats['user_id'] == test_user.id
            assert stats['activity_count'] >= 2
            assert stats['login_count'] >= 1
    
    def test_user_permissions(self, app, session, admin_user, test_user):
        """Test user permission checking."""
        with app.app_context():
            user_service = get_user_service()
            
            # Admin should have all permissions
            admin_perms = user_service.get_user_permissions(admin_user.id)
            assert len(admin_perms) > 0
            
            # Check specific permission
            assert user_service.check_permission(admin_user.id, 'users.create')
            
            # Regular user should have limited permissions
            assert not user_service.check_permission(test_user.id, 'users.delete')
    
    def test_user_role_update(self, app, session, test_user):
        """Test updating user role."""
        with app.app_context():
            user_service = get_user_service()
            
            # Update role
            success = user_service.update_user_role(test_user.id, 'trainer')
            assert success
            
            # Verify update
            user = user_service.get_user(test_user.id)
            assert user.role == 'trainer'
            
            # Check activity was logged
            activities = user_service.get_user_activities(test_user.id)
            role_change = next((a for a in activities if a.activity_type == 'role_changed'), None)
            assert role_change is not None
            assert role_change.details['new_role'] == 'trainer'
    
    def test_user_activation_deactivation(self, app, session, test_user):
        """Test user activation and deactivation."""
        with app.app_context():
            user_service = get_user_service()
            
            # Deactivate user
            success = user_service.deactivate_user(test_user.id)
            assert success
            
            user = user_service.get_user(test_user.id)
            assert not user.is_active
            
            # Activate user
            success = user_service.activate_user(test_user.id)
            assert success
            
            user = user_service.get_user(test_user.id)
            assert user.is_active
    
    def test_user_profile_management(self, app, session, test_user):
        """Test user profile operations."""
        with app.app_context():
            user_service = get_user_service()
            
            # Update profile
            profile_data = {
                'bio': 'Test bio',
                'phone': '+1234567890',
                'address': '123 Test St'
            }
            
            profile = user_service.update_user_profile(test_user.id, profile_data)
            assert profile.bio == 'Test bio'
            assert profile.phone == '+1234567890'
    
    def test_users_by_tenant(self, app, session, test_tenant):
        """Test getting users by tenant."""
        with app.app_context():
            user_service = get_user_service()
            
            # Create users for tenant
            for i in range(3):
                user_service.create_user({
                    'email': f'tenant_user{i}@example.com',
                    'password': 'Password123!',
                    'name': f'TenantUser{i}',
                    'surname': 'Test',
                    'role': 'user',
                    'tenant_id': test_tenant.id
                })
            
            # Get users by tenant
            users = user_service.get_users_by_tenant(test_tenant.id)
            assert len(users) >= 3
    
    def test_overall_user_statistics(self, app, session, test_tenant):
        """Test overall user statistics."""
        with app.app_context():
            user_service = get_user_service()
            
            # Create users with different roles
            user_service.create_user({
                'email': 'trainer@example.com',
                'password': 'Password123!',
                'name': 'Trainer',
                'surname': 'User',
                'role': 'trainer',
                'tenant_id': test_tenant.id
            })
            
            stats = user_service.get_users_statistics()
            
            assert stats['total'] > 0
            assert 'by_role' in stats
            assert stats['active'] > 0
    
    def test_user_delete_cascade(self, app, session, test_user):
        """Test that user deletion cascades properly."""
        with app.app_context():
            user_service = get_user_service()
            
            # Create profile and activities
            user_service.update_user_profile(test_user.id, {'bio': 'Test'})
            user_service.log_user_activity(test_user.id, 'test', {})
            
            # Delete user
            success = user_service.delete_user(test_user.id)
            assert success
            
            # Verify user is deleted
            user = user_service.get_user(test_user.id)
            assert user is None