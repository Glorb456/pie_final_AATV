"""AA-TV v7 schematic. usage: python3 layout2.py A|B out.kicad_sch project_name"""
import sys
import gen
from gen import *

PLAN = sys.argv[1]
OUT = sys.argv[2]
gen.PROJECT = sys.argv[3]
WHEELS = PLAN == 'A'
NOTE = 1.27
TITLE_SZ = 2.54

gen.TITLE.update({
    'title': f'AA-TV electrical v7, Plan {PLAN}: ' + ('front driven wheels' if WHEELS else 'no front driven motors'),
    'c1': 'Two solder-boards (Board A main drybox, Board B rear drybox). Cables epoxy-potted through drybox walls.',
    'c2': 'Only connectors: Deutsch DT in the wet zone + 5.08 mm screw terminals / bus bars inside dryboxes.',
    'c3': 'Two wire gauges: HIGH = 14 AWG (12 V, 7.5 V, motor), LOW = 20 AWG (signals, 3.3 V, servo leads).',
})

# ------------------------------------------------------------------ zones
BUOY = ((10.16, 15.24), (129.54, 160.02))
MAIN = ((167.64, 15.24), (335.28, 241.3))
REAR = ((345.44, 15.24), (584.2, 241.3))
WET = ((10.16, 251.46), (584.2, 372.11))
BOARD_A = ((175.26, 27.94), (325.12, 233.68))
BOARD_B = ((350.52, 27.94), (466.09, 233.68))
for z in (BUOY, MAIN, REAR):
    rect(*z, width=0.6)
rect(*WET, width=0.6, style='dash_dot')
rect(*BOARD_A, width=0.35, style='dash')
rect(*BOARD_B, width=0.35, style='dash')

text(f'AA-TV wiring v7, PLAN {PLAN}: ' + ('front driven wheels' if WHEELS else 'NO front driven motors')
     + '. Deutsch DT connectors only (wet zone); cables epoxy-potted into dryboxes; 14 AWG / 20 AWG.',
     (12.7, 6.35), 3, bold=True)
text('BUOY  (surface, dry)', (12.7, 17.78), TITLE_SZ, bold=True)
text('MAIN DRYBOX  (upper, on hull)', (170.18, 17.78), TITLE_SZ, bold=True)
text('BOARD A: Pico solder-board', (177.8, 30.48), 1.8, bold=True)
text('REAR DRYBOX  (inside open rear endcap)', (347.98, 17.78), TITLE_SZ, bold=True)
text('BOARD B: servo / signal board', (353.06, 30.48), 1.8, bold=True)
text('Off-board, in rear drybox', (469.9, 30.48), 1.8, bold=True)
text('WET ZONE  (flooded hull, open rear endcap, splash areas): Deutsch DT connectors live here', (12.7, 254.0), TITLE_SZ, bold=True)
text('TETHER', (134.62, 17.78), TITLE_SZ, bold=True)

# ================================================================== BUOY
pi = Part('Connector:Raspberry_Pi_4', 'J1', 'Raspberry Pi 4 (buoy)', 68.58, 93.98,
          refpos=(68.58, 59.69), valpos=(68.58, 128.27))
stub(pi, 2, '5V_PI')
stub(pi, 6, 'GND_PI')
for p in PINS[pi.lib_id]:
    if p['num'] not in ('2', '4', '6', '9', '14', '20', '25', '30', '34', '39'):
        nc(pi, p['num'])
bank = Part('Device:Battery', 'BT2', 'USB-C power bank 5 V / 3 A', 25.4, 40.64,
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
text('Vinyl air tube from the buoy;\nUSB cable runs inside it.\nUSB plugs are dry (buoy, Pico).', (131.06, 60.96), NOTE)
Part('AATV:Penetration', 'PEN1', 'A1: air-tube fitting (USB inside)', 167.64, 45.72,
     refpos=(170.18, 55.88), valpos=(170.18, 58.42), just='left')

# ================================================================== BOARD A
pico = Part('MCU_Module:RaspberryPi_Pico', 'A1', 'Raspberry Pi Pico', 279.4, 106.68,
            refpos=(287.02, 64.77), valpos=(287.02, 62.23), just='left')
stub(pico, 40, 'VBUS_PICO'); stub(pico, 36, '+3V3'); stub(pico, 3, 'GND'); stub(pico, 33, 'GND')
gp = {16: 'GP12', 17: 'GP13', 19: 'GP14', 20: 'GP15', 21: 'GP16', 25: 'GP19'}
if WHEELS:
    gp.update({22: 'GP17', 24: 'GP18'})
for pin, net in gp.items():
    stub(pico, pin, net)
stub(pico, 31, 'LEAK_MAIN'); stub(pico, 32, 'LEAK_REAR')
used = {'40', '36', '3', '8', '13', '18', '23', '28', '38', '33', '31', '32'} | {str(k) for k in gp}
for p in PINS[pico.lib_id]:
    if p['num'] not in used:
        nc(pico, p['num'])
res = [('GP12', 'M4_PWM'), ('GP13', 'M5_PWM'), ('GP14', 'M6_PWM'), ('GP15', 'M7_PWM'),
       ('GP16', 'THR_PWM'), ('GP19', 'PUMP_PWM')]
if WHEELS:
    res += [('GP17', 'DRV_L_PWM'), ('GP18', 'DRV_R_PWM')]
for i, (a, b) in enumerate(res):
    y = 66.04 + i * 10.16
    r = Part('Device:R', f'R{i+1}', '220', 213.36, y, rot=90,
             refpos=(213.36, y - 2.54), valpos=(213.36, y + 2.54), valsize=1.0, refsize=1.0)
    stub(r, 1, a, 5.08); stub(r, 2, b, 5.08)
text('220 ohm in series on every PWM line\nthat leaves the drybox.', (185.42, 152.4), NOTE)

H1 = ['M4_PWM', 'M5_PWM', 'M6_PWM', 'M7_PWM', 'THR_PWM',
      'DRV_L_PWM' if WHEELS else None, 'DRV_R_PWM' if WHEELS else None, 'PUMP_PWM',
      'LEAK_REAR', '+3V3', 'GND', 'GND']

def term(ref, n, X, Y, nets, value, mirror=False, valpos=None, refpos=None):
    lib = f'Connector:Screw_Terminal_01x{n:02d}'
    t = Part(lib, ref, value, X, Y, mirror=mirror,
             refpos=refpos or (X, Y - (n * 1.27) - 3.81),
             valpos=valpos or (X, Y + (n * 1.27) + 5.08))
    for i, net in enumerate(nets):
        if net is None:
            nc(t, i + 1)
        else:
            stub(t, i + 1, net, 5.08, 1.0)
    return t

ta2 = term('TA2', 3, 205.74, 177.8, ['+3V3', 'GND', 'LEAK_MAIN'], 'Main leak sensor', mirror=True,
           valpos=(205.74, 187.96), refpos=(205.74, 170.18))
ta1 = term('TA1', 12, 304.8, 203.2, H1, 'H1 out (20 AWG)', valpos=(304.8, 226.06), refpos=(304.8, 184.15))
Part('AATV:Penetration', 'PEN2', 'A2: H1 cable, epoxy-potted', 304.8, 241.3,
     refpos=(309.88, 238.76), valpos=(309.88, 245.11), just='left')
text('All Board A terminals: 5.08 mm pitch\n(0.2 in, fits the breadboard grid).', (180.34, 205.74), NOTE)

# ================================================================== BOARD B
tb1 = term('TB1', 12, 368.3, 66.04, H1, 'H1 in (20 AWG)', refpos=(368.3, 46.99), valpos=(368.3, 86.36))
servo_nets = []
for s in ('M4', 'M5', 'M6', 'M7'):
    servo_nets += [f'{s}_PWM', 'SERVO_7V5', 'GND']
tb2 = term('TB2', 12, 368.3, 129.54, servo_nets, 'Servo cable (20 AWG)', refpos=(368.3, 110.49), valpos=(368.3, 149.86))
tb3 = term('TB3', 2, 368.3, 165.1, ['THR_PWM', 'GND'], 'Thruster ESC signal', refpos=(368.3, 160.02), valpos=(368.3, 171.45))
tb4 = term('TB4', 2, 368.3, 182.88, ['PUMP_PWM', 'GND'], 'Pump ESC signal', refpos=(368.3, 177.8), valpos=(368.3, 189.23))
tb5 = term('TB5', 3, 368.3, 200.66, ['+3V3', 'GND', 'LEAK_REAR'], 'Rear leak sensor', refpos=(368.3, 194.31), valpos=(368.3, 208.28))
if WHEELS:
    tb7 = term('TB7', 4, 368.3, 220.98, ['DRV_L_PWM', 'GND', 'DRV_R_PWM', 'GND'], 'Wheel ESC signals',
               refpos=(368.3, 213.36), valpos=(368.3, 229.87))
tb6 = term('TB6', 2, 434.34, 50.8, ['SERVO_7V5', 'GND'], '7.5 V in (14 AWG)', mirror=True,
           refpos=(434.34, 45.72), valpos=(434.34, 57.15))
c1 = Part('Device:C_Polarized', 'C1', '1000uF 16V', 436.88, 76.2,
          refpos=(439.42, 74.93), valpos=(439.42, 77.47), just='left')
stub(c1, 1, 'SERVO_7V5'); stub(c1, 2, 'GND')
text('Board B:\n- 7.5 V + GND rails: strip of\n  14 AWG soldered along strips\n- No 12 V on the breadboard\n- 5.08 mm terminals only',
     (412.75, 96.52), NOTE)

# ================================================================== REAR off-board
def busbar(ref, X, Y, net, value, inputs, outputs):
    t = Part('Connector:Screw_Terminal_01x08', ref, value, X, Y,
             refpos=(X, Y - 15.24), valpos=(X, Y + 17.78))
    pts = [t.P(i) for i in range(1, 9)]
    for a, b in zip(pts, pts[1:]):
        wire(a, b)
    label(net, pts[0], 90)
    return t
bp = busbar('BB1', 492.76, 66.04, 'VBAT', '+12 V bus bar (>=30 A)', 2, 0)
bn = busbar('BB2', 492.76, 116.84, 'GND', 'GND bus bar (>=30 A)', 2, 0)
text('Bus bars (screw studs, ring terminals):\n'
     '+ in: D1 pins 1+2 (two 14 AWG)\n'
     '+ out: buck, pump ESC, D2 thruster'
     + (',\n        D5 wheel L, D5 wheel R' if WHEELS else '') +
     '\nGND bar mirrors the + bar.', (499.11, 48.26), NOTE)
pf = Part('power:PWR_FLAG', '#FLG01', 'PWR_FLAG', 480.06, 58.42, hide_ref=True, hide_val=True)
wire((480.06, 58.42), (487.68, 58.42))
u1 = Part('AATV:Buck_12V_7V5', 'U1', '12 V -> 7.5 V buck (>=5 A)', 497.84, 157.48,
          refpos=(497.84, 149.86), valpos=(497.84, 165.1))
stub(u1, 1, 'VBAT'); stub(u1, 2, 'GND'); stub(u1, 3, 'SERVO_7V5'); stub(u1, 4, 'GND')
u3 = Part('AATV:ESC_Brushed', 'U3', 'Pump ESC (brushed, reversible)', 541.02, 190.5,
          refpos=(541.02, 182.88), valpos=(541.02, 203.2))
stub(u3, 1, 'VBAT'); stub(u3, 2, 'GND'); nc(u3, 3); stub(u3, 4, 'PUMP_PWM'); stub(u3, 5, 'GND')
stub(u3, 6, 'PUMP_M+'); stub(u3, 7, 'PUMP_M-')
text('Pump ESC sits dry so any brushed ESC\nor H-bridge works. BEC wire cut.', (515.62, 210.82), NOTE)
Part('AATV:Penetration', 'PEN3', 'R2: 20 AWG cables potted (H1, servo, THR sig' + (', wheel sig' if WHEELS else '') + ')', 368.3, 241.3,
     refpos=(373.38, 238.76), valpos=(373.38, 245.11), just='left')
Part('AATV:Penetration', 'PEN4', 'R3: 14 AWG cables potted (trunk, thruster pwr, pump motor' + (', wheel pwr' if WHEELS else '') + ')',
     480.06, 241.3, refpos=(485.14, 238.76), valpos=(485.14, 245.11), just='left')

# ================================================================== WET ZONE
def dt_pair(tag, n, X, Y, box_nets, dev_nets, value, sub):
    """Deutsch DT mated pair. Left = box/source side (DT06 plug, sockets). Right = device side (DT04 receptacle, pins)."""
    a = Part(f'Connector:Conn_01x{n:02d}_Socket', f'{tag}A', f'{value} DT06-{n}S', X, Y,
             refpos=(X - 3.81, Y - n * 1.27 - 3.81), valpos=(X - 3.81, Y + n * 1.27 + 5.08))
    b = Part(f'Connector:Conn_01x{n:02d}_Pin', f'{tag}B', f'DT04-{n}P', X + 1, Y,
             refpos=(X + 5.08, Y - n * 1.27 - 3.81), valpos=(X + 5.08, Y + n * 1.27 + 7.62))
    for i in range(n):
        for part, nets in ((a, box_nets), (b, dev_nets)):
            net = nets[i]
            if net is None:
                nc(part, i + 1)
            else:
                stub(part, i + 1, net, 5.08, 1.0)
    text(sub, (X - 3.81, Y + n * 1.27 + 10.16), 1.0)
    return a, b

# --- battery pack
bt1 = Part('Device:Battery', 'BT1', '3S LiPo (wet, no box)', 22.86, 300.99,
           refpos=(26.67, 299.72), valpos=(26.67, 302.26), just='left')
sw1 = Part('Switch:SW_SPST', 'SW1', 'Kill switch, low side, >=30 A', 40.64, 317.5,
           refpos=(40.64, 314.96), valpos=(40.64, 321.31))
f1 = Part('Device:Fuse', 'F1', ('25 A' if WHEELS else '20 A') + ' ATC, waterproof holder', 40.64, 289.56, rot=90,
          refpos=(40.64, 287.02), valpos=(40.64, 284.48))
bp_, bn_ = bt1.P(1), bt1.P(2)
path(bp_, (bp_[0], 289.56), f1.P(1))
path(bn_, (bn_[0], 317.5), sw1.P(1))
fo = f1.P(2); wire(fo, (55.88, fo[1])); label('VBAT', (55.88, fo[1]), 0)
so = sw1.P(2); wire(so, (55.88, so[1])); label('GND', (55.88, so[1]), 0)
text('Battery side harness: battery + -> F1 -> split to D1 pins 1, 2;\nbattery - -> SW1 -> split to D1 pins 3, 4.\n'
     'Splits: solder + adhesive heat-shrink.\nCharge through a DT04-4P -> XT60 adapter.', (12.7, 330.2), NOTE)
dt_pair('D1', 4, 81.28, 303.53, ['VBAT', 'VBAT', 'GND', 'GND'], ['VBAT', 'VBAT', 'GND', 'GND'],
        'D1 battery', 'D1 battery: 2 contacts per pole = 26 A.\nTrunk to rear box: 4 x 14 AWG.')

# --- D4 H1 (between main and rear dryboxes)
dt_pair('D4', 12, 152.4, 300.99, H1, H1, 'D4 harness H1', 'D4: main box <-> rear box, 12 x 20 AWG.\nPins 6-7 spare in Plan B.')

# --- D3 servos
dt_pair('D3', 12, 228.6, 300.99, servo_nets, servo_nets, 'D3 servos', 'D3: 4 servo leads, 12 x 20 AWG.')
for i, s in enumerate(('M4', 'M5', 'M6', 'M7')):
    y = 276.86 + i * 15.24
    m = Part('Motor:Motor_Servo', s, ['Rudder', 'Rudder', 'Elevator', 'Elevator'][i] + ' servo', 274.32, y,
             refpos=(278.13, y - 3.81), valpos=(278.13, y + 6.35), just='left')
    stub(m, 1, f'{s}_PWM', 2.54, 1.0); stub(m, 2, 'SERVO_7V5', 2.54, 1.0); stub(m, 3, 'GND', 2.54, 1.0)

# --- D2 aft: thruster ESC (wet) + pump motor
dt_nets = ['VBAT', 'GND', 'THR_PWM', 'GND', 'PUMP_M+', 'PUMP_M-', None, None]
dt_pair('D2', 8, 337.82, 300.99, dt_nets, dt_nets, 'D2 aft',
        'D2: 1-2 thruster ESC 12 V (14 AWG), 3-4 ESC signal (20 AWG),\n5-6 pump motor (14 AWG), 7-8 spare (2nd pump).')
u2 = Part('AATV:ESC_TD1.2', 'U2', 'TD1.2 ESC (waterproof, wet)', 386.08, 292.1,
          refpos=(386.08, 284.48), valpos=(386.08, 304.8))
stub(u2, 1, 'VBAT', 2.54, 1.0); stub(u2, 2, 'GND', 2.54, 1.0); stub(u2, 3, 'THR_PWM', 2.54, 1.0); stub(u2, 4, 'GND', 2.54, 1.0)
mt1 = Part('AATV:Thruster_TD1.2', 'MT1', 'TD1.2 thruster', 421.64, 292.1, refpos=(421.64, 284.48), valpos=(421.64, 299.72))
for k in (5, 6, 7):
    wire(u2.P(k), mt1.P(k - 4))
text('Factory thruster cable stays on the ESC.', (375.92, 309.88), 1.0)
m3 = Part('Motor:Motor_DC', 'M3', 'Ballast pump, 12 V brushed (TBD, <=5 A)', 391.16, 335.28,
          refpos=(395.0, 334.0), valpos=(395.0, 336.55), just='left')
stub(m3, 1, 'PUMP_M+', 2.54, 1.0); stub(m3, 2, 'PUMP_M-', 2.54, 1.0)

# --- D5 wheels (Plan A)
if WHEELS:
    wn = ['VBAT', 'GND', 'VBAT', 'GND', 'DRV_L_PWM', 'GND', 'DRV_R_PWM', 'GND']
    dt_pair('D5', 8, 462.28, 300.99, wn, wn, 'D5 wheels',
            'D5: 1-4 wheel ESC power (14 AWG),\n5-8 wheel ESC signals (20 AWG).')
    for i, (u, m, sig, y) in enumerate((('U4', 'M1', 'DRV_L_PWM', 284.48), ('U5', 'M2', 'DRV_R_PWM', 325.12))):
        e = Part('AATV:ESC_Brushed', u, f'Wheel ESC {"L" if i == 0 else "R"} (waterproof)', 513.08, y,
                 refpos=(513.08, y - 7.62), valpos=(513.08, y + 13.97))
        stub(e, 1, 'VBAT', 2.54, 1.0); stub(e, 2, 'GND', 2.54, 1.0); nc(e, 3)
        stub(e, 4, sig, 2.54, 1.0); stub(e, 5, 'GND', 2.54, 1.0)
        mo = Part('Motor:Motor_DC', m, f'Driven wheel {"L" if i == 0 else "R"} (550)', 543.56, y + 2.54,
                  refpos=(547.37, y + 1.27), valpos=(547.37, y + 3.81), just='left')
        path(e.P(6), (mo.P(1)[0], e.P(6)[1]), mo.P(1))
        path(e.P(7), (530.86, e.P(7)[1]), (530.86, mo.P(2)[1]), mo.P(2))
else:
    text('PLAN B: no front driven motors.\nNo D5, no wheel ESCs, no TB7.\nH1 pins 6-7 and Pico GP17/GP18 spare.\nFuse drops to 20 A.',
         (462.28, 287.02), 1.8, bold=True)

text('Deutsch DT: 13 A per contact, 14-20 AWG, IP68 when every cavity is filled\n(cavity plugs in unused ones). Source side gets sockets (DT06 plug).',
     (12.7, 360.68), NOTE)

write(OUT)
print('ok', PLAN, len(ITEMS))
