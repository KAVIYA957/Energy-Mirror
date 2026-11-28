import os
from PIL import Image, ImageDraw, ImageFont

assets_dir = r"C:\Users\Kaviya\Downloads\Energy Mirror\docs\assets"
os.makedirs(assets_dir, exist_ok=True)

# Helper to load fonts
try:
    font_hero = ImageFont.truetype("arialbd.ttf", 22)
    font_h2 = ImageFont.truetype("arialbd.ttf", 16)
    font_h3 = ImageFont.truetype("arialbd.ttf", 13)
    font_body = ImageFont.truetype("arial.ttf", 11)
    font_badge = ImageFont.truetype("arialbd.ttf", 11)
    font_stat = ImageFont.truetype("arialbd.ttf", 18)
except Exception:
    font_hero = ImageFont.load_default()
    font_h2 = font_hero
    font_h3 = font_hero
    font_body = font_hero
    font_badge = font_hero
    font_stat = font_hero


# ==============================================================================
# DIAGRAM 1: SYSTEM ARCHITECTURE (system_architecture.svg & .png)
# ==============================================================================
def generate_system_architecture():
    svg_path = os.path.join(assets_dir, "system_architecture.svg")
    png_path = os.path.join(assets_dir, "system_architecture.png")

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1160" width="100%" height="100%" style="background-color: #0B0F19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#151D2F"/>
      <stop offset="100%" stop-color="#0F1728"/>
    </linearGradient>
    <linearGradient id="subCardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1A243B"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
    <marker id="arrowCyan" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="#00E5FF"/>
    </marker>
    <marker id="arrowIndigo" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="#6366F1"/>
    </marker>
    <marker id="arrowAmber" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M 0 0 L 8 4 L 0 8 Z" fill="#F59E0B"/>
    </marker>
  </defs>

  <!-- 0. TOP HERO HEADER -->
  <rect x="30" y="25" width="1540" height="75" rx="14" fill="#111827" stroke="#00E5FF" stroke-width="1.8" filter="url(#cardShadow)"/>
  <text x="55" y="58" fill="#FFFFFF" font-size="22" font-weight="800" letter-spacing="0.8">ENERGY MIRROR: LIVING CURRENT</text>
  <text x="55" y="80" fill="#00E5FF" font-size="13" font-weight="600">End-to-End System Architecture &amp; Progress Verification Map</text>

  <!-- Top Badges (140px each, 12px gap, right aligned to 1545) -->
  <g transform="translate(949, 47)">
    <rect x="0" y="0" width="140" height="30" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1.4"/>
    <circle cx="15" cy="15" r="4" fill="#10B981"/>
    <text x="75" y="20" fill="#E6FFFA" font-size="11" font-weight="800" text-anchor="middle">193 TESTS PASSED</text>
  </g>
  <g transform="translate(1101, 47)">
    <rect x="0" y="0" width="140" height="30" rx="8" fill="#0C4A6E" stroke="#00E5FF" stroke-width="1.4"/>
    <circle cx="15" cy="15" r="4" fill="#00E5FF"/>
    <text x="75" y="20" fill="#E0F2FE" font-size="11" font-weight="800" text-anchor="middle">60 FPS / WCAG AAA</text>
  </g>
  <g transform="translate(1253, 47)">
    <rect x="0" y="0" width="140" height="30" rx="8" fill="#4C1D95" stroke="#A855F7" stroke-width="1.4"/>
    <circle cx="15" cy="15" r="4" fill="#A855F7"/>
    <text x="75" y="20" fill="#F3E8FF" font-size="11" font-weight="800" text-anchor="middle">LOOPBACK GUARD</text>
  </g>
  <g transform="translate(1405, 47)">
    <rect x="0" y="0" width="140" height="30" rx="8" fill="#78350F" stroke="#F59E0B" stroke-width="1.4"/>
    <circle cx="15" cy="15" r="4" fill="#F59E0B"/>
    <text x="75" y="20" fill="#FEF3C7" font-size="10.5" font-weight="800" text-anchor="middle">HW: PROCUREMENT</text>
  </g>

  <!-- 1. PRESENTATION LAYER -->
  <g transform="translate(30, 120)">
    <rect x="0" y="0" width="1540" height="230" rx="14" fill="url(#cardGrad)" stroke="#0284C7" stroke-width="1.8" filter="url(#cardShadow)"/>
    <path d="M 0 14 Q 0 0 14 0 L 1526 0 Q 1540 0 1540 14 L 1540 42 L 0 42 Z" fill="#1E293B"/>
    <text x="25" y="27" fill="#FFFFFF" font-size="15" font-weight="800">1. PRESENTATION LAYER: FLUTTER WEBDESKTOP / MOBILE DASHBOARD</text>
    <rect x="1265" y="8" width="250" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1390" y="25" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">VERIFIED LIVE (38 TESTS PASSED)</text>

    <!-- 4 Sub-boxes: width=360 each, x=20, 400, 780, 1160, right margin=20 -->
    <g transform="translate(20, 56)">
      <rect x="0" y="0" width="360" height="155" rx="10" fill="url(#subCardGrad)" stroke="#38BDF8" stroke-width="1.2"/>
      <text x="18" y="28" fill="#00E5FF" font-size="13.5" font-weight="700">Hero Energy Pulse (60 FPS)</text>
      <text x="18" y="52" fill="#CBD5E1" font-size="11.5">• Radial breathing cyan glow visualizer</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• Real-time baseline readout: 284.0 W</text>
      <text x="18" y="92" fill="#CBD5E1" font-size="11.5">• Tabular typography (zero layout shift)</text>
      <text x="18" y="112" fill="#CBD5E1" font-size="11.5">• Truth-in-reporting pill: [SIMULATED]</text>
      <text x="18" y="132" fill="#CBD5E1" font-size="11.5">• Mobile (393px) &amp; Desktop (1440px) checked</text>
    </g>

    <g transform="translate(400, 56)">
      <rect x="0" y="0" width="360" height="155" rx="10" fill="url(#subCardGrad)" stroke="#38BDF8" stroke-width="1.2"/>
      <text x="18" y="28" fill="#00E5FF" font-size="13.5" font-weight="700">Appliance Constellation Grid</text>
      <text x="18" y="52" fill="#CBD5E1" font-size="11.5">• Water Heater: 140.0 W (49.3%, PF 0.99)</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• Water Pump: 75.0 W (26.4%, PF 0.78)</text>
      <text x="18" y="92" fill="#CBD5E1" font-size="11.5">• Ceiling Fan: 45.0 W (15.8%, PF 0.91)</text>
      <text x="18" y="112" fill="#CBD5E1" font-size="11.5">• LED Bulb: 12.0 W (4.2%, PF 0.95)</text>
      <text x="18" y="132" fill="#CBD5E1" font-size="11.5">• Interactive toggles &amp; duty cycle models</text>
    </g>

    <g transform="translate(780, 56)">
      <rect x="0" y="0" width="360" height="155" rx="10" fill="url(#subCardGrad)" stroke="#38BDF8" stroke-width="1.2"/>
      <text x="18" y="28" fill="#00E5FF" font-size="13.5" font-weight="700">Load Reconciliation Bar</text>
      <text x="18" y="52" fill="#CBD5E1" font-size="11.5">• Invariant: P_agg = Sum(P_app) + P_residual</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• Attributed Sum: 272.0 W (95.8%)</text>
      <text x="18" y="92" fill="#CBD5E1" font-size="11.5">• Unattributed Floor: 12.0 W (4.2%)</text>
      <text x="18" y="112" fill="#CBD5E1" font-size="11.5">• Parasitic standby baseline model</text>
      <text x="18" y="132" fill="#CBD5E1" font-size="11.5">• Strictly distinct from 12.0 W LED bulb</text>
    </g>

    <g transform="translate(1160, 56)">
      <rect x="0" y="0" width="360" height="155" rx="10" fill="url(#subCardGrad)" stroke="#38BDF8" stroke-width="1.2"/>
      <text x="18" y="28" fill="#00E5FF" font-size="13.5" font-weight="700">Dynamic Registry Workbench</text>
      <text x="18" y="52" fill="#CBD5E1" font-size="11.5">• Add / Edit / Inspect appliance dialogs</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• Tolerance bounds: Delta P, Expected PF</text>
      <text x="18" y="92" fill="#CBD5E1" font-size="11.5">• Capability honesty: PRODUCTION vs UNSUPPORTED</text>
      <text x="18" y="112" fill="#CBD5E1" font-size="11.5">• Protected default 4-appliance guard</text>
      <text x="18" y="132" fill="#CBD5E1" font-size="11.5">• FlChart 15m/1h/6h/24h non-flatline view</text>
    </g>
  </g>

  <!-- 2. API GATEWAY LAYER -->
  <g transform="translate(30, 375)">
    <rect x="0" y="0" width="1540" height="185" rx="14" fill="url(#cardGrad)" stroke="#6366F1" stroke-width="1.8" filter="url(#cardShadow)"/>
    <path d="M 0 14 Q 0 0 14 0 L 1526 0 Q 1540 0 1540 14 L 1540 42 L 0 42 Z" fill="#1E293B"/>
    <text x="25" y="27" fill="#FFFFFF" font-size="15" font-weight="800">2. API GATEWAY, REVERSE PROXY &amp; SECURITY ENGINE (FASTAPI ASGI)</text>
    <rect x="1265" y="8" width="250" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1390" y="25" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">HARDENED (18 TESTS PASSED)</text>

    <!-- 4 Sub-boxes: width=360 each, x=20, 400, 780, 1160 -->
    <g transform="translate(20, 54)">
      <rect x="0" y="0" width="360" height="115" rx="10" fill="url(#subCardGrad)" stroke="#818CF8" stroke-width="1.2"/>
      <text x="18" y="26" fill="#A5B4FC" font-size="13" font-weight="700">Unified Proxy (:5000 / :8000)</text>
      <text x="18" y="48" fill="#CBD5E1" font-size="11">• Single-port reverse proxy (serve_web.py)</text>
      <text x="18" y="68" fill="#CBD5E1" font-size="11">• Static Flutter web release bundle host</text>
      <text x="18" y="88" fill="#CBD5E1" font-size="11">• Resilient client offline fallback &amp; retry</text>
      <text x="18" y="106" fill="#CBD5E1" font-size="11">• WebSocket / SSE live telemetry stream</text>
    </g>

    <g transform="translate(400, 54)">
      <rect x="0" y="0" width="360" height="115" rx="10" fill="url(#subCardGrad)" stroke="#818CF8" stroke-width="1.2"/>
      <text x="18" y="26" fill="#A5B4FC" font-size="13" font-weight="700">Local Loopback Security Guard</text>
      <text x="18" y="48" fill="#CBD5E1" font-size="11">• Loopback isolation (127.0.0.1, ::1)</text>
      <text x="18" y="68" fill="#CBD5E1" font-size="11">• Administrative mutations guarded (POST, DEL)</text>
      <text x="18" y="88" fill="#CBD5E1" font-size="11">• Remote write requests rejected: HTTP 403</text>
      <text x="18" y="106" fill="#CBD5E1" font-size="11">• Strict CORS origin checking (no wildcards)</text>
    </g>

    <g transform="translate(780, 54)">
      <rect x="0" y="0" width="360" height="115" rx="10" fill="url(#subCardGrad)" stroke="#818CF8" stroke-width="1.2"/>
      <text x="18" y="26" fill="#A5B4FC" font-size="13" font-weight="700">Pydantic v2 Schema Guardrails</text>
      <text x="18" y="48" fill="#CBD5E1" font-size="11">• Physical conservation check: P &lt;= S * 1.08</text>
      <text x="18" y="68" fill="#CBD5E1" font-size="11">• Extra payload fields forbidden</text>
      <text x="18" y="88" fill="#CBD5E1" font-size="11">• Multi-turn CT turn scaling (N=10 divisor)</text>
      <text x="18" y="106" fill="#CBD5E1" font-size="11">• Timing-safe token auth (compare_digest)</text>
    </g>

    <g transform="translate(1160, 54)">
      <rect x="0" y="0" width="360" height="115" rx="10" fill="url(#subCardGrad)" stroke="#818CF8" stroke-width="1.2"/>
      <text x="18" y="26" fill="#A5B4FC" font-size="13" font-weight="700">RESTful Service Endpoints</text>
      <text x="18" y="48" fill="#CBD5E1" font-size="11">• GET /api/v1/health &amp; /diagnostics</text>
      <text x="18" y="68" fill="#CBD5E1" font-size="11">• GET /api/v1/telemetry/live &amp; /history</text>
      <text x="18" y="88" fill="#CBD5E1" font-size="11">• GET /api/v1/nilm/live-disaggregation</text>
      <text x="18" y="106" fill="#CBD5E1" font-size="11">• POST /api/v1/appliances &amp; /simulator/toggle</text>
    </g>
  </g>

  <!-- 3. MIDDLE TIER: 3 LARGE CARDS (493px each, 30px gap, perfectly centered) -->
  <!-- 3A -->
  <g transform="translate(30, 585)">
    <rect x="0" y="0" width="493" height="235" rx="14" fill="url(#cardGrad)" stroke="#10B981" stroke-width="1.8" filter="url(#cardShadow)"/>
    <path d="M 0 14 Q 0 0 14 0 L 479 0 Q 493 0 493 14 L 493 42 L 0 42 Z" fill="#1E293B"/>
    <text x="20" y="27" fill="#FFFFFF" font-size="14" font-weight="800">3A. DYNAMIC REGISTRY &amp; SIMULATOR</text>
    <rect x="335" y="8" width="145" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="407" y="25" fill="#34D399" font-size="10.5" font-weight="800" text-anchor="middle">VERIFIED (30 TESTS)</text>

    <g transform="translate(18, 55)">
      <rect x="0" y="0" width="457" height="162" rx="10" fill="url(#subCardGrad)" stroke="#059669" stroke-width="1.2"/>
      <text x="18" y="26" fill="#34D399" font-size="13" font-weight="700">Deterministic Mathematical Simulator</text>
      <text x="18" y="50" fill="#CBD5E1" font-size="11.5">• Dynamic database-backed appliance catalog</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• 16-state combinatorial permutation logic</text>
      <text x="18" y="94" fill="#CBD5E1" font-size="11.5">• All appliances OFF = exactly 12.0 W residual</text>
      <text x="18" y="116" fill="#CBD5E1" font-size="11.5">• Calibrated power factor &amp; apparent power math</text>
      <text x="18" y="138" fill="#CBD5E1" font-size="11.5">• State isolation across server restarts &amp; resets</text>
    </g>
  </g>

  <!-- 3B -->
  <g transform="translate(553, 585)">
    <rect x="0" y="0" width="494" height="235" rx="14" fill="url(#cardGrad)" stroke="#06B6D4" stroke-width="1.8" filter="url(#cardShadow)"/>
    <path d="M 0 14 Q 0 0 14 0 L 480 0 Q 494 0 494 14 L 494 42 L 0 42 Z" fill="#1E293B"/>
    <text x="20" y="27" fill="#FFFFFF" font-size="14" font-weight="800">3B. RULE-BASED NILM &amp; ML BENCHMARKS</text>
    <rect x="315" y="8" width="165" height="26" rx="6" fill="#164E63" stroke="#06B6D4" stroke-width="1.2"/>
    <text x="397" y="25" fill="#67E8F9" font-size="10.5" font-weight="800" text-anchor="middle">BENCHMARKED (74 TESTS)</text>

    <g transform="translate(18, 55)">
      <rect x="0" y="0" width="458" height="162" rx="10" fill="url(#subCardGrad)" stroke="#0891B2" stroke-width="1.2"/>
      <text x="18" y="26" fill="#22D3EE" font-size="13" font-weight="700">1 Hz Derivative Edge &amp; Public Data Benchmarks</text>
      <text x="18" y="50" fill="#CBD5E1" font-size="11.5">• Derivative step detector: Delta P &amp; Delta PF envelopes</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• Noise floor suppression: |Delta P| &lt; 5.0 W ignored</text>
      <text x="18" y="94" fill="#CBD5E1" font-size="11.5">• Simultaneous switching tagged: [AMBIGUOUS]</text>
      <text x="18" y="116" fill="#CBD5E1" font-size="11.5">• UK REFIT &amp; Indian iAWE benchmark validation</text>
      <text x="18" y="138" fill="#CBD5E1" font-size="11.5">• Deep Learning Roadmap: Seq2Point &amp; TCN models</text>
    </g>
  </g>

  <!-- 3C -->
  <g transform="translate(1077, 585)">
    <rect x="0" y="0" width="493" height="235" rx="14" fill="url(#cardGrad)" stroke="#A855F7" stroke-width="1.8" filter="url(#cardShadow)"/>
    <path d="M 0 14 Q 0 0 14 0 L 479 0 Q 493 0 493 14 L 493 42 L 0 42 Z" fill="#1E293B"/>
    <text x="20" y="27" fill="#FFFFFF" font-size="14" font-weight="800">3C. DURABLE PERSISTENCE LAYER</text>
    <rect x="335" y="8" width="145" height="26" rx="6" fill="#581C87" stroke="#A855F7" stroke-width="1.2"/>
    <text x="407" y="25" fill="#D8B4FE" font-size="10.5" font-weight="800" text-anchor="middle">VERIFIED (11 TESTS)</text>

    <g transform="translate(18, 55)">
      <rect x="0" y="0" width="457" height="162" rx="10" fill="url(#subCardGrad)" stroke="#9333EA" stroke-width="1.2"/>
      <text x="18" y="26" fill="#C084FC" font-size="13" font-weight="700">Dual-Engine Relational Storage (Alembic @ 8f8361eca0e9)</text>
      <text x="18" y="50" fill="#CBD5E1" font-size="11.5">• SQLite (energy_mirror.db) for zero-dependency dev</text>
      <text x="18" y="72" fill="#CBD5E1" font-size="11.5">• PostgreSQL (psycopg2) production-ready driver</text>
      <text x="18" y="94" fill="#CBD5E1" font-size="11.5">• Idempotent upgrades &amp; clean rollback migrations</text>
      <text x="18" y="116" fill="#CBD5E1" font-size="11.5">• Deduplicated state event persistence &amp; retrieval</text>
      <text x="18" y="138" fill="#CBD5E1" font-size="11.5">• Schema tables: telemetry, estimates, events, registry</text>
    </g>
  </g>

  <!-- 4. HARDWARE LAYER: 4 Sub-boxes (360px each, matching Section 1 and 2!) -->
  <g transform="translate(30, 855)">
    <rect x="0" y="0" width="1540" height="245" rx="14" fill="#151515" stroke="#F59E0B" stroke-width="1.8" filter="url(#cardShadow)"/>
    <path d="M 0 14 Q 0 0 14 0 L 1526 0 Q 1540 0 1540 14 L 1540 42 L 0 42 Z" fill="#29200C"/>
    <text x="25" y="27" fill="#FEF3C7" font-size="15" font-weight="800">4. METROLOGY &amp; HARDWARE INGESTION LAYER (LABORATORY PROCUREMENT BLUEPRINT)</text>
    <rect x="1225" y="8" width="295" height="26" rx="6" fill="#78350F" stroke="#F59E0B" stroke-width="1.2"/>
    <text x="1372" y="25" fill="#FDE68A" font-size="10.5" font-weight="800" text-anchor="middle">PENDING PHYSICAL PROCUREMENT</text>

    <!-- Sub-Box 1 -->
    <g transform="translate(20, 56)">
      <rect x="0" y="0" width="360" height="170" rx="10" fill="#1C180E" stroke="#D97706" stroke-width="1.2"/>
      <text x="18" y="26" fill="#FBBF24" font-size="13" font-weight="700">Service Panel Sensing</text>
      <text x="18" y="52" fill="#E2E8F0" font-size="11.5">• Single-point distribution panel sensing</text>
      <text x="18" y="74" fill="#E2E8F0" font-size="11.5">• PZEM-004T v3.0 Digital Energy IC</text>
      <text x="18" y="96" fill="#E2E8F0" font-size="11.5">• Split-core 100A / 100mA current clamp</text>
      <text x="18" y="118" fill="#E2E8F0" font-size="11.5">• Modbus-RTU over RS-485 / UART</text>
      <text x="18" y="140" fill="#E2E8F0" font-size="11.5">• 1 Hz V, I, P, PF, Frequency acquisition</text>
    </g>

    <!-- Sub-Box 2 -->
    <g transform="translate(400, 56)">
      <rect x="0" y="0" width="360" height="170" rx="10" fill="#1C180E" stroke="#D97706" stroke-width="1.2"/>
      <text x="18" y="26" fill="#FBBF24" font-size="13" font-weight="700">Low-Power CT Multi-Turn Scaling</text>
      <text x="18" y="52" fill="#E2E8F0" font-size="11.5">• N = 10 primary conductor turns</text>
      <text x="18" y="74" fill="#E2E8F0" font-size="11.5">• Multiplies magnetic flux 10x (12W -> 120W)</text>
      <text x="18" y="96" fill="#E2E8F0" font-size="11.5">• Lifts low loads above CT non-linear floor</text>
      <text x="18" y="118" fill="#E2E8F0" font-size="11.5">• Firmware / Ingestion inverse divisor (N=10)</text>
      <text x="18" y="140" fill="#E2E8F0" font-size="11.5">• Enables sub-15W LED bulb measurement</text>
    </g>

    <!-- Sub-Box 3 -->
    <g transform="translate(780, 56)">
      <rect x="0" y="0" width="360" height="170" rx="10" fill="#1C180E" stroke="#D97706" stroke-width="1.2"/>
      <text x="18" y="26" fill="#FBBF24" font-size="13" font-weight="700">Firmware Architecture</text>
      <text x="18" y="52" fill="#E2E8F0" font-size="11.5">• ESP32-WROOM-32D Dual-Core MCU</text>
      <text x="18" y="74" fill="#E2E8F0" font-size="11.5">• Core 0: FreeRTOS 1 Hz Modbus acquisition</text>
      <text x="18" y="96" fill="#E2E8F0" font-size="11.5">• Core 1: Wi-Fi HTTP POST client</text>
      <text x="18" y="118" fill="#E2E8F0" font-size="11.5">• HLK-PM01 5V isolated AC-DC supply</text>
      <text x="18" y="140" fill="#E2E8F0" font-size="11.5">• Ring buffer for offline network caching</text>
    </g>

    <!-- Sub-Box 4 -->
    <g transform="translate(1160, 56)">
      <rect x="0" y="0" width="360" height="170" rx="10" fill="#1C180E" stroke="#D97706" stroke-width="1.2"/>
      <text x="18" y="26" fill="#FBBF24" font-size="13" font-weight="700">Electrical Bench Safety &amp; Ingest</text>
      <text x="18" y="52" fill="#E2E8F0" font-size="11.5">• Single-pole 6A MCB (10kA breaking capacity)</text>
      <text x="18" y="74" fill="#E2E8F0" font-size="11.5">• 2-pole 30mA RCD / RCCB earth fault trip</text>
      <text x="18" y="96" fill="#E2E8F0" font-size="11.5">• 5kV Optocoupler galvanic isolation barrier</text>
      <text x="18" y="118" fill="#E2E8F0" font-size="11.5">• Endpoint: POST /api/v1/telemetry/ingest</text>
      <text x="18" y="140" fill="#E2E8F0" font-size="11.5">• Staged Inactive (ENABLE_HW_INGEST=false)</text>
    </g>
  </g>

  <!-- 5. PERFECTLY ALIGNED CONNECTORS -->
  <!-- Layer 1 to Layer 2 -->
  <line x1="230" y1="350" x2="230" y2="373" stroke="#00E5FF" stroke-width="2.5" marker-end="url(#arrowCyan)"/>
  <line x1="1370" y1="375" x2="1370" y2="352" stroke="#00E5FF" stroke-width="2.5" marker-end="url(#arrowCyan)"/>
  
  <rect x="165" y="354" width="130" height="18" rx="4" fill="#0B0F19" stroke="#00E5FF" stroke-width="1"/>
  <text x="230" y="367" fill="#00E5FF" font-size="10" font-weight="700" text-anchor="middle">HTTP REST / SSE</text>
  
  <rect x="1305" y="354" width="130" height="18" rx="4" fill="#0B0F19" stroke="#00E5FF" stroke-width="1"/>
  <text x="1370" y="367" fill="#00E5FF" font-size="10" font-weight="700" text-anchor="middle">JSON DTO STREAM</text>

  <!-- Layer 2 to Layer 3 -->
  <line x1="276" y1="560" x2="276" y2="583" stroke="#6366F1" stroke-width="2.5" marker-end="url(#arrowIndigo)"/>
  <line x1="800" y1="560" x2="800" y2="583" stroke="#6366F1" stroke-width="2.5" marker-end="url(#arrowIndigo)"/>
  <line x1="1324" y1="560" x2="1324" y2="583" stroke="#6366F1" stroke-width="2.5" marker-end="url(#arrowIndigo)"/>

  <!-- Layer 4 to Layer 2 (Staged Ingestion Flow) -->
  <line x1="1370" y1="855" x2="1370" y2="563" stroke="#F59E0B" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrowAmber)"/>
  <rect x="1305" y="700" width="130" height="20" rx="4" fill="#0B0F19" stroke="#F59E0B" stroke-width="1"/>
  <text x="1370" y="714" fill="#F59E0B" font-size="9.5" font-weight="700" text-anchor="middle">STAGED INGESTION</text>

</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    # Render PNG
    W, H = 1600, 1160
    img = Image.new("RGB", (W, H), color="#0B0F19")
    draw = ImageDraw.Draw(img)

    # Header
    draw.rounded_rectangle([30, 25, 1570, 100], radius=14, fill="#111827", outline="#00E5FF", width=2)
    draw.text((55, 42), "ENERGY MIRROR: LIVING CURRENT", fill="#FFFFFF", font=font_hero)
    draw.text((55, 74), "End-to-End System Architecture & Progress Verification Map", fill="#00E5FF", font=font_h3)

    badges = [
        ("193 TESTS PASSED", "#10B981", "#064E3B", 949),
        ("60 FPS / WCAG AAA", "#00E5FF", "#0C4A6E", 1101),
        ("LOOPBACK GUARD", "#A855F7", "#4C1D95", 1253),
        ("HW: PROCUREMENT", "#F59E0B", "#78350F", 1405),
    ]
    for text, border_c, bg_c, x in badges:
        draw.rounded_rectangle([x, 48, x + 140, 78], radius=6, fill=bg_c, outline=border_c, width=1)
        draw.text((x + 14, 56), text, fill=border_c, font=font_badge)

    def draw_section(y, h, title, status, border_c, header_c):
        draw.rounded_rectangle([30, y, 1570, y + h], radius=14, fill="#131B2E", outline=border_c, width=2)
        draw.rounded_rectangle([30, y, 1570, y + 42], radius=14, fill=header_c, outline=border_c, width=2)
        draw.text((50, y + 12), title, fill="#FFFFFF", font=font_h2)
        draw.rounded_rectangle([1265, y + 8, 1550, y + 34], radius=6, fill="#0F172A", outline=border_c, width=1)
        draw.text((1285, y + 14), status, fill=border_c, font=font_badge)

    def draw_box(x, y, w, h, title, lines, border_c, title_c="#38BDF8"):
        draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill="#182238", outline=border_c, width=1)
        draw.text((x + 16, y + 14), title, fill=title_c, font=font_h3)
        curr_y = y + 42
        for line in lines:
            draw.text((x + 16, curr_y), line, fill="#CBD5E1", font=font_body)
            curr_y += 20

    # 1. Presentation
    draw_section(120, 230, "1. PRESENTATION LAYER: FLUTTER WEBDESKTOP / MOBILE DASHBOARD", "VERIFIED LIVE (38 TESTS PASSED)", "#0284C7", "#1E293B")
    draw_box(50, 176, 360, 155, "Hero Energy Pulse (60 FPS)", [
        "• Radial breathing cyan glow visualizer",
        "• Real-time baseline readout: 284.0 W",
        "• Tabular typography (zero layout shift)",
        "• Truth-in-reporting pill: [SIMULATED]",
        "• Mobile (393px) & Desktop (1440px) checked"
    ], "#38BDF8", "#00E5FF")

    draw_box(430, 176, 360, 155, "Appliance Constellation Grid", [
        "• Water Heater: 140.0 W (49.3%, PF 0.99)",
        "• Water Pump: 75.0 W (26.4%, PF 0.78)",
        "• Ceiling Fan: 45.0 W (15.8%, PF 0.91)",
        "• LED Bulb: 12.0 W (4.2%, PF 0.95)",
        "• Interactive toggles & duty cycle models"
    ], "#38BDF8", "#00E5FF")

    draw_box(810, 176, 360, 155, "Load Reconciliation Bar", [
        "• Invariant: P_agg = Sum(P_app) + P_residual",
        "• Attributed Sum: 272.0 W (95.8%)",
        "• Unattributed Floor: 12.0 W (4.2%)",
        "• Parasitic standby baseline model",
        "• Strictly distinct from 12.0 W LED bulb"
    ], "#38BDF8", "#00E5FF")

    draw_box(1190, 176, 360, 155, "Dynamic Registry Workbench", [
        "• Add / Edit / Inspect appliance dialogs",
        "• Tolerance bounds: Delta P, Expected PF",
        "• Capability honesty: PRODUCTION vs UNSUPPORTED",
        "• Protected default 4-appliance guard",
        "• FlChart 15m/1h/6h/24h non-flatline view"
    ], "#38BDF8", "#00E5FF")

    # 2. Gateway
    draw_section(375, 185, "2. API GATEWAY, REVERSE PROXY & SECURITY ENGINE (FASTAPI ASGI)", "HARDENED (18 TESTS PASSED)", "#6366F1", "#1E293B")
    draw_box(50, 429, 360, 115, "Unified Proxy (:5000 / :8000)", [
        "• Single-port reverse proxy (serve_web.py)",
        "• Static Flutter web release bundle host",
        "• Resilient client offline fallback & retry"
    ], "#818CF8", "#A5B4FC")

    draw_box(430, 429, 360, 115, "Local Loopback Security Guard", [
        "• Loopback isolation (127.0.0.1, ::1)",
        "• Administrative mutations guarded (POST, DEL)",
        "• Remote write requests rejected: HTTP 403"
    ], "#818CF8", "#A5B4FC")

    draw_box(810, 429, 360, 115, "Pydantic v2 Schema Guardrails", [
        "• Physical conservation check: P <= S * 1.08",
        "• Extra payload fields forbidden",
        "• Timing-safe token auth (compare_digest)"
    ], "#818CF8", "#A5B4FC")

    draw_box(1190, 429, 360, 115, "RESTful Service Endpoints", [
        "• GET /api/v1/health & /diagnostics",
        "• GET /api/v1/telemetry/live & /history",
        "• GET /api/v1/nilm/live-disaggregation"
    ], "#818CF8", "#A5B4FC")

    # 3. Middle Tier (493px each)
    draw_section(585, 235, "3. CORE INTELLIGENCE & PERSISTENCE ENGINE", "115 COMBINED TESTS PASSED", "#10B981", "#1E293B")
    draw_box(50, 640, 475, 162, "3A. Dynamic Registry & Simulator", [
        "• Dynamic database-backed appliance definitions",
        "• 16-state combinatorial permutation logic",
        "• All appliances OFF = exactly 12.0 W residual",
        "• Calibrated power factor & apparent power math",
        "• State isolation across server restarts & resets"
    ], "#059669", "#34D399")

    draw_box(563, 640, 475, 162, "3B. Rule-Based NILM & ML Benchmarks", [
        "• 1 Hz active derivative step detector (Delta P, PF)",
        "• Noise floor suppression: |Delta P| < 5.0 W ignored",
        "• Simultaneous switching tagged: [AMBIGUOUS]",
        "• UK REFIT & Indian iAWE benchmark validation",
        "• Deep Learning Roadmap: Seq2Point & TCN models"
    ], "#0891B2", "#22D3EE")

    draw_box(1075, 640, 475, 162, "3C. Durable Persistence Layer", [
        "• SQLite (energy_mirror.db) for zero-dependency dev",
        "• PostgreSQL (psycopg2) production-ready driver",
        "• Alembic migrations (@ 8f8361eca0e9)",
        "• Deduplicated state event persistence & retrieval",
        "• Schema tables: telemetry, estimates, events, registry"
    ], "#9333EA", "#C084FC")

    # 4. Hardware Layer (360px each)
    draw_section(855, 245, "4. METROLOGY & HARDWARE INGESTION LAYER (LABORATORY BLUEPRINT)", "PENDING PHYSICAL PROCUREMENT", "#F59E0B", "#29200C")
    draw_box(50, 911, 360, 170, "Service Panel Sensing", [
        "• Single-point distribution panel sensing",
        "• PZEM-004T v3.0 Digital Energy IC",
        "• Split-core 100A / 100mA current clamp",
        "• Modbus-RTU over RS-485 / UART",
        "• 1 Hz V, I, P, PF, Frequency acquisition"
    ], "#D97706", "#FBBF24")

    draw_box(430, 911, 360, 170, "Low-Power CT Multi-Turn Scaling", [
        "• N = 10 primary conductor turns",
        "• Multiplies magnetic flux 10x (12W -> 120W)",
        "• Lifts low loads above CT non-linear floor",
        "• Firmware / Ingestion inverse divisor (N=10)",
        "• Enables sub-15W LED bulb measurement"
    ], "#D97706", "#FBBF24")

    draw_box(810, 911, 360, 170, "Firmware Architecture", [
        "• ESP32-WROOM-32D Dual-Core MCU",
        "• Core 0: FreeRTOS 1 Hz Modbus acquisition",
        "• Core 1: Wi-Fi HTTP POST client",
        "• HLK-PM01 5V isolated AC-DC supply",
        "• Ring buffer for offline network caching"
    ], "#D97706", "#FBBF24")

    draw_box(1190, 911, 360, 170, "Electrical Bench Safety & Ingest", [
        "• Single-pole 6A MCB (10kA breaking capacity)",
        "• 2-pole 30mA RCD / RCCB earth fault trip",
        "• 5kV Optocoupler galvanic isolation barrier",
        "• Endpoint: POST /api/v1/telemetry/ingest",
        "• Staged Inactive (ENABLE_HW_INGEST=false)"
    ], "#D97706", "#FBBF24")

    img.save(png_path, "PNG", optimize=True)
    print("System Architecture regenerated successfully!")


# ==============================================================================
# DIAGRAM 2: NILM CONCEPT DISAGGREGATION (nilm_concept_diagram.svg & .png)
# ==============================================================================
def generate_nilm_concept():
    svg_path = os.path.join(assets_dir, "nilm_concept_diagram.svg")
    png_path = os.path.join(assets_dir, "nilm_concept_diagram.png")

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 820" width="100%" height="100%" style="background-color: #0B0F19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="panelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="engineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0369A1"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#161F33"/>
      <stop offset="100%" stop-color="#0D1322"/>
    </linearGradient>
    <filter id="boxShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
  </defs>

  <!-- 0. HEADER BANNER -->
  <rect x="30" y="20" width="1540" height="65" rx="12" fill="#111827" stroke="#00E5FF" stroke-width="1.8" filter="url(#boxShadow)"/>
  <text x="55" y="56" fill="#FFFFFF" font-size="20" font-weight="800" letter-spacing="0.8">NON-INTRUSIVE LOAD MONITORING (NILM) DISAGGREGATION PRINCIPLE</text>
  <rect x="1255" y="36" width="290" height="32" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
  <text x="1400" y="56" fill="#34D399" font-size="11.5" font-weight="800" text-anchor="middle">ZERO SMART PLUGS REQUIRED</text>

  <!-- 1. TOP NODE: SERVICE PANEL SENSOR (Centered at x=800, width=700) -->
  <g transform="translate(450, 110)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="700" height="140" rx="14" fill="url(#panelGrad)" stroke="#F59E0B" stroke-width="2"/>
    <rect x="25" y="-12" width="280" height="24" rx="6" fill="#78350F" stroke="#F59E0B" stroke-width="1.2"/>
    <text x="165" y="4" fill="#FDE68A" font-size="11" font-weight="800" text-anchor="middle">SINGLE SERVICE PANEL SENSING POINT</text>
    
    <text x="30" y="42" fill="#FFFFFF" font-size="18" font-weight="800">Whole-Home Main Distribution Panel</text>
    <text x="30" y="66" fill="#FBBF24" font-size="13" font-weight="700">PZEM-004T v3.0 Metrology IC + Split-Core Current Transformer (CT)</text>
    
    <g transform="translate(25, 88)">
      <rect x="0" y="0" width="150" height="34" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="75" y="22" fill="#F8FAFC" font-size="12" font-weight="700" text-anchor="middle">Aggregate: 284.0 W</text>

      <rect x="166" y="0" width="150" height="34" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="241" y="22" fill="#F8FAFC" font-size="12" font-weight="700" text-anchor="middle">Voltage: 230.2 V</text>

      <rect x="332" y="0" width="150" height="34" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="407" y="22" fill="#F8FAFC" font-size="12" font-weight="700" text-anchor="middle">Power Factor: 0.96</text>

      <rect x="498" y="0" width="150" height="34" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="573" y="22" fill="#00E5FF" font-size="12" font-weight="700" text-anchor="middle">Sampling: 1 Hz Clock</text>
    </g>
  </g>

  <!-- Connector Line 1 -->
  <g stroke="#00E5FF" stroke-width="2.5" fill="none">
    <path d="M 800 250 L 800 310"/>
    <polygon points="793,300 807,300 800,312" fill="#00E5FF" stroke="none"/>
  </g>
  <rect x="660" y="266" width="280" height="26" rx="6" fill="#0B0F19" stroke="#00E5FF" stroke-width="1"/>
  <text x="800" y="283" fill="#00E5FF" font-size="11" font-weight="700" text-anchor="middle">1 Hz Aggregate Power &amp; PF Stream</text>

  <!-- 2. MIDDLE NODE: BACKEND ENGINE (Centered at x=800, width=780) -->
  <g transform="translate(410, 310)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="780" height="140" rx="14" fill="url(#engineGrad)" stroke="#00E5FF" stroke-width="2"/>
    <rect x="25" y="-12" width="290" height="24" rx="6" fill="#0C4A6E" stroke="#00E5FF" stroke-width="1.2"/>
    <text x="170" y="4" fill="#E0F2FE" font-size="11" font-weight="800" text-anchor="middle">ENERGY MIRROR DISAGGREGATION ENGINE</text>

    <text x="30" y="42" fill="#FFFFFF" font-size="19" font-weight="800">FastAPI Core + 1 Hz Derivative Edge NILM Detector</text>
    <text x="30" y="66" fill="#38BDF8" font-size="13" font-weight="600">Extracts Discrete Step Transitions: |Delta P| &gt;= 5.0 W &amp; Delta PF Envelopes</text>
    
    <g transform="translate(25, 88)">
      <rect x="0" y="0" width="230" height="34" rx="6" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="115" y="22" fill="#E2E8F0" font-size="11.5" font-weight="700" text-anchor="middle">Dynamic Signature Matching</text>

      <rect x="250" y="0" width="230" height="34" rx="6" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="365" y="22" fill="#E2E8F0" font-size="11.5" font-weight="700" text-anchor="middle">Exact Conservation Accounting</text>

      <rect x="500" y="0" width="230" height="34" rx="6" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="615" y="22" fill="#34D399" font-size="11.5" font-weight="700" text-anchor="middle">Deduplicated State Events</text>
    </g>
  </g>

  <!-- 3. BUS & DROP LINES -->
  <line x1="800" y1="450" x2="800" y2="500" stroke="#38BDF8" stroke-width="2.5"/>
  <line x1="174" y1="500" x2="1426" y2="500" stroke="#38BDF8" stroke-width="2.5"/>

  <!-- Drop Lines (EXACT CENTERS: 174, 487, 800, 1113, 1426) -->
  <g stroke="#38BDF8" stroke-width="2.5" fill="none">
    <path d="M 174 500 L 174 548"/>
    <polygon points="168,540 180,540 174,550" fill="#38BDF8" stroke="none"/>

    <path d="M 487 500 L 487 548"/>
    <polygon points="481,540 493,540 487,550" fill="#38BDF8" stroke="none"/>

    <path d="M 800 500 L 800 548"/>
    <polygon points="794,540 806,540 800,550" fill="#38BDF8" stroke="none"/>

    <path d="M 1113 500 L 1113 548"/>
    <polygon points="1107,540 1119,540 1113,550" fill="#38BDF8" stroke="none"/>

    <path d="M 1426 500 L 1426 548"/>
    <polygon points="1420,540 1432,540 1426,550" fill="#38BDF8" stroke="none"/>
  </g>

  <!-- Center Callout Pill -->
  <g transform="translate(620, 487)">
    <rect x="0" y="0" width="360" height="26" rx="6" fill="#0B0F19" stroke="#00E5FF" stroke-width="1.4"/>
    <text x="180" y="18" fill="#00E5FF" font-size="11.5" font-weight="800" text-anchor="middle">... ALL EXTRACTED FROM ONE SENSING POINT!</text>
  </g>

  <!-- 4. BOTTOM 5 APPLIANCE CARDS (288px width each, 25px gap, x=30, 343, 656, 969, 1282) -->
  <!-- Card 1 -->
  <g transform="translate(30, 552)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="288" height="235" rx="12" fill="url(#cardGrad)" stroke="#EF4444" stroke-width="1.8"/>
    <rect x="18" y="15" width="34" height="34" rx="8" fill="#450A0A" stroke="#EF4444" stroke-width="1"/>
    <text x="35" y="38" fill="#FCA5A5" font-size="18" font-weight="800" text-anchor="middle">♨</text>
    <text x="62" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Water Heater</text>

    <text x="18" y="78" fill="#EF4444" font-size="22" font-weight="800">140.0 W</text>
    <text x="135" y="78" fill="#94A3B8" font-size="13" font-weight="600">(49.3% Share)</text>

    <line x1="18" y1="95" x2="270" y2="95" stroke="#334155" stroke-width="1"/>
    <text x="18" y="120" fill="#CBD5E1" font-size="11.5">• Signature: Pure Resistive</text>
    <text x="18" y="144" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.99 (Unity)</text>
    <text x="18" y="168" fill="#CBD5E1" font-size="11.5">• Step Delta: +140 W / -140 W</text>
    
    <rect x="18" y="190" width="165" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="100" y="207" fill="#34D399" font-size="10.5" font-weight="800" text-anchor="middle">✓ Rule Envelope Matched</text>
  </g>

  <!-- Card 2 -->
  <g transform="translate(343, 552)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="288" height="235" rx="12" fill="url(#cardGrad)" stroke="#3B82F6" stroke-width="1.8"/>
    <rect x="18" y="15" width="34" height="34" rx="8" fill="#172554" stroke="#3B82F6" stroke-width="1"/>
    <text x="35" y="38" fill="#93C5FD" font-size="18" font-weight="800" text-anchor="middle">💧</text>
    <text x="62" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Water Pump</text>

    <text x="18" y="78" fill="#3B82F6" font-size="22" font-weight="800">75.0 W</text>
    <text x="125" y="78" fill="#94A3B8" font-size="13" font-weight="600">(26.4% Share)</text>

    <line x1="18" y1="95" x2="270" y2="95" stroke="#334155" stroke-width="1"/>
    <text x="18" y="120" fill="#CBD5E1" font-size="11.5">• Signature: Inductive Motor</text>
    <text x="18" y="144" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.78 Lagging</text>
    <text x="18" y="168" fill="#CBD5E1" font-size="11.5">• Step Delta: +75 W (Inrush)</text>
    
    <rect x="18" y="190" width="165" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="100" y="207" fill="#34D399" font-size="10.5" font-weight="800" text-anchor="middle">✓ Rule Envelope Matched</text>
  </g>

  <!-- Card 3 -->
  <g transform="translate(656, 552)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="288" height="235" rx="12" fill="url(#cardGrad)" stroke="#10B981" stroke-width="1.8"/>
    <rect x="18" y="15" width="34" height="34" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="35" y="38" fill="#A7F3D0" font-size="18" font-weight="800" text-anchor="middle">🌀</text>
    <text x="62" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Ceiling Fan</text>

    <text x="18" y="78" fill="#10B981" font-size="22" font-weight="800">45.0 W</text>
    <text x="125" y="78" fill="#94A3B8" font-size="13" font-weight="600">(15.8% Share)</text>

    <line x1="18" y1="95" x2="270" y2="95" stroke="#334155" stroke-width="1"/>
    <text x="18" y="120" fill="#CBD5E1" font-size="11.5">• Signature: Rotary Inductive</text>
    <text x="18" y="144" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.91 Lagging</text>
    <text x="18" y="168" fill="#CBD5E1" font-size="11.5">• Step Delta: +45 W / -45 W</text>
    
    <rect x="18" y="190" width="165" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="100" y="207" fill="#34D399" font-size="10.5" font-weight="800" text-anchor="middle">✓ Rule Envelope Matched</text>
  </g>

  <!-- Card 4 -->
  <g transform="translate(969, 552)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="288" height="235" rx="12" fill="url(#cardGrad)" stroke="#F59E0B" stroke-width="1.8"/>
    <rect x="18" y="15" width="34" height="34" rx="8" fill="#78350F" stroke="#F59E0B" stroke-width="1"/>
    <text x="35" y="38" fill="#FDE68A" font-size="18" font-weight="800" text-anchor="middle">💡</text>
    <text x="62" y="36" fill="#FFFFFF" font-size="16" font-weight="800">LED Bulb</text>

    <text x="18" y="78" fill="#F59E0B" font-size="22" font-weight="800">12.0 W</text>
    <text x="115" y="78" fill="#94A3B8" font-size="13" font-weight="600">(4.2% Share)</text>

    <line x1="18" y1="95" x2="270" y2="95" stroke="#334155" stroke-width="1"/>
    <text x="18" y="120" fill="#CBD5E1" font-size="11.5">• Signature: SMPS Driver</text>
    <text x="18" y="144" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.95 Leading</text>
    <text x="18" y="168" fill="#CBD5E1" font-size="11.5">• Scaled via N=10 CT turn</text>
    
    <rect x="18" y="190" width="165" height="26" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="100" y="207" fill="#34D399" font-size="10.5" font-weight="800" text-anchor="middle">✓ Rule Envelope Matched</text>
  </g>

  <!-- Card 5 -->
  <g transform="translate(1282, 552)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="288" height="235" rx="12" fill="url(#cardGrad)" stroke="#A855F7" stroke-width="1.8"/>
    <rect x="18" y="15" width="34" height="34" rx="8" fill="#4C1D95" stroke="#A855F7" stroke-width="1"/>
    <text x="35" y="38" fill="#DDD6FE" font-size="18" font-weight="800" text-anchor="middle">⚡</text>
    <text x="62" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Residual Floor</text>

    <text x="18" y="78" fill="#A855F7" font-size="22" font-weight="800">12.0 W</text>
    <text x="115" y="78" fill="#94A3B8" font-size="13" font-weight="600">(4.2% Floor)</text>

    <line x1="18" y1="95" x2="270" y2="95" stroke="#334155" stroke-width="1"/>
    <text x="18" y="120" fill="#CBD5E1" font-size="11.5">• Parasitic Standby Baseline</text>
    <text x="18" y="144" fill="#CBD5E1" font-size="11.5">• Smoke alarms, router, clock</text>
    <text x="18" y="168" fill="#CBD5E1" font-size="11.5">• Distinct from 12.0 W LED</text>
    
    <rect x="18" y="190" width="180" height="26" rx="6" fill="#3B0764" stroke="#A855F7" stroke-width="1"/>
    <text x="108" y="207" fill="#E9D5FF" font-size="10.5" font-weight="800" text-anchor="middle">✓ Conservation Invariant</text>
  </g>

</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    # Render PNG
    W, H = 1600, 820
    img = Image.new("RGB", (W, H), color="#0B0F19")
    draw = ImageDraw.Draw(img)

    # Top Bar
    draw.rounded_rectangle([30, 20, 1570, 85], radius=12, fill="#111827", outline="#00E5FF", width=2)
    draw.text((55, 38), "NON-INTRUSIVE LOAD MONITORING (NILM) DISAGGREGATION PRINCIPLE", fill="#FFFFFF", font=font_hero)
    draw.rounded_rectangle([1255, 36, 1545, 68], radius=6, fill="#064E3B", outline="#10B981", width=1)
    draw.text((1275, 45), "ZERO SMART PLUGS REQUIRED", fill="#34D399", font=font_badge)

    # Top Node (x=450, w=700)
    draw.rounded_rectangle([450, 110, 1150, 250], radius=14, fill="#151D2F", outline="#F59E0B", width=2)
    draw.rounded_rectangle([475, 98, 755, 122], radius=6, fill="#78350F", outline="#F59E0B", width=1)
    draw.text((490, 103), "SINGLE SERVICE PANEL SENSING POINT", fill="#FDE68A", font=font_badge)
    draw.text((480, 134), "Whole-Home Main Distribution Panel", fill="#FFFFFF", font=font_h2)
    draw.text((480, 162), "PZEM-004T v3.0 Metrology IC + Split-Core Current Transformer (CT)", fill="#FBBF24", font=font_h3)

    stats = [
        ("Aggregate: 284.0 W", 475),
        ("Voltage: 230.2 V", 641),
        ("Power Factor: 0.96", 807),
        ("Sampling: 1 Hz Clock", 973)
    ]
    for text, x in stats:
        draw.rounded_rectangle([x, 195, x + 150, 230], radius=6, fill="#1E293B", outline="#64748B", width=1)
        draw.text((x + 16, 205), text, fill="#F8FAFC", font=font_body)

    # Connector 1
    draw.line([(800, 250), (800, 310)], fill="#00E5FF", width=3)
    draw.rounded_rectangle([660, 266, 940, 292], radius=6, fill="#0B0F19", outline="#00E5FF", width=1)
    draw.text((680, 272), "1 Hz Aggregate Power & PF Stream", fill="#00E5FF", font=font_badge)

    # Middle Node (x=410, w=780)
    draw.rounded_rectangle([410, 310, 1190, 450], radius=14, fill="#102036", outline="#00E5FF", width=2)
    draw.rounded_rectangle([435, 298, 725, 322], radius=6, fill="#0C4A6E", outline="#00E5FF", width=1)
    draw.text((450, 303), "ENERGY MIRROR DISAGGREGATION ENGINE", fill="#E0F2FE", font=font_badge)
    draw.text((440, 335), "FastAPI Core + 1 Hz Derivative Edge NILM Detector", fill="#FFFFFF", font=font_h2)
    draw.text((440, 363), "Extracts Discrete Step Transitions: |Delta P| >= 5.0 W & Delta PF Envelopes", fill="#38BDF8", font=font_h3)

    engine_badges = [
        ("Dynamic Signature Matching", 435),
        ("Exact Conservation Accounting", 685),
        ("Deduplicated State Events", 935)
    ]
    for text, x in engine_badges:
        draw.rounded_rectangle([x, 395, x + 230, 430], radius=6, fill="#0F172A", outline="#0284C7", width=1)
        draw.text((x + 20, 405), text, fill="#E2E8F0", font=font_body)

    # Bus
    draw.line([(800, 450), (800, 500)], fill="#38BDF8", width=3)
    draw.line([(174, 500), (1426, 500)], fill="#38BDF8", width=3)

    draw.rounded_rectangle([620, 487, 980, 513], radius=6, fill="#0B0F19", outline="#00E5FF", width=1)
    draw.text((635, 493), "... ALL EXTRACTED FROM ONE SENSING POINT!", fill="#00E5FF", font=font_badge)

    appliances = [
        ("Water Heater", "140.0 W", "(49.3% Share)", "#EF4444", 30, [
            "• Signature: Pure Resistive",
            "• Power Factor: 0.99 (Unity)",
            "• Step Delta: +140 W / -140 W",
            "✓ Rule Envelope Matched"
        ]),
        ("Water Pump", "75.0 W", "(26.4% Share)", "#3B82F6", 343, [
            "• Signature: Inductive Motor",
            "• Power Factor: 0.78 Lagging",
            "• Step Delta: +75 W (Inrush)",
            "✓ Rule Envelope Matched"
        ]),
        ("Ceiling Fan", "45.0 W", "(15.8% Share)", "#10B981", 656, [
            "• Signature: Rotary Inductive",
            "• Power Factor: 0.91 Lagging",
            "• Step Delta: +45 W / -45 W",
            "✓ Rule Envelope Matched"
        ]),
        ("LED Bulb", "12.0 W", "(4.2% Share)", "#F59E0B", 969, [
            "• Signature: SMPS Driver",
            "• Power Factor: 0.95 Leading",
            "• Scaled via N=10 CT turn",
            "✓ Rule Envelope Matched"
        ]),
        ("Residual Floor", "12.0 W", "(4.2% Floor)", "#A855F7", 1282, [
            "• Parasitic Standby Baseline",
            "• Smoke alarms, router, clock",
            "• Distinct from 12.0 W LED",
            "✓ Conservation Invariant"
        ])
    ]

    for name, power, share, color, x, lines in appliances:
        center_x = x + 144
        draw.line([(center_x, 500), (center_x, 552)], fill="#38BDF8", width=3)
        draw.rounded_rectangle([x, 552, x + 288, 787], radius=12, fill="#131B2E", outline=color, width=2)
        
        draw.text((x + 18, 568), name, fill="#FFFFFF", font=font_h2)
        draw.text((x + 18, 598), power, fill=color, font=font_stat)
        draw.text((x + 120, 603), share, fill="#94A3B8", font=font_body)
        draw.line([(x + 18, 630), (x + 270, 630)], fill="#334155", width=1)
        
        curr_y = 645
        for line in lines:
            c = "#34D399" if "✓" in line else ("#C084FC" if "Invariant" in line else "#CBD5E1")
            draw.text((x + 18, curr_y), line, fill=c, font=font_body)
            curr_y += 24

    img.save(png_path, "PNG", optimize=True)
    print("NILM Concept diagram regenerated successfully!")


# ==============================================================================
# DIAGRAM 3: APPLIANCE BASELINE TABLE (appliance_baseline_table.svg & .png)
# ==============================================================================
def generate_appliance_baseline():
    svg_path = os.path.join(assets_dir, "appliance_baseline_table.svg")
    png_path = os.path.join(assets_dir, "appliance_baseline_table.png")

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 880" width="100%" height="100%" style="background-color: #0B0F19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="rowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#151D2F"/>
      <stop offset="100%" stop-color="#0D1322"/>
    </linearGradient>
    <linearGradient id="totGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0F2840"/>
      <stop offset="100%" stop-color="#091A2B"/>
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
  </defs>

  <!-- 0. TOP HEADER BANNER -->
  <rect x="30" y="20" width="1540" height="70" rx="12" fill="#111827" stroke="#00E5FF" stroke-width="1.8" filter="url(#cardShadow)"/>
  <text x="55" y="52" fill="#FFFFFF" font-size="20" font-weight="800" letter-spacing="0.8">VIRTUAL APPLIANCE BASELINE CONFIGURATION &amp; POWER ACCOUNTING</text>
  <text x="55" y="74" fill="#00E5FF" font-size="12.5" font-weight="600">P_aggregate (284.0 W) ≡ 140.0 W + 75.0 W + 45.0 W + 12.0 W + 12.0 W Residual Floor</text>

  <rect x="1255" y="38" width="285" height="30" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.4"/>
  <circle cx="1275" cy="53" r="5" fill="#10B981"/>
  <text x="1405" y="58" fill="#D1FAE5" font-size="11.5" font-weight="800" text-anchor="middle">100.0% CONSERVATION INVARIANT</text>

  <!-- 1. PROPORTIONAL STACKED BAR (Total = 1480px, x=60) -->
  <g transform="translate(30, 105)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="65" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
    <text x="25" y="24" fill="#94A3B8" font-size="11.5" font-weight="700">AGGREGATE HOUSEHOLD POWER DISTRIBUTION (284.0 W):</text>

    <g transform="translate(25, 34)">
      <!-- 1. Water Heater (49.3% = 730px) -->
      <path d="M 6 0 L 730 0 L 730 18 L 6 18 Q 0 18 0 12 L 0 6 Q 0 0 6 0 Z" fill="#EF4444"/>
      <text x="365" y="13" fill="#FFFFFF" font-size="10.5" font-weight="800" text-anchor="middle">Water Heater 140W (49.3%)</text>

      <!-- 2. Water Pump (26.4% = 391px) -->
      <rect x="732" y="0" width="391" height="18" fill="#3B82F6"/>
      <text x="927" y="13" fill="#FFFFFF" font-size="10.5" font-weight="800" text-anchor="middle">Water Pump 75W (26.4%)</text>

      <!-- 3. Ceiling Fan (15.8% = 234px) -->
      <rect x="1125" y="0" width="234" height="18" fill="#10B981"/>
      <text x="1242" y="13" fill="#FFFFFF" font-size="10" font-weight="800" text-anchor="middle">Fan 45W (15.8%)</text>

      <!-- 4. LED Bulb (4.2% = 62.5px) -->
      <rect x="1361" y="0" width="62" height="18" fill="#F59E0B"/>
      <text x="1392" y="13" fill="#000000" font-size="9" font-weight="800" text-anchor="middle">12W</text>

      <!-- 5. Standby Floor (4.2% = 62.5px) -->
      <path d="M 1425 0 L 1484 0 Q 1490 0 1490 6 L 1490 12 Q 1490 18 1484 18 L 1425 18 Z" fill="#A855F7"/>
      <text x="1457" y="13" fill="#FFFFFF" font-size="9" font-weight="800" text-anchor="middle">Floor</text>
    </g>
  </g>

  <!-- 2. TABLE HEADER ROW (Total width=1540, aligned columns) -->
  <!-- Col 1: 55, Col 2: 350, Col 3: 520, Col 4: 720, Col 5: 940 (width 400!), Col 6: 1370 -->
  <g transform="translate(30, 185)">
    <rect x="0" y="0" width="1540" height="42" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
    <text x="35" y="26" fill="#94A3B8" font-size="12" font-weight="800">APPLIANCE / LOAD NAME</text>
    <text x="350" y="26" fill="#94A3B8" font-size="12" font-weight="800">ACTIVE POWER (W)</text>
    <text x="520" y="26" fill="#94A3B8" font-size="12" font-weight="800">POWER FACTOR (PF)</text>
    <text x="720" y="26" fill="#94A3B8" font-size="12" font-weight="800">NOMINAL SHARE (%)</text>
    <text x="940" y="26" fill="#94A3B8" font-size="12" font-weight="800">ELECTRICAL SIGNATURE &amp; PHYSICS</text>
    <text x="1370" y="26" fill="#94A3B8" font-size="12" font-weight="800">DETECTION ENVELOPE</text>
  </g>

  <!-- 3. TABLE BODY ROWS -->
  <!-- ROW 1 -->
  <g transform="translate(30, 235)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#EF4444" stroke-width="1.2"/>
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#450A0A" stroke="#EF4444" stroke-width="1"/>
    <text x="44" y="42" fill="#FCA5A5" font-size="18" font-weight="800" text-anchor="middle">♨</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Water Heater</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Heating Element (water_heater_01)</text>

    <rect x="350" y="18" width="130" height="36" rx="6" fill="#201015" stroke="#EF4444" stroke-width="1"/>
    <text x="415" y="42" fill="#EF4444" font-size="16" font-weight="800" text-anchor="middle">140.0 W</text>

    <rect x="520" y="18" width="150" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="595" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.99 (Unity)</text>

    <g transform="translate(720, 24)">
      <text x="0" y="16" fill="#EF4444" font-size="16" font-weight="800">49.3%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="56" height="12" rx="4" fill="#EF4444"/>
    </g>

    <text x="940" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Pure Resistive Nichrome</text>
    <text x="940" y="52" fill="#94A3B8" font-size="11.5">No inrush spike; instant flat step transition</text>

    <rect x="1370" y="20" width="145" height="32" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1442" y="41" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 2 -->
  <g transform="translate(30, 315)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#3B82F6" stroke-width="1.2"/>
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#172554" stroke="#3B82F6" stroke-width="1"/>
    <text x="44" y="42" fill="#93C5FD" font-size="18" font-weight="800" text-anchor="middle">💧</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Water Pump</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Induction Motor (water_pump_01)</text>

    <rect x="350" y="18" width="130" height="36" rx="6" fill="#10182E" stroke="#3B82F6" stroke-width="1"/>
    <text x="415" y="42" fill="#3B82F6" font-size="16" font-weight="800" text-anchor="middle">75.0 W</text>

    <rect x="520" y="18" width="150" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="595" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.78 Lagging</text>

    <g transform="translate(720, 24)">
      <text x="0" y="16" fill="#3B82F6" font-size="16" font-weight="800">26.4%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="30" height="12" rx="4" fill="#3B82F6"/>
    </g>

    <text x="940" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Inductive Motor Inrush</text>
    <text x="940" y="52" fill="#94A3B8" font-size="11.5">Lagging PF transition envelope with starting spike</text>

    <rect x="1370" y="20" width="145" height="32" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1442" y="41" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 3 -->
  <g transform="translate(30, 395)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#10B981" stroke-width="1.2"/>
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="44" y="42" fill="#A7F3D0" font-size="18" font-weight="800" text-anchor="middle">🌀</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Ceiling Fan</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Rotary Motor (ceiling_fan_01)</text>

    <rect x="350" y="18" width="130" height="36" rx="6" fill="#0F241E" stroke="#10B981" stroke-width="1"/>
    <text x="415" y="42" fill="#10B981" font-size="16" font-weight="800" text-anchor="middle">45.0 W</text>

    <rect x="520" y="18" width="150" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="595" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.91 Lagging</text>

    <g transform="translate(720, 24)">
      <text x="0" y="16" fill="#10B981" font-size="16" font-weight="800">15.8%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="18" height="12" rx="4" fill="#10B981"/>
    </g>

    <text x="940" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Rotary Inductive Load</text>
    <text x="940" y="52" fill="#94A3B8" font-size="11.5">Moderate inductive phase shift with stable plateau</text>

    <rect x="1370" y="20" width="145" height="32" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1442" y="41" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 4 -->
  <g transform="translate(30, 475)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#F59E0B" stroke-width="1.2"/>
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#78350F" stroke="#F59E0B" stroke-width="1"/>
    <text x="44" y="42" fill="#FDE68A" font-size="18" font-weight="800" text-anchor="middle">💡</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">LED Bulb</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Solid-State Lighting (led_bulb_01)</text>

    <rect x="350" y="18" width="130" height="36" rx="6" fill="#251A08" stroke="#F59E0B" stroke-width="1"/>
    <text x="415" y="42" fill="#F59E0B" font-size="16" font-weight="800" text-anchor="middle">12.0 W</text>

    <rect x="520" y="18" width="150" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="595" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.95 Leading</text>

    <g transform="translate(720, 24)">
      <text x="0" y="16" fill="#F59E0B" font-size="16" font-weight="800">4.2%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="6" height="12" rx="4" fill="#F59E0B"/>
    </g>

    <text x="940" y="35" fill="#E2E8F0" font-size="13" font-weight="700">SMPS Driver Rectifier</text>
    <text x="940" y="52" fill="#94A3B8" font-size="11.5">Capacitive filter leading PF; scaled via N=10 CT turn</text>

    <rect x="1370" y="20" width="145" height="32" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1442" y="41" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 5 -->
  <g transform="translate(30, 555)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#A855F7" stroke-width="1.2"/>
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#4C1D95" stroke="#A855F7" stroke-width="1"/>
    <text x="44" y="42" fill="#DDD6FE" font-size="18" font-weight="800" text-anchor="middle">⚡</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Unattributed Residual Floor</text>
    <text x="75" y="52" fill="#C084FC" font-size="11.5">Strictly Distinct from 12.0 W LED Bulb</text>

    <rect x="350" y="18" width="130" height="36" rx="6" fill="#1D112A" stroke="#A855F7" stroke-width="1"/>
    <text x="415" y="42" fill="#A855F7" font-size="16" font-weight="800" text-anchor="middle">12.0 W</text>

    <rect x="520" y="18" width="150" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="595" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">1.00 Nominal</text>

    <g transform="translate(720, 24)">
      <text x="0" y="16" fill="#A855F7" font-size="16" font-weight="800">4.2%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="6" height="12" rx="4" fill="#A855F7"/>
    </g>

    <text x="940" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Parasitic Ambient Standby Load</text>
    <text x="940" y="52" fill="#94A3B8" font-size="11.5">Smoke detectors, Wi-Fi router, microwave clock</text>

    <rect x="1370" y="20" width="145" height="32" rx="6" fill="#3B0764" stroke="#A855F7" stroke-width="1.2"/>
    <text x="1442" y="41" fill="#E9D5FF" font-size="11" font-weight="800" text-anchor="middle">RESIDUAL BASELINE</text>
  </g>

  <!-- 4. TOTAL RECONCILIATION SUMMARY FOOTER -->
  <g transform="translate(30, 645)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="85" rx="12" fill="url(#totGrad)" stroke="#00E5FF" stroke-width="2"/>
    <text x="35" y="38" fill="#FFFFFF" font-size="18" font-weight="800">TOTAL HOUSEHOLD AGGREGATE</text>
    <text x="35" y="62" fill="#00E5FF" font-size="12" font-weight="700">P_aggregate = Sum(P_attributed 272W) + P_residual (12W)</text>

    <rect x="350" y="22" width="130" height="42" rx="8" fill="#0A2239" stroke="#00E5FF" stroke-width="1.6"/>
    <text x="415" y="50" fill="#00E5FF" font-size="19" font-weight="800" text-anchor="middle">284.0 W</text>

    <rect x="520" y="22" width="150" height="42" rx="8" fill="#0A2239" stroke="#00E5FF" stroke-width="1.6"/>
    <text x="595" y="50" fill="#00E5FF" font-size="17" font-weight="800" text-anchor="middle">0.96 Net PF</text>

    <rect x="720" y="22" width="140" height="42" rx="8" fill="#0A2239" stroke="#00E5FF" stroke-width="1.6"/>
    <text x="790" y="50" fill="#00E5FF" font-size="18" font-weight="800" text-anchor="middle">100.0%</text>

    <rect x="940" y="22" width="575" height="42" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1.6"/>
    <text x="1227" y="48" fill="#E6FFFA" font-size="13" font-weight="800" text-anchor="middle">✓ ZERO POWER LEAKAGE • EXACT ARITHMETIC RECONCILIATION</text>
  </g>

  <!-- Footnotes -->
  <text x="55" y="765" fill="#94A3B8" font-size="12">• Note: The continuous 12.0 W residual floor is an ambient parasitic baseline assumption and is mathematically distinct from the 12.0 W LED bulb load.</text>
  <text x="55" y="790" fill="#94A3B8" font-size="12">• Dynamic Behavior: When all 4 virtual appliances are toggled OFF in the simulator lab, active power drops to exactly 12.0 W (100% unattributed residual).</text>

</svg>
"""
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    # Render PNG
    W, H = 1600, 880
    img = Image.new("RGB", (W, H), color="#0B0F19")
    draw = ImageDraw.Draw(img)

    # Top Bar
    draw.rounded_rectangle([30, 20, 1570, 90], radius=12, fill="#111827", outline="#00E5FF", width=2)
    draw.text((55, 35), "VIRTUAL APPLIANCE BASELINE CONFIGURATION & POWER ACCOUNTING", fill="#FFFFFF", font=font_hero)
    draw.text((55, 64), "P_aggregate (284.0 W) = 140.0 W + 75.0 W + 45.0 W + 12.0 W + 12.0 W Residual Floor", fill="#00E5FF", font=font_h3)

    draw.rounded_rectangle([1255, 38, 1545, 68], radius=6, fill="#064E3B", outline="#10B981", width=1)
    draw.text((1275, 46), "100.0% CONSERVATION INVARIANT", fill="#D1FAE5", font=font_badge)

    # Proportional Bar
    draw.rounded_rectangle([30, 105, 1570, 170], radius=10, fill="#1E293B", outline="#334155", width=1)
    draw.text((55, 116), "AGGREGATE HOUSEHOLD POWER DISTRIBUTION (284.0 W):", fill="#94A3B8", font=font_badge)

    draw.rounded_rectangle([55, 137, 785, 157], radius=4, fill="#EF4444")
    draw.text((360, 141), "Water Heater 140W (49.3%)", fill="#FFFFFF", font=font_badge)

    draw.rectangle([787, 137, 1178, 157], fill="#3B82F6")
    draw.text((940, 141), "Water Pump 75W (26.4%)", fill="#FFFFFF", font=font_badge)

    draw.rectangle([1180, 137, 1414, 157], fill="#10B981")
    draw.text((1260, 141), "Fan 45W (15.8%)", fill="#FFFFFF", font=font_badge)

    draw.rectangle([1416, 137, 1478, 157], fill="#F59E0B")
    draw.text((1432, 141), "12W", fill="#000000", font=font_badge)

    draw.rounded_rectangle([1480, 137, 1545, 157], radius=4, fill="#A855F7")
    draw.text((1495, 141), "Floor", fill="#FFFFFF", font=font_badge)

    # Table Header
    draw.rounded_rectangle([30, 185, 1570, 227], radius=8, fill="#1E293B", outline="#334155", width=1)
    draw.text((65, 200), "APPLIANCE / LOAD NAME", fill="#94A3B8", font=font_badge)
    draw.text((380, 200), "ACTIVE POWER (W)", fill="#94A3B8", font=font_badge)
    draw.text((550, 200), "POWER FACTOR (PF)", fill="#94A3B8", font=font_badge)
    draw.text((750, 200), "NOMINAL SHARE (%)", fill="#94A3B8", font=font_badge)
    draw.text((970, 200), "ELECTRICAL SIGNATURE & PHYSICS", fill="#94A3B8", font=font_badge)
    draw.text((1400, 200), "DETECTION ENVELOPE", fill="#94A3B8", font=font_badge)

    # Rows
    rows = [
        ("Water Heater", "Heating Element (water_heater_01)", "140.0 W", "0.99 (Unity)", "49.3%", "#EF4444", "Pure Resistive Nichrome", "No inrush spike; instant flat step transition", 235),
        ("Water Pump", "Induction Motor (water_pump_01)", "75.0 W", "0.78 Lagging", "26.4%", "#3B82F6", "Inductive Motor Inrush", "Lagging PF transition envelope with starting spike", 315),
        ("Ceiling Fan", "Rotary Motor (ceiling_fan_01)", "45.0 W", "0.91 Lagging", "15.8%", "#10B981", "Rotary Inductive Load", "Moderate inductive phase shift with stable plateau", 395),
        ("LED Bulb", "Solid-State Lighting (led_bulb_01)", "12.0 W", "0.95 Leading", "4.2%", "#F59E0B", "SMPS Driver Rectifier", "Capacitive filter leading PF; scaled via N=10 CT turn", 475),
        ("Residual Floor", "Strictly Distinct from 12.0W LED", "12.0 W", "1.00 Nominal", "4.2%", "#A855F7", "Parasitic Ambient Standby", "Smoke detectors, Wi-Fi router, microwave clock", 555)
    ]

    for name, sub, power, pf, share, color, sig, desc, y in rows:
        draw.rounded_rectangle([30, y, 1570, y + 70], radius=10, fill="#131B2E", outline=color, width=1)
        
        draw.text((65, y + 16), name, fill="#FFFFFF", font=font_h2)
        draw.text((65, y + 42), sub, fill="#94A3B8", font=font_body)

        draw.rounded_rectangle([350, y + 16, 480, y + 54], radius=6, fill="#0F172A", outline=color, width=1)
        draw.text((378, y + 25), power, fill=color, font=font_stat)

        draw.rounded_rectangle([520, y + 16, 670, y + 54], radius=6, fill="#1E293B", outline="#64748B", width=1)
        draw.text((545, y + 27), pf, fill="#F8FAFC", font=font_h3)

        draw.text((750, y + 26), share, fill=color, font=font_stat)

        draw.text((970, y + 16), sig, fill="#E2E8F0", font=font_h3)
        draw.text((970, y + 42), desc, fill="#94A3B8", font=font_body)

        badge_bg = "#3B0764" if "Residual" in name else "#064E3B"
        badge_bd = "#A855F7" if "Residual" in name else "#10B981"
        badge_tx = "RESIDUAL BASELINE" if "Residual" in name else "PRODUCTION RULE"
        draw.rounded_rectangle([1370, y + 20, 1520, y + 50], radius=6, fill=badge_bg, outline=badge_bd, width=1)
        draw.text((1385, y + 28), badge_tx, fill=badge_bd, font=font_badge)

    # Footer
    draw.rounded_rectangle([30, 645, 1570, 730], radius=12, fill="#0F2840", outline="#00E5FF", width=2)
    draw.text((55, 660), "TOTAL HOUSEHOLD AGGREGATE", fill="#FFFFFF", font=font_h2)
    draw.text((55, 688), "P_aggregate = Sum(P_attributed 272W) + P_residual (12W)", fill="#00E5FF", font=font_body)

    draw.rounded_rectangle([350, 660, 480, 712], radius=8, fill="#0A2239", outline="#00E5FF", width=2)
    draw.text((375, 675), "284.0 W", fill="#00E5FF", font=font_stat)

    draw.rounded_rectangle([520, 660, 670, 712], radius=8, fill="#0A2239", outline="#00E5FF", width=2)
    draw.text((545, 677), "0.96 Net PF", fill="#00E5FF", font=font_stat)

    draw.rounded_rectangle([720, 660, 850, 712], radius=8, fill="#0A2239", outline="#00E5FF", width=2)
    draw.text((750, 677), "100.0%", fill="#00E5FF", font=font_stat)

    draw.rounded_rectangle([940, 660, 1540, 712], radius=8, fill="#064E3B", outline="#10B981", width=2)
    draw.text((1000, 677), "✓ ZERO POWER LEAKAGE • EXACT ARITHMETIC RECONCILIATION", fill="#E6FFFA", font=font_h3)

    draw.text((55, 765), "• Note: The continuous 12.0 W residual floor is an ambient parasitic baseline assumption and is mathematically distinct from the 12.0 W LED bulb load.", fill="#94A3B8", font=font_body)
    draw.text((55, 790), "• Dynamic Behavior: When all 4 virtual appliances are toggled OFF in the simulator, active power drops to exactly 12.0 W (100% unattributed residual).", fill="#94A3B8", font=font_body)

    img.save(png_path, "PNG", optimize=True)
    print("Appliance Baseline diagram regenerated successfully!")


if __name__ == "__main__":
    generate_system_architecture()
    generate_nilm_concept()
    generate_appliance_baseline()
    print("All 3 diagrams generated and aligned with mathematical precision!")
