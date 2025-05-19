import pytest

from app import create_app

unauth_endpoints = [
    '/api/beneficiaries',
    '/api/beneficiaries/1',
    '/api/beneficiaries/1/trainers',
    '/api/beneficiaries/1/notes',
    '/api/beneficiaries/1/documents',
    '/api/beneficiaries/1/evaluations',
    '/api/beneficiaries/1/sessions',
    '/api/beneficiaries/1/progress',
    '/api/beneficiaries/1/skills',
    '/api/beneficiaries/1/comparison',
    '/api/beneficiaries/1/report',
]


@pytest.fixture()
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    return app.test_client()


@pytest.mark.parametrize('url', unauth_endpoints)
def test_unauthorized_access_returns_401(client, url):
    resp = client.get(url)
    assert resp.status_code == 401 