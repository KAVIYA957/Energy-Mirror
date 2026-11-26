# Energy Mirror: Live Demonstration & Reproduction Guide

**Project Path:** `C:\Users\Kaviya\Downloads\Energy Mirror`  
**Design Identity:** Luminous Clarity (Light-First, WCAG AAA Accessible, High Legibility)  
**Milestone State:** Milestone 2C.17 (Demo Polish & Reproducibility)  
**Data Integrity:** All telemetry is **`SIMULATED`**; all disaggregation is **`RULE-BASED ESTIMATE`**. Hardware ingestion is **`STAGED_INACTIVE`** (`ENABLE_HARDWARE_INGEST=false`).

---

## 1. Quick Startup Instructions

For the smoothest demonstration experience without CORS configuration or IP routing issues, use the **Unified Web & Proxy Server** on port 5000.

### Automated Diagnostic Check (Optional but Recommended)
Before starting, run the automated dependency and port conflict assistant in PowerShell:
```powershell
cd "C:\Users\Kaviya\Downloads\Energy Mirror"
powershell -ExecutionPolicy Bypass -File .\start_demo.ps1
```
This script checks the Python virtualenv, Flutter web bundle, SQLite database, and port availability without modifying any database or configuration.

---

### Standard Two-Terminal Startup

#### Terminal 1: Backend API Gateway (FastAPI)
```powershell
cd "C:\Users\Kaviya\Downloads\Energy Mirror"
& ".\backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```
* **API Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
* **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **System Diagnostics Endpoint:** [http://localhost:8000/api/v1/diagnostics/system](http://localhost:8000/api/v1/diagnostics/system)
* **Dynamic Appliance Registry:** [http://localhost:8000/api/v1/appliances](http://localhost:8000/api/v1/appliances)
* **Persistent Event History:** [http://localhost:8000/api/v1/telemetry/events](http://localhost:8000/api/v1/telemetry/events)

#### Terminal 2: Unified Web & API Proxy (Recommended)
```powershell
cd "C:\Users\Kaviya\Downloads\Energy Mirror"
& ".\backend\.venv\Scripts\python.exe" unified_server.py
```
* **Primary Web URL:** [http://localhost:5000](http://localhost:5000) *(or [http://127.0.0.1:5000](http://127.0.0.1:5000))*
* **Mobile Browser on Wi-Fi:** `http://<YOUR_PC_IP>:5000` (e.g., `http://192.168.29.166:5000`)
* **Active Cloudflare Tunnel (External Access):** `https://nations-assistance-highway-roof.trycloudflare.com`

*(Alternative: If you prefer standalone static hosting on port 8080, run `& ".\backend\.venv\Scripts\python.exe" serve_web.py 8080`)*

---

### Safe Process Shutdown
To stop the services safely:
1. In each active terminal window, press **`Ctrl + C`**.
2. If any background Python process continues holding ports 8000 or 5000, stop it in PowerShell:
   ```powershell
   Get-Process python | Where-Object { $_.Path -like "*Energy Mirror*" } | Stop-Process -Force
   ```

---

## 2. Baseline Simulator Values & Physical Accounting Invariant

When the simulator is initialized or reset via **"Reset Simulator"**, it deterministically restores this exact baseline:

| Appliance / Component | Nominal Power | Power Factor | Default Status | Attributed Load | Detection Capability |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Water Heater** | **140.0 W** | 0.99 (Resistive) | ON | 140.0 W | `PRODUCTION_RULE_MATCHED` ($\pm 12$ W) |
| **Water Pump** | **75.0 W** | 0.78 (Inductive) | ON | 75.0 W | `PRODUCTION_RULE_MATCHED` ($\pm 9$ W) |
| **Ceiling Fan** | **45.0 W** | 0.91 (Motor) | ON | 45.0 W | `PRODUCTION_RULE_MATCHED` ($\pm 7$ W) |
| **LED Bulb** | **12.0 W** | 0.85 (Lighting) | ON | 12.0 W | `PRODUCTION_RULE_MATCHED` ($\pm 4$ W) |
| **Total Attributed Load** | — | — | — | **272.0 W** | — |
| **Simulated Background Load** | **12.0 W** | 0.90 (Baseline Floor) | Always Active | **12.0 W** | Assumed Baseline Model Floor |
| **Total Aggregate Power** | — | — | — | **284.0 W** | — |

### Mandatory Physical Accounting Invariant
$$P_{\text{aggregate}} (W) \equiv \sum P_{\text{attributed}} (W) + \text{Simulated Background Load } (12.0\text{ W})$$

> [!NOTE]
> **Methodological Note on Background Load:**  
> The 12.0 W background load is an assumed constant floor within our simulation model to account for continuous household standby electronics. It is **not** a physically measured vampire load. Notice that the LED bulb's 12.0 W is strictly separate: when only the LED bulb is active, aggregate power is $12\text{ W} + 12\text{ W} = 24.0\text{ W}$.

---

## 3. Step-by-Step 9-Stage Demonstration Sequence

Follow this exact sequence during presentations and technical reviews:

```
[1. Dashboard Overview] -> [2. Four Appliances] -> [3. 284W Baseline]
         |
         v
[4. Toggle Heater OFF]  -> [5. Verify 144W & Event] -> [6. Reset Baseline]
         |
         v
[7. History & Diag]     -> [8. Unsupported Reg]     -> [9. Data Transparency]
```

### Stage 1: Dashboard Overview & Simulation Mode
* **Screen:** Dashboard (`/`) at `http://localhost:5000`
* **Action:** Point out the top hero card displaying **284 W** and the explicit **`SIMULATED DATA`** badge.
* **Explanation:** Clarify that this is an end-to-end prototype running on simulated 1 Hz telemetry; no live hardware is attached.

### Stage 2: Four Recognized Default Appliances
* **Screen:** Dashboard (`/`) - scroll to the Recognized Appliances Grid.
* **Action:** Point out the 4 recognized cards with 3D isometric visual renders:
  1. Water Heater: 140 W
  2. Water Pump: 75 W
  3. Ceiling Fan: 45 W
  4. LED Bulb: 12 W
* **Action:** Tap the **Water Pump** card to open the **Inference Evidence & Reasoning** modal: show inductive motor signature notes and calibrated power factor envelope (PF ~ 0.78).

### Stage 3: Baseline Power Reconciliation (284 W)
* **Screen:** Dashboard (`/`) - inspect the Load Reconciliation bar.
* **Action:** Highlight that the attributed load is 272.0 W (95.8%) and the unattributed background floor is 12.0 W (4.2%).
* **Verification:** $272.0\text{ W} + 12.0\text{ W} = 284.0\text{ W}$.

### Stage 4 & 5: Toggle Water Heater OFF & Observe Event
* **Screen:** Appliance Simulator (`/simulator`)
* **Action:** Toggle the **Water Heater** switch from ON to OFF.
* **Observation:**
  - Live aggregate power drops immediately from $284.0\text{ W} \rightarrow \mathbf{144.0\text{ W}}$.
  - The live event feed registers: **`MATCHED: Water Heater OFF (-140.0 W)`**.
* **Key Talking Point:** The event detector was **never informed** which switch the user flipped. It independently observed the mathematical step derivative ($\Delta P = -140.0\text{ W}$) in aggregate telemetry and matched it against its calibrated tolerance bounds ($140.0 \pm 12.0\text{ W}$).

### Stage 6: Restore Simulator Baseline
* **Screen:** Appliance Simulator (`/simulator`)
* **Action:** Click **"Reset Simulator"**.
* **Observation:** The simulator deterministically restores all 4 appliances to ON and returns aggregate power to **284.0 W**.

### Stage 7: History & System Diagnostics
* **Screen:** History & Analytics (`/history`)
  - Show the interactive FL Chart with smooth power curve and solar amber event markers.
  - Scroll down to the **Durable Detected Events** archive: point out that these records are persisted in SQLite and survive server restarts.
* **Screen:** System Diagnostics (`/diagnostics`)
  - Show API connectivity: **`HEALTHY`** with active database connection.
  - Highlight Hardware Ingestion Status: **`STAGED / INACTIVE`**, `ENABLE_HARDWARE_INGEST = false`.
  - Point out that database engine is dynamically reported as `SQLite`.

### Stage 8: Dynamic Registry & Unsupported Appliance Honesty
* **Concept:** Show that new appliances can be added without fabricating recognition capability.
* **Action:** In a terminal, register a new appliance (e.g. an Electric Kettle, 1800 W) with uncalibrated status:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/appliances" -Method Post -Body '{"appliance_id":"kettle_01","name":"Electric Kettle","category":"Heating","nominal_power_w":1800.0,"detection_capability":"UNSUPPORTED"}' -ContentType "application/json"
  ```
* **Explanation:** Point out that `detection_capability` is honestly recorded as `UNSUPPORTED`. The system acknowledges the definition exists in inventory, but refuses to claim that the NILM detector can recognize it without empirical calibration.
* **Cleanup:** Delete the temporary appliance:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/appliances/kettle_01" -Method Delete
  ```

### Stage 9: Confirm UI Data Transparency
* **Action:** Review the badging across all four screens:
  - Dashboard: `SIMULATED DATA`, `RULE-BASED ESTIMATE`
  - History: Range disclaimer banner: *"Showing available data of requested window (no artificial gap interpolation)"*
  - Simulator: `SIMULATION MODE`, `METHODOLOGICAL ARCHITECTURE`
  - Diagnostics: `STAGED_INACTIVE`, zero secrets or internal credentials exposed.

---

## 4. Expected Appliance Toggle Reference Table

| Appliance Toggled | Action | Power Delta ($\Delta P$) | Resulting Aggregate Load | Event Status | Event Detector Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Water Heater** | OFF | **-140.0 W** | **144.0 W** | `MATCHED` | Rule match: Water Heater OFF ($140 \pm 12$ W) |
| **Water Heater** | ON | **+140.0 W** | **284.0 W** | `MATCHED` | Rule match: Water Heater ON ($140 \pm 12$ W) |
| **Water Pump** | OFF | **-75.0 W** | **209.0 W** | `MATCHED` | Rule match: Water Pump OFF ($75 \pm 9$ W) |
| **Water Pump** | ON | **+75.0 W** | **284.0 W** | `MATCHED` | Rule match: Water Pump ON ($75 \pm 9$ W) |
| **Ceiling Fan** | OFF | **-45.0 W** | **239.0 W** | `MATCHED` | Rule match: Ceiling Fan OFF ($45 \pm 7$ W) |
| **Ceiling Fan** | ON | **+45.0 W** | **284.0 W** | `MATCHED` | Rule match: Ceiling Fan ON ($45 \pm 7$ W) |
| **LED Bulb** | OFF | **-12.0 W** | **272.0 W** | `MATCHED` | Rule match: LED Bulb OFF ($12 \pm 4$ W) |
| **LED Bulb** | ON | **+12.0 W** | **284.0 W** | `MATCHED` | Rule match: LED Bulb ON ($12 \pm 4$ W) |
| **All Appliances** | ALL OFF | **-272.0 W** | **12.0 W** | `AMBIGUOUS` | Step of -272.0 W does not match any single signature |
| **Reset Button** | RESET | **Restores** | **284.0 W** | Baseline | Restores all 4 appliances ON (272 W + 12 W floor) |

---

## 5. Troubleshooting & Fallback Procedures

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **Port 5000 or 8000 in use** | A previous Python session is still active. | Run `Get-Process python \| Stop-Process -Force` in PowerShell, then re-run `.\start_demo.ps1`. |
| **"Backend Offline" banner in UI** | FastAPI backend stopped or crashed. | Run `& ".\backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --port 8000`. Tap **Retry** on the UI banner. |
| **External devices cannot connect** | Local Wi-Fi router blocks device-to-device traffic. | Use the active Cloudflare Tunnel: `https://nations-assistance-highway-roof.trycloudflare.com`. |
| **Web browser displays blank page** | Old cached JavaScript bundle in browser. | Hard refresh the browser: **`Ctrl + F5`** (or `Cmd + Shift + R` on Mac). |
| **Database missing tables** | Database was deleted or empty. | Run Alembic migrations: `& ".\backend\.venv\Scripts\alembic.exe" -c backend/alembic.ini upgrade head`. |
