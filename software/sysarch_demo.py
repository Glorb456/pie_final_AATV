# Pico W servo sweep demo (MicroPython)
# Servos on GP12-GP15 (physical pins 16, 17, 19, 20)
from machine import Pin, PWM
import time

r1 = PWM(Pin(15))
r2 = PWM(Pin(14))
r3 = PWM(Pin(13))
r4 = PWM(Pin(12))
servos = (r1, r2, r3, r4)

for s in servos:
    s.freq(50)  # standard 50 Hz servo signal


def set_pulse_us(us):
    for s in servos:
        s.duty_ns(us * 1000)


try:
    while True:
        # left, center, right, center (1000-2000 us is a safe range)
        for us in (1000, 1500, 2000, 1500):
            set_pulse_us(us)
            time.sleep(1)
finally:
    for s in servos:
        s.duty_ns(0)  # stop sending pulses
