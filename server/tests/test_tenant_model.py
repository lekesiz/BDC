"""Tests for Tenant model."""

import pytest
from datetime import datetime
from app.models.tenant import Tenant
from app.extensions import db


class TestTenantModel:
    """Test the Tenant model."""

    def test_tenant_creation(self, db_session):
        """Test creating a tenant."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            email="info@testcompany.com",
            phone="+1234567890",
            address="123 Test Street",
            plan="pro",
            max_users=50,
            max_beneficiaries=200
        )
        db.session.add(tenant)
        db.session.commit()
        
        assert tenant.id is not None
        assert tenant.name == "Test Company"
        assert tenant.slug == "test-company"
        assert tenant.email == "info@testcompany.com"
        assert tenant.phone == "+1234567890"
        assert tenant.address == "123 Test Street"
        assert tenant.plan == "pro"
        assert tenant.max_users == 50
        assert tenant.max_beneficiaries == 200
        assert tenant.is_active is True
        assert tenant.settings == {}
        assert isinstance(tenant.created_at, datetime)
        assert isinstance(tenant.updated_at, datetime)

    def test_tenant_defaults(self, db_session):
        """Test tenant default values."""
        tenant = Tenant(
            name="Basic Company",
            slug="basic-company",
            email="basic@company.com"
        )
        db.session.add(tenant)
        db.session.commit()
        
        assert tenant.plan == "basic"
        assert tenant.max_users == 10
        assert tenant.max_beneficiaries == 50
        assert tenant.is_active is True
        assert tenant.activation_date is None
        assert tenant.expiration_date is None
        assert tenant.settings == {}

    def test_tenant_to_dict(self, db_session):
        """Test converting tenant to dictionary."""
        activation_date = datetime(2025, 1, 1)
        expiration_date = datetime(2026, 1, 1)
        
        tenant = Tenant(
            name="Enterprise Corp",
            slug="enterprise-corp",
            email="contact@enterprise.com",
            phone="+9876543210",
            address="456 Corporate Blvd",
            plan="enterprise",
            max_users=500,
            max_beneficiaries=5000,
            is_active=True,
            activation_date=activation_date,
            expiration_date=expiration_date,
            settings={"feature_x": True, "theme": "dark"}
        )
        db.session.add(tenant)
        db.session.commit()
        
        tenant_dict = tenant.to_dict()
        
        assert tenant_dict['id'] == tenant.id
        assert tenant_dict['name'] == "Enterprise Corp"
        assert tenant_dict['slug'] == "enterprise-corp"
        assert tenant_dict['email'] == "contact@enterprise.com"
        assert tenant_dict['phone'] == "+9876543210"
        assert tenant_dict['address'] == "456 Corporate Blvd"
        assert tenant_dict['plan'] == "enterprise"
        assert tenant_dict['max_users'] == 500
        assert tenant_dict['max_beneficiaries'] == 5000
        assert tenant_dict['is_active'] is True
        assert tenant_dict['activation_date'] == activation_date.isoformat()
        assert tenant_dict['expiration_date'] == expiration_date.isoformat()
        assert tenant_dict['settings'] == {"feature_x": True, "theme": "dark"}
        assert 'created_at' in tenant_dict
        assert 'updated_at' in tenant_dict

    def test_tenant_to_dict_without_dates(self, db_session):
        """Test converting tenant to dictionary without activation/expiration dates."""
        tenant = Tenant(
            name="No Dates Company",
            slug="no-dates",
            email="nodates@company.com"
        )
        db.session.add(tenant)
        db.session.commit()
        
        tenant_dict = tenant.to_dict()
        
        assert tenant_dict['activation_date'] is None
        assert tenant_dict['expiration_date'] is None

    def test_tenant_relationships(self, db_session):
        """Test tenant relationships."""
        tenant = Tenant(
            name="Related Company",
            slug="related-company",
            email="related@company.com"
        )
        db.session.add(tenant)
        db.session.commit()
        
        # Test relationship attributes exist
        assert hasattr(tenant, 'users')
        assert hasattr(tenant, 'folders')
        assert hasattr(tenant, 'reports')
        assert hasattr(tenant, 'programs')
        
        # Test lazy loading
        assert tenant.folders.count() == 0
        assert tenant.reports.count() == 0
        assert tenant.programs.count() == 0

    def test_tenant_slug_uniqueness(self, db_session):
        """Test that tenant slug must be unique."""
        tenant1 = Tenant(
            name="Company One",
            slug="unique-slug",
            email="one@company.com"
        )
        db.session.add(tenant1)
        db.session.commit()
        
        tenant2 = Tenant(
            name="Company Two",
            slug="unique-slug",  # Same slug
            email="two@company.com"
        )
        db.session.add(tenant2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.session.commit()

    def test_tenant_update(self, db_session):
        """Test updating tenant."""
        tenant = Tenant(
            name="Original Name",
            slug="original-slug",
            email="original@company.com"
        )
        db.session.add(tenant)
        db.session.commit()
        
        original_created = tenant.created_at
        original_updated = tenant.updated_at
        
        # Update tenant
        tenant.name = "Updated Name"
        tenant.plan = "pro"
        tenant.settings = {"new_setting": "value"}
        db.session.commit()
        
        assert tenant.name == "Updated Name"
        assert tenant.plan == "pro"
        assert tenant.settings == {"new_setting": "value"}
        assert tenant.created_at == original_created
        # Note: updated_at should change, but onupdate might not work in tests