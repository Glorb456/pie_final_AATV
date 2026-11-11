"""AA-TV wiring diagram v7 (Deutsch DT only, potted entries, 14/20 AWG). build('A'|'B') -> svg string."""
import math
import prims as P
from prims import C, add, wire, cable, text, dot, perfboard, resistor, esc_box, buck, servo_icon, motor, \
    thruster, battery, killswitch, leak_sensor, pico, pin_name, esc, curve_d

HI, LO = 5.0, 2.6          # stroke widths: 14 AWG vs 20 AWG
C = dict(C); C['PUMP'] = '#e64980'   # pump PWM (pink)
W, H = 1700, 1250

def fuse(cx, cy, amps):
    add(f'<rect x="{cx - 26}" y="{cy - 11}" width="52" height="22" rx="10" fill="#212529" stroke="#000"/>')
    add(f'<rect x="{cx - 9}" y="{cy - 8}" width="18" height="16" rx="2" fill="{"#f8f9fa" if amps == 25 else "#fcc419"}" stroke="#333"/>')
    text(cx, cy + 3.5, str(amps), 'devd', 'middle', size=9)
    text(cx, cy - 18, f'F1 · {amps} A blade fuse', 'ref', 'middle')
    text(cx, cy + 27, 'waterproof inline holder', 'small', 'middle')

def vcurve(x0, y0, x1, y1):
    my = (y0 + y1) / 2
    return f'M{x0},{y0} C{x0},{my} {x1},{my} {x1},{y1}'

def wire_d(d, color, w):
    add(f'<path class="halo" d="{d}" stroke-width="{w + 6}"/>')
    add(f'<path class="wo" d="{d}" stroke-width="{w + 1.8}"/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')

def hcable(pts, kind='lo', r=16):
    """Jacketed bundle in the wet zone / between items. kind: lo (20 AWG bundle), hi (14 AWG bundle), mix."""
    w = {'lo': 9, 'hi': 13, 'mix': 13}[kind]
    d = P.path_d(pts, r=r)
    add(f'<path class="halo" d="{d}" stroke-width="{w + 6}"/>')
    add(f'<path d="{d}" fill="none" stroke="#0e1418" stroke-width="{w + 2}" stroke-linecap="round" stroke-linejoin="round"/>')
    add(f'<path d="{d}" fill="none" stroke="#3a4650" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind in ('hi', 'mix'):
        add(f'<path d="{d}" fill="none" stroke="{C["VBAT"]}" stroke-width="2.2" stroke-dasharray="14 10" stroke-linecap="round"/>')
    if kind in ('lo', 'mix'):
        add(f'<path d="{d}" fill="none" stroke="#9aa7b1" stroke-width="1.2" stroke-dasharray="3 5" stroke-linecap="round"/>')

def ctag(x, y, t, anchor='middle'):
    tw = len(t) * 6.0 + 12
    x0 = x - tw / 2 if anchor == 'middle' else (x if anchor == 'start' else x - tw)
    add(f'<rect x="{x0}" y="{y - 9}" width="{tw}" height="17" rx="4" class="ctag"/>')
    text(x0 + tw / 2, y + 3.5, t, 'ctagt', 'middle')

def dt(cx, cy, n, name, sub=None, sub2=None, vertical=False, dx=0, below=False):
    """Deutsch DT mated pair icon. Gray housings, orange (plug) + green (receptacle) wedgelocks."""
    h = 22 + n * 2.2
    add(f'<g>')
    add(f'<rect x="{cx - 40}" y="{cy - h / 2}" width="38" height="{h}" rx="5" fill="#9aa3ab" stroke="#3b4248" stroke-width="1.6"/>')
    add(f'<rect x="{cx - 14}" y="{cy - h / 2 + 3}" width="7" height="{h - 6}" rx="2" fill="#f76707"/>')
    add(f'<rect x="{cx + 2}" y="{cy - h / 2 + 2}" width="36" height="{h - 4}" rx="4" fill="#868e96" stroke="#3b4248" stroke-width="1.6"/>')
    add(f'<rect x="{cx + 8}" y="{cy - h / 2 + 5}" width="6" height="{h - 10}" rx="2" fill="#37b24d"/>')
    add(f'<rect x="{cx - 46}" y="{cy - 5}" width="7" height="10" rx="2" fill="#3b4248"/>')
    add(f'<rect x="{cx + 37}" y="{cy - 5}" width="7" height="10" rx="2" fill="#3b4248"/>')
    add('</g>')
    text(cx + dx, (cy + h / 2 + 16) if below else (cy - h / 2 - 8), name, 'dtname', 'middle')
    if sub:
        text(cx, cy + h / 2 + 14, sub, 'small', 'middle')
    if sub2:
        text(cx, cy + h / 2 + 27, sub2, 'small', 'middle')

def potted(cx, cy, w, label, horiz=True, left=False):
    """Epoxy-potted cable entry through a drybox wall."""
    add(f'<rect x="{cx - w / 2}" y="{cy - 9}" width="{w}" height="18" rx="5" fill="#f59f00" fill-opacity=".85" stroke="#8a5300" stroke-width="1.5"/>')
    add(f'<rect x="{cx - w / 2 + 3}" y="{cy - 6}" width="{w - 6}" height="12" rx="3" fill="url(#epoxy)"/>')
    if left:
        text(cx - w / 2 - 6, cy + 4, label, 'refw', 'end')
    else:
        text(cx + w / 2 + 6, cy + 4, label, 'refw', 'start')

def busbar(x, y, n, color, label, pitch=34):
    w = (n - 1) * pitch + 30
    add(f'<rect x="{x - 15}" y="{y - 9}" width="{w}" height="18" rx="4" fill="{color}" stroke="#11161b" stroke-width="1.5"/>')
    for i in range(n):
        add(f'<circle cx="{x + i * pitch}" cy="{y}" r="6" fill="#dee2e6" stroke="#495057" stroke-width="1.2"/>')
        add(f'<circle cx="{x + i * pitch}" cy="{y}" r="2.4" fill="#495057"/>')
    text(x - 22, y + 4, label, 'ref', 'end')
    return [x + i * pitch for i in range(n)]

def hterm(x0, y, labels, pitch=18, color='#1864ab'):
    """Horizontal 5.08 mm screw terminal row; returns x of each position. Wires enter from above."""
    n = len(labels)
    add(f'<rect x="{x0 - 9}" y="{y - 10}" width="{(n - 1) * pitch + 18}" height="22" rx="3" fill="{color}" stroke="#0b2e4f" stroke-width="1.4"/>')
    xs = []
    for i, lab in enumerate(labels):
        xx = x0 + i * pitch
        xs.append(xx)
        add(f'<circle cx="{xx}" cy="{y + 1}" r="6" fill="#ced4da" stroke="#495057"/>')
        add(f'<line x1="{xx - 4}" y1="{y + 5}" x2="{xx + 4}" y2="{y - 3}" stroke="#495057" stroke-width="1.5"/>')
        if lab:
            text(xx + 3, y + 18, lab, 'tpin', 'start', rot=90)
    return xs

def vterm(x, ys, nums, color='#1864ab'):
    top, bot = min(ys) - 11, max(ys) + 11
    add(f'<rect x="{x}" y="{top}" width="40" height="{bot - top}" rx="3" fill="{color}" stroke="#0b2e4f" stroke-width="1.5"/>')
    for yy, nn in zip(ys, nums):
        add(f'<circle cx="{x + 14}" cy="{yy}" r="6.5" fill="#ced4da" stroke="#495057" stroke-width="1.2"/>')
        add(f'<line x1="{x + 9.5}" y1="{yy + 4.5}" x2="{x + 18.5}" y2="{yy - 4.5}" stroke="#495057" stroke-width="1.6"/>')
        text(x + 32, yy + 3.5, str(nn), 'pinw', 'middle')

NETCOL = {}
def H1map(plan):
    m = {1: ('M4', C['SERVO']), 2: ('M5', C['SERVO']), 3: ('M6', C['SERVO']), 4: ('M7', C['SERVO']),
         5: ('THR', C['THR']), 6: ('DRV L', C['DRV']), 7: ('DRV R', C['DRV']), 8: ('PUMP', C['PUMP']),
         9: ('LEAK R', C['LEAK']), 10: ('3V3', C['V33']), 11: ('GND', C['GND']), 12: ('GND', C['GND'])}
    if plan == 'B':
        m[6] = ('spare', None); m[7] = ('spare', None)
    return m

def build(plan):
    P.out.clear()
    A = plan == 'A'
    fuse_a = 25 if A else 20
    NET = H1map(plan)
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" class="diagram" aria-label="AA-TV wiring diagram, Plan {plan}">')
    add('<defs><pattern id="holes" width="10" height="10" patternUnits="userSpaceOnUse">'
        '<rect width="10" height="10" fill="#efe4c4"/><circle cx="5" cy="5" r="1.5" fill="#c8b48a"/></pattern>'
        '<pattern id="water" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">'
        '<line x1="0" y1="7" x2="14" y2="7" class="waterline"/></pattern>'
        '<pattern id="epoxy" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#ffd8a8"/>'
        '<circle cx="2" cy="2" r="1" fill="#e8590c" opacity=".5"/></pattern></defs>')
    add(f'<rect width="{W}" height="{H}" class="panel"/>')

    # zones
    add('<rect x="14" y="742" width="1672" height="494" rx="16" fill="url(#water)" class="wetzone"/>')
    text(34, 772, 'WET ZONE', 'zone'); text(34, 790, 'every connector out here is a Deutsch DT', 'zones', size=12)
    add('<rect x="30" y="112" width="560" height="610" rx="16" class="drybox"/>')
    text(130, 140, 'MAIN DRYBOX', 'zone'); text(130, 158, 'upper, on hull · cable potted at A2', 'zones', size=12)
    add('<rect x="610" y="112" width="1060" height="610" rx="16" class="drybox"/>')
    text(628, 140, 'REAR DRYBOX', 'zone'); text(628, 158, 'inside open rear endcap · cables potted at R2 (20 AWG) and R3 (14 AWG)', 'zones', size=12)

    # buoy + tube
    add('<rect x="30" y="12" width="300" height="66" rx="33" fill="#ff922b" stroke="#a84300" stroke-width="2"/>')
    add('<rect x="58" y="26" width="64" height="38" rx="4" fill="#2b8a3e" stroke="#0d3b1b"/>')
    text(90, 49, 'Pi 4', 'devw', 'middle', size=12)
    add('<rect x="130" y="30" width="38" height="30" rx="5" fill="#343a40"/>')
    text(149, 49, 'bank', 'devs', 'middle', size=8)
    text(180, 41, 'BUOY · surface', 'devd', 'start', size=13)
    text(180, 58, 'Pi 4 + USB-C power bank', 'devd', 'start', size=10)
    add('<path d="M100,64 L100,112" stroke="#a5d8ff" stroke-opacity=".55" stroke-width="22" stroke-linecap="round" fill="none"/>')
    text(122, 96, 'air tube, USB cable inside', 'small', 'start')
    add('<rect x="84" y="104" width="32" height="16" rx="3" fill="#868e96" stroke="#343a40" stroke-width="2"/>')
    text(120, 124, 'A1', 'refw', 'start')

    # ============================================================ BOARD A
    perfboard(58, 168, 510, 528, f'BOARD A · Pico solder-board', bottom=True)
    top, bot = pico(140, 420)
    cable([(100, 66), (100, 475), (128, 475)], w=7, color=C['USB'])
    add('<rect x="120" y="466" width="12" height="18" rx="2" fill="#adb5bd" stroke="#343a40"/>')
    text(78, 520, 'USB: 5 V + data', 'small', 'start', rot=-90)
    J3X = 486
    rows_top = {12: 240, 11: 262, 10: 284, 9: 306, 8: 328, 7: 350, 6: 372, 5: 394}
    rows_bot = {4: 560, 3: 582, 2: 604, 1: 626}
    JY = {**rows_top, **rows_bot}
    RX = 414
    px, py = top(38); wire([(px, py), (px, 240), (J3X, 240)], C['GND'], LO)
    wire([(462, 240), (462, 262), (J3X, 262)], C['GND'], LO); dot(462, 240)
    px, py = top(36); wire([(px, py), (px, 284), (J3X, 284)], C['V33'], LO)
    px, py = top(33); wire([(px, py), (px, 404)], C['GND'], 2.2)
    add(f'<path d="M{px - 6},404 h12 M{px - 4},400 h8 M{px - 2},396 h4" stroke="#1c1c1c" stroke-width="1.6"/>')
    px, py = top(32); wire([(px, py), (px, 306), (J3X, 306)], C['LEAK'], LO)
    tg = [(25, 8, C['PUMP'])] + ([(24, 7, C['DRV']), (22, 6, C['DRV'])] if A else []) + [(21, 5, C['THR'])]
    for pin, row, col in tg:
        px, py = top(pin); y = JY[row]
        wire([(px, py), (px, y), (RX, y)], col, LO); wire([(RX + 36, y), (J3X, y)], col, LO); resistor(RX, y, 36)
    for pin, row in ((16, 1), (17, 2), (19, 3), (20, 4)):
        px, py = bot(pin); y = JY[row]
        wire([(px, py), (px, y), (RX, y)], C['SERVO'], LO); wire([(RX + 36, y), (J3X, y)], C['SERVO'], LO); resistor(RX, y, 36)
    text(RX + 18, 226, 'R · 220 Ω', 'small', 'middle')
    # TA2 main leak (screw terminal, sensor wired)
    tx = top(31)[0]
    xs = hterm(tx - 36, 206, ['', '', ''])
    text(tx - 18, 186, 'TA2 · leak', 'ref', 'middle')
    wire([(xs[1], 216), (xs[1], 240)], C['GND'], LO); dot(xs[1], 240)
    wire([(xs[0], 216), (xs[0], 284)], C['V33'], LO); dot(xs[0], 284)
    px, py = top(31); wire([(px, py), (px, 216)], C['LEAK'], LO)
    leak_sensor(300, 176, 'sensor → lowest point')
    add(f'<path d="M{xs[1]},196 Q{xs[1] + 16},178 300,186" fill="none" stroke="#c92a2a" stroke-width="3"/>')
    for n, t in ((38, 'GND'), (36, '3V3'), (33, 'AGND'), (32, 'GP27'), (31, 'GP26'), (25, 'GP19'), (24, 'GP18'), (22, 'GP17'), (21, 'GP16')):
        x, y = top(n); pin_name(x, y, t, up=True)
    for n, t in ((16, 'GP12'), (17, 'GP13'), (19, 'GP14'), (20, 'GP15')):
        x, y = bot(n); pin_name(x, y, t, up=False)
    vterm(J3X, [rows_top[k] for k in (12, 11, 10, 9, 8, 7, 6, 5)], [12, 11, 10, 9, 8, 7, 6, 5])
    vterm(J3X, [rows_bot[k] for k in (4, 3, 2, 1)], [4, 3, 2, 1])
    text(J3X + 20, 222, 'TA1 · 5–12', 'ref', 'middle'); text(J3X + 20, 542, 'TA1 · 1–4', 'ref', 'middle')
    for row in JY:
        if row == 11 or NET[row][1] is None:
            continue
        text(RX + 42, JY[row] - 4, NET[row][0], 'net', 'start')
    # H1 fan to A2 (bottom wall)
    order = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    for i, row in enumerate(order):
        col = NET[row][1]
        if col is None:
            continue
        x1 = 538 + i * 2.2
        wire_d(f'M{J3X + 40},{JY[row]} C{J3X + 60},{JY[row]} {x1},{(JY[row] + 690) / 2} {x1},690', col, 2.0)
    potted(550, 722, 40, 'A2')

    # ============================================================ BOARD B
    perfboard(638, 168, 672, 528, 'BOARD B · servo / signal board')
    TBX = 664
    TY = {r: 236 + i * 22 for i, r in enumerate(order)}   # row12 at top
    vterm(TBX, [TY[r] for r in order], order)
    text(TBX + 20, 218, 'TB1 · H1 in', 'ref', 'middle')
    HY = 648
    RG, RV = 588, 612
    servo_lab = []
    for s in ('M4', 'M5', 'M6', 'M7'):
        servo_lab += ['', '', '']
    tb2 = hterm(760, HY, servo_lab)
    tb3 = hterm(tb2[-1] + 34, HY, ['', ''])
    nxt = tb3[-1] + 34
    if A:
        tb7 = hterm(nxt, HY, ['', '', '', '']); nxt = tb7[-1] + 34
    tb4 = hterm(nxt, HY, ['', '']); nxt = tb4[-1] + 34
    tb5 = hterm(nxt, HY, ['', '', '']); nxt = tb5[-1] + 30
    GX = nxt
    RX1 = GX + 26
    # rails
    add(f'<rect x="720" y="{RG - 4}" width="{RX1 - 720}" height="8" rx="4" fill="{C["GND"]}"/>')
    add(f'<rect x="720" y="{RV - 4}" width="{RX1 - 720}" height="8" rx="4" fill="{C["V75"]}"/>')
    text(716, RG + 4, 'GND', 'small', 'end'); text(716, RV + 4, '7.5 V', 'small', 'end')
    text(724, RG - 8, 'rails: 14 AWG soldered along the strips', 'net', 'start')
    def run(row, xt, col):
        y = TY[row]
        wire([(TBX + 40, y), (xt, y), (xt, HY - 10)], col, LO)
    for k, row in enumerate((1, 2, 3, 4)):
        run(row, tb2[k * 3], C['SERVO'])
    run(5, tb3[0], C['THR'])
    if A:
        run(6, tb7[0], C['DRV']); run(7, tb7[2], C['DRV'])
    run(8, tb4[0], C['PUMP'])
    run(9, tb5[0], C['LEAK'])
    run(10, tb5[2], C['V33'])
    for row in (11, 12):
        wire([(TBX + 40, TY[row]), (GX, TY[row])], C['GND'], LO)
    wire([(GX, TY[12]), (GX, RG)], C['GND'], LO); dot(GX, TY[11]); dot(GX, RG)
    for k in range(4):
        xp, xn = tb2[k * 3 + 1], tb2[k * 3 + 2]
        wire([(xp, HY - 10), (xp, RV)], C['V75'], LO); dot(xp, RV, C['V75'])
        wire([(xn, HY - 10), (xn, RG)], C['GND'], LO); dot(xn, RG)
    gnds = [tb3[1], tb4[1], tb5[1]] + ([tb7[1], tb7[3]] if A else [])
    for xg in gnds:
        wire([(xg, HY - 10), (xg, RG)], C['GND'], LO); dot(xg, RG)
    for row in order:
        if row == 11 or NET[row][1] is None:
            continue
        text(TBX + 46, TY[row] - 4, NET[row][0], 'net', 'start')
    for lab, xx in (('TB2 servos', tb2[0]), ('TB3', tb3[0]), ('TB4', tb4[0]), ('TB5', tb5[0])) + ((('TB7', tb7[0]),) if A else ()):
        text(xx - 9, HY - 17, lab, 'net', 'start')
    # C1 at rail left end
    add(f'<rect x="730" y="{RG + 5}" width="20" height="{RV - RG - 10}" rx="4" fill="#364fc7" stroke="#1c2a7a"/>')
    text(740, RV + 22, 'C1', 'ref', 'middle')
    # TB6 7.5 V in at rails' right end
    add(f'<rect x="{RX1}" y="{RG - 10}" width="22" height="{RV - RG + 20}" rx="3" fill="#1864ab" stroke="#0b2e4f" stroke-width="1.4"/>')
    for yy in (RG, RV):
        add(f'<circle cx="{RX1 + 11}" cy="{yy}" r="6" fill="#ced4da" stroke="#495057"/>')
    text(RX1 + 11, RG - 16, 'TB6', 'ref', 'middle')
    # rear leak sensor wired to TB5
    leak_sensor(tb5[-1] + 10, 670, '')
    add(f'<path d="M{tb5[1]},{HY + 12} Q{tb5[1]},676 {tb5[-1] + 10},681" stroke="#c92a2a" stroke-width="3" fill="none"/>')

    # ============================================================ cable exits on Board B -> R2 (low-current pot)
    R2X, R3X = 1010, 1580
    potted(R2X, 722, 100, 'R2 · 20 AWG')
    potted(R3X, 722, 120, 'R3 · 14 AWG', left=True)
    # H1: jacketed inside the box from R2 to TB1
    hcable([(966, 712), (966, 706), (652, 706), (652, 540)], 'lo', r=12)
    for i, row in enumerate(order):
        col = NET[row][1]
        if col is None:
            continue
        x0 = 645 + i * 1.3
        wire_d(f'M{x0},540 C{x0},{(TY[row] + 540) / 2} {TBX - 24},{TY[row]} {TBX},{TY[row]}', col, 1.8)
    # servo wires converge to R2
    for k in range(12):
        col = C['SERVO'] if k % 3 == 0 else (C['V75'] if k % 3 == 1 else C['GND'])
        xe = 982 + k * 1.3
        wire_d(f'M{tb2[k]},{HY + 12} C{tb2[k]},{694} {xe},{680} {xe},712', col, 1.5)
    for k, col in enumerate((C['THR'], C['GND'])):
        wire_d(f'M{tb3[k]},{HY + 12} C{tb3[k]},694 {1022 + k * 2},684 {1022 + k * 2},712', col, 1.8)
    if A:
        for k, col in enumerate((C['DRV'], C['GND'], C['DRV'], C['GND'])):
            wire_d(f'M{tb7[k]},{HY + 12} C{tb7[k]},694 {1040 + k * 2},686 {1040 + k * 2},712', col, 1.8)

    # ============================================================ REAR off-board
    OX = 1340
    text(OX, 190, 'Off-board in the rear drybox', 'refw', 'start')
    # bus bars along the top; one column per load
    cols = [('buck', 1430), ('pump', 1480), ('thr', 1516)] + ([('wl', 1550), ('wr', 1584)] if A else []) + [('t1', 1618), ('t2', 1646)]
    xs_p = [x for _, x in cols]
    xs_n = [x + 12 for _, x in cols]
    def bar(y, xs, color, lab):
        add(f'<rect x="{min(xs) - 16}" y="{y - 9}" width="{max(xs) - min(xs) + 32}" height="18" rx="4" fill="{color}" stroke="#11161b" stroke-width="1.5"/>')
        for x in xs:
            add(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#dee2e6" stroke="#495057" stroke-width="1.2"/>')
            add(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#495057"/>')
        text(min(xs) - 22, y + 4, lab, 'ref', 'end')
    BP, BN = 226, 262
    bar(BP, xs_p, '#c92a2a', '+12 V bar')
    bar(BN, xs_n, '#1c1c1c', 'GND bar')
    text(1540, 206, 'bus bars ≥ 30 A, ring terminals', 'small', 'middle')
    X = dict(cols)
    # buck U1: inputs from top
    buck(1340, 330)
    wire([(X['buck'], BP + 6), (X['buck'], 330)], C['VBAT'], HI)
    wire([(X['buck'] + 12, BN + 6), (X['buck'] + 12, 330)], C['GND'], HI)
    # buck out -> TB6
    wire([(1340, 344), (1326, 344), (1326, RV), (RX1 + 22, RV)], C['V75'], HI)
    wire([(1340, 386), (1312, 386), (1312, RG), (RX1 + 22, RG)], C['GND'], HI)
    # U3 pump ESC
    esc_box(1340, 470, 150, 64, 'U3 · Pump ESC', 'brushed, reversible, BEC cut')
    wire([(X['pump'], BP + 6), (X['pump'], 470)], C['VBAT'], HI)
    wire([(X['pump'] + 12, BN + 6), (X['pump'] + 12, 470)], C['GND'], HI)
    wire([(tb4[0], HY + 12), (tb4[0], 702), (1356, 702), (1356, 534)], C['PUMP'], LO)
    wire([(tb4[1], HY + 12), (tb4[1], 708), (1368, 708), (1368, 534)], C['GND'], LO)
    # pump motor out -> R3
    wire([(1440, 534), (1440, 660), (R3X - 52, 680), (R3X - 52, 712)], C['MOT'], HI)
    wire([(1454, 534), (1454, 652), (R3X - 44, 672), (R3X - 44, 712)], C['MOT'], HI)
    # thruster power -> R3
    wire([(X['thr'], BP + 6), (X['thr'], 640), (R3X - 30, 680), (R3X - 30, 712)], C['VBAT'], HI)
    wire([(X['thr'] + 12, BN + 6), (X['thr'] + 12, 632), (R3X - 22, 672), (R3X - 22, 712)], C['GND'], HI)
    if A:
        for nm, dx in (('wl', -6), ('wr', 10)):
            wire([(X[nm], BP + 6), (X[nm], 650), (R3X + dx, 690), (R3X + dx, 712)], C['VBAT'], HI)
            wire([(X[nm] + 12, BN + 6), (X[nm] + 12, 644), (R3X + dx + 6, 684), (R3X + dx + 6, 712)], C['GND'], HI)
    # trunk in from R3 to bus bars
    for nm, dx in (('t1', 26), ('t2', 40)):
        wire([(R3X + dx, 712), (R3X + dx, 690), (X[nm], 660), (X[nm], BP + 6)], C['VBAT'], HI)
        wire([(R3X + dx + 6, 712), (R3X + dx + 6, 698), (X[nm] + 12, 668), (X[nm] + 12, BN + 6)], C['GND'], HI)

    # ============================================================ WET ZONE
    # H1: A2 -> D4 -> R2
    D4 = (760, 812)
    hcable([(550, 731), (550, D4[1]), (D4[0] - 46, D4[1])], 'lo')
    hcable([(D4[0] + 44, D4[1]), (966, D4[1]), (966, 731)], 'lo')
    dt(D4[0], D4[1], 12, 'D4 · DT 12-pin', 'H1 main ↔ rear · 12 × 20 AWG')
    # battery pack -> D1, trunk back to R3
    D1 = (470, 890)
    battery(70, 848)
    fuse(300, 870, fuse_a)
    killswitch(300, 950)
    wire([(240, 870), (274, 870)], C['VBAT'], HI)
    wire([(240, 910), (256, 910), (256, 950), (278, 950)], C['GND'], HI)
    for dy in (-6, 2):
        wire([(326, 870), (380, 870), (380, 884 + dy), (D1[0] - 46, 884 + dy)], C['VBAT'], HI)
    for dy in (10, 18):
        wire([(322, 950), (392, 950), (392, 884 + dy), (D1[0] - 46, 884 + dy)], C['GND'], HI)
    add('<rect x="374" y="862" width="12" height="16" rx="4" fill="#1c1c1c" opacity=".85"/>')
    add('<rect x="386" y="942" width="12" height="16" rx="4" fill="#1c1c1c" opacity=".85"/>')
    text(290, 1004, 'battery-side splits: solder + adhesive heat-shrink', 'small', 'middle')
    text(155, 1022, 'charge through a D1 → XT60 adapter lead', 'small', 'middle')
    dt(D1[0], D1[1], 4, 'D1 · DT 4-pin', 'battery · 2 contacts per pole', '26 A total')
    hcable([(R3X + 33, 731), (R3X + 33, 752), (1676, 752), (1676, 1214), (720, 1214), (720, D1[1]), (D1[0] + 44, D1[1])], 'hi')
    ctag(900, 1214, 'trunk · 4 × 14 AWG')
    # D3 servos
    D3 = (880, 960)
    hcable([(988, 731), (988, 900), (800, 900), (800, D3[1]), (D3[0] - 46, D3[1])], 'lo')
    ctag(890, 900, '12 × 20 AWG')
    dt(D3[0], D3[1], 12, 'D3 · DT 12-pin · servos')
    for i, (s, role) in enumerate((('M4', 'rudder'), ('M5', 'rudder'), ('M6', 'elevator'), ('M7', 'elevator'))):
        y = 900 + i * 66
        sx = 990
        yy = D3[1] - 15 + i * 10
        for k, col in enumerate((C['SERVO'], C['V75'], C['GND'])):
            wire_d(f'M{D3[0] + 44},{yy + k * 2.5} C{D3[0] + 70},{yy + k * 2.5} {sx - 40},{y + 13 + k * 4} {sx - 8},{y + 13 + k * 4}', col, 1.8)
        servo_icon(sx, y, f'{s} · {role}')
    text(880, 1186, 'JR plugs cut off; DT contacts crimped on the servo leads', 'small', 'middle')
    # D2 aft: low (THR sig) from R2, high (thruster power + pump motor) from R3
    D2 = (1300, 880)
    hcable([(1023, 731), (1023, 786), (1236, 786), (1236, D2[1] - 4), (D2[0] - 46, D2[1] - 4)], 'lo')
    hcable([(R3X - 37, 731), (R3X - 37, 806), (1250, 806), (1250, D2[1] + 6), (D2[0] - 46, D2[1] + 6)], 'hi')
    ctag(1180, 786, '2 × 20 AWG')
    ctag(1380, 806, '4 × 14 AWG')
    dt(D2[0], D2[1], 8, 'D2 · DT 8-pin · aft', dx=30)
    esc_box(1390, 850, 124, 58, 'U2 · TD1.2 ESC', 'waterproof · wet')
    wire([(D2[0] + 44, 866), (1390, 864)], C['VBAT'], HI)
    wire([(D2[0] + 44, 873), (1390, 874)], C['GND'], HI)
    wire([(D2[0] + 44, 880), (1390, 888)], C['THR'], LO)
    wire([(D2[0] + 44, 885), (1390, 896)], C['SIGG'], LO)
    cable([(1514, 879), (1530, 879)], w=8, color='#1c1c1c')
    thruster(1590, 879)
    wire([(D2[0] + 44, 891), (1356, 891), (1356, 986), (1384, 986)], C['MOT'], HI)
    wire([(D2[0] + 44, 897), (1348, 897), (1348, 1000), (1384, 1000)], C['MOT'], HI)
    motor(1420, 992, 'M3 · ballast pump')
    text(1500, 997, '12 V brushed, reversible,', 'small', 'start')
    text(1500, 1010, '≤5 A · model TBD', 'small', 'start')
    if A:
        D5 = (1300, 1120)
        hcable([(1043, 731), (1043, 776), (1226, 776), (1226, D5[1] - 4), (D5[0] - 46, D5[1] - 4)], 'lo')
        hcable([(R3X + 1, 731), (R3X + 1, 820), (1262, 820), (1262, D5[1] + 6), (D5[0] - 46, D5[1] + 6)], 'hi')
        ctag(1090, 776, '4 × 20 AWG')
        ctag(1480, 820, '4 × 14 AWG')
        dt(D5[0], D5[1], 8, 'D5 · DT 8-pin · wheels', dx=10, below=True)
        for k, (ey, nm) in enumerate(((1086, 'U4 · Wheel ESC L'), (1156, 'U5 · Wheel ESC R'))):
            esc_box(1390, ey - 24, 124, 48, nm, 'waterproof · BEC cut')
            y0 = D5[1] - 14 + k * 14
            wire([(D5[0] + 44, y0), (1366 + k * 6, y0), (1366 + k * 6, ey - 12), (1390, ey - 12)], C['VBAT'], HI)
            wire([(D5[0] + 44, y0 + 5), (1378 + k * 4, y0 + 5), (1378 + k * 4, ey - 2), (1390, ey - 2)], C['GND'], HI)
            wire([(D5[0] + 44, y0 + 9), (1384, y0 + 9), (1384, ey + 9), (1390, ey + 9)], C['DRV'], LO) if k == 0 else \
                wire([(D5[0] + 44, y0 + 9), (1360, y0 + 9), (1360, ey + 9), (1390, ey + 9)], C['DRV'], LO)
            wire([(1514, ey - 6), (1556, ey - 6)], C['MOT'], HI); wire([(1514, ey + 6), (1556, ey + 6)], C['MOT'], HI)
            motor(1596, ey, f'M{1 + k} · wheel {"L" if k == 0 else "R"}')
    else:
        add('<rect x="1210" y="1066" width="450" height="104" rx="12" class="planbox"/>')
        text(1435, 1100, 'Plan B: no front driven motors', 'ref', 'middle', size=15)
        text(1435, 1122, 'No D5, no wheel ESCs, no TB7. H1 pins 6–7 and GP17/GP18 spare.', 'small', 'middle')
        text(1435, 1139, 'Fuse 20 A. Bus bars: 5 positions each.', 'small', 'middle')
    add('</svg>')
    return '\n'.join(P.out)

if __name__ == '__main__':
    import sys
    open(sys.argv[2], 'w').write(build(sys.argv[1]))
