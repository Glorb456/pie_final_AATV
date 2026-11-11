import sys, re
sys.path.insert(0, '.')
import page as old            # reuse icon set + base CSS
import diagram2

CSS_BASE = re.search(r'<style>(.*?)</style>', old.HTML, re.S).group(1)
ICONS = dict(old.ICONS)
ICONS.update({
 'dt': '<rect x="2" y="7" width="9" height="10" rx="1.5"/><rect x="13" y="7.5" width="9" height="9" rx="1.5"/><path d="M8 8v8" stroke-width="2.4"/><path d="M15.5 8.5v7" stroke-width="2"/>',
 'potted': '<path d="M2 4h20M2 20h20"/><rect x="7" y="4" width="10" height="16" rx="1" fill="currentColor" opacity=".25"/><path d="M10 2v20M14 2v20"/>',
 'busbar': '<rect x="2" y="9" width="20" height="6" rx="1.5"/><circle cx="6" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="18" cy="12" r="1.3"/>',
 'pump': '<circle cx="10" cy="13" r="6"/><path d="M10 13l4-3M16 13h6M2 13h2"/><path d="M8 4h4v3"/>',
 'wire': '<path d="M2 8c6 0 6 8 12 8h8" stroke-width="3"/><path d="M2 16c6 0 6-8 12-8h8" stroke-width="1.4"/>',
})
sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>'
    for k, v in ICONS.items()) + '</svg>'
def ic(n): return f'<svg class="ic" aria-hidden="true"><use href="#i-{n}"/></svg>'
C = diagram2.C
def chip(c): return f'<span class="sw" style="background:{c}"></span>'

SVG_A = diagram2.build('A')
SVG_B = diagram2.build('B')

legend = [(C['VBAT'], '12 V (VBAT)'), (C['GND'], 'Ground'), (C['V75'], '7.5 V servo rail'), (C['V33'], '3.3 V'),
          (C['SERVO'], 'Servo PWM'), (C['THR'], 'Thruster PWM'), (C['SIGG'], 'TD1.2 signal ground'),
          (C['DRV'], 'Wheel ESC PWM'), (C['PUMP'], 'Pump PWM'), (C['LEAK'], 'Leak sense'), (C['MOT'], 'Motor leads'),
          (C['USB'], 'USB cable')]
legend_html = ''.join(f'<li>{chip(c)}<span>{t}</span></li>' for c, t in legend)

def pinrows(rows):
    return ''.join(f'<tr><td class="num">{p}</td><td>{chip(c) if c else "<span class=sw-empty></span>"}{f}</td><td class="mono">{g}</td></tr>' for p, f, g, c in rows)

# ---------------------------------------------------------------- connector schedule
D = [
 dict(id='D1', pins=4, plans='AB', where='Battery ↔ trunk', side='Battery side: DT06-4S plug (sockets)',
      load='A: ≤22 A · B: ≤20 A, split over 2 contacts per pole', pinmap=[
        (1, '+12 V (after F1)', '14 AWG', C['VBAT']), (2, '+12 V (after F1)', '14 AWG', C['VBAT']),
        (3, 'GND (after SW1)', '14 AWG', C['GND']), (4, 'GND (after SW1)', '14 AWG', C['GND'])]),
 dict(id='D2', pins=8, plans='AB', where='Aft: thruster ESC + pump', side='Rear-box side: DT06-8S plug',
      load='Thruster ≤13 A on pins 1–2 (8 A nominal); pump ≤5 A on 5–6', pinmap=[
        (1, 'Thruster ESC +12 V', '14 AWG', C['VBAT']), (2, 'Thruster ESC GND', '14 AWG', C['GND']),
        (3, 'Thruster PWM (yellow)', '20 AWG', C['THR']), (4, 'Thruster signal GND (white)', '20 AWG', C['SIGG']),
        (5, 'Pump motor +', '14 AWG', C['MOT']), (6, 'Pump motor −', '14 AWG', C['MOT']),
        (7, 'Spare (2nd pump): cavity plug', '—', None), (8, 'Spare (2nd pump): cavity plug', '—', None)]),
 dict(id='D3', pins=12, plans='AB', where='Servo leads', side='Rear-box side: DT06-12S plug',
      load='Each servo on its own 3 pins; ≤7.4 A stall per + pin', pinmap=[
        ('1–3', 'M4: SIG · +7.5 V · GND', '20 AWG', C['SERVO']), ('4–6', 'M5: SIG · +7.5 V · GND', '20 AWG', C['SERVO']),
        ('7–9', 'M6: SIG · +7.5 V · GND', '20 AWG', C['SERVO']), ('10–12', 'M7: SIG · +7.5 V · GND', '20 AWG', C['SERVO'])]),
 dict(id='D4', pins=12, plans='AB', where='H1: main drybox ↔ rear drybox', side='Main-box side: DT06-12S plug',
      load='Signals only, <50 mA per pin', pinmap=None),
 dict(id='D5', pins=8, plans='A', where='Wheel ESCs (Plan A only)', side='Rear-box side: DT06-8S plug',
      load='≤13 A per ESC on its own contact pair', pinmap=[
        (1, 'Wheel ESC L +12 V', '14 AWG', C['VBAT']), (2, 'Wheel ESC L GND', '14 AWG', C['GND']),
        (3, 'Wheel ESC R +12 V', '14 AWG', C['VBAT']), (4, 'Wheel ESC R GND', '14 AWG', C['GND']),
        (5, 'DRV L PWM', '20 AWG', C['DRV']), (6, 'ESC L signal GND', '20 AWG', C['GND']),
        (7, 'DRV R PWM', '20 AWG', C['DRV']), (8, 'ESC R signal GND', '20 AWG', C['GND'])]),
]
h1_rows = {
 'A': [(1, 'M4 servo PWM', 'GP12', C['SERVO']), (2, 'M5 servo PWM', 'GP13', C['SERVO']), (3, 'M6 servo PWM', 'GP14', C['SERVO']),
       (4, 'M7 servo PWM', 'GP15', C['SERVO']), (5, 'Thruster PWM', 'GP16', C['THR']), (6, 'Wheel ESC L PWM', 'GP17', C['DRV']),
       (7, 'Wheel ESC R PWM', 'GP18', C['DRV']), (8, 'Pump PWM', 'GP19', C['PUMP']), (9, 'Rear leak sense', 'GP27', C['LEAK']),
       (10, '3.3 V (rear leak sensor)', '3V3', C['V33']), (11, 'GND', 'GND', C['GND']), (12, 'GND', 'GND', C['GND'])],
}
h1_rows['B'] = [r if r[0] not in (6, 7) else (r[0], 'Spare: cavity plug', '—', None) for r in h1_rows['A']]

def dcard(d, plan):
    if plan not in d['plans']:
        return ''
    pm = d['pinmap'] if d['pinmap'] else h1_rows[plan]
    return (f'<div class="card dcard"><div class="dhead">{ic("dt")}<div><b>{d["id"]} · DT {d["pins"]}-pin</b>'
            f'<span class="sub">{d["where"]}</span></div></div>'
            f'<p class="dmeta">{d["side"]}<br>{d["load"]}</p>'
            f'<div class="tbl" style="margin-top:8px;border:0"><table><thead><tr><th>Pin</th><th>Function</th><th>{"Wire" if d["pinmap"] else "Pico pin (all 20 AWG)"}</th></tr></thead>'
            f'<tbody>{pinrows(pm)}</tbody></table></div></div>')

def plan_block(plan):
    A = plan == 'A'
    svg = SVG_A if A else SVG_B
    n_conn = 5 if A else 4
    shop = ('1 × 4-pin, 2 × 8-pin, 2 × 12-pin' if A else '1 × 4-pin, 1 × 8-pin, 2 × 12-pin')
    budget = [
     ('thruster', 'TD1.2 thruster + ESC', '8 A', '13 A'),
     ('pump', 'Ballast pump (target)', '2–4 A', '5 A'),
     ('buck', 'Servo rail via buck (12 V side)', '~1 A', '~6 A'),
    ] + ([('motor', 'Wheel motors ×2 (estimate)', '5–10 A each', '30 A+ each at stall')] if A else []) + [
     ('pico', 'Pico + leak sensors (USB 5 V)', '<0.1 A', '—'),
    ]
    btxt = ''.join(f'<tr><td class="icc">{ic(i)}</td><td><b>{a}</b></td><td class="num">{t}</td><td class="num">{p}</td></tr>' for i, a, t, p in budget)
    mode = ('Water mode (thruster + pump + servos) peaks near 20 A. Land mode (wheels + servos) peaks near 22 A. '
            'They don’t run together, so a 25 A fuse fits both, and D1’s paired contacts carry 26 A.') if A else \
           ('Thruster + pump + servos peaks near 20 A, typical about 10 A. A 20 A fuse fits, and D1’s paired contacts carry 26 A.')
    cards = ''.join(dcard(d, plan) for d in D)
    return f'''
<section class="plan" data-plan="{plan}" id="plan-{plan.lower()}-view">
  <figure>
    <div class="sheet">{svg}</div>
    <figcaption>Plan {plan}. Thick wires and red-dashed cables are 14 AWG; thin wires and gray cables are 20 AWG. Scroll sideways on a phone.</figcaption>
  </figure>
  <div class="stats">
    <div><b>{n_conn}</b><span>Deutsch DT connectors ({shop})</span></div>
    <div><b>{6 - n_conn}</b><span>spare from a 6-pack, if the pin counts match</span></div>
    <div><b>{25 if A else 20} A</b><span>main fuse F1</span></div>
    <div><b>3</b><span>potted holes: A2, R2, R3 (+ air-tube fitting A1)</span></div>
  </div>
  <section>
    <h2>Deutsch connector schedule</h2>
    <p class="lede">Every connector outside the dryboxes is a Deutsch DT. The source side of each one (battery or drybox) gets the DT06 plug with socket contacts, so no live pins are exposed when unplugged.</p>
    <div class="grid3">{cards}</div>
  </section>
  <section>
    <h2>Current budget</h2>
    <p class="lede">{mode}</p>
    <div class="tbl mid"><table><thead><tr><th></th><th>Load</th><th>Typical</th><th>Peak</th></tr></thead><tbody>{btxt}</tbody></table></div>
  </section>
</section>'''

wire_rows = [
 ('High current', '14 AWG', 'Battery harness, D1 trunk (2 per pole), bus-bar taps, buck in and out, thruster ESC power, pump motor, wheel ESC power (A), Board B 7.5 V/GND rails',
  '≤13 A per conductor by design; 25 A fuse protects the doubled trunk'),
 ('Low current', '20 AWG', 'H1 harness, servo cable, thruster and wheel ESC signal pairs, leak sensors, 3.3 V, all on-board jumpers',
  'Signals under 50 mA; servo leads see up to 7.4 A only in brief stalls'),
]
wire_html = ''.join(f'<tr><td class="icc">{ic("wire")}</td><td><b>{a}</b><span class="sub">{b}</span></td><td>{c}</td><td class="note">{d}</td></tr>' for a, b, c, d in wire_rows)

boardA = [
 ('pico', 'A1 · Raspberry Pi Pico', 'socketed', 'USB from the Pi gives power and data.'),
 ('resistor', 'R1–R6 (+ R7, R8 in Plan A) · 220 Ω', 'series on each PWM line', 'R1–R4 GP12–15 servos, R5 GP16 thruster, R6 GP19 pump, R7/R8 GP17/18 wheels.'),
 ('screw', 'TA1 · 12-pos screw terminal, 5.08 mm', 'H1 out', 'Pin order in the H1 table. Cable potted through the wall at A2.'),
 ('screw', 'TA2 · 3-pos screw terminal, 5.08 mm', 'main leak sensor', '3V3 · GND · GP26. Sensor wired directly, no header.'),
]
boardB = [
 ('screw', 'TB1 · 12-pos', 'H1 in', 'Same pin order as TA1.'),
 ('screw', 'TB2 · 12-pos', 'servo cable to D3', 'SIG/+/− for M4, M5, M6, M7 in that order.'),
 ('screw', 'TB3 · 2-pos', 'thruster ESC signal', 'THR PWM + GND → D2 pins 3–4.'),
 ('screw', 'TB4 · 2-pos', 'pump ESC signal', 'GP19 PWM + GND to U3 (inside the box).'),
 ('screw', 'TB5 · 3-pos', 'rear leak sensor', '3V3 · GND · GP27.'),
 ('screw', 'TB6 · 2-pos', '7.5 V in from buck', '14 AWG from U1.'),
 ('screw', 'TB7 · 4-pos (Plan A)', 'wheel ESC signals', 'DRV L · GND · DRV R · GND → D5 pins 5–8.'),
 ('cap', 'C1 · 1000 µF 16 V', 'across 7.5 V rail', 'Absorbs servo spikes.'),
 ('board', 'Rails · 14 AWG', 'soldered along the strips', 'Carries servo stall current the strips can’t.'),
]
rearOff = [
 ('busbar', 'BB1 / BB2 · +12 V and GND bus bars', '≥30 A, 5 studs (B) or 7 (A)', 'D1 trunk lands on two studs each. Ring terminals on 14 AWG.'),
 ('buck', 'U1 · 12 → 7.5 V buck', '≥5 A continuous', '8–10 A gives headroom for servo stalls.'),
 ('esc', 'U3 · Pump ESC', 'brushed, with reverse', 'Dry, so it doesn’t have to be waterproof. Cut its BEC wire and factory plugs; land on bus bars and TB4.'),
]
def parts(items): return ''.join(f'<li>{ic(i)}<div><b>{a}</b> <span class="sub">{b}</span><p>{c}</p></div></li>' for i, a, b, c in items)

PLANCSS = '''
.toggle { display: inline-flex; gap: 0; margin: 20px 0 8px; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: var(--card); }
.toggle a { padding: 9px 16px; font: 600 14px var(--f-body); color: var(--muted); text-decoration: none; }
.toggle a[aria-current="true"] { background: var(--accent); color: var(--bg); }
.toggle a:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
.plan[hidden] { display: none !important; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap: 12px; margin-top: 18px; }
.stats div { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; display: grid; gap: 2px; }
.stats b { font: 700 28px/1 var(--f-display); color: var(--accent); }
.stats span { font-size: 13px; color: var(--muted); }
.grid3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 330px), 1fr)); gap: 16px; margin-top: 14px; align-items: start; }
.dcard { padding: 14px 14px 6px; }
.dhead { display: flex; gap: 10px; align-items: center; }
.dhead .ic { color: #e8590c; }
.dmeta { margin: 8px 0 0; font-size: 13px; color: var(--muted); }
.sw-empty { display: inline-block; width: 26px; height: 8px; margin-right: 7px; border-radius: 4px; border: 1px dashed var(--muted); vertical-align: middle; }
.gkey { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; list-style: none; padding: 0; margin: 0 0 14px; }
.gkey li { display: flex; align-items: center; gap: 8px; }
.gk { display: inline-block; width: 30px; border-radius: 4px; background: #3a4650; }
.changes { columns: 2 320px; column-gap: 28px; padding-left: 18px; margin: 12px 0 0; max-width: 100%; font-size: 14px; }
.changes li { break-inside: avoid; margin-bottom: 6px; }
'''

HTML = f'''<title>AA-TV Board Wiring</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS_BASE}{PLANCSS}</style>
{sprite}
<div class="wrap">
<header>
  <div class="eyebrow">AA-TV · electrical · v7 · Deutsch-only · two wire gauges</div>
  <h1>Board wiring, Plan A and Plan B</h1>
  <p class="lede">Plan A keeps the front driven wheels. Plan B drops them. Both use the same two solder-boards and pass every cable through epoxy-potted holes in the dryboxes. The only disconnects are Deutsch DT connectors in the wet zone and 5.08 mm screw terminals inside the boxes.</p>
  <nav class="toggle" aria-label="Choose plan">
    <a href="#plan-a" id="tab-a" aria-current="true">Plan A · front driven wheels</a>
    <a href="#plan-b" id="tab-b" aria-current="false">Plan B · no front motors</a>
  </nav>
</header>

<ul class="legend" aria-label="Wire color key">{legend_html}</ul>
<ul class="gkey">
  <li><span class="gk" style="height:5px;background:#e03131"></span>14 AWG wire (thick)</li>
  <li><span class="gk" style="height:2.6px;background:#1c7ed6"></span>20 AWG wire (thin)</li>
  <li><svg width="34" height="14" aria-hidden="true"><rect x="1" y="2" width="32" height="10" rx="5" fill="#3a4650"/><line x1="4" y1="7" x2="30" y2="7" stroke="#e03131" stroke-width="2" stroke-dasharray="6 4"/></svg>14 AWG cable</li>
  <li><svg width="34" height="14" aria-hidden="true"><rect x="1" y="3" width="32" height="8" rx="4" fill="#3a4650"/><line x1="4" y1="7" x2="30" y2="7" stroke="#9aa7b1" stroke-width="1.2" stroke-dasharray="2 3"/></svg>20 AWG cable</li>
  <li><svg class="ic" style="color:#e8590c" aria-hidden="true"><use href="#i-dt"/></svg>Deutsch DT pair</li>
  <li><svg width="34" height="14" aria-hidden="true"><rect x="1" y="2" width="32" height="10" rx="3" fill="#f59f00" stroke="#8a5300"/></svg>Epoxy-potted hole</li>
</ul>

{plan_block('A')}
{plan_block('B')}

<section>
  <h2>Two wire gauges</h2>
  <div class="tbl wide"><table><thead><tr><th></th><th>Gauge</th><th>Used for</th><th>Why it’s enough</th></tr></thead><tbody>{wire_html}</tbody></table></div>
  <p class="callout"><b>Check insulation diameter before buying.</b> DT seals grip automotive-style wire (GXL/TXL/GPT). Thick silicone 14 AWG can be too fat for the seal, and thin factory leads (ESC signal wires, some servo leads) can be too thin. Build thin leads up with adhesive-lined heat-shrink where the seal sits, or splice them to 20 AWG first. DT size-16 contacts take 14–20 AWG; make sure your kit includes contacts for 14 AWG.</p>
  <p class="callout"><b>Potting:</b> epoxy doesn’t bond to silicone insulation, so water can follow it into the box. Use PVC or XLPE-jacketed wire, scuff it where it passes the hole, separate the conductors so epoxy wets each one, and pot at least 15–20 mm deep.</p>
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
      <li>{ic('pump')}<div><b>Interface is reserved</b><p>GP19 → R6 → H1 pin 8 → TB4 → pump ESC U3 in the rear drybox → R3 → D2 pins 5–6 → pump.</p></div></li>
      <li>{ic('pump')}<div><b>Target spec</b><p>12 V brushed DC, reversible (so one ESC both fills and empties), ≤5 A, rated for continuous submersion. A brushed ESC with reverse takes the same 1–2 ms PWM as a servo, 1.5 ms = stop.</p></div></li>
      <li>{ic('pump')}<div><b>From your shortlist</b><p>The SEAflow reversible draws 10 A and weighs 2.5 kg, which blows the budget. The $10 12 V pump is one-way: two of them need a second ESC on D2 spare pins 7–8 and a second PWM pin (GP20 is free).</p></div></li>
    </ul></div>
  </div>
</section>

<section>
  <h2>Build rules</h2>
  <ol class="rules">
    <li>12 V stays on the bus bars. Neither breadboard carries it.</li>
    <li>One ground tie between the boxes: H1 pins 11–12. Board B ground meets battery ground at the buck and bus bar.</li>
    <li>Cut every factory plug off (XT60, T-plug, JR). Inside a box, land wires on screw terminals or ring terminals. Outside, crimp DT contacts.</li>
    <li>Fill unused DT cavities with cavity plugs (D2 pins 7–8; D4 pins 6–7 in Plan B), or the connector isn’t sealed.</li>
    <li>Cut and seal the red BEC wire on every ESC signal lead. The Pico runs from the Pi’s USB.</li>
    <li>Charge through a DT04-4P → XT60 adapter lead that plugs into D1.</li>
    <li>All screw terminals are 5.08 mm pitch. 3.5 mm terminals don’t line up with the 2.54 mm breadboard holes.</li>
  </ol>
</section>

<div class="src"><b>Sources for ratings</b>
<ul>
<li><a href="https://www.hpacademy.com/technical-articles/deutsch-dt-series-connector-guide/" target="_blank" rel="noopener">HP Academy: Deutsch DT/DTM/DTP contact ratings</a></li>
<li><a href="https://www.digikey.at/de/htmldatasheets/production/1103152/0/0/1/dt-series.html" target="_blank" rel="noopener">TE/Deutsch DT series data (13 A size 16, 14–20 AWG, 2–12 pins)</a></li>
<li><a href="https://www.premier-cables.com/news/dt-series-connector-guide-85490296.html" target="_blank" rel="noopener">DT guide: cavity plugs for unused positions</a></li>
<li><a href="https://hobbywater.com/products/underwater-thruster-1-2kg-12v" target="_blank" rel="noopener">Hobbywater: TD1.2 thruster + ESC, 5–13 A at 12 V</a></li>
<li><a href="https://hitecrcd.com/db777wp-32-bit-low-profile-waterproof-metal-case-servo" target="_blank" rel="noopener">Hitec DB777WP</a> · <a href="https://www.cmldistribution.co.uk/product/SAV-SW1210SG+/files/SAV-SW1210SGP%20Data%20Sheet.pdf" target="_blank" rel="noopener">Savox SW-1210SG+</a></li>
</ul>Wheel-motor current is an estimate; measure one on the bench.</div>
</div>
<script>
(function () {{
  function show() {{
    var b = location.hash === '#plan-b';
    document.querySelectorAll('.plan').forEach(function (s) {{ s.hidden = (s.dataset.plan === 'B') !== b; }});
    document.getElementById('tab-a').setAttribute('aria-current', String(!b));
    document.getElementById('tab-b').setAttribute('aria-current', String(b));
  }}
  window.addEventListener('hashchange', show);
  show();
}})();
</script>
'''

if __name__ == '__main__':
    open(sys.argv[1], 'w').write(HTML)
