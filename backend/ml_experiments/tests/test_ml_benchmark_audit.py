"""
test_ml_benchmark_audit.py - Unit tests for NILM event extraction, matching, and audit metrics.

Compatible with both pytest and unittest:
1. Contiguous ON event extraction and boundary edge handling
2. Gap merging tolerance behavior for sensor dropouts
3. Bipartite greedy one-to-one event matching
4. Detection delay and temporal onset tolerance enforcement
5. Sub-population regression MAE/RMSE mathematical decomposition
6. Relative energy total error (RETE) calculations
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Import from ml_experiments
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from evaluate_events import extract_events, match_events


class TestEventBenchmarkAudit(unittest.TestCase):
    def test_extract_events_empty_and_all_zero(self):
        """Verify event extraction handles empty or inactive series gracefully."""
        empty_series = pd.Series([], dtype=int)
        self.assertEqual(extract_events(empty_series), [])

        idx = pd.date_range("2026-10-21 00:00:00", periods=50, freq="6s")
        zero_series = pd.Series(0, index=idx)
        self.assertEqual(extract_events(zero_series), [])

    def test_extract_events_contiguous_segments(self):
        """Verify contiguous segments extract correct boundaries, durations, and sample counts."""
        idx = pd.date_range("2026-10-21 00:00:00", periods=10, freq="6s")
        # Pattern: 0, 1, 1, 1, 0, 0, 1, 1, 0, 0
        data = [0, 1, 1, 1, 0, 0, 1, 1, 0, 0]
        s = pd.Series(data, index=idx)

        events = extract_events(s, min_duration_s=0.0, max_gap_s=0.0)
        self.assertEqual(len(events), 2)

        ev1 = events[0]
        self.assertEqual(ev1["event_id"], 1)
        self.assertEqual(ev1["start"], idx[1])
        self.assertEqual(ev1["end"], idx[3])
        self.assertEqual(ev1["duration_s"], 18.0)
        self.assertEqual(ev1["sample_count"], 3)

        ev2 = events[1]
        self.assertEqual(ev2["event_id"], 2)
        self.assertEqual(ev2["start"], idx[6])
        self.assertEqual(ev2["end"], idx[7])
        self.assertEqual(ev2["duration_s"], 12.0)
        self.assertEqual(ev2["sample_count"], 2)

    def test_extract_events_boundary_at_start_and_end(self):
        """Verify series starting with ON or ending with ON are cleanly bounded."""
        idx = pd.date_range("2026-10-21 00:00:00", periods=5, freq="6s")
        # Starts ON, toggles OFF, toggles ON at the end
        data = [1, 1, 0, 0, 1]
        s = pd.Series(data, index=idx)

        events = extract_events(s)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["start"], idx[0])
        self.assertEqual(events[0]["end"], idx[1])
        self.assertEqual(events[1]["start"], idx[4])
        self.assertEqual(events[1]["end"], idx[4])

    def test_extract_events_gap_merging(self):
        """Verify small sensor dropouts can be merged into unified cycles when configured."""
        idx = pd.date_range("2026-10-21 00:00:00", periods=12, freq="6s")
        # Pattern: ON for 2 samples, OFF for 2 samples (12s gap), ON for 2 samples
        data = [0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0]
        s = pd.Series(data, index=idx)

        # Without merging: 2 distinct events
        events_raw = extract_events(s, max_gap_s=0.0)
        self.assertEqual(len(events_raw), 2)

        # With gap_merge=6s: 12s gap is not merged (still 2 events)
        events_no_merge = extract_events(s, max_gap_s=6.0)
        self.assertEqual(len(events_no_merge), 2)

        # With gap_merge=20s: 12s gap IS merged (1 combined cycle)
        events_merged = extract_events(s, max_gap_s=20.0)
        self.assertEqual(len(events_merged), 1)
        self.assertEqual(events_merged[0]["start"], idx[1])
        self.assertEqual(events_merged[0]["end"], idx[6])
        self.assertEqual(events_merged[0]["sample_count"], 4)

    def test_match_events_perfect_one_to_one(self):
        """Verify identical events produce precision=1.0, recall=1.0, delay=0.0."""
        t0 = pd.Timestamp("2026-10-21 06:00:00")
        t1 = pd.Timestamp("2026-10-21 06:15:00")
        gt = [
            {"event_id": 1, "start": t0, "end": t0 + timedelta(minutes=10), "duration_s": 600, "sample_count": 100},
            {"event_id": 2, "start": t1, "end": t1 + timedelta(minutes=5), "duration_s": 300, "sample_count": 50},
        ]
        pred = [
            {"event_id": 1, "start": t0, "end": t0 + timedelta(minutes=10), "duration_s": 600, "sample_count": 100},
            {"event_id": 2, "start": t1, "end": t1 + timedelta(minutes=5), "duration_s": 300, "sample_count": 50},
        ]

        res = match_events(gt, pred, tolerance_s=60.0, test_duration_days=1.0)
        self.assertEqual(res["tp"], 2)
        self.assertEqual(res["fp"], 0)
        self.assertEqual(res["fn"], 0)
        self.assertEqual(res["precision"], 1.0)
        self.assertEqual(res["recall"], 1.0)
        self.assertEqual(res["f1_score"], 1.0)
        self.assertEqual(res["mean_delay_s"], 0.0)

    def test_match_events_one_to_one_enforcement(self):
        """Verify that multiple predicted events cannot match the same ground truth event."""
        t0 = pd.Timestamp("2026-10-21 06:00:00")
        # Single GT event
        gt = [
            {"event_id": 1, "start": t0, "end": t0 + timedelta(minutes=10), "duration_s": 600, "sample_count": 100},
        ]
        # Two predicted events overlapping with the same single GT event
        pred = [
            {"event_id": 1, "start": t0 + timedelta(seconds=6), "end": t0 + timedelta(minutes=4), "duration_s": 240, "sample_count": 40},
            {"event_id": 2, "start": t0 + timedelta(minutes=5), "end": t0 + timedelta(minutes=9), "duration_s": 240, "sample_count": 40},
        ]

        res = match_events(gt, pred, tolerance_s=60.0, test_duration_days=1.0)
        # Strictly one-to-one: 1 TP, 1 FP (not 2 TP)
        self.assertEqual(res["tp"], 1)
        self.assertEqual(res["fp"], 1)
        self.assertEqual(res["fn"], 0)
        self.assertEqual(res["precision"], 0.5)
        self.assertEqual(res["recall"], 1.0)

    def test_match_events_tolerance_rejection(self):
        """Verify predicted events outside the temporal tolerance are rejected as false alarms."""
        t0 = pd.Timestamp("2026-10-21 06:00:00")
        t_distant = pd.Timestamp("2026-10-21 07:00:00")  # 1 hour later

        gt = [{"event_id": 1, "start": t0, "end": t0 + timedelta(minutes=5), "duration_s": 300, "sample_count": 50}]
        pred = [{"event_id": 1, "start": t_distant, "end": t_distant + timedelta(minutes=5), "duration_s": 300, "sample_count": 50}]

        res = match_events(gt, pred, tolerance_s=60.0, test_duration_days=1.0)
        self.assertEqual(res["tp"], 0)
        self.assertEqual(res["fp"], 1)
        self.assertEqual(res["fn"], 1)
        self.assertEqual(res["precision"], 0.0)
        self.assertEqual(res["recall"], 0.0)

    def test_regression_mae_decomposition(self):
        """Verify the mathematical identity: Overall MAE = w_active * MAE_active + w_inactive * MAE_inactive."""
        np.random.seed(42)
        n_samples = 1000
        n_active = 10  # 1% prevalence

        y_true = np.zeros(n_samples, dtype=float)
        y_true[:n_active] = 650.0  # active power

        y_pred = np.zeros(n_samples, dtype=float)
        y_pred[:n_active] = 200.0  # underestimating
        y_pred[n_active:] = 2.0    # idle drift

        mae_all = float(np.mean(np.abs(y_true - y_pred)))
        mae_active = float(np.mean(np.abs(y_true[:n_active] - y_pred[:n_active])))
        mae_inactive = float(np.mean(np.abs(y_true[n_active:] - y_pred[n_active:])))

        w_active = n_active / n_samples
        w_inactive = (n_samples - n_active) / n_samples

        reconstructed_mae = w_active * mae_active + w_inactive * mae_inactive
        self.assertAlmostEqual(mae_all, reconstructed_mae, places=7)
        self.assertEqual(mae_active, 450.0)
        self.assertEqual(mae_inactive, 2.0)
        self.assertAlmostEqual(mae_all, 6.48, places=2)

    def test_rete_zero_baseline(self):
        """Verify Relative Energy Total Error is 100% when model predicts zero energy."""
        p_true = np.array([600.0, 600.0, 600.0])
        p_pred = np.array([0.0, 0.0, 0.0])

        true_energy = float(np.sum(p_true)) * (6.0 / 3600.0)
        pred_energy = float(np.sum(p_pred)) * (6.0 / 3600.0)
        rete = abs(pred_energy - true_energy) / true_energy * 100.0
        self.assertEqual(rete, 100.0)


if __name__ == "__main__":
    unittest.main()
