# Energy Mirror: Low-Power Appliance Feasibility Study (Milestone 2C.4)

**Document Reference:** `LOW_POWER_FEASIBILITY_REPORT.md`  
**Milestone:** 2C.4 — Low-Power Appliance Feasibility  
**Reference Checkpoint:** `e9023f8`  
**Date:** October 2026  
**Status:** Experimental Feasibility Study Completed — Controlled Synthetic Stress Testing & Multi-Model Benchmarking  

---

## Executive Summary & Direct Answers to the 6 Research Questions

This experimental feasibility study investigates whether whole-house aggregate electrical measurements (active power $P$, reactive power $Q$, and power factor $PF$) can reliably detect and distinguish low-power domestic appliance activity:
1. **12 W LED Bulb** (`bulb_01` — lighting)
2. **45 W Ceiling Fan** (`fan_01` — fractional induction motor)
3. **75 W Water Pump** (`pump_01` — small domestic booster pump)

amid realistic residential background baselines, measurement noise, refrigerator compressor cycling, and concurrent appliance switching.

### Research Question 1: Can a 12 W LED bulb be detected from aggregate active power?
**Scientific Finding: NO. Detection of a 12 W LED bulb from aggregate active power is fundamentally infeasible under realistic residential conditions.**
- **Ideal Laboratory Conditions ($\sigma = 1.5\text{ W}$, zero background distractors):** Differential edge detection achieves an Event $F_1 = 0.933$ with $0.0$ false alarms/hr.
- **Realistic Residential Conditions ($\sigma = 6.0\text{ W}$, refrigerator cycles, baseline drift):** Differential edge detection and rule-based detectors experience **catastrophic failure**, triggering **36.9 false alarms per hour** (885 false alarms per day) with an Event $F_1 = 0.018$ and Event Precision of $0.9\%$.
- **Physical Root Cause:** The Signal-to-Noise Ratio is $\text{SNR} = \frac{12\text{ W}}{6\text{ W}} = 2.0$. In a standard normal distribution, a 2-sigma fluctuation is $\pm 12\text{ W}$. In 14,400 daily telemetry readings, thousands of ordinary baseline fluctuations breach the configured $[8, 16]\text{ W}$ detection envelope. Without high-frequency waveform harmonic capture, a 12 W LED bulb is mathematically indistinguishable from thermal and sensor noise.

### Research Question 2: Can a 45 W fan be distinguished from background variation?
**Scientific Finding: CONDITIONALLY FEASIBLE under low-contention conditions, but FAILS under concurrent switching and competing loads.**
- **Scenario 1 (Ideal $\sigma = 1.5\text{ W}$):** Event $F_1 = 1.000$, FA/hr = $0.0$.
- **Scenario 2 (Realistic Residential $\sigma = 6.0\text{ W}$):** Differential Step and Rule-Based Event $F_1 = 0.857$, FA/hr = $0.0$ (`FEASIBLE_SYNTHETIC`).
- **Scenario 3 (Adverse Concurrent Switching & Distractors):** Event $F_1$ collapses to **$0.216$** and false alarms rise to **$1.2\text{ FA/hr}$** (`NOT_FEASIBLE`).
- **Physical Root Cause:** Competing domestic loads of identical magnitude—specifically 45–65 W laptop chargers, monitors, and television backlight modulations (20–50 W)—create indistinguishable step transitions. Furthermore, when a 12 W bulb turns on concurrently with another device, composite step transitions alias directly into the fan envelope $[38, 52]\text{ W}$.

### Research Question 3: Can a 75 W pump be distinguished from other household switching events?
**Scientific Finding: FEASIBLE for edge detection under moderate noise, but requires reactive power context to prevent motor/compressor ambiguity.**
- **Scenario 1 (Ideal):** Event $F_1 = 1.000$, FA/hr = $0.0$.
- **Scenario 2 (Realistic Residential):** Differential Step and Rule-Based Event $F_1 = 0.800$, FA/hr = $0.0$ (`FEASIBLE_SYNTHETIC`).
- **Scenario 4 (Missing Telemetry & Jitter):** Differential Step Event $F_1 = 0.800$, FA/hr = $0.0$ (`FEASIBLE_SYNTHETIC`).
- **Scenario 3 (Adverse Concurrent Switching):** Event $F_1$ drops to **$0.400$** due to collision with refrigerator compressor transitions ($180\text{ W}$) and multi-load switching.
- **Physical Root Cause:** The 75 W step provides an adequate active-power SNR ($75 / 6 = 12.5$). However, because fractional pumps draw significant inductive current ($PF \approx 0.78, Q \approx 60\text{ VAR}$), separating them from purely resistive or switch-mode steps requires reactive power metrology.

### Research Question 4: How do simultaneous appliance changes affect detection?
**Scientific Finding: Simultaneous appliance transitions cause complete event loss and state corruption for edge detectors.**
- When a 12 W bulb and a 45 W fan turn on within the same 6-second sampling window, the observed aggregate transition is $\Delta P = +57\text{ W}$.
- In the production rule-based envelope architecture:
  - Fan envelope: $[38, 52]\text{ W}$
  - Pump envelope: $[66, 84]\text{ W}$
- The composite step $+57\text{ W}$ falls into the uncalibrated deadband and is classified as `AMBIGUOUS / UNRECOGNIZED`.
- Both appliance onsets are missed ($\text{FN} = 2$). When the bulb subsequently turns off, the single-appliance $-12\text{ W}$ offset is detected, resulting in an orphan shutdown event.

### Research Question 5: Does adding reactive power or power factor improve discrimination when those measurements genuinely exist?
**Scientific Finding: YES for inductive motor loads (pump), but NO for the 12 W LED bulb.**
- In Random Forest classification:
  - **75 W Water Pump:** Moving from Ablation A (Active only) to Ablation C (Active + Reactive + PF) increases Event $F_1$ from **$0.087$ to $0.750$** in Scenario 1, and from **$0.000$ to $0.500$** in Scenario 2. The inductive signature ($Q \approx 60\text{ VAR}$) effectively separates the pump from resistive and switch-mode electronics.
  - **12 W LED Bulb:** Moving from Ablation A to Ablation C does **NOT** improve bulb detection (Event $F_1$ remains $< 0.09$ in all realistic scenarios). Why? The bulb's reactive power is tiny ($Q \approx 7.4\text{ VAR}$), which is equally drowned by reactive measurement noise ($\sigma_Q = 6\text{ VAR}$).
- **Cautionary Metrology Note:** In this synthetic experiment, power factor was modeled under ideal sinusoidal phasor assumptions ($S = \sqrt{P^2 + Q^2}, PF = P/S$). In real homes, low-power LED drivers produce severe harmonic current distortion ($THD_i > 80\%$) rather than fundamental displacement reactive power. True real-world separation requires harmonic current metrology, not 50 Hz displacement PF.

### Research Question 6: Which conditions make detection unreliable or fundamentally ambiguous?
1. **Measurement Noise Floor $\sigma \ge 4.0\text{ W}$:** Guarantees failure for 12 W loads ($\text{SNR} \le 3.0$).
2. **Competing Electronic Distractors of Similar Magnitude:** 45–65 W laptop chargers, TVs, and monitors alias directly into the 45 W fan envelope.
3. **Multi-Appliance Concurrent Switching:** Simultaneous onsets create composite $\Delta P$ steps that bypass single-appliance tolerance envelopes.
4. **Telemetry Drops and Sampling Jitter:** Missing packets during an edge transition leave differential and rule-based detectors permanently desynchronized.
5. **Slow Baseline Drift:** Renders static power thresholds completely useless ($F_1 < 0.28$).

---

## 1. Experimental Methodology & Controlled Synthetic Design

### Strict Separation of Simulator and Detection Pipelines
To prevent methodological leakage:
1. **Label Isolation:** The synthetic generator produces two separate DataFrames:
   - `telemetry_df`: Contains strictly observable mains telemetry: `timestamp`, `active_power_w`, `reactive_power_var`, `power_factor`.
   - `ground_truth_df`: Contains internal appliance binary states (`bulb_01`, `fan_01`, `pump_01`, `heater_01`).
   - Feature extractors and detectors receive **only** `telemetry_df`. Ground-truth labels are never provided as inference features.
2. **Split Isolation (Zero Temporal Leakage):**
   - Data is partitioned by **independent 24-hour simulation runs** (14,400 samples at 6s resolution per run):
     - **Training Set:** Runs 0, 1, 2 (72 hours = 43,200 samples)
     - **Validation Set:** Run 3 (24 hours = 14,400 samples)
     - **Held-Out Test Set:** Run 4 (24 hours = 14,400 samples)
   - Because each run is an independent daily simulation with separate random seed progressions, there is zero lookback buffer overlap or leakage between splits.
3. **Reproducibility:** Fixed random seed `seed = 42` for all NumPy and scikit-learn operations.

### Physical Appliance & Distractor Specifications

| Appliance / Load | Identifier | Nominal Active Power ($P$) | Tolerance Envelope | Power Factor ($PF$) | Reactive Power ($Q$) | Typical Cycle Duration |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **LED Bulb** | `bulb_01` | **12.0 W** | $[8.0, 16.0]\text{ W}$ | 0.85 (capacitive/distorted) | $7.4\text{ VAR}$ | 2 to 45 min (8 cycles/day) |
| **Ceiling Fan** | `fan_01` | **45.0 W** | $[38.0, 52.0]\text{ W}$ | 0.91 (motor/inductive) | $20.5\text{ VAR}$ | 20 to 180 min (4 cycles/day) |
| **Water Pump** | `pump_01` | **75.0 W** | $[66.0, 84.0]\text{ W}$ | 0.78 (motor/inductive) | $60.2\text{ VAR}$ | 5 to 25 min (3 cycles/day) |
| **Water Heater** | `heater_01` | **140.0 W** | $[128.0, 152.0]\text{ W}$ | 0.99 (resistive) | $19.9\text{ VAR}$ | 15 to 35 min (2 cycles/day) |
| **Refrigerator** | `refrigerator` | 180.0 W | — | 0.75 (compressor motor) | $158.8\text{ VAR}$ | 20 min ON / 25 min OFF |
| **Laptop Charger** | `laptop_charger`| 50.0 W | — | 0.95 (active PFC SMPS) | $16.4\text{ VAR}$ | 30 to 120 min |
| **TV / Display** | `tv_entertainment`| 25.0 W | — | 0.92 (SMPS) | $10.6\text{ VAR}$ | 45 to 180 min |
| **Baseline Load** | `baseline` | 150–800 W (drift) | — | 0.92 (mixed domestic) | $P \times 0.426\text{ VAR}$ | Continuous diurnal drift |

---

## 2. Tested Stress Scenarios

1. **Scenario 1: Ideal / Low Noise ("Laboratory Benchmark")**
   - Noise floor: Gaussian $\sigma = 1.5\text{ W}$, ADC quantization: 0.1 W.
   - Baseline load: 120–250 W.
   - Scheduling: Perfectly non-overlapping events (safe intervals between appliance switching).
   - Distractors: None.
   - Purpose: Establish theoretical upper-bound performance under near-perfect metrology.

2. **Scenario 2: Realistic Residential ("Typical Background")**
   - Noise floor: Gaussian $\sigma = 6.0\text{ W}$, ADC quantization: 1.0 W.
   - Baseline load: 150–750 W diurnal curve with random-walk drift.
   - Cyclic loads: 180 W refrigerator cycling ON for 20 min every 45 min.
   - Scheduling: Independent Poisson/Markov appliance scheduling with natural overlaps.
   - Purpose: Evaluate performance under normal Indian domestic electrical conditions.

3. **Scenario 3: Adverse Concurrent Switching ("High Contention & Competing Loads")**
   - Noise floor: Gaussian $\sigma = 10.0\text{ W}$, ADC quantization: 1.0 W.
   - Baseline load: 200–1100 W diurnal baseline.
   - Competing distractors: Refrigerator (180 W), Laptop charger (50 W), TV (25 W), Water heater (140 W).
   - High Concurrency: Forced simultaneous onsets where bulb or fan transitions at the exact same second as other loads.
   - Purpose: Test behavior when step sizes collide and multi-load switching occurs.

4. **Scenario 4: Missing Data & Sampling Jitter ("Real-World Telemetry Degradation")**
   - Realistic residential conditions ($\sigma = 6.0\text{ W}$, fridge cycles).
   - Packet drops: 5% random telemetry loss.
   - Sampling jitter: Sample intervals varying between 3s and 12s, resampled to 6s grid with forward-fill.
   - Purpose: Measure sensitivity of differential edge detectors to dropped edge transitions.

---

## 3. Evaluated Detection Methods

1. **Static Aggregate Power Threshold Baseline:** Sweeps power threshold $\theta$ on training set to maximize F1, predicting ON when $P_{\text{agg}, t} \ge \theta$.
2. **Differential Step Baseline:** Monitors step change $\Delta P_t = P_t - P_{t-1}$. Transitions to ON when $\Delta P_t \in [P_{\text{nom}} - tol, P_{\text{nom}} + tol]$ and OFF when $\Delta P_t \in [-P_{\text{nom}} - tol, -P_{\text{nom}} + tol]$.
3. **Production RuleBasedEventDetector:** Directly reuses `app.services.event_detector.RuleBasedEventDetector` without modifying production code. Feeds step transitions $(P_{t-1}, P_t, PF_{t-1}, PF_t)$ and maintains state from `MATCHED` events.
4. **Random Forest Classifier (Ablations A, B, C):**
   - Trained on 43,200 samples (3 days), tuned threshold on validation set (1 day), tested on held-out test set (1 day).
   - Uses 3-sample median filter debouncing ($\text{kernel\_size} = 3$) to prevent single-sample chatter.
   - **Ablation A:** Active power only ($P_t$).
   - **Ablation B:** Active power + temporal features ($P_t, \Delta P_t$, rolling mean, std, min, max over 5 samples = 30s).
   - **Ablation C:** Active power + temporal + Reactive power ($Q_t, \Delta Q_t$, rolling stats) + Power factor ($PF_t, \Delta PF_t$, rolling stats).

---

## 4. Comprehensive Experimental Results

### Acceptance Criteria & Research Target
- **Proposed Research Target:** Event $F_1 \ge 0.80$ with False Alarms $\le 1.0\text{ FA/hour}$ ($\le 24\text{ FA/day}$).
- **Classification Categories:**
  - `FEASIBLE_SYNTHETIC`: Event $F_1 \ge 0.80$ and $\text{FA/hour} \le 1.0$.
  - `INCONCLUSIVE`: Event $F_1 \in [0.50, 0.80)$ or borderline false alarms.
  - `NOT_FEASIBLE`: Event $F_1 < 0.50$ or $\text{FA/hour} > 1.0$.

---

### Scenario 1: Ideal / Low Noise ($\sigma = 1.5\text{ W}$, No Distractors, Non-Overlapping)

| Appliance | Method | Sample Acc | Sample Prec | Sample Rec | Sample F1 | Event Prec | Event Rec | Event F1 | Event FA/hr | Feasibility Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **12 W Bulb** | Threshold | 0.3844 | 0.1732 | 0.9483 | 0.2929 | 0.0435 | 1.0000 | 0.0833 | 0.62 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9992** | **0.9958** | **0.9984** | **0.9971** | **0.8750** | **1.0000** | **0.9333** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **0.9992** | **0.9958** | **0.9984** | **0.9971** | **0.8750** | **1.0000** | **0.9333** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.8719 | 0.2195 | 0.1770 | 0.1958 | 0.0385 | 0.1429 | 0.0381 | 3.92 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.8653 | 0.2014 | 0.1809 | 0.1906 | 0.0267 | 0.1429 | 0.0276 | 5.46 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8427 | 0.1764 | 0.2058 | 0.1899 | 0.0380 | 0.2857 | 0.0494 | 6.33 | `NOT_FEASIBLE` |
| **45 W Fan** | Threshold | 0.4429 | 0.1485 | 0.7601 | 0.2484 | 0.0323 | 0.7500 | 0.0612 | 1.25 | `NOT_FEASIBLE` |
| | **Diff Step** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.8682 | 0.2427 | 0.2372 | 0.2399 | 0.0270 | 0.2500 | 0.0396 | 6.00 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.8354 | 0.2114 | 0.2530 | 0.2303 | 0.0206 | 0.2500 | 0.0308 | 7.71 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8421 | 0.2227 | 0.2547 | 0.2376 | 0.0230 | 0.2500 | 0.0342 | 7.17 | `NOT_FEASIBLE` |
| **75 W Pump** | Threshold | 0.9419 | 0.4394 | 0.7061 | 0.5414 | 0.5000 | 1.0000 | 0.6667 | 0.04 | `INCONCLUSIVE` |
| | **Diff Step** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.9413 | 0.3551 | 0.3014 | 0.3261 | 0.0667 | 0.3333 | 0.0870 | 0.79 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.9317 | 0.3168 | 0.3473 | 0.3314 | 0.0811 | 0.6667 | 0.1081 | 1.25 | `NOT_FEASIBLE` |
| | **RF (Abl C)** | **0.9992** | **0.9934** | **0.9855** | **0.9894** | **1.0000** | **0.6667** | **0.7500** | **0.04** | **INCONCLUSIVE** |

---

### Scenario 2: Realistic Residential ($\sigma = 6.0\text{ W}$, Refrigerator Cycles, Baseline Drift)

| Appliance | Method | Sample Acc | Sample Prec | Sample Rec | Sample F1 | Event Prec | Event Rec | Event F1 | Event FA/hr | Feasibility Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **12 W Bulb** | Threshold | 0.8710 | 0.1472 | 0.2078 | 0.1724 | 0.0645 | 0.2500 | 0.1000 | 0.46 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.6617** | **0.0898** | **0.4284** | **0.1485** | **0.0091** | **0.5000** | **0.0178** | **36.88** | **NOT_FEASIBLE (CATASTROPHIC)** |
| | **Rule-Based** | **0.6617** | **0.0898** | **0.4284** | **0.1485** | **0.0091** | **0.5000** | **0.0178** | **36.88** | **NOT_FEASIBLE (CATASTROPHIC)** |
| | RF (Abl A) | 0.8529 | 0.1492 | 0.2087 | 0.1740 | 0.0175 | 0.1250 | 0.0286 | 5.21 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.8351 | 0.1652 | 0.2575 | 0.2013 | 0.0294 | 0.2500 | 0.0494 | 6.21 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8242 | 0.1558 | 0.2676 | 0.1969 | 0.0272 | 0.2500 | 0.0460 | 6.67 | `NOT_FEASIBLE` |
| **45 W Fan** | Threshold | 0.8406 | 0.3541 | 0.3364 | 0.3450 | 0.1905 | 0.4444 | 0.2667 | 0.42 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9984** | **0.9859** | **0.9995** | **0.9926** | **0.7500** | **1.0000** | **0.8571** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **0.9984** | **0.9859** | **0.9995** | **0.9926** | **0.7500** | **1.0000** | **0.8571** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.7483 | 0.2606 | 0.3524 | 0.2996 | 0.0163 | 0.3333 | 0.0286 | 11.00 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.7963 | 0.2878 | 0.3484 | 0.3152 | 0.0227 | 0.3333 | 0.0380 | 8.54 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8037 | 0.3013 | 0.3468 | 0.3225 | 0.0246 | 0.3333 | 0.0408 | 7.79 | `NOT_FEASIBLE` |
| **75 W Pump** | Threshold | 0.9004 | 0.0896 | 0.2520 | 0.1322 | 0.0345 | 0.1429 | 0.0541 | 1.38 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9986** | **0.9575** | **0.9980** | **0.9773** | **0.7000** | **1.0000** | **0.8000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **0.9986** | **0.9575** | **0.9980** | **0.9773** | **0.7000** | **1.0000** | **0.8000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.9536 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.62 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.9407 | 0.1242 | 0.1600 | 0.1399 | 0.0800 | 0.2857 | 0.1250 | 1.08 | `NOT_FEASIBLE` |
| | **RF (Abl C)** | **0.9904** | **0.6974** | **0.5400** | **0.6087** | **0.6000** | **0.4286** | **0.5000** | **0.17** | **INCONCLUSIVE** |

---

### Scenario 3: Adverse Concurrent Switching ($\sigma = 10.0\text{ W}$, Laptop Chargers, TVs, Simultaneous Transitions)

| Appliance | Method | Sample Acc | Sample Prec | Sample Rec | Sample F1 | Event Prec | Event Rec | Event F1 | Event FA/hr | Feasibility Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **12 W Bulb** | Threshold | 0.8413 | 0.1472 | 0.2312 | 0.1799 | 0.0769 | 0.2500 | 0.1176 | 0.92 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.6692** | **0.0988** | **0.4639** | **0.1629** | **0.0113** | **0.6250** | **0.0221** | **36.58** | **NOT_FEASIBLE (CATASTROPHIC)** |
| | **Rule-Based** | **0.6692** | **0.0988** | **0.4639** | **0.1629** | **0.0113** | **0.6250** | **0.0221** | **36.58** | **NOT_FEASIBLE (CATASTROPHIC)** |
| | RF (Abl A) | 0.8126 | 0.1424 | 0.2605 | 0.1841 | 0.0202 | 0.2500 | 0.0343 | 9.25 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.8353 | 0.1738 | 0.2647 | 0.2097 | 0.0305 | 0.2500 | 0.0522 | 7.38 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8524 | 0.1796 | 0.2458 | 0.2076 | 0.0309 | 0.2500 | 0.0488 | 6.21 | `NOT_FEASIBLE` |
| **45 W Fan** | Threshold | 0.8465 | 0.3541 | 0.3117 | 0.3315 | 0.2143 | 0.3750 | 0.2727 | 0.58 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9026** | **0.4709** | **0.4286** | **0.4487** | **0.1364** | **0.5000** | **0.2162** | **1.21** | **NOT_FEASIBLE (COLLAPSE)** |
| | **Rule-Based** | **0.9026** | **0.4709** | **0.4286** | **0.4487** | **0.1364** | **0.5000** | **0.2162** | **1.21** | **NOT_FEASIBLE (COLLAPSE)** |
| | RF (Abl A) | 0.7410 | 0.2679 | 0.3725 | 0.3117 | 0.0163 | 0.3750 | 0.0294 | 11.21 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.7766 | 0.2854 | 0.3584 | 0.3178 | 0.0205 | 0.3750 | 0.0353 | 9.33 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8340 | 0.3551 | 0.3364 | 0.3455 | 0.0361 | 0.3750 | 0.0526 | 5.88 | `NOT_FEASIBLE` |
| **75 W Pump** | Threshold | 0.9416 | 0.1118 | 0.1800 | 0.1379 | 0.0625 | 0.2000 | 0.0952 | 0.71 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9856** | **0.8033** | **0.2940** | **0.4306** | **0.6667** | **0.4000** | **0.4000** | **0.00** | **NOT_FEASIBLE (COLLAPSE)** |
| | **Rule-Based** | **0.9856** | **0.8033** | **0.2940** | **0.4306** | **0.6667** | **0.4000** | **0.4000** | **0.00** | **NOT_FEASIBLE (COLLAPSE)** |
| | RF (Abl A) | 0.9806 | 0.2600 | 0.1300 | 0.1733 | 0.1429 | 0.2000 | 0.1333 | 0.50 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.9631 | 0.1000 | 0.1200 | 0.1091 | 0.0357 | 0.2000 | 0.0556 | 1.25 | `NOT_FEASIBLE` |
| | **RF (Abl C)** | **0.9847** | **0.3793** | **0.2200** | **0.2785** | **0.2500** | **0.2000** | **0.2222** | **0.50** | **NOT_FEASIBLE** |

---

### Scenario 4: Missing Data & Sampling Jitter (5% Dropouts, Resampling Jitter)

| Appliance | Method | Sample Acc | Sample Prec | Sample Rec | Sample F1 | Event Prec | Event Rec | Event F1 | Event FA/hr | Feasibility Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **12 W Bulb** | Threshold | 0.8146 | 0.1558 | 0.3205 | 0.2098 | 0.1163 | 0.4545 | 0.1852 | 1.33 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.7162** | **0.1026** | **0.4397** | **0.1663** | **0.0118** | **0.4545** | **0.0219** | **30.21** | **NOT_FEASIBLE (CATASTROPHIC)** |
| | **Rule-Based** | **0.7162** | **0.1026** | **0.4397** | **0.1663** | **0.0118** | **0.4545** | **0.0219** | **30.21** | **NOT_FEASIBLE (CATASTROPHIC)** |
| | RF (Abl A) | 0.7933 | 0.1472 | 0.3346 | 0.2045 | 0.0336 | 0.3636 | 0.0526 | 10.50 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.8122 | 0.1645 | 0.3423 | 0.2222 | 0.0396 | 0.3636 | 0.0602 | 9.08 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8540 | 0.1895 | 0.2987 | 0.2319 | 0.0625 | 0.3636 | 0.0882 | 5.08 | `NOT_FEASIBLE` |
| **45 W Fan** | Threshold | 0.8127 | 0.3125 | 0.2984 | 0.3053 | 0.1429 | 0.3333 | 0.2000 | 1.00 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9984** | **0.9859** | **0.9995** | **0.9926** | **0.7500** | **1.0000** | **0.8571** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **0.9984** | **0.9859** | **0.9995** | **0.9926** | **0.7500** | **1.0000** | **0.8571** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.7410 | 0.2541 | 0.3548 | 0.2961 | 0.0157 | 0.3333 | 0.0276 | 11.75 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.7877 | 0.2798 | 0.3468 | 0.3097 | 0.0208 | 0.3333 | 0.0351 | 9.08 | `NOT_FEASIBLE` |
| | RF (Abl C) | 0.8037 | 0.2984 | 0.3444 | 0.3197 | 0.0242 | 0.3333 | 0.0400 | 8.08 | `NOT_FEASIBLE` |
| **75 W Pump** | Threshold | 0.9419 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.21 | `NOT_FEASIBLE` |
| | **Diff Step** | **0.9986** | **0.9575** | **0.9980** | **0.9773** | **0.7000** | **1.0000** | **0.8000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | **Rule-Based** | **0.9986** | **0.9575** | **0.9980** | **0.9773** | **0.7000** | **1.0000** | **0.8000** | **0.00** | **FEASIBLE_SYNTHETIC** |
| | RF (Abl A) | 0.9788 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.00 | `NOT_FEASIBLE` |
| | RF (Abl B) | 0.9775 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.12 | `NOT_FEASIBLE` |
| | **RF (Abl C)** | **0.9856** | **0.3125** | **0.2500** | **0.2778** | **0.2500** | **0.2000** | **0.1739** | **0.75** | **NOT_FEASIBLE** |

---

## 5. Comparative Ablation Analysis

| Target Appliance | Ablation A (Active Power $P$) | Ablation B (Active + Temporal $\Delta P$, Stats) | Ablation C (Active + Temporal + Reactive $Q$ + $PF$) | Physical vs Artifactual Insight |
| :--- | :---: | :---: | :---: | :--- |
| **12 W Bulb** | Event $F_1: 0.038$ <br> FA/hr: $3.9$ | Event $F_1: 0.028$ <br> FA/hr: $5.5$ | Event $F_1: 0.049$ <br> FA/hr: $6.3$ | **Zero physical benefit.** Bulb $Q$ ($7.4\text{ VAR}$) is equally submerged in reactive noise. Temporal features cannot rescue an SNR of 2.0. |
| **45 W Fan** | Event $F_1: 0.040$ <br> FA/hr: $6.0$ | Event $F_1: 0.031$ <br> FA/hr: $7.7$ | Event $F_1: 0.034$ <br> FA/hr: $7.2$ | **Negligible benefit.** Fan PF ($0.91$) is too close to general domestic baseline ($0.92$) and laptop chargers ($0.95$). |
| **75 W Pump** | Event $F_1: 0.087$ <br> FA/hr: $0.8$ | Event $F_1: 0.108$ <br> FA/hr: $1.3$ | **Event $F_1: 0.750$** <br> **FA/hr: $0.1$** | **Strong Physical Separation.** Inductive motor phase shift ($PF = 0.78, Q = 60\text{ VAR}$) clearly differentiates pump from resistive loads. |

---

## 6. Synthesis & Feasibility Verdict

| Appliance | Nominal Power | Ideal Low-Noise Feasibility | Realistic Domestic Feasibility | Adverse Contention Feasibility | Overall Scientific Feasibility Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **12 W LED Bulb** | 12.0 W | `FEASIBLE_SYNTHETIC` | **`NOT_FEASIBLE`** | **`NOT_FEASIBLE`** | **NOT RELIABLY DISTINGUISHABLE.** Completely submerged in noise. Over 30 false alarms per hour. |
| **45 W Ceiling Fan** | 45.0 W | `FEASIBLE_SYNTHETIC` | `FEASIBLE_SYNTHETIC` | **`NOT_FEASIBLE`** | **INCONCLUSIVE / HIGHLY VULNERABLE.** Feasible in isolation, but fails under concurrent switching or laptop charger steps. |
| **75 W Water Pump** | 75.0 W | `FEASIBLE_SYNTHETIC` | `FEASIBLE_SYNTHETIC` | **`NOT_FEASIBLE`** | **FEASIBLE WITH REACTIVE METROLOGY.** Distinct active step; requires reactive power ($Q$) to reject competing motor/compressor distractors. |

---

## 7. Limitations & Real-World Validation Requirements

1. **Synthetic vs Real-World Metrology:**
   - Synthetic success in Scenarios 1 and 2 **must never be described as real-world validation**.
   - In synthetic simulations, noise is white Gaussian and power factor follows ideal sinusoidal phasors. In real homes:
     - Voltage sag and mains harmonic distortion ($THD_v$) modulate appliance power consumption dynamically.
     - LED bulbs utilize bridge rectifiers and high-frequency DC-DC converters, generating non-linear current spikes with high $THD_i$ rather than pure displacement reactive power.
2. **iAWE Dataset Boundary:**
   - The approved public iAWE dataset contains a Water Motor of ~600–700 W. As established in Milestone 2C.3, it **does not and cannot validate** the detection of a 75 W pump, 45 W fan, or 12 W bulb.
3. **Controlled Real-World Bench Requirement:**
   - To prove low-power NILM feasibility in physical practice, a physical test bench with calibrated high-speed submetering (ADE9153A, BL0942, or PZEM-004T v3.0) and synchronized ground-truth CTs on dedicated 12 W and 45 W circuits is mandatory before any production claims can be made.
