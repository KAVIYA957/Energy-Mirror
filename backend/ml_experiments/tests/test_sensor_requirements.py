"""
test_sensor_requirements.py - Unit tests validating the machine-readable sensor requirements.

Validates:
1. Structural integrity and JSON schema conformity of sensor_requirements.json
2. Presence and physical consistency of target appliance envelopes (12W, 45W, 75W, 140W)
3. Completeness of Tier 1 essential electrical measurements and resolution bounds
4. Clear architectural distinction across metrology timing tiers (waveform vs per-cycle vs telemetry)
5. Comprehensive evaluation of candidate ICs/modules (ADE9153A, BL0942, PZEM-004T v3) with verified citations
6. Small-load detectability budget invariants and honest feasibility verdicts
7. Ground-truth setup label isolation and synchronization tolerances
8. Safety mandates: galvanic isolation, overcurrent fuse, ENABLE_HARDWARE_INGEST=false
"""

import os
import sys
import json
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_EXPERIMENTS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.abspath(os.path.join(ML_EXPERIMENTS_DIR, ".."))

if ML_EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, ML_EXPERIMENTS_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

REQUIREMENTS_JSON_PATH = os.path.join(
    ML_EXPERIMENTS_DIR, "results", "sensor_requirements.json"
)


class TestSensorRequirements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(
            os.path.exists(REQUIREMENTS_JSON_PATH),
            f"Requirements file not found at {REQUIREMENTS_JSON_PATH}",
        )
        with open(REQUIREMENTS_JSON_PATH, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_metadata_and_non_energized_mandate(self):
        """Verify document metadata and non-energized status."""
        meta = self.data.get("metadata", {})
        self.assertEqual(meta.get("milestone"), "2C.5")
        self.assertEqual(meta.get("base_checkpoint"), "122fd36")
        self.assertIn("Non-Energized", meta.get("status", ""))

    def test_target_appliances_schema_and_ratings(self):
        """Verify target appliances match Energy Mirror canonical ratings."""
        apps = self.data.get("target_appliances", {})
        self.assertIn("bulb_01", apps)
        self.assertIn("fan_01", apps)
        self.assertIn("pump_01", apps)
        self.assertIn("heater_01", apps)

        # Check ratings
        self.assertEqual(apps["bulb_01"]["nominal_active_power_w"], 12.0)
        self.assertEqual(apps["fan_01"]["nominal_active_power_w"], 45.0)
        self.assertEqual(apps["pump_01"]["nominal_active_power_w"], 75.0)
        self.assertEqual(apps["heater_01"]["nominal_active_power_w"], 140.0)

        # Check envelopes
        self.assertEqual(apps["bulb_01"]["tolerance_envelope_w"], [8.0, 16.0])
        self.assertEqual(apps["fan_01"]["tolerance_envelope_w"], [38.0, 52.0])
        self.assertEqual(apps["pump_01"]["tolerance_envelope_w"], [66.0, 84.0])
        self.assertEqual(apps["heater_01"]["tolerance_envelope_w"], [128.0, 152.0])

    def test_tier_1_essential_electrical_measurements(self):
        """Verify all essential electrical quantities are specified with resolution."""
        tier1 = self.data.get("electrical_measurement_requirements", {}).get(
            "tier_1_essential_prototype", {}
        )
        essential_keys = [
            "active_power_w",
            "rms_voltage_v",
            "rms_current_a",
            "apparent_power_va",
            "power_factor",
            "synchronized_timestamp",
            "sensor_quality_indicators",
        ]
        for k in essential_keys:
            self.assertIn(k, tier1, f"Missing essential measurement: {k}")

        self.assertLessEqual(tier1["active_power_w"]["minimum_resolution_w"], 0.1)
        self.assertLessEqual(tier1["rms_voltage_v"]["minimum_resolution_v"], 0.1)
        self.assertLessEqual(tier1["rms_current_a"]["minimum_resolution_a"], 0.001)

    def test_metrology_timing_hierarchy(self):
        """Verify clear separation between waveform sampling, per-cycle metrology, and telemetry."""
        hierarchy = self.data.get("metrology_timing_hierarchy", {})
        self.assertIn("high_frequency_waveform_sampling", hierarchy)
        self.assertIn("per_cycle_electrical_metrology", hierarchy)
        self.assertIn("periodic_telemetry_snapshot", hierarchy)
        self.assertIn("nilm_feature_window", hierarchy)

        # Ensure periodic telemetry snapshot rate is 1s or 6s
        telemetry = hierarchy["periodic_telemetry_snapshot"]
        self.assertIn("6.0 s", telemetry["typical_rate"])

    def test_candidate_architectures_evidence(self):
        """Verify candidate architectures have documented evidence, verified status, and interface specs."""
        cands = self.data.get("candidate_architectures", {})
        self.assertIn("ADE9153A", cands)
        self.assertIn("BL0942", cands)
        self.assertIn("PZEM_004T_V3", cands)

        for name, spec in cands.items():
            self.assertIn("manufacturer", spec)
            self.assertIn("accuracy_spec", spec)
            self.assertIn("digital_interface", spec)
            self.assertIn("isolation_and_safety", spec)
            self.assertIn("suitability_for_12w_detection", spec)
            self.assertIn("evidence_status", spec)
            self.assertIn("VERIFIED", spec["evidence_status"])
            self.assertIsInstance(spec.get("important_unknowns"), list)
            self.assertGreater(len(spec["important_unknowns"]), 0)

    def test_small_load_detectability_budget(self):
        """Verify detectability budget explicitly records honest verdicts."""
        budget = self.data.get("small_load_detectability_budget", {})
        self.assertIn("12w_led_bulb", budget)
        self.assertIn("45w_ceiling_fan", budget)
        self.assertIn("75w_water_pump", budget)

        # 12W must be recognized as not reliably distinguishable
        bulb_verdict = budget["12w_led_bulb"]["detectability_verdict"]
        self.assertIn("NOT RELIABLY DISTINGUISHABLE", bulb_verdict)

        # 75W must require reactive power
        pump_verdict = budget["75w_water_pump"]["detectability_verdict"]
        self.assertIn("FEASIBLE", pump_verdict)

    def test_ground_truth_architecture_and_label_isolation(self):
        """Verify ground-truth architecture enforces label isolation and clock synchronization."""
        gt = self.data.get("ground_truth_architecture", {})
        self.assertIn("aggregate_channel", gt)
        self.assertIn("submeter_reference_channels", gt)
        self.assertIn("timestamp_synchronization", gt)
        self.assertIn("label_isolation_enforcement", gt)

        # Max clock skew must be <= 100 ms
        sync = gt["timestamp_synchronization"]
        self.assertLessEqual(sync["max_acceptable_clock_skew_ms"], 100)

        # Label isolation must explicitly mention exclusion from input feature matrix
        isolation = gt["label_isolation_enforcement"]
        self.assertIn("strictly excluded from the detector input feature matrix", isolation)

    def test_validation_protocol_acceptance_criteria(self):
        """Verify acceptance targets align with Milestone 2C.4 research targets."""
        proto = self.data.get("validation_protocol", {})
        criteria = proto.get("acceptance_criteria", {})
        self.assertEqual(criteria.get("preliminary_event_f1_target"), 0.80)
        self.assertEqual(criteria.get("max_false_alarms_per_hour"), 1.0)
        self.assertEqual(criteria.get("max_relative_energy_total_error_pct"), 15.0)

        # Decision framework must include proceed, repeat, and declare infeasible
        decisions = proto.get("decision_framework", {})
        self.assertIn("proceed_to_integration", decisions)
        self.assertIn("repeat_calibration", decisions)
        self.assertIn("declare_fundamentally_infeasible", decisions)

    def test_safety_and_compliance_constraints(self):
        """Verify safety mandates require isolation, overcurrent protection, and software gate."""
        safety = self.data.get("safety_and_compliance", {})
        self.assertIn("mains_isolation_mandatory", safety)
        self.assertIn("overcurrent_protection", safety)
        self.assertIn("personnel_qualification", safety)
        self.assertIn("software_gate", safety)
        self.assertIn("ENABLE_HARDWARE_INGEST remains FALSE", safety["software_gate"])


if __name__ == "__main__":
    unittest.main()
