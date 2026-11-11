"""AA-TV wiring diagram v9: one IP67 main box (battery inside), 4x M16 glands, one solder-board.
build() -> svg string. Same drawing primitives as diagram6.py (prims.py)."""
import math
import prims as P
from prims import add, wire, cable, text, dot, perfboard, resistor, esc_box, servo_icon, motor, \
    thruster, leak_sensor, pico, pin_name

HI, LO = 5.0, 2.6          # stroke widths: 14 AWG vs 20 AWG
C = dict(P.C)
C['PUMP'] = '#e64980'      # pump PWM (pink)
C['I2C'] = '#2b8a3e'       # I2C SCL / SDA (green)
C['BAL'] = '#82c91e'       # balance-lead taps (lime)
W, H = 1700, 1250


def hcable(pts, kind='lo', r=16):
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


def dt(cx, cy, name, sub=None, sub2=None):
    """Deutsch DTP 4-pin mated pair. Left = plug (box side), right = receptacle."""
    h = 22 + 4 * 2.2
    add(f'<rect x="{cx - 40}" y="{cy - h / 2}" width="38" height="{h}" rx="5" fill="#9aa3ab" stroke="#3b4248" stroke-width="1.6"/>')
    add(f'<rect x="{cx - 14}" y="{cy - h / 2 + 3}" width="7" height="{h - 6}" rx="2" fill="#f76707"/>')
    add(f'<rect x="{cx + 2}" y="{cy - h / 2 + 2}" width="36" height="{h - 4}" rx="4" fill="#868e96" stroke="#3b4248" stroke-width="1.6"/>')
    add(f'<rect x="{cx + 8}" y="{cy - h / 2 + 5}" width="6" height="{h - 10}" rx="2" fill="#37b24d"/>')
    add(f'<rect x="{cx - 46}" y="{cy - 5}" width="7" height="10" rx="2" fill="#3b4248"/>')
    add(f'<rect x="{cx + 37}" y="{cy - 5}" width="7" height="10" rx="2" fill="#3b4248"/>')
    text(cx, cy - h / 2 - 8, name, 'dtname', 'middle')
    for lx in (cx - 30, cx + 20):
        add(f'<path d="M{lx},{cy + h / 2} q-10,16 10,16 q20,0 10,-16" fill="none" stroke="#868e96" stroke-width="3" stroke-linecap="round"/>')
    if sub:
        text(cx, cy + h / 2 + 30, sub, 'small', 'middle')
    if sub2:
        text(cx, cy + h / 2 + 43, sub2, 'small', 'middle')


def gland(cx, cy, name, sub, potted=False, anchor='start'):
    """M16 cable gland in the box wall (seen from the side): wall nut + dome."""
    add(f'<rect x="{cx - 17}" y="{cy - 10}" width="34" height="20" rx="3" fill="#495057" stroke="#212529" stroke-width="1.6"/>')
    add(f'<rect x="{cx - 12}" y="{cy + 8}" width="24" height="14" rx="6" fill="#343a40" stroke="#212529" stroke-width="1.4"/>')
    add(f'<rect x="{cx - 12}" y="{cy - 22}" width="24" height="14" rx="4" fill="#343a40" stroke="#212529" stroke-width="1.4"/>')
    if potted:
        add(f'<rect x="{cx - 8}" y="{cy - 6}" width="16" height="12" rx="2" fill="url(#epoxy)" stroke="#8a5300"/>')
    tx = cx + 24 if anchor == 'start' else cx - 24
    text(tx, cy - 2, name, 'refw', anchor)
    text(tx, cy + 12, sub, 'small', anchor)


def busbar(xs, y, color, label, left_label=True):
    x0, x1 = min(xs) - 16, max(xs) + 16
    add(f'<rect x="{x0}" y="{y - 9}" width="{x1 - x0}" height="18" rx="4" fill="{color}" stroke="#11161b" stroke-width="1.5"/>')
    for x in xs:
        add(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#dee2e6" stroke="#495057" stroke-width="1.2"/>')
        add(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#495057"/>')
    if left_label:
        text(x0 - 6, y + 4, label, 'ref', 'end')
    else:
        text(x1 + 6, y + 4, label, 'ref', 'start')


def hterm(x0, y, n, pitch=18, color='#1864ab'):
    add(f'<rect x="{x0 - 9}" y="{y - 10}" width="{(n - 1) * pitch + 18}" height="22" rx="3" fill="{color}" stroke="#0b2e4f" stroke-width="1.4"/>')
    xs = []
    for i in range(n):
        xx = x0 + i * pitch
        xs.append(xx)
        add(f'<circle cx="{xx}" cy="{y + 1}" r="6" fill="#ced4da" stroke="#495057"/>')
        add(f'<line x1="{xx - 4}" y1="{y + 5}" x2="{xx + 4}" y2="{y - 3}" stroke="#495057" stroke-width="1.5"/>')
    return xs


def vterm(x, ys, nums, color='#1864ab'):
    top, bot = min(ys) - 11, max(ys) + 11
    add(f'<rect x="{x}" y="{top}" width="40" height="{bot - top}" rx="3" fill="{color}" stroke="#0b2e4f" stroke-width="1.5"/>')
    for yy, nn in zip(ys, nums):
        add(f'<circle cx="{x + 14}" cy="{yy}" r="6.5" fill="#ced4da" stroke="#495057" stroke-width="1.2"/>')
        add(f'<line x1="{x + 9.5}" y1="{yy + 4.5}" x2="{x + 18.5}" y2="{yy - 4.5}" stroke="#495057" stroke-width="1.6"/>')
        text(x + 32, yy + 3.5, str(nn), 'pinw', 'middle')


def vres(x, y0, h=22, val=None):
    """Small vertical resistor body from y0 to y0+h."""
    add(f'<rect x="{x - 5}" y="{y0}" width="10" height="{h}" rx="5" fill="#d8c3a5" stroke="#7a6248" stroke-width="1"/>')
    for i, c in enumerate(['#a61e4d', '#343a40', '#c9a227']):
        add(f'<rect x="{x - 5}" y="{y0 + 4 + i * 5}" width="10" height="2.5" fill="{c}"/>')
    if val:
        text(x + 8, y0 + h / 2 + 3, val, 'net', 'start')


def vcap(x, y0):
    add(f'<line x1="{x - 7}" y1="{y0}" x2="{x + 7}" y2="{y0}" stroke="#212529" stroke-width="2.4"/>')
    add(f'<line x1="{x - 7}" y1="{y0 + 5}" x2="{x + 7}" y2="{y0 + 5}" stroke="#212529" stroke-width="2.4"/>')


def gnd_sym(x, y):
    add(f'<path d="M{x},{y - 4} V{y} M{x - 7},{y} h14 M{x - 4.5},{y + 3.5} h9 M{x - 2},{y + 7} h4" stroke="#1c1c1c" stroke-width="1.6" fill="none"/>')


def battery(x, y):
    add(f'<rect x="{x}" y="{y}" width="170" height="86" rx="10" fill="#343a40" stroke="#11161b" stroke-width="2"/>')
    add(f'<rect x="{x + 10}" y="{y + 10}" width="150" height="66" rx="6" fill="#495057"/>')
    text(x + 85, y + 38, '3S LiPo', 'devw', 'middle', size=16)
    text(x + 85, y + 58, '11.1 V nom · 12.6 V full', 'devs', 'middle')
    text(x + 85, y - 10, 'BT1 · Battery (inside the box)', 'ref', 'middle')


def fuse(cx, cy):
    add(f'<rect x="{cx - 26}" y="{cy - 11}" width="52" height="22" rx="10" fill="#212529" stroke="#000"/>')
    add(f'<rect x="{cx - 9}" y="{cy - 8}" width="18" height="16" rx="2" fill="#2f9e44" stroke="#0b3d1c"/>')
    text(cx, cy + 3.5, '30', 'devw', 'middle', size=9)
    text(cx, cy - 18, 'F1 · 30 A ATC fuse', 'ref', 'middle')
    text(cx, cy + 27, 'standard holder', 'small', 'middle')


def killswitch(cx, cy):
    add(f'<rect x="{cx - 22}" y="{cy - 14}" width="44" height="28" rx="6" fill="#c92a2a" stroke="#5c0f0f" stroke-width="1.5"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#ffe066" stroke="#5c0f0f"/>')
    text(cx, cy - 22, 'SW1 · Kill switch (+ side)', 'ref', 'middle')
    text(cx, cy + 27, '≥30 A DC · lid off to reach', 'small', 'middle')


def ec5(x, y0):
    """EC5 mated pair (J2), two poles at y0 and y0 + 22."""
    add(f'<rect x="{x}" y="{y0 - 12}" width="22" height="46" rx="4" fill="#1971c2" stroke="#0b3d73" stroke-width="1.5"/>')
    add(f'<rect x="{x + 22}" y="{y0 - 10}" width="20" height="42" rx="4" fill="#1864ab" stroke="#0b3d73" stroke-width="1.5"/>')
    text(x + 21, y0 + 52, 'J2 · EC5', 'ref', 'middle')


def buck(x, y):
    add(f'<rect x="{x}" y="{y}" width="130" height="70" rx="6" fill="#1971c2" stroke="#0b3d73" stroke-width="2"/>')
    add(f'<rect x="{x + 44}" y="{y + 14}" width="42" height="42" rx="6" fill="#212529"/>')
    add(f'<circle cx="{x + 65}" cy="{y + 35}" r="13" fill="none" stroke="#b08968" stroke-width="5"/>')
    add(f'<rect x="{x + 98}" y="{y + 12}" width="16" height="16" rx="2" fill="#4dabf7" stroke="#0b3d73"/>')
    add(f'<circle cx="{x + 106}" cy="{y + 20}" r="4" fill="#e9c46a"/>')
    text(x + 65, y + 86, 'U1 · Buck 12 V → 7.4 V', 'ref', 'middle')
    text(x + 8, y + 26, 'OUT', 'devs', 'start'); text(x + 8, y + 38, '7.4 V', 'devs', 'start')
    text(x + 122, y + 52, 'IN', 'devs', 'end'); text(x + 122, y + 64, '12 V', 'devs', 'end')


def ads(x, y, w=104, h=176):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#5f3dc4" stroke="#2b1a6b" stroke-width="2"/>')
    add(f'<rect x="{x + 34}" y="{y + 64}" width="36" height="36" rx="3" fill="#212529"/>')
    text(x + w / 2, y + 86, 'ADS1115', 'devs', 'middle', size=8)
    text(x + w / 2, y - 10, 'U4 · ADS1115 breakout', 'ref', 'middle')


def build():
    P.out.clear()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" class="diagram" aria-label="AA-TV wiring diagram v9">')
    add('<defs><pattern id="holes" width="10" height="10" patternUnits="userSpaceOnUse">'
        '<rect width="10" height="10" fill="#efe4c4"/><circle cx="5" cy="5" r="1.5" fill="#c8b48a"/></pattern>'
        '<pattern id="water" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">'
        '<line x1="0" y1="7" x2="14" y2="7" class="waterline"/></pattern>'
        '<pattern id="epoxy" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#ffd8a8"/>'
        '<circle cx="2" cy="2" r="1" fill="#e8590c" opacity=".5"/></pattern></defs>')
    add(f'<rect width="{W}" height="{H}" class="panel"/>')

    # ---------------------------------------------------------------- zones
    add('<rect x="14" y="904" width="1672" height="332" rx="16" fill="url(#water)" class="wetzone"/>')
    text(34, 934, 'WET ZONE', 'zone')
    text(34, 952, 'flooded hull = ballast space · only servos, thruster, pump cable + D2 and the pump drybox live out here', 'zones', size=12)
    add('<rect x="30" y="112" width="1640" height="768" rx="16" class="drybox"/>')
    text(130, 140, 'MAIN BOX', 'zone')
    text(130, 158, 'IP67 · 191 × 111 × 58 mm inside · the only drybox · 4 × M16 glands', 'zones', size=12)

    # buoy + tube -> G1
    add('<rect x="30" y="12" width="300" height="66" rx="33" fill="#ff922b" stroke="#a84300" stroke-width="2"/>')
    add('<rect x="58" y="26" width="64" height="38" rx="4" fill="#2b8a3e" stroke="#0d3b1b"/>')
    text(90, 49, 'Pi 4', 'devw', 'middle', size=12)
    add('<rect x="130" y="30" width="38" height="30" rx="5" fill="#343a40"/>')
    text(149, 49, 'bank', 'devs', 'middle', size=8)
    text(180, 41, 'BUOY · surface', 'devd', 'start', size=13)
    text(180, 58, 'Pi 4 + USB-C power bank', 'devd', 'start', size=10)
    add('<path d="M100,64 L100,92" stroke="#a5d8ff" stroke-opacity=".55" stroke-width="22" stroke-linecap="round" fill="none"/>')
    text(122, 90, 'air tube (sheath), USB cable inside', 'small', 'start')

    # ================================================================ BOARD
    perfboard(58, 168, 942, 692, 'BOARD · Pico + servo / signal solder-board', bottom=True)
    top, bot = pico(140, 430)
    cable([(100, 66), (100, 485), (128, 485)], w=7, color=C['USB'])
    gland(100, 112, 'G1 · USB', '')
    add('<rect x="120" y="476" width="12" height="18" rx="2" fill="#adb5bd" stroke="#343a40"/>')
    text(80, 560, 'USB: 5 V + data', 'small', 'start', rot=-90)

    # low-current buses: GND (y 290) and 3V3 (y 306) from the Pico to the ADS1115
    AX, AY = 600, 196          # ADS module top-left
    GY, VY = 290, 306
    px, _ = top(38); wire([(px, 430), (px, GY), (AX, GY)], C['GND'], LO)
    px, _ = top(36); wire([(px, 430), (px, VY), (AX, VY)], C['V33'], LO)

    # TA2 leak sensor between the buses and the Pico
    xs = hterm(214, 384, 3)
    text(232, 412, 'TA2 · leak', 'ref', 'middle')
    wire([(xs[0], 374), (xs[0], VY)], C['V33'], LO); dot(xs[0], VY)
    wire([(xs[1], 374), (xs[1], GY)], C['GND'], LO); dot(xs[1], GY)
    px, _ = top(31); wire([(px, 430), (px, 404), (xs[2], 404), (xs[2], 396)], C['LEAK'], LO)
    leak_sensor(150, 214, 'leak sensor → box low point')
    add(f'<path d="M{xs[1]},374 Q{xs[1] - 40},300 196,236" fill="none" stroke="#c92a2a" stroke-width="3"/>')

    # I2C to the ADS1115 (GP21 SCL, GP20 SDA)
    SCLY, SDAY = 336, 352
    px, _ = top(27); wire([(px, 430), (px, SCLY), (AX, SCLY)], C['I2C'], LO)
    px, _ = top(26); wire([(px, 430), (px, SDAY), (AX, SDAY)], C['I2C'], LO)

    # PWM: thruster + pump from the top pins, servos from the bottom pins
    HY = 770                     # terminal row
    RG, RV = 700, 724            # GND rail, 7.4 V rail
    tb2 = hterm(520, HY, 6)
    tb3 = hterm(644, HY, 6)
    tb4 = hterm(768, HY, 2)
    tb5 = hterm(820, HY, 2)
    PY, TY = 380, 392
    px, _ = top(25); wire([(px, 430), (px, PY), (tb5[0], PY), (tb5[0], HY - 10)], C['PUMP'], LO)
    resistor(470, PY, 36)
    px, _ = top(21); wire([(px, 430), (px, TY), (tb4[0], TY), (tb4[0], HY - 10)], C['THR'], LO)
    resistor(530, TY, 36)
    text(530, TY + 18, 'R6 (pump) · R5 (thruster) · 220 Ω', 'small', 'middle')
    servo = [(16, 634, tb2[0], 'M4'), (17, 616, tb2[3], 'M5'), (19, 598, tb3[0], 'M6'), (20, 580, tb3[3], 'M7')]
    for pin, y, xt, nm in servo:
        px, py = bot(pin)
        wire([(px, py), (px, y), (xt, y), (xt, HY - 10)], C['SERVO'], LO)
        resistor(420, y, 36)
        text(xt + 4, y - 4, nm, 'net', 'start')
    text(438, 570, 'R1–R4 · 220 Ω', 'small', 'middle')
    text(tb4[0] + 4, TY + 14, 'THR', 'net', 'start'); text(tb5[0] + 4, PY + 14, 'PUMP', 'net', 'start')

    # rails
    add(f'<rect x="160" y="{RG - 4}" width="{990 - 160}" height="8" rx="4" fill="{C["GND"]}"/>')
    add(f'<rect x="470" y="{RV - 4}" width="{990 - 470}" height="8" rx="4" fill="{C["V75"]}"/>')
    text(466, RV + 4, '7.4 V', 'small', 'end')
    text(214, RG - 8, 'GND rail · 14 AWG soldered along the strip', 'net', 'start')
    px, py = bot(3); wire([(px, py), (px, RG)], C['GND'], LO); dot(px, RG)
    for t in (tb2, tb3):
        for k in (1, 4):
            wire([(t[k], HY - 10), (t[k], RV)], C['V75'], HI); dot(t[k], RV, C['V75'])
        for k in (2, 5):
            wire([(t[k], HY - 10), (t[k], RG)], C['GND'], HI); dot(t[k], RG)
    for xg in (tb4[1], tb5[1]):
        wire([(xg, HY - 10), (xg, RG)], C['GND'], LO); dot(xg, RG)
    # 10 k pull-downs R13 (THR) / R14 (PUMP) to the GND rail
    for xs_, y, ref in ((tb4[0], 652, 'R13'), (tb5[0], 672, 'R14')):
        dot(xs_, y)
        wire([(xs_, y), (xs_ + 8, y)], C['GND'], LO)
        resistor(xs_ + 8, y, 30)
        wire([(xs_ + 38, y), (xs_ + 44, y), (xs_ + 44, RG)], C['GND'], LO); dot(xs_ + 44, RG)
        text(xs_ + 23, y - 9, f'{ref} 10k', 'net', 'middle')
    for lab, xx in (('TB2 rudder M4 · M5', tb2[0]), ('TB3 elevator M6 · M7', tb3[0]), ('TB4', tb4[0]), ('TB5', tb5[0])):
        text(xx - 9, HY - 17, lab, 'net', 'start')
    add(f'<rect x="486" y="{RG + 5}" width="20" height="{RV - RG - 10}" rx="4" fill="#364fc7" stroke="#1c2a7a"/>')
    text(496, RV + 22, 'C1', 'ref', 'middle')
    TB7X = 958
    add(f'<rect x="{TB7X}" y="{RG - 18}" width="22" height="{RV - RG + 36}" rx="3" fill="#1864ab" stroke="#0b2e4f" stroke-width="1.4"/>')
    for yy in (RG - 6, RG + 6, RV - 6, RV + 6):
        add(f'<circle cx="{TB7X + 11}" cy="{yy}" r="5" fill="#ced4da" stroke="#495057"/>')
    text(TB7X + 11, RV + 36, 'TB7', 'ref', 'middle')

    # ---------------------------------------------------------------- battery monitor
    ads(AX, AY)
    for yy, t in ((GY, 'GND'), (VY, 'VDD'), (SCLY, 'SCL'), (SDAY, 'SDA')):
        text(AX + 6, yy + 3, t, 'pinw', 'start')
    J3X = 930
    rows = [(214, 'A0', '47k', 'cell 1'), (254, 'A1', '200k', 'cell 2'), (294, 'A2', '330k', 'pack +')]
    vterm(J3X, [176] + [r[0] for r in rows], [1, 2, 3, 4])
    text(J3X + 20, 156, 'J3 · balance in', 'ref', 'middle')
    wire([(J3X, 176), (J3X - 26, 176)], C['GND'], LO); gnd_sym(J3X - 26, 182)
    for y, a, rt, lab in rows:
        text(AX + 98, y + 3, a, 'pinw', 'end')
        wire([(AX + 104, y), (J3X, y)], C['BAL'], LO)
        resistor(850, y, 36)
        nx = 812
        dot(nx, y); vres(nx, y + 4, 20); gnd_sym(nx, y + 30)
        dot(786, y); add(f'<line x1="786" y1="{y}" x2="786" y2="{y + 10}" stroke="{C["BAL"]}" stroke-width="2.2"/>')
        vcap(786, y + 11); add(f'<line x1="786" y1="{y + 16}" x2="786" y2="{y + 22}" stroke="#1c1c1c" stroke-width="1.6"/>')
        gnd_sym(786, y + 26)
        text(868, y - 9, rt, 'net', 'middle')
    text(812, 336, '100k', 'net', 'middle'); text(786, 348, '100 nF', 'net', 'middle')
    text(J3X + 40, 322, '1 GND · 2 cell 1 · 3 cell 2 · 4 pack +', 'small', 'end')

    # ================================================================ POWER (off-board, in the box)
    text(1030, 140, 'Power, off-board in the box', 'refw', 'start')
    battery(1470, 196)
    # balance lead to J3 (4 thin wires)
    for i, (yj, col) in enumerate(((176, C['GND']), (214, C['BAL']), (254, C['BAL']), (294, C['BAL']))):
        xb = 1470
        yb = 206 + i * 6
        wire([(xb, yb), (1420 - i * 8, yb), (1420 - i * 8, 196 - (3 - i) * 6), (1040 + i * 8, 196 - (3 - i) * 6),
              (1040 + i * 8, yj), (J3X + 40, yj)], col, 1.6)
    text(1300, 168, 'balance lead (JST-XH 4) · unplug for storage', 'small', 'middle')
    # main leads: battery -> EC5 -> F1 -> SW1 -> +12 V bar ; battery - -> EC5 -> GND bar
    ec5(1410, 238)
    wire([(1470, 238), (1452, 238)], C['VBAT'], HI)
    wire([(1470, 260), (1452, 260)], C['GND'], HI)
    fuse(1335, 238)
    killswitch(1205, 238)
    wire([(1410, 238), (1361, 238)], C['VBAT'], HI)
    wire([(1309, 238), (1227, 238)], C['VBAT'], HI)
    wire([(1183, 238), (1120, 238), (1120, 366)], C['VBAT'], HI)
    wire([(1410, 260), (1400, 260), (1400, 330)], C['GND'], HI)
    GB, PB = 330, 366
    busbar([1212, 1302, 1400, 1482], GB, '#1c1c1c', 'GND', left_label=False)
    busbar([1120, 1200, 1290, 1470], PB, '#c92a2a', '+12 V', left_label=True)
    text(1512, 384, 'OONO 2×6 bus bar', 'small', 'start'); text(1512, 397, '30 A total · one row per pole', 'small', 'start')
    for x in (1212, 1302, 1400, 1482):
        dot(x, GB)
    # buck U1 -> TB7
    buck(1090, 560)
    wire([(1200, PB + 6), (1200, 560)], C['VBAT'], HI)
    wire([(1212, GB + 6), (1212, 560)], C['GND'], HI)
    wire([(1090, 584), (1070, 584), (1070, RV - 6), (TB7X + 22, RV - 6)], C['V75'], HI)
    wire([(1090, 594), (1060, 594), (1060, RV + 6), (TB7X + 22, RV + 6)], C['V75'], HI)
    wire([(1090, 620), (1050, 620), (1050, RG + 6), (TB7X + 22, RG + 6)], C['GND'], HI)
    wire([(1090, 610), (1040, 610), (1040, RG - 6), (TB7X + 22, RG - 6)], C['GND'], HI)
    text(1155, 668, 'set to 7.4 V', 'small', 'middle')
    # pump ESC U3 and thruster ESC U2 (both inside)
    esc_box(1260, 470, 130, 58, 'U3 · Pump ESC', 'reversible · BEC cut')
    wire([(1290, PB + 6), (1290, 470)], C['VBAT'], HI)
    wire([(1302, GB + 6), (1302, 470)], C['GND'], HI)
    esc_box(1440, 470, 150, 58, 'U2 · TD1.2 ESC', 'inside the box · no BEC')
    wire([(1470, PB + 6), (1470, 470)], C['VBAT'], HI)
    wire([(1482, GB + 6), (1482, 470)], C['GND'], HI)
    # ESC signals from TB4 / TB5 (below the board)
    wire([(tb5[0], HY + 12), (tb5[0], 832), (1320, 832), (1320, 528)], C['PUMP'], LO)
    wire([(tb5[1], HY + 12), (tb5[1], 840), (1332, 840), (1332, 528)], C['GND'], LO)
    wire([(tb4[0], HY + 12), (tb4[0], 852), (1500, 852), (1500, 528)], C['THR'], LO)
    wire([(tb4[1], HY + 12), (tb4[1], 860), (1512, 860), (1512, 528)], C['SIGG'], LO)
    text(1150, 826, 'pump ESC signal (TB5)', 'net', 'middle')
    text(1150, 872, 'thruster ESC signal (TB4) · yellow PWM, white signal GND', 'net', 'middle')
    # ESC outputs to glands
    wire([(1390, 488), (1410, 488), (1410, 868)], C['MOT'], HI)
    wire([(1390, 506), (1420, 506), (1420, 868)], C['MOT'], HI)
    for k, yy in enumerate((484, 499, 514)):
        wire([(1590, yy), (1596 + k * 8, yy), (1596 + k * 8, 868)], '#868e96', 3.2)
    text(1640, 560, 'U · V · W', 'small', 'middle', rot=90)

    # ---------------------------------------------------------------- glands in the bottom wall
    gland(600, 880, 'G4', 'servo leads, epoxy-potted', potted=True)
    gland(1415, 880, 'G3', 'pump 2-core', anchor='end')
    gland(1604, 880, 'G2', 'thruster', anchor='end')
    # servo leads from TB2 / TB3 down to G4
    scol = (C['SERVO'], C['V75'], C['GND'])
    for j, (t, k0) in enumerate(((tb2, 0), (tb2, 3), (tb3, 0), (tb3, 3))):
        for k in range(3):
            xe = 590 + j * 6 + k * 1.8
            d = f'M{t[k0 + k]},{HY + 12} C{t[k0 + k]},{HY + 60} {xe},{HY + 50} {xe},868'
            add(f'<path class="halo" d="{d}" stroke-width="7.8"/>')
            add(f'<path class="wo" d="{d}" stroke-width="3.6"/>')
            add(f'<path d="{d}" fill="none" stroke="{scol[k]}" stroke-width="1.8" stroke-linecap="round"/>')
    text(560, 846, 'servo leads', 'net', 'end')

    # ================================================================ WET ZONE
    for j, (s, role) in enumerate((('M4', 'rudder'), ('M5', 'rudder'), ('M6', 'elevator'), ('M7', 'elevator'))):
        xs_ = 592 + j * 6
        sy = 964 + j * 64
        cable([(xs_, 892), (xs_, sy + 17), (760, sy + 17)], w=5, color='#212529')
        add(f'<rect x="{690 - 12}" y="{sy + 9}" width="24" height="16" rx="3" fill="none" stroke="#2f9e44" stroke-width="1.6" stroke-dasharray="3 2"/>')
        servo_icon(768, sy, f'{s} · {role}')
    text(690, 952, 'backup only', 'small', 'middle')
    text(700, 1226, 'Factory servo leads run uncut into the box through G4 and land on TB2 / TB3.', 'small', 'middle')
    text(700, 1213, 'Backup (dashed): one MGYOO 20 AWG 3-pin waterproof plug per servo, only if a lead can’t reach.', 'small', 'middle')

    # thruster: factory phase cable through G2
    cable([(1604, 892), (1604, 940), (1560, 940), (1560, 964)], w=8, color='#1c1c1c')
    thruster(1570, 1000)
    text(1450, 1066, 'factory phase cable · slide the gland on first', 'small', 'middle')

    # pump: G3 -> 2-core round cable -> D2 -> pump drybox
    D2 = (1250, 1110)
    hcable([(1415, 892), (1415, 1000), (1170, 1000), (1170, D2[1]), (D2[0] - 46, D2[1])], 'hi', r=12)
    ctag(1290, 1000, 'pump · 14/2 round cable')
    dt(D2[0], D2[1], 'D2 · pump DTP 4-pin', '1 pump + · 2 pump −', '3–4 dummy loop')
    add('<rect x="1330" y="1078" width="320" height="110" rx="12" fill="#e7f5ff" stroke="#1971c2" stroke-width="2" stroke-dasharray="7 5"/>')
    text(1342, 1098, 'PUMP DRYBOX (or sealed pump)', 'refw', 'start')
    wire([(D2[0] + 44, 1104), (1430, 1104), (1430, 1136), (1446, 1136)], C['MOT'], HI)
    wire([(D2[0] + 44, 1116), (1420, 1116), (1420, 1148), (1446, 1148)], C['MOT'], HI)
    motor(1480, 1142, 'M3 · ballast pump')
    text(1560, 1134, '12 V brushed,', 'small', 'start')
    text(1560, 1147, 'reversible', 'small', 'start')

    # notes in the wet zone
    text(34, 990, 'Glands (M16 × 1.5) seal ONE round cable each.', 'small', 'start')
    text(34, 1004, 'G1 USB · G2 thruster phases · G3 pump 2-core.', 'small', 'start')
    text(34, 1018, 'G4: four flat servo leads can’t seal → pull the', 'small', 'start')
    text(34, 1032, 'rubber insert and fill the gland body with epoxy.', 'small', 'start')
    text(34, 1054, 'IP67 = 1 m for 30 min. Vacuum-test before every dive.', 'small', 'start')
    text(34, 1076, 'No 12 V supply leaves the box: only the pump', 'small', 'start')
    text(34, 1090, 'motor pair and the thruster phase wires.', 'small', 'start')
    add('</svg>')
    return '\n'.join(P.out)


if __name__ == '__main__':
    import sys
    open(sys.argv[1], 'w').write(build())
