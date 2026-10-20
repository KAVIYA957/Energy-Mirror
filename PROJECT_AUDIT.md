# Energy Mirror: Project Baseline Audit & Architectural State
**Document Date:** October 20, 2026  
**Auditor:** Principal Product Designer & Lead Systems Architect  
**Project Root:** `c:\Users\Kaviya\Downloads\Energy Mirror`  
**Milestone:** Phase 0 — Baseline Verification & Safety Freeze  

---

## 1. Executive Summary
Energy Mirror is a hybrid IoT/NILM energy intelligence application engineered to identify individual household appliance activities from aggregate electrical telemetry. Prior to the Luminous Clarity UI/UX and architectural upgrade, the project operates as a fully functional, mathematically verified software prototype with a Python FastAPI backend and a Flutter/Dart multi-platform frontend.

This audit establishes the pre-upgrade operational, algorithmic, and data baseline. All automated tests pass without errors, development databases have been backed up, and all non-negotiable safety constraints (`ENABLE_HARDWARE_INGEST=false`, explicit `SIMULATED` / `RULE_BASED_ESTIMATE` tags) are confirmed active.

---

## 2. Repository & Architectural Inventory

### 2.1 Backend Architecture
- **Framework:** Python 3.11.9, FastAPI 0.110+, Uvicorn 0.28+
- **Database:** SQLite (`backend/energy_mirror.db`), SQLAlchemy 2.0 ORM
- **Migration & Persistence:** Alembic-ready schema with durable SQLite storage for:
  - `telemetry_records`: 215 rows (aggregate simulated voltage, current, active power, reactive power, power factor, THD)
  - `appliance_estimates`: 616 rows (disaggregated appliance states and estimated wattages)
  - `detected_events`: 2 rows (durable event archive with SHA-256 fingerprint deduplication)
- **Mathematical Invariant:**
  $$\text{Aggregate Power } P_{\text{agg}} = \sum_{i=1}^{4} P_{\text{appliance}, i} + P_{\text{residual}}$$
  Where:
  - Water Heater: $140.0\text{ W}$
  - Water Pump: $75.0\text{ W}$
  - Ceiling Fan: $45.0\text{ W}$
  - LED Bulb: $12.0\text{ W}$
  - Background Floor / Residual: $12.0\text{ W}$
  - Full Active Baseline: $140 + 75 + 45 + 12 + 12 = 284.0\text{ W}$
  - All-Off Baseline: $0 + 0 + 0 + 0 + 12 = 12.0\text{ W}$
- **Detection Engine:** `RuleBasedEventDetector` operating with delta thresholds:
  - Heater: $140\text{ W} \pm 20\text{ W}$
  - Pump: $75\text{ W} \pm 15\text{ W}$
  - Fan: $45\text{ W} \pm 10\text{ W}$
  - Bulb: $12\text{ W} \pm 4\text{ W}$
- **Hardware Ingest:** Strictly staged and disabled via `ENABLE_HARDWARE_INGEST=false` in `backend/app/core/config.py`.

### 2.2 Frontend Architecture
- **Framework:** Flutter 3.x, Dart 3.13+
- **State Management:** Riverpod 2.6.1 (`StateNotifierProvider`, `FutureProvider`, auto-dispose lifecycle)
- **Navigation:** GoRouter 14.8.1 with `ShellRoute` housing 4 primary routes:
  - `/` (Dashboard)
  - `/history` (Analytics & Event History)
  - `/simulator` (Appliance Simulator Lab)
  - `/diagnostics` (System Diagnostics & Privacy Audit)
- **HTTP Client:** Dio 5.8.0 with interceptors, timeouts, and structured error handling
- **Visualization:** FL Chart 0.70.2 for historical telemetry line graphs
- **Active Dev Daemon Services:**
  - FastAPI Backend: `http://0.0.0.0:8000` (LAN: `http://192.168.29.166:8000`)
  - Web Server: `http://0.0.0.0:8080` serving release build (LAN: `http://192.168.29.166:8080`)

---

## 3. Baseline Verification Results

| Suite / Check | Command | Target Directory | Baseline Result | Execution Time | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Backend Pytest** | `python -m pytest -v` | `backend/` | **44 passed, 0 failed** | 1.81s | In-memory SQLite isolated fixtures |
| **Flutter Test** | `flutter test` | `mobile/` | **29 passed, 0 failed** | 6.8s | All 6 test files passed |
| **Flutter Analyze** | `flutter analyze` | `mobile/` | **0 issues found** | 5.4s | Zero warnings, zero errors |
| **Flutter Web Build** | `flutter build web --release` | `mobile/` | **Success** | 50.1s | Output at `mobile/build/web` |
| **Database Row Counts** | Direct SQLite inspect | `backend/energy_mirror.db` | **215 / 616 / 2** | Instant | Pre-test state preserved |

---

## 4. Identified UI/UX & Technical Improvement Areas

1. **Visual Hierarchy & Theme:**
   - Previous dark theme (`obsidianCanvas: #080C14` with neon cyan `#00E5FF`) was visually aggressive and caused eye strain during extended analysis.
   - Lacks the serene, consumer-trustworthy aesthetic needed for general homeowners.
   - Transition to **Luminous Clarity** (`#F7F8F4` canvas, `#FFFFFF` cards, `#17243B` text, `#3159C9` primary interaction) will substantially improve readability and emotional calm.

2. **Appliance Visual Assets:**
   - Appliances currently rely solely on Material icons (`Icons.water_damage`, `Icons.waves`, `Icons.mode_fan`, `Icons.lightbulb_outline`).
   - Lacks dedicated, high-fidelity visual representations (photorealistic 3D render style) to establish immediate real-world connection.

3. **Plain-Language Communication:**
   - Jargon such as "Reactive Power VAR", "THD %", and "Rule-Based NILM Invariant" can intimidate non-technical users.
   - Retain technical telemetry under collapsible/diagnostics views, while surfacing plain-language explanations: "Attributed Appliance Load", "Background Power", and clear "SIMULATED" badges.

4. **Responsive Layouts & Viewport Flexibility:**
   - Ensure zero `RenderFlex` overflows on narrow mobile viewports (360–393px) using `Wrap` for metadata badges and adaptive multi-column layouts for tablet (768px) and desktop (1440px).

---

## 5. Safety Checkpoints & Backups
- Baseline DB Backup Created: `backend/energy_mirror_phase0_baseline.db.bak`
- Pre-Events DB Backup: `backend/energy_mirror_pre_events.db.bak`
- All tests run against isolated mock/in-memory fixtures; zero production telemetry was overwritten.
