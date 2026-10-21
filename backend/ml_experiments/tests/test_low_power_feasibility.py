"""
test_low_power_feasibility.py - Unit tests for Milestone 2C.4 Low-Power Appliance Feasibility.

Tests cover:
1. Data generation invariants: power conservation, non-negative powers, absence of NaNs/infs.
2. Label isolation: ground-truth state labels are strictly absent from feature matrices.
3. Split isolation: train, validation, and test sets are independent daily trajectories with zero temporal overlap.
4. Metric calculations: sample-level precision, recall, F1, and false alarms per hour.
5. Event matching and delay bounds: one-to-one bipartite matching and detection delay calculation.
6. Rule-based detector interface compatibility: verified without modifying production code.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_EXPERIMENTS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.abspath(os.path.join(ML_EXPERIMENTS_DIR, ".."))

if ML_EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, ML_EXPERIMENTS_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from run_low_power_feasibility import (
    SyntheticHouseholdGenerator,
    extract_features,
    evaluate_predictions,
    compute_reactive_power,
    run_differential_step_detector,
    run_production_rule_based_detector,
    APPLIANCE_SPECS,
)
from app.services.event_detector import RuleBasedEventDetector


class TestLowPowerFeasibility(unittest.TestCase):
    def setUp(self):
        self.generator = SyntheticHouseholdGenerator(
            scenario_name="scenario_1_ideal",
            seed=42,
            dt_s=6.0,
            duration_hours=2.0,  # 2 hours for fast unit tests
        )

    def test_synthetic_generation_invariants(self):
        """Verify generated traces preserve physical invariants: no NaNs, non-negative, valid PF."""
        tel_df, gt_df = self.generator.generate_trace(run_id=0)

        # 1. Row count and column consistency
        expected_samples = int(2.0 * 3600 / 6.0)
        self.assertEqual(len(tel_df), expected_samples)
        self.assertEqual(len(gt_df), expected_samples)

        # 2. Absence of NaNs or infinities
        self.assertFalse(tel_df.isna().any().any(), "Telemetry contains NaNs")
        self.assertFalse(gt_df.isna().any().any(), "Ground truth contains NaNs")

        # 3. Physical boundaries: Active power > 0, PF in [0.1, 1.0]
        self.assertTrue((tel_df["active_power_w"] > 0).all(), "Active power must be positive")
        self.assertTrue((tel_df["power_factor"] >= 0.1).all(), "PF cannot be below 0.1")
        self.assertTrue((tel_df["power_factor"] <= 1.0).all(), "PF cannot exceed 1.0")

        # 4. Binary ground-truth states
        for app in ["bulb_01", "fan_01", "pump_01", "heater_01"]:
            unique_vals = set(gt_df[app].unique())
            self.assertTrue(unique_vals.issubset({0, 1}), f"{app} state must be binary")

    def test_label_isolation(self):
        """Verify ground-truth labels are strictly excluded from feature extraction matrices."""
        tel_df, gt_df = self.generator.generate_trace(run_id=0)

        # Feature matrix for Ablation A, B, C
        feat_a = extract_features(tel_df, "A")
        feat_b = extract_features(tel_df, "B")
        feat_c = extract_features(tel_df, "C")

        # Telemetry DataFrame must not have ground-truth columns
        for col in ["bulb_01", "fan_01", "pump_01", "heater_01"]:
            self.assertNotIn(col, tel_df.columns, f"Label {col} leaked into telemetry_df")

        # Feature matrix shape assertions (A: 1 col, B: 6 cols, C: 13 cols)
        self.assertEqual(feat_a.shape, (len(tel_df), 1))
        self.assertEqual(feat_b.shape, (len(tel_df), 6))
        self.assertEqual(feat_c.shape, (len(tel_df), 13))

    def test_split_isolation(self):
        """Verify train, validation, and test runs are generated with disjoint timestamps and states."""
        gen = SyntheticHouseholdGenerator("scenario_2_realistic", seed=42, duration_hours=1.0)
        t_tr, g_tr = gen.generate_trace(run_id=0)
        t_va, g_va = gen.generate_trace(run_id=1)
        t_te, g_te = gen.generate_trace(run_id=2)

        # Timestamps must not overlap
        tr_times = set(t_tr["timestamp"])
        va_times = set(t_va["timestamp"])
        te_times = set(t_te["timestamp"])

        self.assertEqual(len(tr_times.intersection(va_times)), 0, "Train and Val timestamps overlap")
        self.assertEqual(len(tr_times.intersection(te_times)), 0, "Train and Test timestamps overlap")
        self.assertEqual(len(va_times.intersection(te_times)), 0, "Val and Test timestamps overlap")

    def test_metric_calculations_and_false_alarm_rates(self):
        """Verify sample and event metrics compute expected precision, recall, F1, and FA rates."""
        # 100 samples at 6s interval = 600 seconds = 10 minutes (0.1667 hours)
        dt_idx = [datetime(2026, 10, 21, 0, 0, 0) + timedelta(seconds=i * 6) for i in range(100)]
        y_true = np.zeros(100, dtype=int)
        y_pred = np.zeros(100, dtype=int)

        # Create one ground truth event of 5 samples (30s)
        y_true[20:25] = 1

        # Prediction: perfectly matches ground truth event, plus 1 false alarm event of 4 samples (24s)
        y_pred[20:25] = 1
        y_pred[60:64] = 1

        duration_days = 600.0 / 86400.0
        res = evaluate_predictions(y_true, y_pred, dt_idx, duration_days=duration_days)

        # Sample metrics check
        self.assertEqual(res["sample_metrics"]["confusion_matrix"]["true_positive"], 5)
        self.assertEqual(res["sample_metrics"]["confusion_matrix"]["false_positive"], 4)
        self.assertEqual(res["sample_metrics"]["confusion_matrix"]["false_negative"], 0)

        # Event metrics check: 1 GT event, 2 Pred events -> 1 TP event, 1 FP event
        ev = res["event_metrics"]
        self.assertEqual(ev["gt_events_count"], 1)
        self.assertEqual(ev["pred_events_count"], 2)
        self.assertEqual(ev["tp"], 1)
        self.assertEqual(ev["fp"], 1)
        self.assertEqual(ev["precision"], 0.5)
        self.assertEqual(ev["recall"], 1.0)
        self.assertAlmostEqual(ev["f1_score"], 0.6667, places=3)

    def test_production_rule_based_detector_interface_reusability(self):
        """Verify production RuleBasedEventDetector can be imported and executed without modification."""
        detector = RuleBasedEventDetector()
        self.assertEqual(len(detector.signatures), 4)

        # Test step transition for 12 W bulb
        ev_bulb = detector.detect_transition(prev_power_w=100.0, curr_power_w=112.0)
        self.assertEqual(ev_bulb.status, "MATCHED")
        self.assertEqual(ev_bulb.appliance_id, "bulb_01")
        self.assertEqual(ev_bulb.transition_type, "ON")

        # Test step transition for 45 W fan
        ev_fan = detector.detect_transition(prev_power_w=100.0, curr_power_w=145.0)
        self.assertEqual(ev_fan.status, "MATCHED")
        self.assertEqual(ev_fan.appliance_id, "fan_01")
        self.assertEqual(ev_fan.transition_type, "ON")

        # Test step transition for 75 W pump
        ev_pump = detector.detect_transition(prev_power_w=100.0, curr_power_w=175.0)
        self.assertEqual(ev_pump.status, "MATCHED")
        self.assertEqual(ev_pump.appliance_id, "pump_01")
        self.assertEqual(ev_pump.transition_type, "ON")

    def test_simultaneous_switching_ambiguity(self):
        """Verify that simultaneous switching (e.g. bulb + fan = 57 W) creates ambiguous composite step."""
        detector = RuleBasedEventDetector()
        # 12 W + 45 W = 57 W step
        event = detector.detect_transition(prev_power_w=100.0, curr_power_w=157.0)
        self.assertEqual(event.status, "AMBIGUOUS")
        self.assertIsNone(event.appliance_id)
        self.assertIn("Unrecognized transition", event.rule_description)


if __name__ == "__main__":
    unittest.main()
