import sys, re
sys.path.insert(0, '.')
import page2 as p2
import diagram7

C = diagram7.C
ic, chip = p2.ic, p2.chip
SVG = diagram7.build()

def pinrows(rows):
    return ''.join(f'<tr><td class="num">{p}</td><td>{chip(c) if c else "<span class=sw-empty></span>"}{f}</td><td class="mono">{g}</td></tr>' for p, f, g, c in rows)

LOOP = '#adb5bd'
legend = [(C['VBAT'], '12 V (VBAT)'), (C['GND'], 'Ground'), (C['V75'], '7.4 V servo rail'), (C['V33'], '3.3 V'),
          (C['SERVO'], 'Servo PWM'), (C['THR'], 'Thruster PWM'), (C['SIGG'], 'TD1.2 signal ground'),
          (C['PUMP'], 'Pump PWM'), (C['LEAK'], 'Leak sense'), (C['I2C'], 'I2C (SCL / SDA)'),
          (C['BAL'], 'Balance taps'), (C['MOT'], 'Motor leads'), (C['USB'], 'USB cable')]
legend_html = ''.join(f'<li>{chip(c)}<span>{t}</span></li>' for c, t in legend)


def card(icon, title, sub, metas, rows=None):
    t = ''.join(f'<p class="dmeta">{m}</p>' for m in metas)
    tbl = ''
    if rows:
        tbl = (f'<div class="tbl" style="margin-top:8px;border:0"><table><thead><tr><th>Pin</th><th>Function</th><th>Net</th></tr></thead>'
               f'<tbody>{pinrows(rows)}</tbody></table></div>')
    return (f'<div class="card dcard"><div class="dhead">{ic(icon)}<div><b>{title}</b>'
            f'<span class="sub">{sub}</span></div></div>{t}{tbl}</div>')


cards = ''.join([
    card('gland', 'G1 · M16 gland', 'USB cable from the buoy', [
        'USB-A to micro-B, about 3 m, Pi 4 → Pico.',
        'The vinyl air tube ends on the gland and is just a sheath. A vented box would need a barbed bulkhead fitting instead.']),
    card('gland', 'G2 · M16 gland', 'TD1.2 thruster phase cable', [
        'The TD1.2 ESC (U2) sits inside the box, so only the 3 phase wires leave it and no 12 V goes out.',
        'Slide the gland nut and seal onto the factory cable before re-terminating it at the ESC (a dry splice inside the box if it has to be cut).']),
    card('gland', 'G3 · M16 gland', 'Pump motor pair → D2', [
        'One round jacketed 14/2 cable from the pump ESC (U3) to D2. Two loose wires won’t seal in a gland.']),
    card('potted', 'G4 · M16 gland, potted', 'All four servo leads', [
        'Four flat factory leads can’t seal in one gland. Pull the rubber insert, pass the leads, and fill the gland body with epoxy.',
        'Measure each lead to G4 first. Backup: one MGYOO 20 AWG 3-pin plug per servo.']),
    card('dt', 'D2 · DTP 4-pin', 'Pump cable ↔ pump drybox', [
        'Box side gets the DTP06 plug (sockets). Pump ~10 A (Seaflo candidate).'], [
        (1, 'Pump motor +', 'PUMP_M+', C['MOT']), (2, 'Pump motor −', 'PUMP_M−', C['MOT']),
        (3, 'Dummy loop (to pin 4)', 'sealed, unpowered', LOOP), (4, 'Dummy loop (to pin 3)', 'sealed, unpowered', LOOP)]),
    card('battery', 'J2 · EC5 · J3 · balance', 'Battery disconnects, inside the box', [
        'J2: the pack’s own EC5 plug mates with an EC5 pigtail into F1. Unplug it to take the battery out or charge it.',
        'J3: the JST-XH balance plug feeds the cell monitor.'], [
        (1, 'Balance GND (battery −)', 'GND', C['GND']), (2, 'Cell 1 + → R7 47k', 'BAL_C1', C['BAL']),
        (3, 'Cell 2 + → R9 200k', 'BAL_C2', C['BAL']), (4, 'Pack + → R11 330k', 'BAT_RAW', C['BAL'])]),
])

buy = [
 ('<b>DTP 4Pin-4 Set</b> <span class="pick">enough for v9</span>', '$21.99', '4', '1', '3'),
 ('DTP 4Pin-12 Set (the v8.3 pick)', '$29.99', '12', '1', '11'),
 ('DTP 2Pin-4 Set (D2 as 2-pin, no dummy loop; differs from the schematic)', '$16.99', '4', '1', '3'),
]
buy_html = ''.join(f'<tr><td>{a}</td><td class="num">{b}</td><td class="num">{c}</td><td class="num">{d}</td><td class="num">{e}</td></tr>' for a, b, c, d, e in buy)

newparts = [
 ('ADS1115 breakout (U4)', 'Reads the three balance taps over I2C. Most breakouts carry the pull-ups and a 100 nF cap.'),
 ('JST-XH 4-pin socket or balance extension (J3)', 'Lets the pack’s balance plug reach the board.'),
 ('EC5 female pigtail, 12–14 AWG (J2)', 'Mates with the pack’s EC5 plug, inside the box.'),
 ('Resistors: 47k, 200k, 330k, 3 × 100k, 2 × 10k', 'Divider top and bottom resistors, plus the R13 / R14 pull-downs. The 6 × 220 Ω stay.'),
 ('3 × 100 nF', 'One across each divider bottom resistor (C2–C4).'),
 ('Round jacketed 14/2 marine cable', 'Pump ESC → G3 → D2 → pump drybox. Sized to the gland clamp range.'),
 ('Potting epoxy for G4', 'Fills the servo gland body.'),
 ('Standard ATC fuse holder', 'F1 is inside the box now, so it no longer needs to be waterproof.'),
]
new_html = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in newparts)

wire_rows = [
 ('14 AWG tinned marine wire', 'Battery → EC5 → F1 → SW1 → bus bar, every bus-bar tap, buck in and out, TB7, servo + / − jumpers, the board rails, DTP contacts and the dummy loop.',
  'Peaks stay at or under the 25 A DTP contact rating; F1 is 30 A.'),
 ('Round 14/2 jacketed cable', 'The pump run through G3 to D2 and on to the pump drybox.', 'A gland seals on one round jacket, not on separate wires.'),
 ('20 AWG hookup wire', 'On-board signal jumpers (Pico → resistors → TB2–TB5), I2C to U4, leak sensor, both ESC signal leads.', 'Never carries motor or rail current.'),
 ('Factory leads', 'Servo leads (through G4), thruster phase cable (through G2), battery balance lead (to J3).', 'Used as supplied.'),
]
wire_html = ''.join(f'<tr><td class="icc">{ic("wire")}</td><td><b>{a}</b></td><td>{b}</td><td class="note">{c}</td></tr>' for a, b, c in wire_rows)

runs = [
 ('G3 → D2 → pump drybox', '2', 'round 14/2 cable'),
 ('G2 → TD1.2 thruster', '3', 'factory phase cable'),
 ('G4 → servos M4–M7', '4 × 3', 'factory leads, potted in G4'),
 ('G1 → buoy', 'USB', 'inside the air tube'),
]
runs_html = ''.join(f'<tr><td>{a}</td><td class="num">{b}</td><td class="note">{c}</td></tr>' for a, b, c in runs)

splices = [
 ('Dry', 'Thruster phase wires at the ESC, only if the factory cable has to be cut to pass G2'),
 ('Dry', 'Pump ESC motor leads → 14/2 cable, inside the box'),
 ('Backup', 'Only if a servo lead won’t reach G4: servo lead ↔ MGYOO pigtail, per servo'),
]
splice_html = ''.join(f'<tr><td><span class="badge {a.lower()}">{a}</span></td><td>{b}</td></tr>' for a, b in splices)

budget = [('thruster', 'TD1.2 thruster + ESC', '8 A', '13 A'), ('pump', 'Ballast pump (Seaflo candidate)', '5–10 A', '10 A'),
          ('buck', 'Servo rail via buck (12 V side)', '~0.7 A', '~9 A, all four stalled'), ('pico', 'Pico, ADS1115, leak sensor (USB 5 V)', '<0.1 A', '—')]
btxt = ''.join(f'<tr><td class="icc">{ic(i)}</td><td><b>{a}</b></td><td class="num">{t}</td><td class="num">{p}</td></tr>' for i, a, t, p in budget)

board = [
 ('pico', 'A1 · Raspberry Pi Pico', 'socketed', 'USB from the Pi (through G1) gives power and data.'),
 ('resistor', 'R1–R6 · 220 Ω', 'series on each PWM line', 'R1–R4 GP12–15 servos, R5 GP16 thruster, R6 GP19 pump.'),
 ('resistor', 'R13 / R14 · 10 kΩ', 'pull-downs', 'THR and PUMP to GND, so the ESCs see a clean low while the Pico boots.'),
 ('screw', 'TA2 · 3-pos', 'leak sensor', '3V3 · GND · GP26. Sensor at the box’s low point.'),
 ('screw', 'TB2 / TB3 · 6-pos', 'servo leads (via G4)', 'Per servo: sig · + · GND. TB2 = M4, M5 rudder; TB3 = M6, M7 elevator.'),
 ('screw', 'TB4 / TB5 · 2-pos', 'ESC signals', 'TB4: GP16 PWM · GND to U2. TB5: GP19 PWM · GND to U3.'),
 ('screw', 'TB7 · 4-pos', '7.4 V in from U1', 'Pins 1–2 +7.4 V, 3–4 GND, two 14 AWG per pole.'),
 ('cap', 'C1 · 1000 µF 16 V', 'across the 7.4 V rail', 'Absorbs servo spikes.'),
 ('board', 'U4 · ADS1115 + J3', 'battery cell monitor', 'Dividers 47k/100k, 200k/100k, 330k/100k: ~2.9 V at a full pack. I2C0 on GP20 SDA, GP21 SCL, address 0x48.'),
]
power = [
 ('battery', 'BT1 · 3S LiPo', 'inside the box', 'EC5 lead to J2, balance lead to J3. Check the fit: a 169 mm pack in a 173 mm floor.'),
 ('fuse', 'F1 · 30 A ATC', 'standard holder', 'Right after J2.'),
 ('switch', 'SW1 · kill switch', 'HIGH side, ≥30 A DC', 'Must be on the + side: J3 ties battery − to board GND. Lid off to reach it; a reed switch + relay can make it external.'),
 ('busbar', 'BB1 / BB2 · OONO 2×6', '30 A total, one row per pole', 'Taps: buck, pump ESC, thruster ESC. One spare per row.'),
 ('buck', 'U1 · 12 → 7.4 V buck', 'adjustable, ≥15 A', 'Set to 7.4 V before connecting servos (Hitec DB777WP max 7.4 V).'),
 ('esc', 'U2 · TD1.2 ESC', 'inside the box', 'No BEC. Yellow = PWM, white = signal GND.'),
 ('esc', 'U3 · Pump ESC', 'brushed, reversible', 'Rated above pump stall. BEC wire cut.'),
]
parts = p2.parts

CSS = re.search(r'<style>(.*?)</style>', p2.HTML, re.S).group(1) + '''
.pick { font: 600 11px var(--f-mono); background: var(--accent); color: var(--bg); padding: 2px 6px; border-radius: 4px; margin-left: 6px; text-transform: uppercase; letter-spacing: .04em; }
.badge { font: 600 11px var(--f-mono); padding: 2px 7px; border-radius: 4px; }
.badge.wet { background: #d0ebff; color: #0b4a75; }
.badge.dry { background: #fff3bf; color: #6b4e00; }
.badge.backup { background: #d3f9d8; color: #1b5e20; }
'''

HTML = f'''<title>AA-TV Board Wiring v9</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
{p2.sprite}
<div class="wrap">
<header>
  <div class="eyebrow">AA-TV · electrical · v9 · single IP67 box · 4 × M16 glands · battery inside</div>
  <h1>Board wiring</h1>
  <p class="lede">One IP67 box holds the battery, fuse, kill switch, bus bar, buck, both ESCs and a single solder-board. Everything outside it is flooded ballast space. Four M16 glands carry the USB cable, the thruster phases, the pump motor pair and the four servo leads. The only Deutsch connector left is D2 on the pump cable.</p>
</header>

<ul class="legend" aria-label="Wire color key">{legend_html}</ul>
<ul class="gkey">
  <li><span class="gk" style="height:5px;background:#e03131"></span>14 AWG marine (thick)</li>
  <li><span class="gk" style="height:2.6px;background:#1c7ed6"></span>20 AWG hookup (thin, on the board)</li>
  <li><svg width="34" height="14" aria-hidden="true"><rect x="1" y="2" width="32" height="10" rx="5" fill="#3a4650"/><line x1="4" y1="7" x2="30" y2="7" stroke="#e03131" stroke-width="2" stroke-dasharray="6 4"/></svg>14 AWG round cable</li>
  <li><svg class="ic" style="color:#e8590c" aria-hidden="true"><use href="#i-dt"/></svg>Deutsch DTP 4-pin pair</li>
  <li><svg width="20" height="14" aria-hidden="true"><rect x="1" y="2" width="18" height="10" rx="2" fill="#495057"/></svg>M16 cable gland</li>
  <li><svg width="20" height="14" aria-hidden="true"><rect x="1" y="2" width="18" height="10" rx="2" fill="#495057"/><rect x="5" y="4" width="10" height="6" rx="1" fill="#ffd8a8" stroke="#8a5300"/></svg>Gland filled with epoxy</li>
</ul>

<figure>
  <div class="sheet">{SVG}</div>
  <figcaption>Scroll sideways on a phone. KiCad schematic: <code>kicad_files/AATV_v9/AATV_v9.kicad_sch</code>.</figcaption>
</figure>
<div class="stats">
  <div><b>4</b><span>M16 glands (all used)</span></div>
  <div><b>1</b><span>Deutsch DTP 4-pin (D2)</span></div>
  <div><b>30 A</b><span>main fuse F1</span></div>
  <div><b>1</b><span>solder-board</span></div>
</div>

<section>
  <h2>Box penetrations and connectors</h2>
  <p class="lede">Each gland seals one round cable. The source side of D2 (the box) gets the DTP06 plug with socket contacts, so no live pins are exposed when unplugged.</p>
  <div class="grid3">{cards}</div>
</section>

<section>
  <h2>What to buy</h2>
  <p class="lede">v9 needs only one Deutsch connector. If the 12-set isn’t ordered yet, the 4Pin-4 Set covers D2 with three spare. Prices are from the listing on Nov 6, 2026.</p>
  <div class="tbl mid"><table><thead><tr><th>DTP option</th><th>Price</th><th>Sets</th><th>Used</th><th>Spare</th></tr></thead><tbody>{buy_html}</tbody></table></div>
  <h3 style="margin-top:22px">New parts for v9</h3>
  <div class="tbl wide"><table><thead><tr><th>Part</th><th>Why</th></tr></thead><tbody>{new_html}</tbody></table></div>
  <p class="callout"><b>No longer needed:</b> the rear drybox, the H1 harness (12 × 14 AWG), five DTP connectors (D1, D3–D6), the 12-way terminals TA1 / TB1, the rear leak sensor and the three potted holes A2 / R2 / R3.</p>
</section>

<section>
  <h2>Wire</h2>
  <div class="tbl wide"><table><thead><tr><th></th><th>Gauge</th><th>Used for</th><th>Why it’s enough</th></tr></thead><tbody>{wire_html}</tbody></table></div>
  <div class="grid2">
    <div class="card"><h3>Runs outside the box</h3>
      <div class="tbl" style="margin-top:0;border:0"><table><thead><tr><th>Run</th><th>Conductors</th><th>Note</th></tr></thead><tbody>{runs_html}</tbody></table></div></div>
    <div class="card"><h3>Splices</h3>
      <div class="tbl" style="margin-top:0;border:0"><table><tbody>{splice_html}</tbody></table></div></div>
  </div>
</section>

<section>
  <h2>Current budget</h2>
  <p class="lede">Typical draw is about 12 A. A realistic peak (thruster at full, pump running, servos moving) is about 25 A, so the 30 A fuse fits. Every servo stalled at the same moment as everything else would be about 32 A and would blow it. With D1 gone, the tightest limit inside the box is the OONO module’s 30 A total.</p>
  <div class="tbl mid"><table><thead><tr><th></th><th>Load</th><th>Typical</th><th>Peak</th></tr></thead><tbody>{btxt}</tbody></table></div>
</section>

<section>
  <h2>What goes where</h2>
  <div class="grid2">
    <div class="card"><h3>The solder-board</h3><ul class="parts">{parts(board)}</ul></div>
    <div class="card"><h3>Power, off the board</h3><ul class="parts">{parts(power)}</ul></div>
  </div>
</section>

<section>
  <h2>Build rules</h2>
  <ol class="rules">
    <li>12 V stays on the bus bar and power leads. The breadboard never carries it; the balance taps reach it only through 47 kΩ or more.</li>
    <li>Kill switch SW1 goes on the + side, between F1 and the bus bar.</li>
    <li>Charge with the lid off: unplug the EC5 (J2) and the balance plug (J3), then charge the pack directly. Unplug J3 for storage.</li>
    <li>One round cable per gland. G4 is the exception: insert out, gland body filled with epoxy.</li>
    <li>Cut and seal the red BEC wire on every ESC signal lead.</li>
    <li>Set U1 to 7.4 V before connecting the servos.</li>
    <li>Bench-test 3.3 V PWM on all four servos and both ESCs before potting G4.</li>
    <li>IP67 covers 1 m for 30 minutes. Vacuum-test the closed box before every dive.</li>
    <li>All screw terminals are Molence 5.08 mm blocks (10 A, 22–12 AWG). They fit the breadboard grid and take 14 AWG.</li>
  </ol>
</section>

<div class="src"><b>Sources</b>
<ul>
<li><a href="https://www.amazon.com/dp/B0CPSRKBJ4" target="_blank" rel="noopener">Amazon: Deutusacc DTP-0412 connector kit (size 12, 14–12 AWG, 25 A, IP67)</a></li>
<li><a href="https://www.amazon.com/dp/B0DX77XPKK" target="_blank" rel="noopener">Amazon: Otdorpatio IP67 enclosure with M16 cable glands</a></li>
<li><a href="https://datasheet.sic-components.com/product-DTP04-4P-L012.datasheet.pdf" target="_blank" rel="noopener">TE DTP04-4P datasheet: 3.4–4.32 mm seal range, 25 A</a></li>
<li><a href="https://hobbywater.com/products/underwater-thruster-1-2kg-12v" target="_blank" rel="noopener">Hobbywater: TD1.2 thruster + ESC, 5–13 A at 12 V</a></li>
<li><a href="https://hitecrcd.com/db777wp-32-bit-low-profile-waterproof-metal-case-servo" target="_blank" rel="noopener">Hitec DB777WP (6.0–7.4 V)</a> · <a href="https://savox-servo.com/en/product/SW-1250MG/savox-servo-sw-1250mg-digital-high-voltage-coreless-motor-waterproof-metal-gear" target="_blank" rel="noopener">Savox SW-1250MG</a></li>
<li><a href="https://www.amazon.com/dp/B0CH8RHCNY" target="_blank" rel="noopener">Amazon: Molence 5.08 mm screw terminal blocks</a> · <a href="https://www.amazon.com/dp/B09D3BV22M" target="_blank" rel="noopener">OONO 2×6 30 A distribution module</a></li>
<li><a href="https://www.westmarine.com/seaflo-marine-seaflo-12v-reversible-8.0-gpm-self-priming-impeller-bilge-ballast-pump-24039984.html" target="_blank" rel="noopener">West Marine: Seaflo 12 V reversible 8 GPM pump (10 A)</a></li>
</ul></div>
</div>
'''

if __name__ == '__main__':
    open(sys.argv[1], 'w').write(HTML)
