def test_end_to_end_integration_flow(client):
    # 1. Check Health & DB connectivity
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] == "healthy"
    assert health_data["database_connected"] is True

    # 2. Query Live Telemetry
    telem_res = client.get("/api/v1/telemetry/live")
    assert telem_res.status_code == 200
    telem_data = telem_res.json()
    assert telem_data["data_source"] == "SIMULATED"
    assert telem_data["is_simulated"] is True
    assert telem_data["active_power_w"] == 284.0
    assert telem_data["unattributed_power_w"] == 12.0

    # 3. Query NILM Disaggregation
    nilm_res = client.get("/api/v1/nilm/live-disaggregation")
    assert nilm_res.status_code == 200
    nilm_data = nilm_res.json()
    assert nilm_data["aggregate_power_w"] == 284.0
    assert nilm_data["is_simulated"] is True

    appliances = nilm_data["appliances"]
    assert len(appliances) == 4
    for a in appliances:
        assert a["data_source"] == "NILM_ESTIMATED"
        assert a["status"] == "RUNNING"
        assert a["estimated_power_w"] > 0

    # 4. Invariant Verification
    app_sum = sum(a["estimated_power_w"] for a in appliances)
    assert round(nilm_data["aggregate_power_w"], 1) == round(app_sum + nilm_data["unattributed_power_w"], 1)

    # 5. Query History
    hist_res = client.get("/api/v1/telemetry/history?minutes=60")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["interval_minutes"] == 60
    assert hist_data["count"] > 0
    assert len(hist_data["points"]) == hist_data["count"]
