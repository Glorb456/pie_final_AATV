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

def build(plan='B'):
    P.out.clear()
    A = False
    fuse_a = 20
    NET = H1map('B')
    NET[6] = ('spare', C['SPARE']); NET[7] = ('spare', C['SPARE'])
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" class="diagram" aria-label="AA-TV wiring diagram v8">')
    add('<defs><pattern id="holes" width="10" height="10" patternUnits="userSpaceOnUse">'
        '<rect width="10" height="10" fill="#efe4c4"/><circle cx="5" cy="5" r="1.5" fill="#c8b48a"/></pattern>'
        '<pattern id="water" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">'
        '<line x1="0" y1="7" x2="14" y2="7" class="waterline"/></pattern>'
        '<pattern id="epoxy" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#ffd8a8"/>'
        '<circle cx="2" cy="2" r="1" fill="#e8590c" opacity=".5"/></pattern></defs>')
    add(f'<rect width="{W}" height="{H}" class="panel"/>')

    # zones
    add('<rect x="14" y="742" width="1672" height="494" rx="16" fill="url(#water)" class="wetzone"/>')
    text(34, 772, 'WET ZONE', 'zone'); text(34, 790, 'every connector out here is a Deutsch DTP 4-pin · all wire 14 AWG marine', 'zones', size=12)
    add('<rect x="30" y="112" width="560" height="610" rx="16" class="drybox"/>')
    text(130, 140, 'MAIN DRYBOX', 'zone'); text(130, 158, 'upper, on hull · cable potted at A2', 'zones', size=12)
    add('<rect x="610" y="112" width="1060" height="610" rx="16" class="drybox"/>')
    text(628, 140, 'REAR DRYBOX', 'zone'); text(628, 158, 'inside open rear endcap · cables potted at R2 (signals) and R3 (power)', 'zones', size=12)

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
        x1 = 536 + i * 2.6
        wire_d(f'M{J3X + 40},{JY[row]} C{J3X + 60},{JY[row]} {x1},{(JY[row] + 690) / 2} {x1},690', col, 2.6)
    potted(550, 722, 40, 'A2')

    # ============================================================ BOARD B
    perfboard(638, 168, 540, 528, 'BOARD B · servo / signal board')
    TBX = 664
    TY = {r: 236 + i * 22 for i, r in enumerate(order)}
    vterm(TBX, [TY[r] for r in order], order)
    text(TBX + 20, 218, 'TB1 · H1 in', 'ref', 'middle')
    HY = 648
    RG, RV = 588, 612
    tb2 = hterm(760, HY, ['', '', '', ''])
    tb3 = hterm(tb2[-1] + 34, HY, ['', '', '', ''])
    tb4 = hterm(tb3[-1] + 34, HY, ['', ''])
    tb5 = hterm(tb4[-1] + 34, HY, ['', ''])
    tb6 = hterm(tb5[-1] + 34, HY, ['', '', ''])
    GX = tb6[-1] + 30
    RX1 = GX + 26
    add(f'<rect x="720" y="{RG - 4}" width="{RX1 - 720}" height="8" rx="4" fill="{C["GND"]}"/>')
    add(f'<rect x="720" y="{RV - 4}" width="{RX1 - 720}" height="8" rx="4" fill="{C["V75"]}"/>')
    text(716, RG + 4, 'GND', 'small', 'end'); text(716, RV + 4, '7.5 V', 'small', 'end')
    text(724, RG - 8, 'rails: 14 AWG soldered along the strips', 'net', 'start')
    def run(row, xt, col):
        y = TY[row]
        wire([(TBX + 40, y), (xt, y), (xt, HY - 10)], col, LO)
    run(1, tb2[0], C['SERVO']); run(2, tb2[1], C['SERVO'])
    run(3, tb3[0], C['SERVO']); run(4, tb3[1], C['SERVO'])
    run(5, tb4[0], C['THR']); run(8, tb5[0], C['PUMP'])
    run(9, tb6[0], C['LEAK']); run(10, tb6[2], C['V33'])
    for row in (6, 7):
        wire([(TBX + 40, TY[row]), (TBX + 58, TY[row])], C['SPARE'], LO)
    for row in (11, 12):
        wire([(TBX + 40, TY[row]), (GX, TY[row])], C['GND'], LO)
    wire([(GX, TY[12]), (GX, RG)], C['GND'], LO); dot(GX, TY[11]); dot(GX, RG)
    for t in (tb2, tb3):
        wire([(t[2], HY - 10), (t[2], RV)], C['V75'], HI); dot(t[2], RV, C['V75'])
        wire([(t[3], HY - 10), (t[3], RG)], C['GND'], HI); dot(t[3], RG)
    for xg in (tb4[1], tb5[1], tb6[1]):
        wire([(xg, HY - 10), (xg, RG)], C['GND'], LO); dot(xg, RG)
    for row in order:
        if row == 11:
            continue
        text(TBX + 46, TY[row] - 4, NET[row][0], 'net', 'start')
    for lab, xx in (('TB2 rudder', tb2[0]), ('TB3 elevator', tb3[0]), ('TB4', tb4[0]), ('TB5', tb5[0]), ('TB6', tb6[0])):
        text(xx - 9, HY - 17, lab, 'net', 'start')
    add(f'<rect x="730" y="{RG + 5}" width="20" height="{RV - RG - 10}" rx="4" fill="#364fc7" stroke="#1c2a7a"/>')
    text(740, RV + 22, 'C1', 'ref', 'middle')
    add(f'<rect x="{RX1}" y="{RG - 10}" width="22" height="{RV - RG + 20}" rx="3" fill="#1864ab" stroke="#0b2e4f" stroke-width="1.4"/>')
    for yy in (RG, RV):
        add(f'<circle cx="{RX1 + 11}" cy="{yy}" r="6" fill="#ced4da" stroke="#495057"/>')
    text(RX1 + 11, RG - 16, 'TB7', 'ref', 'middle')
    leak_sensor(tb6[-1] + 8, 670, '')
    add(f'<path d="M{tb6[1]},{HY + 12} Q{tb6[1]},676 {tb6[-1] + 8},681" stroke="#c92a2a" stroke-width="3" fill="none"/>')

    # ============================================================ potted entries
    R2X, R3X = 880, 1545
    potted(R2X, 722, 110, 'R2 · signals', left=True)
    potted(R3X, 722, 150, 'R3 · power', left=True)
    # H1 inside rear box
    hcable([(836, 712), (836, 706), (652, 706), (652, 540)], 'hi', r=12)
    for i, row in enumerate(order):
        x0 = 645 + i * 1.3
        wire_d(f'M{x0},540 C{x0},{(TY[row] + 540) / 2} {TBX - 24},{TY[row]} {TBX},{TY[row]}', NET[row][1], 2.2)
    for k, col in enumerate((C['SERVO'], C['SERVO'], C['V75'], C['GND'])):
        wire_d(f'M{tb2[k]},{HY + 12} C{tb2[k]},692 {850 + k * 2},684 {850 + k * 2},712', col, 2.4)
        wire_d(f'M{tb3[k]},{HY + 12} C{tb3[k]},692 {866 + k * 2},684 {866 + k * 2},712', col, 2.4)
    for k, col in enumerate((C['THR'], C['GND'])):
        wire_d(f'M{tb4[k]},{HY + 12} C{tb4[k]},694 {886 + k * 3},686 {886 + k * 3},712', col, 2.4)

    # ============================================================ REAR off-board
    text(1200, 190, 'Off-board in the rear drybox', 'refw', 'start')
    cols = [('buck', 1300), ('pump', 1360), ('thr', 1510), ('t1', 1560), ('t2', 1598)]
    X = dict(cols)
    xs_p = [x for _, x in cols]; xs_n = [x + 12 for _, x in cols]
    def bar(y, xs, color, lab):
        add(f'<rect x="{min(xs) - 16}" y="{y - 9}" width="{max(xs) - min(xs) + 32}" height="18" rx="4" fill="{color}" stroke="#11161b" stroke-width="1.5"/>')
        for x in xs:
            add(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#dee2e6" stroke="#495057" stroke-width="1.2"/>')
            add(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#495057"/>')
        text(min(xs) - 22, y + 4, lab, 'ref', 'end')
    BP, BN = 226, 262
    bar(BP, xs_p, '#c92a2a', '+12 V bar'); bar(BN, xs_n, '#1c1c1c', 'GND bar')
    text(1450, 206, 'bus bars ≥ 30 A, ring terminals', 'small', 'middle')
    buck(1210, 330)
    wire([(X['buck'], BP + 6), (X['buck'], 330)], C['VBAT'], HI)
    wire([(X['buck'] + 12, BN + 6), (X['buck'] + 12, 330)], C['GND'], HI)
    wire([(1210, 344), (1196, 344), (1196, RV), (RX1 + 22, RV)], C['V75'], HI)
    wire([(1210, 386), (1184, 386), (1184, RG), (RX1 + 22, RG)], C['GND'], HI)
    esc_box(1340, 470, 150, 64, 'U3 · Pump ESC', 'brushed, reversible, BEC cut')
    wire([(X['pump'], BP + 6), (X['pump'], 470)], C['VBAT'], HI)
    wire([(X['pump'] + 12, BN + 6), (X['pump'] + 12, 470)], C['GND'], HI)
    wire([(tb5[0], HY + 12), (tb5[0], 700), (1352, 700), (1352, 534)], C['PUMP'], LO)
    wire([(tb5[1], HY + 12), (tb5[1], 708), (1364, 708), (1364, 534)], C['GND'], LO)
    # pump motor out: dry splice 1 -> 2 per lead, 4 wires to R3
    for k, (xo, dx) in enumerate(((1440, 0), (1440, 6), (1462, 12), (1462, 18))):
        wire([(xo, 560), (xo, 640), (1478 + dx, 676), (1478 + dx, 712)], C['MOT'], HI)
    wire([(1440, 534), (1440, 560)], C['MOT'], HI); wire([(1462, 534), (1462, 560)], C['MOT'], HI)
    add('<rect x="1432" y="556" width="38" height="12" rx="4" fill="#1c1c1c" opacity=".85"/>')
    text(1428, 566, 'dry splice 1 → 2', 'small', 'end')
    wire([(X['thr'], BP + 6), (X['thr'], 640), (1510, 712)], C['VBAT'], HI)
    wire([(X['thr'] + 12, BN + 6), (X['thr'] + 12, 640), (1522, 712)], C['GND'], HI)
    for nm, dx in (('t1', 40), ('t2', 56)):
        wire([(R3X + dx - 6, 712), (R3X + dx - 6, 690), (X[nm], 660), (X[nm], BP + 6)], C['VBAT'], HI)
        wire([(R3X + dx, 712), (R3X + dx, 698), (X[nm] + 12, 668), (X[nm] + 12, BN + 6)], C['GND'], HI)

    # ============================================================ WET ZONE
    # H1: A2 -> D6/D7/D8 -> R2
    DX = 690
    Dy = (812, 868, 924)
    hcable([(550, 731), (550, 780), (600, 780), (600, Dy[2])], 'hi', r=10)
    for y in Dy:
        hcable([(600, y), (DX - 46, y)], 'hi', r=8)
        hcable([(DX + 44, y), (780, y)], 'hi', r=8)
    hcable([(780, Dy[2]), (780, 780), (836, 780), (836, 731)], 'hi', r=10)
    for y, nm in zip(Dy, ('D6 · H1 1–4', 'D7 · H1 5–8', 'D8 · H1 9–12')):
        dt(DX, y, 4, nm)
    text(DX, 962, 'H1 main ↔ rear · 12 × 14 AWG', 'small', 'middle')
    # battery pack -> D1, trunk to R3
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
    dt(D1[0], D1[1], 4, 'D1 · DTP 4-pin · battery', '2 contacts per pole · 50 A')
    hcable([(R3X + 50, 731), (R3X + 50, 752), (1676, 752), (1676, 1214), (480, 1214), (480, 1060), (540, 1060), (540, D1[1]), (D1[0] + 44, D1[1])], 'hi')
    ctag(1000, 1214, 'trunk · 4 × 14 AWG')
    # servos: D5 elevator (upper, from R2 x868), D4 rudder (lower, from R2 x852)
    SX = 1030
    for (dname, xv, y, servos) in (('D5 · elevator', 868, 880, (('M6', 'elevator'), ('M7', 'elevator'))),
                                   ('D4 · rudder', 852, 1080, (('M4', 'rudder'), ('M5', 'rudder')))):
        hcable([(xv, 731), (xv, y), (930, y)], 'hi', r=12)
        dt(976, y, 4, dname + ' servos', None, None, dx=0)
        for j, (s, role) in enumerate(servos):
            sy = y - 52 + j * 68
            for k, col in enumerate((C['SERVO'], C['V75'], C['GND'])):
                yy = y - 6 + k * 4 + (j * 2)
                wire_d(f'M{1020},{yy} C{1040},{yy} {SX + 20},{sy + 13 + k * 4} {SX + 52},{sy + 13 + k * 4}', col, 1.8)
            servo_icon(SX + 60, sy, s)
        add(f'<rect x="1036" y="{y - 10}" width="10" height="20" rx="3" fill="#1c1c1c" opacity=".85"/>')
    text(1110, 1178, 'servo leads spliced to 14 AWG; the two + and two GND share pins 3–4', 'small', 'middle')
    # D3 thruster: signal pair from R2, power pair from R3
    D3 = (1300, 860)
    hcable([(887, 731), (887, 770), (1236, 770), (1236, D3[1] - 4), (D3[0] - 46, D3[1] - 4)], 'hi')
    hcable([(1516, 731), (1516, 800), (1250, 800), (1250, D3[1] + 6), (D3[0] - 46, D3[1] + 6)], 'hi')
    dt(D3[0], D3[1], 4, 'D3 · thruster', dx=24)
    esc_box(1390, 832, 124, 58, 'U2 · TD1.2 ESC', 'waterproof · wet')
    wire([(D3[0] + 44, 852), (1390, 846)], C['VBAT'], HI)
    wire([(D3[0] + 44, 858), (1390, 856)], C['GND'], HI)
    wire([(D3[0] + 44, 864), (1390, 870)], C['THR'], HI)
    wire([(D3[0] + 44, 870), (1390, 880)], C['SIGG'], HI)
    cable([(1514, 861), (1530, 861)], w=8, color='#1c1c1c')
    thruster(1590, 861)
    text(1452, 930, 'ESC leads spliced to 14 AWG pigtails', 'small', 'middle')
    # D2 pump from R3
    D2 = (1300, 1010)
    hcable([(1487, 731), (1487, 786), (1222, 786), (1222, D2[1]), (D2[0] - 46, D2[1])], 'hi')
    dt(D2[0], D2[1], 4, 'D2 · pump', '2 contacts per lead', dx=0)
    for k, col in enumerate((C['MOT'], C['MOT'], C['MOT'], C['MOT'])):
        wire([(D2[0] + 44, 1002 + k * 5), (1370, 1002 + k * 5)], col, 3.0)
    add('<rect x="1366" y="996" width="12" height="28" rx="4" fill="#1c1c1c" opacity=".85"/>')
    wire([(1378, 1004), (1420, 1004)], C['MOT'], HI); wire([(1378, 1018), (1420, 1018)], C['MOT'], HI)
    motor(1460, 1011, 'M3 · ballast pump')
    text(1530, 1006, '12 V brushed, reversible,', 'small', 'start')
    text(1530, 1019, '≤5 A · model TBD', 'small', 'start')
    add('</svg>')
    return '\n'.join(P.out)

if __name__ == '__main__':
    import sys
    open(sys.argv[2], 'w').write(build(sys.argv[1]))
