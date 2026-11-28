import os
from PIL import Image, ImageDraw, ImageFont

assets_dir = r"C:\Users\Kaviya\Downloads\Energy Mirror\docs\assets"
os.makedirs(assets_dir, exist_ok=True)
svg_path = os.path.join(assets_dir, "appliance_baseline_table.svg")
png_path = os.path.join(assets_dir, "appliance_baseline_table.png")

# ==========================================
# 1. VECTOR SVG GENERATION
# ==========================================
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 840" width="100%" height="100%" style="background-color: #0B0F19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="rowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#151D2F"/>
      <stop offset="100%" stop-color="#0D1322"/>
    </linearGradient>
    <linearGradient id="totGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0F2840"/>
      <stop offset="100%" stop-color="#091A2B"/>
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- ========================================== -->
  <!-- 0. TOP HEADER BANNER                       -->
  <!-- ========================================== -->
  <rect x="30" y="20" width="1540" height="70" rx="12" fill="#111827" stroke="#00E5FF" stroke-width="1.8" filter="url(#cardShadow)"/>
  <text x="60" y="52" fill="#FFFFFF" font-size="20" font-weight="800" letter-spacing="0.8">VIRTUAL APPLIANCE BASELINE CONFIGURATION &amp; POWER ACCOUNTING</text>
  <text x="60" y="74" fill="#00E5FF" font-size="12.5" font-weight="600">P_aggregate (284.0 W) ≡ 140.0 W + 75.0 W + 45.0 W + 12.0 W + 12.0 W Residual Floor</text>

  <rect x="1245" y="38" width="300" height="30" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.4"/>
  <circle cx="1265" cy="53" r="5" fill="#10B981"/>
  <text x="1280" y="58" fill="#D1FAE5" font-size="11.5" font-weight="800">100.0% CONSERVATION INVARIANT</text>

  <!-- ========================================== -->
  <!-- 1. VISUAL PROPORTIONAL STACKED BAR         -->
  <!-- ========================================== -->
  <g transform="translate(30, 105)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="60" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
    <text x="18" y="24" fill="#94A3B8" font-size="11.5" font-weight="700">AGGREGATE HOUSEHOLD POWER DISTRIBUTION (284.0 W):</text>

    <!-- Stacked segments bar (Width = 1500, X = 20, Y = 32, H = 18) -->
    <!-- Total width: 1500 px -->
    <!-- 49.3% = 739.5 px -->
    <!-- 26.4% = 396.0 px -->
    <!-- 15.8% = 237.0 px -->
    <!--  4.2% =  63.5 px -->
    <!--  4.2% =  64.0 px -->
    <!-- Total = 1500 px -->
    
    <g transform="translate(20, 32)">
      <!-- 1. Water Heater (49.3%) -->
      <path d="M 6 0 L 739 0 L 739 18 L 6 18 Q 0 18 0 12 L 0 6 Q 0 0 6 0 Z" fill="#EF4444"/>
      <text x="370" y="13" fill="#FFFFFF" font-size="10.5" font-weight="800" text-anchor="middle">Water Heater 140W (49.3%)</text>

      <!-- 2. Water Pump (26.4%) -->
      <rect x="741" y="0" width="395" height="18" fill="#3B82F6"/>
      <text x="938" y="13" fill="#FFFFFF" font-size="10.5" font-weight="800" text-anchor="middle">Water Pump 75W (26.4%)</text>

      <!-- 3. Ceiling Fan (15.8%) -->
      <rect x="1138" y="0" width="236" height="18" fill="#10B981"/>
      <text x="1256" y="13" fill="#FFFFFF" font-size="10" font-weight="800" text-anchor="middle">Fan 45W (15.8%)</text>

      <!-- 4. LED Bulb (4.2%) -->
      <rect x="1376" y="0" width="61" height="18" fill="#F59E0B"/>
      <text x="1406" y="13" fill="#000000" font-size="9" font-weight="800" text-anchor="middle">12W</text>

      <!-- 5. Standby Floor (4.2%) -->
      <path d="M 1439 0 L 1494 0 Q 1500 0 1500 6 L 1500 12 Q 1500 18 1494 18 L 1439 18 Z" fill="#A855F7"/>
      <text x="1469" y="13" fill="#FFFFFF" font-size="9" font-weight="800" text-anchor="middle">Floor</text>
    </g>
  </g>

  <!-- ========================================== -->
  <!-- 2. TABLE HEADER ROW                        -->
  <!-- ========================================== -->
  <g transform="translate(30, 180)">
    <rect x="0" y="0" width="1540" height="42" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
    <text x="35" y="26" fill="#94A3B8" font-size="12.5" font-weight="800">APPLIANCE / LOAD NAME</text>
    <text x="360" y="26" fill="#94A3B8" font-size="12.5" font-weight="800">ACTIVE POWER (W)</text>
    <text x="560" y="26" fill="#94A3B8" font-size="12.5" font-weight="800">POWER FACTOR (PF)</text>
    <text x="790" y="26" fill="#94A3B8" font-size="12.5" font-weight="800">NOMINAL SHARE (%)</text>
    <text x="1030" y="26" fill="#94A3B8" font-size="12.5" font-weight="800">ELECTRICAL SIGNATURE &amp; PHYSICS</text>
    <text x="1410" y="26" fill="#94A3B8" font-size="12.5" font-weight="800">DETECTION ENVELOPE</text>
  </g>

  <!-- ========================================== -->
  <!-- 3. TABLE BODY ROWS                         -->
  <!-- ========================================== -->
  <!-- ROW 1: Water Heater -->
  <g transform="translate(30, 230)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#EF4444" stroke-width="1.2"/>
    
    <!-- Name with icon -->
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#450A0A" stroke="#EF4444" stroke-width="1"/>
    <text x="44" y="42" fill="#FCA5A5" font-size="18" font-weight="800" text-anchor="middle">♨</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Water Heater</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Heating Element (water_heater_01)</text>

    <!-- Power Badge -->
    <rect x="360" y="18" width="125" height="36" rx="6" fill="#201015" stroke="#EF4444" stroke-width="1"/>
    <text x="422" y="42" fill="#EF4444" font-size="16" font-weight="800" text-anchor="middle">140.0 W</text>

    <!-- PF Badge -->
    <rect x="560" y="18" width="145" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="632" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.99 (Unity)</text>

    <!-- Share Progress -->
    <g transform="translate(790, 24)">
      <text x="0" y="16" fill="#EF4444" font-size="16" font-weight="800">49.3%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="56" height="12" rx="4" fill="#EF4444"/>
    </g>

    <!-- Signature -->
    <text x="1030" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Pure Resistive Nichrome</text>
    <text x="1030" y="52" fill="#94A3B8" font-size="11.5">No inrush spike; instant flat step transition</text>

    <!-- Tag -->
    <rect x="1380" y="20" width="140" height="30" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1450" y="39" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 2: Water Pump -->
  <g transform="translate(30, 310)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#3B82F6" stroke-width="1.2"/>
    
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#172554" stroke="#3B82F6" stroke-width="1"/>
    <text x="44" y="42" fill="#93C5FD" font-size="18" font-weight="800" text-anchor="middle">💧</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Water Pump</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Induction Motor (water_pump_01)</text>

    <rect x="360" y="18" width="125" height="36" rx="6" fill="#10182E" stroke="#3B82F6" stroke-width="1"/>
    <text x="422" y="42" fill="#3B82F6" font-size="16" font-weight="800" text-anchor="middle">75.0 W</text>

    <rect x="560" y="18" width="145" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="632" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.78 Lagging</text>

    <g transform="translate(790, 24)">
      <text x="0" y="16" fill="#3B82F6" font-size="16" font-weight="800">26.4%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="30" height="12" rx="4" fill="#3B82F6"/>
    </g>

    <text x="1030" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Inductive Motor Inrush</text>
    <text x="1030" y="52" fill="#94A3B8" font-size="11.5">Lagging PF transition envelope with starting spike</text>

    <rect x="1380" y="20" width="140" height="30" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1450" y="39" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 3: Ceiling Fan -->
  <g transform="translate(30, 390)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#10B981" stroke-width="1.2"/>
    
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="44" y="42" fill="#A7F3D0" font-size="18" font-weight="800" text-anchor="middle">🌀</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Ceiling Fan</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Rotary Motor (ceiling_fan_01)</text>

    <rect x="360" y="18" width="125" height="36" rx="6" fill="#0F241E" stroke="#10B981" stroke-width="1"/>
    <text x="422" y="42" fill="#10B981" font-size="16" font-weight="800" text-anchor="middle">45.0 W</text>

    <rect x="560" y="18" width="145" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="632" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.91 Lagging</text>

    <g transform="translate(790, 24)">
      <text x="0" y="16" fill="#10B981" font-size="16" font-weight="800">15.8%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="18" height="12" rx="4" fill="#10B981"/>
    </g>

    <text x="1030" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Rotary Inductive Load</text>
    <text x="1030" y="52" fill="#94A3B8" font-size="11.5">Moderate inductive phase shift with stable plateau</text>

    <rect x="1380" y="20" width="140" height="30" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1450" y="39" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 4: LED Bulb -->
  <g transform="translate(30, 470)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#F59E0B" stroke-width="1.2"/>
    
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#78350F" stroke="#F59E0B" stroke-width="1"/>
    <text x="44" y="42" fill="#FDE68A" font-size="18" font-weight="800" text-anchor="middle">💡</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">LED Bulb</text>
    <text x="75" y="52" fill="#94A3B8" font-size="11.5">Solid-State Lighting (led_bulb_01)</text>

    <rect x="360" y="18" width="125" height="36" rx="6" fill="#251A08" stroke="#F59E0B" stroke-width="1"/>
    <text x="422" y="42" fill="#F59E0B" font-size="16" font-weight="800" text-anchor="middle">12.0 W</text>

    <rect x="560" y="18" width="145" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="632" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">0.95 Leading</text>

    <g transform="translate(790, 24)">
      <text x="0" y="16" fill="#F59E0B" font-size="16" font-weight="800">4.2%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="6" height="12" rx="4" fill="#F59E0B"/>
    </g>

    <text x="1030" y="35" fill="#E2E8F0" font-size="13" font-weight="700">SMPS Driver Rectifier</text>
    <text x="1030" y="52" fill="#94A3B8" font-size="11.5">Capacitive filter leading PF; scaled via N=10 CT turn</text>

    <rect x="1380" y="20" width="140" height="30" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
    <text x="1450" y="39" fill="#34D399" font-size="11" font-weight="800" text-anchor="middle">PRODUCTION RULE</text>
  </g>

  <!-- ROW 5: Unattributed Standby Floor -->
  <g transform="translate(30, 550)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="72" rx="10" fill="url(#rowGrad)" stroke="#A855F7" stroke-width="1.2"/>
    
    <rect x="25" y="16" width="38" height="38" rx="8" fill="#4C1D95" stroke="#A855F7" stroke-width="1"/>
    <text x="44" y="42" fill="#DDD6FE" font-size="18" font-weight="800" text-anchor="middle">⚡</text>
    <text x="75" y="35" fill="#FFFFFF" font-size="15.5" font-weight="800">Unattributed Residual Floor</text>
    <text x="75" y="52" fill="#C084FC" font-size="11.5">Strictly Distinct from 12.0 W LED Bulb</text>

    <rect x="360" y="18" width="125" height="36" rx="6" fill="#1D112A" stroke="#A855F7" stroke-width="1"/>
    <text x="422" y="42" fill="#A855F7" font-size="16" font-weight="800" text-anchor="middle">12.0 W</text>

    <rect x="560" y="18" width="145" height="36" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
    <text x="632" y="41" fill="#F8FAFC" font-size="14" font-weight="700" text-anchor="middle">1.00 Nominal</text>

    <g transform="translate(790, 24)">
      <text x="0" y="16" fill="#A855F7" font-size="16" font-weight="800">4.2%</text>
      <rect x="65" y="6" width="115" height="12" rx="4" fill="#1E293B"/>
      <rect x="65" y="6" width="6" height="12" rx="4" fill="#A855F7"/>
    </g>

    <text x="1030" y="35" fill="#E2E8F0" font-size="13" font-weight="700">Parasitic Ambient Standby Load</text>
    <text x="1030" y="52" fill="#94A3B8" font-size="11.5">Smoke detectors, Wi-Fi router, microwave clock</text>

    <rect x="1380" y="20" width="140" height="30" rx="6" fill="#3B0764" stroke="#A855F7" stroke-width="1.2"/>
    <text x="1450" y="39" fill="#E9D5FF" font-size="11" font-weight="800" text-anchor="middle">RESIDUAL BASELINE</text>
  </g>

  <!-- ========================================== -->
  <!-- 4. TOTAL RECONCILIATION SUMMARY FOOTER     -->
  <!-- ========================================== -->
  <g transform="translate(30, 635)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1540" height="85" rx="12" fill="url(#totGrad)" stroke="#00E5FF" stroke-width="2"/>
    
    <!-- Title -->
    <text x="35" y="38" fill="#FFFFFF" font-size="18" font-weight="800">TOTAL HOUSEHOLD AGGREGATE</text>
    <text x="35" y="62" fill="#00E5FF" font-size="12" font-weight="700">P_aggregate = Sum(P_attributed 272W) + P_residual (12W)</text>

    <!-- Total Active Power -->
    <rect x="360" y="22" width="145" height="42" rx="8" fill="#0A2239" stroke="#00E5FF" stroke-width="1.6"/>
    <text x="432" y="50" fill="#00E5FF" font-size="20" font-weight="800" text-anchor="middle">284.0 W</text>

    <!-- Total PF -->
    <rect x="560" y="22" width="155" height="42" rx="8" fill="#0A2239" stroke="#00E5FF" stroke-width="1.6"/>
    <text x="637" y="50" fill="#00E5FF" font-size="18" font-weight="800" text-anchor="middle">0.96 Net PF</text>

    <!-- Total Share -->
    <rect x="790" y="22" width="140" height="42" rx="8" fill="#0A2239" stroke="#00E5FF" stroke-width="1.6"/>
    <text x="860" y="50" fill="#00E5FF" font-size="18" font-weight="800" text-anchor="middle">100.0%</text>

    <!-- Right-side verification pill -->
    <rect x="1100" y="22" width="420" height="42" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1.6"/>
    <text x="1310" y="48" fill="#E6FFFA" font-size="13" font-weight="800" text-anchor="middle">✓ ZERO POWER LEAKAGE • EXACT ARITHMETIC RECONCILIATION</text>
  </g>

  <!-- Note Footer -->
  <text x="60" y="750" fill="#64748B" font-size="12">• Note: The continuous 12.0 W residual floor is an ambient parasitic baseline assumption (smoke alarms, routers, standby clocks) and is mathematically distinct from the 12.0 W LED bulb load.</text>
  <text x="60" y="770" fill="#64748B" font-size="12">• Dynamic Behavior: When all 4 virtual appliances are toggled OFF in the simulator lab, active aggregate power drops to exactly 12.0 W (100% unattributed residual).</text>

</svg>
"""

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Appliance Baseline SVG generated: {svg_path} ({os.path.getsize(svg_path)} bytes)")

# ==========================================
# 2. HIGH-RES RASTER PNG VIA PILLOW
# ==========================================
W, H = 1600, 840
img = Image.new("RGB", (W, H), color="#0B0F19")
draw = ImageDraw.Draw(img)

try:
    font_hero = ImageFont.truetype("arialbd.ttf", 20)
    font_h2 = ImageFont.truetype("arialbd.ttf", 15)
    font_h3 = ImageFont.truetype("arialbd.ttf", 13)
    font_body = ImageFont.truetype("arial.ttf", 12)
    font_badge = ImageFont.truetype("arialbd.ttf", 11)
    font_stat = ImageFont.truetype("arialbd.ttf", 18)
except Exception:
    font_hero = ImageFont.load_default()
    font_h2 = font_hero
    font_h3 = font_hero
    font_body = font_hero
    font_badge = font_hero
    font_stat = font_hero

# Top bar
draw.rounded_rectangle([30, 20, 1570, 90], radius=12, fill="#111827", outline="#00E5FF", width=2)
draw.text((60, 35), "VIRTUAL APPLIANCE BASELINE CONFIGURATION & POWER ACCOUNTING", fill="#FFFFFF", font=font_hero)
draw.text((60, 64), "P_aggregate (284.0 W) = 140.0 W + 75.0 W + 45.0 W + 12.0 W + 12.0 W Residual Floor", fill="#00E5FF", font=font_h3)

draw.rounded_rectangle([1245, 38, 1545, 68], radius=6, fill="#064E3B", outline="#10B981", width=1)
draw.text((1260, 46), "100.0% CONSERVATION INVARIANT", fill="#D1FAE5", font=font_badge)

# Proportional bar container
draw.rounded_rectangle([30, 105, 1570, 165], radius=10, fill="#1E293B", outline="#334155", width=1)
draw.text((50, 116), "AGGREGATE HOUSEHOLD POWER DISTRIBUTION (284.0 W):", fill="#94A3B8", font=font_badge)

# Segments
draw.rounded_rectangle([50, 137, 789, 155], radius=4, fill="#EF4444")
draw.text((360, 140), "Water Heater 140W (49.3%)", fill="#FFFFFF", font=font_badge)

draw.rectangle([791, 137, 1186, 155], fill="#3B82F6")
draw.text((940, 140), "Water Pump 75W (26.4%)", fill="#FFFFFF", font=font_badge)

draw.rectangle([1188, 137, 1424, 155], fill="#10B981")
draw.text((1265, 140), "Fan 45W (15.8%)", fill="#FFFFFF", font=font_badge)

draw.rectangle([1426, 137, 1488, 155], fill="#F59E0B")
draw.text((1440, 140), "12W", fill="#000000", font=font_badge)

draw.rounded_rectangle([1490, 137, 1550, 155], radius=4, fill="#A855F7")
draw.text((1505, 140), "Floor", fill="#FFFFFF", font=font_badge)

# Table Header
draw.rounded_rectangle([30, 180, 1570, 222], radius=8, fill="#1E293B", outline="#334155", width=1)
draw.text((60, 195), "APPLIANCE / LOAD NAME", fill="#94A3B8", font=font_badge)
draw.text((380, 195), "ACTIVE POWER (W)", fill="#94A3B8", font=font_badge)
draw.text((580, 195), "POWER FACTOR (PF)", fill="#94A3B8", font=font_badge)
draw.text((810, 195), "NOMINAL SHARE (%)", fill="#94A3B8", font=font_badge)
draw.text((1040, 195), "ELECTRICAL SIGNATURE & PHYSICS", fill="#94A3B8", font=font_badge)
draw.text((1400, 195), "DETECTION ENVELOPE", fill="#94A3B8", font=font_badge)

# Rows
rows = [
    ("Water Heater", "Heating Element (water_heater_01)", "140.0 W", "0.99 (Unity)", "49.3%", "#EF4444", "Pure Resistive Nichrome", "No inrush spike; instant flat step transition", 230),
    ("Water Pump", "Induction Motor (water_pump_01)", "75.0 W", "0.78 Lagging", "26.4%", "#3B82F6", "Inductive Motor Inrush", "Lagging PF transition envelope with starting spike", 310),
    ("Ceiling Fan", "Rotary Motor (ceiling_fan_01)", "45.0 W", "0.91 Lagging", "15.8%", "#10B981", "Rotary Inductive Load", "Moderate inductive phase shift with stable plateau", 390),
    ("LED Bulb", "Solid-State Lighting (led_bulb_01)", "12.0 W", "0.95 Leading", "4.2%", "#F59E0B", "SMPS Driver Rectifier", "Capacitive filter leading PF; scaled via N=10 CT turn", 470),
    ("Residual Floor", "Strictly Distinct from 12.0W LED", "12.0 W", "1.00 Nominal", "4.2%", "#A855F7", "Parasitic Ambient Standby", "Smoke detectors, Wi-Fi router, microwave clock", 550)
]

for name, sub, power, pf, share, color, sig, desc, y in rows:
    draw.rounded_rectangle([30, y, 1570, y + 70], radius=10, fill="#131B2E", outline=color, width=1)
    
    draw.text((60, y + 16), name, fill="#FFFFFF", font=font_h2)
    draw.text((60, y + 42), sub, fill="#94A3B8", font=font_body)

    draw.rounded_rectangle([360, y + 16, 485, y + 54], radius=6, fill="#0F172A", outline=color, width=1)
    draw.text((385, y + 25), power, fill=color, font=font_stat)

    draw.rounded_rectangle([560, y + 16, 705, y + 54], radius=6, fill="#1E293B", outline="#64748B", width=1)
    draw.text((580, y + 27), pf, fill="#F8FAFC", font=font_h3)

    draw.text((800, y + 26), share, fill=color, font=font_stat)

    draw.text((1040, y + 16), sig, fill="#E2E8F0", font=font_h3)
    draw.text((1040, y + 42), desc, fill="#94A3B8", font=font_body)

    badge_bg = "#3B0764" if "Residual" in name else "#064E3B"
    badge_bd = "#A855F7" if "Residual" in name else "#10B981"
    badge_tx = "RESIDUAL BASELINE" if "Residual" in name else "PRODUCTION RULE"
    draw.rounded_rectangle([1380, y + 20, 1530, y + 50], radius=6, fill=badge_bg, outline=badge_bd, width=1)
    draw.text((1395, y + 28), badge_tx, fill=badge_bd, font=font_badge)

# Summary Total Footer
draw.rounded_rectangle([30, 635, 1570, 720], radius=12, fill="#0F2840", outline="#00E5FF", width=2)
draw.text((60, 650), "TOTAL HOUSEHOLD AGGREGATE", fill="#FFFFFF", font=font_h2)
draw.text((60, 678), "P_aggregate = Sum(P_attributed 272W) + P_residual (12W)", fill="#00E5FF", font=font_body)

draw.rounded_rectangle([360, 650, 485, 702], radius=8, fill="#0A2239", outline="#00E5FF", width=2)
draw.text((385, 665), "284.0 W", fill="#00E5FF", font=font_stat)

draw.rounded_rectangle([560, 650, 705, 702], radius=8, fill="#0A2239", outline="#00E5FF", width=2)
draw.text((585, 667), "0.96 Net PF", fill="#00E5FF", font=font_stat)

draw.rounded_rectangle([790, 650, 915, 702], radius=8, fill="#0A2239", outline="#00E5FF", width=2)
draw.text((820, 667), "100.0%", fill="#00E5FF", font=font_stat)

draw.rounded_rectangle([1040, 650, 1540, 702], radius=8, fill="#064E3B", outline="#10B981", width=2)
draw.text((1060, 667), "✓ ZERO POWER LEAKAGE • EXACT ARITHMETIC RECONCILIATION", fill="#E6FFFA", font=font_h3)

# Notes
draw.text((60, 750), "• Note: The continuous 12.0 W residual floor is an ambient parasitic baseline assumption and is mathematically distinct from the 12.0 W LED bulb load.", fill="#64748B", font=font_body)
draw.text((60, 775), "• Dynamic Behavior: When all 4 virtual appliances are toggled OFF in the simulator, active power drops to exactly 12.0 W (100% unattributed residual).", fill="#64748B", font=font_body)

img.save(png_path, "PNG", optimize=True)
print(f"High-res PNG generated: {png_path} ({os.path.getsize(png_path)} bytes)")
