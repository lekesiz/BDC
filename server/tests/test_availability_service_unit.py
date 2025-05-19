import pytest

from app import create_app
from app.services import AvailabilityService


@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_get_availability_empty(app_ctx):
    slots, total, pages = AvailabilityService.get_availabilities(page=1, per_page=10)
    assert total == 0 