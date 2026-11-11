import sys, re
sys.path.insert(0, '.')
import page2 as p2
import diagram5 as diagram3

C = diagram3.C
ic, chip = p2.ic, p2.chip
SVG = diagram3.build()

def pinrows(rows):
    return ''.join(f'<tr><td class="num">{p}</td><td>{chip(c) if c else "<span class=sw-empty></span>"}{f}</td><td class="mono">{g}</td></tr>' for p, f, g, c in rows)

LOOP = '#adb5bd'
D = [
 ('D1', 'Battery ↔ trunk to rear drybox', 'Battery side gets the DTP06 plug (sockets)', '30 A fuse, two contacts per pole (2 × 25 A)', [
   (1, '+12 V after fuse F1', 'VBAT', C['VBAT']), (2, '+12 V after fuse F1', 'VBAT', C['VBAT']),
   (3, 'GND after kill switch SW1', 'GND', C['GND']), (4, 'GND after kill switch SW1', 'GND', C['GND'])]),
 ('D2', 'Rear drybox ↔ ballast pump', 'Rear-box side gets the plug', 'Pump ~10 A (Seaflo candidate)', [
   (1, 'Pump motor +', 'PUMP_M+', C['MOT']), (2, 'Pump motor −', 'PUMP_M−', C['MOT']),
   (3, 'Dummy loop (to pin 4)', 'sealed, unpowered', LOOP), (4, 'Dummy loop (to pin 3)', 'sealed, unpowered', LOOP)]),
 ('D3', 'Rear drybox ↔ TD1.2 thruster ESC (wet)', 'Rear-box side gets the plug', 'Thruster 8 A nominal, 13 A max on pin 1', [
   (1, 'ESC +12 V (red)', 'VBAT', C['VBAT']), (2, 'ESC GND (black)', 'GND', C['GND']),
   (3, 'Thruster PWM (yellow)', 'GP16', C['THR']), (4, 'Signal GND (white)', 'GND', C['SIGG'])]),
 ('D4', 'H1 pins 1–4: main ↔ rear drybox', 'Main-box side gets the plug', 'Signals only', [
   (1, 'H1 1 · M4 servo PWM', 'GP12', C['SERVO']), (2, 'H1 2 · M5 servo PWM', 'GP13', C['SERVO']),
   (3, 'H1 3 · M6 servo PWM', 'GP14', C['SERVO']), (4, 'H1 4 · M7 servo PWM', 'GP15', C['SERVO'])]),
 ('D5', 'H1 pins 5–8', 'Main-box side gets the plug', 'Signals only; 2 spare conductors', [
   (1, 'H1 5 · Thruster PWM', 'GP16', C['THR']), (2, 'H1 6 · spare (wired, unused)', '—', C['SPARE']),
   (3, 'H1 7 · spare (wired, unused)', '—', C['SPARE']), (4, 'H1 8 · Pump PWM', 'GP19', C['PUMP'])]),
 ('D6', 'H1 pins 9–12', 'Main-box side gets the plug', 'Leak sensor + references', [
   (1, 'H1 9 · Rear leak sense', 'GP27', C['LEAK']), (2, 'H1 10 · 3.3 V for rear leak sensor', '3V3', C['V33']),
   (3, 'H1 11 · GND', 'GND', C['GND']), (4, 'H1 12 · GND', 'GND', C['GND'])]),
]
def dcard(d):
    i, where, side, load, pm = d
    return (f'<div class="card dcard"><div class="dhead">{ic("dt")}<div><b>{i} · DTP 4-pin</b>'
            f'<span class="sub">{where}</span></div></div>'
            f'<p class="dmeta">{side}<br>{load}</p>'
            f'<div class="tbl" style="margin-top:8px;border:0"><table><thead><tr><th>Pin</th><th>Function</th><th>Net / Pico</th></tr></thead>'
            f'<tbody>{pinrows(pm)}</tbody></table></div></div>')
cards = ''.join(dcard(d) for d in D) + (
    f'<div class="card dcard"><div class="dhead">{ic("servo")}<div><b>Servos · no connector</b>'
    f'<span class="sub">Rudder M4, M5 · elevator M6, M7</span></div></div>'
    f'<p class="dmeta">2× Hitec DB777WP (4.5 A stall), 2× Savox SW-1250MG (2.4 A stall), both IP67.</p>'
    f'<p class="dmeta">Factory leads potted straight into the rear drybox at R2 and landed on TB2 / TB3.</p>'
    f'<p class="dmeta"><b>Backup</b>, only if a lead can’t reach the box: one MGYOO 20 AWG 3-pin waterproof connector per servo, '
    f'spliced inline in the wet zone (signal · + · GND). The 3pin-10Pack ($13.99) covers all four with 6 spare.</p></div>')

buy = [
 ('<b>DTP 4Pin-12 Set</b> <span class="pick">buy this</span>', '$29.99', '12', '6', '6', '$2.50'),
 ('DTP 4Pin-4 Set × 2', '$43.98', '8', '6', '2', '$5.50'),
 ('MGYOO 20 AWG 3pin-10Pack (servo backup, only if needed)', '$13.99', '10', '4', '6', '$1.40'),
]
buy_html = ''.join(f'<tr><td>{a}</td><td class="num">{b}</td><td class="num">{c}</td><td class="num">{d}</td><td class="num">{e}</td><td class="num">{f}</td></tr>' for a, b, c, d, e, f in buy)

wire_rows = [
 ('14 AWG tinned marine wire', 'Everything that goes through a DTP contact or leaves a drybox, except the servo leads: battery harness, trunk (2 per pole), H1 (12 conductors), thruster and pump cables, D2 dummy loop. Inside the boxes: bus-bar taps, buck in and out, servo + / − jumpers, Board B rails.',
  'DTP size-12 contacts take 12–14 AWG. Every load is under the 25 A contact rating.'),
 ('20 AWG hookup wire', 'On-board signal jumpers (Pico → resistors → TA1, TB1 → TB2–TB6), leak-sensor leads inside the boxes, pump ESC signal lead.',
  'Never goes through a connector or a drybox wall.'),
 ('Servo factory leads (20–22 AWG)', 'Run uncut from each servo into R2 and onto TB2 / TB3.', 'Potted, so no contact has to fit them.'),
]
wire_html = ''.join(f'<tr><td class="icc">{ic("wire")}</td><td><b>{a}</b></td><td>{b}</td><td class="note">{c}</td></tr>' for a, b, c in wire_rows)

runs = [
 ('Battery → D1 → rear drybox (R3)', '4', 'red ×2, black ×2'),
 ('H1: main drybox (A2) → D4/D5/D6 → rear drybox (R2)', '12', 'colors or numbered heat-shrink bands'),
 ('Rear drybox (R2 + R3) → D3 thruster ESC', '2 power + 2 signal', ''),
 ('Rear drybox (R3) → D2 pump', '2', ''),
 ('Dummy loop, D2 (both halves)', '2 short pieces', 'about 3 cm each'),
]
runs_html = ''.join(f'<tr><td>{a}</td><td class="num">{b}</td><td class="note">{c}</td></tr>' for a, b, c in runs)

splices = [
 ('Wet', 'TD1.2 ESC power and signal leads → 14 AWG pigtails for D3'),
 ('Wet', 'Battery + after F1 → two wires (D1 pins 1–2); battery − after SW1 → two wires (pins 3–4). Sealed Y-splice in adhesive heat shrink, or two ring terminals on a switch stud'),
 ('Wet', 'Battery lead → fuse holder and kill switch: one in-line join each (none if the switch has screw studs for ring terminals)'),
 ('Backup', 'Only if a servo lead won’t reach: servo lead ↔ MGYOO pigtail and pigtail ↔ extension, per servo'),
 ('Dry', 'Pump ESC motor leads → 14 AWG, only if they’re too short to reach D2'),
]
splice_html = ''.join(f'<tr><td><span class="badge {a.lower()}">{a}</span></td><td>{b}</td></tr>' for a, b in splices)

budget = [('thruster', 'TD1.2 thruster + ESC', '8 A', '13 A'), ('pump', 'Ballast pump (Seaflo candidate)', '5–10 A', '10 A'),
          ('buck', 'Servo rail via buck (12 V side)', '~0.7 A', '~9 A, all four stalled'), ('pico', 'Pico + leak sensors (USB 5 V)', '<0.1 A', '—')]
btxt = ''.join(f'<tr><td class="icc">{ic(i)}</td><td><b>{a}</b></td><td class="num">{t}</td><td class="num">{p}</td></tr>' for i, a, t, p in budget)

boardA = [
 ('pico', 'A1 · Raspberry Pi Pico', 'socketed', 'USB from the Pi gives power and data.'),
 ('resistor', 'R1–R6 · 220 Ω', 'series on each PWM line', 'R1–R4 GP12–15 servos, R5 GP16 thruster, R6 GP19 pump.'),
 ('screw', 'TA1 · 12-pos screw terminal, 5.08 mm', 'H1 out (14 AWG)', 'Cable potted at A2. Pins 6–7 spare.'),
 ('screw', 'TA2 · 3-pos screw terminal', 'main leak sensor', '3V3 · GND · GP26.'),
]
boardB = [
 ('screw', 'TB1 · 12-pos', 'H1 in', 'Same pin order as TA1.'),
 ('screw', 'TB2 · 6-pos', 'rudder servo leads (potted)', 'M4: sig · + · GND, then M5: sig · + · GND.'),
 ('screw', 'TB3 · 6-pos', 'elevator servo leads (potted)', 'M6: sig · + · GND, then M7: sig · + · GND.'),
 ('screw', 'TB4 · 2-pos', 'thruster ESC signal → D3', 'PWM · GND.'),
 ('screw', 'TB5 · 2-pos', 'pump ESC signal', 'GP19 PWM · GND to U3.'),
 ('screw', 'TB6 · 3-pos', 'rear leak sensor', '3V3 · GND · GP27.'),
 ('screw', 'TB7 · 4-pos', '7.5 V in from buck', 'Pins 1–2 +7.5 V, 3–4 GND. Two 14 AWG per pole from U1 so no 10 A terminal sees a full servo stall.'),
 ('cap', 'C1 · 1000 µF 16 V', 'across 7.5 V rail', 'Absorbs servo spikes.'),
 ('board', 'Rails · 14 AWG', 'soldered along the strips', 'Servo + / − jumpers also 14 AWG.'),
]
rearOff = [
 ('busbar', 'BB1 / BB2 · OONO 2×6 bus bar', '30 A, one row per pole', 'Trunk in on two positions per row; buck, pump ESC and D3 thruster feed out; 1 spare each. Check the two rows aren’t bridged.'),
 ('buck', 'U1 · 12 → 7.5 V buck', '20 A (BOM)', 'Set to 7.5 V. Hitec’s DB777WP page says 6.0–7.4 V but the package says 8.4 V; if in doubt, set 7.2 V.'),
 ('esc', 'U3 · Pump ESC', 'brushed, with reverse', 'Dry, so it needn’t be waterproof. BEC wire cut.'),
]
parts = p2.parts

CSS = re.search(r'<style>(.*?)</style>', p2.HTML, re.S).group(1) + '''
.pick { font: 600 11px var(--f-mono); background: var(--accent); color: var(--bg); padding: 2px 6px; border-radius: 4px; margin-left: 6px; text-transform: uppercase; letter-spacing: .04em; }
.badge { font: 600 11px var(--f-mono); padding: 2px 7px; border-radius: 4px; }
.badge.wet { background: #d0ebff; color: #0b4a75; }
.badge.dry { background: #fff3bf; color: #6b4e00; }
.badge.backup { background: #d3f9d8; color: #1b5e20; }
'''

HTML = f'''<title>AA-TV Board Wiring</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
{p2.sprite}
<div class="wrap">
<header>
  <div class="eyebrow">AA-TV · electrical · v8.2 · no wheels · Deutsch DTP · servos potted · 30 A fuse</div>
  <h1>Board wiring</h1>
  <p class="lede">No wheels. Six Deutsch DTP 4-pin connectors in the wet zone, each taking the 14 AWG marine wire the team can buy. Servo leads are potted straight into the rear drybox with no connector. Inside the boxes everything lands on 5.08 mm screw terminals or bus bars.</p>
</header>

<ul class="legend" aria-label="Wire color key">{p2.legend_html.replace('<li><span class="sw" style="background:#2f9e44"></span><span>Wheel ESC PWM</span></li>', '')}</ul>
<ul class="gkey">
  <li><span class="gk" style="height:5px;background:#e03131"></span>14 AWG marine (thick)</li>
  <li><span class="gk" style="height:2.6px;background:#1c7ed6"></span>20 AWG hookup (thin, on boards only)</li>
  <li><svg width="34" height="14" aria-hidden="true"><rect x="1" y="2" width="32" height="10" rx="5" fill="#3a4650"/><line x1="4" y1="7" x2="30" y2="7" stroke="#e03131" stroke-width="2" stroke-dasharray="6 4"/></svg>14 AWG cable run</li>
  <li><svg class="ic" style="color:#e8590c" aria-hidden="true"><use href="#i-dt"/></svg>Deutsch DTP 4-pin pair</li>
  <li><svg width="34" height="14" aria-hidden="true"><rect x="1" y="2" width="32" height="10" rx="3" fill="#f59f00" stroke="#8a5300"/></svg>Epoxy-potted hole</li>
  <li><svg width="14" height="14" aria-hidden="true"><rect x="3" y="1" width="8" height="12" rx="3" fill="#1c1c1c"/></svg>Solder splice + adhesive heat-shrink</li>
</ul>

<figure>
  <div class="sheet">{SVG}</div>
  <figcaption>Scroll sideways on a phone. KiCad schematic: <code>kicad_files/AATV/AATV.kicad_sch</code>.</figcaption>
</figure>
<div class="stats">
  <div><b>6</b><span>DTP 4-pin connectors used</span></div>
  <div><b>6</b><span>spare connectors in the 12-set</span></div>
  <div><b>$29.99</b><span>all connectors (4Pin-12 Set)</span></div>
  <div><b>30 A</b><span>main fuse F1</span></div>
</div>

<section>
  <h2>What to buy</h2>
  <p class="lede">Buy the DTP 4Pin-12 Set. Even with six left over, it costs less than two 4Pin-4 Sets. Hold off on the MGYOO 3-pin pack unless a servo lead turns out too short to reach the rear drybox.</p>
  <div class="tbl mid"><table><thead><tr><th>Option</th><th>Price</th><th>Sets</th><th>Used</th><th>Spare</th><th>Per set</th></tr></thead><tbody>{buy_html}</tbody></table></div>
  <p class="callout"><b>Before ordering:</b> the 4-pin sets on this listing appear to include, per set, one plug, one receptacle, both wedgelocks, 4 pin and 4 socket contacts. 6 connectors (including D2’s dummy loop) use 24 of each, leaving 24 spare contacts per kind. Confirm the 4Pin-12 page says 12 sets. The contacts are stamped (open-barrel), so they crimp with an open-barrel crimper for 12–14 AWG, not the solid-contact Deutsch tool. Prices are from the listing on Nov 4, 2026.</p>
</section>

<section>
  <h2>Deutsch connector schedule</h2>
  <p class="lede">The source side (battery or drybox) always gets the DTP06 plug with socket contacts, so no live pins are exposed when unplugged.</p>
  <p class="callout"><b>Dummy loop (D2 only):</b> cut about 3 cm of 14 AWG, crimp a contact on each end, and push the ends into cavities 3 and 4 so the seals close around wire. Do this on both halves: pin contacts in the receptacle, socket contacts in the plug. The loop carries nothing. Keep it on 3–4 only and never let it touch a powered pin.</p>
  <div class="grid3">{cards}</div>
</section>

<section>
  <h2>Wire</h2>
  <div class="tbl wide"><table><thead><tr><th></th><th>Gauge</th><th>Used for</th><th>Why it’s enough</th></tr></thead><tbody>{wire_html}</tbody></table></div>
  <div class="grid2">
    <div class="card"><h3>14 AWG runs outside the boxes</h3>
      <div class="tbl" style="margin-top:0;border:0"><table><thead><tr><th>Run</th><th>Conductors</th><th>Note</th></tr></thead><tbody>{runs_html}</tbody></table></div></div>
    <div class="card"><h3>Splices</h3>
      <div class="tbl" style="margin-top:0;border:0"><table><tbody>{splice_html}</tbody></table></div></div>
  </div>
  <p class="callout"><b>Jacketed marine cable:</b> strip the outer jacket back far enough that each conductor enters its own DTP seal, then cover the jacket end with adhesive-lined heat-shrink. At the potted holes, scuff the jacket and separate the conductors so epoxy wets each one.</p>
</section>

<section>
  <h2>Current budget</h2>
  <p class="lede">Typical draw is about 12 A. A realistic peak (thruster at full, pump running, servos moving) is about 25 A, so the 30 A fuse fits; every servo stalled at the same moment as everything else would be about 32 A and would blow it. D1 splits each pole over two contacts (50 A), so no single contact sees more than about 15 A there. D3 pin 1 sees at most 13 A.</p>
  <div class="tbl mid"><table><thead><tr><th></th><th>Load</th><th>Typical</th><th>Peak</th></tr></thead><tbody>{btxt}</tbody></table></div>
</section>

<section>
  <h2>What goes on each board</h2>
  <div class="grid2">
    <div class="card"><h3>Board A · main drybox</h3><ul class="parts">{parts(boardA)}</ul></div>
    <div class="card"><h3>Board B · rear drybox</h3><ul class="parts">{parts(boardB)}</ul></div>
  </div>
  <div class="grid2">
    <div class="card"><h3>Rear drybox, off the board</h3><ul class="parts">{parts(rearOff)}</ul></div>
    <div class="card"><h3>Ballast pump · not chosen yet</h3><ul class="parts">
      <li>{ic('pump')}<div><b>Path is wired</b><p>GP19 → R6 → H1 pin 8 (D5) → TB5 → pump ESC U3 in the rear drybox → R3 → D2 → pump.</p></div></li>
      <li>{ic('pump')}<div><b>Target spec</b><p>12 V brushed DC, reversible, rated for submersion. Seaflo reversible pumps draw about 10 A (8 GPM) or 14 A (01 series), so the ESC must be rated above the pump’s stall current. It takes servo-style PWM: 1.5 ms stop, 1–2 ms full reverse to full forward.</p></div></li>
      <li>{ic('pump')}<div><b>Two one-way pumps instead?</b><p>Use H1 spare pin 6 (wire it to GP17) for a second ESC, and one of the 6 spare DTP sets for the second pump.</p></div></li>
    </ul></div>
  </div>
</section>

<section>
  <h2>Build rules</h2>
  <ol class="rules">
    <li>12 V stays on the bus bars. Neither breadboard carries it.</li>
    <li>One ground tie between the boxes: H1 pins 11–12.</li>
    <li>Cut every factory plug off (XT60, T-plug). Inside a box, wires land on screw terminals or the bus-bar clamps. Outside, crimp DTP contacts (servo leads are potted instead, uncut).</li>
    <li>Fill all four cavities in every DTP: D1 uses all four for power, D2 pins 3–4 get a dummy loop, and spare H1 pins 6–7 get real wires.</li>
    <li>Cut and seal the red BEC wire on every ESC signal lead.</li>
    <li>Charge through a DTP04-4P → XT60 adapter lead that plugs into D1.</li>
    <li>All screw terminals are Molence 5.08 mm blocks (10 A, 22–12 AWG): they fit the breadboard grid and take 14 AWG. 12-pos = three 4-pos blocks side by side.</li>
  </ol>
</section>

<div class="src"><b>Sources</b>
<ul>
<li><a href="https://www.amazon.com/dp/B0C49B4G3M" target="_blank" rel="noopener">Amazon: Deutusacc Deutsch DTP connector kit (size 12, 12–14 AWG, 25 A)</a></li>
<li><a href="https://www.westmarine.com/pacer-marine-dtp-deutsch-socket-f-14-12-awg-wire-size-12-contact-10-pack-21458062.html" target="_blank" rel="noopener">West Marine: Pacer DTP size-12 sockets for 14–12 AWG marine wire</a></li>
<li><a href="https://www.hpacademy.com/technical-articles/deutsch-dt-series-connector-guide/" target="_blank" rel="noopener">HP Academy: Deutsch DT/DTP contact ratings</a></li>
<li><a href="https://hobbywater.com/products/underwater-thruster-1-2kg-12v" target="_blank" rel="noopener">Hobbywater: TD1.2 thruster + ESC, 5–13 A at 12 V</a></li>
<li><a href="https://hitecrcd.com/db777wp-32-bit-low-profile-waterproof-metal-case-servo" target="_blank" rel="noopener">Hitec DB777WP</a> · <a href="https://savox-servo.com/en/product/SW-1250MG/savox-servo-sw-1250mg-digital-high-voltage-coreless-motor-waterproof-metal-gear" target="_blank" rel="noopener">Savox SW-1250MG</a></li>
<li><a href="https://www.amazon.com/dp/B0CH8RHCNY" target="_blank" rel="noopener">Amazon: Molence 5.08 mm screw terminal blocks (10 A, 22–12 AWG)</a> · <a href="https://www.amazon.com/dp/B09D3BV22M" target="_blank" rel="noopener">OONO 2×6 30 A distribution module</a></li>
<li><a href="https://www.westmarine.com/seaflo-marine-seaflo-12v-reversible-8.0-gpm-self-priming-impeller-bilge-ballast-pump-24039984.html" target="_blank" rel="noopener">West Marine: Seaflo 12 V reversible 8 GPM pump (10 A)</a></li>
</ul></div>
</div>
'''

if __name__ == '__main__':
    open(sys.argv[1], 'w').write(HTML)
