def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Energy Mirror Backend"
    assert data["version"] == "1.0.0"
    assert data["database_connected"] is True
    assert "timestamp" in data

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs_url" in data
    assert "health_url" in data
