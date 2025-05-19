import pytest

from app import create_app

@pytest.fixture()
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    return app.test_client()

def test_programs_unauthorized(client):
    resp = client.get('/api/programs')
    assert resp.status_code == 401 