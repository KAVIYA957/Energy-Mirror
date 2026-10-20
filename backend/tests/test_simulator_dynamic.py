import pytest
from app.services.simulator import simulator


def test_individual_appliance_toggles(client):
    """Verify each individual appliance toggle results in exact expected power change."""
    # Baseline: all ON -> 284.0 W (272 W + 12 W)
    res = client.get("/api/v1/simulator/state")
    assert res.status_code == 200
    assert res.json()["aggregate_power_w"] == 284.0

    # 1. Toggle Water Heater OFF: -140 W -> 144.0 W
    res_heater = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "OFF"},
    )
    assert res_heater.status_code == 200
    data = res_heater.json()
    assert data["status"] == "success"
    assert data["delta_power_w"] == -140.0
    assert data["simulator_state"]["aggregate_power_w"] == 144.0
    assert data["event_detected"]["status"] == "MATCHED"
    assert data["event_detected"]["appliance_id"] == "heater_01"
    assert data["event_detected"]["transition_type"] == "OFF"

    # 2. Toggle Water Pump OFF: -75 W -> 69.0 W
    res_pump = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "pump_01", "target_state": "OFF"},
    )
    assert res_pump.status_code == 200
    data = res_pump.json()
    assert data["status"] == "success"
    assert data["delta_power_w"] == -75.0
    assert data["simulator_state"]["aggregate_power_w"] == 69.0

    # 3. Toggle Ceiling Fan OFF: -45 W -> 24.0 W
    res_fan = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "fan_01", "target_state": "OFF"},
    )
    assert res_fan.status_code == 200
    data = res_fan.json()
    assert data["status"] == "success"
    assert data["delta_power_w"] == -45.0
    assert data["simulator_state"]["aggregate_power_w"] == 24.0

    # 4. Toggle LED Bulb OFF: -12 W -> 12.0 W (Standby floor only!)
    res_bulb = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "bulb_01", "target_state": "OFF"},
    )
    assert res_bulb.status_code == 200
    data = res_bulb.json()
    assert data["status"] == "success"
    assert data["delta_power_w"] == -12.0
    assert data["simulator_state"]["aggregate_power_w"] == 12.0


def test_all_appliances_off_accounting(client):
    """
    Mandatory Milestone S2 accounting rule:
    When all 4 appliances are OFF, the 12 W background component remains active:
    - Aggregate power = 12.0 W
    - Attributed power = 0.0 W
    - Unattributed power = 12.0 W
    - Unattributed percentage = 100.0%
    """
    # Turn off all four appliances
    for app_id in ["heater_01", "pump_01", "fan_01", "bulb_01"]:
        client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": app_id, "target_state": "OFF"})

    # Check simulator state
    state_res = client.get("/api/v1/simulator/state")
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["aggregate_power_w"] == 12.0
    assert state["attributed_power_w"] == 0.0
    assert state["unattributed_power_w"] == 12.0
    assert state["unattributed_percentage"] == 100.0

    # Check live disaggregation endpoint
    disagg_res = client.get("/api/v1/nilm/live-disaggregation")
    assert disagg_res.status_code == 200
    disagg = disagg_res.json()
    assert disagg["aggregate_power_w"] == 12.0
    assert disagg["unattributed_power_w"] == 12.0
    assert disagg["unattributed_percentage"] == 100.0
    for app in disagg["appliances"]:
        assert app["status"] == "OFF"
        assert app["estimated_power_w"] == 0.0

    # Check live telemetry endpoint
    telem_res = client.get("/api/v1/telemetry/live")
    assert telem_res.status_code == 200
    telem = telem_res.json()
    assert telem["active_power_w"] == 12.0
    assert telem["unattributed_power_w"] == 12.0


def test_aggregate_power_reconciliation(client):
    """Reconcile aggregate and attributed power consistently across random toggle combinations."""
    toggles = [
        ("heater_01", "OFF"),  # 284 - 140 = 144
        ("pump_01", "OFF"),    # 144 - 75 = 69
        ("heater_01", "ON"),   # 69 + 140 = 209
        ("fan_01", "OFF"),     # 209 - 45 = 164
    ]
    for app_id, target in toggles:
        client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": app_id, "target_state": target})
        state = client.get("/api/v1/simulator/state").json()
        agg = state["aggregate_power_w"]
        att = state["attributed_power_w"]
        unatt = state["unattributed_power_w"]
        assert round(agg, 1) == round(att + unatt, 1)


def test_invalid_appliance_id_and_malformed_requests(client):
    """Ensure invalid appliance IDs return 404 and malformed bodies return 422."""
    # Unknown appliance ID
    res = client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "microwave_99"})
    assert res.status_code == 404
    assert "Invalid appliance ID" in res.json()["detail"]

    # Missing appliance_id
    res_bad = client.post("/api/v1/simulator/toggle-appliance", json={"target_state": "ON"})
    assert res_bad.status_code == 422

    # Invalid target_state value
    res_bad_state = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "BLOW_UP"},
    )
    assert res_bad_state.status_code == 422

    # Extra fields forbidden
    res_extra = client.post(
        "/api/v1/simulator/toggle-appliance",
        json={"appliance_id": "heater_01", "target_state": "ON", "unexpected_field": "hacked"},
    )
    assert res_extra.status_code == 422


def test_toggle_no_change_when_already_in_state(client):
    """Setting an appliance to its current state should return no_change without triggering false events."""
    # Water heater is already ON by baseline
    res = client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "heater_01", "target_state": "ON"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "no_change"
    assert data["delta_power_w"] == 0.0
    assert data["event_detected"] is None
    assert "was already ON" in data["message"]


def test_simulator_reset_endpoint(client):
    """Verify reset restores baseline all-ON state and clears partial shutdown."""
    # Turn off pump and heater
    client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "heater_01", "target_state": "OFF"})
    client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "pump_01", "target_state": "OFF"})
    assert client.get("/api/v1/simulator/state").json()["aggregate_power_w"] == 69.0

    # Call reset
    reset_res = client.post("/api/v1/simulator/reset")
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["aggregate_power_w"] == 284.0
    assert reset_data["attributed_power_w"] == 272.0
    assert reset_data["unattributed_power_w"] == 12.0
    for app in reset_data["appliances"]:
        assert app["is_on"] is True
        assert app["status"] == "RUNNING"


def test_endpoint_consistency_live_telemetry_disaggregation(client):
    """Verify that toggling an appliance updates both live telemetry and live disaggregation immediately."""
    # Turn heater OFF
    client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "heater_01", "target_state": "OFF"})

    # Check live telemetry
    telem = client.get("/api/v1/telemetry/live").json()
    assert telem["active_power_w"] == 144.0
    assert telem["data_source"] == "SIMULATED"
    assert "Water Heater OFF (-140 W)" in telem["story_headline"]

    # Check live disaggregation
    disagg = client.get("/api/v1/nilm/live-disaggregation").json()
    assert disagg["aggregate_power_w"] == 144.0
    heater_est = next(a for a in disagg["appliances"] if a["appliance_id"] == "heater_01")
    assert heater_est["status"] == "OFF"
    assert heater_est["estimated_power_w"] == 0.0
    assert heater_est["data_source"] == "NILM_ESTIMATED"


def test_simulator_state_isolation_part_1(client):
    """Test 1 of state isolation: turn heater OFF and verify."""
    client.post("/api/v1/simulator/toggle-appliance", json={"appliance_id": "heater_01", "target_state": "OFF"})
    assert client.get("/api/v1/simulator/state").json()["aggregate_power_w"] == 144.0


def test_simulator_state_isolation_part_2(client):
    """
    Test 2 of state isolation: verify that baseline is cleanly restored
    and the heater modification from part 1 did not leak!
    """
    state = client.get("/api/v1/simulator/state").json()
    assert state["aggregate_power_w"] == 284.0
    heater = next(a for a in state["appliances"] if a["appliance_id"] == "heater_01")
    assert heater["is_on"] is True


def test_all_16_combinations_power_accounting_invariants(client):
    """
    Exhaustively test all 2^4 = 16 combinations of the four simulated appliances.
    Verifies that for every single combination:
    - Aggregate power = Attributed appliance power + 12.0 W standby residual
    - LED bulb 12 W is strictly distinct from the 12 W standby floor
    - Reset restores the 284 W baseline
    """
    import itertools

    appliances = ["heater_01", "pump_01", "fan_01", "bulb_01"]
    powers = [140.0, 75.0, 45.0, 12.0]

    for combo in itertools.product([False, True], repeat=4):
        # Configure the simulator to this exact state via API
        for app_id, is_on in zip(appliances, combo):
            target = "ON" if is_on else "OFF"
            res = client.post(
                "/api/v1/simulator/toggle-appliance",
                json={"appliance_id": app_id, "target_state": target},
            )
            assert res.status_code == 200

        # Retrieve current simulator state
        state = client.get("/api/v1/simulator/state").json()
        expected_attr = sum(p for p, is_on in zip(powers, combo) if is_on)
        expected_agg = expected_attr + 12.0

        assert state["attributed_power_w"] == expected_attr
        assert state["aggregate_power_w"] == expected_agg
        assert state["unattributed_power_w"] == 12.0
        # Check strict physical accounting invariant
        assert round(state["aggregate_power_w"], 1) == round(state["attributed_power_w"] + 12.0, 1)

    # Verify reset endpoint restores baseline
    reset_res = client.post("/api/v1/simulator/reset")
    assert reset_res.status_code == 200
    reset_state = reset_res.json()
    assert reset_state["aggregate_power_w"] == 284.0
    assert reset_state["attributed_power_w"] == 272.0
    assert reset_state["unattributed_power_w"] == 12.0

