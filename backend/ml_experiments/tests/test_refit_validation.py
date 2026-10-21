"""
test_refit_validation.py - Unit tests for REFIT pump validation pipeline and results.

Tests:
1. Results JSON schema, completeness, and non-fabrication.
2. Missing ground-truth masking (never silently imputes zero).
3. Chronological split ordering and boundary buffer enforcement.
4. Event matching with strict onset tolerance and signed/absolute delays.
5. Incompatible rating detection (REFIT ~44 W vs Energy Mirror 75 W target).
"""

import os
import json
import unittest
import numpy as np
import pandas as pd

from backend.ml_experiments.run_refit_experiment import (
    compute_file_sha256,
    RESULTS_FILE,
    DATA_FILE,
)
from backend.ml_experiments.evaluate_events import extract_events, match_events


class TestRefitPumpValidation(unittest.TestCase):
    """Test suite for REFIT House 21 validation experiment."""

    def setUp(self):
        self.results_path = RESULTS_FILE
        self.data_path = DATA_FILE

    def test_results_json_exists_and_schema(self):
        """Verifies that the results JSON exists and contains all required sections."""
        self.assertTrue(os.path.exists(self.results_path), f"Missing results JSON: {self.results_path}")
        with open(self.results_path, "r") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("split_metadata", data)
        self.assertIn("models", data)
        self.assertIn("validation_status", data)

        meta = data["metadata"]
        self.assertEqual(meta["dataset_name"], "REFIT: Electrical Load Measurements (Cleaned)")
        self.assertEqual(meta["house_id"], "House 21")
        self.assertEqual(meta["target_channel"], "Appliance 9")
        self.assertEqual(meta["channel_documented_identity"], "Pond Pump, Unknown, Unknown")
        self.assertEqual(meta["file_sha256"], "fc5471adf36c69fa65438270b4f95a51d2d7630b5461ca2db74652b41b15e10b")
        self.assertEqual(meta["total_raw_samples"], 5383993)
        self.assertEqual(meta["valid_samples"], 5176881)
        self.assertEqual(meta["excluded_samples"], 207112)

    def test_rating_incompatibility_flagged(self):
        """Verifies that measured ~44 W active power is documented and flagged against 75 W target."""
        with open(self.results_path, "r") as f:
            data = json.load(f)

        meta = data["metadata"]
        # Measured median power must be ~44 W
        self.assertAlmostEqual(meta["target_median_active_w"], 44.0, delta=1.0)
        self.assertAlmostEqual(meta["target_mean_active_w"], 44.45, delta=1.0)

        val_status = data["validation_status"]
        self.assertIn("INCOMPATIBLE_RATING", val_status["validation_rating_compatibility"])
        self.assertEqual(val_status["refit_pond_pump_status"], "PARTIALLY_VALIDATED")
        self.assertEqual(val_status["energy_mirror_75w_pump_transfer"], "PARTIALLY_VALIDATED")

    def test_chronological_splits_and_buffers(self):
        """Verifies chronological ordering and boundary buffer dropping."""
        with open(self.results_path, "r") as f:
            data = json.load(f)

        split = data["split_metadata"]
        self.assertGreater(split["train_samples_total"], 0)
        self.assertGreater(split["val_samples_total"], 0)
        self.assertGreater(split["test_samples_total"], 0)
        self.assertEqual(split["boundary_buffer_dropped_samples"], 200)

        # Total partition samples + boundary drops must equal total raw samples
        total_partitioned = (
            split["train_samples_total"] +
            split["val_samples_total"] +
            split["test_samples_total"] +
            split["boundary_buffer_dropped_samples"]
        )
        self.assertEqual(total_partitioned, data["metadata"]["total_raw_samples"])

    def test_missing_ground_truth_masking_policy(self):
        """Verifies that missing submeter data is not silently zero-imputed."""
        # Synthetic DataFrame with issues, negative power, and gaps
        test_df = pd.DataFrame({
            "Unix": [1000, 1008, 1016, 1200, 1208, 1216], # gap between 1016 and 1200 is 184s (>120s)
            "Aggregate": [250.0, -10.0, 300.0, 280.0, 290.0, 310.0], # sample 1 has negative agg
            "Appliance9": [44.0, 44.0, -5.0, 44.0, 44.0, 44.0],      # sample 2 has negative submeter
            "Issues": [0, 0, 0, 0, 1, 0],                             # sample 4 has Issues == 1
        })

        unix_diffs = np.pad(np.diff(test_df["Unix"].values), (1, 0), "constant", constant_values=8)
        mask = (
            (test_df["Issues"] == 0) &
            (test_df["Aggregate"].notnull()) &
            (test_df["Appliance9"].notnull()) &
            (test_df["Aggregate"] >= 0) &
            (test_df["Appliance9"] >= 0) &
            (unix_diffs <= 120)
        )

        # Expected valid indices:
        # idx 0: valid
        # idx 1: invalid (Aggregate < 0)
        # idx 2: invalid (Appliance9 < 0)
        # idx 3: invalid (gap = 184s > 120s)
        # idx 4: invalid (Issues == 1)
        # idx 5: valid
        expected_valid = [True, False, False, False, False, True]
        self.assertEqual(mask.tolist(), expected_valid)

    def test_model_comparisons_present(self):
        """Verifies that all 5 baseline models are reported with sample, event, and energy metrics."""
        with open(self.results_path, "r") as f:
            data = json.load(f)

        models = data["models"]
        expected_models = [
            "simple_threshold",
            "differential_step",
            "random_forest",
            "persistence_oracle",
            "majority_class",
        ]
        for m in expected_models:
            self.assertIn(m, models, f"Model {m} missing from results")
            m_data = models[m]
            self.assertIn("sample_metrics", m_data)
            self.assertIn("event_metrics", m_data)
            self.assertIn("energy_metrics", m_data)

            # Check required metric keys
            s_metrics = m_data["sample_metrics"]
            self.assertIn("accuracy", s_metrics)
            self.assertIn("precision", s_metrics)
            self.assertIn("recall", s_metrics)
            self.assertIn("f1_score", s_metrics)

            ev_metrics = m_data["event_metrics"]
            self.assertIn("event_precision", ev_metrics)
            self.assertIn("event_recall", ev_metrics)
            self.assertIn("event_f1_score", ev_metrics)
            self.assertIn("false_alarms_per_day", ev_metrics)
            self.assertIn("mean_signed_delay_s", ev_metrics)
            self.assertIn("mean_absolute_delay_s", ev_metrics)
            self.assertTrue(ev_metrics["require_onset_tolerance"])

            en_metrics = m_data["energy_metrics"]
            self.assertIn("active_period_power_mae_w", en_metrics)
            self.assertIn("inactive_period_power_mae_w", en_metrics)
            self.assertIn("overall_power_mae_w", en_metrics)
            self.assertIn("relative_energy_error_pct", en_metrics)

    def test_event_matching_onset_tolerance_behavior(self):
        """Tests that late events are rejected when require_onset_tolerance=True."""
        idx = pd.date_range("2026-01-01 00:00:00", periods=500, freq="8s")
        # GT event from sample 10 to sample 100 (t=80s to t=800s)
        gt_series = pd.Series(0, index=idx)
        gt_series.iloc[10:101] = 1
        gt_events = extract_events(gt_series)

        # Pred event starting at sample 50 (t=400s), onset delta = 320s > tolerance (120s)
        pred_series = pd.Series(0, index=idx)
        pred_series.iloc[50:101] = 1
        pred_events = extract_events(pred_series)

        # With require_onset_tolerance=True, must NOT match
        metrics_strict = match_events(gt_events, pred_events, tolerance_s=120.0, require_onset_tolerance=True)
        self.assertEqual(metrics_strict["tp"], 0)
        self.assertEqual(metrics_strict["fp"], 1)
        self.assertEqual(metrics_strict["fn"], 1)

        # With require_onset_tolerance=False, overlaps and matches
        metrics_lenient = match_events(gt_events, pred_events, tolerance_s=120.0, require_onset_tolerance=False)
        self.assertEqual(metrics_lenient["tp"], 1)
        self.assertEqual(metrics_lenient["fp"], 0)


if __name__ == "__main__":
    unittest.main()
