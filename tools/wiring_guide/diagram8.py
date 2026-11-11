"""AA-TV wiring diagram v10 (draft): v9 single IP67 box, but the ballast is a 24 V one-way bilge pump
(Rule 28D, water OUT) + a normally-closed solenoid valve (water IN), both switched by MOSFETs.
build() -> svg string. Helpers reused from diagram7 / prims."""
import prims as P
from prims import add, wire, cable, text, dot, perfboard, resistor, esc_box, servo_icon, \
    thruster, leak_sensor, pico, pin_name
import diagram7 as D7
from diagram7 import gland, busbar, hterm, vterm, vres, vcap, gnd_sym, battery, fuse, killswitch, ec5, buck

HI, LO = 5.0, 2.6
C = dict(D7.C)
C['V24'] = '#a61e4d'       # 24 V rail (maroon)
C['VALVE'] = '#8d5524'     # valve enable (brown)
W, H = 1700, 1250


def ads(x, y, w=104, h=168):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#5f3dc4" stroke="#2b1a6b" stroke-width="2"/>')
    add(f'<rect x="{x + 34}" y="{y + 60}" width="36" height="36" rx="3" fill="#212529"/>')
    text(x + w / 2, y + 82, 'ADS1115', 'devs', 'middle', size=8)
    text(x + w / 2, y - 10, 'U4 · ADS1115 breakout', 'ref', 'middle')


def vfuse(cx, cy, label, amps, color='#f8f9fa', anchor='end'):
    add(f'<rect x="{cx - 11}" y="{cy - 24}" width="22" height="48" rx="9" fill="#212529" stroke="#000"/>')
    add(f'<rect x="{cx - 8}" y="{cy - 9}" width="16" height="18" rx="2" fill="{color}" stroke="#333"/>')
    text(cx, cy + 3.5, amps, 'devd', 'middle', size=8)
    tx = cx - 16 if anchor == 'end' else cx + 16
    text(tx, cy + 4, label, 'ref', anchor)


def boost(x, y, w=90, h=58):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#adb5bd" stroke="#495057" stroke-width="2"/>')
    for k in range(5):
        add(f'<rect x="{x + 9 + k * 16}" y="{y + 6}" width="8" height="{h - 12}" rx="2" fill="#868e96"/>')
    text(x + w + 6, y + 20, 'U5 · Boost', 'ref', 'start')
    text(x + w + 6, y + 34, '12 → 24 V · 3 A', 'small', 'start')
    text(x + w + 6, y + 47, 'IP68', 'small', 'start')


def mosfet(cx, cy, ref):
    """TO-220 N-MOSFET icon: body + tab. Pins G (left), D, S (bottom)."""
    add(f'<rect x="{cx - 13}" y="{cy - 20}" width="26" height="8" rx="2" fill="#adb5bd" stroke="#495057"/>')
    add(f'<rect x="{cx - 13}" y="{cy - 13}" width="26" height="26" rx="2" fill="#212529" stroke="#000"/>')
    for dx in (-8, 0, 8):
        add(f'<rect x="{cx + dx - 1.5}" y="{cy + 13}" width="3" height="10" fill="#ced4da"/>')
    text(cx, cy + 4, ref, 'devw', 'middle', size=9)


def diode(cx, cy):
    add(f'<rect x="{cx - 4}" y="{cy - 9}" width="8" height="18" rx="2" fill="#212529"/>')
    add(f'<rect x="{cx - 4}" y="{cy - 9}" width="8" height="4" fill="#dee2e6"/>')


def switchboard(x, y, w=140, h=100):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="url(#holes)" stroke="#b39d6b" stroke-width="2"/>')
    text(x + 8, y + 15, 'U6 · switch board', 'board', 'start', size=12)
    mosfet(x + 40, y + 50, 'Q1')
    mosfet(x + 92, y + 50, 'Q2')
    diode(x + 62, y + 48); diode(x + 114, y + 48)
    text(x + 40, y + 92, 'pump', 'net', 'middle'); text(x + 92, y + 92, 'valve', 'net', 'middle')


def bilge_pump(cx, cy):
    add(f'<rect x="{cx - 30}" y="{cy - 44}" width="60" height="70" rx="10" fill="#c92a2a" stroke="#5c0f0f" stroke-width="2"/>')
    add(f'<rect x="{cx - 34}" y="{cy + 22}" width="68" height="16" rx="5" fill="#212529"/>')
    add(f'<rect x="{cx + 30}" y="{cy - 30}" width="40" height="18" rx="4" fill="#f1f3f5" stroke="#868e96" stroke-width="1.5"/>')
    text(cx, cy - 10, 'rule', 'devw', 'middle', size=12)
    text(cx, cy + 6, '24 V', 'devw', 'middle', size=10)
    text(cx, cy + 56, 'M3 · bilge pump (Rule 28D)', 'dev', 'middle')
    text(cx, cy + 70, '24 V · 1.4 A · one-way: water OUT', 'small', 'middle')


def valve(cx, cy):
    add(f'<rect x="{cx - 44}" y="{cy + 2}" width="88" height="22" rx="4" fill="#e9c46a" stroke="#8a6d1d" stroke-width="2"/>')
    add(f'<rect x="{cx - 22}" y="{cy - 38}" width="44" height="40" rx="5" fill="#343a40" stroke="#11161b" stroke-width="2"/>')
    add(f'<rect x="{cx - 52}" y="{cy + 6}" width="10" height="14" rx="2" fill="#c9a227"/>')
    add(f'<rect x="{cx + 42}" y="{cy + 6}" width="10" height="14" rx="2" fill="#c9a227"/>')
    text(cx, cy - 15, 'NC', 'devw', 'middle', size=11)
    text(cx, cy + 46, 'SV1 · solenoid valve', 'dev', 'middle')
    text(cx, cy + 60, 'normally closed · direct-acting · water IN', 'small', 'middle')


def legend(x, y):
    items = [(C['VBAT'], '12 V'), (C['V24'], '24 V'), (C['GND'], 'GND'), (C['V75'], '7.4 V'), (C['V33'], '3.3 V'),
             (C['SERVO'], 'servo PWM'), (C['THR'], 'thruster PWM'), (C['PUMP'], 'pump on/off'),
             (C['VALVE'], 'valve on/off'), (C['I2C'], 'I2C'), (C['BAL'], 'balance'), (C['LEAK'], 'leak'), (C['MOT'], 'switched load −')]
    xx = x
    for col, t in items:
        add(f'<rect x="{xx}" y="{y - 5}" width="18" height="10" rx="3" fill="{col}" stroke="#11161b" stroke-width="1"/>')
        text(xx + 23, y + 4, t, 'small', 'start')
        xx += 30 + len(t) * 6.2


def build():
    P.out.clear()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" class="diagram" aria-label="AA-TV wiring diagram v10 draft">')
    add('<defs><pattern id="holes" width="10" height="10" patternUnits="userSpaceOnUse">'
        '<rect width="10" height="10" fill="#efe4c4"/><circle cx="5" cy="5" r="1.5" fill="#c8b48a"/></pattern>'
        '<pattern id="water" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">'
        '<line x1="0" y1="7" x2="14" y2="7" class="waterline"/></pattern>'
        '<pattern id="epoxy" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#ffd8a8"/>'
        '<circle cx="2" cy="2" r="1" fill="#e8590c" opacity=".5"/></pattern></defs>')
    add(f'<rect width="{W}" height="{H}" class="panel"/>')

    # zones
    add('<rect x="14" y="904" width="1672" height="332" rx="16" fill="url(#water)" class="wetzone"/>')
    text(34, 934, 'WET ZONE', 'zone')
    text(34, 952, 'flooded hull = ballast · servos, thruster, bilge pump, valve', 'zones', size=12)
    add('<rect x="30" y="112" width="1640" height="768" rx="16" class="drybox"/>')
    text(130, 140, 'MAIN BOX', 'zone')
    text(130, 158, 'IP67 · 191 × 111 × 58 mm inside · the only drybox · 4 × M16 glands', 'zones', size=12)
    text(420, 30, 'AA-TV wiring v10 (draft) · 24 V bilge pump out + solenoid valve in, both MOSFET-switched', 'refw', 'start', size=15)
    legend(420, 58)

    # buoy
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

    AX, AY = 600, 196
    GY, VY = 290, 306
    px, _ = top(38); wire([(px, 430), (px, GY), (AX, GY)], C['GND'], LO)
    px, _ = top(36); wire([(px, 430), (px, VY), (AX, VY)], C['V33'], LO)
    xs = hterm(214, 384, 3)
    text(232, 412, 'TA2 · leak', 'ref', 'middle')
    wire([(xs[0], 374), (xs[0], VY)], C['V33'], LO); dot(xs[0], VY)
    wire([(xs[1], 374), (xs[1], GY)], C['GND'], LO); dot(xs[1], GY)
    px, _ = top(31); wire([(px, 430), (px, 404), (xs[2], 404), (xs[2], 396)], C['LEAK'], LO)
    leak_sensor(150, 214, 'leak sensor → box low point')
    add(f'<path d="M{xs[1]},374 Q{xs[1] - 40},300 196,236" fill="none" stroke="#c92a2a" stroke-width="3"/>')
    SCLY, SDAY = 336, 352
    px, _ = top(27); wire([(px, 430), (px, SCLY), (AX, SCLY)], C['I2C'], LO)
    px, _ = top(26); wire([(px, 430), (px, SDAY), (AX, SDAY)], C['I2C'], LO)

    # PWM / enables: pump (GP19) highest, valve (GP18), thruster (GP16)
    HY = 770
    RG, RV = 700, 724
    tb2 = hterm(520, HY, 6)
    tb3 = hterm(644, HY, 6)
    tb4 = hterm(768, HY, 2)      # thruster ESC signal
    tb8 = hterm(820, HY, 2)      # valve enable
    tb5 = hterm(872, HY, 2)      # pump enable
    PY, VLY, TY = 376, 386, 396
    px, _ = top(25); wire([(px, 430), (px, PY), (tb5[0], PY), (tb5[0], HY - 10)], C['PUMP'], LO)
    resistor(470, PY, 36)
    px, _ = top(24); wire([(px, 430), (px, VLY), (tb8[0], VLY), (tb8[0], HY - 10)], C['VALVE'], LO)
    resistor(520, VLY, 36)
    px, _ = top(21); wire([(px, 430), (px, TY), (tb4[0], TY), (tb4[0], HY - 10)], C['THR'], LO)
    resistor(570, TY, 36)
    text(540, TY + 18, 'R6 pump · R17 valve · R5 thruster · 220 Ω', 'small', 'middle')
    servo = [(16, 634, tb2[0], 'M4'), (17, 616, tb2[3], 'M5'), (19, 598, tb3[0], 'M6'), (20, 580, tb3[3], 'M7')]
    for pin, y, xt, nm in servo:
        px, py = bot(pin)
        wire([(px, py), (px, y), (xt, y), (xt, HY - 10)], C['SERVO'], LO)
        resistor(420, y, 36)
        text(xt + 4, y - 4, nm, 'net', 'start')
    text(438, 570, 'R1–R4 · 220 Ω', 'small', 'middle')
    text(tb4[0] + 4, TY + 14, 'THR', 'net', 'start')
    text(tb8[0] + 4, VLY + 14, 'VALVE', 'net', 'start')
    text(tb5[0] + 4, PY + 14, 'PUMP', 'net', 'start')

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
    for xg in (tb4[1], tb8[1], tb5[1]):
        wire([(xg, HY - 10), (xg, RG)], C['GND'], LO); dot(xg, RG)
    # R13 thruster pull-down (left of TB4)
    dot(tb4[0], 652)
    wire([(tb4[0], 652), (tb4[0] - 8, 652)], C['GND'], LO)
    resistor(tb4[0] - 38, 652, 30)
    wire([(tb4[0] - 38, 652), (tb4[0] - 46, 652), (tb4[0] - 46, RG)], C['GND'], LO); dot(tb4[0] - 46, RG)
    text(tb4[0] - 23, 643, 'R13 10k', 'net', 'middle')
    for lab, xx in (('TB2 rudder M4 · M5', tb2[0]), ('TB3 elevator M6 · M7', tb3[0]), ('TB4', tb4[0]), ('TB8', tb8[0]), ('TB5', tb5[0])):
        text(xx - 9, HY - 17, lab, 'net', 'start')
    add(f'<rect x="486" y="{RG + 5}" width="20" height="{RV - RG - 10}" rx="4" fill="#364fc7" stroke="#1c2a7a"/>')
    text(496, RV + 22, 'C1', 'ref', 'middle')
    TB7X = 958
    add(f'<rect x="{TB7X}" y="{RG - 18}" width="22" height="{RV - RG + 36}" rx="3" fill="#1864ab" stroke="#0b2e4f" stroke-width="1.4"/>')
    for yy in (RG - 6, RG + 6, RV - 6, RV + 6):
        add(f'<circle cx="{TB7X + 11}" cy="{yy}" r="5" fill="#ced4da" stroke="#495057"/>')
    text(TB7X + 11, RV + 36, 'TB7', 'ref', 'middle')

    # battery monitor (unchanged from v9)
    ads(AX, AY)
    for yy, t in ((GY, 'GND'), (VY, 'VDD'), (SCLY, 'SCL'), (SDAY, 'SDA')):
        text(AX + 6, yy + 3, t, 'pinw', 'start')
    J3X = 930
    rows = [(214, 'A0', '47k'), (254, 'A1', '200k'), (294, 'A2', '330k')]
    vterm(J3X, [176] + [r[0] for r in rows], [1, 2, 3, 4])
    text(J3X + 20, 156, 'J3 · balance in', 'ref', 'middle')
    wire([(J3X, 176), (J3X - 26, 176)], C['GND'], LO); gnd_sym(J3X - 26, 182)
    for y, a, rt in rows:
        text(AX + 98, y + 3, a, 'pinw', 'end')
        wire([(AX + 104, y), (J3X, y)], C['BAL'], LO)
        resistor(850, y, 36)
        dot(812, y); vres(812, y + 4, 20); gnd_sym(812, y + 30)
        dot(786, y); add(f'<line x1="786" y1="{y}" x2="786" y2="{y + 10}" stroke="{C["BAL"]}" stroke-width="2.2"/>')
        vcap(786, y + 11); add(f'<line x1="786" y1="{y + 16}" x2="786" y2="{y + 22}" stroke="#1c1c1c" stroke-width="1.6"/>')
        gnd_sym(786, y + 26)
        text(868, y - 9, rt, 'net', 'middle')
    text(812, 336, '100k', 'net', 'middle'); text(786, 348, '100 nF', 'net', 'middle')
    text(J3X + 40, 322, '1 GND · 2 cell 1 · 3 cell 2 · 4 pack +', 'small', 'end')

    # ================================================================ POWER
    text(1030, 140, 'Power, off-board in the box', 'refw', 'start')
    battery(1470, 196)
    for i, (yj, col) in enumerate(((176, C['GND']), (214, C['BAL']), (254, C['BAL']), (294, C['BAL']))):
        yb = 206 + i * 6
        wire([(1470, yb), (1420 - i * 8, yb), (1420 - i * 8, 196 - (3 - i) * 6), (1040 + i * 8, 196 - (3 - i) * 6),
              (1040 + i * 8, yj), (J3X + 40, yj)], col, 1.6)
    text(1300, 168, 'balance lead (JST-XH 4) · unplug for storage', 'small', 'middle')
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
    gnd_studs = [1212, 1232, 1302, 1400, 1482]
    busbar(gnd_studs, GB, '#1c1c1c', 'GND', left_label=False)
    busbar([1120, 1200, 1290, 1470], PB, '#c92a2a', '+12 V', left_label=True)
    text(1530, 384, 'OONO 2×6 bus bar', 'small', 'start'); text(1530, 397, '30 A total', 'small', 'start')
    for x in gnd_studs:
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
    # boost U5 -> F2 (pump) + F3 (valve) -> U6 switch board
    boost(1260, 470)
    wire([(1290, PB + 6), (1290, 470)], C['VBAT'], HI)
    wire([(1302, GB + 6), (1302, 470)], C['GND'], HI)
    wire([(1320, 528), (1320, 576)], C['V24'], HI)
    wire([(1320, 552), (1350, 552), (1350, 576)], C['V24'], HI); dot(1320, 552, C['V24'])
    vfuse(1320, 600, '', '2.5')
    vfuse(1350, 600, '', '1', anchor='start')
    text(1366, 594, 'F2 · 2.5 A (pump)', 'ref', 'start'); text(1366, 609, 'F3 · valve fuse', 'small', 'start')
    wire([(1320, 624), (1320, 740), (1240, 740)], C['V24'], HI)
    wire([(1350, 624), (1350, 760), (1240, 760)], C['V24'], HI)
    SBX, SBY = 1100, 700
    switchboard(SBX, SBY)
    wire([(1232, SBY), (1232, GB + 6)], C['GND'], HI)
    text(1236, 690, 'GND', 'net', 'start')
    # outputs to G3 (pump +/−, valve +/−)
    GX3 = 1275
    for k, (yy, col) in enumerate(((776, C['V24']), (782, C['MOT']), (788, C['V24']), (794, C['MOT']))):
        wire([(SBX + 140, yy), (GX3 - 9 + k * 6, yy), (GX3 - 9 + k * 6, 868)], col, 2.6)
    # pump / valve enable from TB5 / TB8, thruster signal from TB4
    wire([(tb5[0], HY + 12), (tb5[0], 824), (SBX + 48, 824), (SBX + 48, SBY + 100)], C['PUMP'], LO)
    wire([(tb5[1], HY + 12), (tb5[1], 816), (SBX + 40, 816), (SBX + 40, SBY + 100)], C['GND'], LO)
    wire([(tb8[0], HY + 12), (tb8[0], 844), (SBX + 106, 844), (SBX + 106, SBY + 100)], C['VALVE'], LO)
    wire([(tb8[1], HY + 12), (tb8[1], 836), (SBX + 98, 836), (SBX + 98, SBY + 100)], C['GND'], LO)
    text(1000, 812, 'pump enable (TB5)', 'net', 'middle')
    text(1000, 832, 'valve enable (TB8)', 'net', 'middle')
    wire([(tb4[0], HY + 12), (tb4[0], 852), (1500, 852), (1500, 528)], C['THR'], LO)
    wire([(tb4[1], HY + 12), (tb4[1], 860), (1512, 860), (1512, 528)], C['SIGG'], LO)
    text(1400, 846, 'thruster ESC signal (TB4)', 'net', 'middle')
    # thruster ESC U2
    esc_box(1440, 470, 150, 58, 'U2 · TD1.2 ESC', 'inside the box · no BEC')
    wire([(1470, PB + 6), (1470, 470)], C['VBAT'], HI)
    wire([(1482, GB + 6), (1482, 470)], C['GND'], HI)
    for k, yy in enumerate((484, 499, 514)):
        wire([(1590, yy), (1596 + k * 8, yy), (1596 + k * 8, 868)], '#868e96', 3.2)
    text(1640, 560, 'U · V · W', 'small', 'middle', rot=90)
    # switch-board notes

    # glands
    gland(600, 880, 'G4', 'servo leads, epoxy-potted', potted=True)
    gland(GX3, 880, 'G3', 'pump + valve leads, potted', potted=True)
    gland(1604, 880, 'G2', 'thruster', anchor='end')
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
    # thruster
    cable([(1604, 892), (1604, 940), (1560, 940), (1560, 964)], w=8, color='#1c1c1c')
    thruster(1570, 1000)
    text(1500, 1066, 'factory phase cable · slide the gland on first', 'small', 'middle')
    # pump + valve from G3 (factory leads)
    cable([(GX3 - 6, 892), (GX3 - 6, 990), (1180, 990), (1180, 1046)], w=6, color='#5c2b0e')
    cable([(GX3 + 6, 892), (GX3 + 6, 990), (1380, 990), (1380, 1080)], w=6, color='#212529')
    text(1180, 980, 'pump leads (brown +, black −)', 'small', 'middle')
    text(1390, 980, 'valve leads', 'small', 'middle')
    bilge_pump(1180, 1090)
    text(1258, 1066, '→ out', 'refw', 'start')
    valve(1380, 1120)

    # notes
    text(34, 990, 'Glands (M16 × 1.5) seal ONE round cable each.', 'small', 'start')
    text(34, 1004, 'G1 USB · G2 thruster phases.', 'small', 'start')
    text(34, 1018, 'G3 and G4 carry several flat leads → pull the', 'small', 'start')
    text(34, 1032, 'rubber insert and fill the gland body with epoxy.', 'small', 'start')
    text(34, 1054, 'IP67 = 1 m for 30 min. Vacuum-test before every dive.', 'small', 'start')
    text(34, 1076, 'Ballast: valve opens → water IN; pump on → water OUT.', 'small', 'start')
    text(34, 1090, 'Power lost → valve closes and pump stops.', 'small', 'start')
    text(34, 1112, 'U6 switch board: Q1 / Q2 logic-level N-MOSFETs (low side),', 'small', 'start')
    text(34, 1126, 'D3 / D4 flyback diodes across pump and valve, 10 k gate', 'small', 'start')
    text(34, 1140, 'pull-downs R14 / R18. 12 V / 24 V never touch the main board.', 'small', 'start')
    text(34, 1162, 'No Deutsch connectors left: pump, valve and servo leads', 'small', 'start')
    text(34, 1176, 'run uncut into potted glands G3 / G4.', 'small', 'start')
    add('</svg>')
    return '\n'.join(P.out)


if __name__ == '__main__':
    import sys
    open(sys.argv[1], 'w').write(build())
