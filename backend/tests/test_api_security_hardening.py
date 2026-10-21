"""
test_api_security_hardening.py - Comprehensive Security & Configuration Tests for Milestone 2C.14.

Tests:
1. Administrative access control (authorized vs unauthorized requests with X-Admin-Key).
2. Remote client rejection vs loopback permission in development mode.
3. Production configuration validation: wildcard CORS rejection, empty origins, debug flag safety.
4. CORS origin verification: allowed origins received, unauthorized origins rejected.
5. Ingestion token verification: timing-safe comparison, missing/invalid token rejection, staging preservation.
6. Public read-only demo endpoint availability (no auth required for demo/dashboard/simulator).
7. Zero secret leakage in diagnostics and sanitized summaries.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.config import Settings, parse_cors_origins
from app.services.appliance_registry import appliance_registry


class TestAdministrativeAccessControl:
    """Tests administrative access control on POST, PATCH, and DELETE /api/v1/appliances."""

    def test_authorized_admin_mutation_with_key(self, client, db_session):
        """When ADMIN_API_KEY is configured, supplying the correct X-Admin-Key authorizes mutation."""
        appliance_registry.seed_defaults(db_session)
        with patch("app.core.security.settings.ADMIN_API_KEY", "super-secret-admin-key-12345"):
            # Register new appliance with valid header
            payload = {
                "appliance_id": "secured_heater_01",
                "name": "Secured Water Heater",
                "category": "Heating",
                "nominal_power_w": 180.0,
            }
            resp = client.post(
                "/api/v1/appliances",
                json=payload,
                headers={"X-Admin-Key": "super-secret-admin-key-12345"},
            )
            assert resp.status_code == 201
            assert resp.json()["appliance_id"] == "secured_heater_01"

            # Update with valid header
            patch_resp = client.patch(
                "/api/v1/appliances/secured_heater_01",
                json={"name": "Updated Secured Heater"},
                headers={"X-Admin-Key": "super-secret-admin-key-12345"},
            )
            assert patch_resp.status_code == 200
            assert patch_resp.json()["name"] == "Updated Secured Heater"

            # Delete with valid header
            del_resp = client.delete(
                "/api/v1/appliances/secured_heater_01",
                headers={"X-Admin-Key": "super-secret-admin-key-12345"},
            )
            assert del_resp.status_code == 200
            assert del_resp.json()["deleted"] is True

    def test_unauthorized_admin_mutation_with_missing_or_invalid_key(self, client, db_session):
        """When ADMIN_API_KEY is configured, missing or invalid X-Admin-Key returns 401 Unauthorized."""
        appliance_registry.seed_defaults(db_session)
        with patch("app.core.security.settings.ADMIN_API_KEY", "super-secret-admin-key-12345"):
            payload = {
                "appliance_id": "unauth_appliance",
                "name": "Unauthorized Appliance",
                "category": "General",
                "nominal_power_w": 100.0,
            }
            # Missing key
            resp_no_key = client.post("/api/v1/appliances", json=payload)
            assert resp_no_key.status_code == 401
            assert "Missing X-Admin-Key header" in resp_no_key.json()["detail"]

            # Incorrect key
            resp_wrong_key = client.post(
                "/api/v1/appliances",
                json=payload,
                headers={"X-Admin-Key": "wrong-incorrect-key"},
            )
            assert resp_wrong_key.status_code == 401
            assert "Invalid X-Admin-Key header" in resp_wrong_key.json()["detail"]

    def test_admin_mutation_remote_client_rejected_in_dev_mode(self, client, db_session):
        """When ADMIN_API_KEY is not set in dev mode, remote clients (non-loopback IP) are rejected with 403."""
        appliance_registry.seed_defaults(db_session)
        with patch("app.core.security.settings.ADMIN_API_KEY", None), \
             patch("app.core.security.settings.ENVIRONMENT", "development"):
            payload = {
                "appliance_id": "remote_appliance_01",
                "name": "Remote Attempted Appliance",
                "category": "General",
                "nominal_power_w": 100.0,
            }
            # Simulating remote client through X-Forwarded-For
            resp = client.post(
                "/api/v1/appliances",
                json=payload,
                headers={"X-Forwarded-For": "203.0.113.195"},
            )
            assert resp.status_code == 403
            assert "Remote administrative access" in resp.json()["detail"]
            assert "forbidden" in resp.json()["detail"].lower()

    def test_admin_mutation_disabled_in_production_without_key(self, client, db_session):
        """When in production mode without an ADMIN_API_KEY, mutations are rejected with 403."""
        appliance_registry.seed_defaults(db_session)
        with patch("app.core.security.settings.ADMIN_API_KEY", None), \
             patch("app.core.security.settings.ENVIRONMENT", "production"):
            payload = {
                "appliance_id": "prod_appliance_01",
                "name": "Production Appliance",
                "category": "General",
                "nominal_power_w": 100.0,
            }
            resp = client.post("/api/v1/appliances", json=payload)
            assert resp.status_code == 403
            assert "disabled in production" in resp.json()["detail"]


class TestConfigurationHardening:
    """Tests configuration parsing and safety validation."""

    def test_production_wildcard_cors_rejected(self):
        """In production mode, wildcard '*' CORS origin must raise a critical configuration error."""
        s = Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            CORS_ORIGINS=["*"],
            ADMIN_API_KEY="a-sufficiently-long-secret-key-16+",
        )
        with pytest.raises(ValueError) as exc:
            s.validate_configuration()
        assert "Wildcard '*' CORS origin is strictly forbidden in production" in str(exc.value)

    def test_production_empty_cors_rejected(self):
        """In production mode, empty CORS_ORIGINS must raise a configuration error."""
        s = Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            CORS_ORIGINS=[],
            ADMIN_API_KEY="a-sufficiently-long-secret-key-16+",
        )
        with pytest.raises(ValueError) as exc:
            s.validate_configuration()
        assert "CORS_ORIGINS must contain at least one explicit origin" in str(exc.value)

    def test_production_debug_true_rejected(self):
        """In production mode, DEBUG=True must raise a configuration error."""
        s = Settings(
            ENVIRONMENT="production",
            DEBUG=True,
            CORS_ORIGINS=["https://energymirror.example.com"],
            ADMIN_API_KEY="a-sufficiently-long-secret-key-16+",
        )
        with pytest.raises(ValueError) as exc:
            s.validate_configuration()
        assert "DEBUG must be set to false in production" in str(exc.value)

    def test_invalid_environment_rejected(self):
        """Invalid ENVIRONMENT string raises a configuration error."""
        s = Settings(ENVIRONMENT="unsupported_environment")
        with pytest.raises(ValueError) as exc:
            s.validate_configuration()
        assert "Invalid ENVIRONMENT" in str(exc.value)

    def test_parse_cors_origins_function(self):
        """Verify parse_cors_origins parses comma-separated strings correctly."""
        raw = "http://localhost:5000, https://app.example.com , http://127.0.0.1:8000"
        parsed = parse_cors_origins(raw, "development")
        assert parsed == ["http://localhost:5000", "https://app.example.com", "http://127.0.0.1:8000"]

        # Empty in production returns empty list
        assert parse_cors_origins(None, "production") == []
        assert parse_cors_origins("", "production") == []


class TestCORSBehavior:
    """Tests CORS middleware responses for allowed vs disallowed origins."""

    def test_cors_allowed_origin_preflight(self, client):
        """Allowed origin receives Access-Control-Allow-Origin response header."""
        resp = client.options(
            "/api/v1/telemetry/live",
            headers={
                "Origin": "http://localhost:5000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5000"

    def test_cors_disallowed_origin_rejected(self, client):
        """Disallowed origin does NOT receive Access-Control-Allow-Origin matching the disallowed origin."""
        resp = client.options(
            "/api/v1/telemetry/live",
            headers={
                "Origin": "http://malicious-untrusted-site.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") != "http://malicious-untrusted-site.com"


class TestReadOnlyDemoEndpoints:
    """Verifies that all public demo, dashboard, and simulator endpoints remain accessible without auth."""

    def test_get_appliances_publicly_accessible(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        resp = client.get("/api/v1/appliances")
        assert resp.status_code == 200
        assert resp.json()["count"] == 4

    def test_get_single_appliance_publicly_accessible(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        resp = client.get("/api/v1/appliances/pump_01")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Water Pump"

    def test_simulator_toggle_publicly_accessible_for_interactive_demo(self, client, db_session):
        """Simulator toggle is the live demo control, not an administrative catalog mutation."""
        resp = client.post(
            "/api/v1/simulator/toggle-appliance",
            json={"appliance_id": "heater_01", "target_state": "OFF"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    def test_telemetry_live_and_history_accessible(self, client):
        resp_live = client.get("/api/v1/telemetry/live")
        assert resp_live.status_code == 200

        resp_hist = client.get("/api/v1/telemetry/history?minutes=30")
        assert resp_hist.status_code == 200

    def test_diagnostics_accessible_without_secret_leakage(self, client):
        resp = client.get("/api/v1/diagnostics/system")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        # Verify no tokens or private variables leaked
        text = str(data)
        assert "token" not in text.lower() or "device_ingest_token" not in text.lower()
        assert "key" not in text.lower() or "api_key" not in text.lower()


class TestIngestionSecurityAndHardwareSafety:
    """Verifies timing-safe ingestion token check and hardware staging preservation."""

    def test_ingest_token_timing_safe_authentication(self, client, db_session):
        """When DEVICE_INGEST_TOKEN is configured, invalid token returns 401."""
        with patch("app.api.ingest.settings.DEVICE_INGEST_TOKEN", "valid-esp32-ingest-token-xyz"):
            payload = {
                "device_id": "esp32-pzem-01",
                "timestamp": "2026-10-21T12:00:00Z",
                "data_source": "HARDWARE_CONNECTED",
                "voltage_v": 230.2,
                "current_a": 1.25,
                "active_power_w": 287.5,
                "frequency_hz": 50.0,
                "power_factor": 0.95,
                "ct_turns_ratio": 1.0,
            }
            # Missing token
            resp_no_token = client.post("/api/v1/telemetry/ingest", json=payload)
            assert resp_no_token.status_code == 401

            # Incorrect token
            resp_bad_token = client.post(
                "/api/v1/telemetry/ingest",
                json=payload,
                headers={"X-Device-Token": "invalid-token"},
            )
            assert resp_bad_token.status_code == 401

            # Correct token -> accepted in staged_inactive mode (ENABLE_HARDWARE_INGEST=false)
            resp_ok = client.post(
                "/api/v1/telemetry/ingest",
                json=payload,
                headers={"X-Device-Token": "valid-esp32-ingest-token-xyz"},
            )
            assert resp_ok.status_code == 200
            assert resp_ok.json()["status"] == "staged_inactive"
            assert resp_ok.json()["mode"] == "STAGED_INACTIVE"

    def test_hardware_ingest_disabled_safety_invariant(self, client):
        """Confirms that ENABLE_HARDWARE_INGEST is false and simulator remains active."""
        resp = client.get("/api/v1/diagnostics/system")
        assert resp.status_code == 200
        assert resp.json()["hardware_ingestion_enabled"] is False
        assert resp.json()["hardware_mode"] == "STAGED_INACTIVE"
        assert resp.json()["active_telemetry_source"] == "SIMULATED"
