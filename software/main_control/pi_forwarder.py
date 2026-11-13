"""Pi side: pass command lines from SSH to the Pico, and Pico status back.

The laptop starts this over ssh and keeps the session open:
    ssh pi@192.168.50.1 python3 -u /home/pi/pi_forwarder.py

stdin  (from the laptop)  -> USB serial -> Pico
stdout (to the laptop)    <- USB serial <- Pico
If the ssh session ends, we send a stop to the Pico before exiting.

Needs:  sudo apt install python3-serial   and the user in the dialout group.
"""
import sys
import threading

import serial

PORT = "/dev/ttyACM0"
STOP = b"C 0 0 0 0 0 0 0\n"

ser = serial.Serial(PORT, 115200, timeout=0.2)
running = True


def pico_to_stdout():
    while running:
        line = ser.readline()
        if line:
            sys.stdout.write(line.decode(errors="ignore"))
            sys.stdout.flush()


threading.Thread(target=pico_to_stdout, daemon=True).start()

try:
    for line in sys.stdin:               # ends when ssh closes
        if line.startswith("C "):        # only forward real command lines
            ser.write(line.encode())
finally:
    running = False
    ser.write(STOP)
    ser.close()
