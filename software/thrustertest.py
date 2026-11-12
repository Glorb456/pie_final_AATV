# thrustertest.py — first-spin test for the U92 Pro thruster (MicroPython, Raspberry Pi Pico)
#
# Wiring (bench test):
#   GP16 (physical pin 21) -> 200R -> thruster signal wire (white); 10k from signal to GND
#   Thruster signal ground (thin black) -> Pico GND
#   Thruster power pair -> 12 V supply or fused battery (NOT through the Pico)
#
# The ESC is bidirectional: 1500 us = stop, above = one direction, below = the other.
# It will not spin until it has seen a steady 1500 us for a few seconds (arming).
#
# SAFETY
#   - Clamp the thruster down and keep hands, wires and loose items away from the prop.
#   - Run it in water for anything longer than a few seconds. Dry runs: low throttle, brief.
#   - MAX_DELTA limits the throttle. 500 would be 100 %. Start at 100 (about 20 %).
#   - Ctrl-C at any time returns the signal to stop.

from machine import Pin, PWM
import time

THR_PIN = 16        # GPIO number (GP16, physical pin 21)
NEUTRAL = 1500      # us, stop
MAX_DELTA = 100     # us away from neutral; raise in small steps once it behaves
STEP = 10           # us per ramp step
STEP_TIME = 0.2     # seconds per ramp step
HOLD_TIME = 2       # seconds at the top of each ramp
ARM_TIME = 4        # seconds of neutral before the first move

esc = PWM(Pin(THR_PIN))
esc.freq(50)        # standard 50 Hz servo-style signal


def pulse(us):
    esc.duty_ns(us * 1000)


def ramp(start, end):
    step = STEP if end > start else -STEP
    for us in range(start, end + step, step):
        pulse(us)
        print("  %d us" % us)
        time.sleep(STEP_TIME)


def run():
    print("Neutral for %d s (arming). Listen for the ESC's tones." % ARM_TIME)
    pulse(NEUTRAL)
    time.sleep(ARM_TIME)

    print("Direction A, up to +%d us" % MAX_DELTA)
    ramp(NEUTRAL, NEUTRAL + MAX_DELTA)
    time.sleep(HOLD_TIME)
    ramp(NEUTRAL + MAX_DELTA, NEUTRAL)
    time.sleep(2)

    print("Direction B, down to -%d us" % MAX_DELTA)
    ramp(NEUTRAL, NEUTRAL - MAX_DELTA)
    time.sleep(HOLD_TIME)
    ramp(NEUTRAL - MAX_DELTA, NEUTRAL)
    print("Test done")


try:
    run()
except KeyboardInterrupt:
    print("Interrupted")
finally:
    pulse(NEUTRAL)   # always leave the ESC at stop
    print("Signal held at neutral (%d us)" % NEUTRAL)
