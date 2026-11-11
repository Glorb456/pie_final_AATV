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
    text(x + 65, y + 86, 'U1 · Buck 12 V → 7.5 V', 'ref', 'middle')
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

