# Energy Mirror: Living Current

**Energy Mirror** is a hardware + software energy intelligence system that uses aggregate electrical measurements and Non-Intrusive Load Monitoring (NILM) to estimate appliance-level consumption and help users understand invisible electricity usage.

> [!IMPORTANT]
> **HARDWARE STATUS: PENDING PROCUREMENT**  
> **No physical hardware components have been purchased, assembled, or connected yet.**  
> There is currently no physical PZEM meter or ESP32 attached to this application. The application operates in **Deterministic Software Simulation Mode**, serving verified synthetic telemetry ($284.0\text{ W} = 140\text{ W} + 75\text{ W} + 45\text{ W} + 12\text{ W} + 12\text{ W}$). The hardware ingestion endpoint (`POST /api/v1/telemetry/ingest`) is implemented in a **staged, inactive** state (`ENABLE_HARDWARE_INGEST=false` by default).

---

## 1. Project Task & Implementation Status

To maintain total transparency across development, all engineering tasks are strictly partitioned into five categories:

```
+----------------------------------------------------------------------------------------------------+
|                                    PROJECT TASK STATUS TAXONOMY                                    |
+----------------------------------------------------------------------------------------------------+
 [1. COMPLETED IN SOFTWARE]
  ├── Living Current Flutter Web Dashboard (Hero Energy Pulse, Constellation, Unattributed Load Bar)
  ├── Responsive multi-device layout (Mobile 393x852, Tablet 768x1024, Desktop 1440x900)
  ├── Riverpod state management & offline/stale banner handling
  ├── Truth-in-Reporting classification: [LIVE], [SIMULATED], [NILM ESTIMATED], [STALE], [OFFLINE]
  ├── FastAPI backend: GET /health, /telemetry/live, /telemetry/history, /nilm/live-disaggregation
  ├── Deterministic telemetry and NILM disaggregation simulator
  ├── SQLite database persistence and SQLAlchemy models
  ├── Staged hardware ingestion endpoint (POST /api/v1/telemetry/ingest) with Pydantic validation
  ├── Environment-driven secrets isolation (DEVICE_INGEST_TOKEN, .env.example, .gitignore)
  └── Automated test suites: 16 backend Pytest tests passed, 6 Flutter tests passed, 0 lint errors
         │
         ▼
 [2. READY FOR HARDWARE PROCUREMENT]
  ├── Procurement decision report: PZEM-004T v3.0 10A direct-shunt vs 100A CT variants
  ├── Itemized component checklist with purpose, quantities, safety ratings, and estimated budget
  ├── Low-power metrology validation procedure (Keysight/Fluke DMM benchmarking)
  └── Firmware architecture specification (FreeRTOS dual-core Modbus acquisition & Wi-Fi ingestion)
         │
         ▼
 [3. PENDING PHYSICAL ASSEMBLY]
  ├── Physical procurement of meter, ESP32, 5V isolated supply, and IP54 enclosure
  ├── Qualified electrician assembly and inspection of 230V mains wiring, 6A MCB, and 30mA RCD
  ├── Pre-power cold continuity and 500V DC insulation resistance testing (>= 50 MΩ)
  └── Verification of optical isolation barrier and physical creepage (> 4 mm) on PZEM PCB
         │
         ▼
 [4. PENDING REAL-DATA COLLECTION]
  ├── ESP32 firmware implementation, flashing, and FreeRTOS Modbus-RTU query verification
  ├── Benchmark testing of low-power loads (5W, 10W, 12W LED bulb) comparing 1-turn vs 10-turn CT
  ├── Supervised single-appliance characterization runs (10 duty cycles per target load)
  └── 16-state combinatorial multi-appliance permutation logging with synchronized ground truth
         │
         ▼
 [5. PENDING NILM MODEL TRAINING & EVALUATION]
  ├── Physical dataset export (time series with ground-truth binary state masks)
  ├── 2D feature engineering on macroscopic edge transitions (Delta P_norm, Delta |PF|, duration)
  ├── Baseline machine learning classifier training (Random Forest / Decision Tree)
  ├── Holdout evaluation: empirical Precision, Recall, F1-score (target >= 0.85 as evaluation goal)
  └── Promotion of evaluated model into production disaggregation service
```

---

## 2. Project Architecture

```
Energy Mirror/
├── backend/                       # Python & FastAPI Service
│   ├── app/
│   │   ├── main.py                # FastAPI ASGI application & lifespan
│   │   ├── config.py              # Application settings, secrets & CORS
│   │   ├── db/
│   │   │   ├── session.py         # SQLAlchemy engine & session factory
│   │   │   └── models.py          # Telemetry & Appliance ORM models
│   │   ├── schemas/
│   │   │   └── telemetry.py       # Pydantic v2 schemas (Ingest, Response, Physical Guardrails)
│   │   ├── api/
│   │   │   ├── health.py          # GET /api/v1/health
│   │   │   ├── telemetry.py       # GET /api/v1/telemetry/* & /api/v1/nilm/*
│   │   │   └── ingest.py          # POST /api/v1/telemetry/ingest (Staged Inactive)
│   │   └── services/
│   │       ├── simulator.py       # Deterministic telemetry & NILM engine
│   │       └── telemetry_service.py # Persistence & data access
│   ├── tests/                     # 16 Pytest tests (health, ingest, nilm, simulator, auth)
│   ├── requirements.txt
│   ├── .env.example               # Clean configuration template (zero committed secrets)
│   └── README.md
│
├── mobile/                        # Flutter Mobile Application
│   ├── lib/
│   │   ├── main.dart              # ProviderScope & app entrypoint
│   │   ├── app/
│   │   │   ├── theme.dart         # Living Current design tokens (obsidian, cyan, amber)
│   │   │   └── routes.dart        # GoRouter configuration
│   │   ├── core/
│   │   │   ├── models/            # Telemetry, appliance & history models
│   │   │   └── services/          # Dio API client with resilient offline fallback
│   │   └── features/dashboard/
│   │       ├── providers/         # Riverpod DashboardNotifier
│   │       ├── screens/           # DashboardScreen (responsive, 6 states)
│   │       └── widgets/           # EnergyPulseWidget, ApplianceConstellation,
│   │                              # UnattributedLoadBar, PowerTimelineChart,
│   │                              # EnergyStoryPanel, EnergyMirrorHeader
│   ├── test/                      # Unit, widget, and responsive tests (6 tests)
│   └── pubspec.yaml
│
├── .gitignore                     # Protects .env, databases, venv, and build files
└── README.md                      # Master documentation
```

---

## 3. Truth-in-Reporting Invariants (Active Simulator)

The active software prototype enforces exact mathematical and physical invariants across the UI and API:

* **Water Heater**: $140\text{ W}$ ($49.3\%$) — Near-unity power factor ($PF \approx 0.99$).
* **Water Pump**: $75\text{ W}$ ($26.4\%$) — Inductive motor load ($PF \approx 0.78$ lagging).
* **Ceiling Fan**: $45\text{ W}$ ($15.8\%$) — Moderate inductive rotary load ($PF \approx 0.91$).
* **LED Bulb**: $12\text{ W}$ ($4.2\%$) — Switch-mode power supply driver.
* **Total Recognized Appliance Estimates**: $272\text{ W}$ ($95.8\%$).
* **Unattributed Residual Power Floor**: $12\text{ W}$ ($4.2\%$) — Standby power and idle electronics.
* **Total Household Aggregate**: $284\text{ W}$ ($100.0\%$).
* **Invariant Enforced**:
  $$P_{\text{aggregate}} = \sum_{k} P_{\text{appliance}, k} + P_{\text{unattributed}} \implies 284\text{ W} = 272\text{ W} + 12\text{ W}$$

---

## 4. Quickstart & Execution

### 4.1 Backend (FastAPI + SQLite)

```powershell
cd "backend"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run automated tests (16 tests)
python -m pytest -v

# Start the API server on port 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* API Docs (Swagger): `http://127.0.0.1:8000/docs`
* Health Check: `http://127.0.0.1:8000/api/v1/health`
* Live Telemetry (Simulated Active): `http://127.0.0.1:8000/api/v1/telemetry/live`
* Live Disaggregation (Simulated Active): `http://127.0.0.1:8000/api/v1/nilm/live-disaggregation`
* Staged Ingestion Endpoint: `POST http://127.0.0.1:8000/api/v1/telemetry/ingest`

### 4.2 Mobile Application (Flutter Web & Mobile)

```powershell
cd "mobile"

# Run automated tests (6 tests)
flutter test

# Run static code analysis
flutter analyze

# Launch on Microsoft Edge
flutter run -d edge

# Build web release bundle
flutter build web
```

---

## 5. Automated Verification Summary

* **Backend Pytest**: `16 passed in 0.44s`
  * Health & Root endpoints
  * Telemetry history & Query parameter bounds
  * Simulator snapshot & arithmetic invariants
  * Live telemetry & Live disaggregation
  * Staged hardware ingestion (`mode="STAGED_INACTIVE"`)
  * Multi-turn CT turn scaling ($N = 10 \implies P_{\text{eff}} = P_{\text{raw}} / 10$)
  * Physical law violation rejection ($P > S \times 1.08 \implies 422$)
  * Extra field rejection (`extra="forbid"`)
  * Token authentication (`X-Device-Token` enforcement)
  * Hardware active mode toggling (`ENABLE_HARDWARE_INGEST=true`)
* **Flutter Tests**: `6 passed in 0.02s`
  * Model deserialization & invariant parsing
  * Responsive viewports: Mobile (393 × 852), Tablet (768 × 1024), Desktop (1440 × 900)
  * Interactive appliance selection sheet
  * Offline / Backend unreachable state handling
* **Flutter Analyze**: `No issues found! (0 warnings, 0 errors)`
* **Static Web Production Build**: `√ Built build\web`

---

## 6. Next Immediate Action (Before Hardware Procurement)

1. Review and approve the **Procurement Decision Report** comparing the **PZEM-004T 10A direct-shunt** vs **100A split-core CT** variants.
2. Select the final laboratory enclosure, 6A MCB, and 30mA RCD.
3. Place order for laboratory hardware components.
4. Schedule qualified electrician review for bench assembly.
