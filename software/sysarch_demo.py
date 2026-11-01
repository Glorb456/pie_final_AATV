# Pico W servo sweep demo (MicroPython)
# Servos on GP15 (physical pin 20) and GP14 (physical pin 19)
from machine import Pin, PWM
import time

r1 = PWM(Pin(15))
r2 = PWM(Pin(14))
r3 = PWM(Pin(13))
r4 = PWM(Pin(12))

r1.freq(50)
r2.freq(50)
r3.freq(50)
r4.freq(50)
# standard 50 Hz servo signal

def set_pulse_us(us):
    r1.duty_ns(us * 1000)
    r2.duty_ns(us * 1000)
    r3.duty_ns(us * 1000)
    r3.duty_ns(us * 1000)
 

try:
    while True:
        # left, center, right, center (1000-2000 us is a safe range)
        for us in (1000, 1500, 2000, 1500):
            set_pulse_us(us)
            time.sleep(1)
finally:
    r1.duty_ns(0)  # stop sending pulses
    r2.duty_ns(0)
    r3.duty_ns(0)  # stop sending pulses
    r4.duty_ns(0)