import pytest

from app import create_app

ADMIN_CREDENTIALS = {"email": "admin@bdc.com", "password": "Admin123!"}


@pytest.fixture()
def auth_client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    client = app.test_client()
    # Login to obtain JWT
    resp = client.post('/api/auth/login', json=ADMIN_CREDENTIALS)
    assert resp.status_code == 200
    token = resp.json['access_token']
    return client, token


def test_get_beneficiaries_success(auth_client):
    client, token = auth_client
    resp = client.get('/api/beneficiaries', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'items' in resp.json 