import os
from PIL import Image, ImageDraw, ImageFont

assets_dir = r"C:\Users\Kaviya\Downloads\Energy Mirror\docs\assets"
os.makedirs(assets_dir, exist_ok=True)
svg_path = os.path.join(assets_dir, "nilm_concept_diagram.svg")
png_path = os.path.join(assets_dir, "nilm_concept_diagram.png")

# ==========================================
# 1. VECTOR SVG GENERATION
# ==========================================
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 780" width="100%" height="100%" style="background-color: #0B0F19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Gradients -->
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
    <linearGradient id="cyanLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00E5FF"/>
      <stop offset="100%" stop-color="#38BDF8"/>
    </linearGradient>
    
    <!-- Shadows & Glows -->
    <filter id="boxShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- ========================================== -->
  <!-- 0. HEADER BANNER                           -->
  <!-- ========================================== -->
  <rect x="30" y="20" width="1540" height="60" rx="12" fill="#111827" stroke="#00E5FF" stroke-width="1.6" filter="url(#boxShadow)"/>
  <text x="60" y="55" fill="#FFFFFF" font-size="20" font-weight="800" letter-spacing="0.8">NON-INTRUSIVE LOAD MONITORING (NILM) DISAGGREGATION PRINCIPLE</text>
  <rect x="1230" y="35" width="315" height="28" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1.2"/>
  <text x="1387" y="53" fill="#34D399" font-size="11.5" font-weight="800" text-anchor="middle">ZERO SMART PLUGS REQUIRED</text>

  <!-- ========================================== -->
  <!-- 1. TOP NODE: SINGLE SERVICE PANEL SENSOR   -->
  <!-- ========================================== -->
  <g transform="translate(480, 105)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="640" height="135" rx="14" fill="url(#panelGrad)" stroke="#F59E0B" stroke-width="2"/>
    
    <!-- Header Tag -->
    <rect x="18" y="-12" width="280" height="24" rx="6" fill="#78350F" stroke="#F59E0B" stroke-width="1.2"/>
    <text x="158" y="4" fill="#FDE68A" font-size="11" font-weight="800" text-anchor="middle">SINGLE SERVICE PANEL SENSING POINT</text>
    
    <!-- Title & Specs -->
    <text x="30" y="42" fill="#FFFFFF" font-size="18" font-weight="800">Whole-Home Main Distribution Panel</text>
    <text x="30" y="66" fill="#FBBF24" font-size="13" font-weight="700">PZEM-004T v3.0 Metrology IC + Split-Core Current Transformer (CT)</text>
    
    <!-- Badges Row -->
    <g transform="translate(30, 85)">
      <rect x="0" y="0" width="130" height="32" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="65" y="21" fill="#F8FAFC" font-size="12" font-weight="700" text-anchor="middle">Aggregate: 284.0 W</text>

      <rect x="145" y="0" width="130" height="32" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="210" y="21" fill="#F8FAFC" font-size="12" font-weight="700" text-anchor="middle">Voltage: 230.2 V</text>

      <rect x="290" y="0" width="130" height="32" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="355" y="21" fill="#F8FAFC" font-size="12" font-weight="700" text-anchor="middle">Power Factor: 0.96</text>

      <rect x="435" y="0" width="145" height="32" rx="6" fill="#1E293B" stroke="#64748B" stroke-width="1"/>
      <text x="507" y="21" fill="#00E5FF" font-size="12" font-weight="700" text-anchor="middle">Sampling: 1 Hz Clock</text>
    </g>
  </g>

  <!-- Arrow 1: Panel -> Backend -->
  <g stroke="#00E5FF" stroke-width="2.5" fill="none">
    <path d="M 800 240 L 800 295"/>
    <polygon points="793,295 807,295 800,307" fill="#00E5FF" stroke="none"/>
  </g>
  <rect x="670" y="255" width="260" height="24" rx="6" fill="#0B0F19" stroke="#00E5FF" stroke-width="1"/>
  <text x="800" y="271" fill="#00E5FF" font-size="11" font-weight="700" text-anchor="middle">1 Hz Aggregate Active Power &amp; PF Stream</text>

  <!-- ========================================== -->
  <!-- 2. MIDDLE NODE: ENERGY MIRROR BACKEND      -->
  <!-- ========================================== -->
  <g transform="translate(420, 310)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="760" height="135" rx="14" fill="url(#engineGrad)" stroke="#00E5FF" stroke-width="2"/>
    
    <!-- Header Tag -->
    <rect x="20" y="-12" width="290" height="24" rx="6" fill="#0C4A6E" stroke="#00E5FF" stroke-width="1.2"/>
    <text x="165" y="4" fill="#E0F2FE" font-size="11" font-weight="800" text-anchor="middle">ENERGY MIRROR DISAGGREGATION ENGINE</text>

    <!-- Title & Specs -->
    <text x="30" y="42" fill="#FFFFFF" font-size="19" font-weight="800">FastAPI Core + 1 Hz Derivative Edge NILM Detector</text>
    <text x="30" y="66" fill="#38BDF8" font-size="13" font-weight="600">Extracts Discrete Step Transitions: |Delta P| &gt;= 5.0 W &amp; Delta PF Envelopes</text>
    
    <!-- Highlights Row -->
    <g transform="translate(30, 85)">
      <rect x="0" y="0" width="215" height="32" rx="6" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="107" y="21" fill="#E2E8F0" font-size="11.5" font-weight="700" text-anchor="middle">Dynamic Signature Matching</text>

      <rect x="230" y="0" width="235" height="32" rx="6" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="347" y="21" fill="#E2E8F0" font-size="11.5" font-weight="700" text-anchor="middle">Exact Conservation Accounting</text>

      <rect x="480" y="0" width="220" height="32" rx="6" fill="#0F172A" stroke="#0284C7" stroke-width="1"/>
      <text x="590" y="21" fill="#34D399" font-size="11.5" font-weight="700" text-anchor="middle">Deduplicated State Events</text>
    </g>
  </g>

  <!-- ========================================== -->
  <!-- 3. BUS CONNECTOR ARROWS                    -->
  <!-- ========================================== -->
  <!-- Main stem down -->
  <line x1="800" y1="445" x2="800" y2="495" stroke="#38BDF8" stroke-width="2.5"/>
  
  <!-- Horizontal distribution bus -->
  <line x1="160" y1="495" x2="1440" y2="495" stroke="#38BDF8" stroke-width="2.5"/>

  <!-- Vertical drop lines to 5 appliances -->
  <!-- 1. Heater -->
  <line x1="160" y1="495" x2="160" y2="535" stroke="#38BDF8" stroke-width="2.5"/>
  <polygon points="153,535 167,535 160,547" fill="#38BDF8" stroke="none"/>

  <!-- 2. Pump -->
  <line x1="480" y1="495" x2="480" y2="535" stroke="#38BDF8" stroke-width="2.5"/>
  <polygon points="473,535 487,535 480,547" fill="#38BDF8" stroke="none"/>

  <!-- 3. Fan -->
  <line x1="800" y1="495" x2="800" y2="535" stroke="#38BDF8" stroke-width="2.5"/>
  <polygon points="793,535 807,535 800,547" fill="#38BDF8" stroke="none"/>

  <!-- 4. LED Bulb -->
  <line x1="1120" y1="495" x2="1120" y2="535" stroke="#38BDF8" stroke-width="2.5"/>
  <polygon points="1113,535 1127,535 1120,547" fill="#38BDF8" stroke="none"/>

  <!-- 5. Residual Floor -->
  <line x1="1440" y1="495" x2="1440" y2="535" stroke="#38BDF8" stroke-width="2.5"/>
  <polygon points="1433,535 1447,535 1440,547" fill="#38BDF8" stroke="none"/>

  <!-- Center Callout Pill -->
  <g transform="translate(620, 482)">
    <rect x="0" y="0" width="360" height="26" rx="6" fill="#0B0F19" stroke="#00E5FF" stroke-width="1.4"/>
    <text x="180" y="18" fill="#00E5FF" font-size="11.5" font-weight="800" text-anchor="middle">... ALL EXTRACTED FROM ONE SENSING POINT!</text>
  </g>

  <!-- ========================================== -->
  <!-- 4. BOTTOM ROW: DISAGGREGATED APPLIANCES    -->
  <!-- ========================================== -->
  <!-- Appliance 1: Water Heater -->
  <g transform="translate(30, 550)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="280" height="205" rx="12" fill="url(#cardGrad)" stroke="#EF4444" stroke-width="1.6"/>
    <rect x="15" y="15" width="32" height="32" rx="6" fill="#450A0A" stroke="#EF4444" stroke-width="1"/>
    <text x="31" y="37" fill="#FCA5A5" font-size="16" font-weight="800" text-anchor="middle">♨</text>
    <text x="58" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Water Heater</text>

    <text x="20" y="75" fill="#EF4444" font-size="22" font-weight="800">140.0 W</text>
    <text x="135" y="75" fill="#94A3B8" font-size="13" font-weight="600">(49.3% Share)</text>

    <line x1="20" y1="92" x2="260" y2="92" stroke="#334155" stroke-width="1"/>
    <text x="20" y="115" fill="#CBD5E1" font-size="11.5">• Signature: Pure Resistive</text>
    <text x="20" y="137" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.99 (Unity)</text>
    <text x="20" y="159" fill="#CBD5E1" font-size="11.5">• Step Delta: +140 W / -140 W</text>
    <text x="20" y="181" fill="#10B981" font-size="11.5" font-weight="700">✓ Rule Envelope Matched</text>
  </g>

  <!-- Appliance 2: Water Pump -->
  <g transform="translate(345, 550)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="280" height="205" rx="12" fill="url(#cardGrad)" stroke="#3B82F6" stroke-width="1.6"/>
    <rect x="15" y="15" width="32" height="32" rx="6" fill="#172554" stroke="#3B82F6" stroke-width="1"/>
    <text x="31" y="37" fill="#93C5FD" font-size="16" font-weight="800" text-anchor="middle">💧</text>
    <text x="58" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Water Pump</text>

    <text x="20" y="75" fill="#3B82F6" font-size="22" font-weight="800">75.0 W</text>
    <text x="120" y="75" fill="#94A3B8" font-size="13" font-weight="600">(26.4% Share)</text>

    <line x1="20" y1="92" x2="260" y2="92" stroke="#334155" stroke-width="1"/>
    <text x="20" y="115" fill="#CBD5E1" font-size="11.5">• Signature: Inductive Motor</text>
    <text x="20" y="137" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.78 Lagging</text>
    <text x="20" y="159" fill="#CBD5E1" font-size="11.5">• Step Delta: +75 W (Inrush)</text>
    <text x="20" y="181" fill="#10B981" font-size="11.5" font-weight="700">✓ Rule Envelope Matched</text>
  </g>

  <!-- Appliance 3: Ceiling Fan -->
  <g transform="translate(660, 550)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="280" height="205" rx="12" fill="url(#cardGrad)" stroke="#10B981" stroke-width="1.6"/>
    <rect x="15" y="15" width="32" height="32" rx="6" fill="#064E3B" stroke="#10B981" stroke-width="1"/>
    <text x="31" y="37" fill="#A7F3D0" font-size="16" font-weight="800" text-anchor="middle">🌀</text>
    <text x="58" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Ceiling Fan</text>

    <text x="20" y="75" fill="#10B981" font-size="22" font-weight="800">45.0 W</text>
    <text x="120" y="75" fill="#94A3B8" font-size="13" font-weight="600">(15.8% Share)</text>

    <line x1="20" y1="92" x2="260" y2="92" stroke="#334155" stroke-width="1"/>
    <text x="20" y="115" fill="#CBD5E1" font-size="11.5">• Signature: Rotary Inductive</text>
    <text x="20" y="137" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.91 Lagging</text>
    <text x="20" y="159" fill="#CBD5E1" font-size="11.5">• Step Delta: +45 W / -45 W</text>
    <text x="20" y="181" fill="#10B981" font-size="11.5" font-weight="700">✓ Rule Envelope Matched</text>
  </g>

  <!-- Appliance 4: LED Bulb -->
  <g transform="translate(975, 550)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="280" height="205" rx="12" fill="url(#cardGrad)" stroke="#F59E0B" stroke-width="1.6"/>
    <rect x="15" y="15" width="32" height="32" rx="6" fill="#78350F" stroke="#F59E0B" stroke-width="1"/>
    <text x="31" y="37" fill="#FDE68A" font-size="16" font-weight="800" text-anchor="middle">💡</text>
    <text x="58" y="36" fill="#FFFFFF" font-size="16" font-weight="800">LED Bulb</text>

    <text x="20" y="75" fill="#F59E0B" font-size="22" font-weight="800">12.0 W</text>
    <text x="120" y="75" fill="#94A3B8" font-size="13" font-weight="600">(4.2% Share)</text>

    <line x1="20" y1="92" x2="260" y2="92" stroke="#334155" stroke-width="1"/>
    <text x="20" y="115" fill="#CBD5E1" font-size="11.5">• Signature: SMPS Driver</text>
    <text x="20" y="137" fill="#CBD5E1" font-size="11.5">• Power Factor: 0.95 Leading</text>
    <text x="20" y="159" fill="#CBD5E1" font-size="11.5">• Scaled via N=10 CT turn</text>
    <text x="20" y="181" fill="#10B981" font-size="11.5" font-weight="700">✓ Rule Envelope Matched</text>
  </g>

  <!-- Appliance 5: Unattributed Residual Floor -->
  <g transform="translate(1290, 550)" filter="url(#boxShadow)">
    <rect x="0" y="0" width="280" height="205" rx="12" fill="url(#cardGrad)" stroke="#A855F7" stroke-width="1.6"/>
    <rect x="15" y="15" width="32" height="32" rx="6" fill="#4C1D95" stroke="#A855F7" stroke-width="1"/>
    <text x="31" y="37" fill="#DDD6FE" font-size="16" font-weight="800" text-anchor="middle">⚡</text>
    <text x="58" y="36" fill="#FFFFFF" font-size="16" font-weight="800">Residual Floor</text>

    <text x="20" y="75" fill="#A855F7" font-size="22" font-weight="800">12.0 W</text>
    <text x="120" y="75" fill="#94A3B8" font-size="13" font-weight="600">(4.2% Floor)</text>

    <line x1="20" y1="92" x2="260" y2="92" stroke="#334155" stroke-width="1"/>
    <text x="20" y="115" fill="#CBD5E1" font-size="11.5">• Parasitic Standby Baseline</text>
    <text x="20" y="137" fill="#CBD5E1" font-size="11.5">• Smoke detectors, router, clock</text>
    <text x="20" y="159" fill="#CBD5E1" font-size="11.5">• Distinct from 12W LED bulb</text>
    <text x="20" y="181" fill="#A855F7" font-size="11.5" font-weight="700">⚖ Conservation Invariant</text>
  </g>

</svg>
"""

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"NILM Concept SVG generated: {svg_path} ({os.path.getsize(svg_path)} bytes)")

# ==========================================
# 2. HIGH-RES RASTER PNG VIA PILLOW
# ==========================================
W, H = 1600, 780
img = Image.new("RGB", (W, H), color="#0B0F19")
draw = ImageDraw.Draw(img)

try:
    font_hero = ImageFont.truetype("arialbd.ttf", 22)
    font_h2 = ImageFont.truetype("arialbd.ttf", 17)
    font_h3 = ImageFont.truetype("arialbd.ttf", 14)
    font_body = ImageFont.truetype("arial.ttf", 12)
    font_badge = ImageFont.truetype("arialbd.ttf", 11)
    font_stat = ImageFont.truetype("arialbd.ttf", 20)
except Exception:
    font_hero = ImageFont.load_default()
    font_h2 = font_hero
    font_h3 = font_hero
    font_body = font_hero
    font_badge = font_hero
    font_stat = font_hero

# Top bar
draw.rounded_rectangle([30, 20, 1570, 80], radius=12, fill="#111827", outline="#00E5FF", width=2)
draw.text((60, 36), "NON-INTRUSIVE LOAD MONITORING (NILM) DISAGGREGATION PRINCIPLE", fill="#FFFFFF", font=font_hero)
draw.rounded_rectangle([1230, 35, 1545, 65], radius=6, fill="#064E3B", outline="#10B981", width=1)
draw.text((1255, 43), "ZERO SMART PLUGS REQUIRED", fill="#34D399", font=font_badge)

# Top Node (Service panel)
draw.rounded_rectangle([480, 105, 1120, 240], radius=14, fill="#151D2F", outline="#F59E0B", width=2)
draw.rounded_rectangle([498, 93, 778, 117], radius=6, fill="#78350F", outline="#F59E0B", width=1)
draw.text((515, 98), "SINGLE SERVICE PANEL SENSING POINT", fill="#FDE68A", font=font_badge)
draw.text((510, 130), "Whole-Home Main Distribution Panel", fill="#FFFFFF", font=font_h2)
draw.text((510, 158), "PZEM-004T v3.0 Metrology IC + Split-Core Current Transformer (CT)", fill="#FBBF24", font=font_h3)

stats = [
    ("Aggregate: 284.0 W", 510),
    ("Voltage: 230.2 V", 655),
    ("Power Factor: 0.96", 800),
    ("Sampling: 1 Hz Clock", 945)
]
for text, x in stats:
    draw.rounded_rectangle([x, 185, x + 135, 220], radius=6, fill="#1E293B", outline="#64748B", width=1)
    draw.text((x + 10, 195), text, fill="#F8FAFC", font=font_body)

# Connector to Middle Node
draw.line([(800, 240), (800, 310)], fill="#00E5FF", width=3)
draw.rounded_rectangle([670, 258, 930, 286], radius=6, fill="#0B0F19", outline="#00E5FF", width=1)
draw.text((685, 265), "1 Hz Aggregate Power & PF Stream", fill="#00E5FF", font=font_badge)

# Middle Node (Energy Mirror Engine)
draw.rounded_rectangle([420, 310, 1180, 445], radius=14, fill="#102036", outline="#00E5FF", width=2)
draw.rounded_rectangle([440, 298, 730, 322], radius=6, fill="#0C4A6E", outline="#00E5FF", width=1)
draw.text((455, 303), "ENERGY MIRROR DISAGGREGATION ENGINE", fill="#E0F2FE", font=font_badge)
draw.text((450, 335), "FastAPI Core + 1 Hz Derivative Edge NILM Detector", fill="#FFFFFF", font=font_h2)
draw.text((450, 363), "Extracts Discrete Step Transitions: |Delta P| >= 5.0 W & Delta PF Envelopes", fill="#38BDF8", font=font_h3)

engine_badges = [
    ("Dynamic Signature Matching", 450),
    ("Exact Conservation Accounting", 685),
    ("Deduplicated State Events", 935)
]
for text, x in engine_badges:
    draw.rounded_rectangle([x, 392, x + 215, 427], radius=6, fill="#0F172A", outline="#0284C7", width=1)
    draw.text((x + 14, 402), text, fill="#E2E8F0", font=font_body)

# Bus connections
draw.line([(800, 445), (800, 495)], fill="#38BDF8", width=3)
draw.line([(170, 495), (1430, 495)], fill="#38BDF8", width=3)

# Center pill
draw.rounded_rectangle([620, 482, 980, 508], radius=6, fill="#0B0F19", outline="#00E5FF", width=1)
draw.text((635, 488), "... ALL EXTRACTED FROM ONE SENSING POINT!", fill="#00E5FF", font=font_badge)

# Appliance cards data
appliances = [
    ("Water Heater", "140.0 W", "(49.3% Share)", "#EF4444", 30, [
        "• Signature: Pure Resistive",
        "• Power Factor: 0.99 (Unity)",
        "• Step Delta: +140 W / -140 W",
        "✓ Rule Envelope Matched"
    ]),
    ("Water Pump", "75.0 W", "(26.4% Share)", "#3B82F6", 345, [
        "• Signature: Inductive Motor",
        "• Power Factor: 0.78 Lagging",
        "• Step Delta: +75 W (Inrush)",
        "✓ Rule Envelope Matched"
    ]),
    ("Ceiling Fan", "45.0 W", "(15.8% Share)", "#10B981", 660, [
        "• Signature: Rotary Inductive",
        "• Power Factor: 0.91 Lagging",
        "• Step Delta: +45 W / -45 W",
        "✓ Rule Envelope Matched"
    ]),
    ("LED Bulb", "12.0 W", "(4.2% Share)", "#F59E0B", 975, [
        "• Signature: SMPS Driver",
        "• Power Factor: 0.95 Leading",
        "• Scaled via N=10 CT turn",
        "✓ Rule Envelope Matched"
    ]),
    ("Residual Floor", "12.0 W", "(4.2% Floor)", "#A855F7", 1290, [
        "• Parasitic Standby Baseline",
        "• Smoke detectors, router, clock",
        "• Distinct from 12W LED bulb",
        "⚖ Conservation Invariant"
    ])
]

for name, power, share, color, x, lines in appliances:
    # Vertical connector
    draw.line([(x + 140, 495), (x + 140, 550)], fill="#38BDF8", width=3)
    
    # Card box
    draw.rounded_rectangle([x, 550, x + 280, 755], radius=12, fill="#131B2E", outline=color, width=2)
    draw.text((x + 20, 565), name, fill="#FFFFFF", font=font_h2)
    draw.text((x + 20, 595), power, fill=color, font=font_stat)
    draw.text((x + 130, 600), share, fill="#94A3B8", font=font_body)
    draw.line([(x + 20, 630), (x + 260, 630)], fill="#334155", width=1)
    
    curr_y = 645
    for line in lines:
        c = "#34D399" if "✓" in line else ("#A855F7" if "⚖" in line else "#CBD5E1")
        draw.text((x + 20, curr_y), line, fill=c, font=font_body)
        curr_y += 24

img.save(png_path, "PNG", optimize=True)
print(f"High-res PNG generated: {png_path} ({os.path.getsize(png_path)} bytes)")
