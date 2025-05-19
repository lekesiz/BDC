import pytest

from app import create_app

ADMIN = {"email": "admin@bdc.com", "password": "Admin123!"}


@pytest.fixture()
def client_token():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    client = app.test_client()
    token = client.post('/api/auth/login', json=ADMIN).json['access_token']
    # Create beneficiary to use in tests
    payload = {
        "email": "apitest@bdc.com",
        "password": "Test123!",
        "confirm_password": "Test123!",
        "first_name": "Api",
        "last_name": "Test",
    }
    bene = client.post('/api/beneficiaries', json=payload, headers={'Authorization': f'Bearer {token}'}).json
    return client, token, bene['id']


def test_documents_empty_list(client_token):
    client, token, bene_id = client_token
    resp = client.get(f'/api/beneficiaries/{bene_id}/documents', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert resp.json['total'] == 0


def test_progress_endpoint(client_token):
    client, token, bene_id = client_token
    resp = client.get(f'/api/beneficiaries/{bene_id}/progress', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'overview' in resp.json


def test_skills_endpoint(client_token):
    client, token, bene_id = client_token
    resp = client.get(f'/api/beneficiaries/{bene_id}/skills', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    assert 'skills' in resp.json 