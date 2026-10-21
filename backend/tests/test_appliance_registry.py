"""
test_appliance_registry.py - Comprehensive Unit and Integration Tests for Dynamic Appliance Registry.

Verifies Milestone 2C.13 specifications:
1. Default four-appliance configuration and ratings (140W, 75W, 45W, 12W).
2. Registering an additional supported appliance.
3. Duplicate and invalid appliance definition rejection (input validation).
4. Persistence and repeat initialization idempotency.
5. Aggregate-power accounting invariant (P_agg = sum(P_attr) + 12.0 W residual).
6. Unsupported appliance detection status and detection honesty (no hallucinated matches).
7. Disabling appliance behavior and protected baseline deletion prevention.
8. Backward compatibility with existing simulator and telemetry API routes.
"""

import pytest
from app.services.appliance_registry import appliance_registry, DEFAULT_APPLIANCE_DEFINITIONS
from app.services.simulator import TelemetrySimulator
from app.services.event_detector import RuleBasedEventDetector
from app.schemas.appliance import ApplianceCreateRequest, ApplianceUpdateRequest


class TestDynamicApplianceRegistry:
    """Tests the registry data model, validation, and CRUD operations."""

    def test_default_four_appliance_configuration(self, db_session):
        """Verify the 4 baseline appliances and their ratings: 140W, 75W, 45W, 12W."""
        appliance_registry.seed_defaults(db_session)
        apps = appliance_registry.get_all(db_session)
        assert len(apps) == 4

        app_map = {a.appliance_id: a for a in apps}
        assert "heater_01" in app_map
        assert app_map["heater_01"].nominal_power_w == 140.0
        assert app_map["heater_01"].detection_capability == "PRODUCTION_RULE_MATCHED"

        assert "pump_01" in app_map
        assert app_map["pump_01"].nominal_power_w == 75.0
        assert app_map["pump_01"].detection_capability == "PRODUCTION_RULE_MATCHED"

        assert "fan_01" in app_map
        assert app_map["fan_01"].nominal_power_w == 45.0
        assert app_map["fan_01"].detection_capability == "PRODUCTION_RULE_MATCHED"

        assert "bulb_01" in app_map
        assert app_map["bulb_01"].nominal_power_w == 12.0
        assert app_map["bulb_01"].detection_capability == "PRODUCTION_RULE_MATCHED"

    def test_register_additional_supported_appliance(self, db_session):
        """Verify registering a 5th appliance definition successfully adds it to registry."""
        appliance_registry.seed_defaults(db_session)
        new_app = ApplianceCreateRequest(
            appliance_id="air_cooler_01",
            name="Desert Air Cooler",
            category="Cooling",
            nominal_power_w=165.0,
            expected_pf=0.82,
            tolerance_w=15.0,
            is_enabled=True,
            is_simulator_supported=True,
            detection_capability="UNSUPPORTED",
            evidence_notes="High-velocity evaporative cooler blower motor.",
        )
        created = appliance_registry.register(db_session, new_app)
        assert created.appliance_id == "air_cooler_01"
        assert created.nominal_power_w == 165.0

        all_apps = appliance_registry.get_all(db_session)
        assert len(all_apps) == 5

    def test_duplicate_appliance_id_rejected(self, db_session):
        """Verify that attempting to register an existing ID raises an error."""
        appliance_registry.seed_defaults(db_session)
        dup = ApplianceCreateRequest(
            appliance_id="heater_01",
            name="Duplicate Heater",
            category="Heating",
            nominal_power_w=140.0,
        )
        with pytest.raises(ValueError) as exc:
            appliance_registry.register(db_session, dup)
        assert "already exists" in str(exc.value)

    def test_invalid_appliance_definitions_rejected(self, db_session):
        """Verify validation rules: envelope required for PRODUCTION_RULE_MATCHED."""
        appliance_registry.seed_defaults(db_session)
        # Attempting PRODUCTION_RULE_MATCHED without tolerance envelope
        invalid = ApplianceCreateRequest(
            appliance_id="uncalibrated_01",
            name="Uncalibrated Load",
            category="General",
            nominal_power_w=500.0,
            detection_capability="PRODUCTION_RULE_MATCHED",
            tolerance_w=None,  # Missing required envelope!
        )
        with pytest.raises(ValueError) as exc:
            appliance_registry.register(db_session, invalid)
        assert "must define a positive tolerance_w envelope" in str(exc.value)

    def test_persistence_and_repeat_initialization(self, db_session):
        """Verify that repeated seed_defaults calls are idempotent and do not duplicate."""
        appliance_registry.seed_defaults(db_session)
        assert len(appliance_registry.get_all(db_session)) == 4

        # Repeat seeding
        appliance_registry.seed_defaults(db_session)
        assert len(appliance_registry.get_all(db_session)) == 4

        # Add custom appliance, then re-seed
        custom = ApplianceCreateRequest(
            appliance_id="refrig_01",
            name="Mini Refrigerator",
            category="Cooling",
            nominal_power_w=95.0,
        )
        appliance_registry.register(db_session, custom)
        assert len(appliance_registry.get_all(db_session)) == 5

        # Re-seed again: custom appliance must persist, total count remains 5
        appliance_registry.seed_defaults(db_session)
        assert len(appliance_registry.get_all(db_session)) == 5

    def test_protected_default_appliances_deletion_blocked(self, db_session):
        """Verify that deleting protected baseline appliances is rejected."""
        appliance_registry.seed_defaults(db_session)
        with pytest.raises(ValueError) as exc:
            appliance_registry.delete(db_session, "heater_01")
        assert "Cannot delete protected default" in str(exc.value)

    def test_disable_appliance_behavior(self, db_session):
        """Verify disabling an appliance excludes it when filtering enabled_only."""
        appliance_registry.seed_defaults(db_session)
        appliance_registry.update(db_session, "bulb_01", ApplianceUpdateRequest(is_enabled=False))

        enabled_apps = appliance_registry.get_all(db_session, enabled_only=True)
        assert len(enabled_apps) == 3
        assert "bulb_01" not in [a.appliance_id for a in enabled_apps]

        all_apps = appliance_registry.get_all(db_session, enabled_only=False)
        assert len(all_apps) == 4


class TestDynamicSimulatorAndDetector:
    """Tests simulator dynamic state, power accounting, and detector honesty."""

    def test_aggregate_power_accounting_and_12w_residual_invariant(self, db_session):
        """
        Verify the simulator invariant:
        Aggregate Power = sum(active appliance nominal powers) + 12.0 W residual floor.
        """
        appliance_registry.seed_defaults(db_session)
        sim = TelemetrySimulator()
        sim.sync_from_registry(db_session)

        # Baseline 4 appliances all ON: 140 + 75 + 45 + 12 = 272 W attributed + 12 W residual = 284 W aggregate
        assert sim.get_attributed_power() == 272.0
        assert sim.get_aggregate_power() == 284.0

        # Turn OFF heater (-140 W): 272 - 140 = 132 W attributed + 12 W = 144 W aggregate
        sim.toggle_appliance("heater_01", target_state="OFF", db=db_session)
        assert sim.get_attributed_power() == 132.0
        assert sim.get_aggregate_power() == 144.0

        # Turn all appliances OFF: attributed = 0 W, aggregate = 12.0 W (strictly preserves residual)
        sim.toggle_appliance("pump_01", target_state="OFF", db=db_session)
        sim.toggle_appliance("fan_01", target_state="OFF", db=db_session)
        sim.toggle_appliance("bulb_01", target_state="OFF", db=db_session)
        assert sim.get_attributed_power() == 0.0
        assert sim.get_aggregate_power() == 12.0

    def test_variable_number_of_appliances_simulator_accounting(self, db_session):
        """Test simulator with 5 appliances dynamically registered."""
        appliance_registry.seed_defaults(db_session)
        appliance_registry.register(
            db_session,
            ApplianceCreateRequest(
                appliance_id="toaster_01",
                name="Pop-up Toaster",
                category="Cooking",
                nominal_power_w=800.0,
                detection_capability="UNSUPPORTED",
            ),
        )
        sim = TelemetrySimulator()
        sim.sync_from_registry(db_session)

        assert len(sim.appliances) == 5
        # All 5 ON: 272 + 800 = 1072 W attributed + 12 W residual = 1084 W aggregate
        assert sim.get_attributed_power() == 1072.0
        assert sim.get_aggregate_power() == 1084.0

    def test_unsupported_appliance_detection_honesty(self, db_session):
        """
        DETECTION HONESTY REQUIREMENT:
        The detector must NOT classify an unsupported appliance by name alone.
        When an uncalibrated 950W load steps ON, the step is +950W.
        Because no production envelope matches 950W, the detector outputs AMBIGUOUS or unrecognized,
        never falsely claiming to recognize 'Countertop Microwave'.
        """
        appliance_registry.seed_defaults(db_session)
        appliance_registry.register(
            db_session,
            ApplianceCreateRequest(
                appliance_id="microwave_01",
                name="Countertop Microwave",
                category="Cooking",
                nominal_power_w=950.0,
                detection_capability="UNSUPPORTED",
            ),
        )

        detector = RuleBasedEventDetector()
        detector.sync_from_registry(db_session)

        # Baseline 4 appliances have production rules
        assert len(detector.signatures) == 4
        # microwave_01 has NOT been added as a production rule
        assert "microwave_01" not in [s.appliance_id for s in detector.signatures]

        # Simulate a 950 W step
        prev_p = 284.0
        curr_p = 1234.0  # +950 W step
        ev = detector.detect_transition(prev_power_w=prev_p, curr_power_w=curr_p, prev_pf=0.94, curr_pf=0.92)

        # Truth-in-reporting check: Status MUST be AMBIGUOUS or unrecognized, NEVER MATCHED
        assert ev.status == "AMBIGUOUS"
        assert ev.appliance_id is None
        assert "does not match any single appliance signature" in ev.rule_description


class TestApplianceRegistryAPI:
    """Tests the REST API routes under /api/v1/appliances."""

    def test_api_list_appliances(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        resp = client.get("/api/v1/appliances")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 4
        assert len(data["appliances"]) == 4

    def test_api_register_and_get_appliance(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        payload = {
            "appliance_id": "coffee_maker_01",
            "name": "Drip Coffee Maker",
            "category": "Cooking",
            "nominal_power_w": 650.0,
            "expected_pf": 0.99,
            "is_enabled": True,
            "is_simulator_supported": True,
            "detection_capability": "UNSUPPORTED",
        }
        resp = client.post("/api/v1/appliances", json=payload)
        assert resp.status_code == 201
        created = resp.json()
        assert created["appliance_id"] == "coffee_maker_01"
        assert created["nominal_power_w"] == 650.0

        # Retrieve by ID
        get_resp = client.get("/api/v1/appliances/coffee_maker_01")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "Drip Coffee Maker"

    def test_api_duplicate_rejection(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        payload = {
            "appliance_id": "heater_01",
            "name": "Duplicate Water Heater",
            "category": "Heating",
            "nominal_power_w": 140.0,
        }
        resp = client.post("/api/v1/appliances", json=payload)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    def test_api_patch_appliance(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        resp = client.patch(
            "/api/v1/appliances/fan_01",
            json={"name": "High Speed Ceiling Fan", "nominal_power_w": 55.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "High Speed Ceiling Fan"
        assert data["nominal_power_w"] == 55.0

    def test_api_delete_custom_appliance(self, client, db_session):
        appliance_registry.seed_defaults(db_session)
        # Register custom
        client.post(
            "/api/v1/appliances",
            json={
                "appliance_id": "lamp_01",
                "name": "Desk Lamp",
                "category": "Lighting",
                "nominal_power_w": 25.0,
            },
        )
        # Delete custom
        del_resp = client.delete("/api/v1/appliances/lamp_01")
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True

        # Attempt to delete protected default
        prot_resp = client.delete("/api/v1/appliances/heater_01")
        assert prot_resp.status_code == 400
        assert "Cannot delete protected default" in prot_resp.json()["detail"]
