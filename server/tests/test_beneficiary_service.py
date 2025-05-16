"""Tests for beneficiary service."""

import json
import pytest
from datetime import datetime
from app.models import User, Beneficiary, Program, TestSet
from app.services.beneficiary_service import BeneficiaryService
from app.extensions import db

@pytest.fixture
def setup_beneficiary_service_data(session, app):
    """Setup test data for beneficiary service tests."""
    with app.app_context():
        # Create test user
        user = User(
            username='service_user',
            email='service@test.com',
            is_active=True,
            role='admin',
            tenant_id=1
        )
        user.password = 'password123'
        
        # Create programs
        program1 = Program(
            name='Test Program 1',
            description='Test program description',
            is_active=True,
            tenant_id=1
        )
        
        program2 = Program(
            name='Test Program 2',
            description='Another test program',
            is_active=True,
            tenant_id=1
        )
        
        # Create test sets
        test_set1 = TestSet(
            name='Test Set 1',
            description='Test set description',
            is_active=True,
            created_by=user.id,
            tenant_id=1
        )
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            name='Service Test Beneficiary 1',
            email='service_ben1@test.com',
            phone='1111111111',
            tenant_id=1
        )
        
        beneficiary2 = Beneficiary(
            name='Service Test Beneficiary 2',
            email='service_ben2@test.com',
            phone='2222222222',
            tenant_id=1
        )
        
        session.add_all([user, program1, program2, test_set1, beneficiary1, beneficiary2])
        session.commit()
        
        # Add relationships
        beneficiary1.programs.append(program1)
        beneficiary2.programs.extend([program1, program2])
        session.commit()
        
        return {
            'user': user,
            'program1': program1,
            'program2': program2,
            'test_set1': test_set1,
            'beneficiary1': beneficiary1,
            'beneficiary2': beneficiary2
        }


def test_create_beneficiary(session, setup_beneficiary_service_data, app):
    """Test creating a beneficiary via service."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiary_data = {
            'name': 'New Service Beneficiary',
            'email': 'new_service@test.com',
            'phone': '3333333333',
            'date_of_birth': '1990-01-01',
            'address': '789 Service St',
            'city': 'Service City',
            'state': 'SV',
            'zip_code': '99999',
            'country': 'US',
            'emergency_contact': 'Emergency Contact',
            'emergency_phone': '4444444444'
        }
        
        beneficiary = service.create_beneficiary(
            tenant_id=1,
            **beneficiary_data
        )
        
        assert beneficiary is not None
        assert beneficiary.name == 'New Service Beneficiary'
        assert beneficiary.email == 'new_service@test.com'
        assert beneficiary.tenant_id == 1


def test_get_beneficiaries(session, setup_beneficiary_service_data, app):
    """Test getting beneficiaries via service."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiaries = service.get_beneficiaries(tenant_id=1)
        
        assert len(beneficiaries) >= 2
        names = [b.name for b in beneficiaries]
        assert 'Service Test Beneficiary 1' in names
        assert 'Service Test Beneficiary 2' in names


def test_get_beneficiary_by_id(session, setup_beneficiary_service_data, app):
    """Test getting a specific beneficiary by ID."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiary_id = setup_beneficiary_service_data['beneficiary1'].id
        beneficiary = service.get_beneficiary_by_id(
            beneficiary_id=beneficiary_id,
            tenant_id=1
        )
        
        assert beneficiary is not None
        assert beneficiary.id == beneficiary_id
        assert beneficiary.name == 'Service Test Beneficiary 1'


def test_update_beneficiary(session, setup_beneficiary_service_data, app):
    """Test updating a beneficiary."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiary_id = setup_beneficiary_service_data['beneficiary1'].id
        update_data = {
            'name': 'Updated Beneficiary Name',
            'phone': '5555555555',
            'city': 'Updated City'
        }
        
        updated_beneficiary = service.update_beneficiary(
            beneficiary_id=beneficiary_id,
            tenant_id=1,
            **update_data
        )
        
        assert updated_beneficiary is not None
        assert updated_beneficiary.name == 'Updated Beneficiary Name'
        assert updated_beneficiary.phone == '5555555555'
        assert updated_beneficiary.city == 'Updated City'


def test_delete_beneficiary(session, setup_beneficiary_service_data, app):
    """Test deleting a beneficiary."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiary_id = setup_beneficiary_service_data['beneficiary1'].id
        result = service.delete_beneficiary(
            beneficiary_id=beneficiary_id,
            tenant_id=1
        )
        
        assert result is True
        
        # Verify deletion
        deleted = service.get_beneficiary_by_id(
            beneficiary_id=beneficiary_id,
            tenant_id=1
        )
        assert deleted is None


def test_assign_program(session, setup_beneficiary_service_data, app):
    """Test assigning a program to a beneficiary."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiary_id = setup_beneficiary_service_data['beneficiary1'].id
        program_id = setup_beneficiary_service_data['program2'].id
        
        result = service.assign_beneficiary_to_program(
            beneficiary_id=beneficiary_id,
            program_id=program_id,
            tenant_id=1
        )
        
        assert result is True
        
        # Verify assignment
        beneficiary = service.get_beneficiary_by_id(
            beneficiary_id=beneficiary_id,
            tenant_id=1
        )
        program_ids = [p.id for p in beneficiary.programs]
        assert program_id in program_ids


def test_remove_program(session, setup_beneficiary_service_data, app):
    """Test removing a program from a beneficiary."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiary_id = setup_beneficiary_service_data['beneficiary2'].id
        program_id = setup_beneficiary_service_data['program1'].id
        
        result = service.remove_beneficiary_from_program(
            beneficiary_id=beneficiary_id,
            program_id=program_id,
            tenant_id=1
        )
        
        assert result is True
        
        # Verify removal
        beneficiary = service.get_beneficiary_by_id(
            beneficiary_id=beneficiary_id,
            tenant_id=1
        )
        program_ids = [p.id for p in beneficiary.programs]
        assert program_id not in program_ids


def test_search_beneficiaries(session, setup_beneficiary_service_data, app):
    """Test searching beneficiaries."""
    with app.app_context():
        service = BeneficiaryService()
        
        # Search by name
        results = service.search_beneficiaries(
            tenant_id=1,
            query='Service Test'
        )
        
        assert len(results) >= 2
        names = [b.name for b in results]
        assert 'Service Test Beneficiary 1' in names
        assert 'Service Test Beneficiary 2' in names
        
        # Search by email
        results = service.search_beneficiaries(
            tenant_id=1,
            query='service_ben1'
        )
        
        assert len(results) >= 1
        assert results[0].email == 'service_ben1@test.com'


def test_get_beneficiaries_by_program(session, setup_beneficiary_service_data, app):
    """Test getting beneficiaries by program."""
    with app.app_context():
        service = BeneficiaryService()
        
        program_id = setup_beneficiary_service_data['program1'].id
        beneficiaries = service.get_beneficiaries_by_program(
            program_id=program_id,
            tenant_id=1
        )
        
        assert len(beneficiaries) >= 2
        names = [b.name for b in beneficiaries]
        assert 'Service Test Beneficiary 1' in names
        assert 'Service Test Beneficiary 2' in names


def test_bulk_create_beneficiaries(session, app):
    """Test bulk creating beneficiaries."""
    with app.app_context():
        service = BeneficiaryService()
        
        beneficiaries_data = [
            {
                'name': 'Bulk Beneficiary 1',
                'email': 'bulk1@test.com',
                'phone': '6666666666'
            },
            {
                'name': 'Bulk Beneficiary 2',
                'email': 'bulk2@test.com',
                'phone': '7777777777'
            },
            {
                'name': 'Bulk Beneficiary 3',
                'email': 'bulk3@test.com',
                'phone': '8888888888'
            }
        ]
        
        created_beneficiaries = service.bulk_create_beneficiaries(
            tenant_id=1,
            beneficiaries_data=beneficiaries_data
        )
        
        assert len(created_beneficiaries) == 3
        emails = [b.email for b in created_beneficiaries]
        assert 'bulk1@test.com' in emails
        assert 'bulk2@test.com' in emails
        assert 'bulk3@test.com' in emails