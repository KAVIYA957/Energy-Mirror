# Energy Mirror Milestone 2C.15: PostgreSQL and Alembic Migration Report

**Date:** 2026-10-21  
**Project:** Energy Mirror  
**Project Path:** `C:\Users\Kaviya\Downloads\Energy Mirror`  
**Starting Commit:** `a3c6f40` (`feat(security): harden api configuration and appliance administration`)  
**Target Commit:** `feat(database): add postgres support and alembic migrations`  

---

## 1. Executive Summary & Objective

The objective of Milestone 2C.15 was to implement dual-database support (SQLite for local demo development and PostgreSQL for production deployments) along with an Alembic database migration pipeline, while strictly maintaining the zero-hardware, simulation-only constraints and preserving all existing local demo data.

### Critical Invariants & Constraints Maintained
* **Hardware Ingestion Inactive:** `ENABLE_HARDWARE_INGEST=false` is strictly maintained. The system remains 100% software- and simulation-based.
* **Deterministic Accounting Invariant:** Aggregate power strictly equals the sum of attributed appliance loads plus the assumed 12.0 W background residual floor ($P_{\text{agg}} = \sum P_{\text{attr}} + 12.0\text{ W}$).
* **Dynamic Appliance Registry & Defaults:** The 4 default appliances (Water Heater 140 W, Water Pump 75 W, Ceiling Fan 45 W, LED Bulb 12 W) remain idempotent and fully operational.
* **Non-Destructive Migration:** Existing SQLite databases (`energy_mirror.db`) are stamped at head revision without dropping tables or losing telemetry/event history.
* **Truth in Reporting:** Live PostgreSQL runtime verification was tested for local daemon availability; because no daemon was active on port 5432, PostgreSQL runtime execution is explicitly recorded as **NOT PERFORMED / UNVERIFIED AT RUNTIME** rather than claiming an unverified pass.

---

## 2. Dual-Database Architecture & Configuration

### 2.1 Connection URL Normalization
Cloud providers and Docker environments frequently provide database URLs formatted as `postgres://` or `postgresql://`. SQLAlchemy 2.0 requires dialect-specific drivers (such as `postgresql+psycopg2://`). 

In `backend/app/db/session.py`, `normalize_database_url` was implemented:
* Automatically translates `postgres://` and `postgresql://` prefixes to `postgresql+psycopg2://`.
* Preserves explicit drivers (e.g., `postgresql+psycopg2://` or `postgresql+asyncpg://`).
* Preserves SQLite URLs (e.g., `sqlite:///./energy_mirror.db`).
* Falls back safely to default SQLite if empty or unset.

### 2.2 Engine & Connection Pool Isolation
Database engines are conditionally configured based on the resolved dialect:
* **SQLite:** Configured with `connect_args={"check_same_thread": False}` to allow multi-threaded FastAPI workers to share the connection safely, with `StaticPool` utilized in test environments.
* **PostgreSQL:** Configured with production connection pooling:
  * `pool_pre_ping=True`: Proactively validates stale connections before executing queries.
  * `pool_size=10`: Baseline connection pool size.
  * `max_overflow=20`: Burst capacity for concurrent request spikes.
  * `pool_recycle=3600`: Recycles connections hourly to prevent server-side disconnects.

### 2.3 Dynamic Diagnostics Reporting
The system diagnostics endpoint (`GET /api/v1/diagnostics/system` in `backend/app/api/diagnostics.py`) was updated to dynamically detect and report the active database engine type:
* `"database_type": "SQLite"` when running SQLite.
* `"database_type": "PostgreSQL"` when `DATABASE_URL` specifies PostgreSQL.

---

## 3. Alembic Migration Pipeline

### 3.1 Migration Environment Configuration
* **Dependencies:** Added `alembic>=1.13.0` and `psycopg2-binary>=2.9.9` to `backend/requirements.txt` and installed them into `backend/.venv`.
* **Alembic Initialization:** Configured `backend/alembic.ini` and `backend/alembic/env.py`.
* **Metadata Binding:** `target_metadata` binds to `Base.metadata` from `app.db.models`, which explicitly imports:
  * `TelemetryModel` (`telemetry_records`)
  * `ApplianceEstimateModel` (`appliance_estimates`)
  * `DetectedEventModel` (`detected_events`)
  * `ApplianceDefinitionModel` (`appliance_definitions`)
* **SQLite Batch Mode:** Configured `render_as_batch=True` for SQLite connections to permit schema alterations (such as column additions, drops, or constraint modifications) without table locking issues.
* **Resolution Order in `env.py`:**
  1. CLI argument `-x url=<db_url>`
  2. Programmatic `sqlalchemy.url` override (used in isolated pytest test runs)
  3. `settings.DATABASE_URL` from application environment
  4. Fallback: `sqlite:///./energy_mirror.db`

### 3.2 Initial Migration Revision
* **Revision ID:** `8f8361eca0e9`
* **File:** `backend/alembic/versions/8f8361eca0e9_initial_schema_telemetry_appliances_.py`
* **Tables Created:**
  1. `telemetry_records`: Stores aggregate power, voltage, current, power factor, frequency, and timestamp.
  2. `appliance_estimates`: Foreign-keyed to `telemetry_records`, storing individual disaggregated appliance active power.
  3. `detected_events`: Durable storage for NILM step transitions ($\Delta P$, $\Delta\text{PF}$, status, rule description, fingerprint).
  4. `appliance_definitions`: Dynamic appliance registry (nominal power, tolerances, confidence, evidence notes).
  5. `alembic_version`: Tracks migration state.

---

## 4. Migration Operational Guide

### 4.1 Checking Migration Status
To inspect the current database migration revision:
```powershell
cd "C:\Users\Kaviya\Downloads\Energy Mirror\backend"
& ".\.venv\Scripts\alembic.exe" current
```
*Output on initialized SQLite database:*
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
8f8361eca0e9 (head)
```

To list target head revisions:
```powershell
& ".\.venv\Scripts\alembic.exe" heads
```

### 4.2 Upgrading the Database
To upgrade a fresh or outdated database to the latest schema:
```powershell
# For default configured database (.env or SQLite fallback):
& ".\.venv\Scripts\alembic.exe" upgrade head

# For an explicit target database (e.g., PostgreSQL staging):
& ".\.venv\Scripts\alembic.exe" -x url="postgresql+psycopg2://user:password@pg-host:5432/energy_mirror" upgrade head
```

### 4.3 Stamping an Existing Database
If an existing SQLite database already contains tables created via `create_all()`, stamp it at head without re-executing `CREATE TABLE`:
```powershell
& ".\.venv\Scripts\alembic.exe" stamp head
```

### 4.4 Generating Future Migrations
When SQLAlchemy models in `backend/app/db/models.py` are modified:
```powershell
& ".\.venv\Scripts\alembic.exe" revision --autogenerate -m "describe_changes"
```
Review the generated file under `backend/alembic/versions/`, adjust batch operations if necessary, and apply with `alembic upgrade head`.

---

## 5. Automated Test Results & Verification

All test suites across backend, ML experiments, and Flutter frontend were executed and verified:

### 5.1 Backend Pytest Suite
Command: `backend\.venv\Scripts\pytest.exe backend\tests`
* **Total Tests:** 92
* **Passed:** 92 (100%)
* **Failed / Errors:** 0
* **Execution Time:** 4.20s

Specific database and migration tests in `backend/tests/test_database_and_migrations.py` (11 passed):
1. `TestDatabaseUrlNormalization::test_legacy_postgres_url_normalized` (PASSED)
2. `TestDatabaseUrlNormalization::test_standard_postgresql_url_normalized_to_psycopg2` (PASSED)
3. `TestDatabaseUrlNormalization::test_explicit_driver_postgresql_url_preserved` (PASSED)
4. `TestDatabaseUrlNormalization::test_sqlite_url_preserved` (PASSED)
5. `TestDatabaseUrlNormalization::test_empty_or_none_url_fallback` (PASSED)
6. `TestAlembicMigrations::test_upgrade_from_empty_database` (PASSED - verified table creation and indexes from scratch)
7. `TestAlembicMigrations::test_repeat_upgrade_idempotency` (PASSED - verified idempotency of repeated upgrades)
8. `TestAlembicMigrations::test_downgrade_and_reupgrade_cycle` (PASSED - verified complete downgrade to base and re-upgrade)
9. `TestAlembicMigrations::test_seeding_and_persistence_on_migrated_db` (PASSED - verified appliance registry seeding and event persistence)
10. `TestDiagnosticsDatabaseType::test_diagnostics_reports_sqlite_by_default` (PASSED)
11. `TestDiagnosticsDatabaseType::test_diagnostics_reports_postgresql_when_configured` (PASSED)

### 5.2 Machine Learning Experiment Test Suite
Command: `& "backend\ml_experiments\.venv_ml\Scripts\python.exe" -m unittest discover -s backend\ml_experiments\tests`
* **Total Tests:** 63
* **Passed:** 63 (100%)
* **Execution Time:** 0.079s

### 5.3 Flutter Frontend Test Suite
Command: `flutter test` (in `mobile/`)
* **Total Tests:** 34
* **Passed:** 34 (100%)
* **Execution Time:** 9s

### 5.4 Flutter Static Analysis
Command: `flutter analyze` (in `mobile/`)
* **Issues Found:** 0 (ran in 4.6s)

### 5.5 Flutter Web Release Build
Command: `flutter build web --release` (in `mobile/`)
* **Result:** `√ Built build\web` (completed in 50.5s)

### 5.6 Live Backend Endpoint Verification
Tested against running daemon at `http://127.0.0.1:8000`:
* `GET /api/v1/diagnostics/system`:
  * `"status": "healthy"`
  * `"active_telemetry_source": "SIMULATED"`
  * `"hardware_ingestion_enabled": false`
  * `"hardware_mode": "STAGED_INACTIVE"`
  * `"database_connected": true`
  * `"database_type": "SQLite"`
  * `"simulator_aggregate_w": 284.0`
  * `"unattributed_baseline_w": 12.0`
* `GET /api/v1/appliances`:
  * `"count": 4`
  * Water Heater (140.0 W, PF 0.99)
  * Water Pump (75.0 W, PF 0.78)
  * Ceiling Fan (45.0 W, PF 0.91)
  * LED Bulb (12.0 W, PF 0.85)

---

## 6. PostgreSQL Verification Disclosure (Truth in Reporting)

In adherence to project truth-in-reporting guidelines:
* **Port 5432 Listener Check:** Verified via PowerShell:
  ```powershell
  Test-NetConnection -ComputerName 127.0.0.1 -Port 5432 -InformationLevel Quiet
  # Output: False
  ```
* **PostgreSQL Runtime Verification Status:** Because no local PostgreSQL server was running on the test machine, runtime database queries against a live PostgreSQL daemon are categorized as **NOT PERFORMED / UNVERIFIED AT RUNTIME**.
* **Syntactic and Structural Coverage:** URL parsing, normalization to `postgresql+psycopg2`, dialect identification, dynamic diagnostic reporting, and Alembic batch migration generation were verified via automated tests. Passing SQLite tests must not be claimed as verification of live PostgreSQL runtime behavior.

---

## 7. Modified and Added Repository Files

| File | Status | Description |
| :--- | :--- | :--- |
| `backend/requirements.txt` | Modified | Added `alembic>=1.13.0` and `psycopg2-binary>=2.9.9`. |
| `backend/.env.example` | Modified | Documented SQLite default and PostgreSQL `DATABASE_URL` format. |
| `backend/app/db/session.py` | Modified | Added `normalize_database_url`, SQLite vs PostgreSQL engine options, and connection pooling. |
| `backend/app/api/diagnostics.py` | Modified | Added dynamic `database_type` reporting ("SQLite" vs "PostgreSQL"). |
| `backend/alembic.ini` | Added | Alembic configuration with dynamic URL resolution. |
| `backend/alembic/env.py` | Added | Alembic migration runner binding `Base.metadata`, batch mode for SQLite, and URL prioritization. |
| `backend/alembic/script.py.mako` | Added | Template for autogenerated migrations. |
| `backend/alembic/versions/8f8361eca0e9_initial_schema_telemetry_appliances_.py` | Added | Initial migration revision covering all 4 application tables. |
| `backend/tests/test_database_and_migrations.py` | Added | 11 unit and integration tests for migrations, idempotency, downgrades, and URL normalization. |
| `KNOWN_LIMITATIONS.md` | Modified | Added Section 9 documenting dual-database support and PostgreSQL runtime verification status. |
| `POSTGRESQL_ALEMBIC_MIGRATION_REPORT.md` | Added | This comprehensive milestone report. |
