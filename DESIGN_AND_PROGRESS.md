# AA-TV design and progress

Last updated: November 11, 2026

This is the plain-language summary of where the AA-TV electrical design stands and how it got here. For exact pin tables and part ratings see `CLAUDE.md`. For the detailed change log of each schematic version see `edits.md`.

## Where we are

The design is settled enough to build, and most parts are ordered. The drawings are behind: the newest schematic (v9) and the newest wiring diagram (v10 draft) both show an older thruster and an older ballast system. The next job is a v11 schematic and wiring guide that match what is described here.

| Area | State |
|---|---|
| Parts | Main Amazon order placed November 6. Valve, check valve and a few small items still to buy |
| Bench tests | Servos, MOSFET switches and the buck's low-voltage cutoff all pass |
| Schematic | v9 is the latest file. It is out of date |
| Wiring diagram | v10 draft. It is out of date and has one error that would damage a 12 V valve |
| Firmware | Servo sweep and pump on/off test scripts exist. No vehicle firmware yet |

## The current design

### What it is

A tethered submarine. A floating buoy carries a Raspberry Pi 4 and a USB power bank. A 3 m USB cable runs down a tube to a Raspberry Pi Pico inside the vehicle. The Pi sends commands; the Pico drives everything.

All the electronics sit in one waterproof box with four cable glands. Outside the box, in the water, are four servos (two rudder, two elevator), one thruster, a bilge pump and a solenoid valve.

### Power

One 3S LiPo battery (11.1 V, 5200 mAh) feeds everything except the Pico, which runs from the buoy over USB.

```
Battery -> EC5 plug -> 25 A fuse -> kill switch -> 12 V bus bar
                                                     |-> thruster (speed controller built in)
                                                     |-> 7.5 V converter -> four servos
                                                     |-> 24 V converter  -> pump and valve
```

- The kill switch cuts the positive side. It sits inside the sealed box, so the lid comes off to reach it.
- The 25 A fuse depends on a throttle limit in firmware. At full throttle with the pump running, the vehicle draws about 22 A on a full battery, and about 30 A if all four servos stall at once.
- The 24 V converter has its own fuse on its input wire. Nothing else is fused after the bus bar except, optionally, the valve.

### Control

- **Servos:** four PWM signals from the Pico, each through a 200 ohm resistor.
- **Thruster:** one servo-style signal. 1.5 ms is stop, shorter is reverse, longer is forward.
- **Pump and valve:** each is switched on and off by a MOSFET that the Pico drives directly. A diode across each one absorbs the voltage spike at turn-off. A 10k resistor on each MOSFET keeps it off whenever the Pico is not driving it.
- **Battery monitor:** the battery's balance lead goes through three resistor dividers into an ADS1115 converter, which the Pico reads over I2C. This gives each cell's voltage.
- **Leak sensor:** one sensor at the low point of the box.

### Ballast

The ballast tank is sealed, with no air line to the surface.

- Opening the valve lets water in. The water compresses the trapped air and stops when the pressures match.
- Running the pump pushes water out.
- With the valve closed and the pump off, the amount of water stays fixed. This needs a check valve on the pump outlet, because water can run backward through a stopped bilge pump.

This limits how much the ballast can do. At 1 m deep, only about 9% of the tank's air space can fill with water. The vehicle has to be trimmed very close to neutral, and it has to drive itself under with the thruster and elevators before the valve does anything. Depth is then held with the elevators while moving, with the vehicle trimmed slightly buoyant so it floats up if something fails.

### Main parts

| Part | Choice | Status |
|---|---|---|
| Thruster | ApisQueen U92 Pro 12 V, speed controller built in | Chosen (replaced an out-of-stock model) |
| Servos | 2 Hitec DB777WP, 2 Savox SW-1250MG | Owned |
| Battery | Zeee 3S 5200 mAh, EC5 plug, pack of two | Ordered |
| Servo supply | WSOLDMA 12 V to 7.5 V, 20 A | Ordered, tested |
| Pump supply | 12 V to 24 V boost, 3 A | Ordered |
| Pump | Rule 28D bilge pump, 24 V | Owned (free) |
| Valve | 24 V, normally closed, direct-acting | Not chosen |
| Check valve | Low opening pressure, to fit the pump hose | Not chosen |
| Pump and valve switches | IRLZ44N MOSFETs, 1N5822 diodes | Ordered, tested |
| Battery monitor | ADS1115 board | Ordered |
| Box | Otdorpatio IP67 with four M16 glands | Ordered (size to confirm) |
| Fuses | Blade fuse kit with six inline holders | Ordered |
| Kill switch | 30 A waterproof rocker | Ordered |

The full list with links and prices is in the BOM Google Sheet. Rows highlighted green are ordered.

## What has been tested

| Test | Result |
|---|---|
| Both servo types driven straight from the Pico's 3.3 V signal | Work |
| MOSFET switching the pump from a Pico pin | Works |
| Servo converter fed a falling input voltage, no load | Output held until 9 V, which is below where the battery should ever go |

## What is still open

**To decide or buy**
- The valve. It should be 24 V so it can share the pump's supply.
- A check valve for the pump outlet, then hose and clamps once the fittings can be measured.
- Small parts: 100 nF capacitors, potting epoxy, header sockets for the Pico, glue-lined heat shrink, silicone wire.

**To test**
- The pump starting from the 24 V converter with the battery low (about 10 V).
- Thruster current at the planned throttle limit.
- The servo converter's exact output voltage. Up to about 7.6 V is fine.
- The value printed on the 24 V converter's input fuse. It needs to be 7.5 to 10 A.

**To measure**
- The air volume of the sealed tank. This sets how much the ballast can change the vehicle's weight.
- The thruster cable's diameter against the gland.
- Which box size arrived, and that it fits the hull.

**To draw**
- v11 schematic and wiring guide.
- Vehicle firmware: throttle limit, battery limits, pump and valve interlock.

## Corrections to apply when reading the current drawings

Until v11 exists, these override the v9 schematic and the v10 draft diagram:

1. The thruster's speed controller is inside the thruster, not inside the box. Two power wires and a signal pair pass through the thruster gland.
2. There is no pump speed controller and no Deutsch connector. The pump is switched by a MOSFET.
3. The valve runs from the 24 V supply only if it is a 24 V valve. The draft shows it on 24 V regardless.
4. There is no fuse after the 24 V converter.
5. The main fuse is 25 A, not 30 A.
6. The servo supply is fixed at 7.5 V. It cannot be "set to 7.4 V".
7. Battery-monitor resistors are 100k/200k, 200k/100k and 100k/30k, not 47k, 200k and 330k over 100k.
8. Every 220 ohm resistor is 200 ohm.

## How the design got here

| Date | Version | What changed | Why |
|---|---|---|---|
| Before Nov 3 | v5 and earlier | Custom circuit board. Pi and Pico linked by a serial cable and a reset wire | Starting point |
| Nov 3 | v6 | Circuit board replaced by two solderable breadboards in two dryboxes. Pico powered and controlled over USB from the buoy. Servos on their own 7.5 V supply | No time or need for a custom board |
| Nov 4 | v7 | All cables potted through the box walls. Deutsch waterproof connectors outside the boxes. Wire limited to two gauges. Thruster speed controller moved into the water | Simpler, more reliable sealing |
| Nov 4 | v8 | Front driven wheels dropped. Switched to the larger Deutsch DTP connectors | DT connectors did not fit marine wire |
| Nov 4 | v8.1 | Servo leads potted straight into the box, no connectors | Avoid cutting expensive servo leads |
| Nov 5 | v8.2, v8.3 | Battery connection reworked twice, ending with one contact per pole and no underwater splice. Bus bar and terminal parts chosen. Servo data corrected to the servos actually owned | Contact current limits; no wet splices |
| Nov 6 | BOM review | First full check of the BOM against the schematic before buying | Purchasing was about to start |
| Nov 6 | v9 | Everything combined into one waterproof box with the battery inside. Kill switch moved to the positive side. Battery monitor added | The whole hull became ballast space, so separate boxes were no longer needed |
| Nov 6 | v10 draft | Free 24 V bilge pump adopted. 24 V converter added. Pump speed controller replaced by a MOSFET switch. Solenoid valve added to let water in | A free, fast pump that only runs one way |
| Nov 6 | Orders | BOM cleaned up, Type column added, totals fixed. Main Amazon order placed. All fuses standardized on one blade-fuse kit | |
| Nov 6 to 7 | Thruster | Original thruster went out of stock. ApisQueen U92 Pro chosen: more thrust, more current, speed controller built in | Availability |
| Nov 7 to 11 | Bench work | Pump switch built and tested on a breadboard. Servos tested from the Pico | |
| Nov 11 | Design review | Full check of drawings against the parts and datasheets. Found the drawings out of date and the valve drawn on the wrong voltage. Battery-monitor resistors redesigned around the values on hand | Parts had changed since the drawings were made |
| Nov 11 | Ballast | Tank changed from vented to sealed. Check valve added to the plan. Fuse after the 24 V converter removed. Servo converter cutoff measured at 9 V | Simpler plumbing; fewer parts |

## Where things are

| What | Where |
|---|---|
| Latest schematic | `kicad_files/AATV_v9/AATV_v9.kicad_sch` and `AATV_v9.pdf` |
| Latest wiring diagram | `../AATV_wiring_v10_draft.png` |
| Last complete wiring guide | `../AATV_wiring_guide_v9.html` |
| Older schematics and guides | `kicad_files/AATV/` and `../old-wiring/` |
| Test scripts | `software/sysarch_demo.py` (servo sweep), `software/pumptest.py` (pump on/off) |
| Drawing generators | `tools/schematic_gen/`, `tools/wiring_guide/` |
| Parts list and orders | BOM Google Sheet, tabs "BOM" and "Orders" |
| Detailed change log | `edits.md` |
| Notes for Claude | `CLAUDE.md` |
