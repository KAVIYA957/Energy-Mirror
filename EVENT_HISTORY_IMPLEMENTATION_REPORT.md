# Energy Mirror: Persistent Event History Implementation Report

**Project Path:** `C:\Users\Kaviya\Downloads\Energy Mirror`  
**Execution Date:** 2026-10-20  
**Status:** **IMPLEMENTED & VERIFIED**  
**Data Integrity:** All telemetry is **SIMULATED**; event classifications are **RULE_BASED_ESTIMATE**. Hardware ingestion remains **STAGED / INACTIVE** (`ENABLE_HARDWARE_INGEST=false`).

---

## 1. Executive Summary

This report documents the implementation of durable event storage for Energy Mirror's rule-based detected events, bridging the previously in-memory transient event ring buffer with SQLite persistent storage and integrating it directly into the **Analytics & History** screen.

All operations were executed without altering working modules, modifying the Living Current design language, or disturbing existing telemetry records.

---

## 2. Schema and API Changes

### A. SQLite Schema (`detected_events` table)
Added `DetectedEventModel` to `backend/app/db/models.py`:

```python
class DetectedEventModel(Base):
    __tablename__ = "detected_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    status = Column(String(32), index=True, nullable=False)          # "MATCHED", "AMBIGUOUS"
    appliance_id = Column(String(64), nullable=True, index=True)    # Inferred appliance ID or None
    appliance_name = Column(String(128), nullable=True)             # Inferred name or None
    transition_type = Column(String(16), nullable=True)             # "ON", "OFF", None
    delta_power_w = Column(Float, nullable=False)                   # Signed aggregate power derivative
    delta_pf = Column(Float, nullable=True)                         # Observed power-factor delta
    rule_description = Column(Text, nullable=False)                 # Tolerance envelope matching reasoning
    data_classification = Column(String(64), default="RULE_BASED_ESTIMATE", nullable=False)
    event_fingerprint = Column(String(128), unique=True, index=True, nullable=True) # Deduplication key
```

### B. Pydantic Schemas (`backend/app/schemas/telemetry.py`)
1. **`PersistedEventSchema`**:
   Exposes the full typed event payload with `id`, `timestamp`, `status`, `appliance_id`, `appliance_name`, `transition_type`, `delta_power_w`, `delta_pf`, `rule_description`, and `data_classification`.
2. **`HistoryResponse` Extension**:
   Extended with `events: List[PersistedEventSchema] = Field(default_factory=list)`, preserving 100% backward compatibility with prior frontend clients.
3. **`DetectedEventSchema` Update** (`backend/app/schemas/simulator.py`):
   Added `delta_pf: Optional[float] = None`.

### C. REST API Endpoints
1. **`GET /api/v1/telemetry/events` (New Dedicated Endpoint):**
   - Query Parameters: `minutes: int = Query(default=60, ge=5, le=1440)`
   - Response: `List[PersistedEventSchema]` ordered descending by timestamp (newest first).
2. **`GET /api/v1/telemetry/history` (Extended):**
   - Query Parameters: `minutes: int = Query(default=60, ge=5, le=1440)`
   - Response: `HistoryResponse` now includes the `events` array alongside historical power points.
3. **`POST /api/v1/simulator/toggle-appliance` (Durable Persistence):**
   - Injected database session dependency (`db: Session = Depends(get_db)`).
   - Automatically invokes `telemetry_service.persist_detected_event(db, event)` upon state transitions.

---

## 3. Event Generation and Persistence Flow

```
Virtual Appliance Toggle (Simulator Lab)
                │
                ▼
Calculate Aggregate Active Power & Composite Power Factor
   P_curr - P_prev = ΔP,   PF_curr - PF_prev = ΔPF
                │
                ▼
RuleBasedEventDetector.detect_transition(...)
   ├── Check Noise Floor (|ΔP| < 5.0 W) ──► status: NO_CHANGE (NOT persisted)
   ├── Match Single Envelope ──────────────► status: MATCHED (Persisted)
   ├── Multiple Matches ───────────────────► status: AMBIGUOUS (Persisted, no fake ID)
   └── Zero Matches / Multi-Load ──────────► status: AMBIGUOUS (Persisted, no fake ID)
                │
                ▼
TelemetryService.persist_detected_event(db, event)
   ├── Idempotency Check: Computes fingerprint {ISO_SEC}_{ΔP}_{STATUS}_{APPLIANCE}
   ├── Near-Time Window Check: Skips duplicates within ±2 seconds
   ├── Transaction Safety: db.add() ──► db.commit()
   └── Rollback on Concurrency Collision: db.rollback() ──► returns existing record
                │
                ▼
SQLite Database: `detected_events`
   Survives Server Restarts & In-Memory Simulator Resets
                │
                ▼
Analytics & History Screen (Flutter)
   Renders "DURABLE EVENT ARCHIVE (SQLITE)" with status badges, timestamps, ΔP, ΔPF, and rules
```

---

## 4. Test Verification Results

All tests were executed against active builds. The development database was verified to remain untouched during automated tests.

### A. Backend Pytest (`python -m pytest -v`)
- **Total Tests:** **44 passed, 0 failed, 1 warning in 2.12s**
- **New Test Suite:** `tests/test_persistent_events.py` (6 new comprehensive tests):
  1. `test_successful_event_persistence`: Verified Water Heater OFF (-140 W) stores `MATCHED` record in `detected_events`.
  2. `test_event_retrieval_after_restart`: Verified events survive `simulator.reset()` and are retrievable via `/api/v1/telemetry/events`.
  3. `test_duplicate_prevention_during_repeated_polling_or_retries`: Verified identical fingerprint and within-window retries produce exactly 1 record.
  4. `test_ambiguous_event_persistence`: Verified uncalibrated/multi-load step (+215 W) stores `AMBIGUOUS` status without fabricated appliance ID.
  5. `test_no_event_creation_when_no_observed_transition`: Verified steady-state noise (< 5 W) and same-state toggles add zero records.
  6. `test_compatibility_with_existing_telemetry_history`: Verified `/api/v1/telemetry/history` returns points and events array simultaneously.

### B. Flutter Test Suite (`flutter test`)
- **Total Tests:** **29 passed, 0 failed in 7.0s**
- **New Test Suite:** `test/persistent_event_history_test.dart` (2 new tests):
  1. Verified rendering of durable archive header, distinct disclaimer, `MATCHED` item, and `AMBIGUOUS` item with power deltas, $\Delta\text{PF}$, and timestamps.
  2. Verified empty state when zero events exist in the selected window (`"No durable events recorded in this time window."`).
  3. Verified responsiveness: Replaced horizontal row with `Wrap` to ensure zero `RenderFlex` overflow on narrow viewports (393 × 852).

### C. Static Analysis (`flutter analyze`)
- **Result:** `No issues found! (ran in 5.3s)` (0 errors, 0 warnings, 0 lints).

### D. Production Web Build (`flutter build web --release`)
- **Result:** Clean compilation into `mobile/build/web` in 50.1s.

### E. Database Isolation & Row Count Immutability
- **Pre-Test Counts:** `telemetry_records: 213`, `appliance_estimates: 608`, `detected_events: 0`
- **Post-Test Counts:** `telemetry_records: 213`, `appliance_estimates: 608`, `detected_events: 0` (0 delta during test execution)

---

## 5. Migration and Rollback Strategy

### Migration Strategy
- SQLAlchemy's `Base.metadata.create_all(bind=engine)` runs on startup within the FastAPI lifespan handler in `backend/app/main.py`.
- It executes `CREATE TABLE IF NOT EXISTS detected_events (...)`.
- Existing tables `telemetry_records` and `appliance_estimates` are completely untouched.
- `seed_initial_history()` checks `db.query(DetectedEventModel).count() == 0` and seeds the baseline Water Pump event (from 42 minutes prior) only if the table is empty.

### Rollback Strategy
- A full binary database backup was created prior to changes: `backend/energy_mirror_pre_events.db.bak`.
- If rollback is ever required:
  1. Remove `DetectedEventModel` from `backend/app/db/models.py`.
  2. In SQLite: `DROP TABLE IF EXISTS detected_events;` or restore `backend/energy_mirror_pre_events.db.bak`.
  3. Revert `backend/app/api/telemetry.py` and `mobile/lib/core/models/telemetry_model.dart`.
  4. Existing telemetry history continues operating without disruption.

---

## 6. Known Limitations

1. **No Physical Metering Hardware:** No physical PZEM or ESP32 hardware is connected. Telemetry is `SIMULATED`, and event classification is `RULE_BASED_ESTIMATE`.
2. **Derivative Granularity:** The detector evaluates 1-second derivatives ($\Delta P, \Delta\text{PF}$). Simultaneous switching of multiple appliances within the same second is honestly classified as `AMBIGUOUS`.
3. **In-Memory Feed vs Durable Archive:** The Simulator Lab live event feed uses the in-memory ring buffer (`simulator.recent_events`) for real-time interactivity, while the Analytics & History screen queries the durable SQLite archive.
