def test_live_disaggregation_endpoint(client):
    response = client.get("/api/v1/nilm/live-disaggregation")
    assert response.status_code == 200
    data = response.json()
    assert data["data_source"] == "SIMULATED"
    assert data["is_simulated"] is True
    assert data["aggregate_power_w"] == 284.0

    appliances = data["appliances"]
    assert len(appliances) == 4

    # Verify appliance names & power
    app_map = {a["name"]: a for a in appliances}
    assert "Water Heater" in app_map
    assert "Water Pump" in app_map
    assert "Ceiling Fan" in app_map
    assert "LED Bulb" in app_map

    assert app_map["Water Heater"]["estimated_power_w"] == 140.0
    assert app_map["Water Pump"]["estimated_power_w"] == 75.0
    assert app_map["Ceiling Fan"]["estimated_power_w"] == 45.0
    assert app_map["LED Bulb"]["estimated_power_w"] == 12.0

    # Verify all appliances explicitly tagged as NILM_ESTIMATED
    for a in appliances:
        assert a["data_source"] == "NILM_ESTIMATED"
        assert a["confidence_score"] is not None
        assert 0.0 <= a["confidence_score"] <= 1.0

    # Arithmetic integrity check
    appliance_sum = sum(a["estimated_power_w"] for a in appliances)
    assert appliance_sum == 272.0
    assert data["unattributed_power_w"] == 12.0
    assert round(data["aggregate_power_w"], 1) == round(appliance_sum + data["unattributed_power_w"], 1)
    assert data["unattributed_percentage"] == 4.2
