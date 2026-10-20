def test_live_telemetry_endpoint(client):
    response = client.get("/api/v1/telemetry/live")
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "esp32-sim-01"
    assert data["data_source"] == "SIMULATED"
    assert data["is_simulated"] is True
    assert data["active_power_w"] == 284.0
    assert data["voltage_v"] == 230.2
    assert data["current_a"] > 0
    assert data["unattributed_power_w"] == 12.0
    assert "timestamp" in data
