def test_history_endpoint_default(client):
    response = client.get("/api/v1/telemetry/history")
    assert response.status_code == 200
    data = response.json()
    assert data["interval_minutes"] == 60
    assert data["count"] > 0
    assert len(data["points"]) == data["count"]
    assert data["is_simulated"] is True
    assert data["available_range_minutes"] is not None

    first_pt = data["points"][0]
    assert "timestamp" in first_pt
    assert "active_power_w" in first_pt
    assert first_pt["data_source"] == "SIMULATED"


def test_history_all_four_intervals(client):
    """
    Milestone S3 requirement:
    Confirm all four selectable intervals are supported and validated:
    15 minutes, 1 hour (60m), 6 hours (360m), 24 hours (1440m).
    """
    intervals = [15, 60, 360, 1440]
    for minutes in intervals:
        response = client.get(f"/api/v1/telemetry/history?minutes={minutes}")
        assert response.status_code == 200
        data = response.json()
        assert data["interval_minutes"] == minutes
        assert data["count"] > 0
        assert data["available_range_minutes"] is not None
        assert data["is_simulated"] is True
        for pt in data["points"]:
            assert pt["active_power_w"] >= 0.0


def test_history_query_validation(client):
    # Interval less than 5 min must trigger 422 Unprocessable Entity
    response_low = client.get("/api/v1/telemetry/history?minutes=2")
    assert response_low.status_code == 422

    # Interval greater than 1440 min must trigger 422
    response_high = client.get("/api/v1/telemetry/history?minutes=1441")
    assert response_high.status_code == 422
