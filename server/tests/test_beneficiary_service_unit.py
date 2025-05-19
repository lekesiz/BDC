import pytest

from app import create_app
from app.services import BeneficiaryService
from app.models import Tenant


@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_get_beneficiary_not_found(app_ctx):
    assert BeneficiaryService.get_beneficiary(9999) is None


def test_create_and_get_beneficiary(app_ctx):
    tenant = Tenant.query.first()
    user_data = {
        'email': 'unitbene@bdc.com',
        'password': 'Unit123!',
        'first_name': 'Unit',
        'last_name': 'Test',
    }
    bene_data = {
        'tenant_id': tenant.id,
    }
    bene = BeneficiaryService.create_beneficiary(user_data, bene_data)
    assert bene is not None
    fetched = BeneficiaryService.get_beneficiary(bene.id)
    assert fetched.id == bene.id 