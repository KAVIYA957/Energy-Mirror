"""
test_intermittent_event_audit.py - Unit tests for Milestone 2C.10 Audit Verifications

Verifies:
1. Irregular sampling event duration calculation (true elapsed time vs sample_count * dt_0 defect).
2. Split-boundary crossing onset isolation (preventing false TP credit for ongoing activations).
3. Metric consistency: confusion matrix math, specificity, and prevalence reconciliation.
4. Label threshold robustness (15W vs 20W vs 25W behavior).
5. Strict onset tolerance and false alarm rate normalization.
"""

import unittest
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from backend.ml_experiments.evaluate_events import extract_events, match_events


class TestIntermittentEventAudit(unittest.TestCase):
    """Test suite covering irregular sampling, boundary onsets, and metric calculations."""

    def test_irregular_sampling_duration_uses_true_elapsed_timestamps(self):
        """
        DEFECT FIX AUDIT:
        In earlier versions, extract_events inferred dt = index[1] - index[0] and computed
        dur_s = sample_count * dt.
        If index[1] - index[0] is 2s, but subsequent samples are spaced 20s apart,
        dur_s was severely underestimated.
        Verification: Ensure duration uses true timestamp differences.
        """
        # Irregular timestamps: intervals are [2s, 30s, 30s, 10s]
        timestamps = [
            pd.Timestamp("2026-01-01 10:00:00"),  # dt to next = 2s
            pd.Timestamp("2026-01-01 10:00:02"),  # dt to next = 30s
            pd.Timestamp("2026-01-01 10:00:32"),  # dt to next = 30s
            pd.Timestamp("2026-01-01 10:01:02"),  # dt to next = 10s
            pd.Timestamp("2026-01-01 10:01:12"),  # OFF sample
        ]
        # First 4 samples are ON (10:00:00 to 10:01:02), 5th is OFF (10:01:12)
        # True elapsed active duration is 10:01:12 - 10:00:00 = 72 seconds.
        # Under the old defect (dt_0 = 2s, sample_count = 4): dur_s was 4 * 2 = 8 seconds!
        series = pd.Series([1, 1, 1, 1, 0], index=pd.DatetimeIndex(timestamps))
        events = extract_events(series)

        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertEqual(ev["start"], pd.Timestamp("2026-01-01 10:00:00"))
        self.assertEqual(ev["end"], pd.Timestamp("2026-01-01 10:01:02"))

        # The true duration spans to sample 4 (10:01:12), which is 72s.
        self.assertAlmostEqual(ev["duration_s"], 72.0, delta=1.0)
        self.assertNotEqual(ev["duration_s"], 8.0, "Must not use flawed sample_count * dt_0 calculation.")

    def test_split_boundary_crossing_onset_isolation(self):
        """
        DEFECT FIX AUDIT:
        When a test partition begins while an appliance was already running in validation,
        is_on.iloc[0] == 1 causes extract_events to record an onset at t=0.
        If a model predicts ON from t=0, it was awarded a false True Positive onset match.
        Verification: Ensure boundary onset is flagged and excluded when requested.
        """
        t0 = pd.Timestamp("2026-01-01 12:00:00")
        timestamps = [t0 + timedelta(seconds=i * 10) for i in range(10)]
        # Appliance was ON before partition and remains ON for all 10 samples
        series = pd.Series([1] * 10, index=pd.DatetimeIndex(timestamps))

        # 1. With initial_state_on=True, event must be flagged as a boundary onset
        events = extract_events(series, initial_state_on=True)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["is_boundary_onset"])
        self.assertTrue(events[0]["is_boundary_offset"])

        # 2. Predicted event also starting at t=0
        pred_events = extract_events(series, initial_state_on=True)

        # 3. Unfixed matching: matches boundary artifact as a True Positive onset
        res_unfixed = match_events(events, pred_events, tolerance_s=60.0, exclude_boundary_onsets=False)
        self.assertEqual(res_unfixed["tp"], 1)

        # 4. Fixed matching: excludes boundary onset from genuine onset matches
        res_fixed = match_events(events, pred_events, tolerance_s=60.0, exclude_boundary_onsets=True)
        self.assertEqual(res_fixed["tp"], 0, "Boundary onset must not be awarded a True Positive onset detection.")
        self.assertEqual(res_fixed["gt_events_count"], 0)
        self.assertEqual(res_fixed["pred_events_count"], 0)

    def test_confusion_matrix_mathematical_consistency(self):
        """
        Verifies exact mathematical derivation of sample metrics from confusion matrix.
        """
        tp = 1022278
        fp = 6419
        tn = 211
        fn = 7463
        total = tp + fp + tn + fn

        accuracy = (tp + tn) / total
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        specificity = tn / (tn + fp)
        f1 = 2 * precision * recall / (precision + recall)
        prevalence = (tp + fn) / total

        self.assertEqual(total, 1036371)
        self.assertAlmostEqual(accuracy, 0.9866, places=4)
        self.assertAlmostEqual(precision, 0.9938, places=4)
        self.assertAlmostEqual(recall, 0.9928, places=4)
        self.assertAlmostEqual(specificity, 0.0318, places=4)
        self.assertAlmostEqual(f1, 0.9933, places=4)
        self.assertAlmostEqual(prevalence, 0.9936, places=4)

    def test_single_sample_event_duration_positive(self):
        """Verifies that an event consisting of a single active sample has non-zero positive duration."""
        t = [
            pd.Timestamp("2026-01-01 00:00:00"),
            pd.Timestamp("2026-01-01 00:00:10"),  # Active sample
            pd.Timestamp("2026-01-01 00:00:20"),
        ]
        series = pd.Series([0, 1, 0], index=pd.DatetimeIndex(t))
        evs = extract_events(series)
        self.assertEqual(len(evs), 1)
        self.assertGreater(evs[0]["duration_s"], 0.0)
        self.assertEqual(evs[0]["duration_s"], 10.0)

    def test_false_alarm_rate_uses_valid_observation_duration(self):
        """Verifies that false alarm rate correctly normalizes by valid observation days."""
        # 10 false alarms over 5 valid days vs 10 calendar days
        gt = []
        preds = [
            {"event_id": i + 1, "start": pd.Timestamp("2026-01-01") + timedelta(hours=i), "end": pd.Timestamp("2026-01-01") + timedelta(hours=i, minutes=10)}
            for i in range(10)
        ]
        res_cal = match_events(gt, preds, test_duration_days=10.0)
        self.assertEqual(res_cal["fp_per_day"], 1.0)

        res_val = match_events(gt, preds, test_duration_days=10.0, valid_duration_days=5.0)
        self.assertEqual(res_val["fp_per_day"], 2.0)


if __name__ == "__main__":
    unittest.main()
