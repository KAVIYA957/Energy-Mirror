"""
test_iawe_motor_validation.py - Unit tests for Milestone 2C.11 iAWE validation.

Verifies:
1. CurrentCost sensor overflow sentinel filtering (32767.0 W).
2. Threshold bimodal deadband stability (150 W to 300 W).
3. Cycle gap merging against RF packet-drop fragmentation.
4. Majority class baseline invariants (0 false alarms, 0 recall).
5. Differential step baseline vulnerability to concurrent loads.
6. Detection delay calculation and temporal tolerance bounds.
"""

import unittest
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from backend.ml_experiments.evaluate_events import extract_events, match_events


class TestIAWEMotorValidation(unittest.TestCase):
    """Test suite covering iAWE intermittent water motor evaluation physics."""

    def test_sentinel_filtering_removes_32767_overflow_artifacts(self):
        """
        Verifies that CurrentCost 32767.0 W sentinel does not skew motor power statistics.
        """
        raw_readings = pd.Series([0.0, 700.0, 710.0, 32767.0, 690.0, 0.0])
        # Unfiltered mean of active readings (> 50 W):
        unfiltered_active = raw_readings[raw_readings > 50]
        self.assertGreater(unfiltered_active.mean(), 8000.0, "Unfiltered sentinel corrupts mean power.")

        # Filtered readings:
        clean_readings = raw_readings.copy()
        clean_readings[clean_readings >= 30000] = np.nan
        filtered_active = clean_readings[clean_readings > 50].dropna()
        self.assertAlmostEqual(filtered_active.mean(), 700.0, delta=15.0)

    def test_threshold_bimodal_deadband_stability(self):
        """
        Verifies that the 200 W threshold sits in a natural bimodal deadband between
        low-power standby/secondary loads (~50 W) and full motor pumping (~700 W).
        """
        # Simulated distribution matching iAWE observations:
        # Standby noise at ~45-60 W, active motor runs at ~650-750 W
        readings = np.array([0.0, 50.0, 55.0, 48.0, 0.0, 680.0, 710.0, 720.0, 690.0, 0.0])

        state_150 = (readings >= 150.0).astype(int)
        state_200 = (readings >= 200.0).astype(int)
        state_300 = (readings >= 300.0).astype(int)
        state_500 = (readings >= 500.0).astype(int)

        # In the deadband [150, 500] W, the binary active state must be strictly identical
        np.testing.assert_array_equal(state_150, state_200)
        np.testing.assert_array_equal(state_200, state_300)
        np.testing.assert_array_equal(state_300, state_500)
        self.assertEqual(state_200.sum(), 4)

    def test_cycle_gap_merging_prevents_rf_packet_drop_fragmentation(self):
        """
        Verifies that when a single continuous 30-second motor run drops a single 6s RF packet,
        max_gap_s=20s correctly reconstructs the single event, while max_gap_s=0s falsely splits it.
        """
        # 6s cadence with a 12s gap due to dropped packet:
        # t0: ON (700W), t1(+6s): ON, t2(+12s): dropped (0W in resample), t3(+18s): ON, t4(+24s): OFF
        t0 = pd.Timestamp("2026-06-01 06:30:00")
        timestamps = [
            t0,
            t0 + timedelta(seconds=6),
            t0 + timedelta(seconds=12),  # Missing packet filled with 0
            t0 + timedelta(seconds=18),
            t0 + timedelta(seconds=24),  # True OFF
        ]
        series = pd.Series([1, 1, 0, 1, 0], index=pd.DatetimeIndex(timestamps))

        # Without gap merging: 2 separate events
        events_raw = extract_events(series, max_gap_s=0.0)
        self.assertEqual(len(events_raw), 2, "Zero gap tolerance fragments dropped packet into 2 events.")

        # With 15s gap merging: 1 contiguous motor run
        events_merged = extract_events(series, max_gap_s=15.0)
        self.assertEqual(len(events_merged), 1, "Gap tolerance must merge packet-drop into 1 event.")
        self.assertEqual(events_merged[0]["start"], t0)
        self.assertEqual(events_merged[0]["end"], t0 + timedelta(seconds=18))

    def test_all_off_baseline_invariants(self):
        """
        Verifies that the majority class (All-OFF) baseline yields strictly:
        TP=0, FP=0, FN=N, Recall=0, Precision=0, and FP/day=0.0.
        """
        t0 = pd.Timestamp("2026-06-01 00:00:00")
        gt_events = [
            {"event_id": 1, "start": t0 + timedelta(hours=1), "end": t0 + timedelta(hours=1, minutes=2), "duration_s": 120.0},
            {"event_id": 2, "start": t0 + timedelta(hours=5), "end": t0 + timedelta(hours=5, minutes=1), "duration_s": 60.0},
        ]
        pred_events = []  # All-OFF predicts no events

        match_res = match_events(gt_events, pred_events, tolerance_s=60.0, test_duration_days=2.0)
        self.assertEqual(match_res["tp"], 0)
        self.assertEqual(match_res["fp"], 0)
        self.assertEqual(match_res["fn"], 2)
        self.assertEqual(match_res["precision"], 0.0)
        self.assertEqual(match_res["recall"], 0.0)
        self.assertEqual(match_res["f1_score"], 0.0)
        self.assertEqual(match_res["fp_per_day"], 0.0)

    def test_differential_step_vulnerability_to_concurrent_loads(self):
        """
        Verifies that a naive delta_P threshold baseline falsely detects concurrent
        household appliance steps (e.g. AC compressor, kettle, water heater) as motor onsets.
        """
        t0 = pd.Timestamp("2026-06-01 06:00:00")
        # 1 motor onset at t=10m, but 3 concurrent AC/kettle steps at t=1m, 3m, 7m
        delta_p = pd.Series(
            [0.0, 750.0, 0.0, 900.0, 0.0, 0.0, 0.0, 1200.0, 0.0, 0.0, 700.0, 0.0],
            index=pd.date_range(t0, periods=12, freq="1min"),
        )
        # Ground truth: only the step at index 10 is the motor
        gt_state = pd.Series(0, index=delta_p.index)
        gt_state.iloc[10] = 1

        step_threshold = 600.0
        pred_state = (delta_p >= step_threshold).astype(int)

        gt_events = extract_events(gt_state)
        pred_events = extract_events(pred_state)

        self.assertEqual(len(gt_events), 1)
        self.assertEqual(len(pred_events), 4, "Naive delta_P captures 4 onsets instead of 1.")

        match_res = match_events(gt_events, pred_events, tolerance_s=60.0, test_duration_days=1.0)
        self.assertEqual(match_res["tp"], 1)
        self.assertEqual(match_res["fp"], 3, "Concurrent appliances generate 3 false alarms.")
        self.assertAlmostEqual(match_res["precision"], 0.25, places=2)

    def test_detection_delay_signed_and_absolute(self):
        """
        Verifies that match_events calculates signed and absolute delay correctly.
        """
        t0 = pd.Timestamp("2026-06-01 12:00:00")
        # Ground truth onset at 12:00:00
        gt = [{"event_id": 1, "start": t0, "end": t0 + timedelta(minutes=5), "duration_s": 300.0}]
        # Predicted onset delayed by 18 seconds (12:00:18)
        pred = [{"event_id": 1, "start": t0 + timedelta(seconds=18), "end": t0 + timedelta(minutes=5), "duration_s": 282.0}]

        res = match_events(gt, pred, tolerance_s=60.0)
        self.assertEqual(res["tp"], 1)
        self.assertEqual(len(res["delays_s"]), 1)
        self.assertEqual(res["delays_s"][0], 18.0)
        self.assertEqual(res["mean_signed_delay_s"], 18.0)
        self.assertEqual(res["mean_absolute_delay_s"], 18.0)


if __name__ == "__main__":
    unittest.main()
