# Energy Mirror: Public Real-Dataset Experiment & Ground-Truth Integrity Report
**Document ID:** `EM-NILM-PUB-001`  
**Milestone:** Milestone 2C: Download REFIT Data and Run Real-Data NILM Benchmark  
**Status:** Ground-Truth Audit Completed · Stopping Criteria Enforced · Pipeline Validated  
**Date:** October 2026  
**Target Environment:** Isolated ML Research (`backend/ml_experiments/`)

---

## 1. Executive Summary

Milestone 2C sought to download two approved public dataset files from the **REFIT** repository (`CLEAN_House11.csv` and `CLEAN_House12.csv`), inspect their contents, and execute Energy Mirror's first genuine real-world NILM benchmark for motor/pump appliance disaggregation.

In strict adherence to the directive's non-negotiable instructions:
> *"Before training any model, inspect both files and document... Whether the expected pump channel is genuinely present in each house... If either file does not contain the expected ground truth, stop that experiment and explain why."*
> *"If the source is unavailable, the files cannot be isolated safely, or the actual download requirement differs materially from the audit, stop and report the issue rather than downloading additional data."*

A direct inspection of the authoritative REFIT metadata schema (`CLEAN_READ_ME_081116.txt`) published by the creators (David Murray, Lina Stankovic, Vladimir Stankovic) at the University of Strathclyde revealed a critical ground-truth discrepancy:

### Critical Forensic Discovery
1. **House 11 contains NO pump:**
   - Appliance 8 is an **Internet Router** (`Router, Unknown, Unknown`).
   - Appliance 9 is a **Hi-Fi Stereo** (`Hi-Fi, Unknown, Unknown`).
2. **House 12 contains NO pump:**
   - Appliance 7 is `Toaster (Nothing Recorded)`.
   - Appliance 8 is `Television (Nothing Recorded)`.
   - Appliance 9 is `Unknown (Nothing Recorded)`.
3. **The genuine Pond Pump is located in House 21:**
   - In REFIT, the fractional-horsepower AC induction motor (`Pond Pump`) is instrumented **exclusively in House 21, Appliance 9**.
4. **Archive Packaging Reality:** The University of Strathclyde pure repository does not offer individual house CSV downloads; it packages all 20 residences into a single 1.2 GB compressed archive (`CLEAN_REFIT_081116.7z`). Zenodo record 5063428 hosts individual CSVs (240–415 MB each), but only for Houses 1–5 and 11, omitting House 21.

**Enforced Action:** Rather than training a model on an Internet router and an unrecorded toaster, the experiment on House 11/12 was halted per the user's explicit stopping rule. The experiment runner ([run_public_dataset_experiment.py](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/run_public_dataset_experiment.py)) was updated with a verified catalog of all 20 houses, strict ground-truth validation assertions, and support for House 21 (`Pond Pump`) and House 2 (`Overhead Fan`).

---

## 2. Authoritative Dataset Provenance & Ground-Truth Inspection

The official schema was fetched directly from the Strathclyde Pure repository (`CLEAN_READ_ME_081116.txt`) via [inspect_refit_schema.py](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/inspect_refit_schema.py).

### Complete Ground-Truth Comparison: Houses 11, 12, and 21
| Channel | House 11 (Erronously Cited) | House 12 (Erronously Cited) | House 21 (Genuine Pump Truth) |
| :--- | :--- | :--- | :--- |
| **0. Aggregate** | Whole-House Active Power ($P$) | Whole-House Active Power ($P$) | Whole-House Active Power ($P$) |
| **1. Submeter 1** | Fridge (Gorenje HPI 1566) | Fridge-Freezer (Gorenje HZS 3266) | Fridge-Freezer (Samsung SR-L3216B) |
| **2. Submeter 2** | Fridge-Freezer | Unknown / Unlabeled | Tumble Dryer |
| **3. Submeter 3** | Washing Machine | Unknown / Unlabeled | Washing Machine (Beko WMB81241LW) |
| **4. Submeter 4** | Dishwasher | Computer Site | Dishwasher (AEG FAVORIT) |
| **5. Submeter 5** | Computer Site | Microwave | Food Mixer |
| **6. Submeter 6** | Microwave | Kettle | Television |
| **7. Submeter 7** | Kettle | Toaster *(Nothing Recorded)* | Kettle |
| **8. Submeter 8** | **Router (Broadband Modem)** | Television *(Nothing Recorded)* | Vivarium |
| **9. Submeter 9** | **Hi-Fi (Audio System)** | Unknown *(Nothing Recorded)* | **Pond Pump (Fractional AC Motor)** |

> [!CAUTION]
> **Scientific Integrity Blunder Prevented:** If Energy Mirror had blindly extracted `Appliance8` from House 11, it would have trained a "water pump NILM model" to recognize the constant 10 W draw of an **Internet Router**. If it had extracted House 12, it would have trained on an unrecorded empty channel. This validates the strict requirement to verify primary data before training.

---

## 3. Audit and Correction of the Experiment Runner

The public dataset runner ([run_public_dataset_experiment.py](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/run_public_dataset_experiment.py)) was thoroughly audited and updated with protective guardrails:

### 3.1 Strict Ground-Truth Catalog & Assertions
```python
# Authoritative REFIT appliance mappings from official CLEAN_READ_ME_081116.txt
REFIT_APPLIANCE_CATALOG = {
    "House1":  {"Appliance9": "Electric Heater (GLEN 2172)"},
    "House2":  {"Appliance9": "Overhead Fan"},
    "House11": {"Appliance8": "Router", "Appliance9": "Hi-Fi"},
    "House12": {"Appliance7": "Toaster (Empty)", "Appliance8": "Television (Empty)"},
    "House21": {"Appliance9": "Pond Pump"},
}

def validate_refit_target(house_id: str, target_category: str) -> Tuple[bool, str, str]:
    # Throws explicit ValueError if requested appliance does not exist in house metadata
```

### 3.2 Anti-Leakage & Temporal Alignment Verification
1. **Temporal Alignment:** REFIT data records active power every ~8 seconds monotonically. Timestamps are parsed as UTC pandas DatetimeIndex.
2. **Chunk Gap Detection:** Gaps $> 60\text{ s}$ trigger segment cuts via `detect_contiguous_chunks`. No silent linear interpolation across sensor outages.
3. **Zero Split Overlap:** Chronological partitioning drops a boundary buffer equal to $W = 15\text{ samples}$ (120 seconds) between Train/Val and Val/Test, ensuring zero window overlap.
4. **Sampling Cadence Limitation Documented:** REFIT's ~8-second sampling rate cannot resolve sub-second startup inrush spikes (which typically last 100–300 ms for AC induction motors). The pipeline evaluates steady-state active power steps, not high-speed inrush physics.

---

## 4. Evaluation Protocol Architecture

The experiment runner supports two evaluation modes:

### Protocol A: Time-Held-Out Chronological Evaluation
* **Target Residence:** REFIT House 21 (Appliance 9: Pond Pump).
* **Partitioning:**
  - **Train Set (60%):** Early longitudinal window.
  - *Buffer Window:* 15 samples dropped (120 s isolation).
  - **Validation Set (20%):** Mid-period window for hyperparameter checks.
  - *Buffer Window:* 15 samples dropped.
  - **Held-Out Test Set (20%):** Final chronological segment.
* **Evaluated Models & Baselines:**
  1. **Random Forest Classifier:** 100 estimators, max depth 8, windowed features ($P_{\text{curr}}, P_{\text{mean}}, P_{\text{std}}, P_{\text{min}}, P_{\text{max}}, \Delta P_{\text{instant}}, \Delta P_{\text{window}}$).
  2. **Simple Power Threshold Baseline:** Classifies ON when $P_{\text{mains}} \ge \text{threshold\_w}$.
  3. **Power-Change Step Baseline:** Differential step detector tracking transitions ($\Delta P \ge \text{step\_thresh}$).
  4. **Persistence Baseline ($t-1$):** Carries forward state from prior sample.
  5. **Majority-Class Baseline:** Predicts state 0 (OFF) and 0.0 W.

### Protocol B: Unseen-Building Cross-Residence Evaluation
* **Training:** Train on House 21 Pond Pump (Appliance 9).
* **Testing:** Test on an unseen residence (or UK-DALE House 1 solar thermal pump, Ch 3).
* **Constraint:** Zero tuning or threshold adjustment on the test house.

---

## 5. Delineation of the Three Validation Pillars

| Pillar | Data Source | What It Proves | What It Does NOT Prove | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Pillar 1: Synthetic Pipeline Tests** | 1 Hz simulated AC vector traces ([run_experiment.py](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/backend/ml_experiments/run_experiment.py)) | Mathematical correctness, feature extraction, boundary buffer isolation, and regression code. | Does **NOT** prove physical accuracy, sensor tolerance, or real-world disaggregation performance. | **COMPLETED & AUDITED.** |
| **Pillar 2: Public Real-Dataset Experiments** | Strathclyde REFIT Archive (House 21 Pond Pump) | Model resilience against unmetered background loads, household noise, and cross-residence transfer. | Does **NOT** prove performance on Indian domestic water pumps, ceiling fans, or 140 W heaters due to dataset domain gaps. | **SOFTWARE PIPELINE READY.** Blocked pending download of House 21 from archive. |
| **Pillar 3: Physical Calibration Experiments** | Benchtop PZEM-004T v3.0 metering physical target appliances | True hardware sensor calibration, CT turns ratio scaling, motor phase angles, physical inrush spikes. | Requires bench hardware assembly. | **DEFERRED.** `ENABLE_HARDWARE_INGEST=false` preserved. |

---

## 6. Verification Gate & System Health

| Domain | Target & Command | Result | Status |
| :--- | :--- | :--- | :--- |
| **Backend Test Suite** | `pytest -v` in `backend/` | **48 passed in 3.12s** | **VERIFIED** |
| **Frontend Test Suite** | `flutter test` in `mobile/` | **29 passed in 9.0s** | **VERIFIED** |
| **Static Code Analysis** | `flutter analyze` in `mobile/` | **No issues found (6.9s)** | **VERIFIED** |
| **Backend REST Health** | `GET http://127.0.0.1:8000/api/v1/health` | **HTTP 200 (`database_connected: true`)** | **ACTIVE** |
| **Web Preview Server** | `GET http://127.0.0.1:8080` | **HTTP 200 (Flutter Web build)** | **ACTIVE** |
| **Safety Invariants** | `ENABLE_HARDWARE_INGEST=false`, DB schema | **Unchanged, preserved** | **VERIFIED** |

---

## 7. Actionable Findings & Next Decision

### Summary of What Was Discovered
1. **House 11 and House 12 are invalid for water pump NILM:** House 11 submeters an Internet Router, and House 12 recorded nothing on its target channels.
2. **House 21 contains the genuine Pond Pump:** Appliance 9 in House 21 is the sole pump channel in REFIT.
3. **Download Packaging:** Strathclyde Pure packages REFIT as a single 1.2 GB 7z archive (`CLEAN_REFIT_081116.7z`). Zenodo hosts individual house CSVs (240–415 MB), but only for Houses 1–5 and 11 (excluding House 21).

### Next Decision Required from User
To run the genuine real-world public benchmark:
1. **Option A (Download Official 1.2 GB REFIT Archive):** Download `CLEAN_REFIT_081116.7z` (1.2 GB) from the Strathclyde repository, extract `CLEAN_House21.csv` (~250 MB uncompressed), and execute the real-data benchmark on the genuine Pond Pump.
2. **Option B (Use UK-DALE House 1 Solar Thermal Pump):** Download only `mains.dat` and `channel_3.dat` from UK-DALE House 1 (~1.2 GB) for a fractional inductive motor with active and apparent power.
3. **Option C (Remain on Validated Synthetic Pipeline & Defer to Hardware Bench Phase):** Maintain the software-only status quo with `RULE_BASED_ESTIMATE`, preserve clean code, and proceed directly to physical bench calibration when hardware is procured.
