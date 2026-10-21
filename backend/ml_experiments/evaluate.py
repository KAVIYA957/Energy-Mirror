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
) -> Dict[str, Any]:
    """
    Evaluates two reference baselines:
      1. Simple Thresholding: Classify ON if current aggregate power exceeds threshold.
      2. Mean Active Power Baseline: When classified ON, predict nominal on-power; when OFF, predict 0.
    """
    # 1. Simple Thresholding Baseline
    pred_class_thresh = (X_test_p_curr >= threshold_w).astype(int)
    metrics_thresh_class = compute_classification_metrics(y_test_class, pred_class_thresh)

    # Power estimation from simple threshold
    pred_power_thresh = pred_class_thresh * nominal_on_power_w
    metrics_thresh_power = compute_power_metrics(y_test_power, pred_power_thresh)

    # 2. Persistence Baseline (prior state carry-forward)
    pred_class_persist = np.roll(y_test_class, 1)
    pred_class_persist[0] = 0
    metrics_persist_class = compute_classification_metrics(y_test_class, pred_class_persist)

    pred_power_persist = np.roll(y_test_power, 1)
    pred_power_persist[0] = 0.0
    metrics_persist_power = compute_power_metrics(y_test_power, pred_power_persist)

    return {
        "simple_threshold_baseline": {
            "threshold_w": threshold_w,
            "classification": metrics_thresh_class,
            "power_estimation": metrics_thresh_power,
        },
        "persistence_baseline": {
            "classification": metrics_persist_class,
            "power_estimation": metrics_persist_power,
        }
    }

def print_evaluation_summary(appliance_name: str, model_results: Dict[str, Any], baseline_results: Dict[str, Any]):
    print("\n" + "=" * 78)
    print(f"NILM EVALUATION REPORT: {appliance_name.upper()}")
    print("=" * 78)
    print(f"{'Model / Baseline':<28} | {'F1-Score':<10} | {'Precision':<10} | {'Recall':<10} | {'MAE (W)':<10}")
    print("-" * 78)

    # ML Model
    ml_c = model_results.get("classification", {})
    ml_p = model_results.get("power_estimation", {})
    print(f"{'ML Candidate (Random Forest)':<28} | {ml_c.get('f1_score', 0):<10} | {ml_c.get('precision', 0):<10} | {ml_c.get('recall', 0):<10} | {ml_p.get('mae_w', 'N/A'):<10}")

    # Baselines
    st_b = baseline_results.get("simple_threshold_baseline", {})
    st_c = st_b.get("classification", {})
    st_p = st_b.get("power_estimation", {})
    print(f"{'Simple Threshold Baseline':<28} | {st_c.get('f1_score', 0):<10} | {st_c.get('precision', 0):<10} | {st_c.get('recall', 0):<10} | {st_p.get('mae_w', 'N/A'):<10}")

    ps_b = baseline_results.get("persistence_baseline", {})
    ps_c = ps_b.get("classification", {})
    ps_p = ps_b.get("power_estimation", {})
    print(f"{'Persistence Baseline (t-1)':<28} | {ps_c.get('f1_score', 0):<10} | {ps_c.get('precision', 0):<10} | {ps_c.get('recall', 0):<10} | {ps_p.get('mae_w', 'N/A'):<10}")
    print("=" * 78)
