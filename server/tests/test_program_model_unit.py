import pytest

from app import create_app
from app.models.program import Program

@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_program_table_empty(app_ctx):
    assert Program.query.count() == 0 