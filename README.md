# Energy Mirror: Living Current

<div align="center">

![Energy Mirror Banner](https://img.shields.io/badge/Energy%20Mirror-Living%20Current-00E5FF?style=for-the-badge&logo=electron&logoColor=black)

**Intelligent Non-Intrusive Load Monitoring (NILM) & Real-Time Residential Energy Intelligence Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.x%20Web%20%7C%20Mobile-02569B?style=flat-square&logo=flutter&logoColor=white)](https://flutter.dev)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations%20@%208f8361eca0e9-orange?style=flat-square)](https://alembic.sqlalchemy.org)
[![Tests](https://img.shields.io/badge/Tests-193%20Automated%20Passing-brightgreen?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)
[![Security](https://img.shields.io/badge/Security-Local%20Loopback%20Guarded-blueviolet?style=flat-square)](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/API_SECURITY_HARDENING_REPORT.md)
[![Accessibility](https://img.shields.io/badge/Accessibility-WCAG%20AAA%20%7C%2060%20FPS-success?style=flat-square)](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/UI_UX_RESEARCH_AND_DECISIONS.md)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Architecture](#2-system-architecture--data-flow) • [Truth-in-Reporting](#3-truth-in-reporting--current-prototype-status) • [Features](#4-key-features--user-experience) • [Quickstart](#5-quickstart--execution-guide) • [API Reference](#6-rest-api-documentation) • [Testing](#7-verification-testing--quality-gates) • [Hardware Blueprint](#8-hardware-specifications--procurement-blueprint) • [Documentation Index](#10-project-documentation-index)

</div>

---

## 1. Executive Summary & Problem Statement

Residential electrical monitoring has long suffered from an unresolved dilemma between total whole-home blindness and intrusive, costly sub-metering:

1. **Whole-Home Blindness:** Standard smart utility meters report aggregate kilowatt-hour usage every 15 to 60 minutes or as a single aggregate figure at billing cycles. Homeowners cannot diagnose which appliance is wasting electricity, cycling excessively, or degrading toward catastrophic failure.
2. **Sub-Metering Fatigue & Impracticality:** Traditional sub-metering demands placing individual smart plugs on dozens of wall outlets. This introduces excessive cost ($25–$50 per outlet), aesthetic clutter, dozens of fragile Wi-Fi failure points, and is **completely impossible for hardwired high-draw appliances** such as submerged borehole well pumps, storage water heaters, central HVAC compressors, and ceiling fans.

### The Energy Mirror Solution
**Energy Mirror** implements **Non-Intrusive Load Monitoring (NILM)** to extract appliance-level operational intelligence from a **single aggregate sensing point** installed at the home's main electrical service distribution panel. By mathematically decomposing aggregate active power ($P$), power factor ($PF$), apparent power ($S$), and high-frequency edge transition signatures, Energy Mirror provides granular appliance breakdown without a single smart plug.

```
       SINGLE SERVICE PANEL SENSOR
   [PZEM-004T v3.0 / Current Transformer]
                     │ (Aggregate 1 Hz Metrology)
                     ▼
          ENERGY MIRROR BACKEND
  [FastAPI + Derivative Edge NILM Engine]
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
Water Heater     Water Pump      Ceiling Fan     ... All from ONE Sensing Point!
(140.0 W Active) (75.0 W Active) (45.0 W Active)
```

---

## 2. System Architecture & Data Flow

Energy Mirror is built on an asynchronous, decoupled, multi-tier reactive architecture designed for zero latency and strict data integrity.

### Architectural Diagram

```
+-----------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER                                   |
|   Flutter Web & Multiplatform Dashboard (Electrum Slate Theme, 60 FPS, WCAG AAA)        |
|   - Real-Time Aggregate Hero Pulse Gauge (Breathing Cyan Glow, Active Dynamic Power)    |
|   - Interactive Appliance Constellation (3D Render Cards, Duty Cycles, Toggle Lab)     |
|   - Physical Load Reconciliation Bar (Attributed Sum vs Calibrated 12.0W Residual Floor)|
|   - Responsive Multi-Device Views (Mobile 393x852, Tablet 768x1024, Desktop 1440x900)   |
|   - Dynamic Appliance Management Workbench (CRUD Dialogs, Safety Deletion Guards)       |
+--------------------------------------------+--------------------------------------------+
                                             | HTTP/REST & WebSocket Polling (Reverse Proxy :5000)
+--------------------------------------------v--------------------------------------------+
|                                      BACKEND GATEWAY                                    |
|   FastAPI ASGI Application (:8000) with Pydantic v2 Strict Validation & Lifespan Hooks  |
|   - Security Hardening: Loopback Mutation Guards (403 on Remote Writes), Timing-Safe Auth|
|   - Unified Reverse Proxy & Static Web Host (serve_web.py / unified_server.py)          |
+---------------------+-------------------------------+-----------------------------------+
                      |                               |
+---------------------v-------------+   +-------------v-----------------------------------+
|     DYNAMIC APPLIANCE REGISTRY    |   |     RULE-BASED NILM EVENT DETECTOR              |
|   - Database-backed definitions   |   |   - Derivative Step Detection (Delta P, Delta PF)|
|   - Calibrated tolerance bounds   |   |   - Real-time signature envelope matching       |
|   - Capability honesty gating:    |   |   - Idempotent event fingerprinting             |
|     PRODUCTION_RULE_MATCHED vs    |   |   - Simultaneous switching ambiguity tagging   |
|     UNSUPPORTED (prevents false   |   |                                                 |
|     recognition claims)           |   |                                                 |
+---------------------+-------------+   +-------------+-----------------------------------+
                      |                               |
+---------------------v-------------------------------v-----------------------------------+
|                                  DURABLE PERSISTENCE LAYER                              |
|   Dual-Engine Database Architecture (Alembic Migrations @ 8f8361eca0e9):                |
|   - SQLite (energy_mirror.db) for zero-dependency local development and review          |
|   - PostgreSQL (postgresql+psycopg2) compatible for production container deployments    |
|   - Tables: telemetry_records, appliance_estimates, detected_events, appliance_registry|
+-----------------------------------------------------------------------------------------+
                                             ▲
                                             │ (Staged Hardware Ingestion Pipeline)
+--------------------------------------------┴--------------------------------------------+
|                            PLANNED HARDWARE METROLOGY LAYER                             |
|   - PZEM-004T v3.0 Digital Multi-Function Energy Meter (UART / Modbus-RTU)              |
|   - ESP32 Dual-Core Microcontroller (Core 0: FreeRTOS Metrology, Core 1: Wi-Fi HTTP)    |
|   - Multi-Turn CT Scaling (N = 10 turns for 10x resolution on low-wattage loads)        |
|   - High-Voltage Safety: 6A MCB, 30mA RCD, 5kV Optocoupler Galvanic Isolation Barrier   |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Truth-in-Reporting & Current Prototype Status

Energy Mirror maintains absolute transparency regarding prototype status across all UI badges, API contracts, and documentation:

> [!IMPORTANT]
> **PROTOTYPE CLASSIFICATION: VERIFIED SOFTWARE SIMULATION**  
> * **Hardware Status:** Pending procurement and physical bench assembly.  
> * **Zero Physical Hardware Connected:** No physical Current Transformer (CT), PZEM-004T sensor, or ESP32 microcontroller is transmitting live physical signals to this instance.  
> * **Hardware Ingestion Inactive:** The configuration setting `ENABLE_HARDWARE_INGEST=false` is enforced at the root settings level. The ingestion endpoint (`POST /api/v1/telemetry/ingest`) is staged in `STAGED_INACTIVE` mode.  
> * **Calibrated Deterministic Simulator:** The running application serves high-fidelity synthetic telemetry conforming to strict physical laws at 1 Hz.  
> * **Transparent Truth Badging:** Every payload and UI component clearly displays `"data_source": "SIMULATED"` or `"data_source": "NILM_ESTIMATED"`.

### The 12.0 W Background Residual Floor Invariant
In real-world residential systems, there is an irreducible parasitic baseline load (smoke detectors, Wi-Fi routers, microwave standby displays, doorbell transformers).

Within the Energy Mirror simulator:
* The continuous **12.0 W unattributed background floor** is a **calibrated baseline assumption**.
* **It is strictly distinct from the 12.0 W LED bulb load.**
* Total aggregate power satisfies the exact conservation invariant:

$$P_{\text{aggregate}} \equiv \sum_{k} P_{\text{attributed}, k} + P_{\text{unattributed}}$$

```
+----------------------------------------------------------------------------------------+
| VIRTUAL APPLIANCE BASELINE CONFIGURATION                                               |
+--------------------+------------+--------------+---------------+-----------------------+
| Appliance Name     | Active (W) | Power Factor | Nominal Share | Electrical Signature  |
+--------------------+------------+--------------+---------------+-----------------------+
| Water Heater       | 140.0 W    | 0.99 (Unity) | 49.3%         | Pure Resistive Nichrome|
| Water Pump         |  75.0 W    | 0.78 Lagging | 26.4%         | Inductive Motor Inrush|
| Ceiling Fan        |  45.0 W    | 0.91 Lagging | 15.8%         | Rotary Inductive      |
| LED Bulb           |  12.0 W    | 0.95 Leading |  4.2%         | SMPS Driver Rectifier |
| Unattributed Floor |  12.0 W    | 1.00 Nominal |  4.2%         | Parasitic Standby     |
+--------------------+------------+--------------+---------------+-----------------------+
| TOTAL AGGREGATE    | 284.0 W    | 0.96 Net     | 100.0%        | Exact Reconciliation  |
+--------------------+------------+--------------+---------------+-----------------------+
```

* **All 4 Appliances ON:** $140\text{ W} + 75\text{ W} + 45\text{ W} + 12\text{ W} + 12\text{ W} = \mathbf{284.0\text{ W}}$
* **Water Heater Toggled OFF:** $0\text{ W} + 75\text{ W} + 45\text{ W} + 12\text{ W} + 12\text{ W} = \mathbf{144.0\text{ W}}$
* **All Appliances OFF:** $0\text{ W} + 0\text{ W} + 0\text{ W} + 0\text{ W} + 12\text{ W} = \mathbf{12.0\text{ W}}$ ($100\%$ unattributed residual)

---

## 4. Key Features & User Experience

### 1. Living Current Hero Pulse Gauge
- Central radial gauge with a 60 FPS breathing cyan glow synchronized to active household draw.
- Real-time tabular numerical readout with zero layout shift.
- Visual status pills for truth-in-reporting (`[SIMULATED]`, `[NILM_ESTIMATED]`).

### 2. Interactive Appliance Constellation Grid
- Custom 3D isometric iconography representing each household appliance category.
- Live interactive toggle switches enabling reviewers to test instant load recalculation.
- Operational metrics: Real-time power ($W$), voltage ($V$), power factor ($PF$), and estimated daily duty cycle.

### 3. Dynamic Appliance Registry & Workbench
- Database-backed appliance catalog supporting on-the-fly registration of new equipment.
- Calibrated tolerance envelopes ($\Delta P$ nominal, $\pm \text{tolerance}$, expected $PF$).
- **Capability Honesty Gating:** Dynamically distinguishes between `PRODUCTION_RULE_MATCHED` (appliances within calibrated detection envelopes) and `UNSUPPORTED` (custom devices without verified signatures, preventing deceptive claims).
- Protected baseline definitions: The four primary demo appliances are guarded against accidental deletion.

### 4. Physical Load Reconciliation Bar
- Segmented visual reconciliation displaying the exact proportion of power attributed to active appliances versus the background parasitic floor.
- Prevents the "phantom load illusion" by showing users unmonitored residual draw.

### 5. Multi-Interval Durable Power Timeline Chart
- FlChart-powered historical telemetry visualization supporting 15m, 1h, 6h, and 24h intervals.
- Non-flatline rendering: dynamic minimum and maximum vertical axis scaling preserves subtle fluctuations even during steady-state conditions.

### 6. API Security Hardening & Administrative Protection
- **Local Loopback Isolation:** Mutation endpoints (`POST /api/v1/appliances`, `PATCH`, `DELETE`) are restricted to local loopback clients (`127.0.0.1`, `::1`). Remote mutation requests are rejected with `HTTP 403 Forbidden`.
- **Timing-Safe Token Authentication:** Ingestion endpoints use constant-time `secrets.compare_digest` to prevent side-channel timing attacks.
- Strict CORS validation preventing wildcard origins in production environments.

---

## 5. Quickstart & Execution Guide

### Prerequisites
* **Python 3.10 or 3.11** installed (`python --version`)
* **Flutter SDK 3.x** installed with Edge or Chrome support (`flutter doctor`)
* **PowerShell 7+ or standard Windows PowerShell**
* **Git**

---

### Option A: One-Click Unified Launch (Recommended)

Run the included automated launch script from the repository root:

```powershell
.\start_demo.ps1
```

The script will:
1. Verify Python and Flutter environments.
2. Initialize or verify the Python virtual environment (`backend\.venv`).
3. Apply all database migrations via Alembic (`alembic upgrade head`).
4. Launch the unified server hosting both the FastAPI backend (`:8000`) and the Flutter Web application (`:5000`).
5. Open your default web browser directly to `http://localhost:5000`.

---

### Option B: Step-by-Step Manual Launch

#### Step 1: Start the Backend Service
```powershell
cd "backend"

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Run database migrations
alembic upgrade head

# Start the FastAPI ASGI server on port 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Diagnostic Endpoint: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

#### Step 2: Launch the Frontend Web Dashboard
In a separate terminal window:
```powershell
cd "mobile"

# Launch directly in Microsoft Edge or Google Chrome
flutter run -d edge
```

Or build the static web release bundle and serve it via Python:
```powershell
cd "mobile"
flutter build web --release

cd ..
python serve_web.py --port 5000
```
Navigate to [http://localhost:5000](http://localhost:5000).

---

## 6. REST API Documentation

The backend exposes a clean, versioned, RESTful API documented automatically via OpenAPI / Swagger.

| Method | Endpoint | Access Policy | Description |
|:-------|:---------|:--------------|:------------|
| `GET` | `/api/v1/health` | Public | System health, uptime, and database connectivity status |
| `GET` | `/api/v1/diagnostics` | Public | System diagnostics, active mode, and database driver info |
| `GET` | `/api/v1/telemetry/live` | Public | Real-time aggregate telemetry (voltage, current, power, PF) |
| `GET` | `/api/v1/telemetry/history` | Public | Historical telemetry series with configurable intervals (`15m`, `1h`, `6h`, `24h`) |
| `GET` | `/api/v1/nilm/live-disaggregation` | Public | Current disaggregated appliance breakdown and residual floor |
| `GET` | `/api/v1/nilm/events` | Public | Detected state-transition event history (ON/OFF steps, timestamps) |
| `POST` | `/api/v1/simulator/toggle` | Public (Demo) | Toggle virtual appliance state for interactive simulation |
| `POST` | `/api/v1/simulator/reset` | Public (Demo) | Reset simulator to the default 284.0 W baseline state |
| `GET` | `/api/v1/appliances` | Public | List all registered appliances in the dynamic catalog |
| `GET` | `/api/v1/appliances/{id}` | Public | Retrieve detailed definition for a specific appliance |
| `POST` | `/api/v1/appliances` | Admin / Loopback | Register a new appliance definition with calibrated tolerances |
| `PATCH` | `/api/v1/appliances/{id}` | Admin / Loopback | Update an existing appliance's operational parameters |
| `DELETE` | `/api/v1/appliances/{id}` | Admin / Loopback | Remove an appliance definition (Default 4 appliances protected) |
| `POST` | `/api/v1/telemetry/ingest` | Staged Inactive | Hardware ingestion endpoint (`X-Device-Token` authenticated) |

### Sample Payload: Live Telemetry (`GET /api/v1/telemetry/live`)
```json
{
  "timestamp": "2026-11-26T10:48:00Z",
  "voltage_v": 230.2,
  "current_a": 1.28,
  "active_power_w": 284.0,
  "power_factor": 0.963,
  "apparent_power_va": 294.6,
  "frequency_hz": 50.0,
  "data_source": "SIMULATED",
  "device_id": "SIMULATOR_CORE_01"
}
```

### Sample Payload: Live Disaggregation (`GET /api/v1/nilm/live-disaggregation`)
```json
{
  "timestamp": "2026-11-26T10:48:00Z",
  "total_aggregate_power_w": 284.0,
  "total_attributed_power_w": 272.0,
  "unattributed_residual_power_w": 12.0,
  "data_source": "NILM_ESTIMATED",
  "appliances": [
    {
      "id": "water_heater_01",
      "name": "Water Heater",
      "category": "HEATING",
      "state": "ON",
      "estimated_power_w": 140.0,
      "confidence": 0.98,
      "power_factor": 0.99
    },
    {
      "id": "water_pump_01",
      "name": "Water Pump",
      "category": "MOTOR",
      "state": "ON",
      "estimated_power_w": 75.0,
      "confidence": 0.94,
      "power_factor": 0.78
    },
    {
      "id": "ceiling_fan_01",
      "name": "Ceiling Fan",
      "category": "ROTARY",
      "state": "ON",
      "estimated_power_w": 45.0,
      "confidence": 0.91,
      "power_factor": 0.91
    },
    {
      "id": "led_bulb_01",
      "name": "LED Bulb",
      "category": "LIGHTING",
      "state": "ON",
      "estimated_power_w": 12.0,
      "confidence": 0.90,
      "power_factor": 0.95
    }
  ]
}
```

---

## 7. Verification, Testing & Quality Gates

The codebase is protected by **193 automated tests** spanning backend integration, public dataset benchmarks, and mobile frontend suites, plus real browser end-to-end acceptance.

```
+---------------------------------------------------------------------------------------+
| TOTAL VERIFIED TEST SUITE: 193 AUTOMATED TESTS PASSED (0 FAILURES, 0 WARNINGS)        |
+------------------------------------+------------+-------------------------------------+
| Test Suite Category                | Tests Run  | Target Modules / Scope              |
+------------------------------------+------------+-------------------------------------+
| Backend API & Ingestion Security   | 18 Tests   | Loopback auth, timing-safe tokens   |
| Dynamic Appliance Registry         | 15 Tests   | Dynamic CRUD, capability honesty    |
| Database & Alembic Migrations      | 11 Tests   | Empty DB upgrade, idempotency, seed |
| Event Detector & NILM Algorithms   | 11 Tests   | Derivative steps, ambiguity checks  |
| Telemetry & History Endpoints      | 10 Tests   | Data bounds, 15m/1h/6h/24h intervals|
| Simulator & Power Accounting       | 15 Tests   | 16 combinatorial states, 12W floor  |
| System Diagnostics & Health        |  4 Tests   | Database driver & telemetry health  |
| Ingestion Physical Law Guardrails  |  8 Tests   | CT multi-turn scaling, P <= S*1.08  |
| Public Dataset ML Benchmarks       | 63 Tests   | REFIT & iAWE intermittent datasets  |
| Flutter Unit, Widget & Responsive  | 38 Tests   | 11 suites (Mobile, Tablet, Desktop) |
+------------------------------------+------------+-------------------------------------+
| TOTAL AUTOMATED TEST PASS RATE     | 193 / 193  | 100% Pass Rate                      |
+------------------------------------+------------+-------------------------------------+
```

### Running Backend Tests
```powershell
cd "backend"
.\.venv\Scripts\python.exe -m pytest -v
```

### Running Flutter Tests
```powershell
cd "mobile"
flutter test
flutter analyze
```

### Real Browser End-to-End Acceptance (Microsoft Edge via CDP)
Automated real-browser acceptance testing has been verified against the live reverse proxy (`http://localhost:5000`):
- Tested on standard **Desktop (1440 × 900)** and **Mobile (393 × 852)** viewports.
- Verified live simulator power reconciliation ($284\text{ W} \to 144\text{ W} \to 284\text{ W}$).
- Verified dynamic appliance lifecycle (add 850 W electric kettle, update to 900 W, delete, verify cleanup).
- Zero unhandled console errors or layout overflow exceptions.

---

## 8. Hardware Specifications & Procurement Blueprint

For academic reviewers and engineering teams preparing to transition Energy Mirror from simulation to live hardware, complete schematics and bill-of-materials are documented in [HARDWARE_ARCHITECTURE_REVIEW.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/HARDWARE_ARCHITECTURE_REVIEW.md).

### Bill of Materials (BOM)

```
+------------------------------------------------------------------------------------------------+
| COMPONENT BILL OF MATERIALS & PROCUREMENT SPECIFICATIONS                                       |
+-------------------+-------------------+-----+-----------------------------+--------------------+
| Component         | Model / Variant   | Qty | Purpose                     | Safety / Rating    |
+-------------------+-------------------+-----+-----------------------------+--------------------+
| Energy Meter IC   | PZEM-004T v3.0    |  1  | 1 Hz V, I, P, PF, E, Freq   | Optical Isolation  |
| Current Sensor    | Split-Core CT     |  1  | 100A / 100mA secondary      | 500V Cat III rated |
| Microcontroller   | ESP32-WROOM-32D   |  1  | FreeRTOS Modbus & HTTP POST | CE / FCC certified |
| Power Supply      | HLK-PM01 (5V 3W)  |  1  | Isolated AC-DC for ESP32    | 3000V Isolation    |
| Circuit Breaker   | Single-Pole MCB   |  1  | Overcurrent protection      | 6A, 10kA breaking  |
| Residual Device   | 2-Pole RCD / RCCB |  1  | Earth fault protection      | 30mA trip threshold|
| Enclosure         | DIN-Rail Polycarb |  1  | Electrical bench isolation  | IP54 Flame Retard  |
+-------------------+-------------------+-----+-----------------------------+--------------------+
```

### Low-Power CT Multi-Turn Scaling ($N = 10$)
Standard 100A split-core current transformers exhibit non-linear distortion when measuring low-wattage loads below $20\text{ W}$ (such as a $12\text{ W}$ LED bulb). 

To resolve this limitation without expensive metrology equipment, Energy Mirror incorporates **Multi-Turn Primary Winding**:
* By looping the target primary conductor through the CT aperture **$N = 10$ times**, the effective magnetic flux is multiplied tenfold ($I_{\text{sensed}} = 10 \times I_{\text{actual}}$).
* The ESP32 firmware and backend ingestion layer apply inverse scaling:
  $$P_{\text{actual}} = \frac{P_{\text{measured}}}{N} = \frac{120\text{ W}}{10} = 12.0\text{ W}$$
* This scales low-current signals cleanly into the PZEM's linear dynamic range.

---

## 9. Repository & Directory Structure

```
Energy Mirror/
├── backend/                             # Python & FastAPI Service
│   ├── alembic/                         # Alembic database migrations
│   │   ├── versions/                    # Version scripts (8f8361eca0e9_create_initial_schema.py)
│   │   └── env.py                       # Migration environment & model binding
│   ├── app/
│   │   ├── main.py                      # FastAPI ASGI application & lifespan
│   │   ├── config.py                    # Environment settings, CORS, and loopback guards
│   │   ├── db/
│   │   │   ├── session.py               # SQLAlchemy dual-engine session factory
│   │   │   └── models.py                # Telemetry, Appliance, & Event ORM models
│   │   ├── schemas/
│   │   │   └── telemetry.py             # Pydantic v2 schemas & physical guardrails
│   │   ├── api/
│   │   │   ├── health.py                # GET /health & /diagnostics
│   │   │   ├── telemetry.py             # GET /telemetry/live & /telemetry/history
│   │   │   ├── appliances.py            # Dynamic appliance registry CRUD
│   │   │   └── ingest.py                # POST /telemetry/ingest (Staged Inactive)
│   │   └── services/
│   │       ├── simulator.py             # Deterministic telemetry & NILM engine
│   │       ├── event_detector.py        # Rule-based derivative edge detector
│   │       └── telemetry_service.py     # Persistent data access layer
│   ├── ml_experiments/                  # ML dataset benchmarks (REFIT & iAWE)
│   │   ├── experiments/                 # Benchmark runners & feature extractors
│   │   └── tests/                       # 63 automated ML validation tests
│   ├── tests/                           # 92 Pytest backend integration tests
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example                     # Clean configuration template
│
├── mobile/                              # Flutter Multiplatform Dashboard
│   ├── lib/
│   │   ├── main.dart                    # Application entrypoint & ProviderScope
│   │   ├── app/
│   │   │   ├── theme.dart               # Electrum Slate design system tokens
│   │   │   └── routes.dart              # GoRouter configuration & routes
│   │   ├── core/
│   │   │   ├── models/                  # Telemetry, appliance, & event DTO models
│   │   │   └── services/                # Dio HTTP client with offline retry policies
│   │   └── features/dashboard/
│   │       ├── providers/               # Riverpod DashboardNotifier & states
│   │       ├── screens/                 # Responsive dashboard screens (Compact / Wide)
│   │       └── widgets/                 # HeroPulse, Constellation, TimelineChart,
│   │                                    # DynamicRegistryModal, ReconciliationBar
│   ├── test/                            # 38 Flutter unit, widget, and responsive tests
│   └── pubspec.yaml
│
├── serve_web.py                         # Unified static host and reverse proxy
├── start_demo.ps1                       # Automated one-click demo launcher
├── energy_mirror.db                     # SQLite database file for local development
└── README.md                            # Master project documentation
```

---

## 10. Project Documentation Index

Energy Mirror is documented across an exhaustive series of audit, benchmark, and architectural reports:

| Document | Primary Focus |
|:---------|:--------------|
| [BENCHMARK_AUDIT_REPORT.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/BENCHMARK_AUDIT_REPORT.md) | Comprehensive audit of all 193 automated tests, coverage, and benchmarks |
| [DEMO_PRESENTATION_NOTES.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/DEMO_PRESENTATION_NOTES.md) | Structured presentation script and talking points for technical judges |
| [HARDWARE_ARCHITECTURE_REVIEW.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/HARDWARE_ARCHITECTURE_REVIEW.md) | Schematics, safety ratings, optical isolation, and itemized procurement BOM |
| [API_SECURITY_HARDENING_REPORT.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/API_SECURITY_HARDENING_REPORT.md) | Loopback authorization, timing-safe authentication, and CORS verification |
| [DYNAMIC_APPLIANCE_REGISTRY_REPORT.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/DYNAMIC_APPLIANCE_REGISTRY_REPORT.md) | Registry schema, capability honesty tags, and dynamic CRUD lifecycle |
| [POSTGRESQL_ALEMBIC_MIGRATION_REPORT.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/POSTGRESQL_ALEMBIC_MIGRATION_REPORT.md) | Dual-engine database design, schema evolution, and migration testing |
| [REAL_DATA_NILM_VALIDATION_REPORT.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/REAL_DATA_NILM_VALIDATION_REPORT.md) | Empirical validation on public datasets (UK REFIT & Indian iAWE) |
| [UI_UX_RESEARCH_AND_DECISIONS.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/UI_UX_RESEARCH_AND_DECISIONS.md) | Electrum Slate design system, WCAG AAA compliance, and interaction design |
| [SCREENSHOT_QA_AND_FIX_REPORT.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/SCREENSHOT_QA_AND_FIX_REPORT.md) | Visual evidence, responsive checks (393px to 1440px), and Edge browser QA |
| [KNOWN_LIMITATIONS.md](file:///c:/Users/Kaviya/Downloads/Energy%20Mirror/KNOWN_LIMITATIONS.md) | Explicit algorithmic boundary conditions and simultaneous switching limits |

---

## 11. Realistic Future Roadmap

```
+-----------------------------------------------------------------------------------+
| MILESTONE 1-3: COMPLETE (CURRENT PROTOTYPE)                                       |
| - Deterministic 1 Hz simulation prototype adhering to conservation laws           |
| - Rule-based derivative NILM edge detector with ambiguity tagging                 |
| - Dynamic database-backed appliance registry with capability honesty gating       |
| - Electrum Slate Flutter Web / Mobile Dashboard (60 FPS, WCAG AAA, 393px-1440px)   |
| - Dual-engine persistence (SQLite / PostgreSQL) with Alembic migration revisions  |
| - 193 automated tests passed + real browser acceptance testing                    |
+-----------------------------------------+-----------------------------------------+
                                          |
+-----------------------------------------v-----------------------------------------+
| MILESTONE 4 (Q1): SUPERVISED BENCH TESTING (PENDING PROCUREMENT)                  |
| - Procure PZEM-004T v3.0, ESP32, 6A MCB, 30mA RCD, and IP54 enclosure            |
| - Conduct 500V DC insulation resistance testing (>= 50 MΩ) on test bench           |
| - Flash ESP32 FreeRTOS firmware with Modbus-RTU 1 Hz acquisition loop             |
| - Evaluate N=10 multi-turn CT scaling against Fluke/Keysight laboratory DMM       |
| - Activate POST /api/v1/telemetry/ingest via mutual TLS (mTLS) or device token    |
+-----------------------------------------+-----------------------------------------+
                                          |
+-----------------------------------------v-----------------------------------------+
| MILESTONE 5 (Q2): EXTENDED MACHINE LEARNING NILM PIPELINE                         |
| - Collect multi-week high-frequency ground-truth traces across diverse homes      |
| - Train Sequence-to-Point (Seq2Point) and Temporal Convolutional Networks (TCN)   |
| - Deploy ONNX runtime inference microservice for continuous variable inverters    |
+-----------------------------------------------------------------------------------+
```

---

## 12. Authors & Acknowledgments

* **Lead Engineer & Architect:** Kaviya
* **Project Repository:** [https://github.com/KAVIYA957/Energy-Mirror.git](https://github.com/KAVIYA957/Energy-Mirror.git)
* **Dataset References:**
  * UK REFIT Electrical Load Dataset (Loughborough University)
  * Indian Ambient Water and Energy (iAWE) Dataset (IIIT Delhi)

---

<div align="center">
<b>Energy Mirror: Living Current</b> • Revealing Invisible Electricity with Transparent Engineering.
</div>
