import pytest

from app import create_app

ADMIN = {"email": "admin@bdc.com", "password": "Admin123!"}


@pytest.fixture()
def client_token():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    client = app.test_client()
    token = client.post('/api/auth/login', json=ADMIN).json['access_token']
    return client, token


def test_create_beneficiary_and_add_note(client_token):
    client, token = client_token
    # create beneficiary
    payload = {
        "email": "testbene@bdc.com",
        "password": "Test123!",
        "confirm_password": "Test123!",
        "first_name": "Test",
        "last_name": "Bene"
    }
    bene_resp = client.post('/api/beneficiaries', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert bene_resp.status_code == 201
    bene_id = bene_resp.json['id']

    # add note
    note_payload = {"title": "Note1", "content": "Test note"}
    note_resp = client.post(f'/api/beneficiaries/{bene_id}/notes', json=note_payload, headers={'Authorization': f'Bearer {token}'})
    assert note_resp.status_code == 201
    assert note_resp.json['title'] == 'Note1' 