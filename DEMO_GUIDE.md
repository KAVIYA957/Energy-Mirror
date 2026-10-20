# Energy Mirror: Live Demonstration & Presentation Guide

**Project Path:** `C:\Users\Kaviya\Downloads\Energy Mirror`  
**Design Identity:** Luminous Clarity (Light-First, WCAG AAA Accessible, High Legibility)  
**Milestone State:** Jury-Ready Demonstration Prototype  
**Data Integrity:** All telemetry is **SIMULATED**; all disaggregation is **RULE-BASED ESTIMATE**. Hardware ingestion is **STAGED / INACTIVE** (`ENABLE_HARDWARE_INGEST=false`).

---

## 1. Quick Startup Commands

To start the complete application for a live demonstration, open two terminal windows:

### Terminal 1: Backend API Gateway (FastAPI)
```powershell
cd "C:\Users\Kaviya\Downloads\Energy Mirror\backend"
& ".\.venv\Scripts\Activate.ps1"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* **API Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
* **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **System Diagnostics Endpoint:** [http://localhost:8000/api/v1/diagnostics/system](http://localhost:8000/api/v1/diagnostics/system)
* **Persistent Event History Endpoint:** [http://localhost:8000/api/v1/telemetry/events](http://localhost:8000/api/v1/telemetry/events)

### Terminal 2: Frontend Web Application (Flutter Web)
```powershell
cd "C:\Users\Kaviya\Downloads\Energy Mirror"
& ".\backend\.venv\Scripts\python.exe" -m http.server 8080 --bind 0.0.0.0 --directory ".\mobile\build\web"
```
* **PC Desktop Browser:** [http://localhost:8080](http://localhost:8080) *(or [http://127.0.0.1:8080](http://127.0.0.1:8080))*
* **Mobile Device on Local Wi-Fi:** `http://<YOUR_PC_IP>:8080` (e.g., `http://192.168.29.166:8080`)

---

## 2. Baseline Simulator Values & Physical Accounting Invariant

When the simulator is initialized or reset via the **"Reset Simulator"** control, it deterministically restores this exact baseline:

| Appliance / Component | Power | Power Factor | Status | Visual Asset | Attributed Load |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Water Heater** | 140.0 W | 0.99 (Resistive) | ON | `assets/images/appliances/water_heater.png` | 140.0 W |
| **Water Pump** | 75.0 W | 0.78 (Inductive) | ON | `assets/images/appliances/water_pump.png` | 75.0 W |
| **Ceiling Fan** | 45.0 W | 0.91 (Motor) | ON | `assets/images/appliances/ceiling_fan.png` | 45.0 W |
| **LED Bulb** | 12.0 W | 0.85 (Lighting) | ON | `assets/images/appliances/led_bulb.png` | 12.0 W |
| **Total Attributed Load** | — | — | — | — | **272.0 W** |
| **Simulated Background Load** | **12.0 W** | 0.90 (Baseline Floor) | Always Active | Fixed Residual Floor | **12.0 W** |
| **Total Aggregate Power** | — | — | — | — | **284.0 W** |

### Mandatory Physical Accounting Invariant
$$\text{Aggregate Power } (W) = \sum \text{Attributed Appliances } (W) + \text{Simulated Background Load } (12.0\text{ W})$$

> [!NOTE]
> **Methodological Note on Background Load:**  
> The 12.0 W background load is a **simulated baseline assumption** within the deterministic simulator model. It represents a continuous baseline floor. It is **not** a physically measured vampire load or a detected physical appliance. Notice that the LED bulb's 12.0 W is strictly separate: when only the LED bulb is active, aggregate power is $12\text{ W} + 12\text{ W} = 24.0\text{ W}$.

---

## 3. Five-Minute Live Jury Demonstration Script

| Timing | Screen | Action | Talking Points & What to Highlight |
| :---: | :--- | :--- | :--- |
| **0:00 – 1:00** | **Dashboard** (`/`) | Open `http://localhost:8080` in browser | • Introduce **Energy Mirror**: A non-intrusive energy intelligence platform that identifies appliance activity from single-point electrical measurements without sub-metering every plug.<br>• Highlight the **Luminous Clarity** visual identity: Soft, daylight-inspired canvas (`#F7F8F4`), crisp cards (`#FFFFFF`), high-contrast ink typography (`#17243B`), and vibrant cobalt interactions (`#3159C9`).<br>• Show the aggregate power hero card at **284 W** and the explicit **`SIMULATED`** badge. Emphasize complete data honesty: hardware ingestion is staged/inactive. |
| **1:00 – 1:45** | **Dashboard** (`/`) | Scroll down to the Appliance Grid & Residual Bar | • Point out the 4 recognized appliance cards with consistent 3D visual renders: Water Heater (140W), Pump (75W), Fan (45W), Bulb (12W).<br>• Tap the **Water Pump** card to open the interactive **Inference Evidence & Reasoning** modal: shows the inductive motor inrush signature and 0.78 PF classification.<br>• Inspect the **Load Reconciliation bar**: 272 W attributed (95.8%), 12 W simulated background residual floor (4.2%). Badges clearly state **`RULE-BASED ESTIMATE`**. |
| **1:45 – 2:45** | **Appliance Simulator** (`/simulator`) | Click "Simulator" in Nav. Toggle **Water Heater OFF** | • In Simulator Lab, toggle Water Heater from ON to OFF.<br>• Observe live aggregate power drop: $284\text{ W} \rightarrow 144\text{ W}$ ($\Delta P = -140\text{ W}$).<br>• Show the event feed: **`MATCHED: Water Heater OFF (-140 W)`**.<br>• **Key Technical Point:** The detector was **never informed** which switch was flipped. It observed the mathematical step derivative ($\Delta P = -140\text{ W}$) in aggregate telemetry and matched it against its calibrated tolerance envelope ($140 \pm 12\text{ W}$). |
| **2:45 – 3:30** | **Appliance Simulator** (`/simulator`) | Toggle all 4 appliances OFF, then click **Reset** | • Switch off all remaining appliances.<br>• Point out the live accounting bar: Attributed is 0 W, aggregate is **12.0 W** ($100\%$ unattributed floor). The baseline floor never drops to zero.<br>• Click **"Reset Simulator"**: Instantly restores the baseline 284 W aggregate and 272 W attributed load with all 4 appliances running. |
| **3:30 – 4:15** | **History & Analytics** (`/history`) | Click "History" in Nav. Toggle 15m $\rightarrow$ 6h | • Show the interactive FL Chart with smooth power curve and solar amber event markers.<br>• Toggle the interval selector: 15m, 1h, 6h, 24h. Point out the **honest range banner**: *"Showing available data of requested window (no artificial gap interpolation)"*.<br>• Scroll to the **Durable Detected Events** archive: shows persistent SQLite records surviving backend restarts. |
| **4:15 – 4:45** | **System Diagnostics** (`/diagnostics`) | Click "Diagnostics" in Nav | • Show API Connectivity: **`HEALTHY`** with active database connection.<br>• Point out **Hardware Ingestion Status**: **`STAGED / INACTIVE`**, `ENABLE_HARDWARE_INGEST = false`.<br>• Verify the security audit: Zero device tokens, passwords, or internal server paths are exposed. |
| **4:45 – 5:00** | **Wrap-Up** | Conclude presentation | • Summarize: Responsive multi-screen Flutter architecture, consistent 3D appliance visual library, transparent rule-based NILM event detection, and strict physical accounting are 100% verified.<br>• State the next milestone: Supervised physical bench testing with ESP32 and PZEM-004T under laboratory electrical safety protocols. |

---

## 4. Expected Appliance Toggle Outcomes

Use this table as a reference during live questions from judges or evaluators:

| Appliance Toggled | Action | Power Delta ($\Delta P$) | Resulting Aggregate Load | Event Status | Event Detector Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Water Heater** | OFF | **-140.0 W** | **144.0 W** | `MATCHED` | Rule-based match: Water Heater OFF (matches 140 W in [128, 152] W envelope) |
| **Water Heater** | ON | **+140.0 W** | **284.0 W** | `MATCHED` | Rule-based match: Water Heater ON (matches 140 W in [128, 152] W envelope) |
| **Water Pump** | OFF | **-75.0 W** | **209.0 W** | `MATCHED` | Rule-based match: Water Pump OFF (matches 75 W in [66, 84] W envelope) |
| **Water Pump** | ON | **+75.0 W** | **284.0 W** | `MATCHED` | Rule-based match: Water Pump ON (matches 75 W in [66, 84] W envelope) |
| **Ceiling Fan** | OFF | **-45.0 W** | **239.0 W** | `MATCHED` | Rule-based match: Ceiling Fan OFF (matches 45 W in [38, 52] W envelope) |
| **Ceiling Fan** | ON | **+45.0 W** | **284.0 W** | `MATCHED` | Rule-based match: Ceiling Fan ON (matches 45 W in [38, 52] W envelope) |
| **LED Bulb** | OFF | **-12.0 W** | **272.0 W** | `MATCHED` | Rule-based match: LED Bulb OFF (matches 12 W in [8, 16] W envelope) |
| **LED Bulb** | ON | **+12.0 W** | **284.0 W** | `MATCHED` | Rule-based match: LED Bulb ON (matches 12 W in [8, 16] W envelope) |
| **All Appliances** | ALL OFF | **-272.0 W** | **12.0 W** | `AMBIGUOUS` | Step of -272.0 W does not match any single signature (multi-load step) |
| **Reset Button** | RESET | **Restores** | **284.0 W** | Baseline | Restores all 4 appliances ON (272 W attributed + 12 W floor) |

---

## 5. Troubleshooting & Fallback Procedures

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **"ERR_CONNECTION_REFUSED" on phone** | Phone cannot resolve `localhost` or PC Wi-Fi IP changed. | Open the Wi-Fi IP address on your phone: `http://<YOUR_PC_IP>:8080`. Ensure PC and phone are on the same Wi-Fi network. |
| **"Backend Offline" banner in UI** | FastAPI backend daemon is stopped. | Run `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` in `backend/`. Tap the **Retry** button on the UI banner. |
| **Web page does not refresh after build** | Browser caching old JavaScript bundle. | Hard refresh the browser: **`Ctrl + F5`** (or `Cmd + Shift + R` on Mac). |
| **Port 8080 or 8000 already in use** | A prior Python process is holding the port. | In PowerShell: `Get-Process python \| Stop-Process -Force`, then restart the two commands in Section 1. |

### 5.1 Manual Real Browser Verification Checklist

Since headless automated browser drivers are unavailable in this environment, use this manual procedure in Microsoft Edge, Google Chrome, or a mobile browser:

1. **Desktop Viewport Verification (1440 × 900):**
   - Open [http://localhost:8080](http://localhost:8080) in full screen.
   - Verify the left **NavigationRail** renders with 4 icons: Dashboard, History, Simulator, Diagnostics.
   - Verify the top aggregate load hero card displays **284 W** in high-contrast ink typography.
   - Tap through `/history`, `/simulator`, `/diagnostics`; verify no layout overflow or visual glitches.
   - Press **F5** on `/simulator`; verify the shell restores and stays on the Simulator screen.
2. **Mobile Viewport Verification (393 × 852):**
   - Open Chrome DevTools (`F12`), toggle Device Toolbar (`Ctrl + Shift + M`), and select iPhone 15 / 16 (393 × 852).
   - Alternatively, open `http://<YOUR_PC_IP>:8080` directly on your smartphone connected to Wi-Fi.
   - Verify the bottom **NavigationBar** renders with 4 destinations.
   - Verify cards stack cleanly without horizontal scrollbars or overflow yellow bars.
3. **Interactive Simulator & Reset Flow:**
   - On `/simulator`, toggle **Water Heater** switch to OFF. Verify aggregate drops from 284 W to 144 W.
   - Click **Reset Simulator** button; verify aggregate returns to 284 W immediately.
4. **Offline Error & Recovery Flow:**
   - In terminal, stop Uvicorn (`Ctrl + C`).
   - In browser, wait 4 seconds; verify amber offline banner appears: *"Backend unreachable. Displaying cached data (Stale)."*
   - In terminal, restart Uvicorn.
   - Tap **Retry** on the UI banner; verify data restores and banner disappears.
