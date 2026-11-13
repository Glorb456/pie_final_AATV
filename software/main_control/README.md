# main_control: drive the sub with an Xbox controller

Xbox controller on the laptop -> SSH over a Bluetooth link -> Raspberry Pi 3B on the buoy -> USB cable -> Pico in the sub -> servos, thruster, pump, valve.

```
laptop (controller, USB)  --Bluetooth PAN + SSH-->  Pi 3B  --USB serial-->  Pico (main.py)
laptop_controller.py                                pi_forwarder.py          pico_main.py
```

Bluetooth only carries the network link between the laptop and the Pi. The controller is plugged into the laptop with a USB cable.

## Files

| File | Runs on | Job |
|---|---|---|
| `laptop_controller.py` | laptop | Reads the controller, handles arming, sends one command line per 50 ms over a single SSH session |
| `pi_forwarder.py` | Pi 3B | Passes command lines to the Pico over `/dev/ttyACM0` and passes Pico status back. Sends a stop if the SSH session ends |
| `pico_main.py` | Pico | Save on the Pico as `main.py`. Drives the outputs and enforces the safety rules |

Command line format: `C thr rud elv pump valve arm emerg`. `thr`, `rud`, `elv` are -100 to 100. The rest are 0 or 1.

## Controls

| Input | Action |
|---|---|
| Hold RB for 1 s | Arm. Only works with the left stick centred and LT, RT, LB released |
| Tap RB, or Back | Disarm |
| Left stick Y | Thruster (up = forward, down = reverse) |
| Right stick X | Rudder fins |
| Right stick Y | Elevator fins (up = nose up) |
| Hold LT | Valve open (water in, descend) |
| Hold RT | Pump on (water out, ascend) |
| LB | Emergency ascent: thruster stops, fins centre, valve closed, pump on. Works while disarmed. Disarms you afterwards |

Controller numbering is the Linux `xpad` driver numbering (wired Xbox Series X controller). `python3 laptop_controller.py --show` prints the raw axes and buttons if yours differ, and the constants at the top of the file can be changed to match.

## Safety behaviour (enforced on the Pico)

- Boots disarmed. To arm, the Pico must first see `arm=0` and then `arm=1`, so a laptop that is still armed cannot arm the sub after a Pico reboot or a link drop.
- No command for 0.5 s: disarm, thruster and fins neutral, pump off, valve closed.
- Disarmed: everything neutral and off, except emergency ascent.
- Pump and valve are never on together.
- Thruster is held at neutral for 4 s after boot (ESC arming) and capped at 1500 +/- 100 us (`THR_MAX_DELTA`, 20 % of the 1000 to 2000 us range). This is a pulse-width limit, not a measured thrust or current limit.
- Any exit drives the pump and valve low and the ESC to neutral.
- The emergency pump run has no dry-run timer. The pump only moves water that is in the tank.

## Pins (from `../combined_test.py`, the version verified on the bench)

| Function | GPIO |
|---|---|
| Servos 1 to 4 | GP0, GP1, GP3, GP4 |
| Thruster ESC signal | GP2 |
| Pump enable | GP16 |
| Valve enable | GP18 (not verified, the valve switch is not built yet) |

`pico_main.py` assumes servos 1 and 2 are the rudders and servos 3 and 4 are the elevators. That is a guess.

## Setup

### Pi 3B (done once)

- Raspberry Pi OS with `bluez-tools`. User `aatv`, SSH enabled, `python3-serial` 3.5 present, user in `dialout`.
- A network bridge `pan0` with address `192.168.50.1/24`, made with `nmcli` (connection `bridge-pan0`).
- `bt-pan.service` runs `/usr/bin/bt-network -s nap pan0` (after `bluetooth.service`, `Restart=always`).
- A second one-shot service pipes `power on`, `pairable on`, `discoverable on` into `bluetoothctl` at boot, and `DiscoverableTimeout = 0` is set in `/etc/bluetooth/main.conf`.
- Copy `pi_forwarder.py` to the Pi home folder (`scp pi_forwarder.py aatv@192.168.50.1:~/`).

### Laptop (done once)

1. Pair the laptop with the Pi in Settings, Bluetooth (confirm the code on both sides, then `trust` on the Pi in `bluetoothctl`).
2. Create the network connection with the Pi's Bluetooth MAC (`bluetoothctl devices`):
   ```bash
   nmcli con add type bluetooth con-name pi-pan bluetooth.bdaddr <PI_MAC> bluetooth.type panu
   nmcli con mod pi-pan ipv4.method manual ipv4.addresses 192.168.50.2/24
   nmcli con mod pi-pan connection.autoconnect yes
   ```
3. SSH key login so there is no password prompt: `ssh-copy-id aatv@192.168.50.1`.
4. A venv with the controller library: `python3 -m venv .venv`, then `.venv/bin/pip install pygame mpremote`.

### Pico (done once, and again after each edit of `pico_main.py`)

Plug the Pico into the laptop, then:

```bash
mpremote cp pico_main.py :main.py
mpremote reset
```

Move it to the Pi's USB port. Check it shows up with `ssh aatv@192.168.50.1 'ls /dev/ttyACM*'`.

## Running it

```bash
nmcli con up pi-pan
sleep 10                      # the link needs a few seconds to settle
ping -c 3 192.168.50.1        # must answer before you start
python3 laptop_controller.py  # from the venv: .venv/bin/python laptop_controller.py
```

Other modes: `--show` (print controller axes and buttons, no network) and `--dry-run` (print the command lines, no SSH). `--host` and `--remote-script` override the defaults (`aatv@192.168.50.1`, `/home/aatv/pi_forwarder.py`).

You should see the Pico status twice a second, for example `S thr=0 rud=0 elv=0 pump=0 valve=0 safe`. The last word is `safe`, `ARMED`, `EMERGENCY` or `NO-LINK`.

If you get `No route to host` right after `nmcli con up pi-pan`, wait 10 seconds and ping again before starting the script.

## Known issues and to do

- **Servo orientation needs to be fixed.** Check each fin on the vehicle: right stick up must tilt the nose up, right stick right must turn the rudder right. Flip signs in `RUDDER_DIR` and `ELEVATOR_DIR` (one value per servo, in pin order), or swap `RUDDER_PINS` and `ELEVATOR_PINS` if the pairs are the wrong way round. Then upload again.
- **Thruster direction not verified.** `THR_DIR = 1` means stick forward sends 1600 us. Set it to `-1` if the strong push turns out to be backward.
- **Valve pin GP18 is unverified**, because the valve switch is not built yet.
- **Pin map mismatch.** `../../CLAUDE.md` lists servos on GP12 to GP15, thruster GP16, valve GP18 and pump GP19. The bench-verified wiring (used here) is different. The team has to pick one for the final board.
- **Thruster current at the 20 % cap is not measured** (see CLAUDE.md, open items).
- **Link drop on LB seen once.** Pressing LB (pump on) dropped the Bluetooth and SSH link during testing. The cause was not diagnosed. If it happens again, check whether the pump or boost is powered and run `ssh aatv@192.168.50.1 'uptime; vcgencmd get_throttled'` after it reconnects to see if the Pi rebooted or saw undervoltage.
- **Not included:** battery monitor (ADS1115), leak sensor, sonar, battery limits.
- This README and `../PI_SETUP.md` disagree: `PI_SETUP.md` still describes the old Pi 4 UART and RUN-pin wiring.
