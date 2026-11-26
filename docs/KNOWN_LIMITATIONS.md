# Energy Mirror: Known Limitations & Technical Boundaries

This document transparently records the architectural boundaries, algorithmic scope, and current physical constraints of the Energy Mirror prototype as of Milestone S3.

---

## 1. No Physical Meter or Hardware Connected
* **Current Status:** There is currently **zero physical hardware** connected to the Energy Mirror prototype. No physical PZEM-004T energy meter, current transformer (CT), or ESP32 microcontroller is integrated or transmitting live electrical data.
* **Ingestion State:** The backend configuration flag `ENABLE_HARDWARE_INGEST` is strictly set to `false`. The hardware ingestion endpoint (`POST /api/v1/ingest/telemetry`) is staged, isolated, and rejects unauthenticated or real-time calls.
* **Active Data Source:** All telemetry displayed on the Dashboard, Simulator Lab, and Analytics screens originates from the deterministic software simulator (`DATA_SOURCE = "SIMULATED"`).

---

## 2. No Trained NILM Machine Learning Model
* **Current Status:** The disaggregation engine does **not** use a trained deep learning or machine learning model (such as a CNN, RNN, or Sequence-to-Point neural network).
* **Classification Methodology:** Disaggregation is performed strictly via a transparent **rule-based derivative step detector** (`RULE_BASED_DERIVATIVE_ESTIMATOR`).
* **Truth in Reporting:** All disaggregated load estimates are explicitly labeled in the UI and API responses as **`RULE_BASED_ESTIMATE`** or **`NILM_ESTIMATED`**. The application never claims or generates fabricated confidence scores, ML model loss metrics, or validated F1 scores.

---

## 3. Algorithmic Scope of Rule-Based Event Detection
* **Detection Mechanism:** The detector evaluates step transitions in aggregate active power ($\Delta P = P_{\text{current}} - P_{\text{previous}}$) and power factor ($\Delta \text{PF}$) sampled at 1-second intervals.
* **Tolerance Envelopes:** Steps are mapped against configured calibrated envelopes:
  * Water Heater: $140.0\text{ W} \pm 12.0\text{ W}$ ($[128, 152]\text{ W}$, near-unity PF $\sim 0.99$)
  * Water Pump: $75.0\text{ W} \pm 9.0\text{ W}$ ($[66, 84]\text{ W}$, inductive PF $\sim 0.78$)
  * Ceiling Fan: $45.0\text{ W} \pm 7.0\text{ W}$ ($[38, 52]\text{ W}$, motor PF $\sim 0.91$)
  * LED Bulb: $12.0\text{ W} \pm 4.0\text{ W}$ ($[8, 16]\text{ W}$, non-linear PF $\sim 0.85$)
* **Noise Floor:** Any transition with $|\Delta P| < 5.0\text{ W}$ is classified as steady-state noise (`NO_CHANGE`).

---

## 4. Ambiguity Under Identical or Simultaneous Load Signatures
* **Identical Signatures:** If two physical appliances share similar nominal active power and power factor ratings (e.g., two identical 100 W incandescent lamps, or a 140 W toaster and a 140 W water heater), the 1-second derivative detector cannot distinguish between them without higher-frequency waveform harmonics or contextual state tracking.
* **Simultaneous Switching:** If two or more appliances switch within the same 1-second sampling window (e.g., Water Heater $140\text{ W}$ and Water Pump $75\text{ W}$ turn on simultaneously for a $+215\text{ W}$ step), the composite step does not match any single appliance signature. The detector honestly classifies such transitions as **`AMBIGUOUS`** rather than guessing.

---

## 5. Simulated Background Load Assumption
* **Baseline Assumption:** The continuous $12.0\text{ W}$ background load is a **model assumption** within the simulator to account for continuous household baselines.
* **No Phantom Load Detection:** The $12.0\text{ W}$ floor is **not** a physically measured vampire load, nor does it represent physically detected standby electronics or network hardware.
* **Separation of Loads:** The $12.0\text{ W}$ background floor is mathematically distinct from the $12.0\text{ W}$ LED bulb load. When all 4 virtual appliances are OFF, aggregate load is $12.0\text{ W}$ ($100\%$ unattributed). When the LED bulb is active, aggregate load is $24.0\text{ W}$ ($12\text{ W}$ attributed $+ 12\text{ W}$ background floor).

---

---

## 6. Real-World Accuracy Has Not Been Evaluated
* **Bench Evaluation Pending:** Real-world metrics (such as precision, recall, F1 score, or energy estimation error) have not been evaluated against physical household ground truth or public datasets (such as REDD, UK-DALE, or REFIT).
* **Future Work:** Supervised laboratory testing on physical hardware with reference power analyzers is planned for Milestone 4 to establish empirical accuracy baselines.

---

## 7. Event History Persistence Architecture
* **Durable SQLite Table (`detected_events`):** Transition events produced by the rule-based event detector upon observing aggregate electrical derivatives are durably persisted into the `detected_events` SQLite table. Stored fields include timestamp, signed power delta ($\Delta P$), power factor delta ($\Delta\text{PF}$), event status (`MATCHED` / `AMBIGUOUS`), inferred appliance identity, rule description, data classification (`RULE_BASED_ESTIMATE`), and an idempotent fingerprint.
* **Survival Across Server Restarts:** Persisted events survive backend process restarts and simulator resets, and are retrievable via `GET /api/v1/telemetry/events` and integrated into the `GET /api/v1/telemetry/history` response.
* **Separation of Concerns:** The transient in-memory ring buffer (`simulator.recent_events`, capped at 30 items) remains active to feed the live interactive toggle controls in Simulator Lab, while the durable SQLite archive backs the Analytics & History screen.


---

## 8. Automated Browser Testing Tool Limitations
* **Driver Download Failure:** In this execution environment, automated browser drivers (such as Playwright Chromium) could not be initialized due to upstream driver archive availability (HTTP 404 from CDN). Edge in headless agent sessions on Windows requires interactive GUI display permissions.
* **Verification Scope:** UI layout, component rendering, responsiveness, and state management are verified through Flutter widget tests (34 passing tests), API integration tests, and manual visual inspection via installed browsers (Microsoft Edge / Google Chrome / Mobile Safari/Chrome via LAN IP `http://192.168.29.166:8080`). Automated browser driver checks are strictly categorized as **NOT VERIFIED**.

---

## 9. Database Support & PostgreSQL Runtime Verification Status
* **Active Default Database:** SQLite (`sqlite:///./energy_mirror.db`) remains the active default database engine for all local development, simulation, and demonstration workflows.
* **PostgreSQL Architecture:** The codebase includes production-grade PostgreSQL compatibility, including SQLAlchemy connection URL normalization (`postgres://` / `postgresql://` $\rightarrow$ `postgresql+psycopg2://`), connection pooling (`pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`), and Alembic schema migrations (`alembic upgrade head`).
* **Runtime Verification Status (Truth in Reporting):** In this development environment, no PostgreSQL daemon was listening on port 5432. Therefore, live PostgreSQL runtime integration testing is classified as **NOT PERFORMED / UNVERIFIED AT RUNTIME**. SQLite migrations, schema creation, downgrade/re-upgrade cycles, and URL normalization were 100% verified via automated tests, but passing SQLite tests must not be claimed as verification of live PostgreSQL runtime behavior.

