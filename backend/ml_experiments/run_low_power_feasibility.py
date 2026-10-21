"""
run_low_power_feasibility.py - Milestone 2C.4 Low-Power Appliance Feasibility Study.

Investigates whether aggregate electrical measurements can distinguish low-power domestic
appliance activity:
- 12 W LED Bulb (bulb_01)
- 45 W Ceiling Fan (fan_01)
- 75 W Water Pump (pump_01)
amid realistic background loads, noise, and concurrent appliance switching.

Evaluates 4 Scenarios:
1. Ideal / Low Noise (Laboratory benchmark, sigma = 1.5 W)
2. Realistic Residential (sigma = 6.0 W, baseline drift, fridge cycles)
3. Adverse Concurrent Switching (sigma = 10.0 W, distractors, forced simultaneous transitions)
4. Missing Data & Sampling Jitter (5% dropouts, telemetry jitter)

Compares 4 Detection Methods:
1. Static Power Threshold Baseline
2. Differential Step Baseline
3. Production RuleBasedEventDetector (app.services.event_detector)
4. Random Forest Classifier (Ablations A, B, C)

Ablation Studies:
A. Active Power Only (P_agg)
B. Active Power + Valid Temporal Features (P_agg, Delta P, rolling stats)
C. Active Power + Reactive Power (Q_agg) + Power Factor (PF_agg)
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

# Add parent and ml_experiments directories to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from evaluate_events import extract_events, match_events
from app.services.event_detector import RuleBasedEventDetector

RESULTS_DIR = os.path.join(CURRENT_DIR, "results")
RESULTS_FILE = os.path.join(RESULTS_DIR, "low_power_feasibility_results.json")

# Physical appliance ratings and power factor assumptions
APPLIANCE_SPECS = {
    "bulb_01": {
        "name": "12 W LED Bulb",
        "power_w": 12.0,
        "power_tolerance_w": 4.0,
        "pf": 0.85,  # Switch-mode LED driver with distortion/phase displacement
        "typical_duration_min": (2, 45),
        "typical_cycles_per_day": 8,
    },
    "fan_01": {
        "name": "45 W Ceiling Fan",
        "power_w": 45.0,
        "power_tolerance_w": 7.0,
        "pf": 0.91,  # Single-phase induction motor with run capacitor
        "typical_duration_min": (20, 180),
        "typical_cycles_per_day": 4,
    },
    "pump_01": {
        "name": "75 W Water Pump",
        "power_w": 75.0,
        "power_tolerance_w": 9.0,
        "pf": 0.78,  # Fractional-HP domestic booster pump
        "typical_duration_min": (5, 25),
        "typical_cycles_per_day": 3,
    },
    "heater_01": {
        "name": "140 W Water Heater",
        "power_w": 140.0,
        "power_tolerance_w": 12.0,
        "pf": 0.99,  # Resistive heating element
        "typical_duration_min": (15, 35),
        "typical_cycles_per_day": 2,
    },
}

# Competing distractor specifications
DISTRACTOR_SPECS = {
    "refrigerator": {
        "power_w": 180.0,
        "pf": 0.75,  # Compressor induction motor
        "cycle_period_min": 45.0,
        "on_duration_min": 20.0,
    },
    "laptop_charger": {
        "power_w": 50.0,
        "pf": 0.95,  # Active PFC switch-mode power supply
        "typical_duration_min": (30, 120),
        "typical_cycles_per_day": 3,
    },
    "tv_entertainment": {
        "power_w": 25.0,
        "pf": 0.92,  # TV display / media receiver
        "typical_duration_min": (45, 180),
        "typical_cycles_per_day": 2,
    },
}


def compute_reactive_power(p_w: float, pf: float) -> float:
    """Computes inductive/capacitive reactive power Q = P * tan(acos(pf))."""
    pf_clamped = max(min(pf, 0.9999), 0.05)
    phi = np.arccos(pf_clamped)
    return float(p_w * np.tan(phi))


class SyntheticHouseholdGenerator:
    """
    Controlled Synthetic Aggregate Telemetry Generator for NILM Stress Testing.
    
    Generates physically consistent aggregate active and reactive electrical power traces
    with strict isolation between telemetry features and appliance ground-truth labels.
    """

    def __init__(
        self,
        scenario_name: str,
        seed: int = 42,
        dt_s: float = 6.0,
        duration_hours: float = 24.0,
    ):
        self.scenario_name = scenario_name
        self.seed = seed
        self.dt_s = dt_s
        self.duration_hours = duration_hours
        self.n_samples = int(duration_hours * 3600 / dt_s)
        self.rng = np.random.RandomState(seed)

        # Scenario configurations
        if scenario_name == "scenario_1_ideal":
            self.noise_sigma = 1.5
            self.adc_quantization = 0.1
            self.baseline_range = (120.0, 250.0)
            self.include_fridge = False
            self.include_distractors = False
            self.force_concurrency = False
            self.missing_rate = 0.0
            self.jitter_rate = 0.0
        elif scenario_name == "scenario_2_realistic":
            self.noise_sigma = 6.0
            self.adc_quantization = 1.0
            self.baseline_range = (150.0, 750.0)
            self.include_fridge = True
            self.include_distractors = False
            self.force_concurrency = False
            self.missing_rate = 0.0
            self.jitter_rate = 0.0
        elif scenario_name == "scenario_3_adverse_concurrent":
            self.noise_sigma = 10.0
            self.adc_quantization = 1.0
            self.baseline_range = (200.0, 1100.0)
            self.include_fridge = True
            self.include_distractors = True
            self.force_concurrency = True
            self.missing_rate = 0.0
            self.jitter_rate = 0.0
        elif scenario_name == "scenario_4_missing_jitter":
            self.noise_sigma = 6.0
            self.adc_quantization = 1.0
            self.baseline_range = (150.0, 750.0)
            self.include_fridge = True
            self.include_distractors = False
            self.force_concurrency = False
            self.missing_rate = 0.05
            self.jitter_rate = 0.20
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")

    def _generate_baseline(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generates diurnal drifting residential background load (P and Q)."""
        t_hours = np.linspace(0, self.duration_hours, self.n_samples)
        # Diurnal curve: lowest at night (03:00-05:00), peaks in morning and evening
        diurnal = 0.5 * (1.0 - np.cos(2 * np.pi * (t_hours - 4) / 24.0))
        p_base_min, p_base_max = self.baseline_range
        p_baseline = p_base_min + (p_base_max - p_base_min) * diurnal

        # Add slow random walk drift
        steps = self.rng.normal(0, 0.4, size=self.n_samples)
        drift = np.cumsum(steps)
        # Detrend drift slightly to keep within envelope
        drift = drift - np.linspace(drift[0], drift[-1], self.n_samples)
        p_baseline = np.clip(p_baseline + drift, 50.0, None)

        # Baseline power factor ~0.92 inductive (electronics, standby loads)
        q_baseline = p_baseline * np.tan(np.arccos(0.92))
        return p_baseline, q_baseline

    def _schedule_appliance_events(
        self,
        appliance_key: str,
        n_samples: int,
        forbidden_intervals: Optional[List[Tuple[int, int]]] = None,
    ) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """Schedules ON/OFF state array for an appliance."""
        spec = APPLIANCE_SPECS[appliance_key]
        state = np.zeros(n_samples, dtype=int)
        intervals = []
        n_cycles = spec["typical_cycles_per_day"]
        dur_min_range = spec["typical_duration_min"]

        attempts = 0
        scheduled = 0
        while scheduled < n_cycles and attempts < 100:
            attempts += 1
            dur_min = self.rng.uniform(dur_min_range[0], dur_min_range[1])
            dur_samples = max(2, int(dur_min * 60 / self.dt_s))
            max_allowed = max(2, n_samples // 4)
            dur_samples = min(dur_samples, max_allowed)
            max_start = n_samples - dur_samples - 5
            if max_start <= 5:
                break
            start_idx = self.rng.randint(5, max_start)
            end_idx = start_idx + dur_samples

            # Check collision if non-overlapping required
            if forbidden_intervals:
                collision = any(
                    not (end_idx < f_start - 10 or start_idx > f_end + 10)
                    for f_start, f_end in forbidden_intervals
                )
                if collision:
                    continue

            # Check self-collision
            self_collision = any(
                not (end_idx < s_start - 5 or start_idx > s_end + 5)
                for s_start, s_end in intervals
            )
            if self_collision:
                continue

            state[start_idx:end_idx] = 1
            intervals.append((start_idx, end_idx))
            scheduled += 1

        return state, intervals

    def generate_trace(
        self,
        start_datetime: Optional[datetime] = None,
        run_id: int = 0,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generates independent 24-hour simulation run.
        
        Returns:
            telemetry_df: [timestamp, active_power_w, reactive_power_var, power_factor]
            ground_truth_df: [timestamp, bulb_01, fan_01, pump_01, heater_01]
        """
        if start_datetime is None:
            start_datetime = datetime(2026, 10, 21, 0, 0, 0) + timedelta(days=run_id)

        timestamps = [
            start_datetime + timedelta(seconds=i * self.dt_s)
            for i in range(self.n_samples)
        ]

        # 1. Baseline
        p_base, q_base = self._generate_baseline()

        # 2. Schedule core target appliances
        gt_states = {}
        all_intervals = []
        is_isolated = (self.scenario_name == "scenario_1_ideal")

        # Scheduling order: heater, pump, fan, bulb
        for app_id in ["heater_01", "pump_01", "fan_01", "bulb_01"]:
            forbidden = all_intervals if is_isolated else None
            state, intervals = self._schedule_appliance_events(app_id, self.n_samples, forbidden)
            gt_states[app_id] = state
            all_intervals.extend(intervals)

        # In Scenario 3 (Adverse Concurrent Switching), force simultaneous onsets
        if self.force_concurrency:
            # Force at least 2 simultaneous bulb + fan transitions
            fan_starts = np.where(np.diff(gt_states["fan_01"]) == 1)[0]
            if len(fan_starts) >= 1:
                sync_idx = fan_starts[0] + 1
                bulb_dur = int(15 * 60 / self.dt_s)
                if sync_idx + bulb_dur < self.n_samples:
                    gt_states["bulb_01"][sync_idx : sync_idx + bulb_dur] = 1

            # Force simultaneous pump + laptop or bulb transition
            pump_starts = np.where(np.diff(gt_states["pump_01"]) == 1)[0]
            if len(pump_starts) >= 1:
                sync_idx2 = pump_starts[0] + 1
                bulb_dur2 = int(10 * 60 / self.dt_s)
                if sync_idx2 + bulb_dur2 < self.n_samples:
                    gt_states["bulb_01"][sync_idx2 : sync_idx2 + bulb_dur2] = 1

        # 3. Compute appliance active and reactive powers
        p_appliances = np.zeros(self.n_samples)
        q_appliances = np.zeros(self.n_samples)

        for app_id, state in gt_states.items():
            spec = APPLIANCE_SPECS[app_id]
            p_val = spec["power_w"]
            q_val = compute_reactive_power(p_val, spec["pf"])
            p_appliances += state * p_val
            q_appliances += state * q_val

        # 4. Competing distractors
        p_distractors = np.zeros(self.n_samples)
        q_distractors = np.zeros(self.n_samples)

        if self.include_fridge:
            # Refrigerator 45-min cycle (20 min ON, 25 min OFF)
            fridge_spec = DISTRACTOR_SPECS["refrigerator"]
            cycle_samples = int(fridge_spec["cycle_period_min"] * 60 / self.dt_s)
            on_samples = int(fridge_spec["on_duration_min"] * 60 / self.dt_s)
            fridge_state = np.zeros(self.n_samples, dtype=int)
            for i in range(0, self.n_samples, cycle_samples):
                fridge_state[i : min(i + on_samples, self.n_samples)] = 1
            p_distractors += fridge_state * fridge_spec["power_w"]
            q_distractors += fridge_state * compute_reactive_power(
                fridge_spec["power_w"], fridge_spec["pf"]
            )

        if self.include_distractors:
            # Laptop charger (50 W, PF 0.95)
            lap_spec = DISTRACTOR_SPECS["laptop_charger"]
            lap_state, _ = self._schedule_appliance_events("fan_01", self.n_samples)  # Re-use fan schedule cadence
            p_distractors += lap_state * lap_spec["power_w"]
            q_distractors += lap_state * compute_reactive_power(lap_spec["power_w"], lap_spec["pf"])

            # TV / entertainment (25 W, PF 0.92)
            tv_spec = DISTRACTOR_SPECS["tv_entertainment"]
            tv_state, _ = self._schedule_appliance_events("heater_01", self.n_samples)
            p_distractors += tv_state * tv_spec["power_w"]
            q_distractors += tv_state * compute_reactive_power(tv_spec["power_w"], tv_spec["pf"])

        # 5. Aggregate physics and measurement noise
        p_clean = p_base + p_appliances + p_distractors
        q_clean = q_base + q_appliances + q_distractors

        noise_p = self.rng.normal(0, self.noise_sigma, size=self.n_samples)
        noise_q = self.rng.normal(0, self.noise_sigma, size=self.n_samples)

        p_meas = p_clean + noise_p
        q_meas = q_clean + noise_q

        # ADC quantization
        p_meas = np.round(p_meas / self.adc_quantization) * self.adc_quantization
        q_meas = np.round(q_meas / self.adc_quantization) * self.adc_quantization

        # Clamping
        p_meas = np.clip(p_meas, 10.0, None)
        q_meas = np.clip(q_meas, 0.0, None)

        s_meas = np.sqrt(p_meas**2 + q_meas**2)
        pf_meas = np.clip(p_meas / np.maximum(s_meas, 1e-4), 0.1, 1.0)
        pf_meas = np.round(pf_meas, 3)

        # Assemble DataFrames
        telemetry_df = pd.DataFrame({
            "timestamp": timestamps,
            "active_power_w": p_meas,
            "reactive_power_var": q_meas,
            "power_factor": pf_meas,
        })

        ground_truth_df = pd.DataFrame({
            "timestamp": timestamps,
            "bulb_01": gt_states["bulb_01"],
            "fan_01": gt_states["fan_01"],
            "pump_01": gt_states["pump_01"],
            "heater_01": gt_states["heater_01"],
        })

        # Scenario 4 degradation: missing samples & jitter
        if self.missing_rate > 0 or self.jitter_rate > 0:
            telemetry_df = self._apply_telemetry_degradation(telemetry_df)
            dt_index = pd.DatetimeIndex(timestamps, name="timestamp")
            telemetry_df = (
                telemetry_df.set_index("timestamp")
                .reindex(dt_index, method="ffill")
                .reset_index()
            )
            if "index" in telemetry_df.columns:
                telemetry_df = telemetry_df.rename(columns={"index": "timestamp"})
            telemetry_df["timestamp"] = timestamps
            telemetry_df = telemetry_df.bfill()

        return telemetry_df, ground_truth_df

    def _apply_telemetry_degradation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies random packet dropouts and resampling jitter."""
        n = len(df)
        keep_mask = self.rng.uniform(0, 1, size=n) >= self.missing_rate
        # Ensure at least first sample kept
        keep_mask[0] = True
        df_dropped = df[keep_mask].copy()

        # Add jitter to timestamps
        if self.jitter_rate > 0:
            jitter_offsets = self.rng.uniform(-2.5, 2.5, size=len(df_dropped))
            jittered_ts = [
                ts + timedelta(seconds=float(off))
                for ts, off in zip(df_dropped["timestamp"], jitter_offsets)
            ]
            df_dropped["timestamp"] = jittered_ts
            df_dropped = df_dropped.sort_values("timestamp").reset_index(drop=True)

        return df_dropped


def extract_features(telemetry_df: pd.DataFrame, ablation: str = "B") -> np.ndarray:
    """
    Extracts strictly non-leaking feature matrices for inference.
    
    Ablation A: Active power only [P]
    Ablation B: Active power + valid temporal features [P, Delta P, roll_mean5, roll_std5, roll_min5, roll_max5]
    Ablation C: Active power + temporal + Reactive power (Q) + Power Factor (PF)
    """
    p = telemetry_df["active_power_w"].values
    n = len(p)

    if ablation == "A":
        return p.reshape(-1, 1)

    # Compute delta P
    delta_p = np.zeros(n)
    delta_p[1:] = p[1:] - p[:-1]

    # Rolling window stats (5 samples = 30s lookback, causal / backwards only)
    s_p = pd.Series(p)
    roll5 = s_p.rolling(window=5, min_periods=1)
    p_mean5 = roll5.mean().values
    p_std5 = roll5.std().fillna(0.0).values
    p_min5 = roll5.min().values
    p_max5 = roll5.max().values

    if ablation == "B":
        return np.column_stack([p, delta_p, p_mean5, p_std5, p_min5, p_max5])

    if ablation == "C":
        q = telemetry_df["reactive_power_var"].values
        pf = telemetry_df["power_factor"].values

        delta_q = np.zeros(n)
        delta_q[1:] = q[1:] - q[:-1]

        delta_pf = np.zeros(n)
        delta_pf[1:] = pf[1:] - pf[:-1]

        s_q = pd.Series(q)
        roll5_q = s_q.rolling(window=5, min_periods=1)
        q_mean5 = roll5_q.mean().values
        q_std5 = roll5_q.std().fillna(0.0).values

        s_pf = pd.Series(pf)
        roll5_pf = s_pf.rolling(window=5, min_periods=1)
        pf_mean5 = roll5_pf.mean().values

        return np.column_stack([
            p, delta_p, p_mean5, p_std5, p_min5, p_max5,
            q, delta_q, q_mean5, q_std5,
            pf, delta_pf, pf_mean5,
        ])

    raise ValueError(f"Unknown ablation: {ablation}")


def run_power_threshold_detector(
    p_train: np.ndarray,
    y_train: np.ndarray,
    p_test: np.ndarray,
) -> np.ndarray:
    """Baseline 1: Static Aggregate Power Threshold."""
    # Find best threshold on training set via quantile sweep
    quantiles = np.linspace(0.1, 0.99, 50)
    candidate_thresholds = np.quantile(p_train, quantiles)
    best_thresh = candidate_thresholds[0]
    best_f1 = -1.0

    for thresh in candidate_thresholds:
        y_cand = (p_train >= thresh).astype(int)
        tp = np.sum((y_cand == 1) & (y_train == 1))
        fp = np.sum((y_cand == 1) & (y_train == 0))
        fn = np.sum((y_cand == 0) & (y_train == 1))
        f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh

    return (p_test >= best_thresh).astype(int)


def run_differential_step_detector(
    p_test: np.ndarray,
    appliance_key: str,
) -> np.ndarray:
    """Baseline 2: Differential Step Baseline."""
    spec = APPLIANCE_SPECS[appliance_key]
    nom_w = spec["power_w"]
    tol_w = spec["power_tolerance_w"]
    min_w = nom_w - tol_w
    max_w = nom_w + tol_w

    n = len(p_test)
    y_pred = np.zeros(n, dtype=int)
    current_state = 0

    for i in range(1, n):
        delta_p = p_test[i] - p_test[i - 1]
        if min_w <= delta_p <= max_w:
            current_state = 1
        elif -max_w <= delta_p <= -min_w:
            current_state = 0
        y_pred[i] = current_state

    return y_pred


def run_production_rule_based_detector(
    p_test: np.ndarray,
    pf_test: np.ndarray,
    timestamps: List[datetime],
    appliance_key: str,
) -> np.ndarray:
    """
    Baseline 3: Production RuleBasedEventDetector.
    Reuses app.services.event_detector without modifying production code.
    """
    detector = RuleBasedEventDetector()
    n = len(p_test)
    y_pred = np.zeros(n, dtype=int)
    current_state = 0

    for i in range(1, n):
        event = detector.detect_transition(
            prev_power_w=float(p_test[i - 1]),
            curr_power_w=float(p_test[i]),
            prev_pf=float(pf_test[i - 1]),
            curr_pf=float(pf_test[i]),
            timestamp=timestamps[i],
        )

        if event.status == "MATCHED" and event.appliance_id == appliance_key:
            if event.transition_type == "ON":
                current_state = 1
            elif event.transition_type == "OFF":
                current_state = 0

        y_pred[i] = current_state

    return y_pred


from scipy.signal import medfilt


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    timestamps: List[datetime],
    duration_days: float = 1.0,
) -> Dict[str, Any]:
    """Computes comprehensive sample-level and event-level metrics."""
    # 1. Sample metrics
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    acc = float((tp + tn) / (tp + tn + fp + fn))
    prev = float(np.mean(y_true) * 100.0)
    hours = duration_days * 24.0
    fp_per_hour = float(fp / max(hours, 1e-4))

    # 2. Event metrics (minimum duration 18.0s = 3 samples to filter sub-appliance transient glitches)
    s_true = pd.Series(y_true, index=pd.DatetimeIndex(timestamps))
    s_pred = pd.Series(y_pred, index=pd.DatetimeIndex(timestamps))

    gt_events = extract_events(s_true, min_duration_s=18.0)
    pred_events = extract_events(s_pred, min_duration_s=18.0)

    match_res = match_events(
        gt_events, pred_events, tolerance_s=60.0, test_duration_days=duration_days
    )

    ev_prec = match_res["precision"]
    ev_rec = match_res["recall"]
    ev_f1 = match_res["f1_score"]
    ev_fp_day = match_res["fp_per_day"]
    ev_fp_hour = float(ev_fp_day / 24.0)

    # Acceptance feasibility criteria evaluation:
    # Proposed Target: Event F1 >= 0.80 and Event FA/hour <= 1.0 (<= 24/day)
    if ev_f1 >= 0.80 and ev_fp_hour <= 1.0:
        feasibility = "FEASIBLE_SYNTHETIC"
    elif ev_f1 >= 0.50 and ev_fp_hour <= 3.0:
        feasibility = "INCONCLUSIVE"
    else:
        feasibility = "NOT_FEASIBLE"

    return {
        "sample_metrics": {
            "accuracy": round(acc, 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
            "positive_prevalence_pct": round(prev, 3),
            "false_alarms_per_hour": round(fp_per_hour, 2),
        },
        "event_metrics": {
            "gt_events_count": match_res["gt_events_count"],
            "pred_events_count": match_res["pred_events_count"],
            "tp": match_res["tp"],
            "fp": match_res["fp"],
            "fn": match_res["fn"],
            "precision": ev_prec,
            "recall": ev_rec,
            "f1_score": ev_f1,
            "false_alarms_per_day": ev_fp_day,
            "false_alarms_per_hour": round(ev_fp_hour, 2),
            "mean_delay_s": match_res["mean_delay_s"],
        },
        "feasibility_verdict": feasibility,
    }


def train_and_predict_rf(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
) -> np.ndarray:
    """Trains Random Forest with validation threshold tuning and temporal debouncing."""
    rf = RandomForestClassifier(n_estimators=60, max_depth=10, random_state=42)
    rf.fit(X_train, y_train)

    # If only 1 class in train
    if len(rf.classes_) == 1:
        return np.zeros(len(X_test), dtype=int)

    val_probs = rf.predict_proba(X_val)[:, 1]
    best_thresh = 0.5
    best_f1 = -1.0

    for thresh in [0.25, 0.35, 0.45, 0.50, 0.55, 0.65]:
        val_cand = (val_probs >= thresh).astype(int)
        tp = np.sum((val_cand == 1) & (y_val == 1))
        fp = np.sum((val_cand == 1) & (y_val == 0))
        fn = np.sum((val_cand == 0) & (y_val == 1))
        f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh

    test_probs = rf.predict_proba(X_test)[:, 1]
    y_test_pred = (test_probs >= best_thresh).astype(int)
    # Apply 3-sample median filter debouncing
    y_test_debounced = medfilt(y_test_pred, kernel_size=3)
    return y_test_debounced.astype(int)


def run_full_feasibility_study() -> Dict[str, Any]:
    """Executes the complete experimental study across scenarios, models, and ablations."""
    scenarios = [
        "scenario_1_ideal",
        "scenario_2_realistic",
        "scenario_3_adverse_concurrent",
        "scenario_4_missing_jitter",
    ]
    appliances = ["bulb_01", "fan_01", "pump_01"]

    results: Dict[str, Any] = {
        "metadata": {
            "study_name": "Milestone 2C.4 Low-Power Appliance Feasibility Study",
            "timestamp": datetime.utcnow().isoformat(),
            "random_seed": 42,
            "sampling_interval_s": 6.0,
            "simulated_duration_per_run_hours": 24.0,
            "train_runs_count": 3,
            "val_runs_count": 1,
            "test_runs_count": 1,
            "target_appliances": {
                k: {
                    "name": v["name"],
                    "nominal_power_w": v["power_w"],
                    "tolerance_w": v["power_tolerance_w"],
                    "power_factor": v["pf"],
                }
                for k, v in APPLIANCE_SPECS.items()
            },
            "research_target_criteria": {
                "min_event_f1": 0.80,
                "max_false_alarms_per_hour": 1.0,
            },
        },
        "scenarios": {},
    }

    for sc_name in scenarios:
        print(f"\n==========================================")
        print(f"Executing Study Scenario: {sc_name}")
        print(f"==========================================")

        gen = SyntheticHouseholdGenerator(scenario_name=sc_name, seed=42)

        # Generate 5 independent daily runs
        # Runs 0, 1, 2: Train (72 hrs = 43,200 samples)
        # Run 3: Val (24 hrs = 14,400 samples)
        # Run 4: Test (24 hrs = 14,400 samples)
        train_tel_list = []
        train_gt_list = []
        for r_id in range(3):
            t_df, g_df = gen.generate_trace(run_id=r_id)
            train_tel_list.append(t_df)
            train_gt_list.append(g_df)

        train_tel = pd.concat(train_tel_list, ignore_index=True)
        train_gt = pd.concat(train_gt_list, ignore_index=True)

        val_tel, val_gt = gen.generate_trace(run_id=3)
        test_tel, test_gt = gen.generate_trace(run_id=4)

        test_timestamps = test_tel["timestamp"].tolist()
        p_train = train_tel["active_power_w"].values
        p_test = test_tel["active_power_w"].values
        pf_test = test_tel["power_factor"].values

        # Extract features for ablations
        X_train_A = extract_features(train_tel, "A")
        X_val_A = extract_features(val_tel, "A")
        X_test_A = extract_features(test_tel, "A")

        X_train_B = extract_features(train_tel, "B")
        X_val_B = extract_features(val_tel, "B")
        X_test_B = extract_features(test_tel, "B")

        X_train_C = extract_features(train_tel, "C")
        X_val_C = extract_features(val_tel, "C")
        X_test_C = extract_features(test_tel, "C")

        scenario_res: Dict[str, Any] = {
            "noise_sigma_w": gen.noise_sigma,
            "adc_quantization_w": gen.adc_quantization,
            "appliances": {},
        }

        for app_id in appliances:
            app_name = APPLIANCE_SPECS[app_id]["name"]
            y_train_app = train_gt[app_id].values
            y_val_app = val_gt[app_id].values
            y_test_app = test_gt[app_id].values

            print(f"\n--- Appliance: {app_name} ({app_id}) ---")

            # 1. Static Power Threshold
            y_pred_thresh = run_power_threshold_detector(p_train, y_train_app, p_test)
            res_thresh = evaluate_predictions(y_test_app, y_pred_thresh, test_timestamps)

            # 2. Differential Step Baseline
            y_pred_diff = run_differential_step_detector(p_test, app_id)
            res_diff = evaluate_predictions(y_test_app, y_pred_diff, test_timestamps)

            # 3. Production Rule-Based Event Detector
            y_pred_rule = run_production_rule_based_detector(
                p_test, pf_test, test_timestamps, app_id
            )
            res_rule = evaluate_predictions(y_test_app, y_pred_rule, test_timestamps)

            # 4. Random Forest (Ablation A: Active Power Only)
            y_pred_rf_a = train_and_predict_rf(X_train_A, y_train_app, X_val_A, y_val_app, X_test_A)
            res_rf_a = evaluate_predictions(y_test_app, y_pred_rf_a, test_timestamps)

            # 5. Random Forest (Ablation B: Active Power + Temporal)
            y_pred_rf_b = train_and_predict_rf(X_train_B, y_train_app, X_val_B, y_val_app, X_test_B)
            res_rf_b = evaluate_predictions(y_test_app, y_pred_rf_b, test_timestamps)

            # 6. Random Forest (Ablation C: Active + Reactive + PF)
            y_pred_rf_c = train_and_predict_rf(X_train_C, y_train_app, X_val_C, y_val_app, X_test_C)
            res_rf_c = evaluate_predictions(y_test_app, y_pred_rf_c, test_timestamps)

            print(
                f"Threshold:    Event F1={res_thresh['event_metrics']['f1_score']:.3f}, FA/hr={res_thresh['event_metrics']['false_alarms_per_hour']:.1f} [{res_thresh['feasibility_verdict']}]"
            )
            print(
                f"Diff Step:    Event F1={res_diff['event_metrics']['f1_score']:.3f}, FA/hr={res_diff['event_metrics']['false_alarms_per_hour']:.1f} [{res_diff['feasibility_verdict']}]"
            )
            print(
                f"Rule-Based:   Event F1={res_rule['event_metrics']['f1_score']:.3f}, FA/hr={res_rule['event_metrics']['false_alarms_per_hour']:.1f} [{res_rule['feasibility_verdict']}]"
            )
            print(
                f"RF Ablation A: Event F1={res_rf_a['event_metrics']['f1_score']:.3f}, FA/hr={res_rf_a['event_metrics']['false_alarms_per_hour']:.1f} [{res_rf_a['feasibility_verdict']}]"
            )
            print(
                f"RF Ablation B: Event F1={res_rf_b['event_metrics']['f1_score']:.3f}, FA/hr={res_rf_b['event_metrics']['false_alarms_per_hour']:.1f} [{res_rf_b['feasibility_verdict']}]"
            )
            print(
                f"RF Ablation C: Event F1={res_rf_c['event_metrics']['f1_score']:.3f}, FA/hr={res_rf_c['event_metrics']['false_alarms_per_hour']:.1f} [{res_rf_c['feasibility_verdict']}]"
            )

            scenario_res["appliances"][app_id] = {
                "name": app_name,
                "nominal_power_w": APPLIANCE_SPECS[app_id]["power_w"],
                "methods": {
                    "static_power_threshold": res_thresh,
                    "differential_step_baseline": res_diff,
                    "production_rule_based_detector": res_rule,
                    "random_forest_ablation_a_active_only": res_rf_a,
                    "random_forest_ablation_b_active_temporal": res_rf_b,
                    "random_forest_ablation_c_reactive_pf": res_rf_c,
                },
            }

        results["scenarios"][sc_name] = scenario_res

    # Write output JSON
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nFeasibility study successfully written to {RESULTS_FILE}")
    return results


if __name__ == "__main__":
    run_full_feasibility_study()
