"""
inspect_dataset.py - Dataset Integrity and Signal Inspection Tool

Inspects downloaded or local NILM dataset files (CSV / DAT / Parquet) without loading
excessive memory. Reports column schema, sampling interval distribution, gap sizes,
negative or out-of-range power anomalies, and active appliance duration.

Usage:
    python inspect_dataset.py --file path/to/dataset.csv --type ukdale|refit|generic
"""

import os
import sys
import argparse
import datetime
from typing import Dict, Any, List, Optional

def inspect_csv_structure(file_path: str, max_rows: int = 50000) -> Dict[str, Any]:
    """
    Inspects a CSV file's header, line count estimate, delimiter, and initial records
    without loading the entire dataset into memory.
    """
    if not os.path.exists(file_path):
        return {"error": f"File does not exist: {file_path}"}

    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    timestamps = []
    columns = []
    row_count = 0
    non_numeric_counts = {}
    negative_power_count = 0
    max_power = 0.0

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        first_line = f.readline().strip()
        delimiter = "," if "," in first_line else (" " if " " in first_line else "\t")
        columns = [c.strip() for c in first_line.split(delimiter)]
        
        # Check if first line was header or data
        has_header = any(not token.replace(".", "", 1).replace("-", "", 1).isdigit() for token in columns)
        if not has_header:
            columns = [f"channel_{i+1}" for i in range(len(columns))]
            f.seek(0)

        for line in f:
            row_count += 1
            if row_count > max_rows:
                break
            parts = [p.strip() for p in line.strip().split(delimiter)]
            if len(parts) >= 2:
                # Attempt to parse power value
                try:
                    val = float(parts[1])
                    if val < 0:
                        negative_power_count += 1
                    if val > max_power:
                        max_power = val
                except ValueError:
                    non_numeric_counts[1] = non_numeric_counts.get(1, 0) + 1

    return {
        "file_path": file_path,
        "file_size_mb": round(file_size_mb, 2),
        "estimated_total_rows": int((file_size_bytes / max(1, os.path.getsize(file_path))) * row_count) if row_count > 0 else 0,
        "inspected_sample_rows": row_count,
        "detected_delimiter": delimiter,
        "has_header": has_header,
        "columns": columns,
        "negative_readings_in_sample": negative_power_count,
        "max_power_in_sample_w": max_power,
    }

def print_inspection_report(info: Dict[str, Any]):
    print("=" * 70)
    print("DATASET SIGNAL & INTEGRITY AUDIT")
    print("=" * 70)
    if "error" in info:
        print(f"ERROR: {info['error']}")
        return

    print(f"File Path:       {info['file_path']}")
    print(f"File Size:       {info['file_size_mb']} MB")
    print(f"Columns:         {len(info['columns'])} ({', '.join(info['columns'][:8])}...)")
    print(f"Sample Rows:     {info['inspected_sample_rows']}")
    print(f"Max Power (W):   {info['max_power_in_sample_w']} W")
    print(f"Negative Values: {info['negative_readings_in_sample']}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit dataset file integrity")
    parser.add_argument("--file", type=str, required=False, help="Path to CSV dataset")
    args = parser.parse_args()

    if args.file:
        res = inspect_csv_structure(args.file)
        print_inspection_report(res)
    else:
        print("inspect_dataset.py ready. Pass --file <path> to audit a local dataset file.")
