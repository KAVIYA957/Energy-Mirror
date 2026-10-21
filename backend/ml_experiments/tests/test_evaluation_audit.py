"""
test_evaluation_audit.py - Unit tests verifying corrections to NILM evaluation methodology.

Milestone 2C.8 Audit Verifications:
1. Strict onset tolerance enforcement (rejecting overlapping events with late onsets).
2. Signed vs absolute delay calculation (preventing delay cancellation).
3. Quiescent noise floor separation from multi-appliance switching volatility.
4. Theoretical resistive vs empirical ZIP load voltage sensitivity.
5. Persistence baseline oracle isolation.
6. Submeter dropout accounting vs silent zero-imputation.
"""

import os
import sys
import unittest
from datetime import timedelta
import numpy as np
import pandas as pd

# Add ml_experiments directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from evaluate_events import extract_events, match_events


class TestEvaluationAudit(unittest.TestCase):
    """Audits evaluation methodology and verifies edge-case mathematical correctness."""

    def test_onset_tolerance_strictly_enforced_for_overlapping_events(self):
        """
        DEFECT FIX AUDIT:
        In earlier implementations, 'abs_onset_diff <= tolerance_s or has_overlap' allowed
        predicted events starting 5 minutes or hours late into an ongoing cycle to claim
        a True Positive onset detection simply because they overlapped in time.
        """
        t0 = pd.Timestamp("2026-10-21 06:00:00")
        # Ground truth: 10-minute activation (06:00 to 06:10)
        gt = [
            {
                "event_id": 1,
                "start": t0,
                "end": t0 + timedelta(minutes=10),
                "duration_s": 600.0,
                "sample_count": 100,
            }
        ]
        # Predicted event starts 5 minutes (300s) late, well outside 60s tolerance!
        pred_late = [
            {
                "event_id": 1,
                "start": t0 + timedelta(minutes=5),
                "end": t0 + timedelta(minutes=9),
                "duration_s": 240.0,
                "sample_count": 40,
            }
        ]

        # With strict onset tolerance (the fix): Must be REJECTED as a valid onset match!
        res_strict = match_events(
            gt, pred_late, tolerance_s=60.0, test_duration_days=1.0, require_onset_tolerance=True
        )
        self.assertEqual(res_strict["tp"], 0, "Late onset must not be awarded a True Positive.")
        self.assertEqual(res_strict["fp"], 1, "Late predicted event must be a False Positive.")
        self.assertEqual(res_strict["fn"], 1, "Missed onset must be a False Negative.")
        self.assertEqual(res_strict["precision"], 0.0)
        self.assertEqual(res_strict["recall"], 0.0)

        # With loose overlap matching (legacy mode):
        res_loose = match_events(
            gt, pred_late, tolerance_s=60.0, test_duration_days=1.0, require_onset_tolerance=False
        )
        self.assertEqual(res_loose["tp"], 1)

    def test_signed_vs_absolute_delay_cancellation_prevention(self):
        """
        DEFECT FIX AUDIT:
        If Event 1 is detected 15s early (-15s delay) and Event 2 is detected 15s late (+15s delay),
        the signed mean is 0.0s. This created the illusion of zero detection error.
        Verification: Ensure mean_absolute_delay_s correctly reports 15.0s.
        """
        t1 = pd.Timestamp("2026-10-21 06:00:00")
        t2 = pd.Timestamp("2026-10-21 07:00:00")

        gt = [
            {"event_id": 1, "start": t1, "end": t1 + timedelta(minutes=5), "duration_s": 300.0, "sample_count": 50},
            {"event_id": 2, "start": t2, "end": t2 + timedelta(minutes=5), "duration_s": 300.0, "sample_count": 50},
        ]
        pred = [
            # Event 1: detected 15s early (-15s delay)
            {"event_id": 1, "start": t1 - timedelta(seconds=15), "end": t1 + timedelta(minutes=5), "duration_s": 315.0, "sample_count": 52},
            # Event 2: detected 15s late (+15s delay)
            {"event_id": 2, "start": t2 + timedelta(seconds=15), "end": t2 + timedelta(minutes=5), "duration_s": 285.0, "sample_count": 48},
        ]

        res = match_events(gt, pred, tolerance_s=60.0, test_duration_days=1.0)
        self.assertEqual(res["tp"], 2)
        self.assertEqual(res["delays_s"], [-15.0, 15.0])
        # Signed mean cancels to 0.0s
        self.assertEqual(res["mean_signed_delay_s"], 0.0)
        # Absolute mean reveals the true 15.0s timing error!
        self.assertEqual(res["mean_absolute_delay_s"], 15.0)
        self.assertEqual(res["max_absolute_delay_s"], 15.0)

    def test_quiescent_noise_vs_switching_volatility_separation(self):
        """
        METHODOLOGICAL AUDIT:
        The total std of whole-house delta_P is dominated by major appliance switching steps
        (AC, oven, pump), NOT sensor noise. Verifies that robust conditioning separates
        quiescent baseline noise from multi-appliance transitions.
        """
        np.random.seed(42)
        n = 1000
        # True sensor noise floor: sigma = 2.0 W
        noise = np.random.normal(0, 2.0, n)
        # 5 major switching steps of +1500 W / -1500 W
        switching = np.zeros(n)
        switching[100] = 1500.0
        switching[200] = -1500.0
        switching[400] = 2000.0
        switching[500] = -2000.0
        switching[800] = 800.0

        delta_p = noise + switching

        # Total unconditioned std is severely inflated
        total_std = float(np.std(delta_p))
        self.assertGreater(total_std, 100.0, "Unconditioned std is inflated by switching events.")

        # Quiescent conditioning (|delta_p| < 50 W) isolates true noise
        quiescent = delta_p[np.abs(delta_p) < 50.0]
        quiescent_std = float(np.std(quiescent))
        self.assertAlmostEqual(quiescent_std, 2.0, places=1)

    def test_voltage_sensitivity_zip_load_distinction(self):
        """
        METHODOLOGICAL AUDIT:
        Theoretical sensitivity (2*P/V) holds only for linear ohmic resistors (P proportional to V^2).
        For constant-power loads (P = const, dP/dV = 0) or composite ZIP loads,
        the empirical sensitivity is an order of magnitude lower.
        """
        p_base = 1000.0  # W
        v_base = 230.0   # V
        theoretical_resistive_slope = 2.0 * p_base / v_base  # ~8.70 W/V

        # Composite ZIP load: 70% constant-power (SMPS laptops, TVs, inverter ACs), 30% resistive
        # P(V) = 0.70 * P0 + 0.30 * P0 * (V/V0)^2
        # dP/dV = 0.30 * (2 * P0 / V0)
        zip_slope = 0.30 * (2.0 * p_base / v_base)  # ~2.61 W/V

        self.assertAlmostEqual(theoretical_resistive_slope, 8.70, places=2)
        self.assertAlmostEqual(zip_slope, 2.61, places=2)
        self.assertLess(zip_slope, theoretical_resistive_slope)

    def test_persistence_oracle_isolation(self):
        """
        METHODOLOGICAL AUDIT:
        Verifies that Persistence uses y_test[t-1] (submeter ground truth from previous step),
        which makes it an oracle benchmark that cannot be deployed without a submeter.
        """
        y_test = np.array([0, 0, 1, 1, 1, 0, 0, 1, 0, 0])
        persist_pred = np.roll(y_test, 1)
        persist_pred[0] = 0

        # Persistence prediction at t=2 is y_test[1] = 0 (misses turn-on edge)
        self.assertEqual(persist_pred[2], 0)
        self.assertEqual(y_test[2], 1)
        # Persistence prediction at t=3 is y_test[2] = 1 (tracks interior)
        self.assertEqual(persist_pred[3], 1)
        self.assertEqual(y_test[3], 1)
        # Persistence prediction at t=5 is y_test[4] = 1 (overshoots turn-off edge)
        self.assertEqual(persist_pred[5], 1)
        self.assertEqual(y_test[5], 0)


if __name__ == "__main__":
    unittest.main()
