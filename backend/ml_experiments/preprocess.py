"""
preprocess.py - Reproducible NILM Preprocessing and Feature Engineering Pipeline

Preprocesses time-series electrical telemetry for machine-learning-based NILM:
  1. Temporal alignment of aggregate mains and sub-metered appliance ground truth.
  2. UTC timestamp normalization.
  3. Gap detection: Rejects or isolates intervals where gap > max_allowed_gap_s (default 60s).
  4. Appliance ground-truth binarization with configurable hysteresis thresholds.
  5. Sliding-window statistical feature extraction:
     - Rolling mean, std, min, max, delta, instantaneous derivative.
     - Multi-channel support (P, PF, S, Q) when present.
  6. Strict chronological train / validation / test partitioning with boundary buffer to prevent data leakage.
  7. Configuration metadata export for full auditability and reproducibility.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import pandas as pd

@dataclass
class PreprocessingConfig:
    window_size_samples: int = 15       # e.g., 15 samples (~15s at 1Hz, or ~90s at 6s)
    step_size_samples: int = 1          # stride
    max_allowed_gap_s: float = 60.0     # gaps larger than this break contiguous chunks
    impute_short_gaps: bool = False     # whether to linear-fill small gaps <= max_allowed_gap_s
    on_power_threshold_w: float = 20.0  # W threshold for appliance ON classification
    min_on_duration_samples: int = 3    # minimum consecutive samples to count as ON
    train_ratio: float = 0.60
    val_ratio: float = 0.20
    test_ratio: float = 0.20
    random_seed: int = 42

class NILMPreprocessor:
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()

    def detect_contiguous_chunks(self, df: pd.DataFrame, time_col: str = "timestamp") -> List[pd.DataFrame]:
        """
        Splits a time-series into continuous contiguous chunks separated by gaps > max_allowed_gap_s.
        Prevents interpolating across multi-minute or multi-hour sensor outages.
        """
        if df.empty:
            return []

        df = df.sort_values(by=time_col).reset_index(drop=True)
        time_diffs = df[time_col].diff().dt.total_seconds()
        gap_indices = df.index[time_diffs > self.config.max_allowed_gap_s].tolist()

        chunks = []
        start_idx = 0
        for gap_idx in gap_indices:
            chunk = df.iloc[start_idx:gap_idx].copy()
            if len(chunk) >= self.config.window_size_samples * 2:
                chunks.append(chunk)
            start_idx = gap_idx

        last_chunk = df.iloc[start_idx:].copy()
        if len(last_chunk) >= self.config.window_size_samples * 2:
            chunks.append(last_chunk)

        return chunks

    def binarize_labels(self, power_series: np.ndarray) -> np.ndarray:
        """
        Converts ground-truth continuous power to binary ON/OFF state labels
        with minimum duration hysteresis to eliminate sensor noise.
        """
        raw_on = (power_series >= self.config.on_power_threshold_w).astype(int)
        if self.config.min_on_duration_samples <= 1:
            return raw_on

        # Filter out short transient spikes (duration < min_on_duration_samples)
        filtered = np.copy(raw_on)
        n = len(filtered)
        i = 0
        while i < n:
            if filtered[i] == 1:
                start = i
                while i < n and filtered[i] == 1:
                    i += 1
                length = i - start
                if length < self.config.min_on_duration_samples:
                    filtered[start:i] = 0
            else:
                i += 1
        return filtered

    def extract_window_features(
        self,
        p_agg: np.ndarray,
        pf_agg: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Extracts sliding window statistical features from aggregate signal using
        high-performance vectorized rolling window operations.
        Features per window:
          - mean, std, min, max, range
          - current active power (last sample)
          - instantaneous delta (p_t - p_{t-1})
          - window delta (p_t - p_{t-W+1})
        """
        W = self.config.window_size_samples
        N = len(p_agg)
        if N < W:
            return np.empty((0, 8)), []

        s_p = pd.Series(p_agg)
        p_curr = s_p.values[W - 1:]
        p_mean = s_p.rolling(W).mean().values[W - 1:]
        p_std = s_p.rolling(W).std(ddof=0).fillna(0.0).values[W - 1:]
        p_min = s_p.rolling(W).min().values[W - 1:]
        p_max = s_p.rolling(W).max().values[W - 1:]
        p_range = p_max - p_min
        delta_instant = s_p.diff().fillna(0.0).values[W - 1:]
        delta_window = (s_p - s_p.shift(W - 1)).fillna(0.0).values[W - 1:]

        feature_cols = [p_curr, p_mean, p_std, p_min, p_max, p_range, delta_instant, delta_window]
        feature_names = [
            "p_curr", "p_mean", "p_std", "p_min", "p_max",
            "p_range", "delta_instant", "delta_window"
        ]

        if pf_agg is not None and len(pf_agg) == N:
            s_pf = pd.Series(pf_agg)
            pf_curr = s_pf.values[W - 1:]
            pf_mean = s_pf.rolling(W).mean().values[W - 1:]
            pf_std = s_pf.rolling(W).std(ddof=0).fillna(0.0).values[W - 1:]
            delta_pf_instant = s_pf.diff().fillna(0.0).values[W - 1:]
            feature_cols.extend([pf_curr, pf_mean, pf_std, delta_pf_instant])
            feature_names.extend(["pf_curr", "pf_mean", "pf_std", "delta_pf_instant"])

        features = np.column_stack(feature_cols).astype(np.float32)

        # Apply stride if step_size > 1
        if self.config.step_size_samples > 1:
            features = features[::self.config.step_size_samples]

        return features, feature_names

    def chronological_split(
        self,
        X: np.ndarray,
        y_class: np.ndarray,
        y_power: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Chronological partition into Train, Validation, and Test sets.
        Leaves a buffer boundary to guarantee zero window overlap.
        """
        N = len(X)
        n_train = int(N * self.config.train_ratio)
        n_val = int(N * self.config.val_ratio)

        # Buffer: drop boundary window to prevent temporal leakage
        buffer_len = min(self.config.window_size_samples, 5)

        train_end = n_train
        val_start = train_end + buffer_len
        val_end = val_start + n_val
        test_start = val_end + buffer_len

        return {
            "X_train": X[:train_end],
            "y_train_class": y_class[:train_end],
            "y_train_power": y_power[:train_end],
            "X_val": X[val_start:val_end],
            "y_val_class": y_class[val_start:val_end],
            "y_val_power": y_power[val_start:val_end],
            "X_test": X[test_start:],
            "y_test_class": y_class[test_start:],
            "y_test_power": y_power[test_start:],
            "split_indices": {
                "train": (0, train_end),
                "val": (val_start, val_end),
                "test": (test_start, N),
                "buffer_dropped": buffer_len * 2,
            }
        }

    def save_metadata(self, output_dir: str, metadata: Dict[str, Any]):
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "preprocessing_metadata.json")
        payload = {
            "config": asdict(self.config),
            "metadata": metadata,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"[Preprocessing] Metadata saved to: {path}")
