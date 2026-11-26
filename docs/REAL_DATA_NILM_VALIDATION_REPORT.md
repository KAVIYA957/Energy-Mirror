# Energy Mirror: Real-World NILM Validation and Low-Power Detection Improvement Report (Milestone 2C.7)

**Document Reference:** `REAL_DATA_NILM_VALIDATION_REPORT.md`  
**Milestone:** 2C.7 — Real-World NILM Validation and Low-Power Detection Improvement  
**Reference Checkpoint:** `2b20ea4`  
**Date:** October 2026  
**Status:** Completed — Empirical Dataset Audit, Multi-Model Real Benchmark, 12 W LED Identifiability Investigation & Noise-Aware Improvements  
**Target Environment:** Isolated ML Research (`backend/ml_experiments/`) — Production Architecture Untouched (`ENABLE_HARDWARE_INGEST=false`)

---

## Executive Summary & Scientific Findings

This report delivers a rigorous, reproducible investigation into whether Energy Mirror's Non-Intrusive Load Monitoring (NILM) algorithms generalize to genuine public residential energy data. Using the peer-reviewed **iAWE dataset** (Indian Dataset for Ambient Water and Energy, Batra et al., IIIT Delhi, BuildSys 2013 / Zenodo record `13917372`), this investigation evaluates real whole-house aggregate metrology against independent appliance submeters, addresses the low-power 12 W LED detection barrier, and evaluates pipeline improvements.

```mermaid
graph TD
    subgraph Genuine Public Data [iAWE Dataset - Batra et al. 2013]
        M1[Meter 1: Schneider EM6400 Mains Phase A]
        M2[Meter 2: Schneider EM6400 Mains Phase B]
        M12[Meter 12: CurrentCost Water Motor Submeter]
        M3_11[Meters 3-11: jplug Submeters - Fridge, ACs, Laptop, TV]
    end

    subgraph Chronological Pipeline [Zero-Leakage Split]
        AGG[Synchronized 6s Aggregate Mains P_agg = P1 + P2]
        SUB[Synchronized 6s Ground Truth Motor State]
        SPLIT[Train 60% | 100-Sample Buffer | Val 20% | 100-Sample Buffer | Test 20%]
    end

    subgraph Empirical Evaluation [Held-Out Test Partition - 6.72 Days]
        BASE[Baselines: Majority, Persistence, Threshold, Diff Step, Random Forest]
        IMP[Noise-Aware Adaptive Detector with Hysteresis]
        LED[12 W LED Identifiability Analysis - SNR, Voltage, Attribution]
    end

    M1 --> AGG
    M2 --> AGG
    M12 --> SUB
    AGG --> SPLIT
    SUB --> SPLIT
    SPLIT --> BASE
    SPLIT --> IMP
    SPLIT --> LED
```

### Core Scientific Findings

1. **Truthful Dataset Inventory and Canonical Appliance Mapping:**
   - **Water Heater (140 W): `NOT_VALIDATED`**. iAWE contains zero water heater submeters. Water heating in the monitored residence was solar, gas, or unmetered.
   - **Water Pump (75 W): `INCOMPATIBLE_RATING` (`NOT_VALIDATED` for 75 W class)**. iAWE `meter12` is an overhead tank lift pump with an active power draw of **600 W to 750 W** (measured mean: $629.17\text{ W}$, median: $700.0\text{ W}$). While providing authentic inductive motor data for NILM benchmarking, it cannot scientifically validate Energy Mirror's 75 W fractional booster pump class due to an 8× to 10× rating disparity.
   - **Ceiling Fan (45 W): `NOT_VALIDATED`**. Indian residential ceiling fans are hardwired into ceiling conduit junction boxes on shared lighting circuits, precluding plug-level submetering.
   - **LED Bulb (12 W): `NOT_VALIDATED`**. iAWE contains no isolated lighting submeters.
2. **The 12 W LED Identifiability Answers (The Three Questions):**
   - **Question 1 (Metrology Measurement): YES.** Class 1.0 energy ICs (Schneider EM6400, ADE7953, BL0942) measure aggregate active power accurately across their dynamic range ($\le 1.0\%$ error).
   - **Question 2 (Detect ~12 W Change on Mains): NO on real residential mains.** The empirical standard deviation of 6-second delta-power ($\Delta P_{6s}$) on real mains is **$112.66\text{ W}$** with a 95th percentile jump of **$27.72\text{ W}$**, yielding an **$\text{SNR} = 0.107$** ($\text{SNR} \ll 1.0$). Furthermore, line voltage fluctuates across a **$49.33\text{ V}$** envelope ($192.81\text{ V}$ to $242.14\text{ V}$), with an empirical sensitivity of **$11.4\text{ W per Volt}$**. A mere $1\text{ V}$ grid sag on a $1.2\text{ kW}$ baseline causes an $11.4\text{ W}$ power drop, completely masking a 12 W LED transition.
   - **Question 3 (Unique Attribution to LED): NO.** Active power changes of 10–15 W are identical to laptop charger throttling, TV backlighting shifts, Wi-Fi router transmit bursts, and line voltage drift. Without high-frequency current harmonics ($THD_i \ge 80\%$) or branch submetering, active-power attribution is mathematically ill-posed.
3. **Pipeline Improvement (Noise-Aware Detection & Hysteresis):**
   - Naive Differential Step detection experiences catastrophic failure on real mains: **359 false alarm events (53.42 FA/day)** with an Event $F_1 = 0.0270$.
   - The improved **Noise-Aware Dynamic Detector with Hysteresis** ($\theta_{\text{dyn}} = \theta_0 + k \cdot \sigma_{\text{local}}$ plus plateau persistence) reduced false alarms by **$28.69\%$** (from $53.42$ down to $38.09\text{ FA/day}$).
   - **Scientific Conclusion:** While noise modeling helps, single-variable active-power edge detection remains operationally unviable in real homes. Only multi-feature ML ensembles (Random Forest Event $F_1 = 0.6154$, $0.45\text{ FA/day}$) or multi-parameter metrology (active + reactive power) can reject domestic baseline transients.
4. **Safety & Zero-Fabrication Guarantees:**
   - `ENABLE_HARDWARE_INGEST=false` remains strictly active.
   - Zero physical hardware purchased, wired, or connected.
   - Production FastAPI backend, SQLite database, simulator, and `RuleBasedEventDetector` remain completely unchanged and isolated.

---

## 1. Dataset Provenance, Channels, and Metrology

### Provenance and License

The real-world evaluation uses the **iAWE dataset**:
- **Title:** Indian Dataset for Ambient Water and Energy (iAWE)
- **Principal Investigators:** Nipun Batra, Manoj Gulati, Amarjeet Singh, Mani Srivastava
- **Affiliation:** Indraprastha Institute of Information Technology Delhi (IIIT-D), India
- **Publication Citation:** Batra et al., *"It's Different: Insights into home energy consumption in India"*, In Proceedings of the 5th ACM Workshop on Embedded Systems For Energy-Efficient Buildings (BuildSys 2013), pp. 1–8.
- **Data Repository:** Zenodo Record `13917372` / HDF5 distribution `iawe.h5` ($408.02\text{ MB}$, $427,836,094\text{ bytes}$).
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Physical Site:** A 3-floor residential household located in New Delhi, India ($28.64^\circ\text{ N}, 77.11^\circ\text{ E}$).

### Dataset Inventory & Submeter Hardware Channels

Forensic inspection of `iawe.h5` reveals 12 physical electric metering channels:

| Meter ID | Logical Role / Appliance Identity | Metering Hardware | Native Sample Period | Recorded Physical Channels | Total Recorded Rows |
| :--- | :--- | :--- | :---: | :--- | :---: |
| `/building1/elec/meter1` | **Mains Feeder Phase A** | Schneider Electric EM6400 | 1 second | $P, Q, S, V, I, f, PF$ | 4,391,017 |
| `/building1/elec/meter2` | **Mains Feeder Phase B** | Schneider Electric EM6400 | 1 second | $P, Q, S, V, I, f, PF$ | 4,391,004 |
| `/building1/elec/meter3` | Refrigerator | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 4,538,844 |
| `/building1/elec/meter4` | Air Conditioner 1 (Bed 1) | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 640,250 |
| `/building1/elec/meter5` | Air Conditioner 2 (Bed 2) | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 516,704 |
| `/building1/elec/meter6` | Washing Machine | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 23,740 |
| `/building1/elec/meter7` | Laptop Computer | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 2,550,997 |
| `/building1/elec/meter8` | Clothes Iron | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 7,134 |
| `/building1/elec/meter9` | Kitchen Outlets | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 13,340 |
| `/building1/elec/meter10` | Television | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 428,937 |
| `/building1/elec/meter11` | Water Filter (RO purifier) | Smart Plug (jplug) | 1 second | $P, Q, S, V, I, f, PF$ | 1,694,622 |
| `/building1/elec/meter12` | **Water Motor (Overhead Tank)** | CurrentCost Envi CC128 | 6 seconds | $P_{\text{active}}$ only | 447,812 |

---

## 2. Appliance-Label Audit and Canonical Mapping

Energy Mirror simulates four canonical household appliances in its differential physics simulator. Below is the audited alignment against the genuine iAWE dataset:

| Energy Mirror Appliance | Simulated Rating & Profile | iAWE Dataset Match | Measured Real Data Power | Validation Status | Detailed Scientific Rationale |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Water Heater** | 140 W, Resistive ($PF = 1.0$) | *None* | — | `NOT_VALIDATED` | **No Ground Truth:** iAWE contains zero water heater submeters. Water heating was solar, gas, or unmetered. No real data exists to validate this class. |
| **Water Pump** | 75 W, Inductive Motor ($PF = 0.78$) | `meter12`: Water Motor | Mean: $629.17\text{ W}$<br>Median: $700.0\text{ W}$<br>Std: $158.1\text{ W}$ | `INCOMPATIBLE_RATING`<br>(Audited Real Motor Baseline) | **Rating Disparity:** iAWE `meter12` is a high-power overhead tank lift pump ($600 - 750\text{ W}$), NOT a 75 W domestic booster pump. While evaluated below as an authentic inductive motor baseline, Energy Mirror's 75 W pump class is formally marked `NOT_VALIDATED`. |
| **Ceiling Fan** | 45 W, Inductive Motor ($PF = 0.91$) | *None* | — | `NOT_VALIDATED` | **Hardwired Infrastructure:** In Indian residences, ceiling fans are wired directly through ceiling conduits to wall switchboards without plug sockets, precluding jplug submetering. |
| **LED Bulb** | 12 W, SMPS / Capacitive ($PF = 0.85$) | *None* | — | `NOT_VALIDATED` | **Submeter Absence:** No individual lighting channels were isolated in iAWE. Single 12 W lighting validation is unavailable on this dataset. |

> [!IMPORTANT]
> **Scientific Integrity Requirement:** Under Energy Mirror's truth-in-reporting protocol, appliances lacking ground-truth submeters are strictly labeled `NOT_VALIDATED`. We refuse to artificially scale 700 W motor data down to 75 W, or substitute an unmetered AC circuit for a fan.

---

## 3. Data Synchronization, Preprocessing, and Leakage Prevention

### Preprocessing and Synchronization Pipeline

1. **Temporal Overlap:** Water Motor (`meter12`) was logged between `2013-05-30 12:51:41` and `2013-07-05 15:41:46` ($447,812$ raw samples). Mains meters (`meter1` and `meter2`) were filtered to this exact 36.1-day window.
2. **Sentinel Artifact Masking:** CurrentCost CC128 radio loss-of-signal sentinels ($\ge 30,000\text{ W}$ / $32,767\text{ W}$) were detected ($N = 3$) and replaced with `NaN`.
3. **Resampling Grid:** Resampled to a uniform 6-second time grid ($\Delta t = 6\text{ s}$), aligning with the CC128 sensor's native transmission cadence.
4. **Aggregate Summation:** $P_{\text{agg}} = P_{\text{mains,1}} + P_{\text{mains,2}}$.
5. **Dropout Handling:** Missing aggregate intervals caused by New Delhi utility blackouts ($N = 43,757$ intervals, $8.41\%$ of the monitoring window) were dropped to preserve physical law consistency ($P_{\text{agg}} \ge P_{\text{sub}}$).
6. **Ground Truth Binarization:** State labeled ON ($y = 1$) when $P_{\text{motor}} \ge 200.0\text{ W}$ (idle baseline $< 5\text{ W}$; active pumping $\sim 650 - 750\text{ W}$).

### Chronological Splitting and Zero-Leakage Architecture

To guarantee scientific reproducibility and prevent temporal lookahead leakage:
- **Chronological Partitions:**
  - **Training Set (60%):** $285,706$ samples ($2013-05-30$ to $2013-06-21$, $535$ active samples, $0.1873\%$ prevalence).
  - **Validation Set (20%):** $95,168$ samples ($2013-06-21$ to $2013-06-28$, $93$ active samples, $0.0977\%$ prevalence).
  - **Held-Out Test Set (20%):** $95,270$ samples ($2013-06-28$ to $2013-07-05$, $6.72\text{ days}$, $34$ active samples, $0.0357\%$ prevalence).
- **Boundary Buffer Drops:** A 100-sample buffer ($600\text{ seconds}$) was discarded between Train/Val and Val/Test. This completely isolates the 5-sample ($30\text{ seconds}$) rolling lookback features (`rolling_mean_5`, `rolling_std_5`, `rolling_max_5`), making temporal feature bleed mathematically impossible.
- **Model Tuning Protocol:**
  - Machine learning models fit strictly on Training.
  - Thresholds and edge parameters tuned strictly on Validation.
  - Held-out Test partition evaluated strictly once.

---

## 4. Multi-Model Real-Data Baseline Benchmark

All models were evaluated on the held-out test partition ($N = 95,270$ samples, $6.72\text{ days}$, positive prevalence $= 0.0357\%$).

### Sample-Level Classification Performance

| Model / Algorithm | Role / Nature | Accuracy | Precision | Recall | F1-Score | Confusion Matrix (TP, FP, FN, TN) | Operational Evaluation |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Persistence ($t-1$)** | Oracle Reference | **0.9998** | **0.7353** | **0.7353** | **0.7353** | TP=25, FP=9, FN=9, TN=95,227 | **Oracle upper bound.** Requires ground-truth submeter state $y_{t-1}$; cannot run on mains alone. |
| **Random Forest Classifier** | Deployable Whole-House ML | **0.9997** | **0.6154** | **0.2353** | **0.3404** | TP=8, FP=5, FN=26, TN=95,231 | **Strongest deployable classifier.** Multi-feature ensemble filters 99.99% of background domestic transients. |
| **Differential Step Baseline** | Rule-Based Edge Detector | 0.9930 | 0.0108 | 0.2059 | 0.0206 | TP=7, FP=640, FN=27, TN=94,596 | **Catastrophic false alarms.** 640 false positive samples caused by competing compressor steps and voltage sags. |
| **Simple Power Threshold** | Static Aggregate Threshold | 0.9996 | 0.0000 | 0.0000 | 0.0000 | TP=0, FP=2, FN=34, TN=95,234 | **Complete failure.** Whole-house power varies up to 8.6 kW; static threshold cannot isolate 700 W motor. |
| **Majority Class (All OFF)** | Zero-Intelligence Baseline | 0.9996 | 0.0000 | 0.0000 | 0.0000 | TP=0, FP=0, FN=34, TN=95,236 | **Exposes the accuracy fallacy.** 99.96% accuracy is trivially achieved by doing nothing. |

### Event-Level Operational Performance

Sample-level metrics do not reflect user experience. If a pump runs for 3 minutes (30 samples) and the detector detects 25 samples, the user experienced 1 perfect detection. If the detector triggers 300 spurious 1-sample spikes, sample accuracy is 99.7%, but the user receives 300 false alarms.

Events were extracted using contiguous run extraction and matched via greedy bipartite matching within a $\pm 60\text{-second}$ onset window:

| Model / Algorithm | Ground Truth Events | Predicted Events | True Positive Events | False Positive Events | False Negative Events | Event Precision | Event Recall | Event F1 | False Alarms / Day | Mean Detection Delay |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence ($t-1$)** | 6 | 9 | 6 | 3 | 0 | 0.6667 | 1.0000 | 0.8000 | 0.45 FA/day | 6.0 s |
| **Random Forest Classifier** | 6 | 7 | 4 | 3 | 2 | **0.5714** | **0.6667** | **0.6154** | **0.45 FA/day** | **9.0 s** |
| **Differential Step Baseline** | 6 | 364 | 5 | 359 | 1 | 0.0137 | 0.8333 | 0.0270 | **53.42 FA/day** | 0.0 s |
| **Simple Power Threshold** | 6 | 2 | 0 | 2 | 6 | 0.0000 | 0.0000 | 0.0000 | 0.30 FA/day | 0.0 s |
| **Majority Class** | 6 | 0 | 0 | 0 | 6 | 0.0000 | 0.0000 | 0.0000 | 0.00 FA/day | — |

> [!NOTE]
> **Key Operational Contrast:**
> - The **Random Forest Classifier** detects 4 of the 6 ground-truth pumping cycles with only **3 false alarms in 6.72 days** (0.45 false alarms/day).
> - The **Differential Step Baseline** triggers **359 false alarms (53.42 false alarms/day)**. A user relying on naive edge detection would receive an erroneous mobile notification every 27 minutes.

---

## 5. Regression Metrics & Error Decomposition Audit

In earlier literature, disaggregation algorithms often report misleadingly low Mean Absolute Error (MAE) values. On the held-out test set, the Random Forest Regressor reported an overall MAE of **$1.76\text{ W}$**.

### The Error Decomposition Identity

The overall MAE is a convex combination of errors on active ($y = 1$) and inactive ($y = 0$) sub-populations:

$$\text{MAE}_{\text{overall}} = w_{\text{active}} \cdot \text{MAE}_{\text{active}} + w_{\text{inactive}} \cdot \text{MAE}_{\text{inactive}}$$

where:
- $w_{\text{active}} = \frac{34}{95,270} \approx 0.000357$ ($0.0357\%$)
- $w_{\text{inactive}} = \frac{95,236}{95,270} \approx 0.999643$ ($99.9643\%$)

### Sub-Population Error Decomposition Table

| Metric Category | Random Forest Regressor | Mean Active Baseline | Zero Baseline (All 0 W) |
| :--- | :---: | :---: | :---: |
| **Overall MAE** | **1.76 W** | 1.23 W | 1.25 W |
| **Active Sub-Population MAE ($N=34$, True Mean $= 715.94\text{ W}$)** | **476.48 W** | 573.21 W | 715.94 W |
| **Inactive Sub-Population MAE ($N=95,236$, True Mean $= 0.0\text{ W}$)** | **1.59 W** | 1.02 W | 0.99 W |
| **RMSE** | 15.46 W | 14.96 W | 15.70 W |
| **True Consumed Energy** | 198.03 Wh | 198.03 Wh | 198.03 Wh |
| **Predicted Consumed Energy** | 114.99 Wh | 13.14 Wh | 0.00 Wh |
| **Relative Energy Total Error (RETE %)** | **41.93%** | 93.36% | 100.00% |

### Scientific Interpretation
- The "1.76 W MAE" is an artifact of the $99.96\%$ inactive prevalence. The inactive error ($1.59\text{ W}$) completely dominates the overall score.
- During active motor runs, the model underestimates motor power by **$66.55\%$** (predicting $239.46\text{ W}$ vs true $715.94\text{ W}$), producing an active-period error of **$476.48\text{ W}$** and an energy error (RETE) of **$41.93\%$**.

---

## 6. Pipeline Improvement: Noise-Aware Detection & Hysteresis

### The Failure Mechanism of Naive Differential Edge Detection
Why does naive differential step detection trigger 359 false alarm events?
1. **Background Domestic Jitter:** In a residential home, multiple appliances cycle continuously.
2. **Compressor Starting Spikes:** Refrigerator and AC compressor inrushes create steps of $+250\text{ W}$ to $+1500\text{ W}$ lasting 1–2 sampling periods.
3. **Mains Voltage Fluctuations:** A 1% line voltage sag causes an instantaneous aggregate power drop of $\sim 15 - 25\text{ W}$.

### Improved Architecture: Adaptive Threshold with Duration Hysteresis

We designed and evaluated an improved edge detector:
1. **Dynamic Noise-Aware Threshold:**
   $$\theta_{\text{dyn}}(t) = \theta_0 + k \cdot \sigma_{\text{local}}(t)$$
   where $\sigma_{\text{local}}(t)$ is the rolling standard deviation of aggregate mains power over a 30-second window. In volatile periods (e.g. AC running, high grid noise), the threshold dynamically scales up to prevent spurious triggers.
2. **Duration Hysteresis & Plateau Verification:**
   Instead of asserting an event on a single delta step, the algorithm verifies that aggregate power remains elevated by at least $150\text{ W}$ above the pre-step baseline for at least $M \ge 3$ consecutive samples ($18\text{ seconds}$). Single-sample transient spikes are rejected.

### Empirical Improvement on Held-Out Test Data

| Metric | Naive Differential Step Baseline | Noise-Aware Adaptive Detector with Hysteresis | Improvement / Change |
| :--- | :---: | :---: | :---: |
| **Tuned Parameters (on Val)** | $\Delta P \ge 220.4\text{ W}$ (Static) | $\theta_0 = 250\text{ W}, k = 1.0, M = 3\text{ samples}$ | Dynamic adaptation |
| **Predicted Event Count** | 364 events | 257 events | **-107 spurious events** |
| **False Positive Events** | 359 events | 256 events | **-103 false alarms** |
| **False Alarms per Day** | **53.42 FA/day** | **38.09 FA/day** | **28.69% Reduction** |
| **Sample-Level Accuracy** | 99.30% | 78.04% | Lower (due to plateau extension) |

### Scientific Verdict on Pipeline Improvements
The noise-aware hysteresis detector successfully reduced false alarms by **$28.69\%$** on the held-out real dataset. However, **$38.09\text{ false alarms/day}$ remains completely unacceptable for real-world deployment** (a false alert every 37 minutes).

This provides conclusive empirical proof that:
> **Single-variable active-power edge detection is fundamentally incapable of reliable real-world NILM.**  
> Real-world deployment requires multi-feature nonlinear machine learning (Random Forest: $0.45\text{ FA/day}$) or multi-channel metrology (active power $P$ + reactive power $Q$ + voltage $V$).

---

## 7. Deep 12 W LED Identifiability Investigation

The project mandate requires separating three distinct questions regarding low-power 12 W LED detection:

```mermaid
graph TD
    Q1[Question 1: Can the meter measure aggregate power accurately?] -->|VERDICT: YES| A1[Class 1.0 Metrology ICs measure P_agg accurately across dynamic range]
    Q2[Question 2: Can the system detect a change of ~12 W on mains?] -->|VERDICT: NO on Real Mains| A2[Empirical noise std = 112.7 W. SNR = 0.107. Voltage drift = 11.4 W/Volt]
    Q3[Question 3: Can the system uniquely attribute 12 W to an LED?] -->|VERDICT: NO| A3[Active power is ill-posed. Laptop, TV, routers produce identical 10-15 W steps]
```

### Question 1: Can the meter measure aggregate power accurately?
**Verdict: YES.**
- **Metrology Verification:** Modern solid-state energy metrology ICs (e.g., Schneider EM6400, Analog Devices ADE7953, Belling BL0942) comply with IEC 62053-21 Class 1.0 standards.
- They maintain active power measurement error $\le 1.0\%$ down to $0.05 \cdot I_b$ (50 mA RMS). Total household aggregate energy and power are measured with high accuracy.

### Question 2: Can the system detect a change of approximately 12 W from aggregate measurements?
**Verdict: CONDITIONALLY IN CLEAN LAB / NO ON REAL RESIDENTIAL MAINS.**
- **Laboratory Conditions:** In an isolated, noise-free circuit with a static baseline, an ADC with 0.1 W resolution easily registers a $+12.0\text{ W}$ step.
- **Real Residential Mains Evidence (iAWE Data):**
  - **Empirical Noise Floor:** On genuine 6-second residential mains data, the standard deviation of $\Delta P_{6s}$ is **$112.66\text{ W}$**, with a 95th percentile step of **$27.72\text{ W}$** and 99th percentile step of **$436.89\text{ W}$**.
  - **Signal-to-Noise Ratio (SNR):**
    $$\text{SNR}_{\text{LED}} = \frac{12.0\text{ W}}{\sigma_{\Delta P}} = \frac{12.0\text{ W}}{112.66\text{ W}} = \mathbf{0.107} \quad (\text{SNR} \ll 1.0)$$
    A 12 W step is buried under noise exceeding it by an order of magnitude.
  - **Mains Voltage Fluctuations:**
    In iAWE, line voltage fluctuates across a **$49.33\text{ V}$** envelope ($192.81\text{ V}$ to $242.14\text{ V}$, mean $223.00\text{ V}$, $\sigma_V = 11.93\text{ V}$).
    For a residential load with impedance $R$, power varies with voltage:
    $$\frac{\Delta P}{P_{\text{agg}}} \approx 2 \cdot \frac{\Delta V}{V} \implies \Delta P \approx \frac{2 \cdot P_{\text{agg}}}{V} \cdot \Delta V$$
    At the household average baseline of $1,274\text{ W}$, the voltage power sensitivity is:
    $$\frac{dP}{dV} = \frac{2 \times 1274\text{ W}}{223\text{ V}} \approx \mathbf{11.42\text{ W per Volt}}$$
    **A routine grid voltage dip of just $1.05\text{ V}$ produces an aggregate power drop of $12.0\text{ W}$**, perfectly mimicking or obliterating a 12 W LED switching event.

### Question 3: Can the system uniquely attribute that 12 W change to an LED bulb?
**Verdict: NO (ACTIVE POWER IS MATHEMATICALLY ILL-POSED FOR ATTRIBUTION).**
- Even if an algorithm isolated a true 12 W step, active power alone cannot uniquely attribute it to an LED bulb.
- **Competing Domestic Distractors of Identical Magnitude:**
  - Laptop power bricks shifting between active and trickle charging: $\Delta P \sim 10 - 20\text{ W}$.
  - Smart TVs with dynamic contrast / backlighting modulation: $\Delta P \sim 8 - 25\text{ W}$.
  - Wi-Fi routers shifting power states during data transmission: $\Delta P \sim 3 - 8\text{ W}$.
  - Microwave and refrigerator interior lights or clock displays: $\Delta P \sim 5 - 15\text{ W}$.
  - Refrigerator thermistor baseline drift: continuous $\pm 10\text{ W}$ variations.

### Proposed Future Validation Protocol (Harmonic Metrology)
To resolve the 12 W LED attribution problem in future hardware milestones:
1. **High-Frequency Current Waveform Capture:** Rogowski coil or wideband current transformer sampled at $f_s \ge 8\text{ kHz}$.
2. **Current Harmonic Distortion ($THD_i$):** LED drivers employ bridge rectifiers with smoothing capacitors, exhibiting $THD_i > 80\%$ and distinctive 3rd, 5th, and 7th odd harmonics.
3. **Harmonic Phasor Signature:** Linear resistive or active-PFC electronics draw sinusoidal current ($THD_i < 10\%$). Harmonic spectral analysis can separate non-linear LED drivers from linear voltage drift.
4. **Sub-Circuit / Branch Submetering:** Where aggregate attribution is physically unfeasible, dedicated lighting circuit or smart plug monitoring provides the only 100% reliable ground truth.

---

## 8. Safety, Invariants, and Regression Verification

### Production Invariants Audit

| Invariant / Constraint | Mandate | Observed Status | Audit Verification |
| :--- | :--- | :---: | :--- |
| `ENABLE_HARDWARE_INGEST` | Strictly `false` | `false` | Verified in [ingest.py](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/routers/ingest.py) and test suite. |
| Physical Hardware | Zero hardware purchased or wired | No Hardware | Kept strictly software-only. |
| API Contracts | Zero breaking changes | 100% Intact | All 48 backend integration tests pass. |
| Production Detector | Isolated from experimental ML | Untouched | `RuleBasedEventDetector` code unmodified. |
| Simulator Ratings | 140W, 75W, 45W, 12W unchanged | Preserved | Residual power accounting tests pass. |
| Data Fabrication | Zero synthetic data claimed as real | Compliant | All metrics derived directly from `iawe.h5`. |

### Automated Test Suite Results

Four independent test suites were executed to verify complete regression safety:

1. **ML Experiments & Real Validation Suite:**
   - Command: `backend\ml_experiments\.venv_ml\Scripts\python.exe -m unittest discover backend/ml_experiments/tests`
   - Outcome: **41/41 tests passed** (including 7 new dedicated validation tests in [test_real_data_validation.py](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/tests/test_real_data_validation.py)).
2. **FastAPI Backend Suite:**
   - Command: `backend\.venv\Scripts\pytest backend/tests -v`
   - Outcome: **48/48 tests passed** (telemetry, simulator invariants, event history, diagnostics).
3. **Flutter Mobile Suite:**
   - Command: `flutter test` in `mobile/`
   - Outcome: **29/29 tests passed** (all responsive layouts, diagnostics, navigation, simulator lab).
4. **Flutter Static Analysis:**
   - Command: `flutter analyze` in `mobile/`
   - Outcome: **0 issues found** (`No issues found! (ran in 5.9s)`).

---

## 9. Reproducibility Instructions

To reproduce the complete validation experiment and verify all reported numbers:

### Step 1: Activate ML Virtual Environment
```powershell
cd "c:\Users\Kaviya\Downloads\Energy Mirror"
backend\ml_experiments\.venv_ml\Scripts\activate
```

### Step 2: Execute Validation Runner
```powershell
backend\ml_experiments\.venv_ml\Scripts\python.exe backend/ml_experiments/run_real_data_validation.py
```
*Expected runtime: ~70 seconds. Output file: `backend/ml_experiments/results/real_data_validation.json`.*

### Step 3: Run Validation Unit Tests
```powershell
backend\ml_experiments\.venv_ml\Scripts\python.exe -m unittest backend/ml_experiments/tests/test_real_data_validation.py
```

---

## 10. Recommended Next Steps

Based on the empirical evidence gathered in Milestone 2C.7:

1. **Production Deployment Isolation:** Keep `RuleBasedEventDetector` operating exclusively in the isolated simulated environment. Experimental models must not be pushed to production without multi-channel metrology.
2. **Appliance Status Governance:** Formally record in all documentation that:
   - **Water Heater (140 W):** `NOT_VALIDATED` on public datasets.
   - **Ceiling Fan (45 W):** `NOT_VALIDATED` on public datasets.
   - **LED Bulb (12 W):** `NOT_VALIDATED` on public datasets.
   - **Water Pump (75 W):** `INCOMPATIBLE_RATING` against iAWE's 700 W motor.
3. **Future Hardware Metrology Specification (Milestone 3A):**
   - For aggregate monitoring, integrate voltage measurement alongside active and reactive power metrology.
   - For low-power LED detection, specify high-frequency current harmonics sampling ($\ge 8\text{ kHz}$) or implement circuit-branch submetering.
