import pytest

from app import create_app
from app.services import EvaluationService


@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_get_evaluation_not_found(app_ctx):
    assert EvaluationService.get_evaluation(999) is None 