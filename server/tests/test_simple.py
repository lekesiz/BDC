"""Simple tests to verify the system works."""

def test_app_runs(client):
    """Test the app starts and runs."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'