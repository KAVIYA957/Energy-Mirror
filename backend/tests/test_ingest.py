import sqlite3
import os
from datetime import datetime, timezone
import pytest
from app.config import settings

def test_ingest_valid_staged_mode(client):
    """Verify that valid physical telemetry is accepted and staged without disrupting simulator."""
    payload = {
        "device_id": "esp32-pzem-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "firmware_version": "1.0.0",
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 230.5,
        "current_a": 1.234,
        "active_power_w": 284.0,
        "apparent_power_va": 284.4,
        "power_factor": 0.998,
        "frequency_hz": 50.01,
        "energy_kwh": 18.423,
        "derived_reactive_power_var": 15.1,
        "ct_turns_ratio": 1,
        "rssi_dbm": -62,
    }

    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "staged_inactive"
    assert data["mode"] == "STAGED_INACTIVE"
    assert data["active_power_w"] == 284.0
    assert data["effective_power_w"] == 284.0
    assert data["ct_turns_ratio"] == 1
    assert "STAGED (inactive)" in data["message"]


def test_ingest_multi_turn_ct_scaling(client):
    """Verify that multi-turn CT turns ratio correctly scales effective power for low-power loads."""
    # Simulating a 12W LED bulb passed 10 times through a 100A CT:
    # 10 turns * 0.052A = 0.52A sensed. Apparent power ~ 120 VA, active power ~ 120 W.
    payload = {
        "device_id": "esp32-pzem-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 230.0,
        "current_a": 0.522,
        "active_power_w": 120.0,
        "apparent_power_va": 120.0,
        "power_factor": 1.0,
        "ct_turns_ratio": 10,
    }

    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["active_power_w"] == 120.0
    # Effective power should be divided by 10 turns -> 12.0 W
    assert data["effective_power_w"] == 12.0
    assert data["ct_turns_ratio"] == 10


def test_ingest_physical_law_validation_rejection(client):
    """Verify that impossible physical readings (P > S by > 8%) are rejected with HTTP 422."""
    payload = {
        "device_id": "esp32-pzem-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 230.0,
        "current_a": 0.5,
        "active_power_w": 200.0,       # Physically impossible: P = 200W with S = 100VA!
        "apparent_power_va": 100.0,
        "power_factor": 0.95,
    }

    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 422
    assert "cannot exceed apparent power" in res.text


def test_ingest_extra_fields_forbidden(client):
    """Verify that unexpected extra fields (e.g. attempting to send raw appliances) are rejected."""
    payload = {
        "device_id": "esp32-pzem-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 230.0,
        "current_a": 1.0,
        "active_power_w": 230.0,
        "unattributed_power_w": 12.0,  # Invalid: downstream NILM field forbidden in hardware ingest
    }

    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 422


def test_ingest_token_authentication(client, monkeypatch):
    """Verify that X-Device-Token is enforced when DEVICE_INGEST_TOKEN is configured."""
    monkeypatch.setattr(settings, "DEVICE_INGEST_TOKEN", "test-secret-token-xyz")

    payload = {
        "device_id": "esp32-pzem-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 230.0,
        "current_a": 1.0,
        "active_power_w": 230.0,
    }

    # 1. Missing header -> 401
    res1 = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res1.status_code == 401
    assert "Invalid or missing X-Device-Token" in res1.json()["detail"]

    # 2. Wrong token -> 401
    res2 = client.post(
        "/api/v1/telemetry/ingest",
        json=payload,
        headers={"X-Device-Token": "wrong-token"},
    )
    assert res2.status_code == 401

    # 3. Correct token -> 200
    res3 = client.post(
        "/api/v1/telemetry/ingest",
        json=payload,
        headers={"X-Device-Token": "test-secret-token-xyz"},
    )
    assert res3.status_code == 200
    assert res3.json()["status"] == "staged_inactive"


def test_ingest_hardware_active_mode(client, monkeypatch):
    """Verify that when ENABLE_HARDWARE_INGEST is explicitly enabled, readings enter hardware mode."""
    monkeypatch.setattr(settings, "ENABLE_HARDWARE_INGEST", True)

    payload = {
        "device_id": "esp32-pzem-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 231.2,
        "current_a": 1.23,
        "active_power_w": 284.3,
        "power_factor": 0.99,
    }

    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "accepted"
    assert data["mode"] == "HARDWARE_ACTIVE"
    assert "hardware database stream" in data["message"]


def test_dev_database_untouched_during_ingest(client, monkeypatch):
    """
    Regression Test for Task 1:
    Explicitly verify that even when hardware ingestion is active and writes to the DB,
    the real development database 'energy_mirror.db' is strictly UNTOUCHED and unchanged.
    """
    dev_db_path = "energy_mirror.db"
    initial_count = None
    if os.path.exists(dev_db_path):
        con = sqlite3.connect(dev_db_path)
        initial_count = con.execute("SELECT COUNT(*) FROM telemetry_records").fetchone()[0]
        con.close()

    monkeypatch.setattr(settings, "ENABLE_HARDWARE_INGEST", True)

    # Ingest a test hardware packet
    payload = {
        "device_id": "esp32-isolated-test-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": "HARDWARE_CONNECTED",
        "voltage_v": 230.0,
        "current_a": 2.0,
        "active_power_w": 460.0,
        "power_factor": 1.0,
    }

    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 200
    assert res.json()["mode"] == "HARDWARE_ACTIVE"

    # Verify that the dev database on disk experienced ZERO record additions
    if os.path.exists(dev_db_path):
        con = sqlite3.connect(dev_db_path)
        final_count = con.execute("SELECT COUNT(*) FROM telemetry_records").fetchone()[0]
        con.close()
        assert final_count == initial_count, f"Dev database was modified! Initial: {initial_count}, Final: {final_count}"
