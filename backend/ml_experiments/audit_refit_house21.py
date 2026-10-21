"""
audit_refit_house21.py - Data-Quality and Ground-Truth Audit for REFIT House 21

Audits CLEAN_House21.csv:
- Total rows and date range
- Sampling intervals and irregularity
- Duplicate timestamps
- Missing/null values
- Negative/invalid power values
- Issues column breakdown
- Appliance 9 (Pond Pump) power distribution, active threshold, duty cycle
- Overlapping appliance activity
- Missing ground-truth intervals and validity mask definition
"""

import os
import json
import numpy as np
import pandas as pd

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "CLEAN_House21.csv"))

def run_audit():
    print(f"Loading {DATA_PATH} for complete audit...")
    # Load required columns to inspect memory efficiently
    cols = ['Time', 'Unix', 'Aggregate', 'Appliance9', 'Issues']
    df = pd.read_csv(DATA_PATH)
    
    total_rows = len(df)
    print(f"Total rows: {total_rows:,}")
    print(f"Columns: {df.columns.tolist()}")

    # 1. Timestamps and Date Range
    start_time = df['Time'].iloc[0]
    end_time = df['Time'].iloc[-1]
    start_unix = int(df['Unix'].iloc[0])
    end_unix = int(df['Unix'].iloc[-1])
    duration_days = (end_unix - start_unix) / 86400.0

    print(f"Start: {start_time} (Unix {start_unix})")
    print(f"End:   {end_time} (Unix {end_unix})")
    print(f"Total span: {duration_days:.2f} days (~{duration_days/30.4375:.1f} months)")

    # 2. Duplicate timestamps
    dup_unix = df['Unix'].duplicated().sum()
    print(f"Duplicate Unix timestamps: {dup_unix:,} ({dup_unix / total_rows * 100:.3f}%)")

    # 3. Sampling Cadence (Unix diffs)
    unix_diffs = np.diff(df['Unix'].values)
    median_interval = float(np.median(unix_diffs))
    mean_interval = float(np.mean(unix_diffs))
    p10_interval = float(np.percentile(unix_diffs, 10))
    p90_interval = float(np.percentile(unix_diffs, 90))
    p99_interval = float(np.percentile(unix_diffs, 99))
    max_interval = int(np.max(unix_diffs))
    min_interval = int(np.min(unix_diffs))
    
    print(f"Sampling cadence: median={median_interval:.1f}s, mean={mean_interval:.2f}s, p10={p10_interval:.1f}s, p90={p90_interval:.1f}s, p99={p99_interval:.1f}s, min={min_interval}s, max={max_interval}s")

    # 4. Missing / NaN values
    null_counts = df.isnull().sum().to_dict()
    print("Null value counts per column:")
    for col, cnt in null_counts.items():
        if cnt > 0:
            print(f"  {col}: {cnt}")
    if sum(null_counts.values()) == 0:
        print("  Zero null values found across all columns.")

    # 5. Negative values
    neg_agg = (df['Aggregate'] < 0).sum()
    neg_app9 = (df['Appliance9'] < 0).sum()
    print(f"Negative Aggregate values: {neg_agg}")
    print(f"Negative Appliance9 values: {neg_app9}")

    # 6. Issues column distribution
    issue_counts = df['Issues'].value_counts().to_dict()
    print(f"Issues column breakdown: {issue_counts}")

    # 7. Appliance 9 (Pond Pump) Power Distribution
    p_pump = df['Appliance9'].values
    p_agg = df['Aggregate'].values
    
    # Active power stats
    # Check non-zero distribution
    non_zero_pump = p_pump[p_pump > 0]
    print(f"\nAppliance 9 Non-zero count: {len(non_zero_pump):,} / {total_rows:,} ({len(non_zero_pump)/total_rows*100:.2f}%)")
    if len(non_zero_pump) > 0:
        print(f"  Min: {np.min(non_zero_pump)} W")
        print(f"  P5:  {np.percentile(non_zero_pump, 5):.1f} W")
        print(f"  P25: {np.percentile(non_zero_pump, 25):.1f} W")
        print(f"  P50 (Median active): {np.percentile(non_zero_pump, 50):.1f} W")
        print(f"  Mean active: {np.mean(non_zero_pump):.2f} W")
        print(f"  P75: {np.percentile(non_zero_pump, 75):.1f} W")
        print(f"  P95: {np.percentile(non_zero_pump, 95):.1f} W")
        print(f"  Max: {np.max(non_zero_pump)} W")

    # Operational Power Analysis
    # Let's inspect power histogram bins for Appliance 9
    bins = [0, 5, 20, 50, 70, 80, 90, 100, 150, 500, 5000]
    binned = pd.cut(df['Appliance9'], bins=bins, include_lowest=True).value_counts().sort_index()
    print("\nAppliance 9 Power Bins:")
    for interval, count in binned.items():
        print(f"  {str(interval):<16}: {count:,} ({count/total_rows*100:.2f}%)")

    # Aggregate Power Distribution
    print(f"\nAggregate Power Summary:")
    print(f"  Min: {np.min(p_agg)} W, Mean: {np.mean(p_agg):.1f} W, Median: {np.median(p_agg):.1f} W, Max: {np.max(p_agg)} W")

    # Submeter vs Aggregate consistency (Appliance 9 <= Aggregate + margin)
    pump_exceeds_agg = (p_pump > p_agg + 5).sum()
    print(f"Appliance 9 exceeds Aggregate (+5W): {pump_exceeds_agg:,} ({pump_exceeds_agg/total_rows*100:.3f}%)")

    # Concurrent appliances operating
    submeter_cols = [c for c in df.columns if c.startswith('Appliance') and c != 'Appliance9']
    other_submeters = df[submeter_cols].values
    other_active = (other_submeters > 20).sum(axis=1) # number of other appliances ON > 20W
    pump_active = (p_pump >= 20)
    
    concurrent_counts = pd.Series(other_active[pump_active]).value_counts().sort_index().to_dict()
    print(f"\nConcurrent other submetered appliances active (>20W) during Pump active periods:")
    for n_active, cnt in concurrent_counts.items():
        print(f"  {n_active} other appliances active: {cnt:,} samples ({cnt/max(1, pump_active.sum())*100:.2f}%)")

    # Audit Validity Mask Definition
    # Valid ground truth:
    # 1. Non-null Aggregate and Appliance9
    # 2. Non-negative Aggregate and Appliance9
    # 3. Issues == 0 (no missing sensor / logging glitch reported in Issues column)
    # 4. Sampling gap < 120 seconds (gaps > 2 minutes indicate power outage or data dropout)
    gap_over_120s = np.zeros(total_rows, dtype=bool)
    gap_over_120s[1:] = (unix_diffs > 120)
    
    valid_mask = (
        (df['Aggregate'].notnull()) &
        (df['Appliance9'].notnull()) &
        (df['Aggregate'] >= 0) &
        (df['Appliance9'] >= 0) &
        (df['Issues'] == 0) &
        (~gap_over_120s)
    )
    
    valid_count = int(valid_mask.sum())
    excluded_count = total_rows - valid_count
    print(f"\nValidity Mask Summary:")
    print(f"  Valid samples:    {valid_count:,} ({valid_count/total_rows*100:.2f}%)")
    print(f"  Excluded samples: {excluded_count:,} ({excluded_count/total_rows*100:.2f}%)")
    print(f"    - Issues != 0: {(df['Issues'] != 0).sum():,}")
    print(f"    - Sampling gaps > 120s: {gap_over_120s.sum():,}")

    audit_summary = {
        "total_rows": total_rows,
        "date_start": str(start_time),
        "date_end": str(end_time),
        "duration_days": round(duration_days, 2),
        "median_cadence_s": median_interval,
        "mean_cadence_s": round(mean_interval, 2),
        "duplicates_count": int(dup_unix),
        "negative_aggregate": int(neg_agg),
        "negative_appliance9": int(neg_app9),
        "appliance9_median_active_w": float(np.percentile(non_zero_pump, 50)) if len(non_zero_pump) > 0 else 0.0,
        "appliance9_mean_active_w": float(np.mean(non_zero_pump)) if len(non_zero_pump) > 0 else 0.0,
        "valid_samples": valid_count,
        "excluded_samples": excluded_count,
    }
    
    out_json = os.path.join(os.path.dirname(__file__), "results", "refit_audit_summary.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(audit_summary, f, indent=2)
    print(f"\nAudit summary saved to {out_json}")

if __name__ == "__main__":
    run_audit()
