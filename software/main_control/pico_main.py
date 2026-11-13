# Pico firmware (MicroPython). Save on the Pico as main.py.
#
# Reads lines from USB serial:   C thr rud elv pump valve arm emerg
#   thr, rud, elv  -100..100       pump, valve, arm, emerg  0 or 1
# Pins follow software/combined_test.py, the version verified on the bench:
#   servos GP0, GP1, GP3, GP4, thruster GP2, pump GP16 (200R + 10k gate pull-down).
# The valve is not in that test (its switch is not built yet), so GP18 from CLAUDE.md
# is UNVERIFIED. CLAUDE.md's pin map (servos GP12-15, thruster GP16, pump GP19)
# disagrees with the bench wiring; ask the team which one the board will use.
#
# Safety:
#   - Boots DISARMED. To arm, the Pico must first see arm=0, then arm=1. So a laptop
#     that is still "armed" cannot arm the sub after a Pico reboot or a link drop.
#   - Link silent for TIMEOUT_MS -> disarm, thruster/fins neutral, pump off, valve closed.
#   - Disarmed -> everything neutral/off, except emergency ascent.
#   - emerg=1 (LB): thruster neutral, fins neutral, valve closed, pump ON. Works
#     even when disarmed. The pump only moves water that is in the tank; running it
#     dry for long is not checked here.
#   - Pump and valve are never on together.
#   - Thruster held at neutral for ESC_ARM_MS after boot, and capped by THR_MAX_DELTA
#     (100 us is about 20 %; raise in small steps after measuring current).
#   - Any exit drives pump/valve low and the ESC to neutral.
#
# NOT included yet: battery monitor (ADS1115), leak sensor, sonar.

import select
import sys
import time

from machine import Pin, PWM

# ---- pins ------------------------------------------------------------------
# combined_test.py calls them Servo 1..4 on GP0, GP1, GP3, GP4. Which servo is a
# rudder and which is an elevator is MY GUESS (1,2 rudders; 3,4 elevators). Run
# the servo section of combined_test.py, see which fin moves, and swap if needed.
RUDDER_PINS = (0, 1)
ELEVATOR_PINS = (3, 4)
THR_PIN = 2
VALVE_PIN = 18               # unverified, switch not built yet
PUMP_PIN = 16

# ---- tuning ----------------------------------------------------------------
NEUTRAL = 1500
SERVO_SPAN = 400             # us each side of centre for a full stick
THR_MAX_DELTA = 100          # us each side of neutral at full stick. 500 us = 100 % of the
                             # ESC's 1000-2000 us range, so 100 us = 20 %. This is the
                             # hard cap: no command can push the pulse past 1500 +- 100.
# +1: stick forward = longer pulse (1600 us, "Direction A" in combined_test.py).
# Set to -1 if, on the bench, stick forward pushes the sub backward. Forward is the
# strong direction (about 2.6x reverse), so the strong push should be stick forward.
THR_DIR = 1
ESC_ARM_MS = 4000
TIMEOUT_MS = 500
# Flip a sign to -1 if that fin moves the wrong way on the vehicle. Stick up must
# tilt the nose up, so check the elevators on the bench.
RUDDER_DIR = (1, 1)
ELEVATOR_DIR = (1, -1)       # elevators are usually mirrored; check on the bench

# ---- outputs (pump and valve are created low) -------------------------------
pump = Pin(PUMP_PIN, Pin.OUT, value=0)
valve = Pin(VALVE_PIN, Pin.OUT, value=0)


def make_pwm(pin):
    p = PWM(Pin(pin))
    p.freq(50)
    p.duty_ns(NEUTRAL * 1000)
    return p


rudders = [make_pwm(p) for p in RUDDER_PINS]
elevators = [make_pwm(p) for p in ELEVATOR_PINS]
thruster = make_pwm(THR_PIN)


def clamp(v, lo=-100, hi=100):
    return max(lo, min(hi, v))


def set_us(pwm, us):
    pwm.duty_ns(int(us * 1000))


def apply(thr, rud, elv, want_pump, want_valve, esc_ready):
    if not esc_ready:
        thr = 0
    set_us(thruster, NEUTRAL + THR_DIR * THR_MAX_DELTA * thr / 100)
    for pwm, d in zip(rudders, RUDDER_DIR):
        set_us(pwm, NEUTRAL + d * SERVO_SPAN * rud / 100)
    for pwm, d in zip(elevators, ELEVATOR_DIR):
        set_us(pwm, NEUTRAL + d * SERVO_SPAN * elv / 100)
    if want_pump and want_valve:            # never both
        want_pump = want_valve = 0
    # switch the one that is turning OFF first
    if not want_pump:
        pump.value(0)
    if not want_valve:
        valve.value(0)
    if want_pump:
        pump.value(1)
    if want_valve:
        valve.value(1)


def parse(line):
    parts = line.split()
    if len(parts) != 8 or parts[0] != "C":
        return None
    try:
        thr, rud, elv = (clamp(int(x)) for x in parts[1:4])
        p, v, arm, emerg = (1 if int(x) else 0 for x in parts[4:8])
    except ValueError:
        return None
    return thr, rud, elv, p, v, arm, emerg


poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

boot = time.ticks_ms()
last_cmd = time.ticks_ms()
last_status = time.ticks_ms()
cmd = (0, 0, 0, 0, 0, 0, 0)
armed = False
need_disarmed_first = True      # must see arm=0 before arm=1 is accepted
buf = ""

try:
    while True:
        while poll.poll(0):
            ch = sys.stdin.read(1)
            if ch == "\n":
                parsed = parse(buf)
                buf = ""
                if parsed:
                    cmd = parsed
                    last_cmd = time.ticks_ms()
                    if cmd[5] == 0:
                        need_disarmed_first = False
                        armed = False
                    elif not need_disarmed_first:
                        armed = True
            elif len(buf) < 60:
                buf += ch
            else:
                buf = ""                    # junk, throw away

        now = time.ticks_ms()
        stale = time.ticks_diff(now, last_cmd) > TIMEOUT_MS
        esc_ready = time.ticks_diff(now, boot) > ESC_ARM_MS
        if stale:
            cmd = (0, 0, 0, 0, 0, 0, 0)
            armed = False
            need_disarmed_first = True

        thr, rud, elv, p, v, _, emerg = cmd
        if emerg:
            apply(0, 0, 0, 1, 0, esc_ready)      # emergency ascent
            armed = False
        elif armed:
            apply(thr, rud, elv, p, v, esc_ready)
        else:
            apply(0, 0, 0, 0, 0, esc_ready)

        if time.ticks_diff(now, last_status) > 500:
            last_status = now
            state = "NO-LINK" if stale else ("EMERGENCY" if emerg else ("ARMED" if armed else "safe"))
            print("S thr=%d rud=%d elv=%d pump=%d valve=%d %s" % (thr, rud, elv, p, v, state))
        time.sleep_ms(10)
finally:
    pump.value(0)
    valve.value(0)
    set_us(thruster, NEUTRAL)
