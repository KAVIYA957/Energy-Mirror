"""
evaluate.py - Standardized Evaluation Protocol for NILM Classification and Power Estimation

Implements the official evaluation criteria defined in Milestone 2A:
  1. Appliance ON/OFF state classification metrics:
     - Precision, Recall, F1-score, Accuracy, Confusion Matrix (TP, FP, TN, FN).
  2. Power estimation regression metrics:
     - Mean Absolute Error (MAE) in Watts.
     - Root Mean Squared Error (RMSE) in Watts.
     - Relative Energy Estimation Error (REEE / SAE).
  3. Classical baseline comparisons:
     - Simple Threshold Baseline.
     - Persistence Baseline (prior state carry-forward).
     - Mean Active State Power Baseline.
  4. Per-appliance performance reporting.
  5. Formatted tabular output and JSON export for verifiable reporting.
"""

import json
import math
from typing import Dict, Any, List, Optional
import numpy as np

def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Computes Precision, Recall, F1-score, Accuracy, and Confusion Matrix.
    Handles zero-division edge cases truthfully.
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    total = len(y_true)
    accuracy = (tp + tn) / total if total > 0 else 0.0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "accuracy": round(float(accuracy), 4),
        "confusion_matrix": {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
        },
        "sample_count": total,
        "positive_support": tp + fn,
    }

def compute_power_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Computes MAE, RMSE, and Relative Energy Estimation Error (REEE / SAE).
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)

    errors = np.abs(y_pred - y_true)
    mae = float(np.mean(errors))
    rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))

    sum_true = float(np.sum(y_true))
    sum_pred = float(np.sum(y_pred))
    reee = abs(sum_pred - sum_true) / sum_true if sum_true > 0 else (0.0 if sum_pred == 0 else 1.0)

    return {
        "mae_w": round(mae, 2),
        "rmse_w": round(rmse, 2),
        "energy_truth_wh": round(sum_true / 3600.0, 3), # assuming 1-sec sampling
        "energy_pred_wh": round(sum_pred / 3600.0, 3),
        "reee_ratio": round(float(reee), 4),
    }

def evaluate_baseline_models(
    X_test_p_curr: np.ndarray,
    y_test_class: np.ndarray,
    y_test_power: np.ndarray,
    nominal_on_power_w: float,
    threshold_w: float,
    step_threshold_w: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Evaluates four standardized reference baselines against held-out test data:
      1. Majority Class Baseline (predicts 0 / OFF state and 0.0 W always).
      2. Simple Power Threshold Baseline (classifies ON if p_curr >= threshold_w).
      3. Power-Change Threshold Baseline (differential step detector: triggers ON when delta_p >= step_thresh).
      4. Persistence Baseline (carries forward state and power from t-1).
    """
    N = len(y_test_class)
    step_thresh = step_threshold_w if step_threshold_w is not None else (nominal_on_power_w * 0.5)

    # 1. Majority-Class Baseline (Appliance is predominantly OFF)
    pred_class_majority = np.zeros(N, dtype=int)
    pred_power_majority = np.zeros(N, dtype=np.float64)
    metrics_majority_class = compute_classification_metrics(y_test_class, pred_class_majority)
    metrics_majority_power = compute_power_metrics(y_test_power, pred_power_majority)

    # 2. Simple Power Threshold Baseline
    pred_class_thresh = (X_test_p_curr >= threshold_w).astype(int)
    pred_power_thresh = pred_class_thresh.astype(np.float64) * nominal_on_power_w
    metrics_thresh_class = compute_classification_metrics(y_test_class, pred_class_thresh)
    metrics_thresh_power = compute_power_metrics(y_test_power, pred_power_thresh)

    # 3. Power-Change Threshold Baseline (Differential Step Detector)
    # Reconstructs state based on step changes in aggregate active power
    pred_class_step = np.zeros(N, dtype=int)
    current_state = 0
    delta_p = np.diff(X_test_p_curr, prepend=X_test_p_curr[0])
    for i in range(N):
        if delta_p[i] >= step_thresh:
            current_state = 1
        elif delta_p[i] <= -step_thresh:
            current_state = 0
        pred_class_step[i] = current_state
    pred_power_step = pred_class_step.astype(np.float64) * nominal_on_power_w
    metrics_step_class = compute_classification_metrics(y_test_class, pred_class_step)
    metrics_step_power = compute_power_metrics(y_test_power, pred_power_step)

    # 4. Persistence Baseline (Prior State Carry-Forward: y_t = y_{t-1})
    pred_class_persist = np.roll(y_test_class, 1)
    pred_class_persist[0] = 0
    pred_power_persist = np.roll(y_test_power, 1)
    pred_power_persist[0] = 0.0
    metrics_persist_class = compute_classification_metrics(y_test_class, pred_class_persist)
    metrics_persist_power = compute_power_metrics(y_test_power, pred_power_persist)

    return {
        "majority_class_baseline": {
            "classification": metrics_majority_class,
            "power_estimation": metrics_majority_power,
        },
        "simple_threshold_baseline": {
            "threshold_w": threshold_w,
            "classification": metrics_thresh_class,
            "power_estimation": metrics_thresh_power,
        },
        "power_change_threshold_baseline": {
            "step_threshold_w": step_thresh,
            "classification": metrics_step_class,
            "power_estimation": metrics_step_power,
        },
        "persistence_baseline": {
            "classification": metrics_persist_class,
            "power_estimation": metrics_persist_power,
        },
    }

def print_evaluation_summary(appliance_name: str, model_results: Dict[str, Any], baseline_results: Dict[str, Any]):
    print("\n" + "=" * 90)
    print(f"NILM VALIDATION REPORT: {appliance_name.upper()} (HELD-OUT TEST SET)")
    print("=" * 90)

    # --- TASK 1: APPLIANCE ON/OFF STATE DETECTION ---
    print("\n[TASK 1: APPLIANCE ON/OFF STATE DETECTION (CLASSIFICATION)]")
    print(f"{'Model / Baseline':<32} | {'F1-Score':<10} | {'Precision':<10} | {'Recall':<10} | {'Accuracy':<10}")
    print("-" * 90)

    ml_c = model_results.get("classification", {})
    print(f"{'ML Candidate (Random Forest)':<32} | {ml_c.get('f1_score', 0):<10.4f} | {ml_c.get('precision', 0):<10.4f} | {ml_c.get('recall', 0):<10.4f} | {ml_c.get('accuracy', 0):<10.4f}")

    st_c = baseline_results.get("simple_threshold_baseline", {}).get("classification", {})
    print(f"{'Simple Power Threshold Baseline':<32} | {st_c.get('f1_score', 0):<10.4f} | {st_c.get('precision', 0):<10.4f} | {st_c.get('recall', 0):<10.4f} | {st_c.get('accuracy', 0):<10.4f}")

    sc_c = baseline_results.get("power_change_threshold_baseline", {}).get("classification", {})
    print(f"{'Power-Change Step Baseline':<32} | {sc_c.get('f1_score', 0):<10.4f} | {sc_c.get('precision', 0):<10.4f} | {sc_c.get('recall', 0):<10.4f} | {sc_c.get('accuracy', 0):<10.4f}")

    ps_c = baseline_results.get("persistence_baseline", {}).get("classification", {})
    print(f"{'Persistence Baseline (t-1)':<32} | {ps_c.get('f1_score', 0):<10.4f} | {ps_c.get('precision', 0):<10.4f} | {ps_c.get('recall', 0):<10.4f} | {ps_c.get('accuracy', 0):<10.4f}")

    mj_c = baseline_results.get("majority_class_baseline", {}).get("classification", {})
    print(f"{'Majority-Class Baseline (All-0)':<32} | {mj_c.get('f1_score', 0):<10.4f} | {mj_c.get('precision', 0):<10.4f} | {mj_c.get('recall', 0):<10.4f} | {mj_c.get('accuracy', 0):<10.4f}")

    # --- TASK 2: APPLIANCE-LEVEL POWER ESTIMATION ---
    print("\n[TASK 2: APPLIANCE-LEVEL POWER ESTIMATION (REGRESSION / DISAGGREGATION)]")
    print(f"{'Model / Baseline':<32} | {'MAE (W)':<10} | {'RMSE (W)':<10} | {'REEE (SAE)':<12} | {'Pred Energy (Wh)':<16}")
    print("-" * 90)

    ml_p = model_results.get("power_estimation", {})
    print(f"{'ML Candidate (Random Forest)':<32} | {ml_p.get('mae_w', 0):<10.2f} | {ml_p.get('rmse_w', 0):<10.2f} | {ml_p.get('reee_ratio', 0):<12.4f} | {ml_p.get('energy_pred_wh', 0):<16.2f}")

    st_p = baseline_results.get("simple_threshold_baseline", {}).get("power_estimation", {})
    print(f"{'Simple Power Threshold Baseline':<32} | {st_p.get('mae_w', 0):<10.2f} | {st_p.get('rmse_w', 0):<10.2f} | {st_p.get('reee_ratio', 0):<12.4f} | {st_p.get('energy_pred_wh', 0):<16.2f}")

    sc_p = baseline_results.get("power_change_threshold_baseline", {}).get("power_estimation", {})
    print(f"{'Power-Change Step Baseline':<32} | {sc_p.get('mae_w', 0):<10.2f} | {sc_p.get('rmse_w', 0):<10.2f} | {sc_p.get('reee_ratio', 0):<12.4f} | {sc_p.get('energy_pred_wh', 0):<16.2f}")

    ps_p = baseline_results.get("persistence_baseline", {}).get("power_estimation", {})
    print(f"{'Persistence Baseline (t-1)':<32} | {ps_p.get('mae_w', 0):<10.2f} | {ps_p.get('rmse_w', 0):<10.2f} | {ps_p.get('reee_ratio', 0):<12.4f} | {ps_p.get('energy_pred_wh', 0):<16.2f}")

    mj_p = baseline_results.get("majority_class_baseline", {}).get("power_estimation", {})
    print(f"{'Majority-Class Baseline (0 W)':<32} | {mj_p.get('mae_w', 0):<10.2f} | {mj_p.get('rmse_w', 0):<10.2f} | {mj_p.get('reee_ratio', 0):<12.4f} | {mj_p.get('energy_pred_wh', 0):<16.2f}")
    print("=" * 90)
