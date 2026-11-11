import sys
sys.path.insert(0, '.')
import diagram

SVG = diagram.build()
SVGCSS = open('svgcss.css').read()

# --------------------------------------------------------------- icons (24x24, currentColor)
ICONS = {
 'pico': '<rect x="3" y="7" width="18" height="10" rx="1.5"/><rect x="1" y="10" width="3" height="4" rx=".5"/><rect x="10" y="9.5" width="5" height="5" rx=".6" fill="currentColor"/><path d="M5 7V5M8 7V5M11 7V5M14 7V5M17 7V5M20 7V5M5 19v-2M8 19v-2M11 19v-2M14 19v-2M17 19v-2M20 19v-2"/>',
 'resistor': '<path d="M1 12h4M19 12h4"/><rect x="5" y="9" width="14" height="6" rx="3"/><path d="M9 9v6M12 9v6M16 9v6"/>',
 'screw': '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="12" r="3"/><circle cx="16" cy="12" r="3"/><path d="M6.5 13.5l3-3M14.5 13.5l3-3"/>',
 'header': '<rect x="3" y="12" width="18" height="6" rx="1"/><path d="M7 12V5M12 12V5M17 12V5"/>',
 'circular': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="9" r=".9" fill="currentColor"/><circle cx="9.5" cy="13" r=".9" fill="currentColor"/><circle cx="14.5" cy="13" r=".9" fill="currentColor"/>',
 'gland': '<path d="M12 2.5l8.2 4.75v9.5L12 21.5l-8.2-4.75v-9.5z"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
 'tube': '<path d="M9 2v8M15 2v8"/><rect x="5" y="10" width="14" height="5" rx="1"/><path d="M7 15v3h10v-3"/><path d="M12 4v15" stroke-dasharray="1.5 1.5"/>',
 'xt60': '<rect x="4" y="6" width="16" height="12" rx="2"/><path d="M12 6v12"/><path d="M7 4v2M17 4v2"/>',
 'xt60w': '<rect x="4" y="6" width="16" height="12" rx="2"/><rect x="2" y="4" width="20" height="16" rx="3.5" stroke-dasharray="2 1.6"/><path d="M12 6v12"/>',
 'fuse': '<path d="M1 12h4M19 12h4"/><rect x="5" y="8" width="14" height="8" rx="4"/><path d="M9 10.5h6v3H9z" fill="currentColor"/>',
 'switch': '<path d="M2 16h5M17 16h5"/><circle cx="7" cy="16" r="1.4"/><circle cx="17" cy="16" r="1.4"/><path d="M8 15l8-7"/>',
 'splice': '<path d="M2 8h7M2 16h7M9 8c4 0 4 4 6 4M9 16c4 0 4-4 6-4M15 12h7"/><rect x="11" y="9" width="6" height="6" rx="2" fill="currentColor" opacity=".35"/>',
 'usb': '<rect x="4" y="9" width="11" height="6" rx="1"/><path d="M15 12h6M6.5 12h6"/><path d="M18 10l3 2-3 2"/>',
 'cap': '<path d="M12 2v7M12 15v7"/><path d="M6 9h12"/><path d="M6 15c3-2 9-2 12 0"/><path d="M15 5h3M16.5 3.5v3"/>',
 'buck': '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="12" cy="12" r="4"/><path d="M4 9h3M17 15h3"/>',
 'esc': '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M7 10h6M7 14h3"/><path d="M16 9l-2 3h3l-2 3"/>',
 'servo': '<rect x="2" y="8" width="16" height="10" rx="1.5"/><circle cx="13" cy="13" r="2.5"/><path d="M13 13l6-8"/><path d="M1 13h1"/>',
 'thruster': '<rect x="2" y="8" width="13" height="8" rx="4"/><path d="M15 12h2M17 8l4 4-4 4z"/>',
 'motor': '<rect x="3" y="7" width="14" height="10" rx="2"/><path d="M17 12h4M7 7v10M11 7v10"/>',
 'battery': '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 10v4"/><path d="M6 12h4M8 10v4M13 12h3"/>',
 'leak': '<path d="M12 3c3 4.5 6 7.5 6 11a6 6 0 01-12 0c0-3.5 3-6.5 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 002.5 2.5"/>',
 'board': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M5 8h14M5 16h14" opacity=".6"/><circle cx="7" cy="12" r=".9" fill="currentColor"/><circle cx="12" cy="12" r=".9" fill="currentColor"/><circle cx="17" cy="12" r=".9" fill="currentColor"/>',
 'pi': '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M5 8h10"/><rect x="15" y="11" width="5" height="5" rx=".5"/>',
}
sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>'
    for k, v in ICONS.items()) + '</svg>'
def ic(name):
    return f'<svg class="ic" aria-hidden="true"><use href="#i-{name}"/></svg>'

C = diagram.C
def chip(col, light=False):
    return f'<span class="sw" style="background:{col}"></span>'

legend = [
    (C['VBAT'], '12 V battery (VBAT)'), (C['GND'], 'Ground'), (C['V75'], '7.5 V servo rail'),
    (C['V33'], '3.3 V (leak sensors)'), (C['SERVO'], 'Servo PWM M4–M7'), (C['THR'], 'Thruster PWM'),
    (C['SIGG'], 'TD1.2 signal ground (white)'), (C['DRV'], 'Wheel ESC PWM'), (C['LEAK'], 'Leak sense'),
    (C['SPARE'], 'Spare PWM (pump)'), (C['USB'], 'USB cable (5 V + data)'), (C['MOT'], 'Motor leads'),
]
legend_html = ''.join(f'<li>{chip(c)}<span>{t}</span></li>' for c, t in legend)

def rows(items):
    return ''.join(f'<tr><td class="icc">{ic(i)}</td><td><b>{a}</b><span class="sub">{b}</span></td><td>{c}</td></tr>' for i, a, b, c in items)

board_a = [
 ('pico', 'A1 · Raspberry Pi Pico', 'in two 20-pin female headers', 'Power and data from the Pi 4 over USB. VSYS, RUN and UART pins unused.'),
 ('resistor', 'R1–R8 · 220 Ω, ¼ W', 'one per PWM output', 'In series on GP12–GP19. Protects the Pico if a wet connector shorts.'),
 ('header', 'J2 · 3-pin header, 2.54 mm', 'main leak sensor', '3V3 · GND · GP26 (ADC0). Sensor sits at the lowest point of the box.'),
 ('screw', 'J3 · 12-position screw terminal', '3.5 mm pitch is fine', 'Board side of harness H1. Wires from here to P1 solder cups: 22–24 AWG.'),
]
board_b = [
 ('screw', 'J4 · 12-position screw terminal', 'H1 from P4', 'Same pin order as J3.'),
 ('header', 'J5–J8 · 3-pin headers, 2.54 mm', 'servo plugs M4–M7', 'SIG · +7.5 V · GND. Servo leads re-crimped inside the box after the gland.'),
 ('header', 'J9 · 2-pin header', 'TD1.2 ESC signal lead', 'Yellow → THR PWM (GP16), white → GND. No power pin: the ESC has no BEC.'),
 ('screw', 'J10 · 3-position screw terminal', 'wheel ESC signal cable', 'DRV L (GP17) · DRV R (GP18) · GND, out through gland R2.'),
 ('header', 'J11 · 3-pin header', 'rear leak sensor', '3V3 · GND · GP27 (ADC1), fed through H1 pins 9–10.'),
 ('header', 'J13 · 2-pin header', 'spare', 'GP19 PWM + GND, reserved for the ballast pump.'),
 ('screw', 'J12 · 2-position screw terminal, 5.08 mm', '7.5 V in from buck', 'Pick one rated 10 A or more. 16 AWG from the buck.'),
 ('cap', 'C1 · 1000 µF 16 V low-ESR', 'across the 7.5 V rail', 'Absorbs servo current spikes. Mount next to J5–J8.'),
 ('board', 'Rails · 18 AWG tinned bus wire', 'soldered along the strips', 'Breadboard copper alone is too thin for servo stall current.'),
]
rear_off = [
 ('buck', 'U1 · 12 V → 7.5 V buck', 'off-board, rear drybox', 'Rate it 5 A continuous minimum; 8–10 A gives headroom for servo stalls.'),
 ('esc', 'U2 · TD1.2 ESC', 'off-board, rear drybox', 'Power straight off the XT60 Y-pigtail (14 AWG), never the breadboard.'),
 ('xt60', 'J14 / J15 · XT60 pair + Y-pigtail', 'dry side', 'Battery cable end ↔ pigtail to U2 and U1. Plain XT60 is fine inside the box.'),
]

conn = [
 ('xt60w', 'J16/J17 · Amass XT60W pair', 'Wet · battery disconnect', 'Everything (≤30 A, fused)', '30 A continuous', 'May not mate with a plain XT60: re-terminate the battery lead or use a short adapter.'),
 ('fuse', 'F1 · ATC blade fuse, 30 A', 'Wet · + line at battery', 'Everything', 'Waterproof inline holder rated ≥30 A, 12 AWG leads', 'Sized to the 12 AWG battery wiring.'),
 ('switch', 'SW1 · Kill switch', 'Wet / splash · − line', 'Everything', '≥30 A DC at 12 V, sealed', 'Seal the terminals: water can bridge an open low-side switch.'),
 ('splice', 'S1 · Y-splice', 'Wet', '12 AWG in, 14 AWG out ×2, 12 AWG to rear', 'Solder + adhesive-lined heat-shrink', 'No connector here on purpose.'),
 ('gland', 'R2 · Multi-hole cable gland', 'Rear drybox wall', '7 cables: battery, thruster, 4 servo leads, wheel signals', 'IP68 nylon M25/M32 with a multi-hole seal sized to each cable', 'Round flat servo leads with adhesive heat-shrink first.'),
 ('xt60', 'J14/J15 · XT60', 'Dry · rear drybox', 'Thruster + buck: up to ~13 A + ~6 A', '30 A continuous', '14 AWG to the ESC, 16 AWG to the buck.'),
 ('circular', 'P1 / P4 · IP68 12-pin circular', 'Main (A2) and rear (R1) walls', 'Signals, 3V3, GND: under 50 mA per pin', 'M12 A-coded 12-pin: 1.5 A per contact, 30 V, IP68', 'Panel receptacle on each box, plug on each end of H1.'),
 ('screw', 'J3 / J4 / J10 · Screw terminals', 'On boards', 'Signals only', '3.5 mm pitch (~6–8 A typical)', 'Leaves the boards removable without desoldering.'),
 ('screw', 'J12 · Screw terminal', 'Board B', '7.5 V servo rail: 1–2 A typical, ~10 A stall peaks', '5.08 mm pitch, ≥10 A', ''),
 ('header', 'J5–J8 · 2.54 mm headers', 'Board B', 'One servo each: 0.1–0.35 A running; stall 2–7.4 A in bursts', '~3 A per pin typical', 'Same JR/Futaba plugs the servos ship with. Avoid holding a servo in stall.'),
 ('header', 'J2 / J9 / J11 / J13 · headers', 'Boards', 'Signal level only', '~3 A per pin typical', ''),
 ('tube', 'A1 · Air-tube bulkhead', 'Main drybox wall', 'USB cable passes through inside the tube', 'Hose-barb bulkhead with O-ring', 'Not an electrical connector. The tube also vents the box to the buoy.'),
 ('usb', 'W1 · USB-A → micro-B cable', 'Buoy → Pico, inside air tube', 'Pico: under 0.1 A at 5 V', 'USB 2.0, keep under 5 m', 'The Pi 4 shares 1.2 A across all its USB ports.'),
]
conn_html = ''.join(
    f'<tr><td class="icc">{ic(i)}</td><td><b>{a}</b><span class="sub">{w}</span></td><td>{carries}</td><td class="rate">{rate}</td><td class="note">{note}</td></tr>'
    for i, a, w, carries, rate, note in conn)

budget = [
 ('thruster', 'TD1.2 thruster (with its ESC)', '12 V', '8 A nominal', '13 A', 'Hobbywater lists 5–13 A for the TD1.2 + ESC set at 12 V.'),
 ('motor', 'Wheel motors ×2 (550 brushed)', '12 V', '5–10 A each (estimate)', '30 A+ each at stall', 'Not on the listing. Wheels and thruster rarely run hard together.'),
 ('servo', 'Hitec DB777WP', '7.5 V', '0.35 A', '4.5 A stall', 'Hitec spec at 7.4 V.'),
 ('servo', 'Savox SW-1210SG', '7.5 V', '0.15 A', '7.4 A stall', 'Savox spec at 7.4 V. Hungriest servo on the rail.'),
 ('servo', 'Savox SW-1250MG', '7.5 V', '0.12 A', '2.0 A stall', 'Savox spec at 7.4 V.'),
 ('buck', 'Buck input (servo rail)', '12 V', '~1 A', '~6–7 A', 'About 0.7 × the 7.5 V current after conversion losses.'),
 ('pico', 'Pico + leak sensors', '5 V USB / 3.3 V', '<0.1 A', '—', 'Keep 3V3 load well under the Pico’s 300 mA.'),
]
budget_html = ''.join(
    f'<tr><td class="icc">{ic(i)}</td><td><b>{a}</b></td><td class="num">{v}</td><td class="num">{t}</td><td class="num">{p}</td><td class="note">{n}</td></tr>'
    for i, a, v, t, p, n in budget)

gauge = [
 ('Battery → XT60W → F1/SW1 → S1', '12 AWG silicone'),
 ('S1 → rear drybox (through R2) → J14', '12 AWG 2-core'),
 ('S1 → each wheel ESC', '14 AWG'),
 ('J15 Y-pigtail → TD1.2 ESC', '14 AWG'),
 ('J15 Y-pigtail → buck input', '16 AWG'),
 ('Buck output → J12', '16 AWG'),
 ('Board B 7.5 V and GND rails', '18 AWG tinned bus wire'),
 ('All signals, on-board jumpers, J3/J4 ↔ P1/P4', '22–24 AWG'),
 ('Harness H1 cordset', '24–26 AWG (0.14–0.25 mm²) is fine'),
]
gauge_html = ''.join(f'<tr><td>{a}</td><td class="rate">{b}</td></tr>' for a, b in gauge)

h1 = [
 (1, 'M4 servo PWM', 'GP12', C['SERVO']), (2, 'M5 servo PWM', 'GP13', C['SERVO']),
 (3, 'M6 servo PWM', 'GP14', C['SERVO']), (4, 'M7 servo PWM', 'GP15', C['SERVO']),
 (5, 'Thruster PWM', 'GP16', C['THR']), (6, 'Wheel ESC L PWM', 'GP17', C['DRV']),
 (7, 'Wheel ESC R PWM', 'GP18', C['DRV']), (8, 'Spare PWM (pump)', 'GP19', C['SPARE']),
 (9, 'Rear leak sense', 'GP27', C['LEAK']), (10, '3.3 V for rear leak sensor', '3V3', C['V33']),
 (11, 'Ground', 'GND', C['GND']), (12, 'Ground', 'GND', C['GND']),
]
h1_html = ''.join(f'<tr><td class="num">{p}</td><td>{chip(c)}{f}</td><td class="mono">{g}</td></tr>' for p, f, g, c in h1)

parts_html = lambda items: ''.join(
    f'<li>{ic(i)}<div><b>{a}</b> <span class="sub">{b}</span><p>{c}</p></div></li>' for i, a, b, c in items)

HTML = f'''<title>AA-TV Board Wiring</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
/* Layout: a single reading column with one full-bleed drawing sheet; reference tables below. */
:root {{
  --bg: #f4f7f8; --fg: #16232d; --muted: #52646f; --line: #d5dfe4; --card: #ffffff;
  --accent: #0b6e7f; --accent-soft: #d7eef1; --hl: #fff4d6; --ring: rgba(10,20,28,.45);
  --f-display: "Barlow Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0c151b; --fg: #e3ecf0; --muted: #9db0bb; --line: #24343e; --card: #121f27;
  --accent: #4cc2d3; --accent-soft: #143840; --hl: #3a3215; --ring: rgba(230,240,245,.5); color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #0c151b; --fg: #e3ecf0; --muted: #9db0bb; --line: #24343e; --card: #121f27;
  --accent: #4cc2d3; --accent-soft: #143840; --hl: #3a3215; --ring: rgba(230,240,245,.5); color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.55 var(--f-body); }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 56px; }}
header .eyebrow {{ font: 600 13px/1 var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }}
h1 {{ font: 700 clamp(34px, 5vw, 52px)/1.02 var(--f-display); letter-spacing: .01em; margin: 10px 0 10px; text-wrap: balance; }}
h2 {{ font: 700 28px/1.1 var(--f-display); letter-spacing: .02em; margin: 0 0 6px; text-wrap: balance; }}
h3 {{ font: 700 19px/1.2 var(--f-display); letter-spacing: .04em; text-transform: uppercase; margin: 0 0 10px; color: var(--accent); }}
.lede {{ max-width: 68ch; color: var(--muted); margin: 0; }}
.pens {{ display: flex; flex-wrap: wrap; gap: 8px 18px; margin: 16px 0 0; padding: 0; list-style: none; font-size: 13.5px; }}
.pens li {{ display: flex; gap: 8px; align-items: center; }}
.pens b {{ font: 600 12px var(--f-mono); background: var(--accent-soft); color: var(--fg); padding: 2px 7px; border-radius: 4px; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 16px; list-style: none; padding: 0; margin: 22px 0 12px; font-size: 13px; }}
.legend li {{ display: flex; align-items: center; gap: 7px; }}
.sw {{ display: inline-block; width: 26px; height: 8px; border-radius: 4px; box-shadow: 0 0 0 1px var(--ring); vertical-align: middle; margin-right: 7px; flex: none; }}
.legend .sw {{ margin-right: 0; }}
figure {{ margin-block: 0; margin-inline: calc((100% - min(1640px, 100vw - 48px)) / 2); }}
.sheet {{ overflow-x: auto; border-radius: 14px; border: 1px solid var(--line); background: #eef3f5;
  --panel: #eef3f5; --dry: #ffffff; --sea: #0b6e7f; --wave: #d3e5eb; --ink: #16232d; --muted: #4f6170; }}
.sheet .diagram {{ min-width: 1100px; }}
figcaption {{ font-size: 13px; color: var(--muted); margin-top: 8px; }}
section {{ margin-top: 48px; }}
.grid2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 20px; margin-top: 16px; align-items: start; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 18px 18px 8px; min-width: 0; }}
.parts {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }}
.parts li {{ display: grid; grid-template-columns: 30px 1fr; gap: 10px; align-items: start; padding-bottom: 12px; border-bottom: 1px dashed var(--line); }}
.parts li:last-child {{ border-bottom: 0; }}
.parts p {{ margin: 2px 0 0; color: var(--muted); font-size: 14px; }}
.ic {{ width: 26px; height: 26px; color: var(--accent); flex: none; }}
.sub {{ display: block; font-size: 12.5px; color: var(--muted); font-weight: 400; }}
.parts .sub {{ display: inline; }}
.tbl {{ overflow-x: auto; margin-top: 14px; border: 1px solid var(--line); border-radius: 12px; background: var(--card); }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
th {{ text-align: left; font: 600 12px var(--f-mono); letter-spacing: .05em; text-transform: uppercase; color: var(--muted); padding: 10px 12px; border-bottom: 1px solid var(--line); white-space: nowrap; }}
td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }}
tr:last-child td {{ border-bottom: 0; }}
td.icc {{ width: 34px; padding-right: 0; }}
td.rate {{ font-weight: 600; }}
td.note {{ color: var(--muted); font-size: 13.5px; }}
td.num, .mono {{ font-family: var(--f-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.wide table {{ min-width: 860px; }}
.mid table {{ min-width: 640px; }}
.rules {{ counter-reset: r; list-style: none; padding: 0; margin: 14px 0 0; display: grid; gap: 10px; max-width: 80ch; }}
.rules li {{ counter-increment: r; display: grid; grid-template-columns: 30px 1fr; gap: 8px; }}
.rules li::before {{ content: counter(r); font: 700 15px/1.5 var(--f-mono); color: var(--accent); }}
.callout {{ background: var(--hl); border-radius: 10px; padding: 12px 14px; margin-top: 14px; font-size: 14px; max-width: 80ch; }}
.src {{ font-size: 13px; color: var(--muted); margin-top: 48px; }}
.src a {{ color: var(--accent); }}
.src ul {{ padding-left: 18px; }}
{SVGCSS}
</style>
{sprite}
<div class="wrap">
<header>
  <div class="eyebrow">AA-TV · electrical · v6 · follows architecture v5</div>
  <h1>Board wiring: Board A, Board B and the wet zone</h1>
  <p class="lede">Two solderable breadboards replace the PCB. Board A holds the Pico in the main drybox. Board B handles the servos, thruster signal and the 7.5 V rail in the rear drybox. 12 V never touches either board. Every wire color in the drawing means one thing everywhere it appears.</p>
  <ul class="pens">
    <li><b>A1</b> air-tube bulkhead, USB cable inside</li>
    <li><b>A2</b> IP68 12-pin receptacle P1</li>
    <li><b>R1</b> IP68 12-pin receptacle P4</li>
    <li><b>R2</b> multi-hole cable gland, 7 cables</li>
  </ul>
</header>

<ul class="legend" aria-label="Wire color key">{legend_html}</ul>
<figure>
  <div class="sheet">{SVG}</div>
  <figcaption>Wire colors are functional. If your harness cordset comes with fixed colors, follow the pin numbers on J3/J4, not the color. Scroll sideways on a phone.</figcaption>
</figure>

<section>
  <h2>What goes on each board</h2>
  <div class="grid2">
    <div class="card"><h3>Board A · main drybox</h3><ul class="parts">{parts_html(board_a)}</ul></div>
    <div class="card"><h3>Board B · rear drybox</h3><ul class="parts">{parts_html(board_b)}</ul></div>
  </div>
  <div class="grid2">
    <div class="card"><h3>Rear drybox, off the board</h3><ul class="parts">{parts_html(rear_off)}</ul></div>
    <div class="card"><h3>Harness H1 pin map</h3>
      <div class="tbl" style="margin-top:0;border:0"><table><thead><tr><th>Pin</th><th>Function</th><th>Pico</th></tr></thead><tbody>{h1_html}</tbody></table></div>
    </div>
  </div>
</section>

<section>
  <h2>Connectors and current ratings</h2>
  <p class="lede">The rating column is what to buy. The load column is what actually flows through it in this build.</p>
  <div class="tbl wide"><table>
    <thead><tr><th></th><th>Connector</th><th>Load through it</th><th>Rating to buy</th><th>Notes</th></tr></thead>
    <tbody>{conn_html}</tbody></table></div>
</section>

<section>
  <h2>Current budget</h2>
  <p class="lede">Water mode (thruster + servos) runs roughly 10–20 A from the battery. Land mode (wheels + servos) runs roughly 15–25 A. The 30 A fuse covers either, but not every motor at full stall at once.</p>
  <div class="tbl wide"><table>
    <thead><tr><th></th><th>Load</th><th>Supply</th><th>Typical</th><th>Peak</th><th>Source / note</th></tr></thead>
    <tbody>{budget_html}</tbody></table></div>
  <div class="grid2">
    <div class="card"><h3>Wire gauge</h3>
      <div class="tbl mid" style="margin-top:0;border:0"><table><tbody>{gauge_html}</tbody></table></div></div>
    <div class="card"><h3>Build rules</h3>
      <ol class="rules">
        <li>No 12 V on either breadboard. VBAT runs battery → XT60 → Y-pigtail → ESC and buck.</li>
        <li>On Board B, solder 18 AWG bus wire along the 7.5 V and GND strips before adding headers.</li>
        <li>Keep one ground tie between the boards: H1 pins 11–12. Don’t add a second GND link.</li>
        <li>Cut and seal the red BEC wire on each wheel ESC’s signal lead. The Pico gets its 5 V from the Pi.</li>
        <li>Put adhesive-lined heat-shrink over each flat servo lead where it passes the gland seal.</li>
        <li>Mount each leak sensor at the lowest point of its box.</li>
        <li>Socket the Pico. With screw terminals on every off-board wire, both boards lift out with a screwdriver.</li>
      </ol></div>
  </div>
  <p class="callout"><b>Servo stall:</b> the SW-1210SG pulls 7.4 A when stalled, above a 2.54 mm header’s ~3 A rating. Short stalls are normal in RC use, but don’t let a control surface sit jammed against a hard stop.</p>
</section>

<div class="src"><b>Sources for ratings</b>
<ul>
<li><a href="https://hobbywater.com/products/underwater-thruster-1-2kg-12v" target="_blank" rel="noopener">Hobbywater: TD1.2 underwater thruster, 12 V</a></li>
<li><a href="https://hitecrcd.com/db777wp-32-bit-low-profile-waterproof-metal-case-servo" target="_blank" rel="noopener">Hitec: DB777WP specifications</a></li>
<li><a href="https://www.cmldistribution.co.uk/product/SAV-SW1210SG+/files/SAV-SW1210SGP%20Data%20Sheet.pdf" target="_blank" rel="noopener">Savox SW-1210SG+ data sheet</a> · <a href="https://www.cmldistribution.co.uk/product/SAV-SW1250MG+/files/SAV-SW1250MG+%20Data%20Sheet.pdf" target="_blank" rel="noopener">Savox SW-1250MG+ data sheet</a></li>
<li><a href="https://pro.maplin.co.uk/products/male-waterproof-xt60-gold-plated-connector-30a-xt60w-m-amass" target="_blank" rel="noopener">Maplin: Amass XT60W, 30 A</a></li>
<li><a href="https://www.maritex.eu/en/product/amphenol-ltw-m12a-12pffs-sh8001-circular-connectors" target="_blank" rel="noopener">Amphenol LTW M12 A-code 12-pin receptacle, 1.5 A, IP68</a></li>
</ul>
Screw-terminal and header ratings are typical values; check the part you buy.</div>
</div>
'''

if __name__ == '__main__':
    open(sys.argv[1], 'w').write(HTML)
