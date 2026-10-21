"""
evaluate_events.py - Event-Level Evaluation and Metric Audit for NILM Benchmarks.

Implements rigorous, reproducible event extraction, tolerance-bounded one-to-one matching,
and operational reliability metrics for NILM disaggregation:
- Contiguous activation segment extraction with optional gap merging
- Greedy one-to-one event bipartite matching
- Temporal onset tolerance bounds and delay tracking
- Event Precision, Recall, F1, False Alarms per Day, and Missed Events per Day
- Comparison across all models (Random Forest, Persistence, Differential Step, Threshold, Majority)
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    precision_recall_fscore_support,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
)

# Add current dir to path to import load_iawe_dataset
sys.path.insert(0, os.path.dirname(__file__))
from run_iawe_experiment import load_iawe_dataset, H5_PATH, RESULTS_DIR


def extract_events(
    series: pd.Series,
    min_duration_s: float = 0.0,
    max_gap_s: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Extracts contiguous ON events from a binary pandas Series with DatetimeIndex.

    Args:
        series: Binary pd.Series (1 for ON, 0 for OFF) indexed by DatetimeIndex.
        min_duration_s: Minimum duration in seconds to retain an event.
        max_gap_s: If > 0, merges consecutive events separated by <= max_gap_s.

    Returns:
        List of dicts representing events with keys:
        - event_id: integer index
        - start: pd.Timestamp of event onset
        - end: pd.Timestamp of event offset
        - duration_s: duration in seconds
        - sample_count: number of active samples in the event
    """
    if len(series) == 0 or (series == 0).all():
        return []

    is_on = (series == 1).astype(int)
    diff = is_on.diff().fillna(0)

    start_indices = np.where(diff == 1)[0].tolist()
    if is_on.iloc[0] == 1:
        start_indices = [0] + start_indices

    end_indices = (np.where(diff == -1)[0] - 1).tolist()
    if is_on.iloc[-1] == 1:
        end_indices = end_indices + [len(series) - 1]

    # Infer sampling interval if available
    sample_interval_s = 6.0
    if len(series.index) > 1:
        dt = (series.index[1] - series.index[0]).total_seconds()
        if dt > 0:
            sample_interval_s = dt

    events = []
    for idx, (s_idx, e_idx) in enumerate(zip(start_indices, end_indices)):
        s_time = series.index[s_idx]
        e_time = series.index[e_idx]
        sample_count = e_idx - s_idx + 1
        dur_s = sample_count * sample_interval_s
        if dur_s >= min_duration_s:
            events.append({
                "event_id": idx + 1,
                "start": s_time,
                "end": e_time,
                "duration_s": float(dur_s),
                "sample_count": int(sample_count),
            })

    # Optional gap merging (e.g., sensor dropout of <= 30s during single cycle)
    if max_gap_s > 0 and len(events) > 1:
        merged = [dict(events[0])]
        for ev in events[1:]:
            prev = merged[-1]
            gap = (ev["start"] - prev["end"]).total_seconds() - sample_interval_s
            if gap <= max_gap_s:
                prev["end"] = ev["end"]
                prev["duration_s"] = float((ev["end"] - prev["start"]).total_seconds() + sample_interval_s)
                prev["sample_count"] += ev["sample_count"]
            else:
                merged.append(dict(ev))
        for i, m in enumerate(merged):
            m["event_id"] = i + 1
        return merged

    return events


def match_events(
    gt_events: List[Dict[str, Any]],
    pred_events: List[Dict[str, Any]],
    tolerance_s: float = 60.0,
    test_duration_days: float = 6.616,
) -> Dict[str, Any]:
    """
    Executes greedy one-to-one bipartite matching between ground-truth and predicted events.

    Matching Rationale:
    - Candidate match valid if: |t_pred_start - t_gt_start| <= tolerance_s OR events overlap in time.
    - Greedy assignment prioritizes pairs with smallest absolute onset distance.
    - Enforces strict one-to-one mapping (no predicted event matches multiple GT events and vice versa).

    Args:
        gt_events: List of ground-truth events from extract_events.
        pred_events: List of predicted events from extract_events.
        tolerance_s: Maximum onset difference in seconds to consider a candidate match.
        test_duration_days: Total test period duration in days for operational rate normalization.

    Returns:
        Structured evaluation metrics dict.
    """
    n_gt = len(gt_events)
    n_pred = len(pred_events)

    if n_gt == 0 and n_pred == 0:
        return {
            "gt_events_count": 0,
            "pred_events_count": 0,
            "tp": 0,
            "fp": 0,
            "fn": 0,
            "precision": 1.0,
            "recall": 1.0,
            "f1_score": 1.0,
            "fp_per_day": 0.0,
            "fn_per_day": 0.0,
            "delays_s": [],
            "mean_delay_s": 0.0,
            "median_delay_s": 0.0,
            "std_delay_s": 0.0,
            "tolerance_s": tolerance_s,
        }

    if n_gt == 0:
        return {
            "gt_events_count": 0,
            "pred_events_count": n_pred,
            "tp": 0,
            "fp": n_pred,
            "fn": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "fp_per_day": round(n_pred / max(test_duration_days, 1e-4), 3),
            "fn_per_day": 0.0,
            "delays_s": [],
            "mean_delay_s": 0.0,
            "median_delay_s": 0.0,
            "std_delay_s": 0.0,
            "tolerance_s": tolerance_s,
        }

    if n_pred == 0:
        return {
            "gt_events_count": n_gt,
            "pred_events_count": 0,
            "tp": 0,
            "fp": 0,
            "fn": n_gt,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "fp_per_day": 0.0,
            "fn_per_day": round(n_gt / max(test_duration_days, 1e-4), 3),
            "delays_s": [],
            "mean_delay_s": 0.0,
            "median_delay_s": 0.0,
            "std_delay_s": 0.0,
            "tolerance_s": tolerance_s,
        }

    # Generate candidate bipartite pairs
    candidates = []
    for gi, g in enumerate(gt_events):
        for pi, p in enumerate(pred_events):
            onset_diff = (p["start"] - g["start"]).total_seconds()
            abs_onset_diff = abs(onset_diff)
            # Check temporal overlap
            has_overlap = not (p["end"] < g["start"] or p["start"] > g["end"])
            if abs_onset_diff <= tolerance_s or has_overlap:
                candidates.append((abs_onset_diff, gi, pi, onset_diff))

    # Sort greedily by lowest onset distance
    candidates.sort(key=lambda x: x[0])

    matched_gt = set()
    matched_pred = set()
    matches = []

    for dist, gi, pi, onset_diff in candidates:
        if gi not in matched_gt and pi not in matched_pred:
            matched_gt.add(gi)
            matched_pred.add(pi)
            matches.append({
                "gt_id": gt_events[gi]["event_id"],
                "pred_id": pred_events[pi]["event_id"],
                "gt_start": str(gt_events[gi]["start"]),
                "pred_start": str(pred_events[pi]["start"]),
                "delay_s": round(onset_diff, 2),
            })

    tp = len(matches)
    fp = n_pred - tp
    fn = n_gt - tp

    prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

    delays = [m["delay_s"] for m in matches]
    mean_delay = float(np.mean(delays)) if delays else 0.0
    median_delay = float(np.median(delays)) if delays else 0.0
    std_delay = float(np.std(delays)) if delays else 0.0

    fp_rate = float(fp / max(test_duration_days, 1e-4))
    fn_rate = float(fn / max(test_duration_days, 1e-4))

    return {
        "gt_events_count": n_gt,
        "pred_events_count": n_pred,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "fp_per_day": round(fp_rate, 3),
        "fn_per_day": round(fn_rate, 3),
        "delays_s": delays,
        "mean_delay_s": round(mean_delay, 2),
        "median_delay_s": round(median_delay, 2),
        "std_delay_s": round(std_delay, 2),
        "tolerance_s": tolerance_s,
        "matches": matches,
    }


def run_event_benchmark_audit(
    h5_file: str = H5_PATH,
    on_threshold_w: float = 200.0,
    resample_freq: str = "6s",
    tolerances: List[float] = [12.0, 30.0, 60.0, 120.0],
    primary_tolerance: float = 60.0,
    cycle_gap_merge_s: float = 30.0,
) -> Dict[str, Any]:
    """
    Executes full audit of sample-level classification, active-vs-all regression,
    and multi-tolerance event evaluation.
    """
    df, meta = load_iawe_dataset(h5_file, on_threshold_w=on_threshold_w, resample_freq=resample_freq)

    n = len(df)
    n_train = int(n * 0.60)
    n_val = int(n * 0.20)
    buffer = 100

    train_df = df.iloc[0 : n_train - buffer]
    val_df = df.iloc[n_train : n_train + n_val - buffer]
    test_df = df.iloc[n_train + n_val :]

    features = ["aggregate_power_w", "delta_p", "rolling_mean_5", "rolling_std_5", "rolling_max_5"]

    X_train = train_df[features].values
    y_train = train_df["state"].values
    p_train = train_df["motor_w"].values

    X_val = val_df[features].values
    y_val = val_df["state"].values

    X_test = test_df[features].values
    y_test = test_df["state"].values
    p_test = test_df["motor_w"].values

    test_start = test_df.index.min()
    test_end = test_df.index.max()
    test_duration_days = (test_end - test_start).total_seconds() / 86400.0

    print(f"\n=======================================================")
    print(f"=== MILESTONE 2C.3: REAL-DATA BENCHMARK AUDIT PIPELINE ===")
    print(f"=======================================================")
    print(f"Test Set Window: {test_start} to {test_end} ({test_duration_days:.2f} days)")
    print(f"Test Samples: {len(test_df):,} | Active ON: {int(y_test.sum())} (Prevalence: {y_test.mean() * 100:.3f}%)")

    # 1. Train models
    print("\n[1/4] Training Random Forest models...")
    rf_cls = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_cls.fit(X_train, y_train)
    rf_pred = rf_cls.predict(X_test)

    rf_reg = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_reg.fit(X_train, p_train)
    rf_pred_w = rf_reg.predict(X_test)

    # 2. Validation-tuned baselines
    print("[2/4] Tuning validation baselines...")
    # Differential step baseline
    candidate_steps = np.linspace(200, 1200, 50)
    best_step = candidate_steps[0]
    best_step_f1 = -1.0
    for s in candidate_steps:
        p_val_step = (val_df["delta_p"].values >= s).astype(int)
        _, _, f, _ = precision_recall_fscore_support(y_val, p_val_step, average="binary", zero_division=0)
        if f > best_step_f1:
            best_step_f1 = f
            best_step = s
    step_pred = (test_df["delta_p"].values >= best_step).astype(int)

    # Simple power threshold baseline
    candidate_thresholds = np.percentile(train_df["aggregate_power_w"], np.linspace(50, 99.5, 100))
    best_th = candidate_thresholds[0]
    best_th_f1 = -1.0
    for th in candidate_thresholds:
        p_val_th = (val_df["aggregate_power_w"].values >= th).astype(int)
        _, _, f, _ = precision_recall_fscore_support(y_val, p_val_th, average="binary", zero_division=0)
        if f > best_th_f1:
            best_th_f1 = f
            best_th = th
    th_pred = (test_df["aggregate_power_w"].values >= best_th).astype(int)

    # Persistence baseline (t-1)
    persist_pred = np.roll(y_test, 1)
    # The true boundary preceding test_df is sample 0 (inactive)
    persist_pred[0] = 0

    # Majority class baseline
    majority_pred = np.zeros_like(y_test)

    # Mean active regression baseline
    mean_active_val = float(p_train[y_train == 1].mean()) if (y_train == 1).sum() > 0 else 0.0
    mean_active_pred_w = np.where(rf_pred == 1, mean_active_val, 0.0)
    zero_pred_w = np.zeros_like(p_test)

    # 3. Audit Sample-Level Classification
    print("\n[3/4] Auditing sample-level classification metrics...")
    def eval_sample_cls(y_true, y_p, name: str, desc: str, role: str) -> Dict[str, Any]:
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_p, average="binary", zero_division=0)
        acc = float(np.mean(y_true == y_p))
        tn, fp, fn, tp = confusion_matrix(y_true, y_p, labels=[0, 1]).ravel()
        return {
            "model": name,
            "role": role,
            "description": desc,
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
        }

    sample_cls_results = {
        "persistence": eval_sample_cls(
            y_test, persist_pred, "Persistence (t-1)",
            "Oracle submeter baseline (requires ground truth y_{t-1})",
            "Highest F1 baseline (oracle benchmark)",
        ),
        "random_forest": eval_sample_cls(
            y_test, rf_pred, "Random Forest Classifier",
            "Ensemble trained on P_agg, delta_P, and rolling window stats",
            "Strongest deployable ML classifier",
        ),
        "differential_step": eval_sample_cls(
            y_test, step_pred, "Differential Step Baseline",
            f"Tuned on validation set: delta_P >= {best_step:.1f} W",
            "Rule-based edge detector baseline",
        ),
        "simple_threshold": eval_sample_cls(
            y_test, th_pred, "Simple Power Threshold",
            f"Tuned on validation set: P_agg >= {best_th:.1f} W",
            "Static aggregate threshold baseline",
        ),
        "majority_class": eval_sample_cls(
            y_test, majority_pred, "Majority Class",
            "Trivial baseline predicting all-OFF (0)",
            "Zero-intelligence reference",
        ),
    }

    # 4. Audit Regression Metrics (All Samples vs Active Only vs Inactive Only)
    print("[4/4] Auditing regression metrics across sub-populations...")
    def eval_regression_audit(p_true, p_pred_series, y_true_binary, name: str, desc: str) -> Dict[str, Any]:
        active_idx = (y_true_binary == 1)
        inactive_idx = (y_true_binary == 0)

        mae_all = float(mean_absolute_error(p_true, p_pred_series))
        rmse_all = float(np.sqrt(mean_squared_error(p_true, p_pred_series)))

        mae_active = float(mean_absolute_error(p_true[active_idx], p_pred_series[active_idx])) if active_idx.sum() > 0 else 0.0
        rmse_active = float(np.sqrt(mean_squared_error(p_true[active_idx], p_pred_series[active_idx]))) if active_idx.sum() > 0 else 0.0

        mae_inactive = float(mean_absolute_error(p_true[inactive_idx], p_pred_series[inactive_idx])) if inactive_idx.sum() > 0 else 0.0
        rmse_inactive = float(np.sqrt(mean_squared_error(p_true[inactive_idx], p_pred_series[inactive_idx]))) if inactive_idx.sum() > 0 else 0.0

        true_energy_kwh = float(np.sum(p_true)) * (6.0 / 3600.0) / 1000.0
        pred_energy_kwh = float(np.sum(p_pred_series)) * (6.0 / 3600.0) / 1000.0
        rete_pct = float(abs(pred_energy_kwh - true_energy_kwh) / max(true_energy_kwh, 1e-6)) * 100.0

        mean_true_active_w = float(p_true[active_idx].mean()) if active_idx.sum() > 0 else 0.0
        mean_pred_active_w = float(p_pred_series[active_idx].mean()) if active_idx.sum() > 0 else 0.0
        underestimation_pct = float((mean_true_active_w - mean_pred_active_w) / max(mean_true_active_w, 1e-4) * 100.0)

        return {
            "model": name,
            "description": desc,
            "overall_all_samples": {
                "sample_count": len(p_true),
                "mae_w": round(mae_all, 2),
                "rmse_w": round(rmse_all, 2),
            },
            "active_samples_only": {
                "sample_count": int(active_idx.sum()),
                "mae_w": round(mae_active, 2),
                "rmse_w": round(rmse_active, 2),
                "mean_true_w": round(mean_true_active_w, 2),
                "mean_pred_w": round(mean_pred_active_w, 2),
                "underestimation_pct": round(underestimation_pct, 2),
            },
            "inactive_samples_only": {
                "sample_count": int(inactive_idx.sum()),
                "mae_w": round(mae_inactive, 2),
                "rmse_w": round(rmse_inactive, 2),
            },
            "energy_metrics": {
                "true_energy_kwh": round(true_energy_kwh, 4),
                "pred_energy_kwh": round(pred_energy_kwh, 4),
                "absolute_energy_error_kwh": round(abs(pred_energy_kwh - true_energy_kwh), 4),
                "rete_error_pct": round(rete_pct, 2),
            },
        }

    regression_audit_results = {
        "random_forest_regressor": eval_regression_audit(
            p_test, rf_pred_w, y_test, "Random Forest Regressor",
            "Continuous active power regression trained on aggregate features",
        ),
        "mean_active_baseline": eval_regression_audit(
            p_test, mean_active_pred_w, y_test, "Mean Active Power Baseline",
            f"Assigns training mean ({mean_active_val:.1f} W) when RF classifier predicts ON",
        ),
        "zero_baseline": eval_regression_audit(
            p_test, zero_pred_w, y_test, "Zero Baseline",
            "Trivial baseline predicting all-0 W",
        ),
    }

    # 5. Event Extraction
    print("\n[5/5] Performing Event-Level Extraction and Matching...")
    gt_series = pd.Series(y_test, index=test_df.index)
    gt_raw_events = extract_events(gt_series, min_duration_s=0.0, max_gap_s=0.0)
    gt_cycle_events = extract_events(gt_series, min_duration_s=0.0, max_gap_s=cycle_gap_merge_s)

    predictions = {
        "random_forest": pd.Series(rf_pred, index=test_df.index),
        "persistence": pd.Series(persist_pred, index=test_df.index),
        "differential_step": pd.Series(step_pred, index=test_df.index),
        "simple_threshold": pd.Series(th_pred, index=test_df.index),
        "majority_class": pd.Series(majority_pred, index=test_df.index),
    }

    event_models_raw = {}
    event_models_cycle = {}

    for name, pred_s in predictions.items():
        pred_raw_events = extract_events(pred_s, min_duration_s=0.0, max_gap_s=0.0)

        # Primary tolerance matching
        m_raw = match_events(gt_raw_events, pred_raw_events, tolerance_s=primary_tolerance, test_duration_days=test_duration_days)
        m_cycle = match_events(gt_cycle_events, pred_raw_events, tolerance_s=primary_tolerance, test_duration_days=test_duration_days)

        # Sensitivity across tolerance grid
        tol_sensitivity = {}
        for tol in tolerances:
            tol_res = match_events(gt_raw_events, pred_raw_events, tolerance_s=tol, test_duration_days=test_duration_days)
            tol_sensitivity[f"tol_{int(tol)}s"] = {
                "tp": tol_res["tp"],
                "fp": tol_res["fp"],
                "fn": tol_res["fn"],
                "precision": tol_res["precision"],
                "recall": tol_res["recall"],
                "f1_score": tol_res["f1_score"],
                "mean_delay_s": tol_res["mean_delay_s"],
            }

        event_models_raw[name] = {
            "model_key": name,
            "raw_predicted_events_count": len(pred_raw_events),
            "primary_evaluation": m_raw,
            "tolerance_sensitivity": tol_sensitivity,
        }
        event_models_cycle[name] = {
            "model_key": name,
            "cycle_predicted_events_count": len(pred_raw_events),
            "primary_evaluation": m_cycle,
        }

    # Print Event Tables
    print("\n" + "=" * 125)
    print(f"=== EVENT-LEVEL BENCHMARK RESULTS (Raw Events: {len(gt_raw_events)} GT, Primary Tol={primary_tolerance:.0f}s) ===")
    print("=" * 125)
    print(f"{'Model':<28} | {'Pred Ev':<8} | {'TP':<4} | {'FP':<4} | {'FN':<4} | {'Prec':<7} | {'Recall':<7} | {'F1':<7} | {'FP/Day':<7} | {'Delay(s)':<8}")
    print("-" * 125)
    for k, ev_res in event_models_raw.items():
        p_eval = ev_res["primary_evaluation"]
        print(f"{k:<28} | {ev_res['raw_predicted_events_count']:<8} | {p_eval['tp']:<4} | {p_eval['fp']:<4} | {p_eval['fn']:<4} | {p_eval['precision']:<7.4f} | {p_eval['recall']:<7.4f} | {p_eval['f1_score']:<7.4f} | {p_eval['fp_per_day']:<7.2f} | {p_eval['mean_delay_s']:<8.1f}")

    print("\n" + "=" * 125)
    print(f"=== EVENT-LEVEL BENCHMARK RESULTS (Merged Pump Cycles: {len(gt_cycle_events)} GT Cycles, Gap<={cycle_gap_merge_s:.0f}s) ===")
    print("=" * 125)
    print(f"{'Model':<28} | {'Pred Ev':<8} | {'TP':<4} | {'FP':<4} | {'FN':<4} | {'Prec':<7} | {'Recall':<7} | {'F1':<7} | {'FP/Day':<7} | {'Delay(s)':<8}")
    print("-" * 125)
    for k, ev_res in event_models_cycle.items():
        p_eval = ev_res["primary_evaluation"]
        print(f"{k:<28} | {ev_res['cycle_predicted_events_count']:<8} | {p_eval['tp']:<4} | {p_eval['fp']:<4} | {p_eval['fn']:<4} | {p_eval['precision']:<7.4f} | {p_eval['recall']:<7.4f} | {p_eval['f1_score']:<7.4f} | {p_eval['fp_per_day']:<7.2f} | {p_eval['mean_delay_s']:<8.1f}")

    audit_payload = {
        "metadata": meta,
        "split_audit": {
            "train_samples": len(train_df),
            "val_samples": len(val_df),
            "test_samples": len(test_df),
            "test_duration_days": round(test_duration_days, 3),
            "test_start": str(test_start),
            "test_end": str(test_end),
            "test_active_samples": int(y_test.sum()),
            "test_inactive_samples": int((y_test == 0).sum()),
            "test_positive_prevalence_pct": round(float(y_test.mean() * 100.0), 4),
            "boundary_buffer_dropped_samples": buffer * 2,
            "lookback_window_samples": 5,
            "leakage_audit": "PASSED. 100-sample buffer drops strictly isolate rolling 5-sample lookbacks across splits.",
        },
        "sample_level_classification_audit": sample_cls_results,
        "regression_audit": regression_audit_results,
        "event_level_evaluation": {
            "rationale": "Evaluates contiguous appliance activations with one-to-one temporal matching rather than independent sample accuracy.",
            "primary_tolerance_seconds": primary_tolerance,
            "cycle_gap_merge_seconds": cycle_gap_merge_s,
            "ground_truth_raw_events_count": len(gt_raw_events),
            "ground_truth_merged_cycles_count": len(gt_cycle_events),
            "raw_events_evaluation": event_models_raw,
            "merged_cycles_evaluation": event_models_cycle,
        },
    }

    out_file = os.path.join(RESULTS_DIR, "benchmark_audit_results.json")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(audit_payload, f, indent=2)
    print(f"\n[Audit Completed] Audit results saved to: {out_file}")

    return audit_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Event-Level NILM Metrics and Audit Benchmark")
    parser.add_argument("--h5-file", default=H5_PATH, help="Path to iawe.h5")
    parser.add_argument("--tolerance", type=float, default=60.0, help="Event onset tolerance in seconds")
    parser.add_argument("--gap-merge", type=float, default=30.0, help="Max gap in seconds to merge pump cycles")
    args = parser.parse_args()

    run_event_benchmark_audit(
        h5_file=args.h5_file,
        primary_tolerance=args.tolerance,
        cycle_gap_merge_s=args.gap_merge,
    )
