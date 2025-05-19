import pytest

from app import create_app
from datetime import datetime

ADMIN = {"email": "admin@bdc.com", "password": "Admin123!"}

@pytest.fixture()
def auth_client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    client = app.test_client()
    token = client.post('/api/auth/login', json=ADMIN).json['access_token']
    return client, token


def test_program_crud_flow(auth_client):
    client, token = auth_client
    headers = {'Authorization': f'Bearer {token}'}

    # Create
    data = {"name": "Test Program"}
    create_resp = client.post('/api/programs', json=data, headers=headers)
    assert create_resp.status_code == 201
    program_id = create_resp.json['id']

    # Retrieve detail
    detail_resp = client.get(f'/api/programs/{program_id}', headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json['name'] == 'Test Program'

    # Update
    upd_resp = client.put(f'/api/programs/{program_id}', json={"name": "Updated"}, headers=headers)
    assert upd_resp.status_code == 200
    assert upd_resp.json['name'] == 'Updated'

    # Delete
    del_resp = client.delete(f'/api/programs/{program_id}', headers=headers)
    assert del_resp.status_code == 200
    # Ensure deleted
    get_resp = client.get(f'/api/programs/{program_id}', headers=headers)
    assert get_resp.status_code == 404 