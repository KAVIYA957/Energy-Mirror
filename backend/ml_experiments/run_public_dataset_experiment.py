"""
run_public_dataset_experiment.py - Public NILM Dataset Experiment Pipeline

Supports empirical evaluation on real residential electricity datasets:
  - REFIT (House 21: Appliance 9 Pond Pump single-phase induction motor; Houses 11 & 12 rejected as invalid)
  - UK-DALE (House 1: Solar Thermal Pump / Boiler circulation pump)

Evaluation Protocols:
  1. Time-held-out chronological evaluation (60% Train, 20% Val, 20% Test) with boundary buffer dropped.
  2. Unseen-building / Cross-residence generalization (Train on House A, Test on House B).
  3. Four standardized baselines: Simple Threshold, Differential Step, Persistence (t-1), Majority Class.
  4. Full separation of Task 1 (State Detection) and Task 2 (Power Disaggregation).
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
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

# Authoritative REFIT appliance mappings from official CLEAN_READ_ME_081116.txt
REFIT_APPLIANCE_CATALOG = {
    "House1": {"Appliance9": "Electric Heater (GLEN 2172)"},
    "House2": {"Appliance9": "Overhead Fan"},
    "House11": {
        "Appliance1": "Fridge",
        "Appliance2": "Fridge-Freezer",
        "Appliance3": "Washing Machine",
        "Appliance4": "Dishwasher",
        "Appliance5": "Computer Site",
        "Appliance6": "Microwave",
        "Appliance7": "Kettle",
        "Appliance8": "Router",
        "Appliance9": "Hi-Fi",
    },
    "House12": {
        "Appliance1": "Fridge-Freezer",
        "Appliance4": "Computer Site",
        "Appliance5": "Microwave",
        "Appliance6": "Kettle",
        "Appliance7": "Toaster (Nothing Recorded)",
        "Appliance8": "Television (Nothing Recorded)",
        "Appliance9": "Unknown (Nothing Recorded)",
    },
    "House21": {
        "Appliance1": "Fridge-Freezer",
        "Appliance2": "Tumble Dryer",
        "Appliance3": "Washing Machine",
        "Appliance4": "Dishwasher",
        "Appliance5": "Food Mixer",
        "Appliance6": "Television",
        "Appliance7": "Kettle",
        "Appliance8": "Vivarium",
        "Appliance9": "Pond Pump",
    },
}

def validate_refit_target(house_id: str, target_category: str) -> Tuple[bool, str, str]:
    """
    Validates whether the requested target appliance is genuinely instrumented
    in the specified REFIT house according to authoritative metadata.
    Returns: (is_valid, matched_column_name, appliance_description)
    """
    house_meta = REFIT_APPLIANCE_CATALOG.get(house_id, {})
    if not house_meta:
        return False, "", f"Unknown house identifier: {house_id}"

    target_lower = target_category.lower()
    for col, desc in house_meta.items():
        desc_lower = desc.lower()
        if "pump" in target_lower and "pump" in desc_lower:
            return True, col, desc
        if "fan" in target_lower and "fan" in desc_lower:
            return True, col, desc
        if "heater" in target_lower and "heater" in desc_lower:
            return True, col, desc

    return False, "", f"Target '{target_category}' NOT PRESENT in {house_id}."

def load_refit_house(
    csv_path: str,
    target_appliance_col: Optional[str] = None,
    target_category: str = "water_pump",
    max_rows: Optional[int] = 100000,
) -> Tuple[pd.DataFrame, str]:
    """
    Loads and normalizes a REFIT house CSV file with strict ground-truth verification.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"REFIT file not found at: {csv_path}")

    filename = os.path.basename(csv_path)
    # Extract house id (e.g. CLEAN_House11.csv -> House11)
    house_id = "House11"
    for h in ["House1", "House2", "House11", "House12", "House21"]:
        if h in filename:
            house_id = h
            break

    # Validate ground truth against official schema
    is_valid, col, desc = validate_refit_target(house_id, target_category)
    if not is_valid:
        raise ValueError(
            f"GROUND-TRUTH MISMATCH ERROR: {desc} "
            f"REFIT {house_id} does NOT contain a '{target_category}'. "
            f"In {house_id}: Appliance8 is '{REFIT_APPLIANCE_CATALOG.get(house_id, {}).get('Appliance8')}', "
            f"and Appliance9 is '{REFIT_APPLIANCE_CATALOG.get(house_id, {}).get('Appliance9')}'. "
            f"The genuine Pond Pump in REFIT is located strictly in House21 (Appliance9)."
        )

    chosen_col = target_appliance_col or col
    print(f"[Ground-Truth Verified] {house_id}: '{chosen_col}' mapped to '{desc}'.")

    df = pd.read_csv(csv_path, nrows=max_rows)
    df["timestamp"] = pd.to_datetime(df["Time"])
    
    result = pd.DataFrame({
        "timestamp": df["timestamp"],
        "aggregate_power_w": df["Aggregate"].astype(float),
        "target_power_w": df[chosen_col].astype(float),
    })
    return result, desc

def load_ukdale_house(
    mains_path: str,
    submeter_path: str,
    max_rows: Optional[int] = 100000,
) -> pd.DataFrame:
    """
    Loads and temporally aligns UK-DALE 1Hz mains and 6s submeter files.
    mains.dat schema: timestamp (unix), active_power, apparent_power, voltage
    channel_X.dat schema: timestamp (unix), active_power
    """
    if not os.path.exists(mains_path):
        raise FileNotFoundError(f"UK-DALE mains file not found: {mains_path}")
    if not os.path.exists(submeter_path):
        raise FileNotFoundError(f"UK-DALE submeter file not found: {submeter_path}")

    # Read mains
    df_mains = pd.read_csv(
        mains_path,
        sep=r"\s+",
        header=None,
        names=["unix", "active_p", "apparent_p", "voltage"],
        nrows=max_rows,
    )
    df_mains["timestamp"] = pd.to_datetime(df_mains["unix"], unit="s")

    # Read submeter
    df_sub = pd.read_csv(
        submeter_path,
        sep=r"\s+",
        header=None,
        names=["unix", "target_p"],
        nrows=max_rows,
    )
    df_sub["timestamp"] = pd.to_datetime(df_sub["unix"], unit="s")

    # Merge on nearest timestamp within 3 seconds
    merged = pd.merge_asof(
        df_mains.sort_values("timestamp"),
        df_sub.sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(seconds=3),
    ).dropna()

    # Calculate power factor: PF = P / S
    apparent = np.maximum(merged["apparent_p"].values, 1.0)
    pf = np.clip(merged["active_p"].values / apparent, 0.50, 1.00)

    return pd.DataFrame({
        "timestamp": merged["timestamp"],
        "aggregate_power_w": merged["active_p"].values,
        "power_factor": pf,
        "target_power_w": merged["target_p"].values,
    })

def run_public_dataset_experiment(
    train_file: str,
    test_file: Optional[str] = None,
    dataset_type: str = "refit",
    target_appliance: str = "water_pump",
    nominal_power_w: float = 75.0,
    threshold_w: float = 40.0,
    step_threshold_w: float = 30.0,
    output_dir: str = "backend/ml_experiments/results",
) -> Dict[str, Any]:
    """
    Executes a real public dataset experiment using either:
      1. Single-file chronological split (Train/Val/Test).
      2. Cross-building evaluation (Train on train_file, Test on test_file).
    """
    print("=" * 90)
    print("ENERGY MIRROR: REAL PUBLIC DATASET NILM EXPERIMENT")
    print(f"Target Appliance: {target_appliance.upper()} | Dataset: {dataset_type.upper()}")
    print("=" * 90)

    # 1. Load Training Data
    if not os.path.exists(train_file):
        print(f"\n[Status] Dataset file not found locally: {train_file}")
        print("[Status] Awaiting user approval to download real public dataset.")
        return {
            "status": "AWAITING_USER_DOWNLOAD_APPROVAL",
            "required_file": train_file,
            "dataset_type": dataset_type,
            "target_appliance": target_appliance,
        }

    print(f"[Data] Loading real training data from: {train_file}")
    if dataset_type == "refit":
        df_train, train_desc = load_refit_house(train_file, target_category=target_appliance)
    else:
        df_train = pd.read_csv(train_file)
        train_desc = "Custom CSV"

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

    # Preprocess Train
    chunks_train = preprocessor.detect_contiguous_chunks(df_train, time_col="timestamp")
    active_chunk = chunks_train[0]
    p_agg_train = active_chunk["aggregate_power_w"].values
    pf_agg_train = active_chunk["power_factor"].values if "power_factor" in active_chunk else None
    target_p_train = active_chunk["target_power_w"].values
    target_c_train = preprocessor.binarize_labels(target_p_train)

    X_train_full, feat_names = preprocessor.extract_window_features(p_agg_train, pf_agg=pf_agg_train)
    W = config.window_size_samples
    y_c_train = target_c_train[W - 1:len(X_train_full) + W - 1]
    y_p_train = target_p_train[W - 1:len(X_train_full) + W - 1]

    # Handle evaluation mode
    if test_file and os.path.exists(test_file):
        print(f"\n[Evaluation Mode] UNSEEN-BUILDING CROSS-RESIDENCE EVALUATION")
        print(f"[Train Residence] {train_file} ({train_desc})")
        print(f"[Test Residence]  {test_file}")
        
        df_test, test_desc = load_refit_house(test_file, target_category=target_appliance)
        chunks_test = preprocessor.detect_contiguous_chunks(df_test, time_col="timestamp")
        active_test_chunk = chunks_test[0]
        p_agg_test = active_test_chunk["aggregate_power_w"].values
        pf_agg_test = active_test_chunk["power_factor"].values if "power_factor" in active_test_chunk else None
        target_p_test = active_test_chunk["target_power_w"].values
        target_c_test = preprocessor.binarize_labels(target_p_test)

        X_train = X_train_full
        y_train_c = y_c_train
        y_train_p = y_p_train

        X_test, _ = preprocessor.extract_window_features(p_agg_test, pf_agg=pf_agg_test)
        y_test_c = target_c_test[W - 1:len(X_test) + W - 1]
        y_test_p = target_p_test[W - 1:len(X_test) + W - 1]
        p_curr_test = p_agg_test[W - 1:len(X_test) + W - 1]
        split_desc = "UNSEEN_BUILDING_CROSS_RESIDENCE"
    else:
        print(f"\n[Evaluation Mode] TIME-HELD-OUT CHRONOLOGICAL SPLIT (WITH BOUNDARY BUFFER DROPPED)")
        splits = preprocessor.chronological_split(X_train_full, y_c_train, y_p_train)
        X_train, y_train_c, y_train_p = splits["X_train"], splits["y_train_class"], splits["y_train_power"]
        X_test, y_test_c, y_test_p = splits["X_test"], splits["y_test_class"], splits["y_test_power"]
        
        test_start_idx = splits["split_indices"]["test"][0]
        p_curr = p_agg_train[W - 1:len(X_train_full) + W - 1]
        p_curr_test = p_curr[test_start_idx:test_start_idx + len(y_test_c)]
        split_desc = "TIME_HELD_OUT_CHRONOLOGICAL"

    # Train Random Forest Models
    print(f"\n[Training] Training Random Forest Classifier on {len(X_train):,} real data samples...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_split=4, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train_c)

    print(f"[Training] Training Random Forest Regressor on {len(X_train):,} real data samples...")
    reg = RandomForestRegressor(n_estimators=100, max_depth=8, min_samples_split=4, random_state=42, n_jobs=-1)
    reg.fit(X_train, y_train_p)

    # Predict
    y_pred_c = clf.predict(X_test)
    y_pred_p = reg.predict(X_test)

    ml_class_metrics = compute_classification_metrics(y_test_c, y_pred_c)
    ml_power_metrics = compute_power_metrics(y_test_p, y_pred_p)

    baseline_metrics = evaluate_baseline_models(
        X_test_p_curr=p_curr_test,
        y_test_class=y_test_c,
        y_test_power=y_test_p,
        nominal_on_power_w=nominal_power_w,
        threshold_w=threshold_w,
        step_threshold_w=step_threshold_w,
    )

    model_summary = {
        "classification": ml_class_metrics,
        "power_estimation": ml_power_metrics,
    }
    print_evaluation_summary(target_appliance, model_summary, baseline_metrics)

    # Save artifact
    os.makedirs(output_dir, exist_ok=True)
    results_payload = {
        "timestamp_utc": datetime.utcnow().isoformat(),
        "target_appliance": target_appliance,
        "nominal_power_w": nominal_power_w,
        "data_provenance": {
            "source_type": "REAL_PUBLIC_DATASET",
            "dataset_name": dataset_type,
            "train_source": train_file,
            "test_source": test_file or train_file,
            "evaluation_mode": split_desc,
            "is_physical_measurement": False,
            "is_real_public_dataset": True,
        },
        "ml_candidate_results": model_summary,
        "baseline_results": baseline_metrics,
        "verification_status": "REAL_PUBLIC_DATASET_EVALUATION_COMPLETED",
    }
    out_path = os.path.join(output_dir, f"real_dataset_results_{target_appliance}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    print(f"[Artifacts] Results saved to: {out_path}")
    return results_payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real Public Dataset NILM Experiment")
    parser.add_argument("--train-file", type=str, default="backend/ml_experiments/data/CLEAN_House21.csv", help="Primary training house CSV")
    parser.add_argument("--test-file", type=str, default=None, help="Optional unseen test house CSV for cross-building evaluation")
    parser.add_argument("--dataset", type=str, default="refit", choices=["refit", "ukdale"])
    parser.add_argument("--appliance", type=str, default="water_pump", choices=["water_pump", "ceiling_fan", "water_heater"])
    args = parser.parse_args()

    run_public_dataset_experiment(
        train_file=args.train_file,
        test_file=args.test_file,
        dataset_type=args.dataset,
        target_appliance=args.appliance,
    )
