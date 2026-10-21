"""
test_real_data_validation.py - Comprehensive Unit Tests for Milestone 2C.7.

Validates the integrity, reproducibility, and scientific claims of the
real-world NILM validation pipeline and low-power 12 W LED investigation.
"""

import os
import json
import unittest
from typing import Dict, Any

RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "results",
    "real_data_validation.json",
)


class TestRealDataValidation(unittest.TestCase):
    """Test suite for Milestone 2C.7 real-data NILM validation."""

    @classmethod
    def setUpClass(cls):
        """Loads the serialized validation results."""
        if not os.path.exists(RESULTS_PATH):
            raise FileNotFoundError(
                f"Results file missing: {RESULTS_PATH}. Run run_real_data_validation.py first."
            )
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            cls.results: Dict[str, Any] = json.load(f)

    def test_top_level_structure(self):
        """Verifies that all required top-level sections exist."""
        required_keys = [
            "milestone",
            "title",
            "timestamp_utc",
            "dataset_inventory",
            "data_synchronization",
            "chronological_splits",
            "real_data_baselines",
            "pipeline_improvement",
            "low_power_12w_led_investigation",
            "production_safety_invariants",
            "recommended_next_steps",
        ]
        for key in required_keys:
            self.assertIn(key, self.results, f"Missing key: {key}")
        self.assertEqual(self.results["milestone"], "2C.7")

    def test_appliance_inventory_and_status_invariants(self):
        """
        Verifies that Energy Mirror's four simulated appliances are truthfully mapped
        and that unrepresented or incompatible loads are strictly flagged.
        """
        mapping = self.results["dataset_inventory"]["appliance_mapping"]
        self.assertIn("water_heater_140w", mapping)
        self.assertIn("water_pump_75w", mapping)
        self.assertIn("ceiling_fan_45w", mapping)
        self.assertIn("led_bulb_12w", mapping)

        # 140 W Water Heater
        self.assertEqual(mapping["water_heater_140w"]["status"], "NOT_VALIDATED")
        self.assertIsNone(mapping["water_heater_140w"]["dataset_match"])

        # 75 W Water Pump
        self.assertIn(
            mapping["water_pump_75w"]["status"],
            ["INCOMPATIBLE_RATING", "NOT_VALIDATED"],
        )
        self.assertEqual(mapping["water_pump_75w"]["dataset_match"], "/building1/elec/meter12")
        self.assertGreater(mapping["water_pump_75w"]["measured_mean_active_w"], 500.0)

        # 45 W Ceiling Fan
        self.assertEqual(mapping["ceiling_fan_45w"]["status"], "NOT_VALIDATED")
        self.assertIsNone(mapping["ceiling_fan_45w"]["dataset_match"])

        # 12 W LED Bulb
        self.assertEqual(mapping["led_bulb_12w"]["status"], "NOT_VALIDATED")
        self.assertIsNone(mapping["led_bulb_12w"]["dataset_match"])

    def test_chronological_splits_and_leakage_prevention(self):
        """Verifies strict chronological splitting and boundary buffer isolation."""
        splits = self.results["chronological_splits"]
        self.assertGreater(splits["train_samples"], 250000)
        self.assertGreater(splits["val_samples"], 90000)
        self.assertGreater(splits["test_samples"], 90000)
        self.assertEqual(splits["boundary_buffer_dropped_samples"], 200)

        # Chronological order verification
        self.assertLess(splits["train_end"], splits["val_start"])
        self.assertLess(splits["val_end"], splits["test_start"])

    def test_baseline_models_evaluated(self):
        """Verifies all required classification and regression baselines."""
        cls_baselines = self.results["real_data_baselines"]["classification"]
        expected_cls = [
            "persistence",
            "random_forest",
            "differential_step",
            "simple_threshold",
            "majority_class",
        ]
        for m in expected_cls:
            self.assertIn(m, cls_baselines, f"Missing classification model: {m}")
            self.assertIn("sample_level", cls_baselines[m])
            self.assertIn("event_level", cls_baselines[m])

        # Persistence must be documented as oracle
        self.assertIn("oracle", cls_baselines["persistence"]["description"].lower())

        reg_baselines = self.results["real_data_baselines"]["regression"]
        expected_reg = ["random_forest_regressor", "mean_active_baseline", "zero_baseline"]
        for m in expected_reg:
            self.assertIn(m, reg_baselines, f"Missing regression model: {m}")
            self.assertIn("mae_active_w", reg_baselines[m])
            self.assertIn("mae_inactive_w", reg_baselines[m])

    def test_pipeline_improvement_false_alarm_reduction(self):
        """Verifies that the noise-aware detector reduces false alarms on real test data."""
        imp = self.results["pipeline_improvement"]["held_out_test_comparison"]
        naive_fa = imp["naive_differential_step"]["false_alarms_per_day"]
        improved_fa = imp["noise_aware_hysteresis_detector"]["false_alarms_per_day"]

        # Improved detector must reduce false alarms per day relative to naive differential step
        self.assertLess(improved_fa, naive_fa)
        self.assertGreaterEqual(imp["false_alarm_reduction_percentage"], 20.0)

    def test_12w_led_three_question_framework(self):
        """Verifies the three-question LED identifiability framework."""
        led = self.results["low_power_12w_led_investigation"]
        tq = led["three_question_framework"]

        # Question 1: Metrology measurement
        self.assertEqual(tq["question_1"]["verdict"], "YES")

        # Question 2: Detect 12 W change on mains
        self.assertIn("NO", tq["question_2"]["verdict"])

        # Question 3: Unique attribution to LED
        self.assertIn("NO", tq["question_3"]["verdict"])

        # Empirical noise and SNR invariants
        noise_6s = led["empirical_mains_noise"]["resolution_6s"]
        self.assertGreater(noise_6s["delta_p_std_w"], 15.0)
        self.assertLess(noise_6s["snr_for_12w_step"], 1.0)

    def test_production_safety_invariants(self):
        """Verifies strict adherence to safety and non-hardware constraints."""
        safety = self.results["production_safety_invariants"]
        self.assertFalse(safety["ENABLE_HARDWARE_INGEST"])
        self.assertFalse(safety["hardware_purchased"])
        self.assertFalse(safety["physical_connections_made"])
        self.assertFalse(safety["production_rule_based_detector_modified"])
        self.assertFalse(safety["simulator_appliance_ratings_modified"])
        self.assertFalse(safety["synthetic_results_claimed_as_real"])


if __name__ == "__main__":
    unittest.main()
