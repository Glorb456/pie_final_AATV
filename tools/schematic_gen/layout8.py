"""AA-TV v11 schematic: thruster with built-in ESC, 24 V bilge pump + solenoid valve on
MOSFET switches, sealed ballast tank, battery-monitor dividers from the resistors on hand.
usage: python3 layout8.py out.kicad_sch [out.kicad_sym]
Does not touch the v9 files. Same helpers as layout7.py (gen.py, libs.py, custom.py).
"""
import sys
import gen
import custom
from custom import sym, _rect, _text, _pin, _poly, _circle
from gen import *

OUT = sys.argv[1]
gen.PROJECT = 'AATV_v11'
NOTE = 1.27
TITLE_SZ = 2.54

# ------------------------------------------------------------------ new symbols
custom.CUSTOM['Boost_12V_24V'] = sym(
    'Boost_12V_24V', 'U', '12V->24V boost', [
        _rect(-7.62, 5.08, 7.62, -5.08),
        _text('BOOST', 0, 0, 1.27)],
    [_pin('power_in', -10.16, 2.54, 0, 'VIN+', 1),
     _pin('power_in', -10.16, -2.54, 0, 'VIN-', 2),
     _pin('power_out', 10.16, 2.54, 180, 'VOUT+', 3),
     _pin('passive', 10.16, -2.54, 180, 'VOUT-', 4)],
    desc='12 V to 24 V boost module, 3 A max, non-isolated. Red/black = input, yellow/black = output.',
    refpos=(0, 6.35), valpos=(0, -6.35))

custom.CUSTOM['Thruster_ESC'] = sym(
    'Thruster_ESC', 'MT', 'Thruster with ESC', [
        _rect(-7.62, 6.35, 12.7, -6.35),
        _circle(7.62, 1.905, 2.54),
        _poly([(6.35, 3.175), (8.89, 0.635)]), _poly([(6.35, 0.635), (8.89, 3.175)]),
        _text('BLDC + ESC', 7.62, -3.81, 1.016)],
    [_pin('power_in', -10.16, 3.81, 0, 'BAT+', 1),
     _pin('power_in', -10.16, 1.27, 0, 'BAT-', 2),
     _pin('input', -10.16, -1.27, 0, 'SIG', 3),
     _pin('passive', -10.16, -3.81, 0, 'SIG_GND', 4)],
    desc='Underwater thruster with the ESC built in. Thick pair = battery power, thin pair = PWM signal + signal ground.',
    refpos=(0, 7.62), valpos=(0, -7.62))

custom.CUSTOM['Solenoid_Valve'] = sym(
    'Solenoid_Valve', 'SV', 'Solenoid valve', [
        _rect(-2.54, 2.54, 2.54, -2.54),
        _text('SOL', 0, 0, 1.016),
        _poly([(3.81, 2.54), (3.81, -2.54), (8.89, 2.54), (8.89, -2.54), (3.81, 2.54)]),
        _poly([(2.54, 0), (6.35, 0)])],
    [_pin('passive', 0, 5.08, 270, '+', 1),
     _pin('passive', 0, -5.08, 90, '-', 2)],
    desc='Normally closed, direct-acting solenoid valve (coil shown).',
    hide_pin_names=True, refpos=(0, 7.62), valpos=(0, -7.62))

gen.TITLE.update({
    'title': 'AA-TV electrical v11: 24 V ballast, built-in-ESC thruster',
    'rev': 'v11',
    'date': '2026-11-11',
    'c1': 'One IP67 box: battery, F1, SW1, bus bar, buck, boost, Pico board, switch board.',
    'c2': 'Glands: G1 USB, G2 thruster, G3 pump + valve, G4 servos (G2-G4 potted).',
    'c3': 'High-side kill switch. F1 25 A. Servo rail 7.5 V. 24 V rail from the boost.',
})

# ------------------------------------------------------------------ zones
BUOY = ((10.16, 15.24), (129.54, 160.02))
MAIN = ((167.64, 15.24), (584.2, 266.7))
BOARD = ((175.26, 27.94), (401.32, 259.08))
SWBOARD = ((492.76, 182.88), (581.66, 259.08))
WET = ((10.16, 276.86), (584.2, 372.11))
for z in (BUOY, MAIN):
    rect(*z, width=0.6)
rect(*WET, width=0.6, style='dash_dot')
rect(*BOARD, width=0.35, style='dash')
rect(*SWBOARD, width=0.35, style='dash')

text('AA-TV wiring v11: single IP67 main box, 4x M16 cable glands, thruster with built-in ESC, '
     '24 V bilge pump (water out) + solenoid valve (water in) on MOSFET switches, sealed ballast tank.',
     (12.7, 6.35), 3, bold=True)
text('BUOY  (surface, dry)', (12.7, 17.78), TITLE_SZ, bold=True)
text('TETHER', (134.62, 17.78), TITLE_SZ, bold=True)
text('MAIN BOX  (IP67 ABS, 4x M16 glands; the only drybox)', (170.18, 17.78), TITLE_SZ, bold=True)
text('BOARD: Pico + servo / signal solder-board', (177.8, 30.48), 1.8, bold=True)
text('Power, off-board (in the box)', (406.4, 30.48), 1.8, bold=True)
text('U6: switch board (small perfboard)', (495.3, 185.42), 1.8, bold=True)
text('OUTSIDE THE BOX  (wet): servos, thruster, bilge pump, solenoid valve', (12.7, 279.4), TITLE_SZ, bold=True)

# ================================================================== BUOY (unchanged)
pi = Part('Connector:Raspberry_Pi_4', 'J1', 'Raspberry Pi 4 (buoy)', 68.58, 93.98,
          refpos=(68.58, 59.69), valpos=(68.58, 128.27))
stub(pi, 2, '5V_PI')
stub(pi, 6, 'GND_PI')
for p in PINS[pi.lib_id]:
    if p['num'] not in ('2', '4', '6', '9', '14', '20', '25', '30', '34', '39'):
        nc(pi, p['num'])
bank = Part('Device:Battery', 'BT5', 'USB-C power bank 5 V / 3 A', 25.4, 40.64,
            refpos=(29.21, 39.37), valpos=(29.21, 41.91), just='left')
stub(bank, 1, '5V_PI'); stub(bank, 2, 'GND_PI')
text('Pi 4 talks to the Pico over USB serial\n(/dev/ttyACM0) and powers it from USB 5 V.\n'
     'Reset the Pico by power-cycling the Pi USB\nports (uhubctl).', (12.7, 135.89), NOTE)

# ================================================================== TETHER
line((129.54, 38.1), (167.64, 38.1), 0.4, 'dash')
line((129.54, 53.34), (167.64, 53.34), 0.4, 'dash')
w1 = Part('AATV:USB_Cable', 'W1', 'USB-A to micro-B, 3 m', 142.24, 45.72,
          refpos=(142.24, 35.56), valpos=(142.24, 57.15))
x, y = w1.P(1); wire((x, y), (127.0, y)); label('5V_PI', (127.0, y), 180)
x, y = w1.P(4); wire((x, y), (127.0, y)); label('GND_PI', (127.0, y), 180)
x, y = w1.P(5); wire((x, y), (180.34, y)); label('VBUS_PICO', (180.34, y), 0)
x, y = w1.P(8); wire((x, y), (180.34, y)); label('GND', (180.34, y), 0)
text('Vinyl tube from the buoy is a sheath\nfor the USB cable; it ends on G1.\n'
     'USB plugs are dry (buoy, Pico).', (131.06, 60.96), NOTE)
Part('AATV:Penetration', 'G1', 'G1: M16 gland, USB cable', 167.64, 45.72,
     refpos=(170.18, 55.88), valpos=(170.18, 58.42), just='left')

# ================================================================== BOARD
pico = Part('MCU_Module:RaspberryPi_Pico', 'A1', 'Raspberry Pi Pico', 279.4, 106.68,
            refpos=(287.02, 64.77), valpos=(287.02, 62.23), just='left')
stub(pico, 40, 'VBUS_PICO'); stub(pico, 36, '+3V3'); stub(pico, 3, 'GND'); stub(pico, 33, 'GND')
gp = {16: 'GP12', 17: 'GP13', 19: 'GP14', 20: 'GP15', 21: 'GP16', 24: 'GP18', 25: 'GP19'}
for pin, net in gp.items():
    stub(pico, pin, net)
stub(pico, 26, 'I2C_SDA'); stub(pico, 27, 'I2C_SCL')
stub(pico, 31, 'LEAK_MAIN')
used = {'40', '36', '3', '8', '13', '18', '23', '28', '38', '33', '31', '26', '27'} | {str(k) for k in gp}
for p in PINS[pico.lib_id]:
    if p['num'] not in used:
        nc(pico, p['num'])
res = [('R1', 'GP12', 'M4_PWM'), ('R2', 'GP13', 'M5_PWM'), ('R3', 'GP14', 'M6_PWM'), ('R4', 'GP15', 'M7_PWM'),
       ('R5', 'GP16', 'THR_PWM'), ('R6', 'GP19', 'PUMP_EN'), ('R17', 'GP18', 'VALVE_EN')]
for i, (ref, a, b) in enumerate(res):
    y = 66.04 + i * 10.16
    r = Part('Device:R', ref, '200', 213.36, y, rot=90,
             refpos=(213.36, y - 2.54), valpos=(213.36, y + 2.54), valsize=1.0, refsize=1.0)
    stub(r, 1, a, 5.08); stub(r, 2, b, 5.08)
text('200 ohm in series on every signal\nthat leaves the board (R1-R6, R17).', (185.42, 152.4), NOTE)


def term(ref, n, X, Y, nets, value, mirror=False, valpos=None, refpos=None, lib=None):
    lib = lib or f'Connector:Screw_Terminal_01x{n:02d}'
    t = Part(lib, ref, value, X, Y, mirror=mirror,
             refpos=refpos or (X, Y - (n * 1.27) - 3.81),
             valpos=valpos or (X, Y + (n * 1.27) + 5.08))
    for i, net in enumerate(nets):
        if net is None:
            nc(t, i + 1)
        else:
            stub(t, i + 1, net, 5.08, 1.0)
    return t


term('TA2', 3, 205.74, 177.8, ['+3V3', 'GND', 'LEAK_MAIN'], 'Leak sensor (box low point)', mirror=True,
     valpos=(205.74, 187.96), refpos=(205.74, 170.18))

# --- battery monitor: balance plug -> dividers -> ADS1115
term('J3', 4, 200.66, 213.36, ['GND', 'BAL_C1', 'BAL_C2', 'BAT_RAW'], 'Balance lead in (JST-XH 4)',
     mirror=True, lib='Connector_Generic:Conn_01x04', refpos=(200.66, 205.74), valpos=(200.66, 222.25))
taps = [('BAL_C1', 'ADC_C1', '100k', '200k', 'C2'), ('BAL_C2', 'ADC_C2', '200k', '100k', 'C3'),
        ('BAT_RAW', 'ADC_C3', '100k', '30k', 'C4')]
for i, (src, adc, rtop, rbot, cref) in enumerate(taps):
    y = 203.2 + i * 12.7
    rt = Part('Device:R', f'R{7 + 2 * i}', rtop, 243.84, y, rot=90,
              refpos=(243.84, y - 2.54), valpos=(243.84, y + 2.54), valsize=1.0, refsize=1.0)
    stub(rt, 1, src, 5.08, 1.0); stub(rt, 2, adc, 5.08, 1.0)
    rb = Part('Device:R', f'R{8 + 2 * i}', rbot, 281.94, y, rot=90,
              refpos=(281.94, y - 2.54), valpos=(281.94, y + 2.54), valsize=1.0, refsize=1.0)
    stub(rb, 1, adc, 5.08, 1.0); stub(rb, 2, 'GND', 5.08, 1.0)
    c = Part('Device:C', cref, '100nF', 314.96, y, rot=90,
             refpos=(314.96, y - 3.81), valpos=(314.96, y + 3.81), valsize=1.0, refsize=1.0)
    stub(c, 1, adc, 5.08, 1.0); stub(c, 2, 'GND', 5.08, 1.0)
u4 = Part('Analog_ADC:ADS1015IDGS', 'U4', 'ADS1115 16-bit ADC (breakout)', 358.14, 215.9,
          refpos=(362.0, 200.66), valpos=(362.0, 228.6), just='left')
stub(u4, 4, 'ADC_C1', 5.08, 1.0); stub(u4, 5, 'ADC_C2', 5.08, 1.0); stub(u4, 6, 'ADC_C3', 5.08, 1.0); nc(u4, 7)
stub(u4, 10, 'I2C_SCL', 5.08, 1.0); stub(u4, 9, 'I2C_SDA', 5.08, 1.0); stub(u4, 1, 'GND', 5.08, 1.0); nc(u4, 2)
stub(u4, 8, '+3V3', 2.54, 1.0); stub(u4, 3, 'GND', 2.54, 1.0)

# --- servo / signal terminals (right column)
term('TB7', 4, 373.38, 45.72, ['SERVO_7V5', 'SERVO_7V5', 'GND', 'GND'], '7.5 V in (2x14 AWG per pole)')
c1 = Part('Device:C_Polarized', 'C1', '1000uF 35V', 391.16, 45.72,
          refpos=(388.62, 44.45), valpos=(388.62, 46.99), just='right')
stub(c1, 1, 'SERVO_7V5'); stub(c1, 2, 'GND')
term('TB2', 6, 373.38, 78.74, ['M4_PWM', 'SERVO_7V5', 'GND', 'M5_PWM', 'SERVO_7V5', 'GND'], 'Rudder servo leads (via G4)')
term('TB3', 6, 373.38, 111.76, ['M6_PWM', 'SERVO_7V5', 'GND', 'M7_PWM', 'SERVO_7V5', 'GND'], 'Elevator servo leads (via G4)')
term('TB4', 2, 373.38, 139.7, ['THR_PWM', 'GND'], 'Thruster signal pair (via G2)')
term('TB5', 2, 373.38, 160.02, ['PUMP_EN', 'GND'], 'Pump enable (to U6, Q1)')
term('TB8', 2, 373.38, 180.34, ['VALVE_EN', 'GND'], 'Valve enable (to U6, Q2)')
r13 = Part('Device:R', 'R13', '10k', 391.16, 139.7, refpos=(393.7, 138.43), valpos=(393.7, 140.97), just='left',
           valsize=1.0, refsize=1.0)
stub(r13, 1, 'THR_PWM', 2.54, 1.0); stub(r13, 2, 'GND', 2.54, 1.0)

text('Board:\n- One solderable breadboard. 7.5 V + GND rails: 14 AWG soldered along strips;\n'
     '  servo + / - jumpers 14 AWG. Signal jumpers 20 AWG.\n'
     '- No 12 V or 24 V on this board.\n'
     '- R13: 10 k pull-down so the thruster ESC sees a clean low while the Pico boots.\n'
     '- Pump and valve are plain on/off outputs (GP19, GP18). Never switch both on together.\n'
     '- Free Pico pins: GP4, GP5, GP17, GP27, GP28.', (185.42, 236.22), NOTE)
text('Battery monitor (balance lead -> J3):\n- Dividers 100k/200k, 200k/100k, 100k/30k: 2.80 / 2.80 / 2.91 V\n'
     '  at a full pack. Firmware scale x1.500, x3.000, x4.333.\n'
     '- ADS1115 on I2C0 (GP20 SDA, GP21 SCL), addr 0x48, gain +/-4.096 V.\n'
     '  The breakout has its own pull-ups and decoupling.\n'
     '- Calibrate each channel once against a multimeter.\n'
     '- C2-C4 (100 nF): fit when available. Unplug J3 for storage.', (276.86, 236.22), NOTE)

# ================================================================== POWER (off-board, in box)
cells = []
for i, (ref, yy) in enumerate((('BT3', 50.8), ('BT2', 60.96), ('BT1', 71.12))):
    c = Part('Device:Battery_Cell', ref, f'cell {3 - i}', 419.1, yy, refpos=(422.91, yy - 1.27), valpos=(422.91, yy + 1.27),
             just='left', valsize=1.0, refsize=1.0)
    cells.append(c)
top, mid, bot = cells
wire(top.P(1), (419.1, 40.64)); label('BAT_RAW', (419.1, 40.64), 90)
wire(top.P(2), mid.P(1)); label('BAL_C2', top.P(2), 180, 1.0)
wire(mid.P(2), bot.P(1)); label('BAL_C1', mid.P(2), 180, 1.0)
wire(bot.P(2), (419.1, 78.74)); label('GND', (419.1, 78.74), 270)
text('BT1-BT3: one 3S LiPo pack (5200 mAh), inside the box\n(cells shown so the balance taps appear).\n'
     'Balance plug (JST-XH 4) -> J3 on the board.', (408.94, 86.36), NOTE)


def pair(tag, X, Y, nets, value_a, value_b, n=2, sock='Connector:Conn_01x02_Socket', pin='Connector:Conn_01x02_Pin'):
    a = Part(sock, f'{tag}A', value_a, X, Y, refpos=(X - 3.81, Y - 6.35), valpos=(X - 3.81, Y + 6.35))
    b = Part(pin, f'{tag}B', value_b, X + 1, Y, refpos=(X + 5.08, Y - 6.35), valpos=(X + 5.08, Y + 8.89))
    for i in range(n):
        for part in (a, b):
            stub(part, i + 1, nets[i], 5.08, 1.0)
    return a, b


pair('J2', 449.58, 43.18, ['BAT_RAW', 'GND'], 'EC5 (pack lead)', 'EC5 pigtail')
f1 = Part('Device:Fuse', 'F1', '25 A blade (standard holder, 12 AWG)', 482.6, 40.64, rot=90,
          refpos=(482.6, 38.1), valpos=(482.6, 35.56))
stub(f1, 1, 'BAT_RAW', 5.08, 1.0); stub(f1, 2, 'BAT_FUSED', 5.08, 1.0)
sw1 = Part('Switch:SW_SPST', 'SW1', 'Kill switch, HIGH side, 30 A DC', 533.4, 40.64,
           refpos=(533.4, 38.1), valpos=(533.4, 35.56))
stub(sw1, 1, 'BAT_FUSED', 5.08, 1.0); stub(sw1, 2, 'VBAT', 5.08, 1.0)
text('Battery + -> EC5 -> F1 -> SW1 -> +12 V bus. Battery - goes straight to the GND bus.\n'
     'Everything on this path is 12 AWG (14 AWG minimum). F1 at 25 A relies on the\n'
     'firmware throttle cap. High-side switch is required: J3 ties battery - to board GND.\n'
     'SW1 sits inside the sealed box (lid off to reach it).', (440.69, 57.15), NOTE)


def busbar(ref, X, Y, net, value):
    t = Part('Connector:Screw_Terminal_01x06', ref, value, X, Y,
             refpos=(X, Y - 10.16), valpos=(X, Y + 12.7))
    pts = [t.P(i) for i in range(1, 7)]
    for a, b in zip(pts, pts[1:]):
        wire(a, b)
    label(net, pts[0], 90)
    return t


bb1 = busbar('BB1', 502.92, 86.36, 'VBAT', '+12 V row A (OONO 2x6, 30 A)')
bb2 = busbar('BB2', 502.92, 119.38, 'GND', 'GND row B (OONO 2x6, 30 A)')
text('Bus bar (OONO 2x6, one row per pole):\nin: SW1 output / battery -\nout: thruster power pair (14 AWG),\n'
     '     buck U1, boost U5, switch board GND\n(spare positions on each row)', (510.54, 76.2), NOTE)
for ref, part, xy in (('#FLG01', bb1, (490.22, 78.74)), ('#FLG02', bb2, (490.22, 111.76))):
    Part('power:PWR_FLAG', ref, 'PWR_FLAG', *xy, hide_ref=True, hide_val=True)
    p1 = part.P(1)
    path(xy, (p1[0], xy[1]), p1)
pf3 = Part('power:PWR_FLAG', '#FLG03', 'PWR_FLAG', 187.96, 38.1, hide_ref=True, hide_val=True)
x, y = w1.P(5)
path((172.72, 38.1), (172.72, y))
junction((172.72, y))

u1 = Part('AATV:Buck_12V_7V5', 'U1', '12/24 V -> 7.5 V buck, 20 A, fixed (WSOLDMA)', 497.84, 152.4,
          refpos=(497.84, 144.78), valpos=(497.84, 160.02))
stub(u1, 1, 'VBAT'); stub(u1, 2, 'GND'); stub(u1, 3, 'SERVO_7V5'); stub(u1, 4, 'GND')
text('U1 output is fixed at 7.5 V. Low-voltage cutoff measured at 9 V in.\n'
     'Hitec DB777WP: 6.0-7.4 V on the spec sheet; up to ~7.6 V measured is OK.', (455.93, 165.1), NOTE)

# --- 24 V rail: boost with its own input fuse
f2 = Part('Device:Fuse', 'F2', 'Boost input fuse (built in, red lead), 7.5-10 A mini blade', 436.88, 185.42, rot=90,
          refpos=(436.88, 182.88), valpos=(436.88, 180.34))
stub(f2, 1, 'VBAT', 5.08, 1.0); stub(f2, 2, 'BOOST_IN', 5.08, 1.0)
u5 = Part('AATV:Boost_12V_24V', 'U5', '12 V -> 24 V boost, 3 A max', 464.82, 200.66,
          refpos=(464.82, 193.04), valpos=(464.82, 208.28))
stub(u5, 1, 'BOOST_IN', 2.54, 1.0); stub(u5, 2, 'GND', 2.54, 1.0); stub(u5, 3, 'V24', 2.54, 1.0); stub(u5, 4, 'GND', 2.54, 1.0)
text('24 V rail:\n- U5 red/black = 12 V in, yellow/black = 24 V out.\n'
     '  In - and out - must be common (check continuity).\n'
     '- No fuse after U5: it limits its output to 3 A,\n  which 20 AWG leads and the switches can carry.\n'
     '- V24 feeds the pump + and the valve + directly.\n  Q1 / Q2 switch the - side of each load.\n'
     '- Valve drawn as 24 V. A 12 V valve must NOT go on V24:\n  feed its + from the +12 V bus through a 2 A fuse.\n'
     '- Optional: 1-2 A fuse in the valve + lead keeps the\n  pump working if the valve shorts.', (408.94, 213.36), NOTE)

# --- U6 switch board
for k, (qref, dref, rref, en, sw) in enumerate((('Q1', 'D3', 'R14', 'PUMP_EN', 'PUMP_SW'),
                                                ('Q2', 'D4', 'R18', 'VALVE_EN', 'VALVE_SW'))):
    X = 513.08 + k * 40.64
    d = Part('Device:D_Schottky', dref, '1N5822', X, 205.74,
             refpos=(X, 201.93), valpos=(X, 209.55), valsize=1.0, refsize=1.0)
    stub(d, 1, 'V24', 5.08, 1.0); stub(d, 2, sw, 5.08, 1.0)
    qq = Part('Transistor_FET:BUZ11', qref, 'IRLZ44N', X, 226.06,
              refpos=(X + 7.62, 224.79), valpos=(X + 7.62, 227.33), just='left', valsize=1.0, refsize=1.0)
    stub(qq, 1, en, 5.08, 1.0); stub(qq, 2, sw, 2.54, 1.0); stub(qq, 3, 'GND', 2.54, 1.0)
    r = Part('Device:R', rref, '10k', X, 248.92, rot=90,
             refpos=(X, 246.38), valpos=(X, 251.46), valsize=1.0, refsize=1.0)
    stub(r, 1, en, 5.08, 1.0); stub(r, 2, 'GND', 5.08, 1.0)
text('Low-side switches. D3 / D4: stripe (K) to the + side of the load.\n'
     'R14 / R18 hold the gates low while the Pico boots or loses USB.', (495.3, 189.23), 1.0)
text('pump', (513.08, 255.27), 1.27, bold=True, just='top')
text('valve', (553.72, 255.27), 1.27, bold=True, just='top')

Part('AATV:Penetration', 'G4', 'G4: M16 gland, 4 servo leads (insert removed, epoxy-potted)', 373.38, 266.7,
     refpos=(378.46, 264.16), valpos=(378.46, 270.51), just='left')
Part('AATV:Penetration', 'G2', 'G2: M16 gland, thruster cable + signal pair (potted)', 459.74, 266.7,
     refpos=(464.82, 264.16), valpos=(464.82, 270.51), just='left')
Part('AATV:Penetration', 'G3', 'G3: M16 gland, pump + valve leads (potted)', 525.78, 266.7,
     refpos=(530.86, 264.16), valpos=(530.86, 270.51), just='left')

# ================================================================== OUTSIDE (wet)
for i, s in enumerate(('M4', 'M5', 'M6', 'M7')):
    y = 289.56 + i * 15.24
    m = Part('Motor:Motor_Servo', s, ['Rudder', 'Rudder', 'Elevator', 'Elevator'][i] + ' servo', 375.92, y,
             refpos=(386.08, y - 1.27), valpos=(379.73, y + 6.35), just='left')
    stub(m, 1, f'{s}_PWM', 2.54, 1.0); stub(m, 2, 'SERVO_7V5', 2.54, 1.0); stub(m, 3, 'GND', 2.54, 1.0)

mt1 = Part('AATV:Thruster_ESC', 'MT1', 'ApisQueen U92 Pro 12 V (ESC built in)', 472.44, 300.99,
           refpos=(474.98, 292.1), valpos=(474.98, 309.88))
stub(mt1, 1, 'VBAT', 2.54, 1.0); stub(mt1, 2, 'GND', 2.54, 1.0); stub(mt1, 3, 'THR_PWM', 2.54, 1.0); stub(mt1, 4, 'GND', 2.54, 1.0)
text('Thick pair: + to the +12 V bus, - to the GND bus (14 AWG).\n'
     'Thin pair: white = signal -> TB4.1, black = signal GND -> TB4.2.\n'
     'Cut off the XT60 to pass G2. 17 A at 12 V and 100 % throttle;\n'
     'cap the throttle in firmware. Max supply 16.8 V.', (431.8, 314.96), NOTE)

m3 = Part('Motor:Motor_DC', 'M3', 'Rule 28D pump, 24 V', 533.4, 302.26,
          refpos=(538.48, 300.99), valpos=(533.4, 325.12), just=None)
stub(m3, 1, 'V24', 2.54, 1.0); stub(m3, 2, 'PUMP_SW', 2.54, 1.0)
sv1 = Part('AATV:Solenoid_Valve', 'SV1', '24 V NC valve', 561.34, 302.26,
           refpos=(572.77, 300.99), valpos=(563.88, 325.12))
stub(sv1, 1, 'V24', 2.54, 1.0); stub(sv1, 2, 'VALVE_SW', 2.54, 1.0)
text('M3: bilge pump, 1.3 A at 24 V, one way: water OUT. Brown lead = +.\n'
     'SV1: normally closed, direct-acting: water IN. Not chosen yet.\n'
     'Plumbing: check valve on the pump outlet (water runs back through\n'
     'a stopped pump). Valve inlet and pump intake at the tank bottom.', (500.38, 330.2), 1.0)

text('Servos: 2x Hitec DB777WP (4.5 A stall), 2x Savox SW-1250MG (2.4 A stall).\n'
     'All four stalled = 13.8 A on the 7.5 V rail. Both types tested on the Pico 3.3 V signal.\n'
     'Factory leads run uncut into the box through G4 and land on TB2 / TB3.', (226.06, 345.44), NOTE)
text('Gland rules (M16 x 1.5, clamp range about 4-8 mm):\n'
     '- A gland seals ONE round cable. Anything else: pull the rubber insert, pass the leads,\n'
     '  fill the gland body with epoxy (G2, G3, G4). Epoxy bonds poorly to silicone jackets.\n'
     '- IP67 = 1 m for 30 min. Vacuum-test the closed box before every dive.', (12.7, 290.83), NOTE)
text('Ballast (sealed tank, no vent):\n'
     '- Valve open: water in until the trapped air matches the outside pressure\n'
     '  (about 9 % of the air space at 1 m). Open in short bursts.\n'
     '- Pump on: water out. Valve closed + pump off + check valve: volume holds.\n'
     '- Power or USB lost: pump off, valve closed.', (12.7, 312.42), NOTE)
text('Changed vs v9: thruster ESC (U2) is now inside the thruster. Pump ESC (U3), D2 Deutsch connector and the\n'
     'pump drybox are gone. Added boost U5, switch board U6 (Q1, Q2, D3, D4, R14, R18), valve SV1, R17, TB8.\n'
     'F1 30 A -> 25 A. Servo rail 7.4 V -> 7.5 V. Series resistors 220 -> 200 ohm. Dividers re-valued.\n'
     'R15 / R16 / C5 removed (on the ADS1115 breakout).', (12.7, 340.36), NOTE)

write(OUT)
if len(sys.argv) > 2:
    open(sys.argv[2], 'w').write(custom.library_file())
print('ok', len(ITEMS))
