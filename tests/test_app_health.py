def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["version"] == "v1"


def test_root_endpoint_returns_api_information(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Hospital API"
    assert "endpoints" in data
