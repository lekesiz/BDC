"""Tests for UserProfile model."""

import pytest
from datetime import datetime
from app.models.profile import UserProfile
from app.models.user import User
from app.extensions import db


class TestUserProfileModel:
    """Test the UserProfile model."""

    @pytest.fixture
    def setup_user(self, db_session):
        """Set up test user."""
        import uuid
        user = User(
            email=f"profile_test_{uuid.uuid4().hex[:8]}@example.com",
            first_name="Profile",
            last_name="Test",
            role="staff"
        )
        user.password = "password123"
        db.session.add(user)
        db.session.commit()
        return user

    def test_profile_creation(self, db_session, setup_user):
        """Test creating a user profile."""
        profile = UserProfile(
            user_id=setup_user.id,
            avatar_url="https://example.com/avatar.jpg",
            phone_number="+1234567890",
            job_title="Software Engineer",
            department="Engineering",
            bio="Test bio",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/testuser",
            twitter_url="https://twitter.com/testuser",
            website_url="https://testuser.com",
            timezone="America/Los_Angeles",
            language="en",
            notification_preferences='{"email": true, "sms": false}'
        )
        db.session.add(profile)
        db.session.commit()
        
        assert profile.id is not None
        assert profile.user_id == setup_user.id
        assert profile.avatar_url == "https://example.com/avatar.jpg"
        assert profile.phone_number == "+1234567890"
        assert profile.job_title == "Software Engineer"
        assert profile.department == "Engineering"
        assert profile.bio == "Test bio"
        assert profile.location == "San Francisco, CA"
        assert profile.linkedin_url == "https://linkedin.com/in/testuser"
        assert profile.twitter_url == "https://twitter.com/testuser"
        assert profile.website_url == "https://testuser.com"
        assert profile.timezone == "America/Los_Angeles"
        assert profile.language == "en"
        assert profile.notification_preferences == '{"email": true, "sms": false}'
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.updated_at, datetime)

    def test_profile_defaults(self, db_session, setup_user):
        """Test profile with default values."""
        profile = UserProfile(user_id=setup_user.id)
        db.session.add(profile)
        db.session.commit()
        
        assert profile.avatar_url is None
        assert profile.phone_number is None
        assert profile.job_title is None
        assert profile.department is None
        assert profile.bio is None
        assert profile.location is None
        assert profile.linkedin_url is None
        assert profile.twitter_url is None
        assert profile.website_url is None
        assert profile.timezone == "UTC"
        assert profile.language == "en"
        assert profile.notification_preferences is None

    def test_profile_to_dict(self, db_session, setup_user):
        """Test converting profile to dictionary."""
        profile = UserProfile(
            user_id=setup_user.id,
            avatar_url="https://example.com/avatar.jpg",
            phone_number="+1234567890",
            job_title="Software Engineer",
            department="Engineering",
            bio="Test bio",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/testuser",
            twitter_url="https://twitter.com/testuser",
            website_url="https://testuser.com",
            timezone="America/Los_Angeles",
            language="en",
            notification_preferences='{"email": true}'
        )
        db.session.add(profile)
        db.session.commit()
        
        profile_dict = profile.to_dict()
        
        assert profile_dict['id'] == profile.id
        assert profile_dict['user_id'] == setup_user.id
        assert profile_dict['avatar_url'] == "https://example.com/avatar.jpg"
        assert profile_dict['phone_number'] == "+1234567890"
        assert profile_dict['job_title'] == "Software Engineer"
        assert profile_dict['department'] == "Engineering"
        assert profile_dict['bio'] == "Test bio"
        assert profile_dict['location'] == "San Francisco, CA"
        assert profile_dict['linkedin_url'] == "https://linkedin.com/in/testuser"
        assert profile_dict['twitter_url'] == "https://twitter.com/testuser"
        assert profile_dict['website_url'] == "https://testuser.com"
        assert profile_dict['timezone'] == "America/Los_Angeles"
        assert profile_dict['language'] == "en"
        assert profile_dict['notification_preferences'] == '{"email": true}'
        assert profile_dict['created_at'] == profile.created_at.isoformat()
        assert profile_dict['updated_at'] == profile.updated_at.isoformat()

    def test_profile_repr(self, db_session, setup_user):
        """Test profile string representation."""
        profile = UserProfile(user_id=setup_user.id)
        db.session.add(profile)
        db.session.commit()
        
        assert repr(profile) == f'<UserProfile user_id={setup_user.id}>'

    def test_profile_user_relationship(self, db_session, setup_user):
        """Test profile-user relationship."""
        profile = UserProfile(user_id=setup_user.id)
        db.session.add(profile)
        db.session.commit()
        
        # Test forward relationship
        assert profile.user == setup_user
        
        # Test backward relationship
        assert setup_user.profile == profile

    def test_profile_unique_user_constraint(self, db_session, setup_user):
        """Test that each user can only have one profile."""
        profile1 = UserProfile(user_id=setup_user.id)
        db.session.add(profile1)
        db.session.commit()
        
        # Try to create another profile for the same user
        profile2 = UserProfile(user_id=setup_user.id)
        db.session.add(profile2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()

    def test_profile_update(self, db_session, setup_user):
        """Test updating profile."""
        profile = UserProfile(
            user_id=setup_user.id,
            job_title="Junior Developer"
        )
        db.session.add(profile)
        db.session.commit()
        
        original_created = profile.created_at
        
        # Update profile
        profile.job_title = "Senior Developer"
        profile.department = "Engineering"
        profile.bio = "Experienced developer"
        db.session.commit()
        
        assert profile.job_title == "Senior Developer"
        assert profile.department == "Engineering"
        assert profile.bio == "Experienced developer"
        assert profile.created_at == original_created