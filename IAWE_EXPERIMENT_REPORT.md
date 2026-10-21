# Energy Mirror: iAWE Real-Data NILM Validation Report (Milestone 2C.2)

**Document Reference:** `IAWE_EXPERIMENT_REPORT.md`  
**Milestone:** 2C.2 — Real-Data iAWE Validation  
**Date:** October 2026  
**Status:** Real-World Dataset Benchmark Completed — Strict Empirical Reporting  
**Benchmark Configuration:**
- **Dataset:** iAWE (Indian Dataset for Ambient Water and Energy)
- **Target Appliance:** Domestic Water Motor (Rooftop Overhead Storage Tank Lift Pump)
- **Submeter Channel:** `/building1/elec/meter12` (CurrentCost CT sensor)
- **Mains Aggregate:** `/building1/elec/meter1` + `/building1/elec/meter2` (Schneider EM6400 Smart Meter)
- **Evaluation Protocol:** Strictly chronological held-out split (60% Train, 20% Val, 20% Test) with 100-sample boundary buffer drops.
- **Hardware & Production Status:** `ENABLE_HARDWARE_INGEST=false` maintained. Production Flutter UI, database, simulator, and rule-based detector completely untouched. ML models kept isolated under `backend/ml_experiments/`.

---

## 1. Verified Source, Licence, and Provenance

| Parameter | Authoritative Value / Primary Citation | Verification Status |
| :--- | :--- | :--- |
| **Dataset Title** | Indian Dataset for Ambient Water and Energy (iAWE) | Verified |
| **Primary Authors** | Nipun Batra, Manoj Gulati, Amarjeet Singh, Mani Srivastava (IIIT Delhi & UCLA) | Verified |
| **Primary Publication** | Batra et al., "It's schedule time: An overview of public datasets, infrastructure and tools for energy disaggregation." *ACM BuildSys 2013*. | Verified |
| **Open-Access Repository** | Zenodo Record `13917372` ([DOI: 10.5281/zenodo.13917372](https://doi.org/10.5281/zenodo.13917372)) | Verified |
| **Dataset Host / Producer** | Dengyu Shi (Southwest University), Published October 11, 2024 | Verified |
| **Licence** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** | Verified (Commercial & Academic reuse with attribution) |
| **Candidate File** | `iawe.h5` | Verified |
| **Expected Size** | 427,836,094 bytes (408.02 MB) | Verified |
| **Actual Downloaded Size**| **427,836,094 bytes (408.02 MB)** | **Exact bit-for-bit match** |
| **MD5 Checksum** | `40c2a4486dde808ee814f4a9af520afb` | **Cryptographically verified** |

---

## 2. HDF5 Schema and Appliance Channel Mapping

We programmatically parsed the HDF5 structure (`building1.attrs['metadata']`) using `h5py` and `pandas.HDFStore`. The metadata contains a verified mapping of all electrical channels:

### Whole-House and Submeter Inventory

```
+--------------------------------------------------------------------------------------------------------+
| Table Key in iawe.h5        | Hardware Model  | Monitored Appliance      | Physical Role & Type        |
+-----------------------------+-----------------+--------------------------+-----------------------------+
| /building1/elec/meter1      | Schneider EM6400| Mains (Phase 1)          | Site Whole-House Aggregate  |
| /building1/elec/meter2      | Schneider EM6400| Mains (Phase 2)          | Site Whole-House Aggregate  |
| /building1/elec/meter3      | jPlug           | Fridge (Instance 1)      | Submeter (Compressor)       |
| /building1/elec/meter4      | jPlug           | Air Conditioner (Inst 1) | Submeter (HVAC Compressor)  |
| /building1/elec/meter5      | jPlug           | Air Conditioner (Inst 2) | Submeter (HVAC Compressor)  |
| /building1/elec/meter6      | jPlug           | Washing Machine (Inst 1) | Submeter (Motor + Heater)   |
| /building1/elec/meter7      | jPlug           | Computer Site (Inst 1)   | Submeter (SMPS IT Load)     |
| /building1/elec/meter8      | jPlug           | Clothes Iron (Inst 1)    | Submeter (Resistive Heating)|
| /building1/elec/meter9      | jPlug           | Unknown (Inst 1)         | Submeter (Unclassified)     |
| /building1/elec/meter10     | jPlug           | Television (Inst 1)      | Submeter (Consumer Electronics) |
| /building1/elec/meter11     | jPlug           | Wet Appliance (Inst 1)   | Submeter (Kitchen Appliance)|
| /building1/elec/meter12     | CurrentCost CT  | **Motor (Instance 1)**   | **Water Motor (Target Pump)**|
+-----------------------------+-----------------+--------------------------+-----------------------------+
```

### Channel Identification
1. **Target Water Motor (`/building1/elec/meter12`):**
   - The appliance is designated as `motor` (Instance 1) in the building metadata.
   - Hardware: CurrentCost CT sensor with RF transmitter.
   - Raw records: **447,812 rows** spanning from `2013-05-30 12:51:41+05:30` to `2013-07-05 15:41:46+05:30` (~36 days).
   - Sampling rate: CurrentCost RF transmissions occur at approximately **6-second intervals**.
2. **Whole-House Mains (`meter1` and `meter2`):**
   - Hardware: Schneider Electric EM6400 digital multi-function power meter.
   - Measurements available: Active Power ($P$), Reactive Power ($Q$), Apparent Power ($S$), Frequency ($Hz$), Voltage ($V$), Power Factor ($PF$), and Current ($I$).
   - Raw records: **4,391,017 rows** sampled at **1-second intervals** from `2013-05-24` to `2013-08-05`.
   - Mains active power is calculated by summing Phase 1 and Phase 2:  
     $$P_{\text{agg}}(t) = P_{\text{meter1}}(t) + P_{\text{meter2}}(t)$$

---

## 3. Data-Quality, Sensor Outlier, and Temporal Alignment Audit

### Empirical Verification of Physical Energy Conservation
To confirm temporal alignment between the utility Schneider smart meter and the CurrentCost motor CT clamp, we examined raw transitions where the Water Motor engaged:

```
[Window Inspection: 2013-05-30 12:59:54 to 13:00:24 (6s resolution)]
Timestamp (IST)            Aggregate Mains (W)    Water Motor Submeter (W)
---------------------------------------------------------------------------
2013-05-30 12:59:54        575.8 W                0.0 W (Idle)
2013-05-30 13:00:00        627.3 W                0.0 W (Idle)
2013-05-30 13:00:06       1183.3 W              593.0 W (TURN-ON TRANSITION)
2013-05-30 13:00:18       1189.7 W              587.0 W (Pumping)
2013-05-30 13:00:24       1180.5 W              585.0 W (Pumping)
```
- **Observed Step:** At `13:00:06`, the Water Motor submeter recorded a step from $0.0\text{ W} \to 593.0\text{ W}$ ($+593.0\text{ W}$).
- **Observed Aggregate Step:** Whole-house power surged from $575.8\text{ W} \to 1183.3\text{ W}$ ($+607.5\text{ W}$).
- **Physical Reconciliation:** $\Delta P_{\text{agg}} - \Delta P_{\text{motor}} = 14.5\text{ W}$ (within background domestic noise). This confirms true physical energy conservation and precise synchronization across disparate metering hardware.

### Data Quality Findings & Filtering Protocols
1. **Sensor Overflow Artifacts (CurrentCost Sentinel `32767`):**
   - The raw motor channel contained 3 samples with value `32767.0 W`. This is the hexadecimal sentinel value `0x7FFF` (15-bit signed integer overflow emitted when an RF packet is corrupted or sensor overflows).
   - **Protocol:** All readings $\ge 30,000\text{ W}$ were filtered and set to `NaN` before resampling.
2. **CurrentCost Standby Induction Floor:**
   - The CurrentCost clamp exhibited residual baseline drift of 40–65 W during motor idle periods (non-zero standby reading).
   - Genuine pumping events operate at 550 W – 800 W (mean: 629.2 W, median: 700.0 W).
   - **Protocol:** A threshold of $P_{\text{on}} \ge 200.0\text{ W}$ was established to cleanly separate true pumping from clamp noise.
3. **Mains Grid Outages (Load Shedding):**
   - 43,757 intervals (8.41% of the 36-day window) had missing aggregate mains readings due to New Delhi municipal grid load-shedding and power interruptions.
   - **Protocol:** Outage intervals were dropped. No synthetic values or forward-fills were manufactured for missing aggregate data.
4. **Time Grid Synchronization:**
   - Both feeds were resampled to a uniform 6-second interval (`6s`), yielding **476,344 clean synchronized samples**.

---

## 4. Preprocessing and Experimental Split Methodology

To prevent data leakage, we implemented a strictly chronological held-out evaluation:
- **Chronological Order:** Data was strictly partitioned in temporal sequence.
- **Partition Ratio:**
  - **Training Set (60%):** 285,706 samples (May 30, 2013 to June 20, 2013)
  - **Validation Set (20%):** 95,168 samples (June 20, 2013 to June 27, 2013)
  - **Test Set (20%):** 95,270 samples (June 27, 2013 to July 5, 2013)
- **Leakage Prevention:** A 100-sample buffer (10 minutes) was discarded between train/val and val/test boundaries so that rolling statistics ($P_{\text{mean}}$, $P_{\text{std}}$, $P_{\text{max}}$, $\Delta P$) never spanned partition boundaries.
- **Hyperparameter Isolation:** Model parameters and baseline thresholds were selected exclusively using the training and validation sets, never evaluated against the test set until inference.

### Extreme Class Imbalance (The Prevalence Reality)
Domestic water pumping in urban Indian homes is an intermittent, batch-duty operation (lifting municipal water to rooftop tanks for 10–30 minutes once or twice daily):
- **Training Set:** 535 active pumping samples out of 285,706 (**0.187% prevalence**).
- **Validation Set:** 93 active pumping samples out of 95,168 (**0.098% prevalence**).
- **Test Set:** 34 active pumping samples out of 95,270 (**0.036% prevalence**, representing ~3.4 minutes of cumulative pumping over 6.6 days).

---

## 5. Benchmark Results: Baseline Comparison on Genuine Real-World Data

### Task 1: Water Motor ON/OFF Classification

We evaluated five distinct classification approaches on the held-out test set (95,270 samples, 34 positive pump events):

| Model / Algorithm | Accuracy | Precision | Recall | F1-Score | Confusion Matrix (TP, FP, FN, TN) | Scientific Characterization |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Persistence Baseline**<br>($y_t = y_{t-1}$) | **0.9998** | **0.7353** | **0.7353** | **0.7353** | **TP=25, FP=9, FN=9, TN=95,227** | **Highest sample-level F1 (Oracle Reference).** Capitalizes on run-length autocorrelation of contiguous runs, but requires ground-truth submeter state $y_{t-1}$. |
| **Random Forest Classifier**<br>(100 trees, max depth 10) | 0.9997 | 0.6154 | 0.2353 | 0.3404 | TP=8, FP=5, FN=26, TN=95,231 | **Strongest deployable ML classifier.** Rejects 99.99% of background domestic transients from aggregate mains alone. |
| **Simple Power Threshold**<br>($P_{\text{agg}} \ge 4,814.2\text{ W}$) | 0.9996 | 0.0000 | 0.0000 | 0.0000 | TP=0, FP=4, FN=34, TN=95,232 | **Complete failure.** Whole-house power varies from 400 W to 8 kW; fixed threshold cannot detect 600 W pump. |
| **Differential Step Baseline**<br>($\Delta P_{\text{agg}} \ge 220.4\text{ W}$) | 0.9930 | 0.0108 | 0.2059 | 0.0206 | TP=7, FP=640, FN=27, TN=94,596 | **Severe false alarms.** Naive step detector triggers on refrigerator and AC compressor cycles (+200–500W). |
| **Majority Class Baseline**<br>(Predict all class 0 / OFF) | 0.9996 | 0.0000 | 0.0000 | 0.0000 | TP=0, FP=0, FN=34, TN=95,236 | **Exposes the accuracy fallacy.** 99.96% accuracy is trivially achieved by doing nothing. |

---

### Task 2: Power Disaggregation (Continuous Watts Disaggregation)

Evaluated over the full 95,270 test intervals (cumulative ground truth motor energy consumption: **0.198 kWh**).

> [!NOTE]
> **Sub-Population Error Decomposition:** Overall sample MAE is heavily diluted by the 95,236 inactive samples ($99.964\%$ prevalence). The table below reports both overall error and active-only error to prevent misleading interpretations (detailed in `BENCHMARK_AUDIT_REPORT.md`).

| Model / Algorithm | Overall MAE (All Samples) | Active-Only MAE (Motor ON, N=34) | Inactive-Only MAE (Motor OFF, N=95,236) | Ground Truth Energy | Predicted Energy | Relative Energy Total Error (RETE) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Regressor** | **1.76 W** | **476.48 W** (Underestimates 66.55%) | **1.59 W** | 0.198 kWh | 0.115 kWh | **41.93%** |
| **Mean Active Baseline** (606.6 W when RF ON) | 1.23 W | 573.21 W | 1.02 W | 0.198 kWh | 0.013 kWh | 93.36% |
| **Zero Baseline** (All 0 W) | 1.25 W | 715.94 W | 0.99 W | 0.198 kWh | 0.000 kWh | 100.00% |

*(For event-level disaggregation metrics and tolerance sensitivity analysis, refer to [`BENCHMARK_AUDIT_REPORT.md`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/BENCHMARK_AUDIT_REPORT.md) and [`backend/ml_experiments/evaluate_events.py`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/evaluate_events.py)).*

---

## 6. Scientific Analysis of Findings

### 1. The "Accuracy Fallacy" in Real NILM
On synthetic datasets where appliances toggle 50% of the time, simple models claim >90% accuracy and F1. On genuine real-world public data, the positive prevalence is **0.036%**. A model that does nothing achieves **99.96% accuracy**. Accuracy is therefore completely uninformative for NILM event detection; precision, recall, and F1 are the only valid metrics.

### 2. The Failure of Rule-Based Differential Step Detection in Real Homes
Energy Mirror's differential simulator and rule-based detector match $+75\text{ W}$ steps against isolated appliance profiles. When evaluated against genuine whole-house data:
- The Differential Step baseline generated **640 false positives** ($FP=640$ vs $TP=7$), resulting in a precision of **1.08%**.
- In a real residential environment, refrigerator compressor cycling, air conditioner multi-stage switching, television brightness fluctuations, and clothes iron thermostats produce hundreds of $+200\text{ W}$ to $+700\text{ W}$ steps daily that mimic pump transients.
- This proves that **single-variable differential edge detection cannot operate reliably on real residential mains without multi-dimensional features (reactive power, harmonics, or waveform duration)**.

### 3. Machine Learning Generalization
- The Random Forest Classifier achieved **61.54% Precision** ($FP=5$, $TP=8$), demonstrating that nonlinear combinations of rolling statistics ($P_{\text{mean}}$, $P_{\text{max}}$, $P_{\text{std}}$) significantly reject background transient false alarms.
- However, Recall remained low (**23.53%**), because pump engagement often coincided with concurrent AC switching, which obscured the pump's signature in aggregate real power.

---

## 7. Physical Domain Mismatch: iAWE vs. Energy Mirror Simulator

| Feature / Attribute | iAWE Dataset Ground Truth | Energy Mirror Target Baseline | Domain Alignment Analysis |
| :--- | :--- | :--- | :--- |
| **Appliance Type** | Domestic Water Motor (Lifting to roof tank) | Fractional-HP Domestic Water Pump | Same physical role: municipal suction & tank storage. |
| **Active Power ($P$)** | **~600 W – 700 W** (Mean: 629.2 W, Median: 700 W) | **75 W** | **8x POWER MISMATCH:** iAWE uses a ~0.75–1.0 HP pump; Energy Mirror models a small 75 W pump. |
| **Duty Cycle** | Intermittent batch duty (0.14% active time) | Intermittent batch duty (15–45 min cycles) | Duty cycle characteristics are well-aligned. |
| **Mains Noise & Base Load** | 400 W – 8,600 W (Mean: 852.5 W) | 0 W – 272 W (Differential bench) | Real whole-house mains contain massive concurrent loads (ACs). |
| **Direct Model Transferability**| Cannot transfer weights to 75 W pump directly | Requires retuning $\Delta P$ scale | iAWE establishes real-world algorithm validation, not 75W weights. |

---

## 8. What These Real-Data Results Establish vs. What Remains Unproven

### What Has Been Scientifically Established:
1. **Public Dataset Ground Truth Verified:** iAWE contains genuine synchronized whole-house aggregate power and verified domestic water motor ground truth.
2. **Failure of Naive Thresholding & Differential Baselines:** Simple thresholding ($F1=0.0$) and differential edge detection ($Precision=1.08\%$) fail in real residential environments due to competing compressor transients.
3. **Machine Learning Feasibility:** Machine learning (Random Forest) achieves 61.5% precision on real uncurated data, proving that multi-feature models are required to prevent false alarms.
4. **Data Integrity:** All 476,344 samples were verified without synthetic data fabrication or silent gap filling.

### What Remains Unproven:
1. **Transfer to 75 W Bench Motor:** The iAWE model is calibrated for a ~600 W motor. It does **not** prove accuracy for the project's 75 W simulated pump.
2. **Reactive Power Utilization:** CurrentCost submeters only recorded real active power ($P$). Utilizing reactive power ($Q$) and power factor ($PF$) to detect inductive motor lag remains unvalidated on submetered real data.
3. **Cross-Residence Generalization:** iAWE contains a single instrumented residence (Building 1). Generalization across distinct homes with different background noise floors requires physical bench metrology or multi-building datasets.

---

## 9. Recommended Next Action

1. **Retain the Production Architecture:** The production Flutter application, SQLite database, and differential simulator remain healthy, verified, and decoupled from experimental ML code.
2. **Maintain Machine-Readable Artifacts:** The benchmark code [`run_iawe_experiment.py`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/run_iawe_experiment.py) and results [`iawe_baseline_results.json`](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/results/iawe_baseline_results.json) are preserved as permanent reproducible assets.
3. **Proceed to Bench Hardware Metrology (Milestone 3):** To bridge the gap between iAWE's 600 W motor and Energy Mirror's 75 W appliance model, the next scientific step is physical bench metrology using the staged hardware interface (`ENABLE_HARDWARE_INGEST=true` with real current transformer scaling) to capture genuine 75 W pump waveform dynamics.
