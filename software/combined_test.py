# combined_test.py — servo + thruster + pump bench test (MicroPython, Raspberry Pi Pico)
#
# Combines sysarch_demo.py (servos), thrustertest.py (thruster ESC) and pumptest.py (pump).
#
# Wiring (bench test):
#   Servo 1   GP0 (physical pin 1) -> 200R -> servo signal
#   Servo 2   GP1 (physical pin 2) -> 200R -> servo signal
#   Servo 3   GP3 (physical pin 5) -> 200R -> servo signal
#   Servo 4   GP4 (physical pin 6) -> 200R -> servo signal
#   Thruster  GP2 (physical pin 4) -> 200R -> thruster signal (white); 10k from signal to GND
#             Thruster signal ground (thin black) -> Pico GND
#             Thruster power pair -> 12 V supply or fused battery (NOT through the Pico)
#   Pump      GP16 (physical pin 21) -> 200R -> Q1 IRLZ44N gate, 10k gate pull-down to GND
#             +24 V -> pump -> Q1 drain; Q1 source -> GND; 1N5822 flyback across the pump
#   All grounds shared: Pico GND, servo supply GND, thruster signal GND, Q1 source.
#
# Order of the test:
#   1. Pump gate is driven low and the ESC gets a steady 1500 us immediately, so the
#      thruster arms while the servos are being tested.
#   2. Servos, one at a time: each sweeps 1000 / 1500 / 2000 / 1500 us while the
#      others hold centre, so you can tell which servo is on which pin.
#   3. Thruster: ramp up to +MAX_DELTA, back to stop, down to -MAX_DELTA, back to stop.
#   4. Pump: on/off cycles. The on-board LED mirrors the pump pin.
#   Only one subsystem moves at a time. Set RUN_* below to skip a section.
#
# SAFETY
#   - Clamp the thruster down; keep hands, wires and loose items away from the prop.
#     Dry runs: low throttle, brief. MAX_DELTA = 500 would be 100 %; start at 100 (~20 %).
#   - Ctrl-C at any time: pump off, thruster back to stop, servo pulses stopped.

from machine import Pin, PWM
import time

# ---- pins ----------------------------------------------------------------
SERVO_PINS = (0, 1, 3, 4)   # GP0 (pin 1), GP1 (pin 2), GP3 (pin 5), GP4 (pin 6)
THR_PIN = 2             # GP2 (pin 4)
PUMP_PIN = 16           # GP16 (pin 21), unchanged from pumptest.py

# ---- which sections to run ----------------------------------------------
RUN_SERVOS = True
RUN_THRUSTER = True
RUN_PUMP = True

# ---- servo settings ------------------------------------------------------
SERVO_SWEEP = (1000, 1500, 2000, 1500)   # us; 1000-2000 is a safe range
SERVO_DWELL = 1         # seconds at each position
SERVO_SWEEPS = 2        # sweeps per servo
SERVO_GAP = 1           # seconds between servos

# ---- thruster settings ---------------------------------------------------
NEUTRAL = 1500          # us, stop
MAX_DELTA = 100         # us away from neutral; raise in small steps once it behaves
STEP = 10               # us per ramp step
STEP_TIME = 0.2         # seconds per ramp step
HOLD_TIME = 2           # seconds at the top of each ramp
ARM_TIME = 4            # minimum seconds of neutral before the first move

# ---- pump settings -------------------------------------------------------
PUMP_ON_TIME = 3        # seconds
PUMP_OFF_TIME = 3       # seconds
PUMP_CYCLES = 3


# ---- set-up: make the outputs safe first ---------------------------------
pump = Pin(PUMP_PIN, Pin.OUT, value=0)   # gate driven low from the start
try:
    led = Pin("LED", Pin.OUT, value=0)   # Pico and Pico W
except (TypeError, ValueError):
    led = Pin(25, Pin.OUT, value=0)      # very old firmware

esc = PWM(Pin(THR_PIN))
esc.freq(50)
esc.duty_ns(NEUTRAL * 1000)              # start arming right away
arm_start = time.ticks_ms()

servos = []
for n in SERVO_PINS:
    s = PWM(Pin(n))
    s.freq(50)
    servos.append(s)


# ---- helpers -------------------------------------------------------------
def servo_pulse(s, us):
    s.duty_ns(us * 1000)


def servos_centre():
    for s in servos:
        servo_pulse(s, 1500)


def servos_stop():
    for s in servos:
        s.duty_ns(0)    # stop sending pulses


def thr_pulse(us):
    esc.duty_ns(us * 1000)


def thr_ramp(start, end):
    step = STEP if end > start else -STEP
    for us in range(start, end + step, step):
        thr_pulse(us)
        print("  thruster %d us" % us)
        time.sleep(STEP_TIME)


def pump_on():
    pump.value(1)
    led.value(1)
    print("  PUMP ON   (GP%d = 1)" % PUMP_PIN)


def pump_off():
    pump.value(0)
    led.value(0)
    print("  PUMP OFF  (GP%d = 0)" % PUMP_PIN)


# ---- test sections -------------------------------------------------------
def test_servos():
    print("\n[1] Servos on GP%s, one at a time, %d sweeps each"
          % (", GP".join(str(n) for n in SERVO_PINS), SERVO_SWEEPS))
    servos_centre()     # everything holds centre while one servo moves
    time.sleep(SERVO_GAP)
    for k, (n, s) in enumerate(zip(SERVO_PINS, servos), 1):
        print(" Servo %d of %d (GP%d)" % (k, len(servos), n))
        for i in range(1, SERVO_SWEEPS + 1):
            print("  sweep %d of %d" % (i, SERVO_SWEEPS))
            for us in SERVO_SWEEP:
                servo_pulse(s, us)
                print("   GP%d %d us" % (n, us))
                time.sleep(SERVO_DWELL)
        servo_pulse(s, 1500)
        time.sleep(SERVO_GAP)
    print(" All servos centred")


def test_thruster():
    print("\n[2] Thruster ESC on GP%d, limit +/-%d us" % (THR_PIN, MAX_DELTA))
    thr_pulse(NEUTRAL)
    waited = time.ticks_diff(time.ticks_ms(), arm_start) / 1000
    if waited < ARM_TIME:
        print(" Holding neutral %.1f s more to arm" % (ARM_TIME - waited))
        time.sleep(ARM_TIME - waited)

    print(" Direction A, up to +%d us" % MAX_DELTA)
    thr_ramp(NEUTRAL, NEUTRAL + MAX_DELTA)
    time.sleep(HOLD_TIME)
    thr_ramp(NEUTRAL + MAX_DELTA, NEUTRAL)
    time.sleep(2)

    print(" Direction B, down to -%d us" % MAX_DELTA)
    thr_ramp(NEUTRAL, NEUTRAL - MAX_DELTA)
    time.sleep(HOLD_TIME)
    thr_ramp(NEUTRAL - MAX_DELTA, NEUTRAL)
    print(" Thruster back at neutral")


def test_pump():
    print("\n[3] Pump on GP%d: %d cycles, %d s on / %d s off"
          % (PUMP_PIN, PUMP_CYCLES, PUMP_ON_TIME, PUMP_OFF_TIME))
    pump_off()
    time.sleep(1)
    for i in range(1, PUMP_CYCLES + 1):
        print(" Cycle %d of %d" % (i, PUMP_CYCLES))
        pump_on()
        time.sleep(PUMP_ON_TIME)
        pump_off()
        time.sleep(PUMP_OFF_TIME)


def run():
    print("Combined test: servos GP%s, thruster GP%d, pump GP%d"
          % ("/GP".join(str(n) for n in SERVO_PINS), THR_PIN, PUMP_PIN))
    if RUN_SERVOS:
        test_servos()
    if RUN_THRUSTER:
        test_thruster()
    if RUN_PUMP:
        test_pump()
    print("\nAll tests done")


try:
    run()
except KeyboardInterrupt:
    print("\nInterrupted")
finally:
    pump_off()          # always leave the gate held low
    thr_pulse(NEUTRAL)  # always leave the ESC at stop
    servos_stop()
    print("Safe state: pump off, thruster at %d us, servo pulses stopped" % NEUTRAL)
