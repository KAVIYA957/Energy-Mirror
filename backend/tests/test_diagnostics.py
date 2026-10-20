def test_system_diagnostics_endpoint(client):
    """Verify that system diagnostics returns complete system health without exposing secrets."""
    res = client.get("/api/v1/diagnostics/system")
    assert res.status_code == 200
    data = res.json()

    # Core health & identification
    assert data["status"] == "healthy"
    assert "Energy Mirror" in data["app_name"]
    assert data["app_version"] == "1.0.0"

    # Truth-in-reporting invariants
    assert data["active_telemetry_source"] == "SIMULATED"
    assert data["hardware_ingestion_enabled"] is False
    assert data["hardware_mode"] == "STAGED_INACTIVE"

    # Subsystem telemetry
    assert data["database_connected"] is True
    assert data["database_type"] == "SQLite"
    assert data["database_record_count"] >= 0
    assert data["simulator_active"] is True
    assert data["simulator_appliances_count"] == 4
    assert data["simulator_aggregate_w"] == 284.0
    assert data["unattributed_baseline_w"] == 12.0
    assert data["nilm_detector_mode"] == "RULE_BASED_ESTIMATE"

    # Strict Privacy & Security Check: Guarantee zero secrets, tokens, or paths leaked
    raw_text = res.text.lower()
    forbidden_terms = ["secret", "token", "password", "device_token", "c:\\", "/home/", "private"]
    for term in forbidden_terms:
        assert term not in raw_text, f"Security violation: Diagnostics exposed sensitive term '{term}'!"
