#!/usr/bin/env bash
# Run this ON THE PI 4. Flashes / talks to the Pico over the USB cable,
# and hard-resets it through Pi GPIO4 -> Pico RUN (no button presses needed).
#
# One-time setup on the Pi:
#   pip install --user mpremote        (or: sudo apt install python3-mpremote)
#
# Usage:
#   ./flash_pico.sh main  <file.py>       copy a file to the Pico as main.py and restart it
#   ./flash_pico.sh put   <file> [...]     copy files to the Pico (keeps their names)
#   ./flash_pico.sh run   <file.py>        run a file once without saving it
#   ./flash_pico.sh ls                      list files on the Pico
#   ./flash_pico.sh repl                    open the MicroPython prompt (Ctrl-] to exit)
#   ./flash_pico.sh reset                   hard reset through the RUN pin
#   ./flash_pico.sh firmware <fw.uf2>       install / update MicroPython firmware
set -euo pipefail

RUN_GPIO=4                       # Pi header pin 7 -> Pico RUN (pin 30)
MP="mpremote"

hard_reset() {
    # Pull RUN low for 100 ms, then release it (input with pull-up).
    pinctrl set "$RUN_GPIO" op dl
    sleep 0.1
    pinctrl set "$RUN_GPIO" ip pu
    sleep 1.5                    # let the Pico's USB come back up
}

# If a running program has locked up the USB REPL, reset and grab it at boot.
connect_or_reset() {
    if ! timeout 5 $MP exec "pass" >/dev/null 2>&1; then
        echo "Pico not responding, hard-resetting via RUN..."
        hard_reset
    fi
}

cmd="${1:-}"; shift || true
case "$cmd" in
  main)     connect_or_reset; $MP cp "$1" :main.py + reset ;;
  put)      connect_or_reset; for f in "$@"; do $MP cp "$f" ":$(basename "$f")"; done ;;
  run)      connect_or_reset; $MP run "$1" ;;
  ls)       connect_or_reset; $MP ls ;;
  repl)     connect_or_reset; $MP repl ;;
  reset)    hard_reset; echo "Pico reset." ;;
  firmware)
    uf2="$1"
    connect_or_reset
    echo "Rebooting Pico into its USB bootloader..."
    $MP bootloader || true
    for _ in $(seq 20); do [ -e /dev/disk/by-label/RPI-RP2 ] && break; sleep 0.5; done
    [ -e /dev/disk/by-label/RPI-RP2 ] || { echo "Bootloader drive RPI-RP2 did not appear."; exit 1; }
    sudo mkdir -p /mnt/rpi-rp2
    sudo mount /dev/disk/by-label/RPI-RP2 /mnt/rpi-rp2
    sudo cp "$uf2" /mnt/rpi-rp2/
    sync
    sudo umount /mnt/rpi-rp2 2>/dev/null || true   # Pico reboots itself after the copy
    echo "Firmware written. The Pico restarts automatically."
    ;;
  *) sed -n '2,20p' "$0"; exit 1 ;;
esac
