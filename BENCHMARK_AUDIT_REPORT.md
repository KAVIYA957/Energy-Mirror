# Energy Mirror: Real-Data Benchmark Audit and Event-Level Evaluation Report (Milestone 2C.3)

**Document Reference:** `BENCHMARK_AUDIT_REPORT.md`  
**Milestone:** 2C.3 — Benchmark Audit and Event-Level Evaluation  
**Reference Checkpoint:** `9fbd3fb`  
**Date:** October 2026  
**Status:** Rigorous Empirical Audit Completed — Verified Metrics and Operational Event Evaluation  

---

## Executive Summary & Corrected Scientific Claims

In Milestone 2C.2, the first genuine real-world public NILM benchmark was established using the peer-reviewed **iAWE dataset** (Zenodo `13917372`, Batra et al. BuildSys 2013). This audit resolves ambiguities in earlier reporting, introduces event-level evaluation, decomposes regression errors into active and inactive sub-populations, and verifies the experimental methodology against strict scientific standards.

### Corrected Claims & Key Audit Findings

1. **Model Hierarchy and Ranking Clarification:**
   - **Original Report Wording:** Referred to the Random Forest Classifier as the "best overall model" ($F1=0.3404$).
   - **Corrected Audit Finding:** **The Persistence Baseline achieves the highest reported sample-level F1 ($0.7353$)**, but functions as an **oracle benchmark** because it requires the ground-truth submeter state $y_{t-1}$ at test time.
   - **Random Forest is the strongest deployable machine-learning classifier** ($F1=0.3404$, Precision: $61.54\%$, Recall: $23.53\%$), operating strictly from whole-house aggregate features.
2. **Deconstruction of the "1.76 W MAE" Regression Score:**
   - In earlier reporting, the Random Forest Regressor reported an overall MAE of **1.76 W**, which created the misleading impression that motor active power was estimated within $\pm 2\text{ W}$.
   - **Audit Decomposition:** 
     - On the **95,236 inactive samples** (motor OFF), MAE is **1.59 W**.
     - On the **34 active samples** (motor ON, true mean $715.94\text{ W}$), MAE is **476.48 W** (mean predicted: $239.46\text{ W}$).
     - The model underestimates active pump power by **$66.55\%$**, resulting in a **$41.93\%$ Relative Energy Total Error (RETE)**.
     - The low overall sample MAE is a mathematical artifact of extreme class imbalance ($99.964\%$ inactive samples), which dilutes active errors by a factor of 2,800.
3. **Event-Level Disaggregation Findings:**
   - Over the 6.72-day held-out test window, ground truth contains **9 discrete bursts** comprising **6 unified pumping cycles** (representing ~3.4 cumulative minutes of pumping).
   - **Random Forest Event Performance:** Detects 4 of the 6 cycles ($Recall=66.67\%$) with only 3 false alarms ($Precision=57.14\%$, Event $F1=0.6154$, **0.45 false events/day**, mean detection delay of **9.0 seconds**).
   - **Differential Step Event Performance:** Triggers **364 events** (359 false positives), yielding an event precision of **$1.37\%$** and **53.43 false events/day**. This empirically proves that single-variable differential edge detection cannot operate in real homes without catastrophic false alarms.
4. **Data Integrity & Leakage Verification:**
   - Train, validation, and test splits are strictly chronological.
   - The 100-sample boundary buffer (600 seconds) discarded between partitions completely prevents any rolling feature lookback (5 samples = 30 seconds) from leaking across boundaries.

---

## 1. Classification Metrics Audit & Formulas

### Mathematical Definitions

For a test set with ground truth $y \in \{0, 1\}$ and predictions $\hat{y} \in \{0, 1\}$:

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

$$\text{Precision} = \frac{TP}{TP + FP}$$

$$\text{Recall} = \frac{TP}{TP + FN}$$

$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN}$$

### Audited Sample-Level Classification Benchmark

Evaluated over the identical held-out test window ($N = 95,270$ samples, positive prevalence $= 0.0357\%$):

| Model / Algorithm | Role / Nature | Accuracy | Precision | Recall | F1-Score | Confusion Matrix (TP, FP, FN, TN) | Scientific Characterization |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Persistence ($t-1$)** | Oracle submeter reference | **0.9998** | **0.7353** | **0.7353** | **0.7353** | **TP=25, FP=9, FN=9, TN=95,227** | **Highest sample-level F1.** Capitalizes on run-length autocorrelation of 10–30 min cycles, but requires submeter state at $t-1$. |
| **Random Forest Classifier** | Deployable aggregate ML | **0.9997** | **0.6154** | **0.2353** | **0.3404** | **TP=8, FP=5, FN=26, TN=95,231** | **Strongest deployable ML classifier.** Multi-feature ensemble rejects $99.99\%$ of background domestic transients. |
| **Differential Step Baseline** | Rule-based edge detector | 0.9930 | 0.0108 | 0.2059 | 0.0206 | TP=7, FP=640, FN=27, TN=94,596 | **Catastrophic false alarms.** 640 false positive samples caused by competing compressor steps (+200–500 W). |
| **Simple Power Threshold** | Static aggregate threshold | 0.9996 | 0.0000 | 0.0000 | 0.0000 | TP=0, FP=4, FN=34, TN=95,232 | **Complete failure.** Aggregate power varies up to 8 kW; single threshold cannot separate a 600 W pump. |
| **Majority Class (All OFF)** | Zero-intelligence reference | 0.9996 | 0.0000 | 0.0000 | 0.0000 | TP=0, FP=0, FN=34, TN=95,236 | **Exposes the accuracy fallacy.** 99.96% accuracy is trivially achieved by doing nothing. |

### The Mechanics of the Persistence Baseline Score

Why does Persistence achieve $F_1 = 0.7353$ while Random Forest achieves $0.3404$?
- When an appliance operates in contiguous runs of $L$ samples:
  - The onset sample ($t=0$) is preceded by $0 \to$ predicted $0$, true $1 \implies \mathbf{FN = 1}$.
  - The interior samples ($t=1 \dots L-1$) are preceded by $1 \to$ predicted $1$, true $1 \implies \mathbf{TP = L - 1}$.
  - The offset sample ($t=L$) is preceded by $1 \to$ predicted $1$, true $0 \implies \mathbf{FP = 1}$.
- In the test set, the 34 active samples occur in runs averaging 3.8 samples. Across these runs, Persistence records $TP=25$, $FP=9$, and $FN=9$:
  $$\text{Precision} = \frac{25}{25 + 9} = 73.53\%, \quad \text{Recall} = \frac{25}{25 + 9} = 73.53\%, \quad F_1 = 0.7353$$
- **Critical Limitation:** Persistence misses *every single turn-on edge* (delayed by 1 sample) and *every single turn-off edge* (overshoots by 1 sample). It cannot forecast or detect a new event on its own; it merely persists an already established ground-truth state.

---

## 2. Regression & Energy Metric Audit

### Mathematical Definitions

For active power measurements $p_i$ and predictions $\hat{p}_i$ (Watts) at uniform sampling interval $\Delta t = 6\text{ seconds}$:

$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |p_i - \hat{p}_i|, \qquad \text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (p_i - \hat{p}_i)^2}$$

$$\text{Energy}_{\text{True}} = \sum_{i=1}^N p_i \cdot \frac{\Delta t}{3600 \cdot 1000} \text{ [kWh]}, \qquad \text{Energy}_{\text{Pred}} = \sum_{i=1}^N \hat{p}_i \cdot \frac{\Delta t}{3600 \cdot 1000} \text{ [kWh]}$$

$$\text{RETE} = \frac{|\text{Energy}_{\text{Pred}} - \text{Energy}_{\text{True}}|}{\max(\text{Energy}_{\text{True}}, 10^{-6})} \times 100\%$$

### The Error Decomposition Identity

The overall Mean Absolute Error is a convex combination of errors on the active and inactive sub-populations:

$$\text{MAE}_{\text{overall}} = w_{\text{active}} \cdot \text{MAE}_{\text{active}} + w_{\text{inactive}} \cdot \text{MAE}_{\text{inactive}}$$

where $w_{\text{active}} = \frac{N_{\text{active}}}{N} = \frac{34}{95270} \approx 0.000357$, and $w_{\text{inactive}} = \frac{95236}{95270} \approx 0.999643$.

### Sub-Population Regression Results

| Metric Category | Random Forest Regressor | Mean Active Baseline | Zero Baseline (Predict 0 W) |
| :--- | :---: | :---: | :---: |
| **Overall MAE (All 95,270 samples)** | **1.76 W** | 1.23 W | 1.25 W |
| **Overall RMSE (All 95,270 samples)** | **15.46 W** | 14.96 W | 15.70 W |
| **Active-Only MAE ($N = 34$, Motor ON)** | **476.48 W** | 573.21 W | 715.94 W |
| **Active-Only RMSE ($N = 34$, Motor ON)**| **497.38 W** | 628.95 W | 716.36 W |
| **Mean True Active Power** | 715.94 W | 715.94 W | 715.94 W |
| **Mean Predicted Active Power** | 239.46 W | 142.73 W | 0.00 W |
| **Active Power Underestimation** | **66.55%** | 80.06% | 100.00% |
| **Inactive-Only MAE ($N = 95,236$, Motor OFF)**| 1.59 W | 1.02 W | 0.99 W |
| **Inactive-Only RMSE ($N = 95,236$, Motor OFF)**| 12.28 W | 9.10 W | 7.96 W |
| **True Cumulative Energy** | 0.198 kWh | 0.198 kWh | 0.198 kWh |
| **Predicted Cumulative Energy** | 0.115 kWh | 0.013 kWh | 0.000 kWh |
| **Absolute Energy Error** | 0.083 kWh | 0.185 kWh | 0.198 kWh |
| **Relative Energy Total Error (RETE)** | **41.93%** | **93.36%** | **100.00%** |

### Why Low Sample MAE Coexists with High Energy Error

1. The Zero Baseline achieves an overall MAE of **1.25 W**, which is *lower* than the Random Forest's 1.76 W, yet it detects 0 kWh of energy ($\text{RETE} = 100\%$).
2. The Random Forest predicts small non-zero values ($1\text{ W} - 5\text{ W}$) during inactive periods due to background noise. Accumulated over 95,236 inactive samples, this slight baseline lift inflates overall MAE slightly, but helps capture portion of true energy.
3. On actual pumping activations ($715.94\text{ W}$ true mean), the Random Forest predicts only $239.46\text{ W}$ because concurrent air conditioner cycling partially masks the step, leading to **$66.55\%$ underestimation during operation**.
4. **Conclusion:** Sample-level MAE across all samples is **unusable** as a primary metric for low-duty-cycle appliances. Disaggregation benchmarks must report **Active-Only MAE** and **Relative Energy Total Error (RETE)**.

---

## 3. Event-Level Evaluation Methodology & Results

### Rationale for Event-Level Evaluation

In domestic energy management, homeowners and automated systems do not consume individual 6-second predictions. They need answers to operational questions:
1. *Did the water pump turn on this morning?* (True Positive Event)
2. *Did the system falsely claim the pump engaged when it was actually an AC compressor?* (False Alarm Event)
3. *How many false alarms occur per day?* (Operational Burden)

### Event Matching Specification

- **Event Extraction:** Contiguous intervals of $\hat{y} = 1$ are extracted as events.
- **Cycle Merging:** A gap tolerance of $\tau_{\text{gap}} \le 30\text{ seconds}$ merges brief multi-second dropouts into single operating cycles.
- **Candidate Matching:** A predicted event $P$ matches a ground-truth event $G$ if their start times satisfy $|t_{P,\text{start}} - t_{G,\text{start}}| \le \tau_{\text{tol}}$ OR they overlap in time.
- **One-to-One Bipartite Greedy Matching:** Candidate pairs are sorted by absolute onset delay and matched greedily. Neither ground-truth nor predicted events can match multiple times.
- **Primary Tolerance Rationale ($\tau_{\text{tol}} = 60\text{ seconds}$):**
  - Sampling resolution is 6 seconds.
  - Feature extraction uses a 5-sample (30-second) rolling lookback.
  - Induction motors exhibit inrush transients followed by gradual steady-state settling over 2–4 samples.
  - 60 seconds ($\pm 10$ samples) accommodates physical settling and window propagation delays while remaining far below the multi-hour spacing between distinct domestic events.

### Audited Event Benchmark Results

**Test Period:** June 28, 2013 22:25 to July 5, 2013 15:41 (6.72 days).

#### Scenario A: Raw Contiguous Events (9 Ground Truth Events)

| Model | Pred Events | TP | FP | FN | Event Prec | Event Rec | Event F1 | False Events / Day | Mean Delay |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | 7 | 4 | 3 | 5 | **0.5714** | **0.4444** | **0.5000** | **0.45 / day** | +9.0 s |
| **Persistence ($t-1$)** | 9 | 9 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.00 / day | +6.0 s |
| **Differential Step** | 364 | 5 | 359 | 4 | 0.0137 | 0.5556 | 0.0268 | 53.43 / day | -2.4 s |
| **Simple Threshold** | 2 | 0 | 2 | 9 | 0.0000 | 0.0000 | 0.0000 | 0.30 / day | 0.0 s |
| **Majority Class** | 0 | 0 | 0 | 9 | 0.0000 | 0.0000 | 0.0000 | 0.00 / day | 0.0 s |

#### Scenario B: Merged Pumping Cycles (6 Ground Truth Operating Cycles, Gap $\le 30$s)

| Model | Pred Events | TP | FP | FN | Event Prec | Event Rec | Event F1 | False Events / Day | Missed Events / Day | Mean Delay |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | 7 | 4 | 3 | 2 | **0.5714** | **0.6667** | **0.6154** | **0.45 / day** | **0.30 / day** | +9.0 s |
| **Persistence ($t-1$)** | 9 | 6 | 3 | 0 | 0.6667 | 1.0000 | 0.8000 | 0.45 / day | 0.00 / day | +6.0 s |
| **Differential Step** | 364 | 5 | 359 | 1 | 0.0137 | 0.8333 | 0.0270 | 53.43 / day | 0.15 / day | -2.4 s |
| **Simple Threshold** | 2 | 0 | 2 | 6 | 0.0000 | 0.0000 | 0.0000 | 0.30 / day | 0.89 / day | 0.0 s |
| **Majority Class** | 0 | 0 | 0 | 6 | 0.0000 | 0.0000 | 0.0000 | 0.00 / day | 0.89 / day | 0.0 s |

### Tolerance Sensitivity Analysis (Random Forest)

To ensure conclusions are not artifacts of the 60-second window, we audited across a documented tolerance grid:

| Tolerance ($\tau_{\text{tol}}$) | Window Samples | TP | FP | FN | Event Precision | Event Recall | Event F1 | Mean Delay |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **12 s** | $\pm 2$ samples | 3 | 4 | 6 | 0.4286 | 0.3333 | 0.3750 | +8.0 s |
| **30 s** | $\pm 5$ samples | 4 | 3 | 5 | 0.5714 | 0.4444 | 0.5000 | +9.0 s |
| **60 s (Primary)** | $\pm 10$ samples | 4 | 3 | 5 | 0.5714 | 0.4444 | 0.5000 | +9.0 s |
| **120 s** | $\pm 20$ samples | 4 | 3 | 5 | 0.5714 | 0.4444 | 0.5000 | +9.0 s |

**Finding:** The Random Forest event metrics are completely stable across all tolerances $\ge 30\text{ seconds}$. The 4 detected events match with an average onset delay of **9.0 seconds** (1.5 samples), reflecting the time required for rolling window statistics to register the step change.

---

## 4. Temporal Leakage & Baseline Fairness Audit

| Verification Item | Audit Procedure | Finding & Evidence | Status |
| :--- | :--- | :--- | :---: |
| **Chronological Ordering** | Inspected split slicing indices | Train: $[0, 285606)$, Val: $[285706, 380774)$, Test: $[380874, 476144)$. No future samples precede earlier samples. | **VERIFIED** |
| **Boundary Buffer Sufficiency** | Compared buffer length to lookback window | Buffer dropped = 100 samples (600 s). Rolling feature window = 5 samples (30 s). Buffer is $20\times$ larger than feature lookback. Zero leakage across split boundaries. | **VERIFIED** |
| **Hyperparameter Isolation** | Inspected threshold tuning code | Threshold baseline ($P_{\text{agg}} \ge 4814.2\text{ W}$) and Differential baseline ($\Delta P \ge 220.4\text{ W}$) tuned strictly on `val_df`. Random Forest trained strictly on `train_df`. | **VERIFIED** |
| **Persistence Boundary State** | Inspected `persist_pred[0]` | Prior code used `y_train[-1]`. Fixed to true preceding state `0`. No impact on score because motor was OFF at start of test period. | **VERIFIED** |
| **Grid Outage Handling** | Checked NaN mask handling | 43,757 grid-outage intervals dropped from time grid. No forward-filling or synthetic data manufacturing across outages. | **VERIFIED** |
| **Test Set Ground Truth** | Verified sample count and positive prevalence | Test set contains exactly 95,270 samples. Active samples = 34 ($0.0357\%$). No ground truth was fabricated. | **VERIFIED** |

---

## 5. Physical Domain Gap & Boundary of Claims

To prevent misleading claims, this audit re-affirms the physical domain boundaries:

```
+----------------------------------------------------------------------------------------------------+
| DOMAIN GAP MATRIX                                                                                  |
+------------------------------+------------------------------+--------------------------------------+
| Dimension                    | iAWE Public Ground Truth     | Energy Mirror Target Baseline        |
+------------------------------+------------------------------+--------------------------------------+
| Target Appliance             | Domestic Water Motor (Rooftop)| Domestic Fractional-HP Water Pump   |
| Rated Active Power           | ~600 W – 700 W (Mean: 629 W) | 75 W (Fractional HP)                 |
| Power Ratio                  | 8.4x to 9.3x LARGER          | 1.0x (Target Model)                  |
| Concurrent Loads             | Multiple 1.5 kW ACs, Fridge  | Staged: Fan (60W), Bulb (12W), AC    |
| Available Submeter Channels  | Real Active Power (P) only   | Staged Hardware Ingest (V, I, P, PF) |
+------------------------------+------------------------------+--------------------------------------+
```

### Strictly Maintained Boundaries

1. **No Validation for 75 W Pump:** The iAWE experiment proves algorithm behavior on a 600 W motor in a noisy household. It does **not** validate detection of Energy Mirror's 75 W simulated pump.
2. **No Validation for Other Target Appliances:** This experiment does **not** establish disaggregation accuracy for the electric water heater (1500 W), ceiling fan (60 W), or LED bulb (12 W).
3. **No Reactive Power or Harmonics:** CurrentCost CT submeters only measured active power ($P$). Inductive reactive power ($Q$) or power factor ($PF$) signatures remain unvalidated on submetered real data.
4. **No Real-Time Embedded Operation:** The models were evaluated offline in Python. Real-time inference on low-power hardware has not been implemented or claimed.

---

## 6. Deliverable Artifacts

| Deliverable File | Role & Contents | Commit Status |
| :--- | :--- | :--- |
| [`BENCHMARK_AUDIT_REPORT.md`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/BENCHMARK_AUDIT_REPORT.md) | Comprehensive audit report, metric definitions, event evaluation, and domain boundaries. | Created |
| [`backend/ml_experiments/evaluate_events.py`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/evaluate_events.py) | Standalone reproducible event extraction, bipartite matching, and multi-population metrics. | Created |
| [`backend/ml_experiments/results/benchmark_audit_results.json`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/results/benchmark_audit_results.json) | Complete machine-readable results covering sample classification, decomposed regression, and event matching. | Generated |
| [`backend/ml_experiments/tests/test_ml_benchmark_audit.py`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/tests/test_ml_benchmark_audit.py) | 9 unit tests for event extraction, tolerance matching, delay tracking, and mathematical decomposition. | Verified (9/9 passed) |
| [`IAWE_EXPERIMENT_REPORT.md`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/IAWE_EXPERIMENT_REPORT.md) | Updated with corrected wording on model hierarchy and active vs inactive regression metrics. | Updated |

---

## 7. Next Scientific Steps

1. **Retain the Working Production Architecture:** Keep production Flutter application, SQLite database, simulator, and rule-based detector isolated and untouched (`ENABLE_HARDWARE_INGEST=false`).
2. **Preserve Benchmark Assets:** Maintain the automated event evaluation suite [`evaluate_events.py`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/evaluate_events.py) as the standard evaluation harness for all future NILM models.
3. **Advance to Physical Bench Metrology (Milestone 3):** To resolve the 8x power mismatch between iAWE (600 W) and Energy Mirror (75 W), acquire physical bench current-transformer readings of fractional-HP pumps under controlled concurrent loading.
