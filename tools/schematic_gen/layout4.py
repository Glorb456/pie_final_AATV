"""AA-TV v7 schematic. usage: python3 layout2.py A|B out.kicad_sch project_name"""
import sys
import gen
from gen import *

OUT = sys.argv[1]
gen.PROJECT = 'AATV'
WHEELS = False
NOTE = 1.27
TITLE_SZ = 2.54

gen.TITLE.update({
    'title': 'AA-TV electrical v8.1: no wheels, 6x Deutsch DTP 4-pin, servos potted',
    'rev': 'v8.1',
    'c1': 'Two solder-boards (Board A main drybox, Board B rear drybox). Cables epoxy-potted through drybox walls.',
    'c2': 'Only connectors: 6x Deutsch DTP 4-pin in the wet zone + 5.08 mm screw terminals / bus bars inside dryboxes. Servo leads potted.',
    'c3': 'Wire: 14 AWG marine for everything outside the boxes, every DTP contact and all power; 20 AWG hookup for on-board jumpers.',
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

text('AA-TV wiring v8.1: no wheels. 6x Deutsch DTP 4-pin (wet zone), servo leads + cables epoxy-potted into dryboxes, 14 AWG marine outside / 20 AWG on boards.',
     (12.7, 6.35), 3, bold=True)
text('BUOY  (surface, dry)', (12.7, 17.78), TITLE_SZ, bold=True)
text('MAIN DRYBOX  (upper, on hull)', (170.18, 17.78), TITLE_SZ, bold=True)
text('BOARD A: Pico solder-board', (177.8, 30.48), 1.8, bold=True)
text('REAR DRYBOX  (inside open rear endcap)', (347.98, 17.78), TITLE_SZ, bold=True)
text('BOARD B: servo / signal board', (353.06, 30.48), 1.8, bold=True)
text('Off-board, in rear drybox', (469.9, 30.48), 1.8, bold=True)
text('WET ZONE  (flooded hull, open rear endcap, splash areas): Deutsch DTP 4-pin connectors live here', (12.7, 254.0), TITLE_SZ, bold=True)
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

H1 = ['M4_PWM', 'M5_PWM', 'M6_PWM', 'M7_PWM', 'THR_PWM', 'H1_SPARE6', 'H1_SPARE7', 'PUMP_PWM',
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
ta1 = term('TA1', 12, 304.8, 203.2, H1, 'H1 out (14 AWG)', valpos=(304.8, 226.06), refpos=(304.8, 184.15))
Part('AATV:Penetration', 'PEN2', 'A2: H1 cable, epoxy-potted', 304.8, 241.3,
     refpos=(309.88, 238.76), valpos=(309.88, 245.11), just='left')
text('All Board A terminals: 5.08 mm pitch\n(0.2 in, fits the breadboard grid).\nTA1 pins 6-7: spare H1 conductors.', (180.34, 205.74), NOTE)

# ================================================================== BOARD B
tb1 = term('TB1', 12, 368.3, 66.04, H1, 'H1 in (14 AWG)', refpos=(368.3, 46.99), valpos=(368.3, 86.36))
tb2 = term('TB2', 6, 368.3, 109.22, ['M4_PWM', 'SERVO_7V5', 'GND', 'M5_PWM', 'SERVO_7V5', 'GND'], 'Rudder servo leads (potted)', refpos=(368.3, 99.06), valpos=(368.3, 121.92))
tb3 = term('TB3', 6, 368.3, 139.7, ['M6_PWM', 'SERVO_7V5', 'GND', 'M7_PWM', 'SERVO_7V5', 'GND'], 'Elevator servo leads (potted)', refpos=(368.3, 129.54), valpos=(368.3, 152.4))
tb4 = term('TB4', 2, 368.3, 167.64, ['THR_PWM', 'GND'], 'Thruster ESC signal (to D3)', refpos=(368.3, 162.56), valpos=(368.3, 173.99))
tb5 = term('TB5', 2, 368.3, 182.88, ['PUMP_PWM', 'GND'], 'Pump ESC signal (U3)', refpos=(368.3, 177.8), valpos=(368.3, 189.23))
tb6 = term('TB6', 3, 368.3, 200.66, ['+3V3', 'GND', 'LEAK_REAR'], 'Rear leak sensor', refpos=(368.3, 194.31), valpos=(368.3, 208.28))
tb7 = term('TB7', 2, 434.34, 50.8, ['SERVO_7V5', 'GND'], '7.5 V in (14 AWG)', mirror=True,
           refpos=(434.34, 45.72), valpos=(434.34, 57.15))
c1 = Part('Device:C_Polarized', 'C1', '1000uF 16V', 436.88, 76.2,
          refpos=(439.42, 74.93), valpos=(439.42, 77.47), just='left')
stub(c1, 1, 'SERVO_7V5'); stub(c1, 2, 'GND')
text('Board B:\n- 7.5 V + GND rails: strip of\n  14 AWG soldered along strips\n- Servo + / - jumpers: 14 AWG\n- Signal jumpers: 20 AWG\n- No 12 V on the breadboard\n- TB1 pins 6-7: spare, unused',
     (412.75, 96.52), NOTE)

# ================================================================== REAR off-board
def busbar(ref, X, Y, net, value):
    t = Part('Connector:Screw_Terminal_01x05', ref, value, X, Y,
             refpos=(X, Y - 10.16), valpos=(X, Y + 12.7))
    pts = [t.P(i) for i in range(1, 6)]
    for a, b in zip(pts, pts[1:]):
        wire(a, b)
    label(net, pts[0], 90)
    return t
busbar('BB1', 492.76, 66.04, 'VBAT', '+12 V bus bar (>=30 A)')
busbar('BB2', 492.76, 104.14, 'GND', 'GND bus bar (>=30 A)')
text('Bus bars (screw studs, ring terminals):\nin: D1 trunk, one 14 AWG per pole\nout: buck U1, pump ESC U3,\n     D3 thruster ESC feed (1 stud spare)', (499.11, 53.34), NOTE)
pf = Part('power:PWR_FLAG', '#FLG01', 'PWR_FLAG', 480.06, 60.96, hide_ref=True, hide_val=True)
wire((480.06, 60.96), (487.68, 60.96))
u1 = Part('AATV:Buck_12V_7V5', 'U1', '12 V -> 7.5 V buck (>=5 A)', 497.84, 149.86,
          refpos=(497.84, 142.24), valpos=(497.84, 157.48))
stub(u1, 1, 'VBAT'); stub(u1, 2, 'GND'); stub(u1, 3, 'SERVO_7V5'); stub(u1, 4, 'GND')
u3 = Part('AATV:ESC_Brushed', 'U3', 'Pump ESC (brushed, reversible)', 541.02, 185.42,
          refpos=(541.02, 177.8), valpos=(541.02, 198.12))
stub(u3, 1, 'VBAT'); stub(u3, 2, 'GND'); nc(u3, 3); stub(u3, 4, 'PUMP_PWM'); stub(u3, 5, 'GND')
stub(u3, 6, 'PUMP_M+'); stub(u3, 7, 'PUMP_M-')
text('Pump ESC sits dry, so any brushed ESC\nwith reverse works. BEC wire cut.\nMotor leads -> R3 -> D2 pins 1-2\n(extend with 14 AWG if short).', (515.62, 205.74), NOTE)
Part('AATV:Penetration', 'PEN3', 'R2: signal cables potted (H1, 4 servo leads, THR sig)', 368.3, 241.3,
     refpos=(373.38, 238.76), valpos=(373.38, 245.11), just='left')
Part('AATV:Penetration', 'PEN4', 'R3: power cables potted (trunk, thruster feed, pump)', 480.06, 241.3,
     refpos=(485.14, 238.76), valpos=(485.14, 245.11), just='left')

# ================================================================== WET ZONE
def dt_pair(tag, X, Y, box_nets, dev_nets, value, sub):
    """Deutsch DTP 4-pin mated pair. Left = box/source side (DTP06-4S plug, sockets). Right = device side (DTP04-4P receptacle)."""
    n = 4
    a = Part('Connector:Conn_01x04_Socket', f'{tag}A', f'{value} DTP06-4S', X, Y,
             refpos=(X - 3.81, Y - 8.89), valpos=(X - 3.81, Y + 10.16))
    b = Part('Connector:Conn_01x04_Pin', f'{tag}B', 'DTP04-4P', X + 1, Y,
             refpos=(X + 5.08, Y - 8.89), valpos=(X + 5.08, Y + 12.7))
    for i in range(n):
        for part, nets in ((a, box_nets), (b, dev_nets)):
            if nets[i] is None:
                nc(part, i + 1)
            else:
                stub(part, i + 1, nets[i], 5.08, 1.0)
    if sub:
        text(sub, (X - 3.81, Y + 15.24), 1.0)
    return a, b

# --- battery pack + D1
bt1 = Part('Device:Battery', 'BT1', '3S LiPo (wet, no box)', 22.86, 300.99,
           refpos=(26.67, 299.72), valpos=(26.67, 302.26), just='left')
sw1 = Part('Switch:SW_SPST', 'SW1', 'Kill switch, low side, >=30 A', 40.64, 317.5,
           refpos=(40.64, 314.96), valpos=(40.64, 321.31))
f1 = Part('Device:Fuse', 'F1', '20 A ATC, waterproof holder', 40.64, 289.56, rot=90,
          refpos=(40.64, 287.02), valpos=(40.64, 284.48))
bp_, bn_ = bt1.P(1), bt1.P(2)
path(bp_, (bp_[0], 289.56), f1.P(1))
path(bn_, (bn_[0], 317.5), sw1.P(1))
fo = f1.P(2); wire(fo, (55.88, fo[1])); label('VBAT', (55.88, fo[1]), 0)
so = sw1.P(2); wire(so, (55.88, so[1])); label('GND', (55.88, so[1]), 0)
text('Battery side: battery + -> F1 -> D1 pin 1; battery - -> SW1 -> D1 pin 2.\n'
     'D1 pins 3-4: dummy loop on each half (short 14 AWG piece,\ncontact on each end) so every cavity is sealed. No splits.\n'
     'Charge through a DTP04-4P -> XT60 adapter.', (12.7, 330.2), NOTE)
dt_pair('D1', 81.28, 303.53, ['VBAT', 'GND', 'D1_LOOP', 'D1_LOOP'], ['VBAT', 'GND', 'D1_LOOP', 'D1_LOOP'],
        'D1 battery', 'D1: 1 + / 2 GND (25 A each); 3-4 dummy loop.')

# --- H1 split over D6, D7, D8
dt_pair('D4', 152.4, 279.4, H1[0:4], H1[0:4], 'D4 H1 1-4', None)
dt_pair('D5', 152.4, 304.8, H1[4:8], H1[4:8], 'D5 H1 5-8', None)
dt_pair('D6', 152.4, 330.2, H1[8:12], H1[8:12], 'D6 H1 9-12', 'H1 main <-> rear: 12 x 14 AWG\nover D4, D5, D6. Pins 6-7 spare.')

# --- servos: leads potted straight into the rear drybox (R2), no connector
text('Servo leads: potted straight into the rear drybox at R2,\nno connector. BACKUP if a lead can\'t reach the box:\none MGYOO 20 AWG 3-pin waterproof\nconnector per servo, inline in the wet zone.', (226.06, 335.28), NOTE)
for i, s in enumerate(('M4', 'M5', 'M6', 'M7')):
    y = 276.86 + i * 15.24
    m = Part('Motor:Motor_Servo', s, ['Rudder', 'Rudder', 'Elevator', 'Elevator'][i] + ' servo', 274.32, y,
             refpos=(278.13, y - 3.81), valpos=(278.13, y + 6.35), just='left')
    stub(m, 1, f'{s}_PWM', 2.54, 1.0); stub(m, 2, 'SERVO_7V5', 2.54, 1.0); stub(m, 3, 'GND', 2.54, 1.0)

# --- D3 thruster ESC (wet)
dt_pair('D3', 337.82, 289.56, ['VBAT', 'GND', 'THR_PWM', 'GND'], ['VBAT', 'GND', 'THR_PWM', 'GND'],
        'D3 thruster', 'D3: 1 +12 V, 2 GND, 3 PWM (yellow),\n4 signal GND (white). All 14 AWG.')
u2 = Part('AATV:ESC_TD1.2', 'U2', 'TD1.2 ESC (waterproof, wet)', 386.08, 292.1,
          refpos=(386.08, 284.48), valpos=(386.08, 304.8))
stub(u2, 1, 'VBAT', 2.54, 1.0); stub(u2, 2, 'GND', 2.54, 1.0); stub(u2, 3, 'THR_PWM', 2.54, 1.0); stub(u2, 4, 'GND', 2.54, 1.0)
mt1 = Part('AATV:Thruster_TD1.2', 'MT1', 'TD1.2 thruster', 421.64, 292.1, refpos=(421.64, 284.48), valpos=(421.64, 299.72))
for k in (5, 6, 7):
    wire(u2.P(k), mt1.P(k - 4))
text('Factory thruster cable stays on the ESC.', (375.92, 309.88), 1.0)

# --- D2 pump
dt_pair('D2', 337.82, 337.82, ['PUMP_M+', 'PUMP_M-', 'D2_LOOP', 'D2_LOOP'], ['PUMP_M+', 'PUMP_M-', 'D2_LOOP', 'D2_LOOP'],
        'D2 pump', 'D2: 1 pump +, 2 pump -; 3-4 dummy loop.')
m3 = Part('Motor:Motor_DC', 'M3', 'Ballast pump, 12 V brushed (TBD, <=5 A)', 391.16, 337.82,
          refpos=(395.0, 336.55), valpos=(395.0, 339.09), just='left')
stub(m3, 1, 'PUMP_M+', 2.54, 1.0); stub(m3, 2, 'PUMP_M-', 2.54, 1.0)

text('Deutsch DTP: size 12 contacts, 12-14 AWG, 25 A each. Every cavity is filled: unused pins get a dummy wire loop.\n'
     'Source side (battery / drybox) gets the DTP06 plug with socket contacts.', (12.7, 360.68), NOTE)

write(OUT)
print('ok', len(ITEMS))
