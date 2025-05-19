import pytest

from app import create_app

ADMIN = {"email": "admin@bdc.com", "password": "Admin123!"}


@pytest.fixture()
def auth_client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    client = app.test_client()
    token = client.post('/api/auth/login', json=ADMIN).json['access_token']
    return client, token


def test_programs_list_empty(auth_client):
    client, token = auth_client
    resp = client.get('/api/programs', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.json == [] 