"""
run_iawe_experiment.py - Genuine iAWE Public NILM Dataset Experiment Pipeline.

Executes rigorous held-out chronological evaluation on the real Indian household dataset (iAWE):
- Targets verified Water Motor: /building1/elec/meter12 (CurrentCost CT submeter).
- Targets verified Mains Aggregate: /building1/elec/meter1 + /building1/elec/meter2 (Schneider EM6400).
- Overlapping time period: 2013-05-30 12:51:41 to 2013-07-05 15:41:46 (~36 days).
- Aligns to 6-second resolution (matching CurrentCost native transmission).
- Masks 32767.0 sensor overflow/loss-of-signal artifacts.
- Evaluates 5 distinct models on Task 1 (Classification: Water Motor ON/OFF):
  1. Random Forest Classifier
  2. Simple Aggregate Power Threshold Baseline
  3. Differential Power Change Baseline
  4. Persistence Baseline (t-1)
  5. Majority Class Baseline
- Evaluates Task 2 (Power Disaggregation):
  1. Random Forest Regressor
  2. Mean Active Power Baseline
  3. Zero Baseline
- Strict chronological train/val/test split (60% Train, 20% Val, 20% Test) with boundary drops.
- Saves machine-readable results to backend/ml_experiments/results/iawe_baseline_results.json.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, mean_absolute_error, mean_squared_error

H5_PATH = os.path.join(os.path.dirname(__file__), "data", "iawe.h5")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
RESULTS_FILE = os.path.join(RESULTS_DIR, "iawe_baseline_results.json")

def load_iawe_dataset(
    h5_file: str = H5_PATH,
    on_threshold_w: float = 200.0,
    resample_freq: str = "6s",
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads Schneider EM6400 mains (meters 1 & 2) and CurrentCost motor (meter 12),
    filters overflow artifacts, resamples to a common 6-second time grid,
    and returns aligned DataFrame and audit metadata.
    """
    if not os.path.exists(h5_file):
        raise FileNotFoundError(f"iAWE HDF5 file not found: {h5_file}")

    t0 = time.time()
    print(f"Loading iAWE dataset from: {h5_file}")

    metadata = {
        "dataset": "iAWE (Indian Dataset for Ambient Water and Energy)",
        "citation": "Batra et al., IIIT Delhi, BuildSys 2013 / Zenodo 13917372",
        "licence": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "file_size_bytes": os.path.getsize(h5_file),
        "file_size_mb": round(os.path.getsize(h5_file) / (1024 * 1024), 2),
        "target_appliance": "Water Motor (Overhead Tank Lift Pump)",
        "target_submeter": "/building1/elec/meter12",
        "mains_submeters": ["/building1/elec/meter1", "/building1/elec/meter2"],
        "resample_frequency": resample_freq,
        "on_threshold_w": on_threshold_w,
    }

    with pd.HDFStore(h5_file, mode="r") as store:
        # Load meter12 (Motor)
        print("  Reading Meter 12 (Motor)...")
        m12 = store.select("/building1/elec/meter12")
        p_motor_raw = m12[("power", "active")] if ("power", "active") in m12.columns else m12.iloc[:, 0]
        p_motor_raw = p_motor_raw.rename("motor_w")

        # Determine overlapping time window
        start_ts = p_motor_raw.index.min()
        end_ts = p_motor_raw.index.max()
        print(f"  Motor monitoring window: {start_ts} to {end_ts} ({len(p_motor_raw):,} raw readings)")

        # Query mains strictly within motor time window to avoid loading irrelevant weeks
        query_str = f"index >= '{start_ts}' and index <= '{end_ts}'"
        print(f"  Reading Mains (Meters 1 & 2) in overlapping window...")
        m1 = store.select("/building1/elec/meter1", where=query_str)
        m2 = store.select("/building1/elec/meter2", where=query_str)

        p1_raw = m1[("power", "active")].rename("mains_p1")
        p2_raw = m2[("power", "active")].rename("mains_p2")

    load_duration = time.time() - t0
    print(f"  Raw data loaded in {load_duration:.2f}s.")

    # 1. Audit and clean raw sensor readings
    n_motor_raw = len(p_motor_raw)
    n_overflow = (p_motor_raw >= 30000).sum()
    print(f"  Motor overflow artifacts (>= 30kW / 32767 sentinel): {n_overflow:,} ({n_overflow / n_motor_raw * 100:.3f}%)")
    p_motor_clean = p_motor_raw.copy()
    p_motor_clean[p_motor_clean >= 30000] = np.nan

    # 2. Resample mains to 6-second grid
    print(f"  Resampling Mains and Submeter to {resample_freq} time grid...")
    mains_sum = (p1_raw + p2_raw).rename("aggregate_power_w")
    mains_6s = mains_sum.resample(resample_freq).mean()

    # 3. Resample motor to 6-second grid
    # For motor, missing readings during normal gaps represent 0W (idle)
    motor_6s = p_motor_clean.resample(resample_freq).mean().fillna(0.0)

    # 4. Merge into single synchronized DataFrame
    df = pd.concat([mains_6s, motor_6s], axis=1).sort_index()

    # Drop any remaining NaNs in aggregate power (grid outages / meter power failures)
    n_initial_grid = len(df)
    df = df.dropna(subset=["aggregate_power_w"])
    nan_mains_dropped = n_initial_grid - len(df)

    # Physical validity filtering
    valid_mask = (df["aggregate_power_w"] >= 0) & (df["aggregate_power_w"] <= 25000)
    valid_mask &= (df["motor_w"] >= 0) & (df["motor_w"] <= 3000)
    df = df[valid_mask]

    # Label binary ON/OFF state
    df["state"] = (df["motor_w"] >= on_threshold_w).astype(int)

    # Feature engineering for step detection
    df["delta_p"] = df["aggregate_power_w"].diff().fillna(0.0)
    df["rolling_mean_5"] = df["aggregate_power_w"].rolling(window=5, min_periods=1).mean()
    df["rolling_std_5"] = df["aggregate_power_w"].rolling(window=5, min_periods=1).std().fillna(0.0)
    df["rolling_max_5"] = df["aggregate_power_w"].rolling(window=5, min_periods=1).max()

    active_mask = df["state"] == 1
    n_active = active_mask.sum()
    pct_active = n_active / len(df) * 100

    print(f"\n--- iAWE Alignment & Data Quality Audit ---")
    print(f"Total synchronized 6s intervals: {len(df):,}")
    print(f"Mains dropouts (grid outage / missing aggregate): {nan_mains_dropped:,} ({nan_mains_dropped / n_initial_grid * 100:.2f}%)")
    print(f"Water Motor active samples (>= {on_threshold_w}W): {n_active:,} ({pct_active:.3f}%)")
    print(f"Water Motor mean active power: {df.loc[active_mask, 'motor_w'].mean():.1f} W (std={df.loc[active_mask, 'motor_w'].std():.1f} W)")
    print(f"Water Motor median active power: {df.loc[active_mask, 'motor_w'].median():.1f} W")
    print(f"Aggregate mains mean power: {df['aggregate_power_w'].mean():.1f} W (max={df['aggregate_power_w'].max():.1f} W)")

    metadata.update({
        "raw_motor_readings": int(n_motor_raw),
        "overflow_artifacts_filtered": int(n_overflow),
        "grid_outage_intervals_dropped": int(nan_mains_dropped),
        "synchronized_samples": int(len(df)),
        "active_motor_samples": int(n_active),
        "positive_prevalence_pct": round(float(pct_active), 4),
        "mean_active_power_w": round(float(df.loc[active_mask, 'motor_w'].mean()), 2) if n_active > 0 else 0.0,
        "median_active_power_w": round(float(df.loc[active_mask, 'motor_w'].median()), 2) if n_active > 0 else 0.0,
        "std_active_power_w": round(float(df.loc[active_mask, 'motor_w'].std()), 2) if n_active > 0 else 0.0,
        "start_timestamp": str(df.index.min()),
        "end_timestamp": str(df.index.max()),
    })

    return df, metadata

def run_iawe_benchmark(df: pd.DataFrame, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes chronological held-out evaluation:
    - 60% Train, 20% Validation, 20% Test.
    - Drops 100-sample boundary buffer between partitions to prevent rolling leakage.
    - Evaluates 5 classification baselines and 3 power disaggregation baselines.
    """
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

    split_info = {
        "train_samples": len(train_df),
        "train_active_samples": int(y_train.sum()),
        "train_prevalence_pct": round(float(y_train.mean() * 100), 3),
        "val_samples": len(val_df),
        "val_active_samples": int(y_val.sum()),
        "val_prevalence_pct": round(float(y_val.mean() * 100), 3),
        "test_samples": len(test_df),
        "test_active_samples": int(y_test.sum()),
        "test_prevalence_pct": round(float(y_test.mean() * 100), 3),
        "boundary_dropped_samples": buffer * 2,
    }

    print("\n--- Chronological Split Partitions ---")
    print(f"Train: {len(train_df):,} samples ({split_info['train_prevalence_pct']}% ON, {split_info['train_active_samples']} events)")
    print(f"Val:   {len(val_df):,} samples ({split_info['val_prevalence_pct']}% ON, {split_info['val_active_samples']} events)")
    print(f"Test:  {len(test_df):,} samples ({split_info['test_prevalence_pct']}% ON, {split_info['test_active_samples']} events)")

    results = {
        "metadata": meta,
        "split": split_info,
        "classification_baselines": {},
        "regression_baselines": {},
    }

    def eval_cls(y_true, y_pred, model_name: str, desc: str) -> Dict[str, Any]:
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        acc = float(np.mean(y_true == y_pred))
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        return {
            "model": model_name,
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

    # Model 1: Random Forest Classifier
    print("\nTraining Model 1: Random Forest Classifier (100 trees, depth 10)...")
    rf_cls = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_cls.fit(X_train, y_train)
    rf_pred = rf_cls.predict(X_test)
    results["classification_baselines"]["random_forest"] = eval_cls(
        y_test, rf_pred, "Random Forest Classifier", "Nonlinear ensemble trained on P_agg, delta_P, and rolling window stats"
    )

    # Model 2: Simple Power Threshold Baseline
    print("Evaluating Model 2: Simple Aggregate Power Threshold Baseline...")
    candidate_thresholds = np.percentile(train_df["aggregate_power_w"], np.linspace(50, 99.5, 100))
    best_th = candidate_thresholds[0]
    best_f1 = -1.0
    for th in candidate_thresholds:
        p_val = (val_df["aggregate_power_w"].values >= th).astype(int)
        _, _, f, _ = precision_recall_fscore_support(y_val, p_val, average="binary", zero_division=0)
        if f > best_f1:
            best_f1 = f
            best_th = th
    th_pred = (test_df["aggregate_power_w"].values >= best_th).astype(int)
    results["classification_baselines"]["simple_threshold"] = eval_cls(
        y_test, th_pred, "Simple Power Threshold", f"Tuned on validation set: P_agg >= {best_th:.1f} W"
    )

    # Model 3: Differential Power Step Baseline
    print("Evaluating Model 3: Differential Power Change Baseline...")
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
    results["classification_baselines"]["differential_step"] = eval_cls(
        y_test, step_pred, "Differential Step Baseline", f"Tuned on validation set: delta_P >= {best_step:.1f} W"
    )

    # Model 4: Persistence Baseline (y_t = y_{t-1})
    print("Evaluating Model 4: Persistence Baseline...")
    persist_pred = np.roll(y_test, 1)
    persist_pred[0] = y_train[-1]
    results["classification_baselines"]["persistence"] = eval_cls(
        y_test, persist_pred, "Persistence (t-1)", "Predicts state at t is identical to state at t-1"
    )

    # Model 5: Majority Class Baseline (predict all zeros)
    print("Evaluating Model 5: Majority Class Baseline...")
    majority_pred = np.zeros_like(y_test)
    results["classification_baselines"]["majority_class"] = eval_cls(
        y_test, majority_pred, "Majority Class", "Trivial baseline predicting all-OFF state (class 0)"
    )

    # Power Disaggregation Regressors
    print("\nEvaluating Task 2: Power Disaggregation Regressors...")
    # 1. Random Forest Regressor
    rf_reg = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_reg.fit(X_train, p_train)
    p_pred_rf = rf_reg.predict(X_test)

    # 2. Mean Active Power Baseline (Mean active power when state is predicted ON)
    mean_active_val = float(p_train[y_train == 1].mean()) if (y_train == 1).sum() > 0 else 0.0
    p_pred_mean = np.where(rf_pred == 1, mean_active_val, 0.0)

    # 3. Zero Baseline
    p_pred_zero = np.zeros_like(p_test)

    def eval_reg(p_true, p_pred, model_name: str, desc: str) -> Dict[str, Any]:
        mae = float(mean_absolute_error(p_true, p_pred))
        rmse = float(np.sqrt(mean_squared_error(p_true, p_pred)))
        total_energy_true = float(np.sum(p_true)) * (6.0 / 3600.0)  # Wh for 6s intervals
        total_energy_pred = float(np.sum(p_pred)) * (6.0 / 3600.0)
        rete = float(abs(total_energy_pred - total_energy_true) / max(total_energy_true, 1e-6))
        return {
            "model": model_name,
            "description": desc,
            "mae_w": round(mae, 2),
            "rmse_w": round(rmse, 2),
            "total_energy_true_wh": round(total_energy_true, 2),
            "total_energy_pred_wh": round(total_energy_pred, 2),
            "rete_error_pct": round(rete * 100.0, 2),
        }

    results["regression_baselines"]["random_forest_regressor"] = eval_reg(
        p_test, p_pred_rf, "Random Forest Regressor", "Continuous Watts regression from aggregate features"
    )
    results["regression_baselines"]["mean_active_baseline"] = eval_reg(
        p_test, p_pred_mean, "Mean Active Power Baseline", f"Assigns mean active power ({mean_active_val:.1f} W) when RF predicts ON"
    )
    results["regression_baselines"]["zero_baseline"] = eval_reg(
        p_test, p_pred_zero, "Zero Baseline", "Trivial baseline assigning 0 W to all test samples"
    )

    # Print summary tables
    print("\n" + "=" * 115)
    print("=== iAWE REAL-DATA NILM BENCHMARK RESULTS (Task 1: Water Motor ON/OFF Classification) ===")
    print("=" * 115)
    print(f"{'Model':<30} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<7} | {'F1-Score':<8} | Confusion (TP, FP, FN, TN)")
    print("-" * 115)
    for k, v in results["classification_baselines"].items():
        cm = v["confusion_matrix"]
        cm_str = f"TP={cm['true_positive']}, FP={cm['false_positive']}, FN={cm['false_negative']}, TN={cm['true_negative']}"
        print(f"{v['model']:<30} | {v['accuracy']:<8.4f} | {v['precision']:<9.4f} | {v['recall']:<7.4f} | {v['f1_score']:<8.4f} | {cm_str}")

    print("\n" + "=" * 100)
    print("=== iAWE REAL-DATA POWER DISAGGREGATION RESULTS (Task 2: Continuous Power in Watts) ===")
    print("=" * 100)
    print(f"{'Model':<35} | {'MAE (W)':<8} | {'RMSE (W)':<9} | {'True kWh':<9} | {'Pred kWh':<9} | {'RETE Error %':<12}")
    print("-" * 100)
    for k, v in results["regression_baselines"].items():
        true_kwh = v["total_energy_true_wh"] / 1000.0
        pred_kwh = v["total_energy_pred_wh"] / 1000.0
        print(f"{v['model']:<35} | {v['mae_w']:<8.2f} | {v['rmse_w']:<9.2f} | {true_kwh:<9.3f} | {pred_kwh:<9.3f} | {v['rete_error_pct']:<12.2f}%")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nMachine-readable benchmark results saved to: {RESULTS_FILE}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run iAWE Real-Data NILM Benchmark")
    parser.add_argument("--h5-file", default=H5_PATH, help="Path to iawe.h5")
    parser.add_argument("--on-threshold", type=float, default=200.0, help="ON power threshold in Watts")
    parser.add_argument("--resample", default="6s", help="Resample frequency")
    args = parser.parse_args()

    df, meta = load_iawe_dataset(args.h5_file, on_threshold_w=args.on_threshold, resample_freq=args.resample)
    run_iawe_benchmark(df, meta)
