"""Tests for user profile API endpoints."""

import pytest
from app.models.profile import UserProfile


class TestUserProfileAPI:
    """Test user profile API endpoints."""
    
    def test_get_profile_not_exists(self, client, student_headers):
        """Test getting profile when it doesn't exist - should create default."""
        response = client.get('/api/users/me/profile', headers=student_headers)
        assert response.status_code == 200
        assert 'email' in response.json
        assert 'first_name' in response.json
        assert 'last_name' in response.json
        assert response.json['bio'] == ''  # Default empty bio
    
    def test_get_profile_exists(self, client, test_student, student_headers, db_session):
        """Test getting existing profile."""
        profile = UserProfile(
            user_id=test_student.id,
            bio='Test bio',
            phone_number='+1234567890',
            location='New York',
            job_title='Developer'
        )
        db_session.add(profile)
        db_session.commit()
        
        response = client.get('/api/users/me/profile', headers=student_headers)
        assert response.status_code == 200
        assert response.json['bio'] == 'Test bio'
        assert response.json['location'] == 'New York'
    
    def test_update_profile(self, client, student_headers):
        """Test updating user profile."""
        update_data = {
            'bio': 'Updated bio',
            'phone_number': '+9876543210',
            'location': 'San Francisco',
            'job_title': 'Senior Developer',
            'department': 'Engineering',
            'linkedin_url': 'https://linkedin.com/in/testuser',
            'website_url': 'https://testuser.com'
        }
        
        response = client.put('/api/users/me/profile', json=update_data, headers=student_headers)
        assert response.status_code == 200
        assert response.json['bio'] == 'Updated bio'
        assert response.json['location'] == 'San Francisco'
    
    def test_update_user_fields(self, client, student_headers):
        """Test updating user fields through profile endpoint."""
        update_data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'phone': '+1111111111'
        }
        
        response = client.put('/api/users/me/profile', json=update_data, headers=student_headers)
        assert response.status_code == 200
        assert response.json['first_name'] == 'UpdatedFirst'
        assert response.json['last_name'] == 'UpdatedLast'
    
    def test_upload_avatar(self, client, student_headers):
        """Test uploading user avatar."""
        # Create a fake image file
        data = {
            'avatar': (b'fake image data', 'avatar.png')
        }
        
        response = client.post(
            '/api/users/me/profile/avatar',
            data=data,
            headers=student_headers,
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        assert 'avatar_url' in response.json
        assert 'avatar.png' in response.json['avatar_url']
    
    def test_upload_avatar_invalid_type(self, client, student_headers):
        """Test uploading invalid file type as avatar."""
        data = {
            'avatar': (b'fake exe data', 'malware.exe')
        }
        
        response = client.post(
            '/api/users/me/profile/avatar',
            data=data,
            headers=student_headers,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
        assert 'Invalid file type' in response.json['error']
    
    def test_get_privacy_settings(self, client, student_headers):
        """Test getting user privacy settings."""
        response = client.get('/api/users/me/profile/privacy', headers=student_headers)
        assert response.status_code == 200
        assert 'profile_visibility' in response.json
        assert 'show_email' in response.json
        assert 'allow_messages' in response.json
    
    def test_update_privacy_settings(self, client, student_headers):
        """Test updating user privacy settings."""
        privacy_data = {
            'profile_visibility': 'private',
            'show_email': False,
            'show_phone': False,
            'allow_messages': False,
            'allow_notifications': True
        }
        
        response = client.put(
            '/api/users/me/profile/privacy',
            json=privacy_data,
            headers=student_headers
        )
        assert response.status_code == 200
        assert response.json['message'] == 'Privacy settings updated successfully'
    
    def test_update_social_links(self, client, student_headers):
        """Test updating social media links."""
        social_data = {
            'linkedin_url': 'https://linkedin.com/in/newprofile',
            'github_url': 'https://github.com/testuser',
            'twitter_url': 'https://twitter.com/testuser',
            'website_url': 'https://mywebsite.com'
        }
        
        response = client.put(
            '/api/users/me/profile/social',
            json=social_data,
            headers=student_headers
        )
        assert response.status_code == 200
        assert response.json['social_links']['linkedin_url'] == 'https://linkedin.com/in/newprofile'
    
    def test_get_skills(self, client, student_headers):
        """Test getting user skills."""
        response = client.get('/api/users/me/profile/skills', headers=student_headers)
        assert response.status_code == 200
        assert response.json['skills'] == []  # Default empty skills
    
    def test_update_skills(self, client, student_headers):
        """Test updating user skills."""
        skills_data = {
            'skills': ['Python', 'JavaScript', 'Docker', 'AWS']
        }
        
        response = client.put(
            '/api/users/me/profile/skills',
            json=skills_data,
            headers=student_headers
        )
        assert response.status_code == 200
        assert response.json['skills'] == ['Python', 'JavaScript', 'Docker', 'AWS']
    
    def test_update_skills_invalid_format(self, client, student_headers):
        """Test updating skills with invalid format."""
        skills_data = {
            'skills': 'Not a list'
        }
        
        response = client.put(
            '/api/users/me/profile/skills',
            json=skills_data,
            headers=student_headers
        )
        assert response.status_code == 400
        assert 'Skills must be a list' in response.json['error']
    
    def test_profile_without_auth(self, client):
        """Test accessing profile without authentication."""
        response = client.get('/api/users/me/profile')
        assert response.status_code == 401
    
    def test_patch_profile(self, client, student_headers):
        """Test partial update (PATCH) of profile."""
        patch_data = {
            'job_title': 'Lead Developer'
        }
        
        response = client.patch(
            '/api/users/me/profile',
            json=patch_data,
            headers=student_headers
        )
        assert response.status_code == 200
        assert response.json['job_title'] == 'Lead Developer'