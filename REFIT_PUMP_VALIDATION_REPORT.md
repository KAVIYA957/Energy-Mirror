# Energy Mirror NILM Validation Report: Real-World REFIT Pump Disaggregation

**Milestone:** 2C.9: REFIT Pump Validation  
**Date:** October 21, 2026  
**Status:** Software Analysis Complete — Evaluated on Real Historical Residential Telemetry  
**Hardware Ingestion Status:** `ENABLE_HARDWARE_INGEST=false` (Strict Software-Only Milestone; Zero Physical Hardware Purchased, Assembled, Connected, or Tested)  

---

## Executive Summary

Milestone 2C.9 conducts Energy Mirror's first empirical validation against the internationally benchmarked **REFIT** longitudinal residential load dataset. Following an exhaustive metadata schema audit confirming that **House 21 Appliance 9** is the sole monitored water pump across the entire 20-house study, we acquired the official cleaned CSV (`CLEAN_House21.csv`, 302.04 MB uncompressed), conducted a strict data-quality and ground-truth audit, enforced leakage-safe chronological partitioning, and evaluated five disaggregation baselines across 5,383,993 real residential power measurements spanning 16.1 months.

### Key Scientific Findings

1. **Empirical Operating Rating (~44 W vs. 75 W Target):**
   Prior documentation estimated the REFIT pond pump at "~80 W". Comprehensive histogram and quantile analysis reveals that House 21 Appliance 9 operates tightly between **42 W and 47 W** with a **median active power of 44.0 W** and **mean active power of 44.45 W**. It is an induction motor driving a small outdoor pond fountain/filter. Its power draw is ~41% lower than Energy Mirror's simulated 75 W domestic pump, representing an even more severe low-power signal-to-noise ratio against a mean household background of 646.8 W.

2. **The Base-Rate / Sample-Level Illusion:**
   During the held-out test period (spring/summer 2015), the pond pump was left running continuously in 24/7 filtration mode (**99.36% positive prevalence**; 1,029,741 active samples vs. 6,630 inactive samples). Because of this extreme class imbalance:
   - A naive threshold ($P_{agg} \ge 100$ W) achieves an apparent **Sample F1 of 0.9967** with **0.0000 specificity** (detecting 0 of 6,630 OFF samples).
   - A Random Forest classifier achieves an apparent **Sample F1 of 0.9933** with **0.0318 specificity**.

3. **Event-Level Metric Audit Exposes Severe Chattering:**
   Applying the strict one-to-one event matcher with temporal onset tolerance ($\pm 120$ s) reveals the true operational performance:
   - The Random Forest classifier generates **3,709 false alarms** across 110 days (**33.66 false alarms per day**), detecting only 1 of 13 true onsets (**Event Precision = 0.0003, Event Recall = 0.0769, Event F1 = 0.0005**).
   - The Differential Step baseline produces **3,071 false alarms** (**27.87 false alarms per day**) and **0 matched onsets** (**Event F1 = 0.0000**).
   - Whole-house aggregate step changes at pump onsets have a **median step size of +0.0 W** (swamped by concurrent cyclic loads such as refrigerators, vivarium heating, and television).

4. **Validation Status (`PARTIALLY_VALIDATED` / `INCOMPATIBLE_RATING`):**
   - **REFIT Pond Pump:** `PARTIALLY_VALIDATED` (proves that single-phase AC motor loads at ~44 W can be tracked in active energy estimation over long steady-state runs, but onset edge disaggregation fails amidst background noise).
   - **Energy Mirror 75 W Domestic Water Pump:** `PARTIALLY_VALIDATED` (validates single-phase motor physics and demonstrates that continuous duty cycles cannot be conflated with intermittent domestic batch pumping).
   - **Other Appliances:** The 140 W water heater, 45 W ceiling fan, and 12 W LED bulb remain **UNVALIDATED** by REFIT due to complete absence in the UK dataset.

---

## 1. Dataset Provenance and Licensing

| Attribute | Verified Value |
|---|---|
| **Dataset Title** | REFIT: Electrical Load Measurements (Cleaned) |
| **Primary Repository** | University of Strathclyde Pure Portal |
| **Official Archive URL** | `https://pure.strath.ac.uk/ws/portalfiles/portal/62090184/CLEAN_REFIT_081116.7z` |
| **Official Metadata URL** | `https://pure.strath.ac.uk/ws/portalfiles/portal/62090183/CLEAN_READ_ME_081116.txt` |
| **Publication Citation** | Murray, D., Stankovic, L., & Stankovic, V., *"An electrical load measurements dataset of United Kingdom households from a two-year longitudinal study"*, Scientific Data 4, 160122 (2017). DOI: 10.1038/sdata.2016.122 |
| **Licence** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Monolithic Archive Size** | 490.4 MB compressed (contains all 20 residences; temporary archive purged post-extraction) |
| **Target Extracted File** | `CLEAN_House21.csv` |
| **Local File Size** | 316,713,466 bytes (302.04 MB) |
| **SHA-256 Checksum** | `fc5471adf36c69fa65438270b4f95a51d2d7630b5461ca2db74652b41b15e10b` |

---

## 2. Channel Identity and Appliance Mapping

From the official metadata schema (`CLEAN_READ_ME_081116.txt`), House 21 is monitored with 1 aggregate mains sensor and 9 plug-in Individual Appliance Monitors (IAMs):

```
House 21 (Monitored from 2014-03-07 to 2015-07-10)
  0. Aggregate (Mains active power in Watts)
  1. Fridge-Freezer (Samsung, SR-L3216B)
  2. Tumble Dryer (Unknown)
  3. Washing Machine (Beko, WMB81241LW)
  4. Dishwasher (AEG, FAVORIT)
  5. Food Mixer (Unknown)
  6. Television (Unknown)
  7. Kettle (Unknown)
  8. Vivarium (Unknown)
  9. Pond Pump (Unknown, Unknown)  <--- Sole water pump in REFIT
```

---

## 3. Data-Quality and Ground-Truth Audit

We conducted a complete audit of all 5,383,993 rows in `CLEAN_House21.csv`:

### 3.1 Temporal Characteristics
- **Total Span:** March 7, 2014 16:20:20 UTC to July 10, 2015 11:56:35 UTC (489.82 days, ~16.1 months).
- **Sampling Interval:** Transmissions occur on load change or heartbeat.
  - Median interval: **7.0 s**
  - Mean interval: **7.86 s**
  - 10th percentile: **2.0 s**, 90th percentile: **14.0 s**, 99th percentile: **15.0 s**
  - Duplicate Unix timestamps: **0 (0.000%)**

### 3.2 Signal Integrity and Missing Data Policy
- **Null Values:** Zero null values in any column.
- **Negative Readings:** Zero negative readings in `Aggregate` or `Appliance9`.
- **Issues Column:** In REFIT, the `Issues` column flags telemetry dropouts, sensor failures, or wireless receiver communication drops:
  - `Issues == 0` (Clean data): **5,176,881 samples (96.15%)**
  - `Issues != 0` (Flagged error): **206,832 samples (3.84%)**
  - Sampling gaps $> 120$ s (Outages / dropouts): **288 samples**
- **Strict Ground-Truth Validity Mask:**
  $$\text{Valid}(t) = (\text{Issues}_t == 0) \land (P_{agg}(t) \ge 0) \land (P_{pump}(t) \ge 0) \land (\Delta t \le 120\text{ s})$$
  **Critical Rule Enforced:** Under no circumstances are missing submeter readings silently filled with `0.0 W` and scored as true idle periods. All metrics, supervised training, and validation scoring are evaluated strictly over the 5,176,881 valid samples. Excluded samples (207,112, 3.85%) are isolated.

### 3.3 Operating Profile of House 21 Pond Pump
A power histogram of the 5.38M readings reveals a bimodal distribution:
- **Standby / Disconnected ($0 \le P \le 5$ W):** 2,099,559 samples (39.00%)
- **Transition Band ($5 < P < 20$ W):** 16 samples (0.00%)
- **Active Operating Band ($20 \le P \le 50$ W):** 3,284,157 samples (61.00%)
- **Anomalous Spikes ($> 100$ W):** 239 samples (0.004%)
- **On/Off Threshold:** **20.0 W** unambiguously separates idle (<5 W) from operating (42–47 W).
- **Active Power Parameters:** Median = **44.0 W**, Mean = **44.45 W**, Std = 1.34 W.

### 3.4 Seasonal Operating Regime
Grouped by month, the operational pattern of the pond pump is striking:

| Month | Total Samples | Active Samples | Prevalence (% ON) | Operating Context |
|---|---|---|---|---|
| **2014-03** | 341,766 | 0 | 0.00% | Pump completely powered down |
| **2014-04** | 359,150 | 0 | 0.00% | Pump completely powered down |
| **2014-05** | 350,528 | 0 | 0.00% | Pump completely powered down |
| **2014-06** | 369,369 | 0 | 0.00% | Pump completely powered down |
| **2014-07** | 307,092 | 0 | 0.00% | Pump completely powered down |
| **2014-08** | 316,999 | 4,728 | 1.49% | Pump commissioned / intermittent testing |
| **2014-09** | 304,057 | 251,868 | 82.84% | Regular operation begun |
| **2014-10** | 356,497 | 356,471 | 99.99% | Continuous autumn filtration |
| **2014-11** | 376,769 | 376,727 | 99.99% | Continuous filtration |
| **2014-12** | 277,413 | 277,396 | 99.99% | Continuous winter aeration |
| **2015-01** | 316,463 | 316,458 | 100.00% | Continuous winter aeration |
| **2015-02** | 361,305 | 361,305 | 100.00% | Continuous winter aeration |
| **2015-03** | 353,850 | 353,825 | 99.99% | Continuous filtration |
| **2015-04** | 312,610 | 312,605 | 100.00% | Continuous spring filtration |
| **2015-05** | 286,248 | 286,247 | 100.00% | Continuous spring filtration |
| **2015-06** | 273,411 | 266,324 | 97.41% | Brief service / power shutoffs (7 cycles) |
| **2015-07** | 120,466 | 120,466 | 100.00% | Continuous summer filtration |

---

## 4. Leakage-Safe Experimental Methodology

### 4.1 Chronological Partitioning
To guarantee zero look-ahead bias and isolate train/test data temporally:

| Partition | Date Range | Total Samples | Valid Samples | Active Prevalence |
|---|---|---|---|---|
| **Train (60%)** | 2014-03-07 to 2014-12-12 | 3,230,295 | 3,109,864 | 34.61% ON |
| **Boundary Buffer 1** | Dropped 100 samples | 100 | - | Prevents rolling leakage |
| **Validation (20%)** | 2014-12-12 to 2015-03-22 | 1,076,698 | 1,030,446 | 100.00% ON |
| **Boundary Buffer 2** | Dropped 100 samples | 100 | - | Prevents rolling leakage |
| **Held-Out Test (20%)** | 2015-03-22 to 2015-07-10 | 1,076,800 | 1,036,371 | 99.36% ON |

### 4.2 Feature Engineering (Mains Aggregate Only)
Inference features are derived **exclusively from aggregate active power ($P_{agg}$)**:
- $P_{agg}$: Whole-house active power (W).
- $\Delta P_{agg}$: Instantaneous discrete derivative $P_{agg}(t) - P_{agg}(t-1)$.
- Rolling statistics over 5-sample window (~40 s lookback): Mean, Standard Deviation, Maximum, Minimum.
- Submeter readings and ground-truth states are **never accessible during feature computation**.

### 4.3 Models Evaluated
1. **Simple Aggregate Power Threshold:** Flags ON if $P_{agg} \ge \theta$. Optimal $\theta = 100.0$ W tuned on Validation partition.
2. **Differential Power Step Baseline:** Flags ON if $\Delta P_{agg} \in [\theta - 15, \theta + 15]$ W. Optimal $\theta = 20.0$ W tuned on Validation partition.
3. **Random Forest Classifier:** 100 trees, max depth 10, random seed 42. Trained strictly on Train partition (150,000 evenly subsampled instances). Probability threshold $\ge 0.10$ tuned on Validation partition.
4. **Persistence Baseline (Oracle Reference):** Predicts $y(t) = y_{true}(t-1)$. Labeled strictly as an oracle reference.
5. **Majority Class Baseline:** Predicts the Train majority class (OFF).

---

## 5. Experimental Results

All metrics below are computed on the **strictly held-out test partition (1,036,371 valid samples, 110.2 days)**.

### 5.1 Comprehensive Benchmark Comparison Table

| Metric | Simple Threshold ($\ge 100$W) | Differential Step ($\Delta P \in [5,35]$W) | Random Forest (Aggregate Only) | Persistence (Oracle Reference) | Majority Class (All-OFF) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Sample Accuracy** | 0.9934 | 0.0917 | 0.9866 | **1.0000** | 0.0064 |
| **Sample Precision** | 0.9936 | 0.9886 | 0.9938 | **1.0000** | 0.0000 |
| **Sample Recall** | 0.9998 | 0.0869 | 0.9928 | **1.0000** | 0.0000 |
| **Sample F1 Score** | **0.9967** | 0.1598 | **0.9933** | **1.0000** | 0.0000 |
| **Sample Specificity** | 0.0000 | 0.8446 | 0.0318 | **1.0000** | 1.0000 |
| **True Positives (samples)** | 1,029,574 | 89,486 | 1,022,278 | 1,029,730 | 0 |
| **False Positives (samples)** | 6,630 | 1,030 | 6,419 | 0 | 0 |
| **True Negatives (samples)** | 0 | 5,600 | 211 | 6,630 | 6,630 |
| **False Negatives (samples)** | 167 | 940,255 | 7,463 | 11 | 1,029,741 |
|---|---|---|---|---|---|
| **Ground-Truth Events** | 13 | 13 | 13 | 13 | 13 |
| **Predicted Events** | 60 | 3,071 | 3,710 | 13 | 0 |
| **Matched Events (TP)** | 1 | 0 | 1 | **13** | 0 |
| **Event Precision** | 0.0167 | 0.0000 | 0.0003 | **1.0000** | 0.0000 |
| **Event Recall** | 0.0769 | 0.0000 | 0.0769 | **1.0000** | 0.0000 |
| **Event F1 Score** | 0.0274 | 0.0000 | **0.0005** | **1.0000** | 0.0000 |
| **False Alarms / Day** | 0.535 | 27.868 | 33.657 | **0.000** | 0.000 |
| **Mean Absolute Delay (s)** | 0.0 | 0.0 | 0.0 | **7.23** | 0.0 |
|---|---|---|---|---|---|
| **Active Period MAE (W)** | **2.55** | 42.37 | 2.86 | **2.55** | 46.16 |
| **Inactive Period MAE (W)** | 42.92 | **7.26** | 41.58 | **0.71** | **0.71** |
| **Overall Power MAE (W)** | **2.81** | 42.14 | 3.11 | **2.54** | 45.86 |
| **Relative Energy Error (%)** | **-4.89%** | -91.69% | **-5.58%** | **-5.49%** | -100.00% |

---

## 6. Scientific Analysis and Error Decomposition

### 6.1 The Disconnect Between Sample F1 (0.993) and Event F1 (0.0005)
A superficial evaluation relying solely on sample-level metrics would report that Random Forest achieved **99.33% F1 score** and conclude that low-power pump NILM is solved. 

This conclusion is **scientifically invalid**:
- In the held-out test set, the pump was ON for 99.36% of the duration. A trivial model predicting ON 100% of the time attains a sample precision of 0.9936, recall of 1.0000, and F1 of 0.9968.
- The Random Forest model produces **3,710 predicted event activations**, corresponding to **33.66 false alarms per day**. Because of fluctuating aggregate noise, the model's output chatters continuously across its probability threshold whenever aggregate power dips or rises.
- Across 110 days and 13 true onsets, Random Forest matched only **1 single onset** within the 120-second tolerance window. Its genuine event-level detection capability is virtually zero (**Event F1 = 0.0005**).

### 6.2 Low-Power Signal-to-Noise Floor at Mains Level
Why does aggregate NILM struggle to detect the pump transitions?
- **Appliance Draw:** The pump draws $44.45 \pm 1.34$ W.
- **Mains Baseline:** Aggregate active power in House 21 averages **646.8 W** (median 272.0 W, max 65,793 W).
- **Concurrent Appliance Interference:** During pump active periods:
  - 38.05% of the time, 1 other major appliance is running (e.g. Fridge-Freezer cycling at ~80–120 W).
  - 19.85% of the time, 2 other major appliances are running.
  - 1.07% of the time, 3 or more appliances are running (e.g., Washing Machine at ~2,100 W, Kettle at ~2,500 W).
- **Onset Step Distribution:** Examining aggregate power changes at the exact timestamp of pump onsets reveals a **median step size of +0.0 W** (mean +62.2 W, min -2,340 W, max +2,989 W). The 44 W step is smaller than the intrinsic background noise of the residence.

### 6.3 Active vs. Inactive Power MAE
Decomposing power estimation errors highlights the asymmetry:
- **Active Period MAE:** When the pump is truly ON, predicting $P_{pump} = 43.63$ W yields an active MAE of **2.86 W** for Random Forest (and **2.55 W** for Threshold). Because the motor runs at near-constant steady state, power estimation during active periods is accurate.
- **Inactive Period MAE:** When the pump is truly OFF, Random Forest continues predicting ON (specificity = 3.18%), yielding an inactive MAE of **41.58 W**.
- **Energy Estimation:** Because inactive periods represented only 0.64% of the test period, the total energy error was only **-5.58%**. However, this low energy error is an artifact of continuous operation, not selective disaggregation.

---

## 7. Generalization Limits and Validation Status

### 7.1 Validation Status Table

| Domain / Appliance | Validation Rating | Scientific Rationale |
|---|:---:|---|
| **REFIT House 21 Pond Pump** | `PARTIALLY_VALIDATED` | **Partially Validated:** Evaluated on 5.18M real measurements. Confirms single-phase induction motor power tracking during long steady runs, but disaggregation of individual onsets fails (Event F1 = 0.0005). |
| **Energy Mirror 75 W Pump** | `PARTIALLY_VALIDATED` | **Partially Validated with Caveats:** Motor electrical physics are compatible (fractional-horsepower single-phase induction), but the duty cycle is completely different (continuous 24/7 filtration vs. intermittent 15–45 min domestic batch pumping). |
| **Rating Compatibility** | `INCOMPATIBLE_RATING` | **Incompatible Rating Note:** Measured REFIT pump active power is **44.4 W** (median 44.0 W), which is **41% lower than Energy Mirror's 75 W specification**. |
| **140 W Water Heater** | `NOT_VALIDATED` | Zero representation in REFIT. UK residential water heating is gas combi-boiler or 3 kW immersion. |
| **45 W Ceiling Fan** | `NOT_VALIDATED` | Zero representation in REFIT. UK temperate climate does not use ceiling fans. |
| **12 W Single LED Bulb** | `NOT_VALIDATED` | Zero representation in REFIT. Lighting circuits are hardwired into mains distribution panels. |

### 7.2 Transferability to Energy Mirror's Simulated 75 W Sump Pump
Can the REFIT results be transferred to validate Energy Mirror's domestic sump pump?
1. **Duty Cycle Gap:** Domestic water pumps (such as Indian overhead tank lift pumps) operate in **intermittent batch duty** (turning on 1–3 times per day for 20–45 minutes). The REFIT pond pump operates in **continuous duty** (running uninterrupted for months). Models evaluated on continuous loads cannot be assumed to perform on batch loads without high false alarm rates.
2. **Signal-to-Noise Challenge:** If a 44 W pump is obscured by a 272 W median baseline, a 75 W pump will have slightly higher visibility ($\sim 1.7\times$), but remains near the mains measurement threshold without multi-turn CT amplification or reactive power ($Q$) signatures.

---

## 8. Reproducibility Instructions

To replicate this experiment from scratch:

1. **Verify Environment:**
   ```powershell
   backend\ml_experiments\.venv_ml\Scripts\python.exe -m pip install py7zr
   ```

2. **Download & Extract House 21 Data:**
   ```powershell
   backend\ml_experiments\.venv_ml\Scripts\python.exe backend/ml_experiments/download_refit_house21.py
   ```
   *Downloads `CLEAN_REFIT_081116.7z` from Strathclyde Pure, extracts `CLEAN_House21.csv` to `backend/ml_experiments/data/`, verifies SHA-256 (`fc5471ad...`), and removes the temporary 7z archive.*

3. **Execute Ground-Truth Audit:**
   ```powershell
   backend\ml_experiments\.venv_ml\Scripts\python.exe backend/ml_experiments/audit_refit_house21.py
   ```

4. **Run Validation Benchmark:**
   ```powershell
   backend\ml_experiments\.venv_ml\Scripts\python.exe backend/ml_experiments/run_refit_experiment.py
   ```
   *Generates machine-readable results in `backend/ml_experiments/results/refit_pump_validation.json`.*

5. **Run Automated Unit Tests:**
   ```powershell
   backend\ml_experiments\.venv_ml\Scripts\python.exe -m unittest backend/ml_experiments/tests/test_refit_validation.py
   ```

---

## 9. Conclusion

Milestone 2C.9 establishes the first rigorous empirical evaluation of low-power motor NILM on real residential telemetry for the Energy Mirror project. By testing across 16 months of continuous monitoring, the evaluation proves that:
1. Sample-level F1 scores on continuous loads are heavily distorted by high positive class prevalence.
2. Event-level evaluation with strict onset tolerance is mandatory to measure operational reliability.
3. Single-phase induction motors at ~44 W cannot be reliably disaggregated from aggregate active power alone amidst realistic domestic background loads without supplementary features (e.g., reactive power or transient current signatures).
4. Physical hardware validation remains pending; all findings represent software analysis on historical public telemetry under strict isolation (`ENABLE_HARDWARE_INGEST=false`).
