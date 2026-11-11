# Pi 4 <-> Pico setup

## Wiring (see AATV.kicad_sch)
| Pi 4 header | Pico | Purpose |
|---|---|---|
| USB-A port | micro-USB (cable) | flash code / firmware, REPL, 5 V to VBUS |
| pin 8 GPIO14 TXD | pin 2 GP1 (UART0 RX) | Pi -> Pico commands |
| pin 10 GPIO15 RXD | pin 1 GP0 (UART0 TX) | Pico -> Pi telemetry |
| pin 7 GPIO4 | pin 30 RUN | hard reset from the Pi |
| any GND | any GND | common ground |

## Pi one-time setup
1. `sudo raspi-config` -> Interface Options -> Serial Port: login shell **No**, hardware port **Yes**.
2. Add `dtoverlay=disable-bt` to `/boot/firmware/config.txt` so `/dev/serial0` uses the full UART, then reboot.
3. `pip install --user mpremote` (or `sudo apt install python3-mpremote`).
4. Copy `flash_pico.sh` to the Pi and `chmod +x` it.

## Day-to-day
```
./flash_pico.sh main sysarch_demo.py     # upload as main.py and restart
./flash_pico.sh repl                     # MicroPython prompt
./flash_pico.sh reset                    # hard reset through RUN
./flash_pico.sh firmware RPI_PICO_W.uf2  # update MicroPython, no BOOTSEL button needed
```

## Pico side (MicroPython)
```python
from machine import UART, Pin
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
```
Pi side: `serial.Serial('/dev/serial0', 115200)` (pyserial).
