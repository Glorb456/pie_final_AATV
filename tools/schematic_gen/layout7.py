"""AA-TV v9 schematic: one large IP67 main box (battery inside), 4x M16 glands.
usage: python3 layout7.py out.kicad_sch
Does not touch the v8.3 files. Same helpers as layout6.py (gen.py, libs.py, custom.py).
"""
import sys
import gen
import custom
from gen import *

OUT = sys.argv[1]
gen.PROJECT = 'AATV_v9'
NOTE = 1.27
TITLE_SZ = 2.54

# 12 V -> 7.4 V buck symbol (same body as the 7.5 V one)
custom.CUSTOM['Buck_12V_7V4'] = custom.CUSTOM['Buck_12V_7V5'].replace('Buck_12V_7V5', 'Buck_12V_7V4').replace(
    '12V->7.5V buck', '12V->7.4V buck').replace('7.5 V buck module', '7.4 V buck module')

gen.TITLE.update({
    'title': 'AA-TV electrical v9: single IP67 box, 4x M16 glands',
    'rev': 'v9',
    'date': '2026-11-06',
    'c1': 'One IP67 box holds battery, fuse, kill switch, bus bar, buck, both ESCs, one board.',
    'c2': 'Glands: G1 USB, G2 thruster phases, G3 pump pair, G4 servo leads (potted). DTP: D2 only.',
    'c3': 'High-side kill switch. Servo rail 7.4 V. Cells read by ADS1115 (I2C0).',
})

# ------------------------------------------------------------------ zones
BUOY = ((10.16, 15.24), (129.54, 160.02))
MAIN = ((167.64, 15.24), (584.2, 266.7))
BOARD = ((175.26, 27.94), (401.32, 259.08))
WET = ((10.16, 276.86), (584.2, 372.11))
PUMPBOX = ((538.48, 287.02), (581.66, 327.66))
for z in (BUOY, MAIN):
    rect(*z, width=0.6)
rect(*WET, width=0.6, style='dash_dot')
rect(*BOARD, width=0.35, style='dash')
rect(*PUMPBOX, width=0.45)

text('AA-TV wiring v9: single IP67 main box (battery inside), 4x M16 cable glands, one solder-board, 1x Deutsch DTP 4-pin (pump). '
     'Everything outside the box is flooded ballast space.', (12.7, 6.35), 3, bold=True)
text('BUOY  (surface, dry)', (12.7, 17.78), TITLE_SZ, bold=True)
text('TETHER', (134.62, 17.78), TITLE_SZ, bold=True)
text('MAIN BOX  (IP67, 191 x 111 x 58 mm inside; the only drybox)', (170.18, 17.78), TITLE_SZ, bold=True)
text('BOARD: Pico + servo / signal solder-board (old Boards A + B merged)', (177.8, 30.48), 1.8, bold=True)
text('Power, off-board (in the box)', (406.4, 30.48), 1.8, bold=True)
text('WET ZONE  (flooded hull = ballast): servos, thruster motor, pump cable + D2, pump drybox', (12.7, 279.4), TITLE_SZ, bold=True)
text('PUMP DRYBOX (or sealed pump)', (539.75, 289.56), 1.27, bold=True)

# ================================================================== BUOY (unchanged from v8.3)
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
w1 = Part('AATV:USB_Cable', 'W1', 'USB-A to micro-B, ~3 m', 142.24, 45.72,
          refpos=(142.24, 35.56), valpos=(142.24, 57.15))
x, y = w1.P(1); wire((x, y), (127.0, y)); label('5V_PI', (127.0, y), 180)
x, y = w1.P(4); wire((x, y), (127.0, y)); label('GND_PI', (127.0, y), 180)
x, y = w1.P(5); wire((x, y), (180.34, y)); label('VBUS_PICO', (180.34, y), 0)
x, y = w1.P(8); wire((x, y), (180.34, y)); label('GND', (180.34, y), 0)
text('Vinyl air tube from the buoy is a sheath\nfor the USB cable; it ends on G1.\n'
     'USB plugs are dry (buoy, Pico).\nA vented box would need a barbed\nbulkhead instead of a gland.', (131.06, 60.96), NOTE)
Part('AATV:Penetration', 'G1', 'G1: M16 gland, USB cable', 167.64, 45.72,
     refpos=(170.18, 55.88), valpos=(170.18, 58.42), just='left')

# ================================================================== BOARD
pico = Part('MCU_Module:RaspberryPi_Pico', 'A1', 'Raspberry Pi Pico', 279.4, 106.68,
            refpos=(287.02, 64.77), valpos=(287.02, 62.23), just='left')
stub(pico, 40, 'VBUS_PICO'); stub(pico, 36, '+3V3'); stub(pico, 3, 'GND'); stub(pico, 33, 'GND')
gp = {16: 'GP12', 17: 'GP13', 19: 'GP14', 20: 'GP15', 21: 'GP16', 25: 'GP19'}
for pin, net in gp.items():
    stub(pico, pin, net)
stub(pico, 26, 'I2C_SDA'); stub(pico, 27, 'I2C_SCL')
stub(pico, 31, 'LEAK_MAIN')
used = {'40', '36', '3', '8', '13', '18', '23', '28', '38', '33', '31', '26', '27'} | {str(k) for k in gp}
for p in PINS[pico.lib_id]:
    if p['num'] not in used:
        nc(pico, p['num'])
res = [('GP12', 'M4_PWM'), ('GP13', 'M5_PWM'), ('GP14', 'M6_PWM'), ('GP15', 'M7_PWM'),
       ('GP16', 'THR_PWM'), ('GP19', 'PUMP_PWM')]
for i, (a, b) in enumerate(res):
    y = 66.04 + i * 10.16
    r = Part('Device:R', f'R{i+1}', '220', 213.36, y, rot=90,
             refpos=(213.36, y - 2.54), valpos=(213.36, y + 2.54), valsize=1.0, refsize=1.0)
    stub(r, 1, a, 5.08); stub(r, 2, b, 5.08)
text('220 ohm in series on every PWM line\nthat leaves the board.', (185.42, 152.4), NOTE)


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
taps = [('BAL_C1', 'ADC_C1', '47k', 'C2'), ('BAL_C2', 'ADC_C2', '200k', 'C3'), ('BAT_RAW', 'ADC_C3', '330k', 'C4')]
for i, (src, adc, rtop, cref) in enumerate(taps):
    y = 203.2 + i * 12.7
    rt = Part('Device:R', f'R{7 + 2 * i}', rtop, 243.84, y, rot=90,
              refpos=(243.84, y - 2.54), valpos=(243.84, y + 2.54), valsize=1.0, refsize=1.0)
    stub(rt, 1, src, 5.08, 1.0); stub(rt, 2, adc, 5.08, 1.0)
    rb = Part('Device:R', f'R{8 + 2 * i}', '100k', 281.94, y, rot=90,
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
for i, (ref, net) in enumerate((('R15', 'I2C_SDA'), ('R16', 'I2C_SCL'))):
    y = 241.3 + i * 7.62
    r = Part('Device:R', ref, '4.7k', 358.14, y, rot=90,
             refpos=(358.14, y - 2.54), valpos=(358.14, y + 2.54), valsize=1.0, refsize=1.0)
    stub(r, 1, '+3V3', 5.08, 1.0); stub(r, 2, net, 5.08, 1.0)
c5 = Part('Device:C', 'C5', '100nF', 391.16, 215.9, refpos=(393.7, 214.63), valpos=(393.7, 217.17), just='left',
          valsize=1.0, refsize=1.0)
stub(c5, 1, '+3V3', 2.54, 1.0); stub(c5, 2, 'GND', 2.54, 1.0)

# --- servo / ESC terminals (right column)
term('TB7', 4, 373.38, 45.72, ['SERVO_7V4', 'SERVO_7V4', 'GND', 'GND'], '7.4 V in (2x14 AWG per pole)')
c1 = Part('Device:C_Polarized', 'C1', '1000uF 16V', 391.16, 45.72,
          refpos=(393.7, 44.45), valpos=(393.7, 46.99), just='left')
stub(c1, 1, 'SERVO_7V4'); stub(c1, 2, 'GND')
term('TB2', 6, 373.38, 78.74, ['M4_PWM', 'SERVO_7V4', 'GND', 'M5_PWM', 'SERVO_7V4', 'GND'], 'Rudder servo leads (via G4)')
term('TB3', 6, 373.38, 111.76, ['M6_PWM', 'SERVO_7V4', 'GND', 'M7_PWM', 'SERVO_7V4', 'GND'], 'Elevator servo leads (via G4)')
term('TB4', 2, 373.38, 139.7, ['THR_PWM', 'GND'], 'Thruster ESC signal (U2)')
term('TB5', 2, 373.38, 160.02, ['PUMP_PWM', 'GND'], 'Pump ESC signal (U3)')
for ref, net, y in (('R13', 'THR_PWM', 139.7), ('R14', 'PUMP_PWM', 160.02)):
    r = Part('Device:R', ref, '10k', 391.16, y, refpos=(393.7, y - 1.27), valpos=(393.7, y + 1.27), just='left',
             valsize=1.0, refsize=1.0)
    stub(r, 1, net, 2.54, 1.0); stub(r, 2, 'GND', 2.54, 1.0)

text('Board:\n- Old Boards A + B merged into one solderable breadboard; no H1 harness.\n'
     '- 7.4 V + GND rails: 14 AWG soldered along strips; servo + / - jumpers 14 AWG.\n'
     '- Signal jumpers 20 AWG. No 12 V on the breadboard.\n'
     '- R13 / R14: 10 k pull-downs so the ESCs see a clean low while the Pico boots.\n'
     '- Free Pico pins: GP4, GP5, GP17, GP18, GP27 (2nd leak sensor), GP28.', (185.42, 236.22), NOTE)
text('Battery monitor (balance lead -> J3):\n- Dividers 47k/100k, 200k/100k, 330k/100k: ~2.9 V\n  at a full pack (4.2 V/cell). ~29 uA per tap.\n'
     '- Top resistors sit right at J3: a board short\n  only ever sees >= 47 k. Unplug J3 for storage.\n'
     '- ADS1115 on I2C0 (GP20 SDA, GP21 SCL), addr 0x48.\n  R15/R16: omit if the breakout has pull-ups.', (276.86, 236.22), NOTE)

# ================================================================== POWER (off-board, in box)
# 3S pack drawn as three cells so the balance taps show
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
text('BT1-BT3: one 3S LiPo pack, inside the box\n(cells shown so the balance taps appear).\n'
     'Balance plug (JST-XH 4) -> J3 on the board.', (408.94, 86.36), NOTE)


def pair(tag, X, Y, nets, value_a, value_b, n=2, sock='Connector:Conn_01x02_Socket', pin='Connector:Conn_01x02_Pin'):
    a = Part(sock, f'{tag}A', value_a, X, Y, refpos=(X - 3.81, Y - 6.35), valpos=(X - 3.81, Y + 6.35))
    b = Part(pin, f'{tag}B', value_b, X + 1, Y, refpos=(X + 5.08, Y - 6.35), valpos=(X + 5.08, Y + 8.89))
    for i in range(n):
        for part in (a, b):
            stub(part, i + 1, nets[i], 5.08, 1.0)
    return a, b


pair('J2', 449.58, 43.18, ['BAT_RAW', 'GND'], 'EC5 (pack lead)', 'EC5 pigtail')
f1 = Part('Device:Fuse', 'F1', '30 A ATC (standard holder)', 482.6, 40.64, rot=90,
          refpos=(482.6, 38.1), valpos=(482.6, 35.56))
stub(f1, 1, 'BAT_RAW', 5.08, 1.0); stub(f1, 2, 'BAT_FUSED', 5.08, 1.0)
sw1 = Part('Switch:SW_SPST', 'SW1', 'Kill switch, HIGH side, >=30 A DC', 523.24, 40.64,
           refpos=(523.24, 38.1), valpos=(523.24, 35.56))
stub(sw1, 1, 'BAT_FUSED', 5.08, 1.0); stub(sw1, 2, 'VBAT', 5.08, 1.0)
text('Battery + -> EC5 -> F1 -> SW1 -> VBAT bus. Battery - goes straight to the GND bus.\n'
     'High-side switch is required now: J3 ties battery - to board GND, which would\n'
     'bypass a low-side switch. SW1 sits inside the sealed box (lid off to reach it);\n'
     'a reed switch + >= 30 A relay can make it external later.', (440.69, 57.15), NOTE)


def busbar(ref, X, Y, net, value):
    t = Part('Connector:Screw_Terminal_01x06', ref, value, X, Y,
             refpos=(X, Y - 10.16), valpos=(X, Y + 12.7))
    pts = [t.P(i) for i in range(1, 7)]
    for a, b in zip(pts, pts[1:]):
        wire(a, b)
    label(net, pts[0], 90)
    return t


bb1 = busbar('BB1', 502.92, 86.36, 'VBAT', '+12 V row (OONO 2x6, 30 A)')
bb2 = busbar('BB2', 502.92, 119.38, 'GND', 'GND row (OONO 2x6, 30 A)')
text('Bus bar (OONO 2x6, one row per pole, 30 A total):\nin: SW1 output / battery -\nout: buck U1, thruster ESC U2,\n     pump ESC U3 (2 spare per row)', (510.54, 76.2), NOTE)
for ref, part, xy in (('#FLG01', bb1, (490.22, 78.74)), ('#FLG02', bb2, (490.22, 111.76))):
    Part('power:PWR_FLAG', ref, 'PWR_FLAG', *xy, hide_ref=True, hide_val=True)
    p1 = part.P(1)
    path(xy, (p1[0], xy[1]), p1)
pf3 = Part('power:PWR_FLAG', '#FLG03', 'PWR_FLAG', 187.96, 38.1, hide_ref=True, hide_val=True)
x, y = w1.P(5)
path((172.72, 38.1), (172.72, y))
junction((172.72, y))

u1 = Part('AATV:Buck_12V_7V4', 'U1', '12 V -> 7.4 V buck (adjustable, >=15 A)', 497.84, 152.4,
          refpos=(497.84, 144.78), valpos=(497.84, 160.02))
stub(u1, 1, 'VBAT'); stub(u1, 2, 'GND'); stub(u1, 3, 'SERVO_7V4'); stub(u1, 4, 'GND')
text('Set U1 to 7.4 V (Hitec DB777WP max).\nSavox SW-1250MG: 6.0-8.4 V.', (480.06, 165.1), NOTE)

u2 = Part('AATV:ESC_TD1.2', 'U2', 'TD1.2 ESC (inside the box)', 459.74, 213.36,
          refpos=(459.74, 205.74), valpos=(459.74, 226.06))
stub(u2, 1, 'VBAT', 2.54, 1.0); stub(u2, 2, 'GND', 2.54, 1.0); stub(u2, 3, 'THR_PWM', 2.54, 1.0); stub(u2, 4, 'GND', 2.54, 1.0)
stub(u2, 5, 'THR_U', 2.54, 1.0); stub(u2, 6, 'THR_V', 2.54, 1.0); stub(u2, 7, 'THR_W', 2.54, 1.0)
u3 = Part('AATV:ESC_Brushed', 'U3', 'Pump ESC (brushed, reversible, > pump stall)', 541.02, 213.36,
          refpos=(541.02, 205.74), valpos=(541.02, 226.06))
stub(u3, 1, 'VBAT', 2.54, 1.0); stub(u3, 2, 'GND', 2.54, 1.0); nc(u3, 3); stub(u3, 4, 'PUMP_PWM', 2.54, 1.0)
stub(u3, 5, 'GND', 2.54, 1.0); stub(u3, 6, 'PUMP_M+', 2.54, 1.0); stub(u3, 7, 'PUMP_M-', 2.54, 1.0)
text('U2 inside: no 12 V leaves the box and D3 is gone.\nOnly the 3 phase wires go out through G2.\n'
     'ESC outside instead: G2 carries 12 V + GND +\nPWM + signal GND as a 4-core round cable.', (408.94, 231.14), NOTE)
text('Pump ESC sits dry, BEC wire cut.\nMotor pair -> G3 -> D2 -> pump box.', (523.24, 231.14), NOTE)

Part('AATV:Penetration', 'G4', 'G4: M16 gland, 4 servo leads (insert removed, epoxy-potted)', 373.38, 266.7,
     refpos=(378.46, 264.16), valpos=(378.46, 270.51), just='left')
Part('AATV:Penetration', 'G2', 'G2: M16 gland, thruster phase cable', 459.74, 266.7,
     refpos=(464.82, 264.16), valpos=(464.82, 270.51), just='left')
Part('AATV:Penetration', 'G3', 'G3: M16 gland, pump 2-core', 523.24, 266.7,
     refpos=(528.32, 264.16), valpos=(528.32, 270.51), just='left')

# ================================================================== WET ZONE
for i, s in enumerate(('M4', 'M5', 'M6', 'M7')):
    y = 289.56 + i * 15.24
    m = Part('Motor:Motor_Servo', s, ['Rudder', 'Rudder', 'Elevator', 'Elevator'][i] + ' servo', 375.92, y,
             refpos=(386.08, y - 1.27), valpos=(379.73, y + 6.35), just='left')
    stub(m, 1, f'{s}_PWM', 2.54, 1.0); stub(m, 2, 'SERVO_7V4', 2.54, 1.0); stub(m, 3, 'GND', 2.54, 1.0)
mt1 = Part('AATV:Thruster_TD1.2', 'MT1', 'TD1.2 thruster', 480.06, 300.99, refpos=(480.06, 293.37), valpos=(480.06, 308.61))
stub(mt1, 1, 'THR_U', 2.54, 1.0); stub(mt1, 2, 'THR_V', 2.54, 1.0); stub(mt1, 3, 'THR_W', 2.54, 1.0)
text('Factory thruster cable passes G2.\nThread the gland nut + seal over it\nbefore re-terminating at the ESC.', (459.74, 314.96), NOTE)

d2a, d2b = pair('D2', 515.62, 304.8, ['PUMP_M+', 'PUMP_M-', 'D2_LOOP', 'D2_LOOP'], 'D2 pump DTP06-4S', 'DTP04-4P', n=4,
                sock='Connector:Conn_01x04_Socket', pin='Connector:Conn_01x04_Pin')
text('D2: 1 pump +, 2 pump -;\n3-4 dummy loop.', (500.38, 317.5), 1.0)
m3 = Part('Motor:Motor_DC', 'M3', 'Ballast pump (12 V, reversible)', 563.88, 304.8,
          refpos=(567.69, 303.53), valpos=(541.02, 323.85), just='left')
stub(m3, 1, 'PUMP_M+', 2.54, 1.0); stub(m3, 2, 'PUMP_M-', 2.54, 1.0)

text('Servos: 2x Hitec DB777WP (4.5 A stall @ 7.4 V), 2x Savox SW-1250MG (2.4 A).\n'
     'Factory leads run uncut into the box through G4 and land on TB2 / TB3.\n'
     'BACKUP if a lead can\'t reach: one MGYOO 20 AWG 3-pin waterproof connector per servo.', (226.06, 345.44), NOTE)
text('Gland rules (M16 x 1.5, check the clamp range on the box listing, often ~4-8 mm):\n'
     '- A gland seals ONE round cable. Separate wires leak: use round jacketed cable (14/2 for the pump).\n'
     '- G4: 4 flat servo leads can\'t seal in a gland. Pull the rubber insert, pass the leads,\n'
     '  fill the gland body with epoxy.\n'
     '- IP67 = 1 m for 30 min. Vacuum-test the closed box before every dive.', (12.7, 290.83), NOTE)
text('Removed vs v8.3: rear drybox, H1 harness (12 x 14 AWG), D1 / D3 / D4 / D5 / D6, TA1 / TB1,\n'
     'rear leak sensor (TB6), the epoxy holes A2 / R2 / R3. Battery, fuse, kill switch and\n'
     'thruster ESC moved inside the box. Fuse holder no longer needs to be waterproof.', (12.7, 323.85), NOTE)

write(OUT)
print('ok', len(ITEMS))
