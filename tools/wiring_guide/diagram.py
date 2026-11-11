"""Generate the AA-TV wiring diagram SVG (v6). All coordinates in SVG units."""
import math

W, H = 1700, 1210
out = []
def add(s): out.append(s)

# ---------------------------------------------------------------- wire colors
C = {
    'VBAT': '#e03131',   # 12 V battery
    'GND': '#1c1c1c',
    'V75': '#f08c00',    # 7.5 V servo rail
    'V33': '#9c36b5',    # 3.3 V
    'SERVO': '#1c7ed6',  # servo PWM
    'THR': '#fcc419',    # thruster PWM (TD1.2 yellow)
    'SIGG': '#f1f3f5',   # TD1.2 white signal ground
    'DRV': '#2f9e44',    # wheel ESC PWM
    'LEAK': '#15aabf',   # leak sense
    'SPARE': '#868e96',
    'USB': '#5c6b78',
    'MOT': '#495057',
}

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def path_d(pts, r=7):
    """Orthogonal polyline with rounded corners."""
    if len(pts) == 2:
        return f'M{pts[0][0]},{pts[0][1]} L{pts[1][0]},{pts[1][1]}'
    d = f'M{pts[0][0]},{pts[0][1]}'
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1 = math.hypot(x1 - x0, y1 - y0); l2 = math.hypot(x2 - x1, y2 - y1)
        rr = min(r, l1 / 2, l2 / 2)
        if rr < 0.5:
            d += f' L{x1},{y1}'; continue
        ax = x1 - (x1 - x0) / l1 * rr; ay = y1 - (y1 - y0) / l1 * rr
        bx = x1 + (x2 - x1) / l2 * rr; by = y1 + (y2 - y1) / l2 * rr
        d += f' L{ax:.1f},{ay:.1f} Q{x1},{y1} {bx:.1f},{by:.1f}'
    d += f' L{pts[-1][0]},{pts[-1][1]}'
    return d

def wire(pts, color, w=3.2, curve=False, dash=None):
    d = curve_d(pts) if curve else path_d(pts)
    da = f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<path class="halo" d="{d}" stroke-width="{w + 6}"/>')
    add(f'<path class="wo" d="{d}" stroke-width="{w + 1.8}"/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>')

def curve_d(pts):
    (x0, y0), (x1, y1) = pts
    mx = (x0 + x1) / 2
    return f'M{x0},{y0} C{mx},{y0} {mx},{y1} {x1},{y1}'

def cable(pts, w=12, color='#343a40', curve=False):
    d = curve_d(pts) if curve else path_d(pts, r=16)
    add(f'<path class="halo" d="{d}" stroke-width="{w + 6}"/>')
    add(f'<path d="{d}" fill="none" stroke="#11161b" stroke-width="{w + 2}" stroke-linecap="round" stroke-linejoin="round"/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

def text(x, y, t, cls='lbl', anchor='start', rot=None, size=None, weight=None, fill=None):
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    st = ''
    if size: st += f'font-size:{size}px;'
    if weight: st += f'font-weight:{weight};'
    if fill: st += f'fill:{fill};'
    s = f' style="{st}"' if st else ''
    add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}"{tr}{s}>{esc(t)}</text>')

def tag(x, y, t, color, anchor='start', dark_text=False):
    """Colored net tag (pill) at a wire end."""
    tw = len(t) * 6.6 + 12
    x0 = x if anchor == 'start' else x - tw
    tc = '#111' if dark_text else '#fff'
    add(f'<rect x="{x0}" y="{y - 8}" width="{tw}" height="16" rx="8" fill="{color}" stroke="#11161b" stroke-width="1"/>')
    add(f'<text class="tag" x="{x0 + tw / 2}" y="{y + 4}" text-anchor="middle" style="fill:{tc}">{esc(t)}</text>')

def dot(x, y, color='#11161b', r=3.2):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="#11161b" stroke-width="1"/>')

# ---------------------------------------------------------------- component art
def perfboard(x, y, w, h, title, bottom=False):
    add(f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="url(#holes)" stroke="#b39d6b" stroke-width="2"/>')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#8a7445" stroke-width="1" stroke-dasharray="2 3" opacity=".5"/>')
    ty = y + h - 12 if bottom else y + 24
    add(f'<text class="board" x="{x + 14}" y="{ty}">{esc(title)}</text></g>')

def screw_terminal(x, ys, label, side='left', pin_numbers=None, color='#1864ab'):
    """Vertical terminal block. ys = list of wire-entry y. side = where wires enter."""
    top, bot = min(ys) - 11, max(ys) + 11
    add(f'<rect x="{x}" y="{top}" width="40" height="{bot - top}" rx="3" fill="{color}" stroke="#0b2e4f" stroke-width="1.5"/>')
    for i, yy in enumerate(ys):
        add(f'<circle cx="{x + 14}" cy="{yy}" r="6.5" fill="#ced4da" stroke="#495057" stroke-width="1.2"/>')
        add(f'<line x1="{x + 9.5}" y1="{yy + 4.5}" x2="{x + 18.5}" y2="{yy - 4.5}" stroke="#495057" stroke-width="1.6"/>')
        if pin_numbers:
            text(x + 32, yy + 3.5, str(pin_numbers[i]), 'pinw', 'middle')
    if label:
        text(x + 20, top - 7, label, 'ref', 'middle')

def header(xs, y, label, plug=True, plug_color='#212529', label_below=False, sub=None):
    """Horizontal male pin header (2.54 mm) with optional mated plug drawn on it."""
    x0, x1 = min(xs) - 7, max(xs) + 7
    add(f'<rect x="{x0}" y="{y - 6}" width="{x1 - x0}" height="12" rx="2" fill="#212529"/>')
    for xx in xs:
        add(f'<rect x="{xx - 1.6}" y="{y - 11}" width="3.2" height="9" fill="#e9c46a"/>')
    if plug:
        add(f'<rect x="{x0 - 2}" y="{y + 6}" width="{x1 - x0 + 4}" height="12" rx="2" fill="{plug_color}" stroke="#868e96" stroke-width="1"/>')
    if label_below:
        text((x0 + x1) / 2, y + 15.5, label, 'pinw', 'middle', size=8.5)
    else:
        text((x0 + x1) / 2, y - 18, label, 'ref', 'middle')
        if sub:
            text((x0 + x1) / 2, y - 30, sub, 'small', 'middle')

def resistor(x, y, w=34):
    add(f'<rect x="{x}" y="{y - 5}" width="{w}" height="10" rx="5" fill="#d8c3a5" stroke="#7a6248" stroke-width="1"/>')
    for i, c in enumerate(['#d00000', '#d00000', '#7f4f24', '#c9a227']):
        bx = x + 7 + i * 6 + (4 if i == 3 else 0)
        add(f'<rect x="{bx}" y="{y - 5}" width="3" height="10" fill="{c}"/>')

def circ_connector(cx, cy, n, label, sub, r=26, wall=True):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r + 7}" fill="#adb5bd" stroke="#495057" stroke-width="2"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#495057" stroke="#212529" stroke-width="1.5"/>')
    for i in range(n - 1):
        a = 2 * math.pi * i / (n - 1)
        add(f'<circle cx="{cx + math.cos(a) * r * 0.62:.1f}" cy="{cy + math.sin(a) * r * 0.62:.1f}" r="2.6" fill="#e9c46a"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="#e9c46a"/>')
    text(cx, cy - r - 14, label, 'ref', 'middle')
    if sub:
        text(cx, cy + r + 21, sub, 'small', 'middle')

def gland(cx, cy, label, sub, horiz=True):
    pts = ' '.join(f'{cx + 24 * math.cos(math.pi / 6 + k * math.pi / 3):.1f},{cy + 24 * math.sin(math.pi / 6 + k * math.pi / 3):.1f}' for k in range(6))
    add(f'<polygon points="{pts}" fill="#868e96" stroke="#343a40" stroke-width="2"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="15" fill="#495057" stroke="#212529" stroke-width="1.5"/>')
    for k in range(7):
        a = 2 * math.pi * k / 7
        add(f'<circle cx="{cx + math.cos(a) * 8.5:.1f}" cy="{cy + math.sin(a) * 8.5:.1f}" r="2.4" fill="#1c1c1c"/>')

def xt60(cx, cy, label, waterproof=False, vertical=False):
    w, h = (22, 34) if vertical else (34, 22)
    add(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="4" fill="#ffd43b" stroke="#7a5c00" stroke-width="1.5"/>')
    if waterproof:
        add(f'<rect x="{cx - w / 2 - 3}" y="{cy - h / 2 - 3}" width="{w + 6}" height="{h + 6}" rx="6" fill="none" stroke="#1c1c1c" stroke-width="3"/>')
    if vertical:
        add(f'<line x1="{cx - w / 2}" y1="{cy}" x2="{cx + w / 2}" y2="{cy}" stroke="#7a5c00" stroke-width="1.5"/>')
    else:
        add(f'<line x1="{cx}" y1="{cy - h / 2}" x2="{cx}" y2="{cy + h / 2}" stroke="#7a5c00" stroke-width="1.5"/>')
    if label:
        text(cx, cy - h / 2 - 9, label, 'ref', 'middle')

def esc_box(x, y, w, h, title, sub, color='#1d2b36'):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{color}" stroke="#0b1117" stroke-width="2"/>')
    add(f'<rect x="{x + 6}" y="{y + 6}" width="{w - 12}" height="{h - 12}" rx="5" fill="none" stroke="#4dabf7" stroke-width="1" opacity=".45"/>')
    text(x + w / 2, y + h / 2 - 2, title, 'devw', 'middle')
    if sub:
        text(x + w / 2, y + h / 2 + 13, sub, 'devs', 'middle')

def buck(x, y):
    add(f'<rect x="{x}" y="{y}" width="130" height="70" rx="6" fill="#1971c2" stroke="#0b3d73" stroke-width="2"/>')
    add(f'<rect x="{x + 44}" y="{y + 14}" width="42" height="42" rx="6" fill="#212529"/>')
    add(f'<circle cx="{x + 65}" cy="{y + 35}" r="13" fill="none" stroke="#b08968" stroke-width="5"/>')
    add(f'<rect x="{x + 98}" y="{y + 12}" width="16" height="16" rx="2" fill="#4dabf7" stroke="#0b3d73"/>')
    add(f'<circle cx="{x + 106}" cy="{y + 20}" r="4" fill="#e9c46a"/>')
    text(x + 65, y - 8, 'U1 · Buck 12 V → 7.5 V', 'ref', 'middle')
    text(x + 8, y + 26, 'OUT', 'devs', 'start'); text(x + 8, y + 38, '7.5 V', 'devs', 'start')
    text(x + 122, y + 52, 'IN', 'devs', 'end'); text(x + 122, y + 64, '12 V', 'devs', 'end')

def servo_icon(x, y, label):
    add(f'<rect x="{x}" y="{y}" width="58" height="34" rx="4" fill="#212529" stroke="#000" stroke-width="1.5"/>')
    add(f'<rect x="{x - 8}" y="{y + 12}" width="74" height="10" rx="2" fill="#343a40"/>')
    add(f'<circle cx="{x + 42}" cy="{y + 17}" r="8" fill="#495057" stroke="#adb5bd" stroke-width="1.5"/>')
    add(f'<rect x="{x + 39}" y="{y - 10}" width="6" height="26" rx="3" fill="#ced4da" stroke="#495057" transform="rotate(25 {x + 42} {y + 17})"/>')
    text(x + 70, y + 21, label, 'dev', 'start')

def motor(cx, cy, label):
    add(f'<rect x="{cx - 34}" y="{cy - 20}" width="62" height="40" rx="8" fill="#ced4da" stroke="#495057" stroke-width="2"/>')
    add(f'<rect x="{cx - 34}" y="{cy - 20}" width="14" height="40" rx="4" fill="#868e96"/>')
    add(f'<rect x="{cx + 28}" y="{cy - 3}" width="16" height="6" fill="#adb5bd" stroke="#495057"/>')
    for k in range(3):
        add(f'<line x1="{cx - 12 + k * 10}" y1="{cy - 20}" x2="{cx - 12 + k * 10}" y2="{cy + 20}" stroke="#adb5bd"/>')
    text(cx + 6, cy + 36, label, 'dev', 'middle')

def thruster(cx, cy):
    add(f'<rect x="{cx - 70}" y="{cy - 30}" width="120" height="60" rx="18" fill="#f1f3f5" stroke="#868e96" stroke-width="2"/>')
    add(f'<ellipse cx="{cx + 50}" cy="{cy}" rx="10" ry="30" fill="#dee2e6" stroke="#868e96" stroke-width="2"/>')
    add(f'<path d="M{cx + 52},{cy - 22} L{cx + 70},{cy - 8} L{cx + 52},{cy - 2} Z M{cx + 52},{cy + 22} L{cx + 70},{cy + 8} L{cx + 52},{cy + 2} Z" fill="#adb5bd"/>')
    text(cx - 10, cy + 5, 'TD1.2', 'devd', 'middle')
    text(cx - 10, cy + 50, 'MT1 · Thruster (BLDC)', 'dev', 'middle')

def battery(x, y):
    add(f'<rect x="{x}" y="{y}" width="170" height="86" rx="10" fill="#343a40" stroke="#11161b" stroke-width="2"/>')
    add(f'<rect x="{x + 10}" y="{y + 10}" width="150" height="66" rx="6" fill="#495057"/>')
    text(x + 85, y + 38, '3S LiPo', 'devw', 'middle', size=16)
    text(x + 85, y + 58, '11.1 V nom · 12.6 V full', 'devs', 'middle')
    text(x + 85, y - 10, 'BT1 · Battery (wet, no box)', 'ref', 'middle')

def fuse(cx, cy):
    add(f'<rect x="{cx - 26}" y="{cy - 11}" width="52" height="22" rx="10" fill="#212529" stroke="#000"/>')
    add(f'<rect x="{cx - 9}" y="{cy - 8}" width="18" height="16" rx="2" fill="#2f9e44" stroke="#0b3d1c"/>')
    text(cx, cy + 3.5, '30', 'devw', 'middle', size=9)
    text(cx, cy - 18, 'F1 · 30 A blade fuse', 'ref', 'middle')
    text(cx, cy + 27, 'waterproof inline holder', 'small', 'middle')

def killswitch(cx, cy):
    add(f'<rect x="{cx - 22}" y="{cy - 14}" width="44" height="28" rx="6" fill="#c92a2a" stroke="#5c0f0f" stroke-width="1.5"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#ffe066" stroke="#5c0f0f"/>')
    text(cx, cy + 30, 'SW1 · Kill switch (−)', 'ref', 'middle')
    text(cx, cy + 43, '≥30 A, sealed', 'small', 'middle')

def splice(cx, cy, label=None):
    add(f'<rect x="{cx - 9}" y="{cy - 14}" width="18" height="28" rx="6" fill="#1c1c1c" opacity=".88"/>')
    if label:
        text(cx, cy - 20, label, 'ref', 'middle')

def leak_sensor(x, y, label):
    add(f'<rect x="{x}" y="{y}" width="46" height="22" rx="3" fill="#c92a2a" stroke="#5c0f0f"/>')
    for k in range(5):
        add(f'<line x1="{x + 16 + k * 6}" y1="{y + 3}" x2="{x + 16 + k * 6}" y2="{y + 19}" stroke="#e9c46a" stroke-width="2"/>')
    text(x + 52, y + 15, label, 'small', 'start')

def pico(x, y):
    """Pico lying horizontally, USB at left. Returns pin coordinate fn."""
    L, Wd = 270, 110
    add(f'<rect x="{x}" y="{y}" width="{L}" height="{Wd}" rx="7" fill="#1f7a3a" stroke="#0d3b1b" stroke-width="2"/>')
    # socket strips
    add(f'<rect x="{x + 2}" y="{y - 6}" width="{L - 4}" height="7" fill="#212529" opacity=".85"/>')
    add(f'<rect x="{x + 2}" y="{y + Wd - 1}" width="{L - 4}" height="7" fill="#212529" opacity=".85"/>')
    add(f'<rect x="{x - 10}" y="{y + 45}" width="16" height="20" rx="2" fill="#ced4da" stroke="#495057"/>')
    add(f'<rect x="{x + 112}" y="{y + 35}" width="40" height="40" rx="3" fill="#212529"/>')
    text(x + 132, y + 59, 'RP2040', 'devs', 'middle', size=8)
    text(x + 205, y + 50, 'Raspberry Pi', 'devw', 'middle', size=11)
    text(x + 205, y + 65, 'Pico', 'devw', 'middle', size=13)
    def top(n): return (x + 8 + (40 - n) * 13, y)
    def bot(n): return (x + 8 + (n - 1) * 13, y + Wd)
    for n in range(21, 41):
        px, py = top(n); add(f'<circle cx="{px}" cy="{py + 4}" r="2.6" fill="#e9c46a"/>')
    for n in range(1, 21):
        px, py = bot(n); add(f'<circle cx="{px}" cy="{py - 4}" r="2.6" fill="#e9c46a"/>')
    return top, bot

def pin_name(x, y, t, up=True):
    # small white label inside the Pico body next to a pin
    if up:
        text(x + 3.5, y + 12, t, 'pinw', 'end', rot=-90)
    else:
        text(x + 3.5, y - 12, t, 'pinw', 'start', rot=-90)

# =================================================================== DRAW
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="dgT dgD" class="diagram">')
add('<title id="dgT">AA-TV wiring diagram v6</title>')
add('<desc id="dgD">Board A with the Pico in the main drybox, harness H1, Board B with servo and thruster wiring in the rear drybox, and the wet zone with battery, fuse, kill switch, ESCs, motors, thruster and servos.</desc>')
add('<defs><pattern id="holes" width="10" height="10" patternUnits="userSpaceOnUse">'
    '<rect width="10" height="10" fill="#efe4c4"/><circle cx="5" cy="5" r="1.5" fill="#c8b48a"/></pattern>'
    '<pattern id="water" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">'
    '<line x1="0" y1="7" x2="14" y2="7" class="waterline"/></pattern></defs>')
add(f'<rect width="{W}" height="{H}" class="panel"/>')

# ---------------------------------------------------------------- zones
add('<rect x="14" y="738" width="1672" height="460" rx="16" fill="url(#water)" class="wetzone"/>')
text(34, 768, 'WET ZONE', 'zone'); text(34, 786, 'flooded hull · open rear endcap · splash areas', 'zones', size=12)
add('<rect x="30" y="112" width="662" height="610" rx="16" class="drybox"/>')
text(130, 140, 'MAIN DRYBOX', 'zone'); text(130, 158, 'upper, on hull · 2 penetrations: A1, A2', 'zones', size=12)
add('<rect x="866" y="112" width="804" height="610" rx="16" class="drybox"/>')
text(884, 140, 'REAR DRYBOX', 'zone'); text(884, 158, 'inside open rear endcap · 2 penetrations: R1, R2', 'zones', size=12)

# ---------------------------------------------------------------- BUOY + tether
add('<rect x="30" y="12" width="300" height="66" rx="33" fill="#ff922b" stroke="#a84300" stroke-width="2"/>')
add('<rect x="58" y="26" width="64" height="38" rx="4" fill="#2b8a3e" stroke="#0d3b1b"/>')
text(90, 49, 'Pi 4', 'devw', 'middle', size=12)
add('<rect x="130" y="30" width="38" height="30" rx="5" fill="#343a40"/>')
text(149, 49, 'bank', 'devs', 'middle', size=8)
text(180, 41, 'BUOY · surface', 'devd', 'start', size=13)
text(180, 58, 'Pi 4 + USB-C power bank', 'devd', 'start', size=10)
# air tube with USB inside
add('<path d="M100,64 L100,112" stroke="#a5d8ff" stroke-opacity=".55" stroke-width="22" stroke-linecap="round" fill="none"/>')
text(122, 96, 'air tube, USB cable inside', 'small', 'start')

# ================================================================= BOARD A
perfboard(58, 168, 606, 528, 'BOARD A · Pico solder-board', bottom=True)
top, bot = pico(140, 420)
# A1 bulkhead on top wall
add('<rect x="84" y="104" width="32" height="16" rx="3" fill="#868e96" stroke="#343a40" stroke-width="2"/>')
text(120, 124, 'A1', 'refw', 'start')
# USB cable from tube to Pico micro-USB
cable([(100, 66), (100, 475), (128, 475)], w=7, color=C['USB'])
add('<rect x="120" y="466" width="12" height="18" rx="2" fill="#adb5bd" stroke="#343a40"/>')
text(78, 520, 'USB: 5 V + data', 'small', 'start', rot=-90)

# J3 terminal blocks
J3X = 572
rows_top = {12: 240, 11: 262, 10: 284, 9: 306, 8: 328, 7: 350, 6: 372, 5: 394}
rows_bot = {4: 560, 3: 582, 2: 604, 1: 626}
J3Y = {**rows_top, **rows_bot}

# GND (pin 38) -> row 12, jumper to row 11
px, py = top(38); wire([(px, py), (px, 240), (J3X, 240)], C['GND'])
wire([(540, 240), (540, 262), (J3X, 262)], C['GND']); dot(540, 240)
# 3V3 (pin 36) -> row 10
px, py = top(36); wire([(px, py), (px, 284), (J3X, 284)], C['V33'])
# AGND -> ground stub
px, py = top(33); wire([(px, py), (px, 404)], C['GND'], w=2.4)
add(f'<path d="M{px - 6},{404} h12 M{px - 4},{400} h8 M{px - 2},{396} h4" stroke="#1c1c1c" stroke-width="1.6"/>')
# LEAK_REAR (pin 32) -> row 9
px, py = top(32); wire([(px, py), (px, 306), (J3X, 306)], C['LEAK'])
# top group through resistors
for pin, row, col in ((25, 8, C['SPARE']), (24, 7, C['DRV']), (22, 6, C['DRV']), (21, 5, C['THR'])):
    px, py = top(pin); y = J3Y[row]
    wire([(px, py), (px, y), (476, y)], col)
    wire([(512, y), (J3X, y)], col)
    resistor(476, y, 36)
# bottom group through resistors
for pin, row in ((16, 1), (17, 2), (19, 3), (20, 4)):
    px, py = bot(pin); y = J3Y[row]
    wire([(px, py), (px, y), (476, y)], C['SERVO'])
    wire([(512, y), (J3X, y)], C['SERVO'])
    resistor(476, y, 36)
text(494, 230, 'R1–R8 · 220 Ω', 'small', 'middle')
# J2 leak header (main)
j2x = [top(31)[0] - 30, top(31)[0] - 15, top(31)[0]]
header(j2x, 206, 'J2 · leak sensor', plug=True, plug_color='#c92a2a')
wire([(j2x[0], 212), (j2x[0], 240)], C['GND'], w=2.6); dot(j2x[0], 240)
wire([(j2x[1], 212), (j2x[1], 284)], C['V33'], w=2.6); dot(j2x[1], 284)
px, py = top(31); wire([(px, py), (px, 212)], C['LEAK'])
leak_sensor(300, 178, 'sensor → lowest point of box')
add(f'<path d="M{j2x[1]},{218} Q{j2x[1] + 20},{190} 300,189" fill="none" stroke="#c92a2a" stroke-width="3"/>')
# pin names inside Pico
for n, t in ((38, 'GND'), (36, '3V3'), (33, 'AGND'), (32, 'GP27'), (31, 'GP26'), (25, 'GP19'), (24, 'GP18'), (22, 'GP17'), (21, 'GP16')):
    x, y = top(n); pin_name(x, y, t, up=True)
for n, t in ((16, 'GP12'), (17, 'GP13'), (19, 'GP14'), (20, 'GP15')):
    x, y = bot(n); pin_name(x, y, t, up=False)
# J3 blocks
screw_terminal(J3X, [rows_top[k] for k in (12, 11, 10, 9, 8, 7, 6, 5)], 'J3 · 5–12', pin_numbers=[12, 11, 10, 9, 8, 7, 6, 5])
screw_terminal(J3X, [rows_bot[k] for k in (4, 3, 2, 1)], 'J3 · 1–4', pin_numbers=[4, 3, 2, 1])

NET = {12: ('GND', C['GND']), 11: ('GND', C['GND']), 10: ('3V3', C['V33']), 9: ('LEAK R', C['LEAK']),
       8: ('SPARE', C['SPARE']), 7: ('DRV R', C['DRV']), 6: ('DRV L', C['DRV']), 5: ('THR', C['THR']),
       4: ('M7', C['SERVO']), 3: ('M6', C['SERVO']), 2: ('M5', C['SERVO']), 1: ('M4', C['SERVO'])}

for row in (12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1):
    text(548 if row in (12,) else 518, J3Y[row] - 4, NET[row][0], 'net', 'start')
# J3 -> P1 fan (inside main box, to right wall)
P1 = (692, 432)
order = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
for i, row in enumerate(order):
    y0 = J3Y[row]; y1 = P1[1] - 49 + i * 9
    wire([(J3X + 40, y0), (P1[0] - 30, y1)], NET[row][1], w=2.6, curve=True)
circ_connector(P1[0], P1[1], 12, 'P1 · A2', None, r=24)

# ================================================================= HARNESS
cable([(726, 432), (832, 432)], w=20, color='#2b333b')
for k, row in enumerate(order[::2]):
    add(f'<line x1="742" y1="{425 + k * 2.6:.1f}" x2="816" y2="{425 + k * 2.6:.1f}" stroke="{NET[row][1]}" stroke-width="1.6" opacity=".9"/>')
text(779, 400, 'H1', 'zone', 'middle', size=17)
text(779, 467, '12-core cable', 'small', 'middle')
text(779, 480, 'IP68 plug each end', 'small', 'middle')

# ================================================================= BOARD B
P4 = (866, 432)
circ_connector(P4[0], P4[1], 12, 'P4 · R1', None, r=24)
perfboard(902, 168, 556, 528, 'BOARD B · servo / thruster logic')
J4X = 962
J4Y = {row: 236 + i * 22 for i, row in enumerate(order)}   # row12 at top
for i, row in enumerate(order):
    y1 = P4[1] - 49 + i * 9
    wire([(P4[0] + 30, y1), (J4X, J4Y[row])], NET[row][1], w=2.6, curve=True)
screw_terminal(J4X, [J4Y[r] for r in order], 'J4', pin_numbers=order, side='right')

# rails
RG, RV = 524, 560   # GND rail y, 7.5 V rail y
RX0, RX1 = 1010, 1440
add(f'<rect x="{RX0}" y="{RG - 4}" width="{RX1 - RX0}" height="8" rx="4" fill="{C["GND"]}"/>')
add(f'<rect x="{RX0}" y="{RV - 4}" width="{RX1 - RX0}" height="8" rx="4" fill="{C["V75"]}"/>')
text(RX0 - 6, RG + 4, 'GND rail', 'small', 'end')
text(RX0 - 6, RV + 4, '7.5 V rail', 'small', 'end')
text(RX0 - 6, RV + 17, '18 AWG bus wire', 'small', 'end')

HY = 616   # header pin row y
sx = 1046
hdr = {}
for s in ('M4', 'M5', 'M6', 'M7'):
    hdr[s] = (sx, sx + 12, sx + 24); sx += 58
j9 = (sx, sx + 12); sx += 46
j10 = (sx, sx + 16, sx + 32)
# signal wires from J4 to headers (right then down)
xr = J4X + 76   # start x of horizontal run (after net text)
def run(row, xt, col):
    y = J4Y[row]
    wire([(J4X + 40, y), (xt, y), (xt, HY - 10)], col)
for s, row in (('M4', 1), ('M5', 2), ('M6', 3), ('M7', 4)):
    run(row, hdr[s][0], C['SERVO'])
run(5, j9[0], C['THR'])
run(6, j10[0], C['DRV'])
run(7, j10[1], C['DRV'])
for row in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
    text(J4X + 46, J4Y[row] - 4, NET[row][0], 'net', 'start')
# + and - to rails
for s in hdr:
    a, b, c = hdr[s]
    wire([(b, HY - 10), (b, RV)], C['V75'], w=2.6); dot(b, RV, C['V75'])
    wire([(c, HY - 10), (c, RG)], C['GND'], w=2.6); dot(c, RG)
wire([(j9[1], HY - 10), (j9[1], RG)], C['GND'], w=2.6); dot(j9[1], RG)
wire([(j10[2], HY - 10), (j10[2], RG)], C['GND'], w=2.6); dot(j10[2], RG)
for s, sub in (('M4', 'rudder'), ('M5', 'rudder'), ('M6', 'elevator'), ('M7', 'elevator')):
    header(list(hdr[s]), HY, f'J{4 + int(s[1]) - 3}·{s}', plug=True, label_below=True)
header(list(j9), HY, 'J9', plug=True, plug_color='#212529', label_below=True)
# J10 is a screw terminal (horizontal): draw as block
add(f'<rect x="{j10[0] - 10}" y="{HY - 10}" width="{j10[2] - j10[0] + 20}" height="22" rx="3" fill="#1864ab" stroke="#0b2e4f" stroke-width="1.5"/>')
for xx in j10:
    add(f'<circle cx="{xx}" cy="{HY + 1}" r="6" fill="#ced4da" stroke="#495057"/>')
    add(f'<line x1="{xx - 4}" y1="{HY + 5}" x2="{xx + 4}" y2="{HY - 3}" stroke="#495057" stroke-width="1.5"/>')
text(j10[2] + 12, HY + 5, 'J10', 'ref', 'start')

# top-right: J13 spare, J11 leak (rows 8..10), GND rows 11/12 -> rail
J13 = (1300, 1314)
J11 = (1352, 1366, 1380)   # LEAK, GND, 3V3 (pins 3, 2, 1)
HT = 214
for row, xt, col in ((8, J13[0], C['SPARE']), (9, J11[0], C['LEAK']), (10, J11[2], C['V33'])):
    y = J4Y[row]
    wire([(J4X + 40, y), (xt, y), (xt, HT + 10)], col)
# GND rows 11, 12 -> right drop to GND rail
GX = 1420
for row in (11, 12):
    y = J4Y[row]
    wire([(J4X + 40, y), (GX, y)], C['GND'])
wire([(GX, J4Y[12]), (GX, RG)], C['GND']); dot(GX, J4Y[11]); dot(GX, RG)
# J13 GND, J11 GND -> to GX column via short jumpers at y=HT+26
wire([(J13[1], HT + 10), (J13[1], HT + 30), (GX, HT + 30)], C['GND'], w=2.4); dot(GX, HT + 30)
wire([(J11[1], HT + 10), (J11[1], HT + 30)], C['GND'], w=2.4); dot(J11[1], HT + 30)
header(list(J13), HT, 'J13', plug=False, sub='spare (pump)')
header(list(J11), HT, 'J11', plug=True, plug_color='#c92a2a')
leak_sensor(1352, 120 + 8, '')
add(f'<path d="M{J11[1]},{HT - 18} Q{J11[1] + 10},{170} 1375,{150}" fill="none" stroke="#c92a2a" stroke-width="3"/>')
text(1404, 146, 'rear leak sensor', 'small', 'start')

# C1 across rails + J12 (7.5 V in)
add(f'<rect x="1446" y="{RG - 6}" width="22" height="{RV - RG + 12}" rx="3" fill="#1864ab" stroke="#0b2e4f" stroke-width="1.5"/>')
for yy in (RG, RV):
    add(f'<circle cx="1457" cy="{yy}" r="6" fill="#ced4da" stroke="#495057"/>')
text(1444, RV + 24, 'J12', 'ref', 'end')
add(f'<rect x="1384" y="{RG + 6}" width="22" height="{RV - RG - 12}" rx="4" fill="#364fc7" stroke="#1c2a7a"/>')
add(f'<rect x="1384" y="{RG + 6}" width="6" height="{RV - RG - 12}" fill="#adb5bd"/>')
wire([(1395, RG + 4), (1395, RG + 6)], C['GND'], w=2)
text(1395, RV + 20, 'C1 1000 µF', 'small', 'middle')

# ================================================================= REAR off-board
buck(1492, 200)
esc_box(1492, 352, 140, 76, 'U2 · TD1.2 ESC', '12 V direct, no BEC')
xt60(1560, 520, None, vertical=False)
text(1582, 550, 'J14/J15', 'ref', 'start'); text(1582, 563, 'XT60 (dry)', 'small', 'start')
# battery cable from gland up to J14
GL = (1330, 722)
cable([(GL[0] + 40, GL[1]), (1560, 690), (1560, 531)], w=11, color='#7a1f1f')
# Y pigtail from J15 to buck IN and ESC power
wire([(1577, 516), (1640, 516), (1640, 214), (1622, 214)], C['VBAT'], w=4)
wire([(1577, 524), (1652, 524), (1652, 254), (1622, 254)], C['GND'], w=4)
wire([(1640, 380), (1632, 380)], C['VBAT'], w=4); dot(1640, 380, C['VBAT'])
wire([(1652, 400), (1632, 400)], C['GND'], w=4); dot(1652, 400)
# buck OUT -> J12
wire([(1492, 214), (1476, 214), (1476, RV), (1468, RV)], C['V75'], w=3.6)
wire([(1492, 254), (1484, 254), (1484, RG), (1468, RG)], C['GND'], w=3.6)
# ESC signal lead (yellow + white) -> J9 plug
wire([(1492, 410), (1470, 410), (1470, 662), (j9[0], 662), (j9[0], HY + 18)], C['THR'], w=2.6)
wire([(1492, 418), (1462, 418), (1462, 670), (j9[1], 670), (j9[1], HY + 18)], C['SIGG'], w=2.6)
text(1488, 404, 'sig', 'small', 'end')
# thruster cable from ESC to gland
cable([(1562, 428), (1562, 470), (1520, 470), (1520, 640), (GL[0] + 22, 700), (GL[0] + 22, GL[1])], w=8, color='#1c1c1c')

# servo leads + wheel signal cable from headers to gland
for i, s in enumerate(('M4', 'M5', 'M6', 'M7')):
    xm = hdr[s][1]
    cable([(xm, HY + 18), (xm, 680), (GL[0] - 30 + i * 8, 700), (GL[0] - 30 + i * 8, GL[1])], w=5, color='#212529')
xm = j10[1]
cable([(xm, HY + 12), (xm, 650), (GL[0] + 6, 690), (GL[0] + 6, GL[1])], w=6, color='#2b3a2e')
gland(GL[0], GL[1], 'R2', '')
text(GL[0] - 40, GL[1] + 6, 'R2', 'refw', 'end')

# ================================================================= WET ZONE
# cables leave the gland downward
# servos
SX = 1500
servo_y = [870, 940, 1010, 1080]
for i, (s, y) in enumerate(zip(('M4', 'M5', 'M6', 'M7'), servo_y)):
    xs = GL[0] - 30 + i * 8
    cable([(xs, GL[1]), (xs, 800 + i * 8), (SX - 40 + i * 4, 800 + i * 8), (SX - 40 + i * 4, y + 17), (SX - 8, y + 17)], w=5, color='#212529')
    servo_icon(SX, y, f'{s} servo')
text(SX + 10, 850, 'Servos: Hitec DB777WP / Savox', 'small', 'start')
# thruster
cable([(GL[0] + 22, GL[1]), (GL[0] + 22, 1000), (1270, 1000)], w=8, color='#1c1c1c')
thruster(1200, 1000)
# battery feed back to splice
BX = 70
battery(BX, 930)
xt60(290, 973, 'J16 / J17 · XT60W', waterproof=True)
wire([(BX + 170, 960), (273, 960)], C['VBAT'], w=5)
wire([(BX + 170, 986), (273, 986)], C['GND'], w=5)
wire([(307, 960), (360, 960)], C['VBAT'], w=5)
fuse(386, 960)
wire([(412, 960), (520, 960)], C['VBAT'], w=5)
wire([(307, 986), (330, 986), (330, 1030), (364, 1030)], C['GND'], w=5)
killswitch(386, 1030)
wire([(408, 1030), (536, 1030), (536, 980)], C['GND'], w=5)
splice(528, 970, 'S1 splice')
# splice -> rear drybox (battery 2-core) runs right along y 820 up to gland
cable([(540, 966), (600, 966), (600, 830), (GL[0] + 40, 830), (GL[0] + 40, GL[1])], w=11, color='#7a1f1f')
text(940, 822, 'battery 2-core, 12 AWG → rear drybox (through R2)', 'small', 'middle')
# splice -> wheel ESCs
EX = 700
wire([(536, 962), (560, 962), (560, 900), (EX, 900)], C['VBAT'], w=4)
wire([(536, 976), (572, 976), (572, 912), (EX, 912)], C['GND'], w=4)
wire([(560, 962), (560, 1062), (EX, 1062)], C['VBAT'], w=4); dot(560, 962, C['VBAT'])
wire([(572, 976), (572, 1074), (EX, 1074)], C['GND'], w=4); dot(572, 976)
esc_box(EX, 884, 120, 64, 'U3 · Wheel ESC L', 'waterproof, brushed')
esc_box(EX, 1046, 120, 64, 'U4 · Wheel ESC R', 'waterproof, brushed')
# wheel motor leads
for ey, ml in ((916, 'M1 · wheel L'), (1078, 'M2 · wheel R')):
    wire([(EX + 120, ey - 8), (900, ey - 8)], C['MOT'], w=4)
    wire([(EX + 120, ey + 8), (900, ey + 8)], C['MOT'], w=4)
    motor(940, ey, ml)
# wheel signal 3-core from gland to ESCs
cable([(GL[0] + 6, GL[1]), (GL[0] + 6, 800), (660, 800), (660, 860)], w=6, color='#2b3a2e')
splice(660, 868, '')
text(668, 852, 'S2 splice', 'ref', 'start')
wire([(660, 880), (660, 932), (EX, 932)], C['DRV'], w=2.6)
wire([(652, 880), (652, 1094), (EX, 1094)], C['DRV'], w=2.6)
wire([(668, 880), (668, 940), (EX, 940)], C['GND'], w=2.2)
wire([(644, 880), (644, 1102), (EX, 1102)], C['GND'], w=2.2)
# BEC note
text(EX + 60, 970, 'BEC red wire: cut + seal', 'small', 'middle')
text(EX + 60, 1132, 'BEC red wire: cut + seal', 'small', 'middle')

add('</svg>')

def build():
    return '\n'.join(out)

if __name__ == '__main__':
    import sys
    open(sys.argv[1], 'w').write(build())
