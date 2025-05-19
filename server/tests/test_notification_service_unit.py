import pytest

from app import create_app
from app.services import NotificationService


@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_get_notification_not_found(app_ctx):
    assert NotificationService.get_notification(123456) is None


def test_delete_notification_not_found(app_ctx):
    assert NotificationService.delete_notification(123456) is False 