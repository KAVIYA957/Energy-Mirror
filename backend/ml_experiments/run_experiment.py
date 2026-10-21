"""
run_experiment.py - End-to-End NILM Machine Learning Baseline Experiment Runner

Executes the ML baseline experiment pipeline defined in Milestone 2A:
  1. Loads dataset or realistic ground-truth benchmark trace.
  2. Detects contiguous chunks and isolates gaps > 60s (no silent interpolation).
  3. Binarizes target appliance ground-truth (with minimum duration hysteresis).
  4. Extracts sliding window features (mean, std, min, max, range, instantaneous delta, window delta, PF if present).
  5. Partitions chronologically: 60% Train, 20% Validation, 20% Test (with boundary buffer).
  6. Trains the scientifically selected candidate:
     - Random Forest Classifier (n_estimators=100, max_depth=8, random_state=42).
     - Random Forest Regressor (for power estimation in Watts).
  7. Evaluates against Simple Threshold Baseline and Persistence Baseline.
  8. Computes Precision, Recall, F1-Score, Confusion Matrix, MAE (W), RMSE (W), REEE.
  9. Saves artifacts and report to backend/ml_experiments/results/.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import asdict
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from preprocess import NILMPreprocessor, PreprocessingConfig
from evaluate import (
    compute_classification_metrics,
    compute_power_metrics,
    evaluate_baseline_models,
    print_evaluation_summary,
)

def generate_benchmark_trace(
    duration_hours: float = 6.0,
    sample_rate_s: float = 1.0,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generates a realistic multi-hour household electrical trace with known
    ground-truth appliance activations, background base load, and measurement noise
    for pipeline verification and reproducible benchmarking.
    """
    np.random.seed(random_seed)
    n_samples = int(duration_hours * 3600 / sample_rate_s)
    start_time = datetime(2026, 10, 20, 0, 0, 0)
    timestamps = [start_time + timedelta(seconds=i * sample_rate_s) for i in range(n_samples)]

    # 1. Background Unattributed Standby Load (~12W + fluctuating noise)
    background_p = 12.0 + np.random.normal(0, 1.2, n_samples)
    background_p = np.clip(background_p, 8.0, 20.0)

    # 2. Target Appliance: Water Pump (Nominal 75W inductive motor)
    # Activates periodically (e.g. 3 cycles across the 6-hour period)
    pump_truth = np.zeros(n_samples, dtype=np.float32)
    pump_cycles = [
        (int(n_samples * 0.15), int(n_samples * 0.22)),  # Cycle 1: in train split
        (int(n_samples * 0.40), int(n_samples * 0.48)),  # Cycle 2: in train split
        (int(n_samples * 0.68), int(n_samples * 0.74)),  # Cycle 3: in val split
        (int(n_samples * 0.85), int(n_samples * 0.92)),  # Cycle 4: in test split
    ]
    for start, end in pump_cycles:
        # 75W nominal with motor inrush transient and slight thermal settling
        dur = end - start
        spike = np.zeros(dur, dtype=np.float32)
        spike[0:3] = 120.0 # inrush transient
        spike[3:] = 75.0 + np.random.normal(0, 1.5, dur - 3)
        pump_truth[start:end] = spike

    # 3. Confounding Background Loads (simultaneous interference)
    # Fan (45W)
    fan_load = np.zeros(n_samples, dtype=np.float32)
    fan_load[int(n_samples * 0.30):int(n_samples * 0.80)] = 45.0 + np.random.normal(0, 0.8, int(n_samples * 0.50))

    # Water Heater (140W) - short active periods
    heater_load = np.zeros(n_samples, dtype=np.float32)
    heater_load[int(n_samples * 0.05):int(n_samples * 0.12)] = 140.0 + np.random.normal(0, 2.0, int(n_samples * 0.07))
    heater_load[int(n_samples * 0.88):int(n_samples * 0.90)] = 140.0 + np.random.normal(0, 2.0, int(n_samples * 0.02))

    # Total Aggregate Power = background + pump + fan + heater
    aggregate_p = background_p + pump_truth + fan_load + heater_load

    # Power Factor (composite calculation)
    # Resistive heater ~ 0.99, Pump ~ 0.78 inductive, Fan ~ 0.91, Standby ~ 0.90
    power_factor = np.full(n_samples, 0.92, dtype=np.float32)
    for start, end in pump_cycles:
        power_factor[start:end] = 0.81 + np.random.normal(0, 0.02, end - start)
    power_factor = np.clip(power_factor, 0.70, 0.99)

    return pd.DataFrame({
        "timestamp": timestamps,
        "aggregate_power_w": np.round(aggregate_p, 1),
        "power_factor": np.round(power_factor, 2),
        "pump_ground_truth_w": np.round(pump_truth, 1),
        "heater_ground_truth_w": np.round(heater_load, 1),
    })

def run_experiment(
    data_file: Optional[str] = None,
    target_appliance: str = "water_pump",
    output_dir: str = "backend/ml_experiments/results",
) -> Dict[str, Any]:
    """
    Executes the full preprocessing, training, baseline comparison, and evaluation pipeline.
    """
    print("=" * 80)
    print("ENERGY MIRROR ML BASELINE EXPERIMENT (MILESTONE 2A)")
    print("=" * 80)

    # 1. Load Data
    if data_file and os.path.exists(data_file):
        print(f"[Data] Loading dataset from: {data_file}")
        df = pd.read_csv(data_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        print("[Data] Generating reproducible 6-hour continuous household benchmark trace (1 Hz)...")
        df = generate_benchmark_trace(duration_hours=6.0, sample_rate_s=1.0)
        print(f"[Data] Generated {len(df):,} timestamped samples with multi-load interference.")

    # 2. Preprocessing & Gap Detection
    config = PreprocessingConfig(
        window_size_samples=15,
        step_size_samples=1,
        max_allowed_gap_s=60.0,
        on_power_threshold_w=20.0,
        min_on_duration_samples=3,
        train_ratio=0.60,
        val_ratio=0.20,
        test_ratio=0.20,
        random_seed=42,
    )
    preprocessor = NILMPreprocessor(config)

    chunks = preprocessor.detect_contiguous_chunks(df, time_col="timestamp")
    print(f"[Chunks] Detected {len(chunks)} contiguous time-series chunk(s) separated by gaps <= 60s.")

    # Work with primary contiguous segment
    active_chunk = chunks[0]
    p_agg = active_chunk["aggregate_power_w"].values
    pf_agg = active_chunk["power_factor"].values if "power_factor" in active_chunk else None

    target_col = "pump_ground_truth_w" if target_appliance == "water_pump" else "heater_ground_truth_w"
    nominal_w = 75.0 if target_appliance == "water_pump" else 140.0
    thresh_w = 40.0 if target_appliance == "water_pump" else 100.0

    app_power_truth = active_chunk[target_col].values
    app_class_truth = preprocessor.binarize_labels(app_power_truth)

    # 3. Extract Features
    X, feature_names = preprocessor.extract_window_features(p_agg, pf_agg=pf_agg)
    # Align labels with the center/last sample of each window
    W = config.window_size_samples
    y_class = app_class_truth[W - 1:]
    y_power = app_power_truth[W - 1:]
    p_curr = p_agg[W - 1:]

    # Truncate to matching length
    min_len = min(len(X), len(y_class))
    X = X[:min_len]
    y_class = y_class[:min_len]
    y_power = y_power[:min_len]
    p_curr = p_curr[:min_len]

    # 4. Chronological Splitting (No Leakage)
    splits = preprocessor.chronological_split(X, y_class, y_power)
    X_train, y_train_c, y_train_p = splits["X_train"], splits["y_train_class"], splits["y_train_power"]
    X_val, y_val_c, y_val_p = splits["X_val"], splits["y_val_class"], splits["y_val_power"]
    X_test, y_test_c, y_test_p = splits["X_test"], splits["y_test_class"], splits["y_test_power"]

    print(f"[Splits] Chronological partition: Train={len(X_train):,}, Val={len(X_val):,}, Test={len(X_test):,} samples.")
    print(f"[Splits] Test set positive class prevalence: {np.mean(y_test_c):.1%}")

    # 5. Train Random Forest Classifier
    print(f"\n[Training] Training Random Forest Classifier on {len(X_train):,} windowed features...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        random_state=config.random_seed,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train_c)

    # Train Random Forest Regressor for power estimation
    reg = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_split=4,
        random_state=config.random_seed,
        n_jobs=-1,
    )
    reg.fit(X_train, y_train_p)

    # 6. Predict on Held-Out Chronological Test Set
    y_pred_class = clf.predict(X_test)
    y_pred_power = reg.predict(X_test)

    # Evaluate ML Model
    ml_class_metrics = compute_classification_metrics(y_test_c, y_pred_class)
    ml_power_metrics = compute_power_metrics(y_test_p, y_pred_power)

    # Feature Importances
    importances = {name: round(float(imp), 4) for name, imp in zip(feature_names, clf.feature_importances_)}
    sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    # 7. Evaluate Reference Baselines on Identical Test Set
    test_start_idx = splits["split_indices"]["test"][0]
    p_curr_test = p_curr[test_start_idx:test_start_idx + len(y_test_c)]

    baseline_metrics = evaluate_baseline_models(
        X_test_p_curr=p_curr_test,
        y_test_class=y_test_c,
        y_test_power=y_test_p,
        nominal_on_power_w=nominal_w,
        threshold_w=thresh_w,
    )

    # 8. Print Standardized Report
    model_summary = {
        "classification": ml_class_metrics,
        "power_estimation": ml_power_metrics,
    }
    print_evaluation_summary(target_appliance, model_summary, baseline_metrics)

    print("\n[Feature Importances (Random Forest)]:")
    for feat, imp in list(sorted_importances.items())[:6]:
        print(f"  - {feat:<18}: {imp:.4f} ({imp*100:.1f}%)")

    # 9. Save Results & Metadata Artifacts
    os.makedirs(output_dir, exist_ok=True)
    results_payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "target_appliance": target_appliance,
        "nominal_power_w": nominal_w,
        "preprocessing_config": asdict(config),
        "split_indices": splits["split_indices"],
        "feature_names": feature_names,
        "feature_importances": sorted_importances,
        "ml_candidate_results": model_summary,
        "baseline_results": baseline_metrics,
        "verification_status": "EXPERIMENT_EXECUTED_SUCCESSFULLY",
    }
    output_path = os.path.join(output_dir, f"experiment_results_{target_appliance}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    print(f"\n[Artifacts] Full evaluation metrics saved to: {output_path}")

    return results_payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run NILM ML Baseline Experiment")
    parser.add_argument("--data", type=str, default=None, help="Path to input dataset CSV")
    parser.add_argument("--appliance", type=str, default="water_pump", choices=["water_pump", "water_heater"], help="Target appliance")
    parser.add_argument("--outdir", type=str, default="backend/ml_experiments/results", help="Output directory")
    args = parser.parse_args()

    run_experiment(data_file=args.data, target_appliance=args.appliance, output_dir=args.outdir)
