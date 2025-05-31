"""Tests for Folder model."""

import pytest
from datetime import datetime
from app.models.folder import Folder
from app.models.tenant import Tenant
from app.models.user import User
from app.extensions import db


class TestFolderModel:
    """Test the Folder model."""

    @pytest.fixture
    def setup_data(self, db_session):
        """Set up test data."""
        # Create tenant
        import uuid
        unique_slug = f"folder-tenant-{uuid.uuid4().hex[:8]}"
        tenant = Tenant(
            name="Folder Test Tenant",
            slug=unique_slug,
            email="folder@tenant.com"
        )
        db.session.add(tenant)
        
        # Create user
        user = User(
            email=f"folder_user_{uuid.uuid4().hex[:8]}@test.com",
            first_name="Folder",
            last_name="Owner",
            role="admin"
        )
        user.password = "password123"
        db.session.add(user)
        db.session.commit()
        
        return {"tenant": tenant, "user": user}

    def test_folder_creation(self, db_session, setup_data):
        """Test creating a folder."""
        folder = Folder(
            name="Test Folder",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(folder)
        db.session.commit()
        
        assert folder.id is not None
        assert folder.name == "Test Folder"
        assert folder.parent_id is None
        assert folder.tenant_id == setup_data["tenant"].id
        assert folder.owner_id == setup_data["user"].id
        assert isinstance(folder.created_at, datetime)
        assert isinstance(folder.updated_at, datetime)

    def test_folder_with_parent(self, db_session, setup_data):
        """Test creating a folder with parent."""
        # Create parent folder
        parent_folder = Folder(
            name="Parent Folder",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(parent_folder)
        db.session.commit()
        
        # Create child folder
        child_folder = Folder(
            name="Child Folder",
            parent_id=parent_folder.id,
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(child_folder)
        db.session.commit()
        
        assert child_folder.parent_id == parent_folder.id
        assert child_folder.parent == parent_folder
        assert child_folder in parent_folder.subfolders

    def test_folder_to_dict(self, db_session, setup_data):
        """Test converting folder to dictionary."""
        folder = Folder(
            name="Dict Test Folder",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(folder)
        db.session.commit()
        
        folder_dict = folder.to_dict()
        
        assert folder_dict['id'] == folder.id
        assert folder_dict['name'] == "Dict Test Folder"
        assert folder_dict['parent_id'] is None
        assert folder_dict['tenant_id'] == setup_data["tenant"].id
        assert folder_dict['owner_id'] == setup_data["user"].id
        assert folder_dict['created_at'] == folder.created_at.isoformat()
        assert folder_dict['updated_at'] == folder.updated_at.isoformat()
        assert folder_dict['document_count'] == 0

    def test_folder_to_dict_with_parent(self, db_session, setup_data):
        """Test converting folder with parent to dictionary."""
        # Create parent folder
        parent_folder = Folder(
            name="Parent",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(parent_folder)
        db.session.commit()
        
        # Create child folder
        child_folder = Folder(
            name="Child",
            parent_id=parent_folder.id,
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(child_folder)
        db.session.commit()
        
        child_dict = child_folder.to_dict()
        assert child_dict['parent_id'] == parent_folder.id

    def test_folder_relationships(self, db_session, setup_data):
        """Test folder relationships."""
        folder = Folder(
            name="Related Folder",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(folder)
        db.session.commit()
        
        assert folder.tenant == setup_data["tenant"]
        assert folder.owner == setup_data["user"]
        assert folder in setup_data["tenant"].folders.all()
        assert folder in setup_data["user"].folders

    def test_folder_hierarchy(self, db_session, setup_data):
        """Test multi-level folder hierarchy."""
        # Create root folder
        root = Folder(
            name="Root",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(root)
        db.session.commit()
        
        # Create first level child
        level1 = Folder(
            name="Level 1",
            parent_id=root.id,
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(level1)
        db.session.commit()
        
        # Create second level child
        level2 = Folder(
            name="Level 2",
            parent_id=level1.id,
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(level2)
        db.session.commit()
        
        # Test relationships
        assert level1.parent == root
        assert level2.parent == level1
        assert level1 in root.subfolders
        assert level2 in level1.subfolders
        assert len(root.subfolders) == 1
        assert len(level1.subfolders) == 1
        assert len(level2.subfolders) == 0

    def test_folder_update(self, db_session, setup_data):
        """Test updating folder."""
        folder = Folder(
            name="Original Name",
            tenant_id=setup_data["tenant"].id,
            owner_id=setup_data["user"].id
        )
        db.session.add(folder)
        db.session.commit()
        
        original_created = folder.created_at
        
        # Update folder
        folder.name = "Updated Name"
        db.session.commit()
        
        assert folder.name == "Updated Name"
        assert folder.created_at == original_created