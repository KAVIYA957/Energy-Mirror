# Dynamic Appliance Registry Report
**Milestone 2C.13 Completion Audit & Architectural Documentation**

**Project**: Energy Mirror  
**Starting Commit**: `53a0e55` (`audit(project): assess full-stack completion and security`)  
**Target Milestone**: 2C.13 (Dynamic Appliance Registry)  
**Safety Constraints**: `ENABLE_HARDWARE_INGEST=false` strictly preserved; 100% software & simulation; no physical hardware assembled, connected, or tested.

---

## Executive Summary

Prior to Milestone 2C.13, Energy Mirror had static four-appliance assumptions baked into several core subsystems:
1. `TelemetrySimulator` held an immutable dictionary of 4 appliances (`heater_01`, `pump_01`, `fan_01`, `bulb_01`).
2. `RuleBasedEventDetector` initialized an immutable list of 4 calibrated step signatures.
3. Database models lacked an appliance definition entity, relying solely on telemetry snapshot child rows.
4. The Flutter UI contained fallback switch cases assuming the nominal wattage was only known for those 4 appliances.

Milestone 2C.13 successfully removed this four-appliance hardcoding by establishing a database-backed **Dynamic Appliance Registry** (`ApplianceDefinitionModel` and `ApplianceRegistry`). The system now natively supports an arbitrary, variable number of appliance definitions while strictly preserving:
- The default four simulator appliances and their exact ratings: Water Heater (140 W), Water Pump (75 W), Ceiling Fan (45 W), and LED Bulb (12 W).
- The fundamental simulator invariant: $P_{\text{agg}} = \sum P_{\text{attr}} + 12.0\text{ W}$ residual floor across any number of appliances (0, 1, 4, or $>4$).
- **Strict detection honesty**: A registered appliance definition is not assumed to be recognized by NILM simply because its record exists. Unsupported appliances default to `detection_capability = "UNSUPPORTED"` and display as `SIMULATED` without fabricating classification events.

---

## 1. What Was Hardcoded vs. What Became Dynamic

| Subsystem | Previous State (Hardcoded 4-Device) | Milestone 2C.13 Dynamic Architecture |
| :--- | :--- | :--- |
| **Appliance Storage** | Static in-memory Python dictionary in `simulator.py` | SQLite table `appliance_definitions` managed via `ApplianceRegistry` service with CRUD methods |
| **Simulator Topology** | Exactly 4 virtual appliances initialized at boot | Dynamic dictionary synced from `ApplianceRegistry`; supports arbitrary $N$ appliances |
| **Detector Signatures** | Static list of 4 hardcoded `ApplianceSignature` tuples | Dynamic synchronization via `sync_from_registry(db)`; loads only definitions with `PRODUCTION_RULE_MATCHED` and calibrated envelopes |
| **Nominal Power** | Flutter UI had switch statement hardcoded for 4 IDs | Backend sends `nominal_power_w` in `ApplianceEstimateSchema`; Flutter UI reads dynamic rating with fallback |
| **Capability Status** | Implicitly assumed all 4 devices were rule-detected | Explicit `detection_capability` enum (`PRODUCTION_RULE_MATCHED`, `UNSUPPORTED`, `EXPERIMENTAL_ONLY`); UI badges reflect true capability |
| **UI Constellation** | Dynamic grid already in place, but detail sheet had static labels | UI truthfully displays `SIMULATED ONLY` vs `RULE-BASED ESTIMATE` based on backend capability flag |

---

## 2. Registry Architecture and Data Model

### Database Entity (`backend/app/db/models.py`)
```python
class ApplianceDefinitionModel(Base):
    __tablename__ = "appliance_definitions"

    id = Column(Integer, primary_key=True, index=True)
    appliance_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    category = Column(String(64), default="General", nullable=False)
    nominal_power_w = Column(Float, nullable=False)
    expected_pf = Column(Float, nullable=True)
    tolerance_w = Column(Float, nullable=True)
    pf_tolerance = Column(Float, nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_simulator_supported = Column(Boolean, default=True, nullable=False)
    detection_capability = Column(String(64), default="UNSUPPORTED", nullable=False)
    confidence_score = Column(Float, nullable=True)
    evidence_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### Protection of Default Baseline Appliances
To prevent accidental regression of existing tests and demo scenarios, the 4 default appliance identifiers (`heater_01`, `pump_01`, `fan_01`, `bulb_01`) are protected against deletion. They can be disabled (`is_enabled=False`), which removes them from active simulation and filtering without deleting baseline records.

### Input Validation Rules
1. `appliance_id`: Regex validated (`^[a-zA-Z0-9_\-]+$`), 2 to 64 characters, uniqueness enforced at DB level.
2. `nominal_power_w`: Must be strictly positive ($> 0.0$ W) and within realistic physical bounds ($\le 25,000$ W).
3. `detection_capability`: If set to `PRODUCTION_RULE_MATCHED`, validation strictly enforces that a positive `tolerance_w` envelope is provided. Uncalibrated loads default to `UNSUPPORTED`.

---

## 3. API and Frontend Integration

### REST API Endpoints (`/api/v1/appliances`)

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/appliances` | List all appliance definitions (supports `?enabled_only=true`) | `200 OK` |
| `GET` | `/api/v1/appliances/{id}` | Retrieve single appliance definition by ID | `200 OK` / `404 Not Found` |
| `POST` | `/api/v1/appliances` | Register new appliance definition with validation | `201 Created` / `409 Conflict` / `422 Unprocessable` |
| `PATCH`| `/api/v1/appliances/{id}`| Update properties of an existing appliance | `200 OK` / `404 Not Found` / `422 Unprocessable` |
| `DELETE`|`/api/v1/appliances/{id}`| Delete custom appliance (protected baseline IDs blocked) | `200 OK` / `400 Bad Request` / `404 Not Found` |

### Security Note
In accordance with project guidelines, while authentication is absent in the current local development / demo phase, administrative mutation endpoints (`POST`, `PATCH`, `DELETE`) are documented for local and developer configuration.

### Extended Schemas
- `ApplianceEstimateSchema`: Extended with `nominal_power_w: Optional[float]` and `detection_capability: Optional[str]`.
- `SimulatorApplianceState`: Extended with `detection_capability: Optional[str]`.

### Frontend Updates
- `mobile/lib/core/models/simulator_model.dart`: Added `detectionCapability` field to `SimulatorAppliance`.
- `mobile/lib/core/models/telemetry_model.dart`: Added `nominalPowerW` and `detectionCapability` fields to `ApplianceEstimate`.
- `mobile/lib/features/dashboard/widgets/appliance_node.dart`: Reads `nominalPowerW` directly from model; dynamically renders `SIMULATED` badge instead of `RULE-BASED` when `detectionCapability == 'UNSUPPORTED'`.
- `mobile/lib/features/dashboard/widgets/simulator_lab_panel.dart`: Renders `UNMATCHED` tag next to uncalibrated simulator appliances.
- `mobile/lib/features/dashboard/widgets/appliance_detail_sheet.dart`: Displays truthful detection method (`Simulated Only (No Calibrated NILM Envelope)` vs `Rule-Based Step Classifier`).

---

## 4. Preservation of Simulator Invariants

The simulator invariant:
$$\text{Aggregate Power } P_{\text{agg}} = \sum_{i \in \text{Active}} P_{\text{nominal}, i} + P_{\text{unattributed}} \quad (P_{\text{unattributed}} = 12.0\text{ W})$$
holds strictly for any number of active appliances:
- **0 appliances active**: Attributed power = $0.0$ W, Aggregate power = $12.0$ W (exact background residual floor).
- **1 appliance active** (`pump_01` = 75 W): Attributed power = $75.0$ W, Aggregate power = $87.0$ W.
- **Default 4 appliances active** (140 + 75 + 45 + 12 = 272 W): Attributed power = $272.0$ W, Aggregate power = $284.0$ W.
- **5 appliances active** (+ 800 W Toaster): Attributed power = $1072.0$ W, Aggregate power = $1084.0$ W.

---

## 5. Preservation of Detection Honesty

The production `RuleBasedEventDetector` does **not** recognize new appliances by name alone:
- When a 5th appliance (e.g. `toaster_01`, 800 W) is registered with `detection_capability="UNSUPPORTED"`, it is **not** loaded into `detector.signatures`.
- When toggled in the simulator, the aggregate power steps by $+800$ W.
- Because no production rule matches an 800 W step, the detector accurately outputs:
  - `status = "AMBIGUOUS"`
  - `appliance_id = None`
  - `rule_description = "Unrecognized transition: Step of +800.0 W does not match any single appliance signature."`
- The system never hallucinates an appliance name for uncalibrated loads.

---

## 6. Comprehensive Test Results

All four test suites were executed with zero failures:

### 1. Backend Tests (Pytest)
```
backend\tests\test_appliance_registry.py ...............                 [ 23%]
backend\tests\test_diagnostics.py .                                      [ 25%]
backend\tests\test_event_detector.py ..........                          [ 41%]
backend\tests\test_health.py ..                                          [ 44%]
backend\tests\test_history.py ...                                        [ 49%]
backend\tests\test_ingest.py .......                                     [ 60%]
backend\tests\test_integration.py .                                      [ 61%]
backend\tests\test_nilm.py .                                             [ 63%]
backend\tests\test_persistent_events.py ..........                       [ 79%]
backend\tests\test_simulator.py ..                                       [ 82%]
backend\tests\test_simulator_dynamic.py ..........                       [ 98%]
backend\tests\test_telemetry.py .                                        [100%]
======================== 63 passed, 1 warning in 3.16s ========================
```

### 2. ML Experiment Tests (Unittest)
```
Ran 63 tests in 0.082s
OK
```

### 3. Flutter Widget and Integration Tests
```
Ran 34 tests in 00:09
00:09 +34: All tests passed!
```
Including new dynamic rendering tests in `mobile/test/dynamic_appliance_rendering_test.dart`:
- Empty state: renders fallback banner when 0 appliances present.
- One-device state: renders single card with correct nominal rating.
- Default 4-device state: renders all four baseline appliances.
- Variable state: renders 6 devices dynamically.
- Detection honesty badge: unsupported appliance displays `SIMULATED` badge.

### 4. Flutter Static Analysis (`flutter analyze`)
```
Analyzing mobile...
No issues found! (ran in 4.6s)
```

**Total Verified Tests**: 160 passed, 0 failed.

---

## 7. Remaining Detector Limitations

1. **Threshold Overlap**: If multiple appliances have overlapping power envelopes (e.g. two 75 W loads), the rule-based detector classifies the step as `AMBIGUOUS`.
2. **Dynamic Inrush & Variable Speed**: The production detector uses a 1 Hz active power step classifier; it cannot disaggregate variable-speed inverter compressors or complex multi-stage cycles without high-frequency transient or continuous state machine modeling.
3. **Requirement for Physical Ground Truth**: Adding new production signatures requires empirical calibration data from real metrology or benchmark datasets with verified ground truth submetering, rather than arbitrary nominal configuration.

---

## 8. Conclusion: Registry Support vs. Measurement Recognition

There is a fundamental metrological difference between:
- **Supporting an appliance record**: Storing an entry in a database with display metadata, nominal ratings, and simulation parameters.
- **Recognizing an appliance from aggregate measurements**: Inverting an underdetermined single-channel electrical mixture $P(t) = \sum p_i(t)$ into individual disaggregated load states with verified precision and recall.

Energy Mirror Milestone 2C.13 successfully separates these two concerns. The platform can now manage an open-ended catalog of appliances and simulate realistic multi-load environments, while maintaining strict scientific and engineering honesty regarding what the production event detector can and cannot recognize.
