# pump_demo.py — simple ON/OFF pump test for Raspberry Pi Pico (MicroPython)
#
# Hardware (bench test):
#   GP16 (physical pin 21) -> R6 220R -> Q1 IRLZ44N gate, R14 10k gate pull-down to GND
#   +24 V -> F2 3 A -> pump (1.4 A) -> Q1 drain; Q1 source -> GND; D3 1N5822 flyback across pump
#   Pico GND tied to the same GND as Q1 source
#   (In the full v9 schematic GP16 is THR_PWM and the pump is on GP19.)
#
# The pump is switched fully ON or fully OFF (no PWM), and the Pico's
# on-board LED mirrors the pump pin, so you can see what the script is
# asking for. If the pump keeps running while the LED is off and the
# script says "OFF", the problem is in the wiring, not the code.

from machine import Pin
import time

PUMP_PIN = 16      # GPIO number (GP16, physical pin 21)
ON_TIME = 3        # seconds
OFF_TIME = 3       # seconds
CYCLES = 5

pump = Pin(PUMP_PIN, Pin.OUT, value=0)   # gate driven low from the start
try:
    led = Pin("LED", Pin.OUT, value=0)   # Pico and Pico W
except (TypeError, ValueError):
    led = Pin(25, Pin.OUT, value=0)      # very old firmware


def pump_on():
    pump.value(1)
    led.value(1)
    print("PUMP ON   (GP%d = 1)" % PUMP_PIN)


def pump_off():
    pump.value(0)
    led.value(0)
    print("PUMP OFF  (GP%d = 0)" % PUMP_PIN)


def demo():
    print("Pump on/off test on GP%d: %d cycles, %d s on / %d s off"
          % (PUMP_PIN, CYCLES, ON_TIME, OFF_TIME))
    pump_off()
    time.sleep(2)
    for i in range(1, CYCLES + 1):
        print("Cycle %d of %d" % (i, CYCLES))
        pump_on()
        time.sleep(ON_TIME)
        pump_off()
        time.sleep(OFF_TIME)
    print("Test done")


try:
    demo()
except KeyboardInterrupt:
    print("Interrupted")
finally:
    pump_off()   # always leave the gate held low
