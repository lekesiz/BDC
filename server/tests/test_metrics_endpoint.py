import pytest

from app import create_app

@pytest.fixture()
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'PROMETHEUS_ENABLED': True})
    return app.test_client()

def test_metrics_endpoint(client):
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert b'python_info' in resp.data 